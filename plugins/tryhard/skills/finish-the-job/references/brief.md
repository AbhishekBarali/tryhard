# Writing the brief

Read this before writing the brief for anything bigger than a small change. The brief is where you
work out what the user really wants before building, the way a senior colleague would from the same
message. It is also the yardstick the judge uses, so write it in the user's terms.

## What goes in

Keep it to about five to fifteen short lines for a big build. Before you start building, share the
first four parts and your decisions in a progress update so the user can steer early. The
must-not-be list stays in your notes and goes to the judge.

1. What the user is really after, in a sentence or two, and who will use the result.
2. What a thoughtful expert would include without being told. Think through what the situation
   implies. A game needs a way to start, lose and restart, controls the player can discover, a goal
   or score, and feedback when something happens. A form needs clear error messages, an empty state
   and a saving state. A new command needs help text and a clear error for bad input. A scene of the
   Red Sea parting has people hurrying through, because that is what the moment means. Include what
   serves this request, and leave out what would serve a different one.
3. Exact constraints, copied as the user stated them, such as numbers, names, limits, files to leave
   alone, or a style or existing design to match. These hold exactly, and inference works around
   them.
4. The bar, three to six checks a demanding expert in the field would apply, which is what the user
   will look for when they review the result. Make each one something you can observe or measure,
   in the user's terms, and rank them with the user's main goal first. For a document, write checks
   about the reader, such as "a new teammate can set up the project from this page alone".
   For anything people see or play, include a first-impression check, such as "a new player knows
   what to do within ten seconds and wants another go".
5. What the result must not be, meaning the lazy or generic version of this request. Typical entries
   are a stub behind a polished surface, something that only works on the happy path, the first idea
   any model would give, a template look that ignores the subject, invented branding or labels
   nobody asked for, and anything that was never run.
6. Decisions you made where the request was open, one line each with the reason. When a visible
   choice is open, the fresh-ideas procedure settles it here. Put the winner in the brief and the
   rejected defaults in the must-not-be list.

Decide all of this yourself. The user asked for a result, and a list of questions would hand the
work back. Ask only when the test in [ask-or-decide.md](ask-or-decide.md) says to.

A small change needs only the first line and one check, such as "Search should match accented
words. Check that 'café' finds 'Café Lumen' and the old searches still work."

## Example

The details below are made up. Take the pattern, and draw your own content from the user's subject.

The user wrote "make a snake game I can play in the browser". The progress update says this.

> You want a snake game that opens in a browser and is fun for a few minutes on a laptop keyboard.
> The one exact constraint is that it plays in the browser.
>
> A good version also has a start screen that shows the controls, arrow keys and WASD, pause, speed
> that rises as the snake grows, food that never appears inside the snake, a game-over screen with
> the score and a one-key restart, and a best score kept between visits.
>
> I will check the result against these, most important first. A new player starts and understands
> the controls within ten seconds. Fast key presses are never lost and never turn the snake back
> into itself. Losing, restarting and the best score all work. It looks deliberate in a laptop window
> and a phone-sized one. It stays smooth at top speed.
>
> I chose plain HTML, CSS and JavaScript in one folder with no build step, so it opens straight from
> the file.

The must-not-be list in the notes for the judge reads "a bare grid with no start or end, a snake
that dies when two keys land in one tick, the default green-on-black look, a board that ignores the
window size".
