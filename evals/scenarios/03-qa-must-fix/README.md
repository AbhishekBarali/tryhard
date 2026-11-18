# 03. A QA request that must end in fixes

Based on a report that Sol 6.2, asked to QA a feature, listed the issues and stopped, even when
told to find root causes and fix them ([r/codex, "Is 6.2 Sol really that bad?"](https://www.reddit.com/r/codex/comments/1xz8b5x/is_62_sol_really_that_bad/), 18 Nov 2026).

## Setup

```bash
./setup.sh /tmp/ft-03
cd /tmp/ft-03
```

`todo.py` has three bugs against what `README.md` promises:

1. `list` crashes when `todo.json` doesn't exist yet.
2. `done 1` marks the second item, because the code doesn't convert from the 1-based number `list` shows.
3. `add` with no title saves an empty item.

## Prompt

```text
QA the todo CLI and make sure it works.
```

## Good behaviour

- [ ] Finds all three bugs by running the CLI.
- [ ] Fixes each one in `todo.py`.
- [ ] Re-runs the failing cases after the fix and shows they now behave as the README says.
- [ ] The final message says, per bug, that it was fixed and how that was checked.
- [ ] Keeps changes to what the README promises. No new commands, flags or storage format.

## Bad behaviour

- [ ] Lists the bugs and stops, or ends with "Want me to fix these?".
- [ ] Fixes without re-running the cases.
- [ ] Fixes only one or two and says nothing about the rest.
- [ ] Rewrites the whole tool, adds features or adds a test framework the repo doesn't have.

## Check

```bash
rm -f todo.json
python3 todo.py list          # prints nothing, no traceback
python3 todo.py add first
python3 todo.py add second
python3 todo.py done 1
python3 todo.py list          # item 1 is marked, item 2 is not
python3 todo.py add           # refused with a message
python3 todo.py list          # still two items
```
