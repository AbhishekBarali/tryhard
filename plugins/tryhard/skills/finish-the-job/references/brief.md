# Writing the brief

Read this before writing the brief for anything bigger than a small change. The brief is where you
work out what the user really wants before building, the way a senior colleague would from the same
message. It is the spec for the build and the yardstick for the judge, so write it in the user's
terms.

## The parts

A small change needs only parts 1, 2 and 8. A big build needs all of them, in about ten to twenty
short lines.

1. The request, pasted as the user wrote it.
2. Fixed constraints, copied exactly, such as numbers, names, limits, files to leave alone, or a
   style or existing design to match. Inference works around them.
3. Ambition, one sentence on what this is at its best, who it is for and what it lets them do.
4. First impression, what the user meets in the first seconds (the first screen, run, page or
   command). It opens on the finished thing, without setup screens, invented branding or filler
   labels.
5. Detail inventory, the parts a thoughtful expert includes, grouped by area. Include what the
   situation implies but nobody said, the edge cases, and help or docs for anything user-facing. A
   game needs a way to start, lose and restart, controls the player can discover, a goal or score,
   and feedback when something happens. A form needs clear errors, an empty state and a saving
   state. A new command needs help text and a clear error for bad input. A scene of the Red Sea
   parting has people hurrying through. For a QA pass, this is the list of paths and cases you will
   try. Say where you will be exhaustive. Leave out what would serve a different request.
6. Open choices, settled with the fresh-ideas skill, giving the chosen direction and one line on why
   it fits. The obvious default it replaced goes in your notes with part 9.
7. Assumptions, one line for each gap you filled, giving what you assumed, why, and whether it is
   reversible. They bind the build, the judge gets them with the fixed constraints, and the final
   report lists them.
8. Review bar, three to eight lines saying what the user will look for when they review the result,
   each with how it is checked (run it, a screenshot at real size, a measurement, a click-through, a
   check that failed before the change). Name one primary measure, and turn side aims into "does not
   get worse" lines. For a document, write lines about the reader, such as "a new teammate can set up
   the project from this page alone". For creative or design work, include a line asking for choices
   made for this brief that a similar prompt would not produce.
9. Must not be, three to five lazy versions of this result, written as scope outcomes, such as
   half-built, a placeholder behind a polished surface, happy path only, a template layout, or a
   generic default. This list stays in your notes, and the judge gets it rewritten as positive
   checks.

Decide all of this yourself. Stop for the user only in the cases listed in SKILL.md under "When to
stop for the user".

## Sharing it

Before you start building, share parts 2 to 8 in a progress update so the user can steer early. An
opening line such as "I read this as ..." makes it quick to scan.

## After each judged round

Write the confirmed fixes back into the brief, in the detail inventory, the review bar or the
assumptions, so the next round works from the improved spec. A bar line you wrote that turns out
wrong for the user's goal can be corrected with a one-line note. The bar may get stricter as you
learn, and it never drops so that the work passes.

## Example

The details below are made up. Take the pattern, and draw your own content from the user's subject.

The user wrote "make a snake game I can play in the browser". The progress update says this.

> I read this as a snake game that opens in a browser and is fun for a few minutes on a laptop
> keyboard. It opens straight onto the board with the controls shown beside it.
>
> A good version has arrow keys and WASD, pause, speed that rises as the snake grows, food that
> never appears inside the snake, a game-over screen with the score and a one-key restart, and a
> best score kept between visits. I will be exhaustive about input handling, since that is where
> snake games feel broken.
>
> I assumed plain HTML, CSS and JavaScript in one folder with no build step, so it opens straight
> from the file. That is easy to change later.
>
> I will check the result against these, most important first. A new player starts and understands
> the controls within ten seconds, checked by opening it fresh. Fast key presses are never lost and
> never turn the snake back into itself, checked with scripted bursts of two keys in one tick.
> Losing, restarting and the best score all work, checked by playing to a loss and reloading. It
> looks deliberate in a laptop window and a phone-sized one, checked with screenshots at both sizes.
> It stays smooth at top speed, checked by measuring frame times.

The must-not-be list in the notes reads "a bare grid with no start or end, a snake that dies when
two keys land in one tick, happy path only with no pause or restart, a board that ignores the window
size".
