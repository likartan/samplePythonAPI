---
name: refractor
description: >
	Refactor an existing codebase through a specification-first, behavior-preserving workflow.
	Use when the user asks to refactor, refractor, restructure, clean up, remove duplication,
	improve design, normalize source whitespace, or split tangled code into cohesive modules.
	Establish current behavior, agree on intended changes, add characterization tests, deepen
	the owning module, and validate by compiling, testing, and running the result.
user-invokable: true
---

# Specification-First Refactoring

Refactor from evidence. Preserve established behavior deliberately, change known defects explicitly, and leave the codebase in an executable, tested state.

## Completion Contract

Finish only when all applicable conditions hold:

- current and target behavior are documented or otherwise explicitly agreed;
- every intended behavior change is distinguishable from structural refactoring;
- affected behavior has automated characterization or acceptance coverage;
- the implementation has clearer ownership and fewer invalid states;
- source hygiene issues in the touched area are removed;
- the narrowest relevant compile and tests pass; and
- the application or affected executable path runs successfully when the environment supports it.

Report any unavailable validation with the exact environmental blocker.

## Workflow

### 1. Establish the Baseline

Start from the file, symbol, failing behavior, or command named by the user. Read only enough nearby code to identify the module that directly owns the behavior.

Collect facts from the environment rather than asking the user:

- repository structure and local instructions;
- build and test configuration;
- current diagnostics;
- available compiler or runtime toolchain;
- current program output where execution is possible;
- unusual encoding, non-ASCII whitespace, trailing whitespace, or generated artifacts; and
- existing uncommitted changes that must be preserved.

State one falsifiable hypothesis about the current design problem and one cheap check that could disprove it. Avoid broad exploration once the owning code path is clear.

**Complete when:** the current behavior, owning module, available validation command, and relevant source-hygiene issue are known.

### 2. Create or Confirm the Grounding Specification

Look for an existing specification first. If none exists and behavior or intent is ambiguous, create a concise grounding document before implementation.

Separate:

- **Current behavior:** observable output, ordering, thresholds, boundary comparisons, return values, error modes, and known defects.
- **Target behavior:** preserved behavior, intentional corrections, validation rules, and exact acceptance criteria.
- **Non-goals:** adjacent features and redesigns outside the request.
- **Design guidance:** suggested structure that remains non-normative unless the user requires it.

Resolve product and domain decisions with the user. Recommend a concrete answer for each open decision. Find filesystem, toolchain, and code facts yourself.

Do not silently promote a defect into a requirement. Do not silently fix a defect during a behavior-preserving refactor.

**Complete when:** the user has confirmed the behavior boundary or an existing authoritative specification already settles it.

### 3. Characterize the Behavior

Add or identify the cheapest tests that can distinguish preserved behavior from regression. Prefer tests through the module's public interface.

Cover the risks present in the code, including applicable cases such as:

- normal behavior and complete sample output;
- exact threshold boundaries and strict versus inclusive comparisons;
- validation failures and deterministic error ordering;
- empty, zero-result, duplicate, and malformed inputs;
- insertion order and tie-breaking;
- additive calculations and independent rule contributions; and
- rejected input not mutating valid state.

Run the narrow test before structural edits when practical. If the code is not testable at its current seam, make the smallest reversible edit that exposes a testable interface, then validate immediately.

**Complete when:** the affected observable behavior has a check capable of failing on a regression.

### 4. Deepen the Owning Module

Refactor toward a small interface with cohesive behavior behind it. Keep callers responsible for orchestration and adapters; keep domain invariants and policy in the owning module.

Apply these design moves only where supported by the code:

- replace parallel collections with one record or value type;
- replace sentinel ambiguity and silent failure with explicit results when the specification allows it;
- validate before mutating state;
- centralize named immutable policy values;
- separate domain calculations from console, file, network, or framework I/O;
- accept output streams or dependencies at a seam when that makes behavior naturally testable;
- make read-only operations `const` where appropriate;
- remove broad namespace imports from headers and shared code; and
- split files when it creates a real module interface, not merely more files.

Preserve public interfaces unless the agreed target behavior requires a change. Prefer standard-library facilities and the repository's existing patterns over new dependencies.

After the first substantive edit, immediately run the cheapest focused validation. Repair the same slice and rerun that check before widening scope.

**Complete when:** callers learn less, invariants live with the data they govern, and the characterization check passes.

### 5. Normalize Source Hygiene

Clean only the touched area and directly related files:

- replace non-breaking or other accidental Unicode spaces with ordinary ASCII indentation;
- remove trailing whitespace and redundant blank lines;
- preserve the repository's indentation and line-ending conventions;
- remove unused includes and stale comments exposed by the refactor; and
- keep comments only where they explain non-obvious intent.

Use a source-aware formatter when the repository already configures one. Otherwise make focused edits and scan the result for non-ASCII or trailing whitespace.

**Complete when:** touched source is consistently formatted and the hygiene scan is clean.

### 6. Validate End to End

Use the repository's configured commands. When configuration is absent, use the installed native toolchain directly and add minimal portable build support only when it materially helps the codebase.

Validate in this order:

1. diagnostics for touched files;
2. narrow compile with a strong warning level;
3. focused characterization tests;
4. broader relevant tests;
5. application execution and actual output; and
6. final whitespace or formatter check.

On Windows, check Visual Studio installations through `vswhere` when `cl.exe` is not on `PATH`, and load `VsDevCmd.bat` before compiling. Treat a successful compile, passing tests, and successful execution as separate evidence.

Do not claim tests passed based only on editor diagnostics. Do not claim successful execution based only on compilation.

**Complete when:** all available checks pass and actual output agrees with the grounding specification.

## Scope Discipline

- Preserve unrelated user changes and generated files.
- Keep structural edits close to the requested behavior.
- Avoid speculative abstractions, runtime configurability, persistence, concurrency, or new frameworks unless the specification requires them.
- Keep policy changes separate from structural refactoring so failures have one plausible cause.
- Prefer one deep module over several shallow pass-through wrappers.
- Update documentation when the behavior contract changes.

## Final Report

Summarize:

- the module and behavior refactored;
- intentional behavior changes versus preserved behavior;
- files added or changed;
- compile, test, execution, and hygiene results; and
- any validation that remains blocked.

Keep the report concise and link to relevant workspace files.

## Realistic Test Prompts

Use these prompts to verify the skill after installation:

1. `Refactor this C++ device monitor without changing its threshold behavior. Remove the strange spaces and add tests.`
2. `Clean up this legacy module. First document what it does today, then separate validation from console output and prove the behavior still works.`
3. `Refractor the selected class to remove parallel arrays and magic numbers, preserve output exactly, and run the program afterward.`
