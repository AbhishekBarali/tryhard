---
name: set-a-goal
description: Turn a request into a strong Codex /goal for a long run. Writes a goal contract with a measured baseline, ranked goals and checkable done items, starts the goal, and sets rules for keeping only what improves and for handling stalls. Use when the user invokes it by name.
---

# Set a goal

A long run goes nowhere when nothing measures it. Without a baseline every change looks like
progress, unranked goals let the easiest side goal take over, and without a stall rule the run can
spin for days. This skill sets those up before the first edit, then starts a Codex goal that points
at them.

The user's own words win over anything here.

## 1. Gather what you need without asking

Read the request and the repo. Find how the main outcome can be measured (a benchmark, a test suite,
a size, a timing, a score) and how to run it. If the user gave no number, pick the measurement that
best represents the main request. Decide the rest yourself and record each decision in the contract.
Ask the user only when the answer is something only they know, it would change the result in a way
that is costly to redo, and no reasonable default exists.

## 2. Prepare the workspace and measure the baseline

Create `.goal/` at the workspace root and keep it out of git by adding `.goal/` to the exclude file
that `git rev-parse --git-path info/exclude` prints. That way resets during the run never touch the
contract or the ledger. If the workspace is not a git repository, initialise one and commit the
untouched state. Do the run's work on a new branch named `goal/` plus a short name. If there are
uncommitted changes at the start, commit them as the first commit on that branch. Mention any of
these in the final message.

Before changing anything else, run the measurement on the untouched code. For a noisy measurement,
run it three to five times, record the median, and treat the spread as the noise level. Save full
output under `.goal/logs/` and keep what you read back to a short summary.

## 3. Write the contract

Write `.goal/contract.md` with one heading per section and short plain text under each.

- The objective, in one sentence and in the user's terms.
- The primary metric, with what is measured, the exact command, the baseline and the commit it was
  taken on, the target, and the noise level.
- Guardrails, meaning other measurements that must stay within a stated tolerance of their baseline.
- Secondary goals in priority order. They count only while the primary metric holds.
- Non-goals.
- Done when, as a short list of checkable items, each with the command or observation that proves
  it.
- Budgets, giving a time limit per attempt, the stall limits from the long-run rules, and the token
  budget if the user gave one.
- Decisions, one line each, giving what you chose, why, and how to change it.

For work without a number, such as a game level or a design, leave out the primary metric. The done
items carry the weight instead, together with a rubric of three to six checks the evaluator scores.
An attempt then counts as a keep when it turns a failing check into a passing one without breaking a
passing one.

## 4. Start the goal

If the `create_goal` tool is available, call it. The user invoked this skill to set up a goal, which
is the explicit request the tool asks for. Keep the objective short and point it at the contract, for
example like this.

    Meet every "Done when" item in .goal/contract.md. The primary metric, its baseline and the
    rules for keeping or discarding changes are in that file and in .goal/status.md.

Pass `token_budget` only when the user named a budget. If `create_goal` fails because an unfinished
goal already exists, leave that goal alone, since replacing it is the user's call. Give them the
`/goal` line to use once the current goal is cleared or finished.

If the tool is not available, end the turn after the contract and the baseline, and give the user
the exact line to paste, starting with `/goal `.

## 5. Run it

Once the goal is running, read [references/long-run.md](references/long-run.md) and start the first
attempt in the same turn. Read it again after the conversation is compacted. Before each evaluation,
read [references/evaluator-brief.md](references/evaluator-brief.md).

## The first turn's final message

Say that the goal is set, what it measures, the baseline and the target, the branch the work is on,
and the main decisions you made. If the user gave no token budget, say so in one line, and mention
that naming a budget when invoking this skill, or setting `max_goal_token_budget` under `[goals]` in
Codex's `config.toml`, puts a hard cap on future runs. The stall rule ends this run either way.
