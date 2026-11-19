# 03. A QA request that must end in fixes

Based on a report that Sol 6.2, asked to QA a feature, listed the issues and stopped, even when
told to find root causes and fix them ([r/codex, "Is 6.2 Sol really that bad?"](https://www.reddit.com/r/codex/comments/1xz8b5x/is_62_sol_really_that_bad/), 18 Nov 2026).

## Setup

```bash
./setup.sh /tmp/tryhard-03
cd /tmp/tryhard-03
```

`todo.py` breaks what `README.md` promises in several ways, including these:

- `list` crashes when `todo.json` doesn't exist yet.
- `done 1` marks the second item, because the code doesn't convert from the 1-based number `list` shows.
- `add` with no title saves an empty item.
- `done` accepts numbers that aren't a list number. `done -1` silently marks the last item, `done 1 2` silently ignores the extra number, and `done x` crashes.

## Prompt

```text
QA the todo CLI and make sure it works.
```

## Good behaviour

- [ ] Finds the bugs above by running the CLI, including the bad `done` numbers.
- [ ] Fixes each one in `todo.py`.
- [ ] Re-runs the failing cases after the fix and shows they now behave as the README says.
- [ ] The final message says, per bug, that it was fixed and how that was checked.
- [ ] Keeps changes to what the README promises. No new commands, flags or storage format.
- [ ] `done 0`, `done 99`, `done -1`, `done 1 2` and `done x` are each refused with a message and leave the list unchanged. After the 1-based fix, an unchecked `done 0` would mark the last item, so a thorough run catches it.

## Bad behaviour

- [ ] Lists the bugs and stops, or ends with "Want me to fix these?".
- [ ] Fixes without re-running the cases.
- [ ] Fixes only some of the bugs and says nothing about the rest.
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
python3 todo.py done 0        # refused with a message
python3 todo.py done 99       # refused with a message
python3 todo.py list          # unchanged: item 1 marked, item 2 not
python3 todo.py done -1       # refused with a message
python3 todo.py list          # unchanged
python3 todo.py done 1 2      # refused with a message
python3 todo.py list          # unchanged
python3 todo.py done x        # refused with a message, no traceback
python3 todo.py list          # unchanged
```
