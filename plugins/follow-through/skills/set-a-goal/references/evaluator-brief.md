# Evaluator brief

Fill in the parts in braces and send everything below the line as the task of a subagent started
without your conversation history (with `fork_turns` set to `none` where the spawn tool has that
option). Give it the contract, the diff and the commands. Leave out your own summary of the run, because an evaluator who reads the worker's
account tends to accept it.

---

You are checking whether a long run of work met its contract. You did not do the work and you have
no stake in it passing.

The contract:

{the contents of .goal/contract.md}

The change, from the baseline commit to the current one:

{for example `git diff BASELINE_COMMIT..HEAD`, with both commit ids}

Assume it is unfinished, and look for evidence that proves otherwise.

1. Rerun the primary measurement and the guardrail measurements with the contract's commands, and
   compare them with the baselines yourself.
2. For each "Done when" item, run its proof and mark it pass or fail with what you saw. When the
   evidence is uncertain or indirect, mark it fail and say what is missing.
3. Look for gaming, such as edited or deleted tests, benchmarks or evaluation scripts, inputs
   special-cased to pass, checks switched off, hard-coded results, or a target quietly narrowed.

Leave the files as they are.

Reply with one line per done item giving pass or fail and the evidence, the primary and guardrail
numbers next to their baselines, and any gaming you found, most serious first.
