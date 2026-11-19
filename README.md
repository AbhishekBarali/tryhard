<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-light.svg">
  <img alt="Tryhard" src="docs/assets/banner-light.svg">
</picture>

<p><b>GPT-6.2 coasts. Tryhard makes it finish.</b><br>
A Codex plugin that makes it work out what you want, build all of it, judge it and make it better.</p>

<p>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-2f6feb"></a>
  <a href="plugins/tryhard/.codex-plugin/plugin.json"><img alt="Version 0.3.0" src="https://img.shields.io/badge/version-0.3.0-C2410C"></a>
  <a href="docs/why.md"><img alt="For GPT-6.2 Astra and Sol" src="https://img.shields.io/badge/GPT--6.2-Astra%20%26%20Sol-5b6170"></a>
</p>

</div>

## Why

GPT-6.2 Astra and Sol can do the work. They just don't do it properly or all the way. Since launch, people using them in Codex keep reporting the same thing: the model lists bugs instead of fixing them, stops halfway with "Shall I continue?", does the smallest version that runs, and hands over its first draft as the finished thing.

Tryhard flips it into tryhard mode. For real work, it works out what you actually want, builds the whole thing, has a fresh judge check it against a clear bar, and fixes what the judge finds until the bar is met or more rounds stop helping. Five skills and a small Stop hook do the work, and there is nothing new to learn.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/before-after-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/before-after-light.svg">
  <img alt="Three habits, each shown as the model's message without Tryhard and with it: stops at a list, asks about its own files, explains in riddles" src="docs/assets/before-after-light.svg">
</picture>

## How it works

Ask for real work the way you normally would. Tryhard turns that one prompt into a loop:

1. **Works out what you really want.** It writes a short brief and shares it before building: the parts a thoughtful expert would include even though you didn't say them, the gaps it filled as assumptions, and a review bar of what you will look for and how each line gets checked. Anything you stated exactly, like a number, a name or "don't touch X", stays exactly as you said it.
2. **Builds the whole thing**, not a first slice.
3. **Uses it for real.** It runs it, plays it, opens it and looks at it, and fixes what breaks.
4. **A fresh judge checks it.** A new subagent that hasn't seen the conversation tries the result itself, marks each bar line PASS, WEAK or FAIL, and ends with READY or NOT READY.
5. **Fixes what the judge found and judges again.** It confirms each finding before acting on it. It stops at READY, when a round stops helping, or after 3 rounds unless you ask for more, and hands back the best version.
6. **Reports plainly.** What it made, how it was checked, what each round improved, and anything still weak.

The loop fits the task. Quick edits, questions, explanations and reviews get no brief and no judge. A small fix gets a three-line brief and one judge pass. In Plan mode the brief goes into the plan, and the building waits until you leave Plan mode. The full rules are under [More details](#more-details).

There are two levels:

| Level | What you do | What you get |
|---|---|---|
| **Just ask** | Type your request as usual | The loop above, up to 3 rounds |
| **Push further** | Start with `$tryhard:raise-the-bar`, ideally at ultra | A stricter bar and up to 8 rounds, run as a Codex `/goal` until the judge says READY |

The loop costs more time and usage than a single pass. That is the trade: the model does the extra rounds, so you don't have to push it again yourself. Quick edits and questions skip the loop and stay quick.

What it targets:

- **Half-done work.** Every part of the request and the cases it implies get built and checked for real. A QA request ends in fixes, not a list of issues.
- **Doing only what was spelled out.** It reads your request as the minimum and fills the obvious gaps, like bad input and help text for a new command. It doesn't add features you didn't ask for.
- **First drafts passed off as finished.** A fresh judge checks the result against the bar, and it fixes the gaps the judge found until the judge says READY or another round stops helping.
- **Stopping halfway.** When the next step is part of the task, it does it instead of asking "Shall I continue?".
- **The same answer as everyone else.** When a task leaves a real creative choice open, it sets the obvious default aside and picks on fit.
- **Loops that go nowhere.** Every loop has a clear stop and a round cap. Long measured runs keep only the changes that improve the main number.
- **Questions nobody can answer.** It looks things up and decides routine choices itself, and it never asks you about files it made.
- **Explanations you can't read.** The final message leads with the answer or the main cause, in plain words, then says what is still open.

## Quick start

You need the Codex CLI or the Codex desktop app. The Stop hook also needs Python 3.8 or newer as `python3` (macOS, Linux) or `python` (Windows) on your PATH. The skills work without it.

```bash
codex plugin marketplace add AbhishekBarali/tryhard
codex plugin add tryhard@tryhard
```

Then start Codex, open `/hooks` and trust the Tryhard Stop hook. Codex skips plugin hooks until you trust them, so without this step the hook never runs. In the desktop app the same list is under Settings > Hooks.

Installed the earlier version under its old name? Remove it, then install and trust the hook as above:

```bash
codex plugin remove follow-through@follow-through
codex plugin marketplace remove follow-through
```

For real work, use the Tryhard profile too. It raises reasoning effort from Codex's low default to xhigh, which the loop needs to stay with a task through the last round:

```bash
curl -fsSL -o ~/.codex/tryhard.config.toml \
  https://raw.githubusercontent.com/AbhishekBarali/tryhard/main/profiles/tryhard.config.toml
codex --profile tryhard
```

How to switch to ultra, and an optional always-on block for `AGENTS.md`, are under [More details](#more-details).

## What's inside

**Automatic.** These trigger from what you ask, so there is nothing to type.

- `finish-the-job` runs the loop above: a brief, the whole build, real use, a fresh judge and up to 3 rounds of fixes. It runs for builds, features, fixes, QA, games, pages, designs and documents.
- `fresh-ideas` sets the obvious answer aside and picks on fit. It runs inside the brief when a task leaves open a choice you will see, such as a name, a theme, a level concept or a visual direction.
- `explain-plainly` leads with the answer or the main cause, in plain words. It runs when you ask why something happens, ask for a summary, or say you are confused.

**By name.** These run only when you call them.

- `raise-the-bar` pushes further: the same loop with a stricter bar and up to 8 rounds, run as a Codex `/goal`. It works best at ultra effort.
- `set-a-goal` sets up a long-running `/goal` for a measured target, such as speed, size or a score.

**Stop hook.** Once you trust it, it catches hand-backs, needless questions and dense reports.

## Usage

### Just ask

```text
Make a small Snake game I can play in the browser.
```

No prefix needed. Tryhard shares a short brief first. For this one it might decide the game needs a start screen, a score, game over with a restart, and both keyboard and touch controls. Then it builds the game, plays it, has a fresh judge check it against the brief's bar and fixes what the judge confirmed. The final message says how it was checked, what each round improved and what is still weak.

Want more rounds? Say so in the request, for example "do 5 rounds". "Keep going until it's great" means up to 8. If you only want a fast first version, say that instead.

### Push further

Start Codex at ultra effort if your account offers it, then call `raise-the-bar`:

```bash
codex --profile tryhard -c model_reasoning_effort=ultra
```

```text
$tryhard:raise-the-bar Build a landing page for a small bakery in Lisbon.
```

`raise-the-bar` uses the same brief and fresh judge with a stricter bar: what a top expert would be proud to put their name to. It runs as a Codex `/goal`, so Codex keeps starting new turns until the judge says READY or 8 rounds are done, unless you give another number. Its notes go in a `.tryhard/` folder that stays out of your commits. When it can't start a goal, it runs the rounds in the same turn and gives you the `/goal` line to paste. It costs the most, so save it for the asks where you want the best result you can get.

Ultra is limited to some accounts. Without it, raise-the-bar still works at xhigh, the profile's default. How it starts the goal and what it keeps on disk are under [More details](#more-details).

### Set a goal

```text
$tryhard:set-a-goal Make the test suite run under 2 minutes without dropping tests.
```

`set-a-goal` turns a request into a Codex `/goal` for a long run with a number to beat. It measures the starting value first, then writes `.goal/contract.md` with the main measure and the command for it, the side goals in order, what is out of scope and how "done" is proved. Then it starts the goal, or gives you the exact `/goal` line to paste.

It sets a token budget only if you name one in your request. To cap every goal, set `max_goal_token_budget` under `[goals]` in `~/.codex/config.toml`.

It changes your workspace and git state. The section below says exactly how, so read it before the first run.

## More details

<details>
<summary><b>How the default loop decides, judges and stops</b></summary>

<br>

**How much loop a task gets.** A one-line edit, rename or version bump gets no brief and no judge, just the change and a quick real check. A small fix in one place gets a three-line brief (your request, your exact constraints, the review bar), one real run of the changed path and one judge pass, and only confirmed blocking problems get fixed. A new feature, command, page, game, design, document or QA pass gets the whole loop. Questions, explanations and reviews get an answer and no changes.

**The brief.** For a bigger build it is about ten to twenty short lines: your request as you wrote it, your exact constraints, what the result is at its best and who it is for, what you meet in the first seconds, the details an expert would include, any open choices (settled with `fresh-ideas`), the assumptions it made, and three to eight review-bar lines, each with how it is checked. It also keeps a short list of lazy versions the result must not be. That list stays in its notes and reaches the judge as positive checks. You see the brief in a progress update before the build starts, so you can steer early.

**The judge.** Each round it starts a new subagent with `fork_turns` set to `"none"`, so the judge doesn't inherit the conversation. The judge gets five things: your request, your exact constraints, the review bar, how to run or see the result with the folder of screenshots and logs from real use, and from the second round on the blockers the last judge found. It never sees the worker's summary or opinion of the work. It uses the result for real, including at least two edge or hostile inputs, marks each bar line PASS, WEAK or FAIL with evidence it saw itself, ranks the gaps, and ends with READY or NOT READY. READY means every bar line passes and nothing above minor is left.

**Without subagents.** If no subagent can be started, the model does the same review itself from the same five inputs and says in the report that it was a self-review.

**Acting on findings.** The judge's findings are claims. The model confirms each one above minor with its own evidence before fixing it, fixes the confirmed ones in order of importance, and keeps your constraints over the judge's advice. Minor gaps don't start a round. The bar can get stricter as the work goes, but it never drops so the work passes.

**When it stops.** At the first of these:

- The judge says READY, or finds nothing above minor.
- A round moved no bar line toward PASS and closed no real gap.
- A round made a more important bar line worse. It goes back to the best version.
- The same big gap survived two rounds of fixes.
- 3 rounds are done, or the number you gave. "Keep going until it's great" means 8.

Before each round it saves the current version as a patch or a copy under the system temp folder, without touching your branches, commits or stash, so it can hand back the best version rather than the last one. Screenshots and logs from real use go in a temp folder too. After the stop it does no more polishing, and the final message names what still falls short of the bar. Asking for more rounds continues from the best version.

</details>

<details>
<summary><b>How raise-the-bar runs as a goal, and what it keeps on disk</b></summary>

<br>

**What changes from the default loop.** It runs the whole loop whatever the size of the change. If the work already exists, it uses and judges it before changing anything. The bar is five to eight lines of what a top expert would be proud to sign. The run ends only when a fresh judge says READY or 8 rounds are logged (or your number). A round that didn't help, a regression or a stubborn gap sends it back to the best version to try a different approach for the weakest bar line, instead of ending the run. At ultra effort it keeps parallel subagents to about four or five. It works without subagents too, with each review labelled as a self-review.

**Files.** It creates `.tryhard/` in the folder Codex is working in. In a git repository it adds `.tryhard/` to the local exclude file (the path `git rev-parse --git-path info/exclude` prints, usually `.git/info/exclude`), so nothing in it enters a commit.

- `.tryhard/brief.md` holds the brief with its review bar, the path of the judge's instructions, and a note that checks already run on the current state stand until their inputs change.
- `.tryhard/rounds.md` is the round log, one line per round: what changed, the judge's READY or NOT READY and its top gaps, and what is still open. It names the best version.
- `.tryhard/versions/` holds a copy or patch of the changed files from before each round, so a worse round can be undone without touching your branches or commits.
- `.tryhard/evidence/` holds the screenshots, logs and outputs from real use that the judge works from.

Each goal turn starts by reading `brief.md` and `rounds.md` and checking the current state of the work. Delete the folder whenever you no longer need it.

**Starting the goal.** It calls `get_goal` first, then takes the first case that fits:

- No goal is set. It creates one with a short objective that points at `.tryhard/brief.md` and states the 8-round cap. A token budget is added only if you named one.
- The same objective is already active. It continues it.
- A different unfinished goal is active. It leaves that goal alone, tells you in one line, and runs the rounds in the current turn.
- A finished goal is still set, which blocks a new one. It gives you `/goal clear` and the `/goal` line to paste after it, and runs the rounds in the current turn meanwhile.
- The goal tools are missing. It runs the rounds in the current turn and gives you the `/goal` line in the final message. If goals are turned off in your Codex, add this to `~/.codex/config.toml`:

  ```toml
  [features]
  goals = true
  ```

It marks the goal complete only after a final real use and a fresh judge's READY, or once the last allowed round is logged with the gaps that remain. If the same blocker, such as something only you can supply, holds for three goal turns in a row, it marks the goal blocked, the same rule Codex's own goals use.

**Effort.** It mentions once that it does best at ultra, chosen under `/model` in the CLI or in the app's model picker. It still works at xhigh.

</details>

<details>
<summary><b>What set-a-goal does to your files and git</b></summary>

<br>

- It creates a `.goal/` folder (contract, attempt ledger, status and logs) and adds it to the repo's local exclude file (usually `.git/info/exclude`), so it never shows up in commits. Dependency folders, build output, large data files and anything that looks like a secret go in the same exclude file if git doesn't already ignore them.
- If the project folder is not a git repository yet, it runs `git init` there and commits the current files. It never does this in your home folder or in a folder that holds other repositories. Started from one of those, it sets up in the project folder your request is about, and asks which one if the request doesn't say.
- It works on a new branch named `goal/` plus a short name and leaves your own branch where it was. Any uncommitted changes you had become the first commit on that branch. To get them back on your branch, `git switch` to it and run `git cherry-pick --no-commit` on that first commit. The final message tells you which of these steps it took.
- Every attempt is a commit. An attempt that doesn't beat the best result so far is dropped with `git reset --keep`, which leaves your other local changes in place.

</details>

<details>
<summary><b>Reasoning effort, the profile and switching to ultra</b></summary>

<br>

Codex's model catalog sets both GPT-6.2 models to low effort by default. OpenAI's launch charts show a benchmark score at low effort falling sharply compared with the previous models, and OpenAI's own guide says higher effort helps the model stay with a long task through the final checks. The loop leans on exactly that, so use more for real work:

- **xhigh**, the profile's default, for builds, features, debugging and investigations.
- **ultra** with `raise-the-bar` for the biggest asks. On GPT-6.2 it reasons as deeply as xhigh and also lets Codex hand parts of the work to subagents on its own.
- **medium** is fine for quick look-ups and small edits, if you start Codex without the profile.

The profile sets these:

```toml
model_reasoning_effort = "xhigh"
plan_mode_reasoning_effort = "xhigh"
model_verbosity = "medium"

[agents]
default_subagent_reasoning_effort = "xhigh"
```

So effort is xhigh, including in Plan mode and for subagents such as the judge, and verbosity is medium instead of Codex's low default, which leaves room in the final message for what each round improved and what is still open. Codex layers the profile on top of your `~/.codex/config.toml`, so nothing else changes. From a clone you can copy it with `cp profiles/tryhard.config.toml ~/.codex/`.

To switch to ultra, pick one:

- For one session, start Codex with `codex --profile tryhard -c model_reasoning_effort=ultra`.
- Inside a session, choose Ultra under `/model`. In the desktop app, Ultra may first need turning on under Settings > Configuration.
- To make it your default, change `model_reasoning_effort` to `"ultra"` in `~/.codex/tryhard.config.toml`.

Why ultra isn't the default: it is limited to some accounts. Codex accepts the setting either way and starts normally, but when your account's model list doesn't offer ultra, it quietly falls back to the model's default effort, which is low for GPT-6.2. Every GPT-6 model offers xhigh, and if a model doesn't, Codex steps down to the highest level below it. Keep the subagent line at xhigh even when you use ultra. Codex refuses to start a subagent at a level its model doesn't offer, so ultra there would make every spawn fail on accounts without it.

</details>

<details>
<summary><b>The optional always-on block for AGENTS.md</b></summary>

<br>

Skills only apply on the turns where they trigger. A short block in `~/.codex/AGENTS.md` keeps the short form of the loop on every turn: write a brief with a review bar, build the whole thing, use it for real, have a fresh subagent judge it READY or NOT READY (a labelled self-review when subagents aren't available), fix what is confirmed, stop at READY, a round that doesn't help or 3 rounds, and report plainly. To add it, clone the repo and run the installer:

```bash
git clone https://github.com/AbhishekBarali/tryhard.git
cd tryhard
./install.sh
```

`install.sh` backs up `~/.codex/AGENTS.md` (or `$CODEX_HOME/AGENTS.md` if you set `CODEX_HOME`), adds the block between two marker lines (running it again does not add a second copy) and prints the plugin steps above. It changes nothing else. The block itself is in `agents-md/AGENTS.snippet.md` if you prefer to paste it by hand.

</details>

<details>
<summary><b>How the Stop hook works, and how to turn it off</b></summary>

<br>

When Codex is about to end a turn, the hook reads the final message and can send the model back once with a short note. It checks three things:

1. The message ends by offering to do work that belongs to the task ("Shall I...?", "Want me to...?"). The model is told to do it if it is in scope and reversible, or to list it as an open item with a default if it truly needs you.
2. The message ends with a question about files, IDs or paths you never mentioned. The model is told to inspect its own work, decide and continue.
3. A long final message is hard to read: its opening is packed with code names or runs very long, or a paragraph strings clauses together with semicolons. The model is told to rewrite the message in plain words without redoing the work.

It sends the model back at most once per turn, turns a check off for the rest of the session after it fires 3 turns in a row, and does nothing if anything goes wrong. It stays out of Plan mode, and an offer at the end of an answer to a question, a review or a plan you asked for doesn't count as a hand-back.

To turn it off, untrust or disable it in `/hooks`. The hook also reads two environment variables, which have to be set in the environment Codex starts with:

```bash
# Hook off for this session
TRYHARD_HOOK=off codex

# Run only some of the checks
TRYHARD_CHECKS=handback,own-work codex
```

`TRYHARD_CHECKS` takes a comma-separated list of `handback`, `own-work` and `readability`, or `all` or `none`.

</details>

<details>
<summary><b>Updating and installing from a local clone</b></summary>

<br>

Codex copies the plugin when you install it, so an update takes two commands. If you installed from GitHub, the first refreshes Codex's copy of the repo and the second reinstalls the plugin:

```bash
codex plugin marketplace upgrade tryhard
codex plugin add tryhard@tryhard
```

From a local clone you can pass the folder instead of the GitHub name:

```bash
codex plugin marketplace add /path/to/tryhard
```

`marketplace upgrade` works only for GitHub and other Git installs. To update a local-clone install, run `git pull` in the clone, then:

```bash
codex plugin add tryhard@tryhard
```

Codex asks you to trust the hook again in `/hooks` after any update to the plugin, because the approval covers every file in it, not only the hook. Editing a skill is enough to trigger it.

</details>

<details>
<summary><b>Uninstall</b></summary>

<br>

If you added the always-on block, run `./install.sh --remove` from the clone. You can also delete the two Tryhard marker lines and everything between them in `~/.codex/AGENTS.md` (the installer left a backup next to it). Then remove the plugin:

```bash
codex plugin remove tryhard@tryhard
codex plugin marketplace remove tryhard
```

To forget the hook approval too, delete the `[hooks.state."tryhard@tryhard:hooks/hooks.json:stop:0:0"]` table from `~/.codex/config.toml`. If you copied the profile, delete `~/.codex/tryhard.config.toml`. The Stop hook keeps small per-session files under `~/.codex/plugins/data/`. Delete the Tryhard folder there to remove everything.

</details>

## Learn more

- [docs/why.md](docs/why.md) explains each problem above, with the reports and sources behind it.
- [evals/](evals/README.md) has trigger prompts for the three automatic skills and scenario tasks built from real reports, including two for the default loop, each with checkable points for good and bad behaviour. Run them with and without the plugin on your own setup and compare.

## License

[MIT](LICENSE)
