---
name: raise-the-bar
description: Iterate on a result until a demanding expert would sign off. Sets a quality bar, builds a complete version, reviews it against the bar, fixes the biggest gaps, and repeats until another round stops making it visibly better. Use when the user invokes it by name.
---

# Raise the bar

The user invoked this because they want more than a first working version. Treat the first complete
version as a draft. Review it the way a demanding expert in the field would, fix the biggest gaps,
and repeat until another round stops making it visibly better. Because the user asked for these
rounds, this replaces the usual rule of stopping as soon as the work first passes its checks. The
stopping rule below decides when to finish.

The user's own words win over anything here, including a number of rounds they name.

## Write the bar first

Before building, put the bar in your first update so the user can see it.

- Three to six checks a demanding expert in this field would apply to the result. Make each one
  something you can observe or measure, in the user's terms, and rank them with the user's main goal
  first.
- A short list of what the result must not be, such as a placeholder, a stub behind a polished
  surface, the first idea any model would give, or something that was never run.
- If the task leaves a creative or design choice open, settle it before building. Follow the
  fresh-ideas skill from this plugin ([../fresh-ideas/SKILL.md](../fresh-ideas/SKILL.md)) if it is
  installed. If it is not, write down the two or three answers most models would give, come up with
  at least three genuinely different candidates drawn from the user's own subject, and choose on fit
  to the brief.

The bar raises the quality of what was asked for. New features, sections or files the brief did not
ask for are outside it.

## Build a complete first version

Every part of the brief is present and working, and nothing is stubbed. Keep each version
recoverable, for example as a local commit on a work branch or a copy in a temporary folder outside
the deliverable, so a round that makes things worse can be undone.

## Look at it for real

Run it, render it, take a screenshot, play it or measure it, whichever shows the result the way the
user will meet it, and judge what you observed. If the environment cannot show it, use the closest
real check and say in the final message what you could not see.

## Review it as the expert

Read [references/expert-review.md](references/expert-review.md), fill it in, and give it to a new
subagent each round, started without your conversation history (with `fork_turns` set to `none`
where the spawn tool has that option). A fresh reviewer each round judges the result itself, without
anchoring on the last round's verdict. If subagents are unavailable, do the review yourself,
starting from only the brief, the bar and the result. Either
way, the review ends with the gaps ranked and each one marked as blocking the bar, visibly weaker
than an expert would accept, or minor.

## Fix the biggest gaps

Fix everything that blocks the bar, then the visibly weaker items in order. Then look at the result
for real again and compare it with the previous version. When a fix improves a lower-ranked check
but makes a higher-ranked one worse, undo it, because the main goal outranks every side goal.

## When to stop

One review followed by its fixes is one round. Stop when any of these is true.

- A review finds only minor issues.
- A round made no visible or measurable improvement over the version before it. If the last round
  made things worse, go back to the best version.
- Five rounds are done, or the number of rounds the user gave.

When you stop at the round limit, keep the best version and report which checks still fall short
and what it would take to close them.

## Final message

Lead with the result and how it now measures against the checks you set at the start, restated in
plain words. Then say what the rounds improved, in the user's terms, and what still falls short. If
the report guide from this plugin is installed
([../finish-the-job/references/final-report.md](../finish-the-job/references/final-report.md)),
follow its shape. Keep the names of this process and its scaffolding out of the work itself.
