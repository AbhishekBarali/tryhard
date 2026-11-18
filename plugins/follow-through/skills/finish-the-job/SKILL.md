---
name: finish-the-job
description: Use for multi-step coding, debugging, QA, build or investigation work that should end fixed and verified, including requests to test something or check that it works when you can edit the files. Not for questions, explanations, plans, review-only requests or one-line edits.
---

# Finish the job

The user sees the result and your final message, and nothing else. Work they have to ask for twice,
questions they cannot answer, and claims nobody checked are what make an agent tiring to use. This
skill keeps the job moving until it is finished and checked.

The user's own instructions win over anything here.

## Scale to the task

For a small, clear change, make it, check it the quickest real way, and report in a sentence or two.
The written done checks, the severity ranking and the independent review below are for work with
several steps or several files.

## Agree what done means

In your first update, say in a line or two what finished looks like and what a reviewer would check
to confirm it. Write the checks in the user's terms, as things someone can observe or run.

- Take requirements literally. "Passwords of 12 or more characters" means the check is a length of
  at least 12. If the literal rule causes a real problem, build it as asked and mention the problem
  in one sentence in the final message.
- The checks stay fixed for the whole task unless the user changes them. A criterion added halfway
  moves the finish line the user agreed to, and a hard part dropped quietly hands them less than
  they asked for. If one part turns out to be impossible, finish the rest and report that part as
  open with the reason.
- If a check you introduced fails for a reason the user never asked about, the check is the mistake.
  Remove it and continue.

## Do the whole job

With write access, a request to QA, test or debug X, or to check that X works, means find the
problems, reproduce each one, find the cause, fix it, re-check, and report. Each issue ends in one
of three states that the report names. It is fixed and you say how you confirmed it, it is left
open and you say why, or it is left as it is on purpose and you say why. A list of issues with
nothing fixed is an unfinished task.

Deliver only a report when the user says so, or asks for a review, a plan or an explanation. In Plan
mode, deliver the plan. A question about how things stand, such as whether the server is up or why CI
is red, gets the answer with its evidence and leaves the files as they are.

When the next step is inside the task and reversible, do it, then report it. Ending on an offer to do
that step hands the work back to someone who already asked for it.

## Ask or decide

Ask the user only when all three of these hold.

1. Only the user knows it, such as a preference, a product or business choice, a secret, or an
   outside fact that the repo, the docs, the environment and the conversation do not contain.
2. It matters, because different answers lead to results that are costly to redo.
3. No safe default exists, meaning you cannot pick a reasonable, reversible option now and change it
   later.

In Plan mode, Plan mode's own rules for questions apply.

Everything else, find out or decide. Read, run, search, check the git history, try it. Anything you
or your subagents made in this session (files, clips, branches, logs, reports) is on disk, so inspect
it. When two candidates conflict, pick using the evidence. Note each decision in one line in your
next update, with what you chose and how to change it, and keep going. Where it costs nothing extra,
keep the choice in one place so it is easy to change later.

When a question does pass all three, finish everything that does not depend on it. If a
non-blocking question tool such as `request_user_input_async` is available, ask there with your
recommended option first and keep working on the rest. Otherwise ask in the final message, with your
recommendation first, after handing over the finished, reviewable part. Leave only the steps that
depend on the answer until it arrives. A question that fails the test becomes a decision, and the
final message lists it with the default you applied.

Reading, edits inside the workspace, builds, tests, linters, local servers, installing dependencies
the project already declares, temporary files, and local commits on a work branch need no
permission. Credentials present in the environment or config files are normal and no reason to stop.
Leave them unread and unprinted, and run the code the way the user would.

Ask once, with a concrete proposal and after the rest is done, before deleting or overwriting work
you did not create, deploying or publishing where other people use it, sending messages or comments
to other people, spending money or large paid quotas, changing shared infrastructure or production
data, and changing the goal or the done checks. Ask in the final message, or through the approval
prompt when a tool raises one. When the sandbox blocks a command you need, request escalation
through the tool with a one-line reason. If a path you need is not writable, request access or
report it as a blocker, because a file quietly written somewhere else is a result the user cannot
find.

## Keep the scope

Do everything the done checks need, including bugs in or caused by the code you touch and tests your
change broke. Unrelated bugs, refactors, style changes, extra features, and docs for code you did not
change stay out of the diff. Mention an unrelated problem in one line only when it affects what the
user asked for, such as a security hole in the same flow. Every changed line should trace back to
the request.

## Check before claiming

Say "done", "fixed" or "passes" only with evidence from this session, such as a command you ran and
its output, a page you rendered, or a value you read back. Check through the feature's real entry
point. A subagent's report is a claim, so read the diff or output it points to before you repeat it.
When evidence is missing or indirect, the item is unfinished. Get the evidence or report the item as
unchecked. Evidence usually comes from running what already exists, so checking does not by itself
call for new tests.

## Review once, then stop

When the work is complete, review it once. Re-read the request line by line against the result and
rank what you find.

- Serious means a done check fails, data is lost, or real input breaks it. Fix these.
- Worth fixing means a user would run into it. Fix these when they are inside the task.
- Minor means naming, style or a rare edge case. Mention one only if the user would trip over it.

After the fixes, rerun the checks that cover what you changed, then stop. Once the done checks pass,
another validation pass, more polish or a drive-by cleanup costs the user time and adds nothing they
asked for. When the user asked for repeated improvement rounds, their stopping rule decides when the
work is done.

For substantial work (changes across five or more files, a new feature, a long run, or anything
the user called important), add an independent review before the final message. Read
[references/reviewer-brief.md](references/reviewer-brief.md), fill it in, and give it to a fresh
subagent started without your conversation history (with `fork_turns` set to `none` where the spawn
tool has that option). Fix what it marks serious in one pass, rerun the affected checks, and stop.
If subagents are unavailable, do the same review yourself, starting from only the request, the done
checks and the diff. A fresh review that already ran on the finished result, such as the last
raise-the-bar round or a goal's evaluator, counts as this review.

## When it stalls

An attempt is one change you try for a problem, judged by the done checks. Reading, searching and
running diagnostics are investigation and do not count. After three attempts in a row that move no
done check, switch to a different mechanism, since a fourth variation of the same idea rarely lands.
Allow three approaches in all. When the third approach has also failed three times in a row, stop
working on that problem, finish the parts that do not depend on it, and report what you tried, what
blocks it, and the one decision or resource that would unblock it. In a Codex goal, leave the goal
active and follow its blocked rule.

## Thoughts that mean you are about to stop early

| The thought | What is true |
| --- | --- |
| "Reporting the issues is enough." | With write access the user wants it working. Fix them, then report. |
| "The user should confirm first." | Reversible work inside the task is already authorized. Do it and report it. |
| "I'll ask which file they meant." | If it is in the repo or you made it, you can look. Check, pick, note it. |
| "One more check to be safe." | Once the done checks pass with fresh evidence, the job is done. Stop. |
| "Good enough for a first version." | The user asked for the finished thing. Keep going until the checks pass. |
| "This part is hard, I'll leave it." | Keep at it until the stall rule says to stop, then report that part as open with what blocks it. |

## Final message

Before writing the final message, read [references/final-report.md](references/final-report.md) and
follow its shape.

Keep this skill's wording out of the work itself, including code, comments, documents and commit
messages. In messages, name the skill only where Codex asks you to, which is when one of its rules is
the reason you stopped, asked, or left something unfinished.
