---
name: finish-the-job
description: Use for real work that should end finished and good, such as building or changing a feature, app, game, page or design, multi-step coding, debugging and fixing, QA or checking that something works when you can edit the files, or writing a document. Not for questions, explanations, plans, review-only requests or one-line edits.
---

# Finish the job

This skill gets a result a demanding expert would accept from one normal request, so the user
never has to spell everything out or push twice. It takes longer than one pass, on purpose.

The user's own instructions win over anything here.

## Scale to the task

- A one-line edit, rename or version bump gets no brief and no judge. Make it, check it the
  quickest real way, and report in a sentence or two.
- A small but real change, such as a fix in one place, gets a three-line brief (the request, the
  fixed constraints, the review bar), one real run of the changed path and one judge pass. Fix what
  you confirm as blocking, and stop.
- A new feature, command, page, game, design, document or a QA pass over a flow gets the whole loop.
- Questions, explanations and reviews get only an answer, as "Do the whole job" says. In Plan mode,
  put the brief in the plan and leave building and judging for after Plan mode ends.

## The judged loop

1. **Write the brief.** Read [references/brief.md](references/brief.md) unless the change is small,
   write the brief, and share all of it except the must-not-be list in a progress update. Treat the prompt as the minimum, fill gaps as
   a thoughtful expert would, and record each as an assumption. Exact things the user stated, such
   as numbers, names, limits, a style to match or "don't touch X", stay exact. "Passwords of 12 or
   more characters" means a length check of at least 12. If an exact rule causes a real problem,
   build it as asked and say so at the end.
2. **Settle open choices** the user will see, such as a theme, level idea, name or layout, inside the
   brief with [../fresh-ideas/SKILL.md](../fresh-ideas/SKILL.md).
3. **Build the whole thing**, every part of the brief, working and with nothing stubbed. The
   smallest version that runs is a first draft.
4. **Use it for real** through its real entry point, the way its user will meet it, following
   [references/use-it-for-real.md](references/use-it-for-real.md). Fix what breaks.
5. **Judge with fresh eyes.** Fill in [references/judge-brief.md](references/judge-brief.md) and give
   it to a new subagent spawned with `fork_turns` set to `"none"`. If no subagent can be started, do
   the same review yourself from the same inputs and call it a self-review in the report.
6. **Check the findings, then fix.** The judge's findings are claims. Mark each one above minor as
   confirmed, not confirmed or can't verify, using your own evidence, and fix the confirmed ones in
   rank order. Minor gaps never start a round. Leave the bar, tests and measurements as they are
   when fixing for the judge, and keep the user's constraints over the judge's advice. Write the
   fixes back into the brief, use it for real again, and judge again with a new subagent. Fixes plus
   a new judgment make one round.
7. **Stop at the first of these.**
   - The judge says READY, or finds no gap above minor.
   - Plateau. A round moved no bar line toward PASS and closed no gap above minor. New gaps no worse
     than the ones just closed count as drift.
   - Regression. A higher-ranked line got worse. Go back to the best version.
   - The same big gap survived two rounds of fixes.
   - Three rounds are done, or the number the user gave. "Keep going until it's great" means eight.

   Hand back the best version, which is not always the last. Before each round, save the current
   version as a patch or a copy under the system temp folder, leaving the user's branches, commits
   and stash alone. Keep a round log, one line per round, with what changed, what the judge found and
   what is still open. After the stop, skip further polish and checks.
8. **Report** as [references/final-report.md](references/final-report.md) describes, keeping this
   skill's wording out of the work itself.

When raise-the-bar or set-a-goal is in use, follow that skill. Under another Codex goal the same
loop and cap apply across its turns, and the goal's completion audit decides whether its objective
is met.

## Do the whole job

With write access, a request to QA, test or debug X, or to check that X works, means find the
problems, reproduce each one, fix it, use it again and report. A list of issues with nothing fixed
is an unfinished task.

A question, or a request for an explanation, a review, a plan or no changes, gets only that. A why
or how question asks for an explanation even when the answer is a bug, and so does a question about
how things stand. Answer with the evidence, name the fix in one line, and change nothing. This
overrides the QA rule above. A message that also asks for a change gets the change, and so does a
question that points at a gap in work you did for the user. When nothing should change, leave the
files as you found them, and delete by path only what your own commands created.

If your closing message would be a plan, a next step, a routine question or an offer, and the task
still needs that work, do it instead. Bugs in or caused by the code you touch are in scope.
Unrelated bugs, refactors, features and docs stay out of the diff.

Say something is done, fixed, passing or good only when that is completely true, with evidence from
this session.

## When to stop for the user

Decide everything else yourself, note the decision in one line, and keep going. Stop for the user
only in these cases, after the work that does not depend on them, and read
[references/ask-or-decide.md](references/ask-or-decide.md) first.

- The step deletes something you did not make, or cannot be undone.
- It reaches outside this machine or touches something shared, such as a deploy, a message to
  people, a push to a shared branch or production data.
- It spends money, or needs a secret or account access that is not already set up.
- It changes the goal, the scope or an exact constraint the user stated.
- Only the user can know the answer, a wrong guess is costly to redo, and no safe default exists.

## When it stalls

When one problem has resisted three materially different approaches, or before ending a turn with
anything unfinished, unchecked or below the bar, read
[references/stop-early.md](references/stop-early.md).
