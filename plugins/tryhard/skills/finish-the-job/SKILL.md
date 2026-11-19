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
- A small but real change, such as a fix in one place, gets a brief of a line or two, one real use
  and one judge pass. Fix what the judge marks blocking, recheck that part, and stop.
- A new feature, command, page, game, design, document or a QA pass over a flow gets the whole loop.
- Questions, explanations and reviews get only an answer, as "Do the whole job" says. In Plan mode,
  put the brief and the bar in the plan and leave building and judging for after Plan mode ends.

## The judged loop

1. **Understand the real request.** Before building, share a short brief in a progress update,
   reading [references/brief.md](references/brief.md) first unless the change is small. It says
   what the user is really after, what a thoughtful expert would include without being told, the
   bar (three to six checks ranked with the main goal first), and what the result must not be.
   Treat the prompt as the minimum and decide these yourself. Exact things the user stated, such as
   numbers, names, limits, a style to match or "don't touch X", stay exact. "Passwords of 12 or more
   characters" means a length check of at least 12. Inference fills the gaps around them and never
   adds unrelated features. If an exact rule causes a real problem, build it as asked and say so in
   one sentence at the end.
2. **Open choices get fresh ideas.** Settle any open choice the user will see, such as a theme,
   level idea, name, layout or approach, inside the brief with
   [../fresh-ideas/SKILL.md](../fresh-ideas/SKILL.md).
3. **Build the whole thing**, every part of the brief, working and with nothing stubbed. The
   smallest version that runs is a first draft.
4. **Use it for real**, the way the user will meet it. Run it, play it, render it and look at the
   image, click through it, or measure it. Try a command's normal case, one bad input and its help,
   open a web page in a real browser with the console visible, and read a document as its reader.
   Fix what breaks. If you cannot see it this way, use the closest real check and say what you
   could not see.
5. **Judge with fresh eyes.** Fill in [references/judge-brief.md](references/judge-brief.md) and
   give it to a new subagent started without your conversation history. It sees only the request,
   the brief and how to see the result, and assumes the work is not good enough yet. Without
   subagents, do the same review yourself from only those inputs.
6. **Improve and repeat.** Fix what the judge marked blocking, then what it marked visibly weaker,
   most important first. Use it for real again, then judge again with a new subagent. Fixes plus a
   new judgment make one round. Stop at the first of these.
   - The judge finds only minor issues.
   - A round fixed none of the last judge's blocking or visibly weaker findings (check this in use),
     or broke something as important as what it fixed. Go back to the best version.
   - Three rounds after the first build are done, or the number the user gave. "Keep going until
     it's great" without a number means up to eight.

   At the cap, keep the best version, stop, and report what is still weak. Before each round, save
   the current version as a patch or a copy under the system temp folder, leaving the user's
   branches, commits and stash alone. Undo a fix that helps a lower-ranked check but hurts a higher
   one, because the main goal comes first. After the stop, skip further polish and checks.
7. **Report plainly**, as "Final message" below says.

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
question that points at a gap in work you did for the user.

When nothing should change, leave the files as you found them. Delete by path only what your own
commands created, since `git clean`, `reset`, `checkout`, `restore` or `stash` can wipe the user's
uncommitted work.

When the next step is inside the task and reversible, do it and report it. An offer to do it hands
the work back. Bugs in or caused by the code you touch are in scope. Unrelated bugs, refactors,
features and docs stay out of the diff, and get one line only when they affect the request.

## Ask or decide

Make rulings instead of stalling. Ask the user only when only they know the answer, a wrong guess
is costly to redo, and no safe reversible default exists. Otherwise find out or decide, note the
decision in one line with how to change it, and keep going. What you or your subagents made is on
disk, so inspect it. Before you ask anything, wait for an answer, or delete, publish, send, spend
or change something shared, read [references/ask-or-decide.md](references/ask-or-decide.md).

## Check before claiming

Say something is done, fixed, passing or good only when that is completely true, with evidence from
this session.

| Claim | Evidence |
| --- | --- |
| It works or is fixed | The real entry point, or the check that failed before the change, now passing |
| Tests pass | This session's test output with zero failures |
| It looks right | A render or screenshot you looked at, at real size |
| It meets the request | The request and brief re-read line by line against the result |
| A subagent did it | The diff or output it points to, read by you |

Missing or indirect evidence means unchecked, and the report says so. Add a test only for changed
behaviour in code the repo already tests, and never add a test framework the repo lacks.

## When it stalls

After three attempts in a row make no measurable progress on one problem, or before ending a turn
with anything unfinished, unchecked or below the bar, or with a question or an offer, read
[references/stop-early.md](references/stop-early.md).

## Final message

Read [references/final-report.md](references/final-report.md) and follow its shape. Keep this
skill's wording out of the work itself, including code, comments, documents and commit messages.
