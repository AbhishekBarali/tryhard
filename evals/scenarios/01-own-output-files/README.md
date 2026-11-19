# 01. A question about its own output files

Based on Theo's report that a long Astra run blocked itself on a question about which of two
clip files its own reviewer had written ([Theo on X](https://x.com/theo/status/2122760447103484410), 17 Nov 2026).

## Setup

```bash
./setup.sh /tmp/tryhard-01
cd /tmp/tryhard-01
```

Three reviewer scripts in `tools/` write notes to files with random names. Reviewer b writes a
draft and a final file and doesn't say which is which. The final one is marked `FINAL` inside
and is written a second later.

## Prompt

```text
Run the three reviewer scripts in tools/, then write REVIEW.md listing every finding, most
severe first, and fix the high and medium findings in app/form.html.
```

## Good behaviour

- [ ] Runs all three scripts and inspects `out/` itself (listing, timestamps or contents).
- [ ] Picks reviewer b's final file from the evidence (the `FINAL` marker or the later timestamp) and ignores the draft.
- [ ] Notes that choice in one plain line in the final message, or not at all.
- [ ] Writes `REVIEW.md` with three findings in the order high, medium, low.
- [ ] Changes `app/form.html` so an empty form can't be submitted silently and the footer can't cover the Save button.
- [ ] Finishes in one turn without asking anything.

## Bad behaviour

- [ ] Asks which file reviewer b wrote, or which of `b_..._p.txt` and `b_..._g.txt` to use.
- [ ] Reports itself blocked or waits for input.
- [ ] Uses the draft note ("maybe the footer colour").
- [ ] The final message names the random file names as if the user knows them.

## Check

```bash
cat REVIEW.md
git diff app/form.html
```
