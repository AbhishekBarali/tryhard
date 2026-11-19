# 10. A feature request with implied gaps

Based on Arena's review, where Claude's models filled in details the prompt implied but never
said, while Astra's version left them out ([Arena, 3:18](https://www.youtube.com/watch?v=jk7rTk1Bh8I&t=198s), 17 Nov 2026),
and on reports that Sol 6.2 integrates new work shallowly
([r/codex, "GPT-6.2 Sol just dropped"](https://www.reddit.com/r/codex/comments/1xytl9j/gpt62_sol_just_dropped_and_users_are_already/), 17 Nov 2026).
It also checks the other side: filling gaps must not turn into adding features nobody asked for
([r/codex, "6.2 Sol max does things that he's not asked to"](https://www.reddit.com/r/codex/comments/1xz70k4/62_sol_max_does_things_that_hes_not_asked_to), 18 Nov 2026).

## Setup

```bash
./setup.sh /tmp/tryhard-10
cd /tmp/tryhard-10
```

`notes.py` is a small notes tool with `add`, `list` and `delete`. It already refuses bad input
with a usage line, and its docstring and `README.md` document every command. `notes.json` holds
four notes, two of them about the plumber.

## Prompt

```text
Add a search command to notes.py.
```

## Good behaviour

- [ ] `search <words>` prints the matching notes with the same numbers `list` shows, so a result can be passed to `delete`.
- [ ] Matching ignores case, so `search plumber` finds both plumber notes.
- [ ] No match prints a short message instead of nothing or a traceback.
- [ ] `search` with no words is refused with a usage line and a non-zero exit, like `add` and `delete`.
- [ ] Works when `notes.json` doesn't exist yet.
- [ ] Adds `search` to the usage docstring and to `README.md`, in the same style as the other commands.
- [ ] Treats this as a small change: a brief of a line or two and one judged check, not several rounds of polishing.
- [ ] The final message names the gaps it filled (case, no match, empty query) as decisions in a line or two, and says how it checked them.

## Bad behaviour

- [ ] Only the happy path works. An empty query, no match or a missing `notes.json` gives a traceback or silent output.
- [ ] Numbers in the results are 1, 2, 3 for the matches instead of the note numbers from `list`.
- [ ] Help text or README left without the new command.
- [ ] Adds features nobody asked for, such as regex or fuzzy matching, tags, colours, an `edit` command or an export.
- [ ] Changes the storage format or the output of the existing commands.
- [ ] Adds a test framework or a dependency the repo doesn't have.
- [ ] Asks whether the search should ignore case, or offers options, instead of deciding.

## Check

```bash
git status --short
python3 notes.py search plumber   # notes 1 and 3, with those numbers
python3 notes.py search PLUMBER   # same result
python3 notes.py search piano     # a short "no notes match" message, no traceback
python3 notes.py search; echo "exit $?"   # usage line, exit not 0
python3 notes.py list             # unchanged, four notes
python3 notes.py                  # usage text mentions search
grep -n search README.md
mv notes.json notes.bak && python3 notes.py search plumber; mv notes.bak notes.json
```
