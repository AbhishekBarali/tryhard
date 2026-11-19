# Using it for real

Read this before you use the result for real, and before you tell the judge how to see it. The aim
is to meet the result the way its user will, through its real entry point, and keep what you saw.

## What to do for each kind of work

A small change needs one real run of the changed path. A bigger build gets the row that fits.

| Kind | What to do | Evidence to keep |
| --- | --- | --- |
| Web page or app | Serve it and drive it with real clicks and typing. Look at the first screen before scrolling, a phone width and the busiest realistic state. Read the console. | A screenshot of each state you claim, and the console output |
| Game | Start it and play it with scripted input. Get past the menu and through the core loop, one loss, and one win, restart or level change. | A frame and the game state from the same moment at each of those points, and the error log |
| 3D scene or visual asset | Render it at its real display size from the default camera and one more angle. | The renders, set against the brief or a reference |
| Desktop app | Launch it and click through the main flow, with the environment's computer-use or editor tools if it has them. | Screenshots of the main flow |
| Command-line tool | Run the built command as a user would, with `--help`, a real input, a bad input, and an empty or very large input. | The output and exit codes |
| API or service | Start it and send real requests, including an invalid one. Read back what was stored. | The requests and responses |
| Library | Write a short caller in a temporary folder that uses the public API the way the docs describe. | The caller and its output |
| Document or slides | Render to PDF or images and look at every page. | The rendered pages |

## How to do it

- Before you start, list what you will check, drawn from the request, from what you built, and from
  every claim you plan to make in the final message, plus two cases off the happy path. The final
  message claims only what has a check.
- Open every screenshot or render you rely on, for example with `view_image`. A screenshot you did
  not open is no evidence. When a screenshot and a number disagree, believe the screenshot.
- Keep three questions apart. Does it work, does it look right, and does it fit the screen sizes it
  is meant for. A passing click-through says nothing about the look, and a good screenshot says
  nothing about whether it works. Code may set up state, but the steps that prove the result use
  real input.
- A check you write counts only after you have seen it fail once, for example by breaking the code
  on purpose and restoring it. Exit codes from game engines and test runners need a look at the log
  as well.
- For web games, a debug-only hook that prints the game state as text and one that advances time by
  a fixed step make scripted play reliable. Keep them out of the shipped build or behind a flag. Fix
  the first new console error before anything else.
- Use the best tool the environment offers. First its own browser, computer-use or engine
  connection, then a headless browser or a command run from a temporary folder, then software
  rendering under a virtual display, then the closest real check. The final message says what you
  could not see, such as motion, sound or feel on a real device.
- Add no test framework, global install or new dependency to the user's project just to look.
- Keep the evidence, meaning screenshots, state dumps, logs and the command that runs the result, in
  a folder under the system temp folder, or in `.tryhard/evidence/` when raise-the-bar is running.
  The judge gets that folder and the run command.
- Before the final message, stop the servers, browsers and watchers you started and delete your own
  temporary files, keeping the saved versions and the evidence the report points to.

## What counts as proof

| Claim | Evidence it needs |
| --- | --- |
| It works or is fixed | The real entry point, or the check that failed before the change, now passing |
| Tests pass | This session's test output with zero failures, from tests that cover the change |
| It looks right | A render or screenshot you opened, at real size |
| It meets the request | The request and the brief re-read line by line against the result |
| A subagent did it | The diff or output it points to, read by you |

Missing or indirect evidence means the item is unchecked, and the final message says so.
