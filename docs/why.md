# Why Done Done works the way it does

GPT-6.2 Astra and GPT-6.2 Sol came out on 17 November 2026. In the first days, testers and users
described the same few problems again and again. This page goes through each one: what people
reported, what Done Done does about it, and where the technique comes from.

Quotes are kept short. Everything else is paraphrased, so follow the links for the original
wording. Dates are publication dates where known.

## Contents

1. [Stopping early or doing the minimum](#1-stopping-early-or-doing-the-minimum)
2. [Blocking on questions nobody can answer](#2-blocking-on-questions-nobody-can-answer)
3. [Loops that go nowhere](#3-loops-that-go-nowhere)
4. [The same default answer as everyone else](#4-the-same-default-answer-as-everyone-else)
5. [Explanations nobody can read](#5-explanations-nobody-can-read)
6. [Raise the bar: iterating until it is good](#6-raise-the-bar-iterating-until-it-is-good)
7. [Reasoning effort](#7-reasoning-effort)
8. [What Done Done deliberately avoids](#8-what-done-done-deliberately-avoids)

## 1. Stopping early or doing the minimum

### What was reported

- One user said that when asked to QA a new feature, 6.1 Sol would investigate the issues, fix them and summarise, while 6.2 Sol often listed the issues and stopped. It did this even when told to find the root cause and fix the problems ([r/codex, "Is 6.2 Sol really that bad?"](https://www.reddit.com/r/codex/comments/1xz8b5x/is_62_sol_really_that_bad/), 18 Nov 2026).
- Dan Shipper said Every's testing found Astra 6.2 often stopped too early in real coding tasks, which made end-to-end builds frustrating ([Dan Shipper on X](https://x.com/danshipper/status/2122754729012777052) and the [Every vibe check](https://every.to/vibe-check/vibe-check-gpt-6-2-astra-and-sol-leave-us-wanting-more), 17 Nov 2026).
- The habit of ending on an offer is not unique to GPT. A user described Claude Fable closing long runs with "shall I do that?" about opening a PR for work they had never seen ([r/singularity, "Theo on why 6.2 Astra is bad"](https://www.reddit.com/r/singularity/comments/1xysrpg/theo_on_why_62_astra_is_bad), 17 Nov 2026).
- The opposite also shows up. One user's Astra turned "password must be 12 characters long or more" into entropy checks that always failed, and kept moving its own goalposts ([r/singularity 1xysrpg](https://www.reddit.com/r/singularity/comments/1xysrpg/theo_on_why_62_astra_is_bad), 17 Nov 2026). Sol at max effort started a fix when the user had only asked a question ([r/codex, "6.2 Sol max does things that he's not asked to"](https://www.reddit.com/r/codex/comments/1xz70k4/62_sol_max_does_things_that_hes_not_asked_to), 18 Nov 2026).
- In an Opus-supervised comparison, Sol's own check confirmed a bug as correct behaviour, and twice its proof runs never touched the new code ([r/codex, "GPT-6.2 Sol just dropped"](https://www.reddit.com/r/codex/comments/1xytl9j/gpt62_sol_just_dropped_and_users_are_already/), 17 Nov 2026).
- OpenAI had already said of GPT-6 Astra that it may reach a first implementation and come back for review while work remains. Their fix is to define completion before starting ([OpenAI, "Rethinking skills and prompts for GPT-6 Astra"](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)). The 6.2 Codex guide makes the same point: tell the model what counts as finished and what you will look for when you review ([Prompting GPT-6.2 in Codex](https://learn.chatgpt.com/guides/prompting-gpt-6-2-astra), Nov 2026).

### What Done Done does

The `finish-the-job` skill and the always-on block:

- State in a line or two what finished looks like and what a reviewer would check, before any work starts.
- Take requirements literally. "12+ characters" means a length of at least 12. A stronger idea goes in the report, and the criteria don't grow or shrink during the run.
- Do the whole job. With write access, "QA this" means find, reproduce, find the cause, fix, check again and report. Report-only happens when the user asks for it, or asks for a review or a plan. A plain question gets an answer and no code changes.
- Claim "done", "fixed" or "passes" only with fresh evidence from this session, checked through the real entry point. A subagent's claim is checked against the diff.
- Review the finished work once, fix the serious issues and mention minor ones only if the user would trip over them. After that, more polishing or extra validation is treated as wasted effort.
- For substantial work, hand the request, the done criteria and the diff to a fresh reviewer that assumes the work is not done, then make one fix pass.
- Don't end on an offer to do work that is inside the task. Do it, then report it. The Stop hook catches turns that end this way anyway and sends the model back once.

### Why this approach

- Defining done first is OpenAI's own top advice for these models (guide and blog above).
- The evidence-before-claims rule comes from [superpowers' verification skill](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md), a widely copied pattern in open-source agent skills. Superpowers keeps tables of common excuses with rebuttals, and its v6.2.0 notes report that deleting one set of rebuttals measurably weakened test-first behaviour under pressure ([release notes](https://github.com/obra/superpowers/blob/main/RELEASE-NOTES.md), Jul 2026). `finish-the-job` carries a short table of the excuses seen in the reports above.
- The fresh reviewer follows Anthropic's finding that agents grading their own work tend to praise it, while a separate evaluator is far easier to make sceptical ([Anthropic, harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps), Mar 2026). Users suggested the same pattern for these models: pair two models so one checks the other's work ([r/codex 1xz8b5x](https://www.reddit.com/r/codex/comments/1xz8b5x/is_62_sol_really_that_bad/); [Voxyz on X](https://x.com/Voxyz_ai/status/2123038513352622087), 18 Nov 2026).
- The "no polishing after done" rule borrows from [oh-my-openagent's GPT-6 Astra rules](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/packages/omo-codex/plugin/components/rules/bundled-rules/hephaestus/gpt-6.md), which call another validation pass or drive-by cleanup after done a defect. It is there so the push to finish does not turn into the paranoid over-checking users described.
- The scope limits (every changed line traces to the request, unrelated bugs stay out of the diff) come from the "surgical changes" idea in [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md) and from Codex's own base instructions ([default.md](https://github.com/openai/codex/blob/main/codex-rs/protocol/src/prompts/base_instructions/default.md)).
- Compared with 6.1 Sol, the 6.2 base prompt in Codex no longer tells the model not to stop at a plan or an offer to continue ([models.json in openai/codex](https://github.com/openai/codex/blob/main/codex-rs/models-manager/models.json), 17 Nov 2026). Done Done puts that idea back, bounded by the task's scope.

## 2. Blocking on questions nobody can answer

### What was reported

- Theo's letter to OpenAI describes Astra running a long `/goal` well with subagents, then blocking about two hours in on a question about which of two clip files its own reviewer had written. He ended up running other agents on a timer just to check whether Astra had blocked itself ([Theo on X](https://x.com/theo/status/2122760447103484410), 17 Nov 2026; [summary at implicator.ai](https://www.implicator.ai/gpt-6-2-astra-early-testers-theo-letter), 17 Nov 2026).
- One user said Sol 6.2 keeps coming back for authorisation before finishing a task, many times more than any other model ([r/codex 1xz8b5x](https://www.reddit.com/r/codex/comments/1xz8b5x/is_62_sol_really_that_bad/), 18 Nov 2026). Another said Astra refused to run their code because local credentials were present ([r/singularity 1xysrpg](https://www.reddit.com/r/singularity/comments/1xysrpg/theo_on_why_62_astra_is_bad), 17 Nov 2026).
- Another user's Sol 6.2 could not write to the project folder. Without asking, it started writing to a different folder until the disk ran out of space, deleted what it had made, and then stopped ([r/singularity 1xysrpg](https://www.reddit.com/r/singularity/comments/1xysrpg/theo_on_why_62_astra_is_bad), 18 Nov 2026).
- OpenAI's guide for 6.2 in Codex says to leave routine decisions about how to do the work to Codex ([Prompting GPT-6.2 in Codex](https://learn.chatgpt.com/guides/prompting-gpt-6-2-astra)). Its GPT-6 Astra guide already noted that the model is more likely to ask when more input could change the result ([GPT-6 Astra guide](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra)).

### What Done Done does

- An ask-or-decide test. Ask only when all three hold: only the user can know it, the answer changes the result in a way that is costly to redo, and there is no safe reversible default. Otherwise look it up or decide, note the decision in one line and keep going.
- Never ask about your own work. Files, clips, branches and logs made in this session are on disk and can be inspected.
- When a real user-only question comes up, finish everything that doesn't depend on it, use Codex's non-blocking question tool if it is there, and otherwise put the question in the final report with the default already applied.
- A plain list of what needs no permission (reading, workspace edits, builds, tests, declared dependencies, local commits on a work branch) and what does (deleting work you didn't make, deploying or publishing where others use it, messages to other people, spending money, shared infrastructure, production data, changing the goal).
- Local credentials are normal and no reason to stop. A path that isn't writable gets reported or an access request, never a quiet switch to another folder.
- The Stop hook catches a final question that names files or IDs the user never mentioned and sends the model back to inspect them.

### Why this approach

- [Superpowers' executing-plans skill](https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md) has the agent make rulings on ambiguities, log them, and list them at the end, stopping only for a short list of real risks. Its v7.0.2 release gave the brainstorming skill a similar rule, asking only when the answer would change what gets built, and reported fewer filler questions in blind-graded tests ([release notes](https://github.com/obra/superpowers/blob/main/RELEASE-NOTES.md), Nov 2026).
- Research on when agents should ask points the same way. A filter for questions that are relevant and that the user can actually answer matched a strong baseline with far fewer questions ([Asking What Matters, arXiv 2604.14624](https://arxiv.org/abs/2604.14624), Apr 2026). Loose prompts lead to over-asking and strict ones to silent wrong defaults, so the policy has to be stated ([Ambig-DS, arXiv 2605.09698](https://arxiv.org/abs/2605.09698), May 2026). That is why every "decide" comes with a logged decision the user can reverse.
- Codex ships a non-blocking question tool, and its persistent-mode prompt keeps questions pending while useful work continues ([request_user_input_async](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/request_user_input_async.rs); [persistent_mode.md](https://github.com/openai/codex/blob/main/codex-rs/prompts/templates/persistent_mode.md)).
- Codex's goal template only allows "blocked" after the same blocker repeats for three goal turns, never just because work is hard ([continuation.md](https://github.com/openai/codex/blob/main/codex-rs/ext/goal/templates/goals/continuation.md), Nov 2026). Done Done uses the same rule so the two never disagree.
- OpenAI warns that strict boundary wording can make Astra stop where you would be happy for it to continue ([OpenAI skills blog](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)). So the skill grants authority for routine work in plain terms, and it has no approval steps.

## 3. Loops that go nowhere

### What was reported

- Theo's ts-rust run: Astra worked for 7 days and landed no improvements. It fixated on the "also make it smaller" part of the request and made the compiler 56% slower. Told to drop size and close the performance gap, it ran 4 more days and landed nothing ([Theo on X](https://x.com/theo/status/2122760447103484410), 17 Nov 2026).
- One user said Astra never seemed to settle on a single goal and kept moving its own goalposts ([r/singularity 1xysrpg](https://www.reddit.com/r/singularity/comments/1xysrpg/theo_on_why_62_astra_is_bad), 17 Nov 2026).

### What Done Done does

The `set-a-goal` skill writes `.goal/contract.md` before a long run. It holds the objective, one primary metric with the command that measures it and a baseline taken on the untouched code, guardrails, secondary goals in priority order, non-goals, done-when checks each with a proof command, and budgets. The work happens on a new `goal/...` git branch, and `.goal/` is kept out of git so resets never touch it. Then it starts the Codex goal with a short objective that points at the contract. The long-run rules:

- The primary metric wins. A change that makes it worse by more than noise is dropped, whatever it does for a side goal.
- One idea per attempt. Commit, measure, keep it only if it beats the best so far by more than noise, otherwise reset to the best commit.
- An append-only ledger of attempts and a short status file, read at the start of each turn.
- A stall rule. Reading and investigating don't count as attempts, only changes that get measured do. After 3 attempts without a keep, change to a different mechanism. After 2 such changes without a keep, write a stall report that says what would unblock it.
- Tests and benchmarks are read-only. A fresh evaluator decides "done".
- A token budget is set only when you name one. Without one, the stall rule still ends the run with a report.
- For tasks without a number, such as a game level or a design, the done-when checks plus an evaluator's rubric take the metric's place.

### Why this approach

- The keep-or-reset ratchet comes from [Karpathy's autoresearch](https://github.com/karpathy/autoresearch/blob/master/program.md) (Mar 2026). It measures a baseline first, keeps a change only if the metric improves and resets otherwise. Under a rule like this, a commit that made ts-rust slower would not have been kept.
- Codex's goal template already checks for no-progress turns and audits completion strictly, but it has no metric, baseline or goal order ([continuation.md](https://github.com/openai/codex/blob/main/codex-rs/ext/goal/templates/goals/continuation.md), Nov 2026). So investigation that never lands anything can still count as progress. The contract adds what is missing, and its wording matches the template on keeping the full objective and on when "blocked" is allowed.
- Anthropic's long-running harness work keeps a progress file and git log that every session reads first, a feature list where only the pass flag may change, and tests the agent may not edit ([Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), Nov 2025). In their compiler project, agents kept a running note of failed approaches ([Building a C compiler with parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler), Feb 2026).
- One of OpenAI's own long Codex runs froze goals, non-goals and "done when" in a spec file, with validation commands for each milestone ([Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)). OpenAI's goal guide asks for one objective, one stopping condition, and commands that prove progress ([Follow a goal](https://learn.chatgpt.com/use-cases/follow-goals)).
- The evaluator is separate because agents tend to report progress the measurements don't show. In one testbed, an agent claimed improvement on every cycle while 56% of cycles had no measured gain ([Park and Choi, arXiv 2607.25152](https://arxiv.org/abs/2607.25152), Jul 2026). Anthropic also found self-grading skews positive (harness design post above).

## 4. The same default answer as everyone else

### What was reported

- Theo and Ben each asked Astra for a unique level in a different video game. Both got a level themed on water, music and bells, named "Bellwether" ([Theo on X](https://x.com/theo/status/2122760447103484410), 17 Nov 2026). A Sol user got "The Upfall Reservoir", water again ([r/ChatGPT](https://www.reddit.com/r/ChatGPT/comments/1xz6oyu/something_is_seriously_wrong_with_62_astra), 18 Nov 2026).
- Arena's review found every website Astra and Sol built used the same template, with invented branding, category labels and a green palette, whatever the brief ([Arena, "GPT 6.2 vs Claude Fable 5.2", 21:04](https://www.youtube.com/watch?v=jk7rTk1Bh8I&t=1264s), 17 Nov 2026). One viewer added that it keeps reaching for the word "Vesper" and for bells when asked to be creative.
- One user called both Sol and Astra 6.2 terrible at design. Asked to redesign a section of a marketing site, the model missed its point and built a different section ([r/codex 1xz8b5x](https://www.reddit.com/r/codex/comments/1xz8b5x/is_62_sol_really_that_bad/), 18 Nov 2026).
- The ability is there. Theo credits Astra with occasional novel solutions that are genuinely great when it explores, and Arena found that a brief demanding breadth, such as a hundred ways to draw a dog, did bring out real variety ([Arena, 40:10](https://www.youtube.com/watch?v=jk7rTk1Bh8I&t=2410s)).

### What Done Done does

The `fresh-ideas` skill runs only when a task leaves open a choice the user will see: names, themes, a level or story concept, visual direction, copy tone, or genuinely different technical approaches. It does not run for bug fixes, work that must follow existing conventions, or anything the user already specified. When it runs, it:

- writes down what is already fixed by the request and the project;
- names the 2 to 4 answers any model would give, using a few current tells as calibration;
- picks axes the candidates must differ on, then writes 5 candidates as titles first (3 for technical approaches);
- makes them bolder and more different, estimates how typical each is and keeps at least two unusual ones;
- chooses on fit to the brief, spends boldness in one place, builds, and checks the result has not drifted back to a default;
- decides instead of handing a menu to the user, and doesn't invent branding or sections nobody asked for.

### Why this approach

- The sameness is well documented. Across more than 70 models, answers to open-ended prompts were highly similar within a model and between models ([Artificial Hivemind, arXiv 2510.22954](https://arxiv.org/abs/2510.22954), Oct 2025). A 2026 study of model-written stories found the same few names and settings, such as Elara and lighthouses, in most of them ([Hamilton and Mimno, arXiv 2605.26492](https://arxiv.org/abs/2605.26492), May 2026).
- [Verbalized Sampling](https://arxiv.org/abs/2510.01171) (Oct 2025) traces much of this to preference tuning favouring typical answers. Asking for several candidates with estimated probabilities raised creative diversity without hurting accuracy, and the authors note that asking for too many candidates at once lowers quality. That is where the 5 candidates and the "keep two unusual ones" rule come from.
- Writing short idea titles first and then rewriting them bolder and more distinct helped idea diversity in a 2026 ideation study ([Deng, Brucks and Toubia, arXiv 2602.20408](https://arxiv.org/abs/2602.20408), Feb 2026). Prompts that demand explicit divergence, such as going outside conventional categories, raised novelty in another study, though outputs still clustered across models ([IDEAFix, arXiv 2606.00875](https://arxiv.org/abs/2606.00875), May 2026).
- Anthropic's [frontend-design skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) roots choices in the subject's own world, names the defaults AI designs cluster around, and tells the model to spend its boldness in one place. The Arena reviewer's published prompts use explicit "this must not be..." lists of lazy outcomes ([petergpt/3d-prompt-collection](https://github.com/petergpt/3d-prompt-collection)).
- The tell list is calibration only. Banning one habit tends to move the default somewhere else, as when GPT-5.6 Sol learned to avoid purple gradients and then put confetti in over a quarter of its designs ([Design Arena via YouMind](https://youmind.com/es-ES/landing/x-viral-articles/gpt-5-6-sol-design-taste), Jul 2026).
- The narrow trigger and the "stay conventional" list exist because creativity in bug fixes or security code is a defect, and because fit to the brief comes before novelty.

## 5. Explanations nobody can read

### What was reported

- Theo called Astra's output the hardest to parse of any model he had used this year. Asked why git worktrees were slow on one machine, it wrote four paragraphs about package-manager internals, where another model simply said the SSD was slow. He tried system prompt changes and asking for "eli5", and neither worked ([Theo on X](https://x.com/theo/status/2122760447103484410); [implicator.ai](https://www.implicator.ai/gpt-6-2-astra-early-testers-theo-letter), 17 Nov 2026).
- Dan Shipper said Every found Astra 6.2's writing a step back from Astra 6, so concise that it is hard to understand ([Dan Shipper on X](https://x.com/danshipper/status/2122754729012777052), 17 Nov 2026). OpenAI itself describes 6.2 Astra as more concise by default and suggests revisiting "be concise" instructions ([Using GPT-6.2](https://developers.openai.com/api/docs/guides/latest-model), Nov 2026).
- OpenAI's system card found Astra left a known blocker out of its final answer in about 22% of test runs, roughly twice the rate of GPT-6 Astra, and guessed this was linked to its push for concise answers with fewer caveats. The Codex developer prompt reduced it ([GPT-6.2 system card](https://deploymentsafety.openai.com/gpt-6-2-astra-sol), 17 Nov 2026).
- A Codex issue reports Astra at max effort quietly narrowing tasks without saying what it left out ([openai/codex#62258](https://github.com/openai/codex/issues/62258), 18 Nov 2026).

### What Done Done does

`finish-the-job`, `explain-plainly` and the always-on block share one shape for the final message, written as short ordered paragraphs:

1. The answer or result in one or two plain sentences. For a "why", the main cause and its evidence.
2. What changed, in plain words.
3. How it was checked, and plainly what was not checked.
4. Any part of the request that was not done or could not be finished, and why.
5. Decisions made for the user that they may want to change, each with the default already applied, and anything only they can decide.

Empty parts are left out. The message is written for someone who saw only their own request, so it contains no run numbers, subagent names or labels made up during the work. The `explain-plainly` skill adds a pre-send check and one worked before-and-after example. The Stop hook asks for one rewrite when a long message opens with a wall of code names or stacked semicolons.

### Why this approach

- The open-items paragraph is never cut, because OpenAI ties hidden blockers to the push for brevity (system card above). Done Done asks for plain words, and never for short ones.
- OpenAI's guide asks the model not to carry working shorthand or jargon from the run into what it writes ([Using GPT-6.2](https://developers.openai.com/api/docs/guides/latest-model)). Anthropic's prompting guide asks for writing aimed at an intelligent reader who lacks the context, with key points first and no terms invented along the way ([Prompting Fable 5.2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2)).
- Superpowers found that problems of shape respond to a positive recipe, and that a list of bans did worse than the recipe in their tests ([writing-skills](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md)). The [humanizer skill](https://github.com/blader/humanizer/blob/main/SKILL.md) works from paired before-and-after examples. So `explain-plainly` gives a shape and an example instead of a list of banned words.
- "Bottom line up front" is an old writing rule for busy readers ([BLUF](https://en.wikipedia.org/wiki/BLUF_(communication))).
- The shape avoids colons after labels, semicolons and "X, not Y" framing, because the 6.2 base prompt forbids them and a conflicting template would cost the model effort to reconcile ([models.json](https://github.com/openai/codex/blob/main/codex-rs/models-manager/models.json)).
- Theo found that asking alone did not help, so the hook adds a mechanical check that does not depend on the model obeying a style rule. Its thresholds are meant to leave good messages alone.

## 6. Raise the bar: iterating until it is good

### What was reported

- In Arena's review, Astra's best result was a peacock drawing that the reviewer kept pushing over many turns with "do more, be better". He called it the best he had seen. One-shot results in the same video were described as lazy and boring ([Arena, 38:41](https://www.youtube.com/watch?v=jk7rTk1Bh8I&t=2321s), 17 Nov 2026).
- That result cost several times a single generation, and the review gives no matched one-shot comparison.
- A commenter on r/codex put the general point this way: give these models a real target, say what good looks like and what done means, and they do better work for less money ([r/codex 1xz8b5x](https://www.reddit.com/r/codex/comments/1xz8b5x/is_62_sol_really_that_bad/), 18 Nov 2026).

### What Done Done does

`$donedone:raise-the-bar` runs the loop the reviewer drove by hand:

- Write the bar first: 3 to 6 checks a demanding expert would apply and a short "this must not be..." list of lazy outcomes. For open choices, run `fresh-ideas`.
- Build a complete first version, then look at it for real by running, rendering, screenshotting or measuring it.
- Review it as that expert, with a fresh subagent where possible that gets only the brief, the bar and the result. Name the biggest gaps, fix them and check again.
- Stop when a pass finds only minor issues or brings no visible or measurable improvement, with a default cap of 5 passes. Never trade the main goal for a side goal.
- Report what each pass improved, in plain words.

It is explicit-only because it costs more, and most tasks don't need it.

### Why this approach

- The reviewer's own prompts set a quality bar and a "this must not be..." list before building ([petergpt/3d-prompt-collection](https://github.com/petergpt/3d-prompt-collection)). The skill writes that brief itself.
- Anthropic found a separate, sceptical evaluator, working to a definition of done agreed before each chunk of work, far easier to get right than self-grading ([harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps), Mar 2026). In a 2026 comparison of 17 verification designs, independent review by a critic gave a better accuracy-for-cost trade-off than the other checking layers ([arXiv 2610.34577](https://arxiv.org/abs/2610.34577), Oct 2026).
- The stop rule and the cap exist because a loop without them is how ts-rust ran for 11 days. Anthropic's Ralph loop plugin calls its iteration cap the main safety mechanism ([ralph-loop](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop)).

## 7. Reasoning effort

Codex's model catalog sets both 6.2 models to low effort by default ([models.json](https://github.com/openai/codex/blob/main/codex-rs/models-manager/models.json), 17 Nov 2026). OpenAI's launch charts, as reported by AIHubMix, show the LifeVal benchmark score at low effort dropping from 66.8% to 25.3% for Sol compared with 6.1 Sol, and from 67.5% to 46.3% for Astra compared with GPT-6 Astra ([AIHubMix](https://aihubmix.com/blog/gpt-6-2-migration-prefix-edits-drop-reasoning-and-none-is-rejected), 18 Nov 2026). OpenAI's Codex guide maps effort to the job: medium for a quick survey, high for tracing one cause across systems, extra high when several causes may interact. It adds that higher effort helps the model stay with a long task through the final checks ([Prompting GPT-6.2 in Codex](https://learn.chatgpt.com/guides/prompting-gpt-6-2-astra)). The catalog describes ultra as maximum reasoning with automatic task delegation. Hence the README's advice of high or xhigh for real work and ultra for work that splits into parallel parts.

## 8. What Done Done deliberately avoids

- **"Be concise" or word limits.** These models already over-compress, and OpenAI links brevity pressure to hidden blockers.
- **"ELI5".** It failed for Theo and talks down to experts. The skill writes for an intelligent reader without context.
- **"Never stop" or "always do more".** Sol already over-reaches, and an unbounded push is how loops start. Every loop here has a measurable exit, a cap and a report at the cap.
- **"Always write tests" or "be exhaustive".** The base prompt limits new tests, and OpenAI says GPT-6 Astra can already test more broadly than small tasks need ([GPT-6 Astra guide](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra)).
- **Approval steps and check-ins after the first version.** OpenAI says a required stop for review after the first implementation pulls Astra toward an earlier stop ([OpenAI skills blog](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)).
- **ALL CAPS and stacks of "always" and "never".** Strong wording gets over-applied. Each rule explains its reason instead.
- **A long AGENTS.md.** OpenAI's guide says AGENTS.md is for what Codex can't infer from the code, tests or docs ([Prompting GPT-6.2 in Codex](https://learn.chatgpt.com/guides/prompting-gpt-6-2-astra)), so the always-on block is about 2 KB.
- **Creating goals for ordinary tasks.** Codex's `create_goal` tool is meant only for goals the user explicitly asked for, so only `set-a-goal`, which the user invokes by name, starts one.
