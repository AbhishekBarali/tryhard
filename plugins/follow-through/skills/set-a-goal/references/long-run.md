# Long-run rules

Read this before writing the goal contract and again after the conversation is compacted. Codex's
own goal instructions still apply on every turn. These rules add a measurement, so that each turn's
work is judged by the numbers in `.goal/contract.md`.

## Start of every turn

Read `.goal/status.md`, the last lines of `.goal/ledger.tsv` and `git log --oneline -10`. The best
commit is the latest keep in the ledger, or the baseline commit before the first keep. If the
checkout holds an attempt that was never measured, measure it and keep or discard it as usual. If
the checkout is anywhere else, or anything changed since the last measurement, return to the best
commit and rerun the primary measurement before new work. Finished attempts stay finished, so pick
up from the next step in the status file.

## The primary goal wins

Discard any change that makes the primary metric worse by more than the noise level, whatever it
does for a secondary goal. Work on a secondary goal only once the primary target is met, or with
changes that leave the primary metric level or better. Guardrails hold throughout.

## One idea per attempt

1. Write down the idea and the effect you expect.
2. Make the change and commit it.
3. Measure with the contract's command. Iterate on a fast sample when the full run is slow, and run
   the full measurement before any keep.
4. Keep the commit only if it beats the best result so far by more than the noise level and every
   guardrail holds. Otherwise check `git status` for anything that is not part of the attempt, then
   reset to the best commit with `git reset --hard`, which discards only your own attempt.
5. Append one row to the ledger.

Stop an attempt that runs past twice its expected time and log it as a crash. Measure each change on
its own, since stacked unmeasured changes hide which one helped. Aim to land a first small keep
early, so there is always a measured result to hand back.

## Ledger and status

`.goal/ledger.tsv` is append-only, with one row per attempt and the columns attempt, commit, idea,
expected effect, primary result, guardrail results, outcome (keep, discard or crash) and a short
note.

Rewrite `.goal/status.md` after every keep, after every change of approach, and at least every five
attempts. It holds the baseline and the best result, the current approach, the approaches that
failed and why, and the next step. Keep it under a page, because it is what you read after a
compaction.

## Protect the measurement

Tests, benchmarks and evaluation scripts are read-only unless the contract says otherwise. A number
that improved because the measurement changed is no result. Measurement commands print a short
summary and write full output to `.goal/logs/`.

## When it stalls

Codex's goal instructions already ask whether each turn made progress. This rule counts keeps.

- After three attempts in a row without a keep, stop adjusting the same idea. Re-read the contract,
  write three approaches that use different mechanisms (new parameters for the same idea count as
  the same mechanism), pick the one least like what failed, and log the change of approach in the
  ledger. A keep resets this count.
- Allow two such changes of approach in a row. When the second new approach has also gone three
  attempts without a keep, write a stall report into `.goal/status.md` and the final message. It
  gives the baseline and the best result, what was tried, why the number is not moving, and the
  decision that would unblock it. That decision usually belongs to the user, such as accepting the
  best result so far, relaxing a guardrail, changing the target, or providing a resource like more
  hardware or data.
- Then follow Codex's blocked rule. Leave the goal active and report the stall. On each following
  goal turn, check whether anything changed, such as a reply from the user, new evidence, or an
  approach the report did not cover. If something did, act on it under the same limits. If nothing
  did, keep the turn short and report the same stall in a line or two. When the same stall has held
  for three consecutive goal turns, counting the turn that wrote the report, call `update_goal` with
  status `blocked`.

Codex reserves pausing a goal for the user, and marking it blocked before the third turn skips its
audit, so neither is a way out of a stall.

## Done

Before claiming the goal is complete, have a fresh evaluator check the work using
`references/evaluator-brief.md`. Give it to a subagent started without your conversation history
(with `fork_turns` set to `none` where the spawn tool has that option). If subagents are
unavailable, do the same check yourself, starting from only the contract, the diff and the commands.

When the evaluator fails an item, fix it or revert, then run the evaluator again. If the same item
fails twice after fixes, handle it under the stall rule.

When every done item passes, close the run.

1. Rerun the primary measurement on the final commit and compare it with the baseline.
2. Stop any background jobs you started and delete your own temporary files.
3. Run the completion audit from Codex's goal instructions, then call `update_goal` with status
   `complete`.
4. Report the baseline and the final number, what changed, what was dropped and why, what remains,
   and the branch the work is on.
