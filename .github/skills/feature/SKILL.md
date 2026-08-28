---
name: feature
description: >
	Trace a requested feature or behavior change through an existing codebase and produce an
	evidence-based impact map linking requirements to owning symbols, dependencies, tests,
	configuration, and documentation. Use for feature planning, issue refinement, change-impact
	analysis, acceptance criteria, implementation scope, regression risk, and test planning.
argument-hint: "Describe the requested feature or behavior change"
---

# Change Impact and Traceability Skill

Map each requested behavior to the smallest repository-supported implementation and validation surface. Remain read-only: this skill prepares implementation-ready scope and does not modify the project.

## Procedure

### 1. Establish the Behavior Contract

Extract the requested user-visible outcome, inputs, outputs, constraints, compatibility expectations, and explicit non-goals. Split compound requests into independently testable behaviors.

Classify each statement as:

- **required**: explicitly stated by the user or source issue
- **inferred**: supported by repository conventions or existing behavior
- **unresolved**: a product decision whose alternatives materially change behavior or scope

Ask a focused question only when an unresolved decision blocks reliable impact analysis. Include the repository-supported default and the reason for recommending it.

**Complete when:** every requested behavior is stated in observable terms and any blocking ambiguity is explicit.

### 2. Find the Owning Code Path

Start from the most concrete available anchor: an existing route, command, component, service, domain type, test, configuration key, or neighboring implementation. Follow definitions and symbol references to the code that directly decides or mutates the behavior.

Inspect only the nearby evidence needed to identify:

- the entry point and owning symbol
- the data or control-flow path
- public interfaces and persisted or external contracts
- existing tests that exercise the path
- local conventions a compatible implementation should follow

Use filename and text searches to find candidates, then confirm impact with symbol definitions, references, imports, call sites, or executable configuration. Treat a filename match alone as a lead rather than evidence.

**Complete when:** the owning symbol and the dependency path from entry point to observable result are identified, or the report clearly states why the repository contains no such path.

### 3. Build the Impact Map

For each behavior, classify repository elements by evidence:

- **must change**: current code or configuration cannot produce the requested behavior without this change
- **may change**: a likely implementation choice, but another compatible design could avoid it
- **validation only**: tests, fixtures, documentation, or checks that verify or explain the behavior without implementing it
- **out of scope**: nearby code with no dependency or contract connection to the behavior

Record concrete files and symbols, their role, and the evidence connecting them to the request. Include configuration, migrations, generated contracts, documentation, telemetry, and deployment artifacts only when the dependency path reaches them.

Flag risk where the path crosses shared modules, public APIs, persisted data, authorization, concurrency, performance-sensitive code, compatibility boundaries, or external systems.

**Complete when:** every included item has a stated evidence path and every material risk has a corresponding validation point.

### 4. Define Acceptance and Validation

Write numbered acceptance criteria in terms of observable behavior rather than implementation details. Each criterion must identify the relevant precondition or input, action, and expected result.

Map each criterion to focused validation scenarios. Include only applicable categories:

- primary success behavior
- invalid input or failure behavior
- boundary and empty states
- authorization or permission differences
- compatibility and migration behavior
- regression coverage for existing callers
- non-functional limits explicitly required by the request

Prefer extending the nearest existing test layer that can observe the contract. Propose a new test location only when no suitable test boundary exists.

**Complete when:** every acceptance criterion has at least one validation scenario and every identified risk has a check that could reveal a regression.

### 5. Produce the Traceability Report

Return:

1. **Behavior Contract**: required behavior, non-goals, assumptions, and unresolved decisions
2. **Dependency Path**: entry point through owning symbols to the observable result
3. **Impact Map**: must-change, may-change, validation-only, and out-of-scope items with evidence
4. **Acceptance Criteria**: numbered and observable
5. **Validation Matrix**: criterion-to-test mapping and risk coverage
6. **Implementation Order**: the smallest coherent sequence that preserves buildable, testable increments

Use workspace-relative file references and concrete symbol names when available. Distinguish repository evidence from recommendation, and state uncertainty directly.

**Complete when:** each requirement traces to code impact and validation, every included file is justified, and an engineer can begin implementation without repeating the repository investigation.

## Boundaries

- Keep the workflow read-only; produce analysis and scope rather than edits.
- Keep unrelated improvements out of the impact map unless a dependency or contract path connects them.
- Preserve uncertainty by labeling assumptions and may-change items instead of presenting guesses as requirements.
- Stop at a concrete product decision when alternatives produce materially different contracts and repository evidence cannot choose between them.
