---
name: raise-the-bar
description: Max mode for the biggest asks. Runs the same brief, bar and fresh-eyes judge as finish-the-job with a stricter bar and more rounds, as a Codex goal that keeps going across turns when the goal tools are available. Use when the user invokes it by name.
---

# Raise the bar

The user invoked this because they want the best result the work can reach, and they accept that
it takes longer and uses more than the default. It runs the judged loop from finish-the-job with a
stricter bar and more rounds, as a Codex goal when it can, so the work continues across turns until
the bar is met or the stop rule ends it.

The user's own words win over anything here, including a number of rounds or a token budget.

In Plan mode, put the brief and the bar in the plan, and leave the brief file, the goal and the
building for after Plan mode ends.

## The loop it reuses

Read [../finish-the-job/SKILL.md](../finish-the-job/SKILL.md) and follow its section "The judged
loop", with [../finish-the-job/references/brief.md](../finish-the-job/references/brief.md) for the
brief and [../finish-the-job/references/judge-brief.md](../finish-the-job/references/judge-brief.md)
for the judge. Its rules on asking, scope, evidence, stalls and the final message apply too. These
changes take precedence.

- Run the whole loop whatever the size of the change.
- The bar is what a top expert in the field would be proud to put their name to. Write four to
  eight checks, and add an ambition line saying what this would be at its best, a first-impression
  check, and a detail inventory listing the concrete details a top version has, one per line.
- If the work already exists, use it for real and judge it before changing anything. That counts
  as the first judgment.
- The cap is eight rounds, or the number the user gave. A new goal or a user request for more
  rounds starts a fresh count from the best version.
- When a round fixes none of the last judge's blocking or visibly weaker findings, change approach
  once, using a different mechanism for the weakest check instead of new values for the same idea.
  If the next round also fixes none, stop.
- Before each round, save a copy or patch of the files the work changed under `.tryhard/versions/`
  instead of the temp folder, leaving out dependency folders and build output.

## Write the brief file

Before building, write `.tryhard/brief.md` in the folder Codex is working in, so the brief survives
across turns and compaction. In a git repository, add `.tryhard/` to the exclude file that
`git rev-parse --git-path info/exclude` prints, so it never enters a commit. Give the file one
heading per part, with short plain text under each.

- The user's request, pasted as written.
- The brief, including the exact constraints and the decisions you made.
- The bar, with the ambition line, the first-impression check and the detail inventory.
- What the result must not be.
- How to see the result the way the user will.
- The judge procedure. Give the full path of judge-brief.md, and say that each round a new subagent
  without your history judges from this file's request, brief, bar and must-not-be list.
- The stop rule. Stop when a judge finds only minor issues, when a round after a change of approach
  still fixes none of the last findings, or when the cap is reached.
- Where the saved versions are, and which one is the best so far.
- The round log, one line per round giving what changed, the judge's verdict, and whether it beat
  the best version.

Share the brief and the bar in a progress update too, with one line saying this mode does best at
ultra reasoning effort, which also lets Codex split work across subagents. It is chosen under
`/model` in the CLI or in the app's model picker where the account offers it.

## Start the goal

If the `create_goal` tool is available, call it. The user invoked this skill by name, which is the
explicit request the tool asks for. Keep the objective short and point it at the file.

    Bring {the work, in the user's words} up to the bar in .tryhard/brief.md. Done means a fresh
    judge following that file finds only minor issues, or the file's stop rule has been reached with
    the best version kept, and either way the round log records the final verdict and what is still
    weak. Read .tryhard/brief.md at the start of every turn.

Pass `token_budget` only when the user named one. Then start building in the same turn.

If `create_goal` is unavailable, or fails because an unfinished goal exists, leave any existing goal
alone and run the rounds in this turn with the same cap. In the final message, give the line to
paste to continue as a goal, which is `/goal ` followed by the objective above. If goals are off,
`goals = true` under `[features]` in Codex's `config.toml` turns them on.

## Running and stopping

At the start of each goal turn, read `.tryhard/brief.md` and its round log, and check the current
state of the work before relying on memory. Then take the next step of the loop. Log each round when
its judgment comes back. Codex's goal instructions still apply, including that a plan or a status
update alone is no progress.

When the stop rule holds, go back to the best version if the last one is worse, stop any programs
you started, and record the final verdict and what is still weak in the round log. When a goal is
running, then run its completion audit against the file and call `update_goal` with status
`complete`. If the same blocker, such as a missing dependency only the user can supply, holds for
three goal turns in a row, follow Codex's blocked rule.

## Final message

Follow [../finish-the-job/references/final-report.md](../finish-the-job/references/final-report.md).
Lead with the result and how it measures against the bar, in plain words. Give one sentence per
round on what it improved, grouping rounds that made the same kind of fix, then what still falls
short and what it would take, and where the brief file and the saved versions are. Keep the names
of this process out of the work itself.
