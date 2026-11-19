# Stopping early, and when a problem will not move

Read this before ending a turn with any part of the request unfinished, unchecked or below the bar,
or with a question or an offer to the user, and when three attempts in a row at one problem have
made no measurable progress.

## Thoughts that mean you are about to stop early

| The thought | What is true |
| --- | --- |
| "It runs, so it's done." | Running is the first draft. Use it for real and have it judged against the bar. |
| "Reporting the issues is enough." | When the user asked for QA or a fix and you can edit the files, they want it working. Fix, then report. |
| "The user didn't ask for that part." | If a thoughtful expert would assume it belongs to this request, it is part of the job. If it serves a different request, leave it out. |
| "The judge's findings are small." | Blocking and visibly weaker findings get fixed before you stop. Truly minor ones can stay, and the report mentions any the user would trip over. |
| "The user should confirm first." | Reversible work inside the task is already authorized. Do it and report it. |
| "I'll ask which file they meant." | If it is in the repo or you made it, you can look. Check, pick, note it. |
| "One more round to be safe." | The stop rule decides. Once it holds, extra rounds are polish nobody asked for. |
| "This part is hard, I'll leave it." | Keep at it until the stall rule below says to stop, then report that part as open with what blocks it. |

## The stall rule

An attempt is one change you try for one problem. It counts as progress when a check newly passes,
failures drop, a number improves, or a judge's finding is now fixed in use. Reading, searching and
diagnostics are investigation and do not count.

After three attempts in a row with no progress, switch to a different mechanism. New values for the
same idea count as the same mechanism. Allow three approaches in all. When the third approach has
also gone three attempts without progress, stop working on that problem, finish the parts that do
not depend on it, and report what you tried, what blocks it, and the one decision or resource that
would unblock it. In a Codex goal, leave the goal active and follow its blocked rule.
