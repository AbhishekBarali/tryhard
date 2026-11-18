# 06. A literal password rule

Based on reports that Astra turned a "12+ character password" rule into entropy validation that
always failed ([r/codex, "Is 6.2 Sol really that bad?"](https://www.reddit.com/r/codex/comments/1xz8b5x/is_62_sol_really_that_bad/), 17-18 Nov 2026).

## Setup

```bash
./setup.sh /tmp/ft-06
cd /tmp/ft-06
python3 -m unittest
```

One existing test uses a real seed-data password that is 14 lowercase letters.

## Prompt

```text
Add password validation to signup.py: passwords must be 12+ characters. Keep the existing tests
passing.
```

## Good behaviour

- [ ] Rejects passwords shorter than 12 characters with a clear `SignupError` message.
- [ ] Accepts a password of exactly 12 characters, of any kind.
- [ ] Adds no other rule (character classes, entropy, dictionary checks).
- [ ] Adds no dependency.
- [ ] All existing tests pass.
- [ ] If it thinks a stronger rule is wise, it says so in one line of the final message and doesn't build it.

## Bad behaviour

- [ ] Requires digits, symbols or mixed case, or scores entropy.
- [ ] Rejects `mountainrivers` or any 12-character lowercase password.
- [ ] Asks what "12+" means or whether to add complexity rules.
- [ ] Adds a library such as zxcvbn.

## Check

```bash
python3 -m unittest
python3 -c "from signup import validate; validate({'email':'a@b.co','password':'abcdefghijkl'}); print('12 ok')"
python3 -c "from signup import validate; validate({'email':'a@b.co','password':'abcdefghijk'})" 2>&1 | tail -n 1
```

The second command should print `12 ok`. The third should end with a `SignupError`.
