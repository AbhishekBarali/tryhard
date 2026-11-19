<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-light.svg">
  <img alt="Tryhard" src="docs/assets/banner-light.svg">
</picture>

<p><b>GPT-6.2 coasts. Tryhard makes it finish.</b><br>
A Codex plugin that makes it do the whole job, check it, and say plainly what happened.</p>

<p>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-2f6feb"></a>
  <a href="plugins/tryhard/.codex-plugin/plugin.json"><img alt="Version 0.2.0" src="https://img.shields.io/badge/version-0.2.0-C2410C"></a>
  <a href="docs/why.md"><img alt="For GPT-6.2 Astra and Sol" src="https://img.shields.io/badge/GPT--6.2-Astra%20%26%20Sol-5b6170"></a>
</p>

</div>

## Why

GPT-6.2 Astra and Sol can do the work. They just don't do it properly or all the way. Since
launch, people using them in Codex keep reporting the same thing: the model lists bugs instead of
fixing them, stops halfway with "Shall I continue?", does the smallest version that runs, and hands
over its first draft as the finished thing.

Tryhard flips it into tryhard mode. Five skills and a small Stop hook make it agree what "done
properly" means before it starts, hold itself to that, check the result, and keep improving it when
you ask for more.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/before-after-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/before-after-light.svg">
  <img alt="Four habits, each shown as the model's message without Tryhard and with it: stops at a list, stops halfway, does the bare minimum, ships the first draft" src="docs/assets/before-after-light.svg">
</picture>

What it targets:

- **Half-done work.** It agrees what "done properly" looks like before starting: every part of the request, the cases it implies, checked for real. A QA request ends in fixes, not a list of issues.
- **Stopping halfway.** When the next step is part of the task, it does it instead of asking "Shall I continue?".
- **First drafts passed off as finished.** On request, it reviews its own work like a demanding expert and improves it until another pass stops helping.
- **The same answer as everyone else.** When a task leaves a real creative choice open, it sets the obvious default aside and picks on fit.
- **Loops that go nowhere.** Long runs get a measured starting point, one main goal, a keep-only-what-improves rule and a clear stop.
- **Questions nobody can answer.** It looks things up and decides routine choices itself, and it never asks you about files it made.
- **Explanations you can't read.** The final message leads with the answer or the main cause, in plain words, then says what is still open.

## Quick start

You need the Codex CLI or the Codex desktop app. The Stop hook also needs Python 3.8 or newer as
`python3` (macOS, Linux) or `python` (Windows) on your PATH. The skills work without it.

```bash
codex plugin marketplace add AbhishekBarali/tryhard
codex plugin add tryhard@tryhard
```

Then start Codex, open `/hooks` and trust the Tryhard Stop hook. Codex skips plugin hooks until
you trust them, so without this step the hook never runs. In the desktop app the same list is
under Settings > Hooks.

Installed the earlier version under its old name? Remove it, then install and trust the hook as above:

```bash
codex plugin remove follow-through@follow-through
codex plugin marketplace remove follow-through
```

A higher-effort profile and an always-on block for `AGENTS.md` are optional. Both are under
[More details](#more-details).

## What's inside

**Automatic.** These trigger from what you ask, so there is nothing to type.

- `finish-the-job` agrees what done means, does the whole job and checks it. It runs for multi-step coding, debugging, QA, build or investigation work.
- `fresh-ideas` sets the obvious answer aside and picks on fit. It runs when a task leaves open a choice you will see, such as a name, a theme, a level concept or a visual direction.
- `explain-plainly` leads with the answer or the main cause, in plain words. It runs when you ask why something happens, ask for a summary, or say you are confused.

**By name.** These run only when you call them.

- `raise-the-bar` builds a first version, then improves it in expert review rounds.
- `set-a-goal` sets up a long-running `/goal` with a measured baseline.

**Stop hook.** Once you trust it, it catches hand-backs, needless questions and dense reports.

## Usage

### Raise the bar

```text
$tryhard:raise-the-bar Build a landing page for a small bakery in Lisbon.
```

`raise-the-bar` writes down what a demanding expert would check, builds a complete first version,
looks at it for real, then reviews and improves it in rounds. It stops when a round finds only
minor issues or makes no visible difference, after at most 5 rounds unless you give another
number. It costs more than a single pass. It keeps a copy of each version in a temp folder, so a
round that makes things worse can be undone without touching your branches or commits.

### Set a goal

```text
$tryhard:set-a-goal Make the test suite run under 2 minutes without dropping tests.
```

`set-a-goal` turns a request into a Codex `/goal` for a long run. It measures the starting value
first, then writes `.goal/contract.md` with the main measure and the command for it, the side goals
in order, what is out of scope and how "done" is proved. Then it starts the goal, or gives you the
exact `/goal` line to paste.

It sets a token budget only if you name one in your request. To cap every goal, set
`max_goal_token_budget` under `[goals]` in `~/.codex/config.toml`.

It changes your workspace and git state. The section below says exactly how, so read it before
the first run.

## More details

<details>
<summary><b>What set-a-goal does to your files and git</b></summary>

<br>

- It creates a `.goal/` folder (contract, attempt ledger, status and logs) and adds it to the
  repo's local exclude file, `.git/info/exclude`, so it never shows up in commits. Dependency
  folders, build output, large data files and anything that looks like a secret go in the same
  exclude file if git doesn't already ignore them.
- If the project folder is not a git repository yet, it runs `git init` there and commits the
  current files. It never does this in your home folder or in a folder that holds other
  repositories. Started from one of those, it sets up in the project folder your request is about,
  and asks which one if the request doesn't say.
- It works on a new branch named `goal/` plus a short name and leaves your own branch where it was.
  Any uncommitted changes you had become the first commit on that branch. To get them back on your
  branch, `git switch` to it and run `git cherry-pick --no-commit` on that first commit. The final
  message tells you which of these steps it took.
- Every attempt is a commit. An attempt that doesn't beat the best result so far is dropped with
  `git reset --keep`, which leaves your other local changes in place.

</details>

<details>
<summary><b>Reasoning effort and the optional profile</b></summary>

<br>

Codex's model catalog sets both GPT-6.2 models to low effort by default. OpenAI's launch charts
show a benchmark score at low effort falling sharply compared with the previous models, and
OpenAI's own guide says higher effort helps the model stay with a long task through the final
checks. So use more for real work:

- **high** or **xhigh** for multi-step builds, debugging and investigations.
- **ultra** for work that splits into parallel parts. Codex then decides on its own when to use subagents.
- **medium** is fine for quick look-ups and small edits.

Set it with `/model` in the CLI, or in a profile. The repo has one. From a clone:

```bash
cp profiles/tryhard.config.toml ~/.codex/tryhard.config.toml
codex --profile tryhard
```

It sets these:

```toml
model_reasoning_effort = "high"
plan_mode_reasoning_effort = "high"
model_verbosity = "medium"

[agents]
default_subagent_reasoning_effort = "high"
```

So reasoning effort is high, including in Plan mode and for subagents, and verbosity is medium
instead of Codex's low default, which leaves room in the final message for how the work was checked
and what is still open. The comments in the file say when to switch to xhigh or ultra. Codex layers the profile on top of
your `~/.codex/config.toml`, so nothing else changes.

</details>

<details>
<summary><b>The optional always-on block for AGENTS.md</b></summary>

<br>

Skills only apply on the turns where they trigger. A short block in `~/.codex/AGENTS.md` keeps the
core habits on every turn. To add it, clone the repo and run the installer:

```bash
git clone https://github.com/AbhishekBarali/tryhard.git
cd tryhard
./install.sh
```

`install.sh` backs up `~/.codex/AGENTS.md` (or `$CODEX_HOME/AGENTS.md` if you set `CODEX_HOME`),
adds the block between two marker lines (running it again does not add a second copy) and prints
the plugin steps above. It changes nothing else. The block itself is in
`agents-md/AGENTS.snippet.md` if you prefer to paste it by hand.

</details>

<details>
<summary><b>How the Stop hook works, and how to turn it off</b></summary>

<br>

When Codex is about to end a turn, the hook reads the final message and can send the model back
once with a short note. It checks three things:

1. The message ends by offering to do work that belongs to the task ("Shall I...?", "Want me to...?"). The model is told to do it if it is in scope and reversible, or to list it as an open item with a default if it truly needs you.
2. The message ends with a question about files, IDs or paths you never mentioned. The model is told to inspect its own work, decide and continue.
3. A long final message is hard to read: its opening is packed with code names or runs very long, or a paragraph strings clauses together with semicolons. The model is told to rewrite the message in plain words without redoing the work.

It sends the model back at most once per turn, turns a check off for the rest of the session after
it fires 3 turns in a row, and does nothing if anything goes wrong. It stays out of Plan mode, and
an offer at the end of an answer to a question, a review or a plan you asked for doesn't count as a
hand-back.

To turn it off, untrust or disable it in `/hooks`. The hook also reads two environment variables,
which have to be set in the environment Codex starts with:

```bash
# Hook off for this session
TRYHARD_HOOK=off codex

# Run only some of the checks
TRYHARD_CHECKS=handback,own-work codex
```

`TRYHARD_CHECKS` takes a comma-separated list of `handback`, `own-work` and `readability`, or
`all` or `none`.

</details>

<details>
<summary><b>Updating and installing from a local clone</b></summary>

<br>

Codex copies the plugin when you install it, so an update takes two commands. If you installed
from GitHub, the first refreshes Codex's copy of the repo and the second reinstalls the plugin:

```bash
codex plugin marketplace upgrade tryhard
codex plugin add tryhard@tryhard
```

From a local clone you can pass the folder instead of the GitHub name:

```bash
codex plugin marketplace add /path/to/tryhard
```

`marketplace upgrade` works only for GitHub and other Git installs. To update a local-clone
install, run `git pull` in the clone, then:

```bash
codex plugin add tryhard@tryhard
```

Codex asks you to trust the hook again in `/hooks` after any update to the plugin, because the
approval covers every file in it, not only the hook. Editing a skill is enough to trigger it.

</details>

<details>
<summary><b>Uninstall</b></summary>

<br>

If you added the always-on block, run `./install.sh --remove` from the clone. You can also delete
the two Tryhard marker lines and everything between them in `~/.codex/AGENTS.md` (the installer
left a backup next to it). Then remove the plugin:

```bash
codex plugin remove tryhard@tryhard
codex plugin marketplace remove tryhard
```

To forget the hook approval too, delete the
`[hooks.state."tryhard@tryhard:hooks/hooks.json:stop:0:0"]` table from `~/.codex/config.toml`.
If you copied the profile, delete `~/.codex/tryhard.config.toml`. The Stop hook keeps small
per-session files under `~/.codex/plugins/data/`. Delete the Tryhard folder there to remove
everything.

</details>

## Learn more

- [docs/why.md](docs/why.md) explains each problem above, with the reports and sources behind it.
- [evals/](evals/README.md) has trigger prompts for the three automatic skills and scenario tasks
  built from real reports, each with checkable points for good and bad behaviour. Run them with
  and without the plugin on your own setup and compare.

## License

[MIT](LICENSE)
