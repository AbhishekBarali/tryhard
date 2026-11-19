<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-light.svg">
  <img alt="Done Done" src="docs/assets/banner-light.svg">
</picture>

<p><b>Is it done, or done done?</b> A Codex plugin that helps GPT-6.2 finish the whole job.</p>

<p>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-2f6feb"></a>
  <a href="#quick-start"><img alt="Codex plugin" src="https://img.shields.io/badge/Codex-plugin-1f2328"></a>
  <a href="plugins/donedone/.codex-plugin/plugin.json"><img alt="Version 0.2.0" src="https://img.shields.io/badge/version-0.2.0-C2410C"></a>
  <a href="docs/why.md"><img alt="For GPT-6.2 Astra and Sol" src="https://img.shields.io/badge/GPT--6.2-Astra%20%26%20Sol-5b6170"></a>
</p>

</div>

## Why

Since GPT-6.2 Astra and Sol came out, people using them in Codex keep reporting the same habits.
The model lists bugs instead of fixing them, ends a turn with "Shall I...?", asks you about files
it wrote itself, and explains the result in a wall of code names. Done Done adds five skills and a
small Stop hook that push it to agree what "done" means, do the whole task, check it, and tell you
plainly what happened.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/before-after-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/before-after-light.svg">
  <img alt="The same task in Codex without Done Done and with it" src="docs/assets/before-after-light.svg">
</picture>

What it targets:

- **Stopping early.** It agrees what finished looks like before starting, and a QA request ends in fixes, not a list of issues.
- **Questions nobody can answer.** It looks things up and decides routine choices itself, and it never asks you about files it made.
- **Loops that go nowhere.** Long runs get a measured starting point, one main goal, a keep-only-what-improves rule and a clear stop.
- **The same answer as everyone else.** When a task leaves a real creative choice open, it sets the obvious default aside and picks on fit.
- **Explanations you can't read.** The final message leads with the answer or the main cause, in plain words, then says what is still open.
- **First drafts passed off as finished.** On request, it reviews its own work like a demanding expert and improves it until another pass stops helping.

## Quick start

You need the Codex CLI or the Codex desktop app.

```bash
codex plugin marketplace add AbhishekBarali/donedone
codex plugin add donedone@donedone
```

Then start Codex, open `/hooks` and trust the Done Done Stop hook. Codex skips plugin hooks until
you trust them, so without this step the hook never runs. In the desktop app the same list is
under Settings > Hooks.

A higher-effort profile and an always-on block for `AGENTS.md` are optional. Both are under
[More details](#more-details).

## What's inside

| Name | How it runs | What it does |
|---|---|---|
| `finish-the-job` | Automatic | Agrees what done means, does the whole job, checks it. |
| `fresh-ideas` | Automatic | Sets the obvious answer aside when a real choice is open. |
| `explain-plainly` | Automatic | Leads with the answer or the main cause, in plain words. |
| `raise-the-bar` | By name | Builds a first version, then improves it in expert reviews. |
| `set-a-goal` | By name | Sets up a long-running `/goal` with a measured baseline. |
| Stop hook | Once trusted | Catches hand-backs, needless questions and dense reports. |

## Usage

### Automatic skills

These trigger from what you ask, so there is nothing to type:

- `finish-the-job` for multi-step coding, debugging, QA, build or investigation work.
- `fresh-ideas` when a task leaves open a choice you will see, such as a name, a theme, a level concept or a visual direction.
- `explain-plainly` when you ask why something happens, ask for a summary, or say you are confused.

The other two run only when you name them.

### Raise the bar

```text
$donedone:raise-the-bar Build a landing page for a small bakery in Lisbon.
```

`raise-the-bar` writes down what a demanding expert would check, builds a complete first version,
looks at it for real, then reviews and improves it in rounds. It stops when a round finds only
minor issues or makes no visible difference, after at most 5 rounds unless you give another
number. It costs more than a single pass. It keeps each version recoverable, for example as a
local commit on a work branch.

### Set a goal

```text
$donedone:set-a-goal Make the test suite run under 2 minutes without dropping tests.
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
  current files. It won't do this in your home folder or in a folder that holds other repositories.
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
cp profiles/donedone.config.toml ~/.codex/donedone.config.toml
codex --profile donedone
```

It sets these:

```toml
model_reasoning_effort = "high"        # "xhigh" for hard investigations, "ultra" for parallel work
plan_mode_reasoning_effort = "high"
# Codex defaults to low verbosity, and the launch reviews found 6.2 answers over-compressed.
model_verbosity = "medium"

[agents]
default_subagent_reasoning_effort = "high"
```

So reasoning effort is high, including in Plan mode and for subagents, and verbosity is medium.
The comments in the file say when to switch to xhigh or ultra. Codex layers the profile on top of
your `~/.codex/config.toml`, so nothing else changes.

</details>

<details>
<summary><b>The optional always-on block for AGENTS.md</b></summary>

<br>

Skills only apply on the turns where they trigger. A short block in `~/.codex/AGENTS.md` keeps the
core habits on every turn. To add it, clone the repo and run the installer:

```bash
git clone https://github.com/AbhishekBarali/donedone.git
cd donedone
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
3. A long final message opens with a wall of code names or stacked semicolons. The model is told to rewrite it in plain words.

It sends the model back at most once per turn, goes quiet for the session after the same check
fires 3 times in a row, and does nothing if anything goes wrong. A plain question or a plan you
asked for is left alone.

To turn it off, untrust or disable it in `/hooks`. The hook also reads two environment variables,
which have to be set in the environment Codex starts with:

```bash
DONEDONE_HOOK=off codex                       # hook off for this session
DONEDONE_CHECKS=handback,own-work codex       # run only these checks
```

`DONEDONE_CHECKS` takes a comma-separated list of `handback`, `own-work` and `readability`, or
`all` or `none`.

</details>

<details>
<summary><b>Updating, and installing from a local clone</b></summary>

<br>

From a local clone you can pass the folder instead of the GitHub name:

```bash
codex plugin marketplace add /path/to/donedone
```

Codex copies the plugin when you install it, so after pulling changes run these again:

```bash
codex plugin marketplace upgrade donedone
codex plugin add donedone@donedone
```

Codex asks you to trust the hook again in `/hooks` after any update to the plugin, because the
approval covers every file in it, not only the hook. Editing a skill is enough to trigger it.

</details>

<details>
<summary><b>Uninstall</b></summary>

<br>

If you added the always-on block, run `./install.sh --remove` from the clone. You can also delete
the two Done Done marker lines and everything between them in `~/.codex/AGENTS.md` (the installer
left a backup next to it). Then remove the plugin:

```bash
codex plugin remove donedone@donedone
codex plugin marketplace remove donedone
```

To forget the hook approval too, delete the
`[hooks.state."donedone@donedone:hooks/hooks.json:stop:0:0"]` table from `~/.codex/config.toml`.
If you copied the profile, delete `~/.codex/donedone.config.toml`.

</details>

## Learn more

- [docs/why.md](docs/why.md) explains each problem above, with the reports and sources behind it.
- [evals/](evals/README.md) has trigger prompts for the three automatic skills and scenario tasks
  built from real reports, each with checkable points for good and bad behaviour. Run them with
  and without the plugin on your own setup and compare.

## License

[MIT](LICENSE)
