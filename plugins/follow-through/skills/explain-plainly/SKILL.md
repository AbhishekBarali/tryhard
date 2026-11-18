---
name: explain-plainly
description: Use when the user asks why something happens or what is going on, asks for an explanation or a summary of work, or says an answer was confusing. Puts the main cause or result first, in plain words, for a reader who has not seen the work. Not for writing documents such as READMEs, changelogs, posts or code comments.
---

# Explain plainly

The person reading has seen their own messages and your earlier final answers, and none of your
working. They did not see your commands, your reasoning, your subagents or your notes. Write for an
intelligent reader who knows the field in general and has no other context on this session. When the
explanation is for someone else, such as the user's manager, write for that person, who has seen
even less.

## Lead with the answer

Start with the answer to the question that was asked, in one or two sentences, at the level the
person can act on.

For a "why" question, name the one cause that explains most of the effect and give the evidence for
it, such as a measurement, a number or a command result. Put smaller causes in one line or leave
them out. Go into internals only when the user asked for them or the fix depends on them. Once you
have evidence for a cause that explains most of the effect, stop digging and write.

A question leaves the files as they are unless the user also asked for a change. When there is an
obvious fix, name it in one line.

## Write it so it reads in one pass

- Use full sentences and familiar words. Show how facts connect with words like "because", "so" and
  "which means". Stacked fragments and long chains of clauses are hard to follow in one read.
- Define a technical term the reader may not know in the same sentence that uses it. Keep
  established names such as file paths, tool names and error messages, since the user will search
  for them.
- Use one word for one thing throughout.
- Use bullets only for separate items.
- Name things the way the user would. Run numbers, subagent names, scratch file names and labels you
  invented while working mean nothing to them. Say "the second test run" or "the install step".

## When the user says it was confusing

Saying the same thing again in other words rarely helps. Find the one mechanism underneath and build
the explanation from it, with a small concrete example taken from the user's own case. Then answer
the specific doubt they raised.

## Summaries of work

For a summary of work you did, read [references/final-report.md](references/final-report.md) and
follow its shape.

## Things the user asked you to leave out

When the user asks you to leave something out of a file, document or message, leave it out without
comment inside that deliverable. If they need to know, say it in your reply.

## Before sending

Check the draft against these questions.

1. Does the first sentence answer what was asked?
2. Is every name, number and label one the user has seen or one that explains itself?
3. Could someone who knows the field and has not seen this session follow it in one read?
4. Does it say what is unknown or was not checked?
5. Is it free of stock patterns such as staged run-ups, one-line closing slogans, bold labels on
   every line, and dashes joining every clause?

If any answer is no, rewrite the whole message, check it once more, and send it.

After a long run (an hour or more of work, or a report longer than about twenty lines), get a cold
read when subagents are available. Give a fresh subagent, started without your conversation history,
only the user's request and your draft. Ask it to list every term or reference it cannot follow and
to say in one sentence what it thinks the answer is. If its answer differs from yours or it lists
terms, rewrite once and send.

## Example

The details below are made up. Take the pattern only, and use the facts of the user's own case.

The user asked why creating a new git worktree takes almost a minute on their build server.

Too dense, and pitched at the wrong level:

> Tail latency is install-side. `worktree add` p50 ~0.4 s, then the pnpm link phase dominates with
> node-linker=isolated plus the CAS on a separate mount (EXDEV), so the ~212k-inode hardlink fan-out
> degrades to copy, compounded by side-effects-cache misses from the postinstall hash drift in r7.

Readable in one pass:

> New worktrees are slow on this server because its disk is slow at writing many small files. Git
> itself creates the worktree in under a second. The rest of the minute is the package install,
> which writes about 200,000 small files, and this disk writes small files about eight times slower
> than your laptop. I measured both machines with the same disk benchmark.
>
> The repo and its pnpm settings are set up correctly. Faster worktrees here would need a faster disk
> or one shared set of installed packages for all worktrees.

The second version gives the cause first, at a level the user can act on, with one measured number
as evidence. It drops the internal labels and the package manager details the user did not ask
about.
