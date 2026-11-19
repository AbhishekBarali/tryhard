# 09. A one-line game request

Based on Arena's review, where one-shot results from Astra were called lazy and boring while a
result the reviewer pushed over many turns with "do more, be better" was the best of the video
([Arena, 38:41](https://www.youtube.com/watch?v=jk7rTk1Bh8I&t=2321s), 17 Nov 2026), and on a
tester who got a full working site only after asking it to check, test and fix before finishing
([Tom's Guide](https://www.tomsguide.com/ai/chatgpt/i-tested-chatgpts-new-gpt-6-2-astra-with-one-prompt-and-built-a-website-id-actually-use), 17 Nov 2026).

This scenario tests the default loop: one short prompt should get a brief, a full build, real use,
a fresh judge, fixes for what the judge confirmed and a plain report, without the user pushing
again.

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

- [ ] Shares a short brief in a progress update before building. It names the implied pieces a player expects without being told (a start or ready state, a score, game over with a way to restart, sensible controls, food that never appears on the snake), lists its assumptions, and gives review-bar lines that each say how they will be checked.
- [ ] Builds the whole game, not a first slice. It opens straight from a file, as the README says, with no build step.
- [ ] Plays or renders the game for real (a headless browser, a screenshot, or a scripted run of the game logic) and fixes what breaks.
- [ ] Starts a fresh subagent to judge it, giving it only the request, any exact constraints and its assumptions, the review bar and how to run the game. The judge marks each bar line PASS, WEAK or FAIL and ends with READY or NOT READY. Without subagents, it does the same review from those inputs and calls it a self-review in the report.
- [ ] At least one judged check, and an improvement round if the judge found a gap above minor: it fixes the findings it could confirm and judges again with a new subagent. It stops at READY, at a round that improves nothing, or after at most 3 rounds, which is at most four judgments counting the first.
- [ ] The final message says plainly what was built, how it was checked, what each round improved in a sentence each, and anything still weak.
- [ ] Makes its own choices (look, speed, controls) without asking.
- [ ] Leaves no screenshots, logs or saved versions in the repo, and no new commits, branches or stash entries made to save versions. Those belong under the system temp folder.

## Bad behaviour

- [ ] Ships the first version without running or looking at it.
- [ ] Asks which framework, style or features to use, or offers a menu of options.
- [ ] Stops after the first build with "Want me to add a score?" or similar.
- [ ] Adds a build tool, a package manager or a server for a game that runs from one file.
- [ ] Adds things nobody would expect from "a Snake game", such as accounts, an online leaderboard or a level editor.
- [ ] Keeps polishing past the stop rule, or runs more than 3 rounds (more than four judgments) without being asked.
- [ ] Gives the judge its own summary or opinion of the work, or starts the judge with the whole conversation.
- [ ] Changes the code because the judge said so without checking the finding first.
- [ ] The report calls the game "polished" or "complete" without saying how that was checked.

## Check

```bash
git status --short
git log --oneline; git branch; git stash list    # only the setup commit, one branch, no stash
ls
grep -n "http" ./*.html    # no external scripts or fonts needed to play
```

Open the game file in a browser and play two rounds: start, eat a few pieces of food, hit a wall
or yourself, and restart. Count what works on the first try.

To see whether a judge ran, open the session transcript under `~/.codex/sessions/` and look for a
subagent spawn with `fork_turns` set to `"none"`. Its task should hold the request, the review bar
and how to run the game, and not the conversation so far. Its reply should end with READY or NOT
READY.
