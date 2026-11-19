---
name: raise-the-bar
description: Max mode for the biggest asks. Runs the same brief, bar and fresh-eyes judge as finish-the-job with a stricter bar and more rounds, as a Codex goal that keeps going across turns when the goal tools are available. Use when the user invokes it by name.
---

# Raise the bar

The user invoked this because they want the best result the work can reach, and they accept that
it takes longer and uses more than the default. It runs the judged loop from finish-the-job with a
stricter bar and up to eight rounds, as a Codex goal when it can, so the work continues across turns
until a fresh judge says READY or the rounds run out.

The user's own words win over anything here, including a number of rounds or a token budget.

In Plan mode, put the brief in the plan, and leave the files, the goal and the building for after
Plan mode ends.

## The loop it reuses

Read [../finish-the-job/SKILL.md](../finish-the-job/SKILL.md) and follow "The judged loop" with its
references. Its rules on scope, evidence, stopping for the user, stalls and the final message apply
too. These changes take precedence.

- Run the whole loop whatever the size of the change. If the work already exists, use it for real
  and judge it before changing anything, and count that as the first judgment.
- The bar is what a top expert in the field would be proud to put their name to. Write five to eight
  review-bar lines, and write the ambition, first impression and detail inventory out in full.
- The run ends when a fresh judge says READY, or when eight rounds after the first judgment are
  logged (or the number the user gave). A plateau, a regression or a big gap that survives two
  rounds does not end it. Go back to the best version, note what the stuck approach showed, and
  change approach for the weakest bar line.
- When running at ultra effort, keep parallel subagents to about four or five.
- A new goal or a user request for more rounds starts a fresh count from the best version.

## Files

Before building, create `.tryhard/` in the folder Codex is working in. In a git repository, add
`.tryhard/` to the exclude file that `git rev-parse --git-path info/exclude` prints, so none of it
enters a commit.

- `.tryhard/brief.md` holds the brief, with a non-empty review bar, the full path of
  finish-the-job's judge brief, and this line: "Checks already run on the current state stand.
  Rerun a check only when its inputs changed or it failed."
- `.tryhard/rounds.md` is the round log, one line per round with what changed, the judge's READY or
  NOT READY and its top gaps, and what is still open.
- `.tryhard/versions/` holds a copy or patch of the files the work changed, saved before each round,
  leaving out dependency folders and build output. The round log names the best one.
- `.tryhard/evidence/` holds what using it for real produced, for the judge.

Share the brief, except the must-not-be list, in a progress update, and mention once that this mode
does best at ultra reasoning effort where the account offers it, chosen under `/model` in the CLI
or in the app's model picker.

## Start the goal

Call `get_goal` first, then follow the first case that fits.

- No goal is set. Call `create_goal` with the objective below and no other field, adding
  `token_budget` only when the user named a budget. The user invoked this skill by name, which is
  the explicit request the tool asks for.
- The same objective is already active. Continue it.
- A different unfinished goal is active. Leave it alone, tell the user in one line, and run the
  rounds in this turn.
- A finished goal is still set, so a new one cannot be created. Give the user `/goal clear` followed
  by the `/goal` line below, and run the rounds in this turn meanwhile.
- The goal tools are missing. Run the rounds in this turn, and give the `/goal` line in the final
  message. If goals are turned off, `goals = true` under `[features]` in Codex's `config.toml` turns
  them on.

The objective, kept short and stable, with the user's number in place of 8 if they gave one:

    Deliver {the outcome, in the user's words} as specified in .tryhard/brief.md. Done means every
    review-bar line there is met with current evidence and a fresh judge finds only minor issues,
    or 8 improvement rounds are logged in .tryhard/rounds.md with the remaining gaps recorded. Keep
    the brief's fixed constraints exactly.

Then start building in the same turn.

## Each turn and the end

At the start of each goal turn, read `.tryhard/brief.md` and `.tryhard/rounds.md`, check the current
state of the work before relying on memory, and take the next step of the loop.

When the run ends, go back to the best version if the last one is worse, and stop any programs you
started. Call `update_goal` with status `complete` only after the final real use and a fresh
judge's READY, or once the last allowed round is logged with its remaining gaps. If the same
blocker, such as a missing dependency only the user can supply, holds for three goal turns in a row,
follow Codex's blocked rule. A run in this turn ends the same way, without the goal calls.

## Final message

Follow [../finish-the-job/references/final-report.md](../finish-the-job/references/final-report.md).
Lead with the result against the bar, give one sentence per round on what it improved (grouping
rounds that made the same kind of fix), then say what still falls short and where the `.tryhard/`
folder is. Keep the names of this process out of the work itself.
