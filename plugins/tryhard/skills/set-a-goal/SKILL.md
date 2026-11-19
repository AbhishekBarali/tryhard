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

In Plan mode, explore and measure only in ways that leave tracked files alone, put the contract in
the plan, and leave the branch, the files and the goal for after Plan mode ends.

## 1. Gather what you need without asking

Read the request and the repo. Find how the main outcome can be measured (a benchmark, a test suite,
a size, a timing, a score) and how to run it. If the user gave no number, pick the measurement that
best represents the main request. Decide the rest yourself and record each decision in the contract.
Ask the user only when the answer is something only they know, it would change the result in a way
that is costly to redo, and no safe default exists. In that rare case, finish the baseline and the
contract with the question marked open, then ask with your recommended option first, through a
question tool if one is available or in the final message otherwise. Start the goal once it is
answered, since a goal started on the wrong target would spend the whole run on it.

## 2. Prepare the workspace and measure the baseline

Every attempt is a commit that can be undone, so the run needs its own branch and a starting commit
that holds exactly the code the user is running. Set that up as follows, and leave the user's own
branch where it is.

- If the workspace is not a git repository, initialise one. Do this only in a single project folder.
  If the workspace is the home directory or holds other repositories, set up in the project folder
  the request is about, and ask which one only if the request does not say.
- Create `.goal/` at the workspace root and add `.goal/` to the exclude file that
  `git rev-parse --git-path info/exclude` prints, so resets never touch the contract or the ledger.
  Add dependency folders, build output, large data files and anything that looks like a secret to
  the same file if git does not already ignore them, so they never enter a commit.
- Create a branch named `goal/` plus a short name from the current commit and switch to it.
- If there are uncommitted changes, including new files, or the repository is new, commit the files
  as they are on that branch as the baseline commit. When they are the user's uncommitted work, say
  so in the commit message. A reset to an earlier commit would otherwise undo or delete them.

In the final message, say which of these you did. For a baseline made from uncommitted work, add
that `git switch` back to their branch followed by `git cherry-pick --no-commit` of the baseline
commit puts that work back where it was.

Before changing anything else, run the measurement on the untouched code. For a timing or another
noisy measurement, run it three to five times, record the median, and treat the spread as the noise
level. Save full output under `.goal/logs/` and keep what you read back to a short summary.

## 3. Write the contract

Read [references/long-run.md](references/long-run.md) first, because the contract records its limits
and the run follows its rules. Then write `.goal/contract.md` with one heading per section and short
plain text under each.

- The objective, in one sentence and in the user's terms.
- The primary metric, with what is measured, the exact command, the baseline and the commit it was
  taken on, the target, and the noise level.
- Guardrails, meaning other measurements that must stay within a stated tolerance of their baseline.
- Secondary goals in priority order, each with a target or an attempt limit. Use three attempts when
  the user gave neither, because an open-ended "if you can" never finishes. They count only while
  the primary metric holds.
- Non-goals.
- Done when, as a short list of checkable items, each with the command or observation that proves
  it. Each secondary goal is an item that passes once it reaches its target or uses its attempts.
- Budgets, giving the expected time for one attempt, the stall limits from the long-run rules, and
  the token budget if the user gave one.
- Decisions, one line each, giving what you chose, why, and how to change it.
- The full path of [references/long-run.md](references/long-run.md), so the rules can be found
  again after a compaction.

Then start `.goal/ledger.tsv` with its header row and `.goal/status.md` with the baseline and the
first step, since every later turn begins by reading them.

For work without a number, such as a game level or a design, leave out the primary metric. The done
items carry the weight instead, together with a rubric of three to six checks the evaluator scores.
An attempt then counts as a keep when it turns a failing check into a passing one without breaking a
passing one.

## 4. Start the goal

If the `create_goal` tool is available, call it. The user invoked this skill to set up a goal, which
is the explicit request the tool asks for. Keep the objective short. Start it with the one-sentence
objective from the contract and point it at the contract for the rest, for example like this.

    {The one-sentence objective.} Done means every "Done when" item in .goal/contract.md passes.
    The primary metric, its baseline and the rules for keeping or discarding changes are in that
    file, and the current state is in .goal/status.md.

Pass `token_budget` only when the user named a budget. If `create_goal` fails because an unfinished
goal already exists, leave that goal alone, since replacing it is the user's call. Give them the
`/goal` line to use once the current goal is cleared or finished.

If the tool is not available, end the turn after the contract and the baseline, and give the user
the exact line to paste, starting with `/goal `.

## 5. Run it

Once the goal is running, start the first attempt in the same turn, following
[references/long-run.md](references/long-run.md). Read that file again after the conversation is
compacted or a new context window starts. Before each evaluation, read
[references/evaluator-brief.md](references/evaluator-brief.md).

## The first turn's final message

Say that the goal is set, what it measures, the baseline and the target, the branch the work is on,
and the main decisions you made. If the user gave no token budget, say so in one line. Mention that
naming a budget when invoking this skill, or setting `max_goal_token_budget` under `[goals]` in
Codex's `config.toml`, puts a hard cap on future runs, and that this run still ends with a report if
it stops improving.
