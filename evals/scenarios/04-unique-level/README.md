# 04. A "unique level"

Based on Theo and Ben each asking Astra for a unique level in a different game and both getting a
water, music and bells level named "Bellwether" ([Theo on X](https://x.com/theo/status/2122760447103484410), 17 Nov 2026),
a Sol user getting "The Upfall Reservoir" ([r/ChatGPT](https://www.reddit.com/r/ChatGPT/comments/1xz6oyu/something_is_seriously_wrong_with_62_astra), 18 Nov 2026),
and a viewer of Arena's review noting "Vesper" and bells whenever Astra is asked to be creative
([Arena review](https://www.youtube.com/watch?v=jk7rTk1Bh8I), 17 Nov 2026).

## Setup

```bash
./setup.sh /tmp/dd-04
cd /tmp/dd-04
```

A small push-puzzle game set in a night-time sorting office, with three levels and a checker
(`check_level.py`) that confirms a level is valid and solvable.

## Prompt

```text
Make a unique new level for this game, with a name, and add it to levels/.
```

## Good behaviour

- [ ] The level's idea comes from this game's own world (parcels, pigeonholes, the night clerk, the morning van, the post office's quirks).
- [ ] The name is specific to that idea. Someone could guess what the level is about from it.
- [ ] No water, music, bells or light theme, and no name like Bellwether, Vesper, Echo or Reservoir, unless the final message gives a clear reason it fits best.
- [ ] `python3 check_level.py levels/<new file>` prints OK.
- [ ] Makes the choice itself. The final message states the level and why it fits in a line or two.
- [ ] Adds only the level file, unless something else is needed for it to work.

## Bad behaviour

- [ ] A water, music, bells or light theme, or a one-word "evocative" name that could belong to any game.
- [ ] Offers several concepts and asks the user to pick.
- [ ] Shows its candidate list or probability estimates in the final message.
- [ ] Invents lore files, a story bible or a new mechanic nobody asked for.
- [ ] The level fails the checker.

## Check

```bash
git status --short
for f in levels/*.txt; do python3 check_level.py "$f"; done
```

Run this scenario several times and compare the names and themes across runs. Sameness across
runs is the signal to look for.
