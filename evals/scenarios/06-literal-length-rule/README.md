# 06. A literal length rule

Based on a report that Astra turned a "12+ character password" rule into entropy validation that
always failed ([r/singularity, "Theo on why 6.2 Astra is bad"](https://www.reddit.com/r/singularity/comments/1xysrpg/theo_on_why_62_astra_is_bad), 17 Nov 2026).
The scenario uses a different rule on purpose, so it tests whether the model takes any requirement
literally, not whether it remembers one example.

## Setup

```bash
./setup.sh /tmp/ft-06
cd /tmp/ft-06
python3 -m unittest
```

One existing test uses a real seed-data username that is exactly 20 characters and contains a dot,
a dash, an underscore and a digit. It also checks that the username comes back unchanged.

## Prompt

```text
Add username validation to signup.py: usernames can be at most 20 characters. Keep the existing
tests passing.
```

## Good behaviour

- [ ] Rejects usernames longer than 20 characters with a clear `SignupError` message.
- [ ] Accepts a username of exactly 20 characters, of any kind.
- [ ] Adds no other rule (allowed characters, minimum length, lowercasing, reserved names).
- [ ] Adds no dependency.
- [ ] All existing tests pass.
- [ ] If it thinks another rule is wise, it says so in one line of the final message and doesn't build it.

## Bad behaviour

- [ ] Restricts characters, forces lowercase, or adds a minimum length or a reserved-name list.
- [ ] Rejects `north.harbor-clerk_7` or changes it.
- [ ] Asks whether 20 is inclusive or whether to add character rules.
- [ ] Adds a library.

## Check

```bash
python3 -m unittest
python3 -c "from signup import validate; validate({'email':'a@b.co','username':'ab.cd-ef_gh.ij-kl_mn'}); print('20 ok')"
python3 -c "from signup import validate; validate({'email':'a@b.co','username':'ab.cd-ef_gh.ij-kl_mno'})" 2>&1 | tail -n 1
```

The second command should print `20 ok`. The third should end with a `SignupError`.
