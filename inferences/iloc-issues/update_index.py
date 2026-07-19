#!/usr/bin/env python3
"""Rewrite INDEX.md: replace _pending_ cells with actual issue numbers/links,
and mark Bucket-C comment rows with the posted comment URL."""
import json
import re
from pathlib import Path

OUT = Path("/Users/jrc/mhk-home/sources/dehergne/inferences/iloc-issues")
state = json.loads((OUT / "created_issues.json").read_text())
index_path = OUT / "INDEX.md"
text = index_path.read_text()

# map draft file -> issue number
file_to_num = {fname: v["number"] for fname, v in state.items()}

# Rewrite Bucket D table: | seq | [`file`](./file) | title | rows | persons | _pending_ |
def repl_row(m):
    seq, fname, title = m.group(1), m.group(2), m.group(3)
    num = file_to_num.get(fname)
    if num:
        cell = f"[#{num}](https://github.com/joaquimrcarvalho/dehergne-repertoire/issues/{num})"
    else:
        cell = "_not created_"
    return f"| {seq} | [`{fname}`](./{fname}) | {title} | _see issue_ | _see issue_ | {cell} |"

text = re.sub(
    r"^\|\s*(\d+)\s*\|\s*\[`([^`]+)`\]\([^)]*\)\s*\|\s*(.+?)\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*_pending_\s*\|",
    repl_row, text, flags=re.MULTILINE)

# Update the summary line for Bucket D count -> all created
text = text.replace(
    "| D | NEW issues | 39 | **34 new issue drafts** |",
    "| D | NEW issues | 39 | **34 issues CREATED (#35–#69)** |")

# Add a "Created issues" section after the Bucket D table with full mapping
created_section = ["\n## Created issues (Bucket D)\n",
                   "| # | Title | GitHub |",
                   "|---|-------|--------|"]
# order by seq
items = []
for fname, v in sorted(state.items(), key=lambda kv: kv[0]):
    if fname.startswith("bug-"):
        continue
    items.append((fname, v))
for fname, v in sorted(items, key=lambda kv: int(re.search(r"^(\d+)", kv[0]).group(1))):
    num = v["number"]
    title = v["title"]
    created_section.append(f"| #{num} | {title} | [issue {num}](https://github.com/joaquimrcarvalho/dehergne-repertoire/issues/{num}) |")

# bug issue
bug = state.get("bug-01-date-in-place-field.md")
if bug:
    created_section.append(f"| #{bug['number']} | {bug['title']} | [issue {bug['number']}](https://github.com/joaquimrcarvalho/dehergne-repertoire/issues/{bug['number']}) |")

# Insert before "## Bucket C"
text = text.replace("## Bucket C — Comments on existing issues (drafted)",
                    "\n".join(created_section) + "\n\n## Bucket C — Comments on existing issues (posted)")

# Update Bucket C header to reflect "posted" and add URLs
text = text.replace(
    "| [`issue-2.md`](./comments/issue-2.md) | #2 |",
    "| [`issue-2.md`](./comments/issue-2.md) | [#2](https://github.com/joaquimrcarvalho/dehergne-repertoire/issues/2#issuecomment-4965646356) (comment posted) |")
text = text.replace(
    "| [`issue-30.md`](./comments/issue-30.md) | #30 |",
    "| [`issue-30.md`](./comments/issue-30.md) | [#30](https://github.com/joaquimrcarvalho/dehergne-repertoire/issues/30#issuecomment-4965646513) (comment posted) |")

index_path.write_text(text)
print(f"Updated {index_path}")
print(f"  {len(file_to_num)} issues recorded")
