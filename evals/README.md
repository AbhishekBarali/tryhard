# Evals

Two sets of checks you can run on your own setup, with and without Tryhard, to see what it
changes for you.

- `triggers/` holds prompts for the three skills that trigger on their own. Each file has 20 prompts. Half should trigger the skill and half are near-misses that should not.
- `scenarios/` holds 10 small tasks built from real reports about GPT-6.2. Each has a setup script, the prompt, and checkable points for good and bad behaviour.

Nothing here has published results. These are tools for your own comparison.

## Keep the comparison fair

- Use the same Codex version, model, reasoning effort and sandbox mode for both sides.
- Start every run from a fresh setup in a new directory outside any repo, so no other `AGENTS.md` or skills get picked up.
- Run each prompt at least 3 times per side. Single runs vary a lot.
- Don't show the scenario READMEs to the model. They contain the answers.
- Keep the doing and the grading apart. One agent does the task from the prompt alone, and a different agent, or you, grades the result against the scenario README. An agent that has read the README to grade can't also do the task blind.
- Write down the effort level. Effort alone changes results a lot, so it is worth one extra pair of runs at low and at high.

## Switching Tryhard on and off

**With** means the plugin is installed, its hook is trusted in `/hooks`, and, if you use it, the
always-on block is in `~/.codex/AGENTS.md`.

**Without** means none of those. The simplest way is to run all the "without" runs first, then
install, or to remove and re-add between batches:

```bash
codex plugin remove tryhard@tryhard   # without
codex plugin add tryhard@tryhard      # with (check /hooks afterwards)
```

Move the always-on block out of `~/.codex/AGENTS.md` for the "without" runs. The installer made a
backup when it added the block.

A quicker switch is a profile that disables the plugin. Save this as
`~/.codex/no-tryhard.config.toml`:

```toml
[plugins."tryhard@tryhard"]
enabled = false
```

Then run `TRYHARD_HOOK=off codex --profile no-tryhard`. Check in `/skills` that the
Tryhard skills are gone before you trust the run. The AGENTS block still needs moving by
hand.

To see what each part does alone, a third side is useful: plugin installed, AGENTS block absent.

## Trigger tests

These only make sense with the plugin installed. For each prompt, start a fresh session in an
empty scratch repo, send the prompt and check whether the model opened that skill's `SKILL.md`.

A non-interactive loop, with a read-only sandbox so nothing is changed:

```bash
mkdir -p /tmp/tryhard-trigger && cd /tmp/tryhard-trigger && git init -q
skill=fresh-ideas
jq -c '.' ~/tryhard/evals/triggers/$skill.jsonl | while read -r row; do
  id=$(echo "$row" | jq -r .id)
  prompt=$(echo "$row" | jq -r .prompt)
  expected=$(echo "$row" | jq -r .should_trigger)
  codex exec --ephemeral --sandbox read-only --json "$prompt" > "$id.jsonl" 2>/dev/null
  if grep -q "skills/$skill/SKILL.md" "$id.jsonl"; then got=true; else got=false; fi
  echo "$id expected=$expected got=$got"
done | tee "$skill-results.txt"
```

Change the path to wherever you cloned the repo. You can also run the prompts by hand in the
CLI, where you can see the model open the skill file.

What to look at:

- How many of the 10 "should trigger" prompts triggered the skill. Misses mean the description is too narrow for how you phrase things.
- How many of the 10 near-misses triggered it. These should be close to zero. A near-miss that triggers is the more serious problem, because it puts a long procedure on a task that doesn't need it.
- A near-miss that triggers a different Tryhard skill is fine. Only the skill named in the file counts.

Each row has a `why` field explaining the intent, so you can judge borderline cases.

## Scenario tests

Each folder in `scenarios/` has a `setup.sh` and a `README.md`:

```bash
cd ~/tryhard/evals/scenarios/03-qa-must-fix
./setup.sh /tmp/tryhard-03-with-1
cd /tmp/tryhard-03-with-1
codex          # paste the prompt from the scenario README
```

Use a new directory for every run, such as `/tmp/tryhard-03-without-1`, `/tmp/tryhard-03-with-1`. Run in
the normal interactive CLI with workspace write access, the way you would work. When the turn
ends, go through the good and bad points in the scenario README and run its "Check" commands.

| Scenario | What it is about | Most telling point |
|---|---|---|
| 01 own output files | a long run hits a question about files it wrote | did it ask, or inspect and decide |
| 02 why is it slow | a "why" explanation | is the one cause in the first sentence, with evidence |
| 03 QA must fix | a QA request | how many of the bugs were fixed and re-checked, including bad `done` numbers |
| 04 unique level | an open creative choice | names and themes across several runs |
| 05 perf goal with side goal | a `/goal` with "faster, also smaller" | any kept change that is slower, and baseline vs final |
| 06 literal length rule | "at most 20 characters" | any rule beyond length |
| 07 offer instead of doing | in-scope work left as an offer | does the turn end on "Shall I...?" |
| 08 question only | a question with a visible bug | were any files changed |
| 09 one-line game | a short request for a whole game | a brief, real play, a fresh judge's READY or NOT READY, fixes and a plain report, with no push from you |
| 10 feature fills gaps | "add a search command" | bad input and help text handled, nothing unrelated added |

Scenario 08 checks the other direction. The push to finish should not turn a question into
code changes. Scenarios 09 and 10 test the default loop. Scenario 09 is a new game, so it should
get the full loop. The first judgment is round 0 and each fix-then-judge after it is one round, so
it should stop at READY, at a round that improves nothing, or after 3 rounds (at most four
judgments). Scenario 10 adds a subcommand shaped like the existing ones, which makes it a small
change: a short brief, a real run and one judge pass is the right size, and more rounds than that
count against it.

### Trying raise-the-bar

Scenario 09 also works for `raise-the-bar`. Run it with the prompt
`$tryhard:raise-the-bar Make a Snake game I can play in the browser.` and compare it with a plain
"with" run. After the run, check the following.

```bash
ls -A .tryhard               # .gitignore  brief.md  evidence  rounds.md  versions
cat .tryhard/.gitignore      # *
git status --short           # .tryhard/ is not listed
cat .tryhard/rounds.md       # round 0, then one line per round, each with READY or NOT READY
```

The run should end at READY or after 8 rounds (at most nine judgments), with the best version in
place. If Codex could not
start a goal, the final message should give the `/goal` line to paste.

## What to record

One row per run is enough:

| Scenario | Side | Run | Effort | Good points met | Bad points hit | Questions to you | Turns | Tokens | Minutes |
|---|---|---|---|---|---|---|---|---|---|
| 03 | without | 1 | high | | | | | | |
| 03 | with | 1 | high | | | | | | |

- **Good points met** and **bad points hit** come from the checklists.
- **Questions to you** counts every question that stopped the run or ended a turn.
- **Turns** counts turns including any the Stop hook started. The hook should add at most one per turn.
- **Tokens** and **minutes** show the cost. For real work Tryhard runs a judge-and-fix loop, so those runs will cost more than a single pass. Quick edits and questions should cost about the same on both sides. Compare that cost with what you got for it.

Compare the sides per scenario, not as one total. A difference that shows up in one run out of
three is not yet a difference. If you share results, include the Codex version, model, effort
and run count.
