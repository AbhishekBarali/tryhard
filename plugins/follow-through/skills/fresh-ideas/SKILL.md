---
name: fresh-ideas
description: Use when a task leaves open a choice the user will see, such as a name, theme, level or story concept, visual direction, copy tone, or a pick between genuinely different technical approaches. Not for bug fixes, work that must follow existing conventions, or anything the user already specified.
---

# Fresh ideas

When a request leaves a creative choice open, the first answer that comes to mind is usually the
most typical one, and different models land on the same typical answer. Two people who asked for a
"unique" level in two different games both got a water, music and bell level named "Bellwether".
The range to do better is there. A few hundred tokens of planning gets past the default.

## When to use it

Use it when the task leaves open a choice that shapes what the user experiences, and nothing the
user said, the project or an existing style already settles it.

Stay with the expected, conventional answer, with no exploration, for these.

- Bug fixes and regressions.
- Code that follows project conventions, an existing API, a naming pattern or a design system.
- Matching an existing style, voice or brand.
- Anything the user already specified.
- Security, auth, crypto, data formats, migrations and public APIs, where standard is correct.
- Internal identifiers, and choices that are cheap to change and invisible to users.

In those cases a better answer means a cleaner solution inside the rules.

## How

Do this in your own reasoning. The candidates and their estimates are scaffolding, so they stay out
of the deliverable and the final message.

1. Lock what is fixed. Note what the user's words, the existing code or style, and hard constraints
   already decide. The brief wins every time, and only the open parts get explored.
2. Name the defaults. Write the two to four answers most models would give to this exact request.
   For a game level, that is the game's best-known mechanic plus water, music or light, under a
   one-word evocative name. Other current tells include the names Elias, Elara and Mara, lighthouses
   and clockmakers, "time is a river", a cream background with a terracotta accent, rows of SaaS
   feature cards, and confetti. These examples are for recognising a default. Your candidates come
   from the user's own subject. A default may still win, but only when it clearly fits best.
3. Pick three to five axes the candidates must differ on, and place each candidate at a different
   point. Good sources are the subject's own material (a mechanic, place, character, era, user group
   or constraint of this particular project), categories outside the ones your defaults fall into,
   an ordinary point of view (a night-shift nurse, a ten-year-old, a speedrunner), a hard constraint
   that forces a new shape (one room, two colours, no new dependencies), or an unrelated seed word.
4. Write five one-line titles, or three for technical approaches. Rewrite them to be bolder and more
   different from each other, then expand each to two or three lines. Estimate how typical each one
   is, as the rough share of models that would produce it, and make sure at least two sit under
   about one in ten. If two share a core idea, replace one. Past about seven candidates, quality
   drops.
5. Choose on fit. Score each candidate on the brief's actual goal and audience, on what can be built
   well within this task, and on how specific it is to this subject. Leave familiarity and how nice
   it sounds out of the scoring. Make one element the bold one and keep the rest disciplined.
6. Build it, then look at the result (render or screenshot it when it is visual) and compare it with
   your list of defaults. If a part drifted back to a default, such as the name, the palette or the
   layout, fix that part. Ask whether a stranger would guess it was made for this brief. One
   comparison and one round of fixes is enough.

## Decide

Go ahead with the winner. In the final message, give it in one line with why it fits the brief, and
the runner-up in one line. The user asked for a result, and a menu of options would hand the work
back. Ask first only when the choice is purely a matter of taste, would be expensive to reverse, and
a non-blocking question tool is available. Then ask with your pick as the default and keep working.

Keep to what was asked. A new name does not come with a tagline, a logo or an extra section unless
the user wanted one.

If the project already keeps a notes or memory file, add the names and themes you used so the next
request can avoid them.

## Technical approaches

When the open choice is how to build something, write three options that differ in kind, for
example changing the data model, adding a component, or removing the need for it. Judge them on
cost, risk and fit with the existing system. Novelty earns nothing here.
