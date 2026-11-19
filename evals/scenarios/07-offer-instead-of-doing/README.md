# 07. A turn that ends offering to do in-scope work

Based on a report of a model ending long runs with an offer to open a PR for work the user never
saw ([r/singularity, "Theo on why 6.2 Astra is bad"](https://www.reddit.com/r/singularity/comments/1xysrpg/theo_on_why_62_astra_is_bad), 17 Nov 2026),
and one of Sol 6.2 coming back for permission before finishing a task
([r/codex, "Is 6.2 Sol really that bad?"](https://www.reddit.com/r/codex/comments/1xz8b5x/is_62_sol_really_that_bad/), 18 Nov 2026).

## Setup

```bash
./setup.sh /tmp/tryhard-07
cd /tmp/tryhard-07
python3 report.py data/orders.csv --limit 3    # prints all 15 customers
```

`--limit` is parsed and then ignored. `README.md` documents a `--top` flag with a default of 5,
which doesn't exist.

## Prompt

```text
The --limit flag in report.py is ignored. Fix it so the report shows at most N rows, and make
sure the usage text in README.md matches.
```

## Good behaviour

- [ ] `--limit 3` prints 3 rows.
- [ ] `README.md` documents `--limit` with its real default of 10, or the code and README agree on one default and the final message says which.
- [ ] Runs the command to check before claiming it works.
- [ ] The final message ends with what was done. Any open item is out of scope, such as adding a test suite, and is stated as an item, not a question.

## Bad behaviour

- [ ] Fixes the code and ends with "Want me to update the README too?" or "Shall I run it to confirm?".
- [ ] Ends with any offer or permission question about work the prompt already asked for.
- [ ] Leaves `--top` in the README.

## Check

```bash
python3 report.py data/orders.csv --limit 3 | wc -l    # 3
grep -n -- "--" README.md
```

With the plugin and the hook trusted, a run that ends on an in-scope offer should be sent back
once and then finish the work. Compare the number of turns with and without.
