---
name: requirement
description: "Discover project requirements and implement the configuration needed to make a project usable. Use when setting up a new repository, configuring an existing project, adding development tooling, or turning incomplete requirements into package, build, test, lint, format, environment, editor, and CI configuration."
argument-hint: "Describe the project and the configuration it needs"
---

# Project Configuration Requirements

Turn a project setup request into a verified configuration. Work from repository evidence first, clarify only unresolved decisions, then edit the project rather than stopping at recommendations.

## Procedure

### 1. Inspect the Project

Identify the repository root and inspect the smallest set of files that reveals the current stack and setup state:

- README and contributor instructions
- dependency manifests and lock files
- source and test layout
- existing build, lint, format, test, editor, environment, container, and CI configuration
- documented or executable project commands

Treat existing files and conventions as the source of truth. Preserve the selected language, framework, package manager, runtime, and configuration style unless the request explicitly changes them.

**Complete when:** the project type, existing tooling, missing configuration, and likely validation commands are known.

### 2. Define the Requirements

Translate the request and repository evidence into a short checklist covering only relevant categories:

- target runtime, language, and framework versions
- dependency and package management
- build and local development commands
- tests, linting, formatting, and type checking
- environment variables and secret handling
- editor or workspace settings
- containers, CI, deployment, or infrastructure
- supported operating systems and developer prerequisites

Classify each item as **confirmed**, **inferred**, or **unresolved**. Infer conventional, reversible details from the repository. Ask focused questions for choices that are expensive to reverse, affect external systems, require credentials, or have multiple materially different answers.

When questions are necessary, ask no more than three related questions at once and include a recommended default with its reason.

**Complete when:** every setup decision is confirmed or safely inferred, and unresolved blockers have an explicit user decision.

### 3. Plan the Configuration

State a concise implementation plan before editing. Name the files to create or update, the commands the setup will expose, and the validation that will prove each requirement works.

Prefer:

- existing repository patterns over new abstractions
- one authoritative configuration source over duplicated settings
- committed example environment files containing placeholders, with real secrets excluded
- pinned or constrained versions consistent with the ecosystem and existing lock file
- scripts that work through the repository's chosen package or build tool

Keep optional tooling out of scope unless it satisfies a stated requirement or is necessary for a reliable baseline.

**Complete when:** every planned edit maps to a requirement and has a checkable validation step.

### 4. Implement the Setup

Create or update the configuration files and dependency manifests. Install dependencies with the project's package manager when tools permit it. Preserve unrelated user changes and avoid replacing valid configuration wholesale when a focused edit will work.

For a new or nearly empty repository, establish only the minimum coherent baseline needed to install, build, run, test, and contribute. Add brief setup documentation when commands, prerequisites, or environment variables would otherwise be undiscoverable.

Never place passwords, tokens, connection strings, private keys, or other secrets in tracked files. Use environment-variable references and sanitized examples.

**Complete when:** all planned configuration exists, dependencies resolve, and the documented commands match the actual configuration.

### 5. Validate End to End

Run the narrowest relevant checks after the first edit, then finish with all setup-critical commands available in the repository. Depending on the project, validate:

1. dependency installation or restore
2. configuration parsing and type checking
3. lint and format checks
4. tests
5. build or package output
6. application startup or a smoke test

Repair configuration defects revealed by these checks and rerun the failing command. Report pre-existing or environment-specific failures separately rather than hiding them.

**Complete when:** every configured workflow has executable evidence, or each unverified item has a precise blocker and a command the user can run once that blocker is removed.

## Final Response

Summarize:

- the requirements implemented and important defaults chosen
- the configuration files created or changed
- the validation commands and their results
- any remaining user decisions, prerequisites, or secret values that must be supplied outside version control

Do not claim the project is configured successfully when critical validation was skipped or failed.

## Example Requests

- "Set up this TypeScript project with build, test, lint, and formatting configuration."
- "Inspect this repository and finish the missing local development setup."
- "Configure a Python service for contributors, including environment variables and CI checks."
- "Turn these project requirements into working configuration files and verify them."
