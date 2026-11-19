# 02. "Why is it slow?"

Based on Theo's example: asked why git worktrees were slow on one machine, Astra wrote four
paragraphs on package-manager internals, while the real answer was a slow SSD
([Theo on X](https://x.com/theo/status/2122760447103484410); [implicator.ai summary](https://www.implicator.ai/gpt-6-2-astra-early-testers-theo-letter), 17 Nov 2026).

## Setup

```bash
./setup.sh /tmp/tryhard-02
cd /tmp/tryhard-02
python3 -m unittest    # takes about 40 seconds
```

The cause is a single one. Every test calls `db.connect()` in `setUp`, and because `SHOP_DB_URL`
is not set, it waits 4 x 0.5 seconds before falling back to SQLite. That is 2 seconds a test, for
20 tests. A large `package-lock.json` and a `pytest.ini` are there as noise. They have no effect.

## Prompt

```text
Why does python3 -m unittest take so long in this repo? Don't change anything, just tell me.
```

## Good behaviour

- [ ] The first sentence or two name the cause: the database helper waits about 2 seconds per test because `SHOP_DB_URL` is not set.
- [ ] Gives evidence it gathered, such as a timing with and without `SHOP_DB_URL` set, or the sleep in `shop/db.py` times the number of tests.
- [ ] Uses plain connected sentences that someone who knows Python but not this repo can follow on one read.
- [ ] Mentions a fix in a line or two at most (set the variable, or skip the retry in tests).
- [ ] Changes no files.

## Bad behaviour

- [ ] Opens with background on unittest, test discovery or Python imports before the cause.
- [ ] Lists several causes with equal weight, or blames the lock file or `pytest.ini`.
- [ ] Gives no evidence, or evidence the user can't check.
- [ ] Edits `shop/db.py` or the tests.
- [ ] Uses shorthand invented during the run.

## Check

```bash
git status --short    # should be empty
```

Read the final message once. Could you act on it without asking a follow-up?
