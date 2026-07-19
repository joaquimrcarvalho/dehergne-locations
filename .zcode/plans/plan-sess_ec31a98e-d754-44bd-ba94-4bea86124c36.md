## Goal
Establish `timelink-py` as the coordination home for the three-repo stack with minimal ceremony: one version pin, one compatibility manifest, one verification script, one written checklist. No boards, no per-repo issue duplication.

## Preconditions (corrected — no staleness)
The local clone is a **git worktree** at `/Users/jrc/develop/timelink-py-worktree/main`, current at **v1.1.33**, using **GitHub Actions** (`.github/workflows/ci.yml`), with bump2version managing `setup.cfg` + `timelink/__init__.py`. The old `/Users/jrc/develop/timelink-py` clone (v1.1.26, `.travis.yml`) is stale and out of scope. The `.travis.yml` references in my earlier plan are obsolete.

Per `WORKTREE_GUIDE.md`, branching is done **from the worktree root**, not in-place inside `main/`:
```bash
cd /Users/jrc/develop/timelink-py-worktree
git worktree add stack-coordination -b feature/stack-coordination
# then work in /Users/jrc/develop/timelink-py-worktree/stack-coordination/
```

---

## Part 1 — Pin Kleio version via env var (stop defaulting to `:latest`)

Mirror the existing `KLEIO_ADMIN_TOKEN` env pattern already in this file (`kleio_server.py:316-320` — read env, fall back, cache).

**`timelink/kleio/kleio_server.py`:**
- Add module constant near top (after imports): `DEFAULT_KLEIO_VERSION = "12.9.588"`.
- Add a module-level helper (mirroring `make_token`'s pattern):
  ```python
  def get_default_kleio_version() -> str:
      """Resolved Kleio image tag: $KLEIO_VERSION env, else DEFAULT_KLEIO_VERSION."""
      return os.environ.get("KLEIO_VERSION") or DEFAULT_KLEIO_VERSION
  ```
- Change `start()` default at **line 91**: `kleio_version: str | None = "latest"` → `kleio_version: str | None = None`.
- Replace the fallback at **lines 150-151** (`if kleio_version is None: kleio_version = "latest"`) with `kleio_version = get_default_kleio_version()`.
- Update the docstring at **line 114** to reflect the new resolution order.
- Leave `get_server()` at **line 236** (`kleio_version="latest"`) for now — it's a lookup-by-version helper, not a provisioning default; changing it is a separate behavior change. Note it in RELEASE_CHECKLIST as a known follow-up.

Net effect: explicit caller args unaffected; `None` → `KLEIO_VERSION` env → pinned constant. The `f"{image}:{version}"` assembly at line 1136 is untouched.

**`tests/__init__.py`** — add a single source of truth for the test pin, alongside the existing `KleioServerTestMode` config (line 89):
```python
# Kleio server image version used by the test fixture.
# Set to a specific build for reproducibility; "latest" for ad-hoc checks.
use_kleio_version = "12.9.588"
```

**`tests/conftest.py`** — the fixture currently hardcodes `kleio_version = "latest"` at **line 51**, bypassing any shared config. Change it to read the constant:
```python
from tests import use_kleio_version
...
kleio_version = use_kleio_version
```
(Keep the existing commented-out pre-release example at lines 52-54 as documentation of the workflow.)

**`.github/workflows/ci.yml`:**
- Add `KLEIO_VERSION: "12.9.588"` to the top-level `env:` block (lines 10-13), alongside the existing `TRAVIS`/`GITHUB_ACTIONS` vars.
- Change **line 81**: `docker pull timelinkserver/kleio-server:latest` → `docker pull timelinkserver/kleio-server:${KLEIO_VERSION}`.

One env name (`KLEIO_VERSION`) spanning code, tests, and CI → one concept, three sites.

---

## Part 2 — `STACK.md` at repo root (the coordination manifest)

New file `timelink-py-worktree/stack-coordination/STACK.md`. Records a known-good combination and the update rule. Initial content:
- kleio-server `12.9.588` → docker `timelinkserver/kleio-server:12.9.588`
- timelink-py `1.1.33` (current `main`)
- timelink-docs ref + date (filled when docs phase runs; marked "pending" now)
- A "Verified against" line
- The rule: **this file is updated last in every coordinated release**

Note on the version number: local `timelink-kleio` source is at build **592** (dev), while **588** is what the consuming `dehergne` project and `timelink-docs/.kleio.json` both pin. STACK.md records the *released, verified-good* value (588). The actual number is a placeholder pending your confirmation of which build is promoted on Docker Hub `:12.9` — I'll flag this as the one value to confirm before I write it.

---

## Part 3 — `scripts/check-stack.sh` (verification guard)

New file `timelink-py-worktree/stack-coordination/scripts/check-stack.sh` (executable). Reads pinned versions from STACK.md (simple grep) and verifies local reality:
- Installed timelink: `python -c "import timelink; print(timelink.__version__)"` matches STACK.md.
- Prints `KLEIO_VERSION` env if set (warns if it differs from STACK.md's pin).
- Docker image: `docker image inspect timelinkserver/kleio-server:<pinned>` locally; falls back to `docker manifest inspect` against the registry; non-fatal if Docker unavailable.
- Exit non-zero on mismatch; clear one-line-per-check summary.

Run it before any release and after any `git pull`. No dependencies beyond docker/git/python.

---

## Part 4 — `RELEASE_CHECKLIST.md` at repo root (the written workflow)

New file `timelink-py-worktree/stack-coordination/RELEASE_CHECKLIST.md`. This is where the framework lives, written down once. Contains:

1. **Change taxonomy** — table mapping change type A (kleio notation grammar) / B (XML output) / C (py API) / D (docs-only) / E (infra) → which repos move, in what order. A/B = coordinated; C/D/E = single-repo.
2. **Single-repo release** (C/D/E): branch → test → HISTORY.rst → `bumpversion patch|minor|major` (auto-commits + tags `vX.Y.Z`) → push tag → CI → PyPI. Notes the two files bumpversion syncs (`setup.cfg current_version`, `timelink/__init__.py`) and that the legacy `setup.py` is a known-drift risk.
3. **Coordinated release** (A/B) — propagation order:
   - **kleio**: edit → `make inc-build` → `make build-multi` → `make tag-multi-stable` → kleio CHANGELOG. (Caveats from exploration: `tag-multi-stable` creates the git tag but does **not** push it — you push; build number is never reset on minor/major bumps; `inc-major` resets minor but not build; no CI exists in kleio; `make prepare` references a `sources-structure.yaml` path that doesn't match where `cp -r ./src .build` places it.)
   - **py**: update `DEFAULT_KLEIO_VERSION` + CI `KLEIO_VERSION` + `tests/__init__.use_kleio_version` → run tests against new image → HISTORY.rst → bumpversion → tag → PyPI.
   - **docs**: version-note ("requires kleio ≥X, timelink ≥Y") → merge → CI auto-`gh-deploy`.
   - **last**: update STACK.md with all three refs; optionally a GitHub Release on timelink-py summarizing the three changelogs.
4. **kleio release caveats** — the bullets above, recorded so you don't re-hit them.
5. **Security note** — pointer to the follow-on docs phase (token rotation).
6. **One-line pointer**: open one checklist issue on timelink-py, label per affected repo (`kleio` / `timelink-py` / `timelink-docs`), close it only when every box is ticked.

---

## What I will NOT touch in this phase (explicit follow-on list)
- **timelink-kleio**: `CHANGELOG.md` at repo root (none exists).
- **timelink-docs**: (a) `docs/about/versions.md` mirroring STACK.md; (b) fix stale refs — `docs/introduction/installing_timelink.md:10` (`pip -U` → `pip install -U timelink-py`), `docs/developer/development_environment.md:9` (drop hardcoded `0.2.8`); (c) wire `blog` into `docs/.nav.yml` + seed `docs/blog/posts/` for release notes (infra exists but dormant); (d) pin the 8 unpinned `pip install` lines in `.github/workflows/ci.yml`.
- **Token remediation** (your chosen "rotate + untrack forward"): add `.kleio.json` to `timelink-docs/.gitignore` + `git rm --cached .kleio.json`; you rotate the live `kleio_admin_token` server-side. History retains the now-dead token — acceptable, non-destructive.
- **timelink-py round-trip XML test**: frozen `.cli` → expected-XML pair under `tests/` that re-exports on each kleio bump and diffs. Highest-leverage test, distinct piece of work.

---

## One value to confirm before I write files
**Which kleio build should STACK.md and the pin declare — `12.9.588`?** That's what `dehergne/.kleio.json` and `timelink-docs/.kleio.json` both use, and what I've assumed. If a different build is actually promoted on Docker Hub `:12.9`, tell me and I'll use that instead. Everything else is determined.

## Execution permissions I'll need
- `git worktree add` + `git add/commit` in the worktree.
- Run the timelink-py test suite (pytest) to confirm the pin change doesn't break the fixture path.
- `chmod +x scripts/check-stack.sh` and a trial run.