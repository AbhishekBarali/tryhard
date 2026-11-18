# Follow Through

A Codex plugin for GPT-6.2 Astra and Sol. It helps the models carry a job to the end: agree what
"done" means, do the whole task, check it, and explain the result in plain words.

## What it fixes

- **Stopping early.** It agrees what finished looks like before starting, and a QA request ends in fixes, not a list of issues.
- **Questions nobody can answer.** It looks things up and decides routine choices itself, and it never asks you about files it made.
- **Loops that go nowhere.** Long runs get a measured starting point, one main goal, a keep-only-what-improves rule and a clear stop.
- **The same answer as everyone else.** When a task leaves a real creative choice open, it sets the obvious default aside and picks on fit.
- **Explanations you can't read.** The final message leads with the answer or the main cause, in plain words, then says what is still open.
- **First drafts passed off as finished.** On request, it reviews its own work like a demanding expert and improves it until another pass stops helping.

[docs/why.md](docs/why.md) explains each one, with the reports and sources behind it.

## Install

You need the Codex CLI or the Codex desktop app.

```bash
codex plugin marketplace add AbhishekBarali/follow-through
codex plugin add follow-through@follow-through
```

Then start Codex, open `/hooks` and trust the Follow Through Stop hook. Codex skips plugin hooks
until you trust them, so without this step the hook never runs. In the desktop app the same list
is under Settings > Hooks. You will be asked again after an update changes the hook.

### Optional: the always-on block

Skills only apply on the turns where they trigger. A short block in `~/.codex/AGENTS.md` keeps the
core habits on every turn. To add it, clone the repo and run the installer:

```bash
git clone https://github.com/AbhishekBarali/follow-through.git
cd follow-through
./install.sh
```

`install.sh` backs up `~/.codex/AGENTS.md`, adds the block between clear markers (running it again
does not add a second copy) and prints the plugin steps above. It changes nothing else. The block
itself is in `agents-md/AGENTS.snippet.md` if you prefer to paste it by hand.

### Optional: a profile with higher effort

See [Reasoning effort](#reasoning-effort) for why. From the clone:

```bash
cp profiles/follow-through.config.toml ~/.codex/follow-through.config.toml
codex --profile follow-through
```

## How to use it

Most of it works on its own. Three skills trigger from what you ask:

- `finish-the-job` for multi-step coding, debugging, QA, build or investigation work.
- `fresh-ideas` when a task leaves open a choice you will see, such as a name, a theme, a level concept or a visual direction.
- `explain-plainly` when you ask why something happens, ask for a summary, or say you are confused.

Two skills run only when you name them:

```text
$follow-through:raise-the-bar Build a landing page for a small bakery in Lisbon.
```

`raise-the-bar` writes down what a demanding expert would check, builds a complete first version,
looks at it for real, then reviews and improves it. It stops when a pass finds only minor issues
or makes no visible difference, after at most 5 passes unless you give another number. It costs
more than a single pass.

```text
$follow-through:set-a-goal Make the test suite run under 2 minutes without dropping tests.
```

`set-a-goal` turns a request into a Codex `/goal` for a long run. It writes `.goal/contract.md` in
your workspace with the main measure, how it is measured and its starting value, the side goals in
order, what is out of scope and how "done" is proved. Then it starts the goal, or gives you the
exact `/goal` line to paste. It also suggests a token budget so the run has a natural end.

## Reasoning effort

Codex's model catalog sets both GPT-6.2 models to low effort by default. OpenAI's launch charts
show scores at low effort falling sharply compared with the previous models, and OpenAI's own
guide says higher effort helps the model stay with a long task through the final checks. So use
more for real work:

- **high** or **xhigh** for multi-step builds, debugging and investigations.
- **ultra** for work that splits into parallel parts. Codex then decides on its own when to use subagents.
- **medium** is fine for quick look-ups and small edits.

Set it with `/model` in the CLI, or in a profile:

```toml
model_reasoning_effort = "xhigh"
# Optional. Codex defaults to low verbosity, and the launch reviews found 6.2 answers over-compressed.
model_verbosity = "medium"
```

## The Stop hook

When Codex is about to end a turn, the hook reads the final message and can send the model back
once with a short note. It checks three things:

1. The message ends by offering to do work that belongs to the task ("Shall I...?", "Want me to...?"). The model is told to do it if it is in scope and reversible, or to list it as an open item with a default if it truly needs you.
2. The message ends with a question about files, IDs or paths you never mentioned. The model is told to inspect its own work, decide and continue.
3. A long final message opens with a wall of code names or stacked semicolons. The model is told to rewrite it in plain words.

It sends the model back at most once per turn, goes quiet for the session after the same check
fires 3 times in a row, and does nothing if anything goes wrong. A plain question or a plan you
asked for is left alone.

To turn it off, untrust or disable it in `/hooks`. To turn it off from the shell you start Codex
from, set `FOLLOW_THROUGH_HOOK=off`. To keep only some checks, set `FOLLOW_THROUGH_CHECKS` to a
comma-separated list of `handback`, `own-work` and `readability`.

## Uninstall

```bash
codex plugin remove follow-through@follow-through
codex plugin marketplace remove follow-through
```

If you added the always-on block, delete the lines between the Follow Through markers in
`~/.codex/AGENTS.md` (the installer left a backup next to it). If you copied the profile, delete
`~/.codex/follow-through.config.toml`.

## Evals

[evals/](evals/README.md) has trigger prompts for the three automatic skills and scenario tasks
built from real reports, each with checkable points for good and bad behaviour. Run them with and
without the plugin on your own setup and compare.

## License

MIT
