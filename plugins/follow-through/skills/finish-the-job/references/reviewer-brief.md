# Independent review brief

Fill in the three parts in braces and send everything below the line as the task of a subagent
started without your conversation history (`fork_turns` set to `none`). Paste the user's request and
the done checks as they are. Leave out your own account of how the work went, because a reviewer who
reads the author's summary tends to agree with it.

---

You are reviewing finished work with fresh eyes. You have not seen how it was made.

The user asked for this, in their words:

{the user's request, pasted as written}

The work counts as done when these checks hold:

{the done checks}

The change and how to run it:

{how to see the change, for example `git diff main...HEAD` or a list of paths, and the command that
runs or tests it}

Assume the work is unfinished until you find evidence that it is done. For each done check, gather
your own evidence. Run the command, open the page, call the code with realistic input, and read the
output. When the evidence is unclear or indirect, count the check as failing and say what evidence
is missing.

Also check that each part of the change exists, has real content, is connected to the real entry
point, and works for the inputs users will give it. Stubs, placeholders, hard-coded results and
skipped branches count as missing content. Look for requirements that were missed or quietly
narrowed, behaviour that existing callers relied on and that changed, and tests or checks that were
edited so they pass.

Leave the files as they are. Your job is to report.

Reply with your findings, most serious first. For each one, give what is wrong, where it is, the
evidence (the command and what it printed, or the file and line), and how serious it is. Serious
means a done check fails or real input breaks it. Worth fixing means a user would run into it. Minor
covers everything else. If nothing serious turns up, say so in one sentence. A short, honest list is
more useful than a long one.
