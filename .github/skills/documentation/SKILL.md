---
name: documentation
description: "Document a repository, module, package, or public API through an evidence-based workflow: confirm scope, analyze files and logic, write or update inline documentation, generate Sphinx output, and review for accuracy and drift. Use for documentation generation, missing or stale docstrings, API documentation, module documentation, repository documentation, Sphinx-backed docs, documentation audits, or documentation maintenance."
argument-hint: "Describe the repository, module, or API to document and the target audience"
---

# Documentation Workflow

Document source code from evidence, then generate and review the published output. Execute the phases in order and preserve an explicit artifact from each phase:

1. Scope specification
2. Evidence map and documentation plan
3. Inline documentation changes
4. Generated documentation and build log
5. Review decision and maintenance follow-up

Generated output is never the source of truth. Correct source files, documentation sources, or Sphinx configuration and regenerate.

## Workflow State

Track the active phase and its output in the task list or progress log. Record failures with the phase, command or check, relevant file or symbol, observed result, and next action. A phase advances only when its completion criterion is met.

Use these return transitions:

- Documentation content, docstring, example, directive, or reference failure: return to phase 3.
- Sphinx configuration, dependency, extension, builder, or environment failure: remain in phase 4.
- Missing evidence or misunderstood implementation behavior: return to phase 2.
- Changed audience, repository boundary, standards, goal, or exclusion: return to phase 1.

## Phase 1: Scope Identification

Translate the request into a proposed scope. Establish:

- target audience, documentation goal, and expected deliverables
- target files, packages, modules, public APIs, and generated surfaces
- repository documentation standards and neighboring conventions
- boundaries, exclusions, and non-goals
- applicable source and generated documentation locations

Infer clear details from the request and repository. Ask the human owner only about consequential ambiguity. Treat a narrow, explicit request as approved scope; present broad, ambiguous, or repository-wide scope for confirmation before editing.

**Phase output:** a scope specification listing audience, goals, targets, standards, deliverables, boundaries, and exclusions.

**Complete when:** every requested deliverable maps to an in-scope source or generated artifact and no consequential boundary is unresolved.

## Phase 2: File and Logic Analysis

Read the in-scope source, tests, configuration, and existing documentation. Start at public entry points and trace only far enough to explain observable behavior and implementation intent. Inspect:

- public functions, classes, modules, commands, configuration, and extension points
- parameters, return values, exceptions, side effects, state transitions, and lifecycle constraints
- call sites, dependencies, control flow, and tests that establish intended use
- existing docstrings, comments, type contracts, examples, pages, and generated API coverage
- differences between current behavior and current documentation

Treat implementation and tests as evidence, not permission to guess. Resolve conflicts or report them. Classify each target as missing, stale, ambiguous, incorrect, or already sufficient.

Create an evidence map with one entry per documentation target:

| Target | Source evidence | Current gap | Destination | Planned change |
|--------|-----------------|-------------|-------------|----------------|
| symbol, file, or API | code, test, call site, or config | classification | docstring, type hint, comment, page, or none | concise action |

**Phase output:** an evidence map and ordered documentation plan covering the approved scope.

**Complete when:** every planned change names its evidence and destination, and every in-scope public contract is covered or explicitly dispositioned.

## Phase 3: Inline Documentation Application

Apply source-level documentation before invoking Sphinx:

- Write or update docstrings for in-scope public modules, classes, functions, and methods.
- Document supported parameters, return values, exceptions, side effects, state changes, and usage constraints.
- Add or refine type annotations when they form part of the repository's documentation contract and do not alter runtime behavior.
- Add focused comments only for non-obvious intent, invariants, or decisions that names and structure cannot express.
- Add examples that match the current implementation and can be checked by an existing test or documentation mechanism when available.
- Preserve local style and the repository's configured docstring convention.

Do not silently change product behavior to make documentation easier. Surface required behavior changes as separate work. After the first substantive edit, run the narrowest available test, type check, lint, doctest, or import check for the touched source and repair in-scope failures before continuing.

**Phase output:** committed-ready source changes implementing the evidence map, plus focused validation results.

**Complete when:** every evidence-map item is applied or explicitly dispositioned, source behavior is unchanged unless requested, and focused checks pass or have a precise blocker.

## Phase 4: Sphinx Automation and Generation

Load and follow the complete [Sphinx documentation skill](../sphinx-documentation/SKILL.md) for Sphinx discovery, configuration, dependencies, extensions, builders, warning diagnosis, and rendered-output validation.

Configure or refresh `conf.py`, autodoc, Napoleon, source paths, toctrees, and extensions only as required by the approved scope and repository conventions. Generate the requested outputs and retain the command results as the build log.

Inspect each failure before editing:

- Return to phase 3 for invalid docstrings, malformed documentation content, examples, directives, or references.
- Stay in phase 4 for configuration, package import wiring, missing extensions, builder setup, dependency, or environment failures.

Never repair generated HTML, doctrees, inventories, or build artifacts directly.

**Phase output:** generated documentation and a build log for each affected builder.

**Complete when:** the relevant builders exit successfully with warnings treated as failures, or each remaining failure has a precise external blocker and owner.

## Phase 5: Review and Maintenance

Review source changes and representative generated pages against the scope specification and evidence map. Verify:

- documented behavior agrees with source, tests, and public contracts
- all in-scope targets are complete and no unsupported claims were introduced
- navigation, cross-references, examples, and visible assets render correctly
- build logs contain no warnings, broken references, or missing modules
- generated output and transient build files are handled according to repository policy

Prepare an engineer sign-off summary with scope, evidence consulted, files changed, generated output location, checks run, build results, limitations, and decisions requiring approval. Classify corrections using the workflow return transitions and rerun from the owning phase.

For maintenance, treat later changes to documented code, APIs, tests, dependencies, and configuration as drift signals. Flag stale sections and schedule phases 2 through 4 again; return to phase 1 when the original scope no longer holds.

**Phase output:** approval or a classified correction list, plus maintenance actions for detected drift.

**Complete when:** generated output matches the approved scope and source behavior, findings are closed or routed to an owning phase, and the human owner has the evidence needed for sign-off.

## Final Report

Report:

- approved scope and audience
- evidence and public contracts analyzed
- inline documentation and Sphinx source/configuration changed
- validation and builder commands with results
- generated output location
- review status, drift findings, and routed follow-up
- any blocked or unverified work with its exact cause
