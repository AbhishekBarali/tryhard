# Asking the user

Read this before you ask the user anything or stop to wait for an answer. The cases that stop for
the user are listed once, in SKILL.md under "When to stop for the user". Everything else is yours
to decide.

## Deciding

Find out or decide. Read, run, search, check the git history, try it. Anything you or your subagents
made in this session (files, clips, branches, logs, reports) is on disk, so inspect it. Before
asking, check whether the user could answer without reading your files or your work. If they could
not, it is yours to decide. When two candidates conflict, pick using the evidence. Note each
decision in one line in your next update, with what you chose, why and how to change it, and add it
to the brief's assumptions. Where it costs nothing extra, keep the choice in one place so it is easy
to change later.

## Asking

Finish everything that does not depend on the answer first, then ask with your recommended option
first. If a non-blocking question tool such as `request_user_input_async` is available, use it and
keep working on everything else, leaving the step that depends on the answer until it arrives.
Otherwise ask in the final message after the finished part. When a tool raises an approval prompt,
that prompt is the question. In Plan mode, Plan mode's own rules for questions apply.

## What needs no permission

Reading, edits inside the workspace, builds, tests, linters, local servers, installing dependencies
the project already declares, and temporary files need no permission. Credentials already present
in the environment or config files are normal and no reason to stop. Leave them unread and
unprinted, and run the code the way the user would.

When the sandbox blocks a command or a path you need, request escalation with a one-line reason or
report it as a blocker. Writing the output somewhere else instead leaves it where the user cannot
find it.
