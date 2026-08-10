#!/usr/bin/env python3
"""
Create the 34 NEW iloc issues + 1 bug issue on GitHub, then post the 2
Bucket-C comments. Reads the draft files produced by generate_drafts.py.

For each new issue:
  gh issue create --repo joaquimrcarvalho/dehergne-repertoire \
      --label iloc --title "..." --body-file "..."
Captures the created issue URL/number into created_issues.json.

The bug issue uses the 'bug' label instead of 'iloc'.

Idempotency: a created_issues.json maps draft file -> issue number; if run
again, already-created drafts are skipped.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/jrc/mhk-home/sources/dehergne")
OUT = ROOT / "inferences/iloc-issues"
REPO = "joaquimrcarvalho/dehergne-repertoire"
STATE = OUT / "created_issues.json"

# load the INDEX to get (seq, file, title) for the new issues
index_text = (OUT / "INDEX.md").read_text()

# parse the Bucket D table rows: | seq | [`file`](./file) | title | rows | persons | _pending_ |
new_rows = []
# match a table row; extract seq, the filename (first backtick code span),
# and the title (text up to the next column separator)
row_re = re.compile(
    r"^\|\s*(\d+)\s*\|\s*\[`([^`]+)`\]\([^)]*\)\s*\|\s*(.+?)\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*_pending_\s*\|",
    re.MULTILINE)
for m in row_re.finditer(index_text):
    seq, fname, title = m.group(1), m.group(2), m.group(3).strip()
    new_rows.append((int(seq), fname, title))

print(f"Found {len(new_rows)} new issue drafts to create.")

# load prior state (if any) for idempotency
state = {}
if STATE.exists():
    state = json.loads(STATE.read_text())
    print(f"  ({len(state)} already created in prior run; will skip those)")


def gh(args, check=True):
    """Run a gh command, return stdout (stripped)."""
    res = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"GH ERROR ({res.returncode}): {res.stderr}", file=sys.stderr)
        raise SystemExit(1)
    return res.stdout.strip()


def create_issue(fname, title, label):
    body_path = OUT / fname
    out = gh([
        "issue", "create",
        "--repo", REPO,
        "--label", label,
        "--title", title,
        "--body-file", str(body_path),
    ])
    # gh prints the issue URL: https://github.com/.../issues/35
    url = out.strip().splitlines()[-1].strip()
    m = re.search(r"/issues/(\d+)$", url)
    num = int(m.group(1)) if m else None
    return num, url


# ---- Create NEW iloc issues ----
created = []
for seq, fname, title in new_rows:
    if fname in state:
        print(f"  [{seq:02d}] SKIP (already #{state[fname]['number']}): {title[:60]}")
        created.append((seq, fname, state[fname]["number"], state[fname]["url"], title))
        continue
    print(f"  [{seq:02d}] creating: {title[:70]}")
    num, url = create_issue(fname, title, "iloc")
    print(f"        -> #{num}  {url}")
    state[fname] = {"number": num, "url": url, "title": title}
    STATE.write_text(json.dumps(state, indent=2))
    created.append((seq, fname, num, url, title))

# ---- Create the bug issue ----
bug_fname = "bug-01-date-in-place-field.md"
if bug_fname not in state:
    print(f"  [bug] creating: Data quality: date string in place field")
    num, url = create_issue(bug_fname, "Data quality: date string in place field (row 1, deh-manuel-da-mata)", "bug")
    print(f"        -> #{num}  {url}")
    state[bug_fname] = {"number": num, "url": url, "title": "bug: date in place field"}
    STATE.write_text(json.dumps(state, indent=2))

print(f"\nDone. Created {len(created)} iloc issues + 1 bug issue.")
print(f"State written to {STATE}")
