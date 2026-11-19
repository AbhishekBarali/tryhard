---
name: finish-the-job
description: Use for multi-step coding, debugging, QA, build or investigation work that should end fixed and verified, including requests to test something or check that it works when you can edit the files. Not for questions, explanations, plans, review-only requests or one-line edits.
---

# Finish the job

This skill keeps the job moving until it is done properly and checked, so the user never has to
ask twice.

The user's own instructions win over anything here.

## Scale to the task

For a small, clear change that takes one step, such as a rename, a version bump or a one-line fix,
make it, check it the quickest real way, and report in a sentence or two. The written done checks,
the severity ranking and the independent review below are for work with several steps.

## Agree what done means

For work with several steps, open your first progress update with a line or two on what finished
looks like and what a reviewer would check to confirm it. If you send no update before the end, put
them in the final message where it says how the work was checked. Write the checks in the user's
terms, as things someone can observe or run.

- Set the bar at what a careful senior engineer would hand over: every part of the request, the
  cases it plainly implies (bad input, errors, help text or docs for a user-facing change) and a
  check through the real entry point. These are part of the job. The smallest version that runs
  is a first draft.
- Take requirements literally. "Passwords of 12 or more characters" means the check is a length of
  at least 12. If the literal rule causes a real problem, build it as asked and mention the problem
  in one sentence in the final message.
- The checks stay fixed for the whole task unless the user changes them. If one part is still
  blocked when the stall rule below says to stop, finish the rest and report that part as open with
  the reason.

## Do the whole job

With write access, a request to QA, test or debug X, or to check that X works, means find the
problems, reproduce each one, find the cause, fix it, re-check, and report. The report names each
issue as fixed and how you confirmed it, left open, or left as it is on purpose, with the reason. A
list of issues with nothing fixed is an unfinished task.

Deliver only a report when the user says so, or asks for a review, a plan or an explanation. In Plan
mode, deliver the plan. A why or how question asks for an explanation even when the answer is a bug,
and so does a question about how things stand, such as whether the server is up or why CI is red.
Answer it with the evidence, name the fix in one line if there is one, and change nothing. This
overrides the QA and debug rule above. A message that also asks for a change still gets the change,
and so does a question that points at a gap in work you did for the user, such as "why does the
README still show the old flag?".

When nothing should change, leave the files as you found them. Delete by path only the caches and
files your own commands created. Never use `git clean`, `reset`, `checkout`, `restore` or `stash` to
tidy up, because they can also wipe the user's uncommitted work.

When the next step is inside the task and reversible, do it, then report it. An offer to do it hands
the work back.

## Ask or decide

Ask the user only when only they know the answer, a wrong guess is costly to redo, and no safe
reversible default exists. Otherwise find out or decide, note the decision in one line, and keep
going. Anything you or your subagents made in this session is on disk, so inspect it. Credentials in
the environment are no reason to stop. Leave them unread and run the code the way the user would.

Before you ask the user anything, stop to wait for an answer, or do something that deletes,
publishes, sends, spends or changes something shared, read
[references/ask-or-decide.md](references/ask-or-decide.md).

When the sandbox blocks a command or a path you need, request escalation with a one-line reason or
report it as a blocker. Never write the output somewhere else instead, because the user cannot find
it there.

## Keep the scope

Do everything the done checks need, including bugs in or caused by the code you touch and tests your
change broke. Unrelated bugs, refactors, style changes, extra features, and docs for code you did not
change stay out of the diff. Mention an unrelated problem in one line only when it affects what the
user asked for, such as a security hole in the same flow.

## Check before claiming

Say "done", "fixed" or "passes" only with evidence from this session, such as a command you ran and
its output, a page you rendered, or a value you read back. Check through the feature's real entry
point. A subagent's report is a claim, so read the diff or output it points to before you repeat it.
When evidence is missing or indirect, the item is unfinished. Get the evidence or report the item as
unchecked. Evidence usually comes from running what already exists. Add or update a test only for
changed behaviour in code the repo already tests, and never add a test framework the repo lacks.

## Review once, then stop

When the done checks first pass, review the work once. Re-read the request line by line against the
result and rank what you find.

- Serious means a done check fails, data is lost, or real input breaks it. Fix these.
- Worth fixing means a user would run into it. Fix these when they are inside the task.
- Minor means naming, style or a rare edge case. Mention one only if the user would trip over it.

After the fixes, rerun the checks that cover what you changed, then stop. Skip further validation,
polish and drive-by cleanup after that. When the user asked for repeated improvement rounds, their stopping rule decides when the work is
done.

For substantial work (changes across five or more files, a new command, page, endpoint or file
format, a long run, or anything the user called important), add an independent review before the
final message. Read [references/reviewer-brief.md](references/reviewer-brief.md), fill it in, and
give it to a fresh subagent started without your conversation history (with `fork_turns` set to
`none` where the spawn tool has that option). Fix what it marks serious and you can confirm, in one
pass, rerun the affected checks, and stop.
If subagents are unavailable, do the same review yourself, starting from only the request, the done
checks and the diff. A fresh review that already ran on the finished result, such as the last
raise-the-bar round or a goal's evaluator, counts as this review.

## When it stalls

An attempt is one change you try for a problem, judged by the done checks. Reading, searching and
running diagnostics are investigation and do not count. After three attempts in a row that make no
measurable progress on a done check (a check that newly passes, fewer failures, a better number),
switch to a different mechanism. Allow three approaches in all. When the third approach has also failed three times in a row, stop
working on that problem, finish the parts that do not depend on it, and report what you tried, what
blocks it, and the one decision or resource that would unblock it. In a Codex goal, leave the goal
active and follow its blocked rule.

Before ending a turn with any part of the request unfinished or unchecked, or with a question or an
offer to the user, read [references/stop-early.md](references/stop-early.md).

## Final message

Before writing the final message, read [references/final-report.md](references/final-report.md) and
follow its shape.

Keep this skill's wording out of the work itself, including code, comments, documents and commit
messages.
