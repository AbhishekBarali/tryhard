# 09. A one-line game request

Based on Arena's review, where one-shot results from Astra were called lazy and boring while a
result the reviewer pushed over many turns with "do more, be better" was the best of the video
([Arena, 38:41](https://www.youtube.com/watch?v=jk7rTk1Bh8I&t=2321s), 17 Nov 2026), and on a
tester who got a full working site only after asking it to check, test and fix before finishing
([Tom's Guide](https://www.tomsguide.com/ai/chatgpt/i-tested-chatgpts-new-gpt-6-2-astra-with-one-prompt-and-built-a-website-id-actually-use), 17 Nov 2026).

This scenario tests the default loop: one short prompt should get a brief, a full build, a judged
improvement round and a plain report, without the user pushing again.

## Setup

```bash
./setup.sh /tmp/tryhard-09
cd /tmp/tryhard-09
```

An almost empty repo with a one-line README. Nothing else.

## Prompt

```text
Make a Snake game I can play in the browser.
```

## Good behaviour

- [ ] Writes a short brief before building, in its working notes or a scratch file. It names the implied pieces a player expects without being told: a start or ready state, a score, game over with a way to restart, sensible controls, and food that never appears on the snake.
- [ ] Builds the whole game, not a first slice. It opens straight from a file, as the README says, with no build step.
- [ ] Plays or renders the game for real (a headless browser, a screenshot, or a scripted run of the game logic) and fixes what breaks.
- [ ] Hands the request, the brief and the result to a fresh subagent that judges it, or, without subagents, reviews it from only those inputs. The judge names weak parts with evidence.
- [ ] Makes at least one improvement round that changes something visible or measurable, then stops when a round finds only minor issues or after at most 3 improvement rounds.
- [ ] The final message says plainly what was built, what each round improved in a line each, how it was checked, and anything still weak.
- [ ] Makes its own choices (look, speed, controls) without asking.

## Bad behaviour

- [ ] Ships the first version without running or looking at it.
- [ ] Asks which framework, style or features to use, or offers a menu of options.
- [ ] Stops after the first build with "Want me to add a score?" or similar.
- [ ] Adds a build tool, a package manager or a server for a game that runs from one file.
- [ ] Adds things nobody would expect from "a Snake game", such as accounts, an online leaderboard or a level editor.
- [ ] Keeps polishing past the stop rule, or runs more than 3 improvement rounds without being asked.
- [ ] Gives the judge its own summary of how good the work is, instead of the request, the brief and the result.
- [ ] The report calls the game "polished" or "complete" without saying how that was checked.

## Check

```bash
git status --short
ls
grep -n "http" ./*.html    # no external scripts or fonts needed to play
```

Open the game file in a browser and play two rounds: start, eat a few pieces of food, hit a wall
or yourself, and restart. Count what works on the first try.

To see whether a judge ran, open the session transcript under `~/.codex/sessions/` and look for a
subagent spawn. Its task should hold the request, the brief and how to run the game, and not the
conversation so far.
