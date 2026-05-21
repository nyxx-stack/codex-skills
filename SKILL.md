---
name: cli-builder
description: Guide for building hyper-optimized, agent-native command-line interfaces that autonomous agents can discover, call, validate, retry, and audit. Use when creating or refactoring CLIs, command wrappers, scripts, developer tools, deployment tools, data tools, API CLIs, batch processors, or local tools intended primarily for AI agents rather than humans.
metadata:
  version: "1.0.0"
---

# Agent-Native CLI Builder

## Prerequisites

Designed for agents with shell and filesystem access. The optional validator script (`scripts/validate_agent_cli.py`) requires Python 3.10+.

## Overview

Build command-line interfaces for agents, not humans. Treat the CLI as a typed process-execution API: deterministic inputs, structured outputs, bounded context cost, explicit side effects, and self-describing contracts.

A high-quality agent CLI lets an agent:
- Discover capabilities without reading external docs.
- Construct valid commands without guessing.
- Preview mutation scope before execution.
- Parse every result and error deterministically.
- Retry safely when allowed.
- Produce audit artifacts a reviewer can inspect.

Primary quality metric: how reliably an agent can complete realistic tasks with low token use, low command count, no blocked prompts, no hidden state, and reviewable side effects.

---

# Process

## High-Level Workflow

Creating a high-quality agent CLI has five phases:

1. Deep research and planning
2. Contract design
3. Implementation
4. Review and test
5. Agent evaluations

---

## Phase 1: Deep Research and Planning

### 1.1 Understand agent-native CLI design

Design for autonomous execution:

**Non-interactive by default:** Never require TTY prompts, menus, password dialogs, confirmations, progress spinners, or animated output. Accept all inputs through flags, stdin, files, or environment variables. Fail fast if required input is missing.

**Structured output first:** Default to JSON for agent mode. If the CLI must preserve a human mode, expose `--json` and `--quiet`, and make agent workflows always use them. Data goes to stdout. Diagnostics, warnings, and progress go to stderr.

**Introspection:** Every CLI must expose machine-readable self-description:
- `--help` for concise human-readable usage.
- `--help-json` or `schema` for command schemas.
- `capabilities` for supported operations, auth needs, risk levels, and examples.
- `version` for CLI version, schema version, and feature flags.

**Explicit scope:** Mutating commands must require scope flags such as `--file`, `--dir`, `--resource-id`, `--project`, `--env`, or `--account`. If scope is ambiguous, fail closed.

**Plan before mutation:** Destructive, external, batch, billing, deployment, or data-writing commands must support `--dry-run` or a separate `plan` command. The plan must list intended side effects, touched resources, external calls, validations, and required confirmations.

**Idempotent and retry-safe:** Agents retry. Provide `--idempotency-key`, `--operation-id`, or natural idempotency semantics for writes. Return conflicts as typed errors, not ambiguous failures.

**Bounded context cost:** Default outputs must be compact and limited. Support `--limit`, `--offset`/`--cursor`, `--fields`, `--summary`, and `--output FILE` for large results. Avoid dumping large logs to stdout unless explicitly requested.

**Typed errors:** Error output must be structured, include an error code, explain what was expected, show what was received when safe, and provide the next action.

**Auditability:** Mutations should emit an artifact manifest with command intent, scope, plan, validations, final side effects, warnings, and output file paths.

Read [references/agent-cli-best-practices.md](references/agent-cli-best-practices.md) for the full design contract.

### 1.2 Research the target situation

Before designing commands, inspect the task domain:

- Target users: agents only, or agents plus humans?
- Core tasks: read, search, validate, transform, mutate, deploy, monitor, audit.
- Data models: resources, identifiers, relationships, schema versions.
- Authentication: env vars, config files, keychains, cloud identities, service accounts.
- State model: local-only, remote API, long-running jobs, eventually consistent systems.
- Risk tiers: read-only, local write, remote write, destructive, money/legal/security impact.
- Failure modes: auth, permissions, missing scope, malformed input, rate limits, conflicts, partial success, timeouts.
- Output size: small records, paginated lists, logs, binary artifacts, reports.
- Agent environment: shell, filesystem, network availability, package manager, CI, sandbox limits.

Use web search and primary documentation for any current API, dependency, platform, or standard. Do not rely on memory for version-sensitive details.

### 1.3 Decide CLI shape

Default shape for new CLIs:

```bash
tool capabilities --format json
tool schema --command <command-name> --format json
tool validate <domain> --input file.json --format json
tool plan <domain-action> --scope <scope> --input request.json --output plan.json --format json
tool execute --plan plan.json --confirm --format json
tool status --operation-id <id> --format json
tool logs --operation-id <id> --limit 100 --format jsonl
```

For domain operations, use action-oriented subcommands:

```bash
tool <resource> list --limit 50 --format json
tool <resource> get --id <id> --format json
tool <resource> create --input request.json --dry-run --format json
tool <resource> update --id <id> --input patch.json --dry-run --format json
tool <resource> delete --id <id> --dry-run --confirm --format json
```

Prefer comprehensive primitive operations plus a few high-value workflow commands. Primitive commands give agents composability; workflow commands reduce repeated multi-step command sequences. When uncertain, implement safe primitives first, then add workflows only after real evals show repeated friction.

See [references/architecture-patterns.md](references/architecture-patterns.md) for command archetypes.

### 1.4 Choose implementation stack

Default stack when constraints are unknown:
- Python 3.10+ with `argparse`, `json`, `dataclasses`, and no required external packages.
- Add Pydantic/Typer only if the project already accepts dependencies and needs richer validation.
- Use TypeScript with Commander/Zod when the target ecosystem is Node/TypeScript.
- Use Rust with clap/serde when single-binary distribution, startup time, or high-throughput parsing dominates.

Do not pick a stack because it is fashionable. Pick the smallest stack that can enforce schemas, produce deterministic output, and test non-interactivity.

See [references/implementation-guides.md](references/implementation-guides.md) for templates.

---

## Phase 2: Contract Design

### 2.1 Write the CLI contract before code

Create a contract document with:

- CLI name and version.
- Global flags.
- Command list.
- Required/optional arguments.
- Input schema for each command.
- Output schema for each command.
- Error codes.
- Exit codes.
- Risk tier per command.
- Dry-run behavior.
- Idempotency behavior.
- Pagination behavior.
- Artifact outputs.
- Auth/environment requirements.
- Examples using JSON/stdin/files.

### 2.2 Global flags

Include these unless the situation proves they are unnecessary:

```text
--format json|jsonl|text        Default: json for agent mode.
--quiet                         Suppress non-essential diagnostics.
--no-color                      Disable ANSI output.
--input FILE                    Read structured input from file.
--stdin-json                    Read JSON request from stdin.
--output FILE                   Write large result/artifact to file.
--limit N                       Bound list/log output.
--cursor TOKEN                  Continue pagination.
--fields a,b,c                  Return selected fields only.
--dry-run                       Preview side effects without executing.
--confirm                       Required for destructive/stateful execution.
--idempotency-key KEY           Deduplicate safe retries.
--timeout SECONDS               Bound runtime.
--trace-id ID                   Correlate logs and audit records.
--help-json                     Print machine-readable interface.
```

Avoid ambiguous positionals except obvious input paths. Prefer long flag names over short flags.

### 2.3 Output envelopes

Success envelope:

```json
{
  "schema_version": "1.0",
  "ok": true,
  "command": "resource.create",
  "operation_id": "op_...",
  "risk": "remote_write",
  "data": {},
  "artifacts": [],
  "warnings": [],
  "next_actions": []
}
```

Error envelope:

```json
{
  "schema_version": "1.0",
  "ok": false,
  "command": "resource.create",
  "operation_id": null,
  "error": {
    "code": "invalid_scope",
    "message": "Scope is required for remote writes.",
    "expected": "--project and --env",
    "received": "--env staging",
    "next_action": "Retry with --project <project-id> --env staging."
  },
  "warnings": []
}
```

JSONL streaming event:

```json
{"schema_version":"1.0","event":"progress","operation_id":"op_...","step":"validate","ok":true}
```

Use the schemas in [assets/agent_cli_contract.schema.json](assets/agent_cli_contract.schema.json) and [assets/error_envelope.schema.json](assets/error_envelope.schema.json).

### 2.4 Exit codes

Document exit codes in `--help` and `--help-json`.

Recommended mapping:

| Code | Meaning |
|---:|---|
| 0 | success |
| 1 | runtime/internal error |
| 2 | invalid arguments or malformed input |
| 3 | validation failed |
| 4 | resource not found |
| 5 | authentication missing/invalid |
| 6 | authorization denied |
| 7 | conflict/already exists/stale state |
| 8 | rate limited |
| 9 | timeout |
| 10 | external dependency unavailable |
| 11 | unsafe operation blocked |
| 12 | partial success; inspect `data.failures` |

Avoid using shell-reserved meanings such as command-not-found or permission-denied codes for application semantics.

### 2.5 Safety model

Risk tiers:

```text
read_only          No state change.
local_write        Writes local files only.
remote_write       Changes external service state.
destructive        Deletes, overwrites, deploys, rotates secrets, or irreversible action.
regulated          Money, legal, medical, security, identity, PII, production infrastructure.
```

Rules:
- `read_only`: may execute directly.
- `local_write`: require explicit output path or scope.
- `remote_write`: require `--dry-run` support and explicit scope.
- `destructive`: require `--dry-run`, `--confirm`, and typed audit artifact.
- `regulated`: require all destructive controls plus provenance, review artifacts, and conservative defaults.

---

## Phase 3: Implementation

### 3.1 Project structure

Recommended structure:

```text
agent-cli/
├── pyproject.toml | package.json | Cargo.toml
├── README.md
├── src/
│   ├── cli entrypoint
│   ├── contracts/          # schemas and envelopes
│   ├── commands/           # command handlers
│   ├── clients/            # API/filesystem clients
│   ├── validation/         # input/output validators
│   └── audit/              # plan and artifact generation
├── schemas/
│   ├── capabilities.schema.json
│   ├── success.schema.json
│   └── error.schema.json
├── tests/
│   ├── test_non_interactive.*
│   ├── test_output_contracts.*
│   ├── test_exit_codes.*
│   └── test_agent_scenarios.*
└── examples/
    ├── request.json
    ├── plan.json
    └── success.json
```

### 3.2 Core infrastructure

Implement shared utilities before domain commands:

- Envelope builder for success/error JSON.
- Error-code registry.
- Exit-code registry.
- Schema validation.
- JSON/JSONL writer.
- Stderr diagnostic writer.
- Pagination helpers.
- Timeout handling.
- Auth loader with explicit missing-auth errors.
- Dry-run plan model.
- Audit artifact writer.
- Idempotency key handling.
- Deterministic sorting and stable timestamps.

### 3.3 Command implementation rules

For each command:

1. Parse only explicit inputs.
2. Validate arguments before external calls.
3. Reject ambiguity; do not infer risky scope.
4. Run preflight checks.
5. For mutations, build a plan before execution.
6. Execute only after required confirmation gates.
7. Emit a success/error envelope.
8. Keep stdout parseable.
9. Send warnings and diagnostics to stderr.
10. Bound output and support pagination.
11. Include examples in `--help`.
12. Add tests for success, invalid input, missing auth, not found, and retry behavior.

### 3.4 Hyper-optimization rules

Optimize for agent runtime, not terminal aesthetics:

- Minimize command count for common workflows.
- Keep `capabilities`, `schema`, and `--help-json` fast and network-free.
- Lazy-load heavy dependencies after argument validation.
- Default to compact JSON; provide pretty output only behind `--pretty`.
- Let agents request only needed fields with `--fields`.
- Write large artifacts to files and return paths.
- Use JSONL for streaming logs/progress.
- Include enough error detail for one-shot correction.
- Avoid hidden prompts, colored tables, spinners, progress bars, paging, browser launches, or editor launches.
- Use stable key names and deterministic ordering.
- Make all side effects visible in the result envelope.

---

## Phase 4: Review and Test

### 4.1 Static review

Check:

- No command blocks on stdin unless `--stdin-json` is set.
- No interactive prompt is reachable in agent mode.
- All commands support parseable output.
- All mutation commands support dry-run or plan mode.
- All destructive commands require `--confirm`.
- Every output includes `schema_version`.
- Errors include `code`, `message`, and `next_action`.
- Exit codes match documented meanings.
- Large outputs are paginated or written to files.
- Auth failures never leak secrets.
- Paths and resource IDs are echoed only when safe.

### 4.2 Run the validator

From the skill root, run:

```bash
python3 scripts/validate_agent_cli.py -- <your-cli> --format json
```

The validator checks basic agent-readiness signals:
- `--help` exits successfully.
- Output is not ANSI-decorated by default.
- Commands do not hang waiting for input.
- JSON output parses when available.
- `--help-json`, `capabilities`, or `schema` exists when implemented.

The validator is a heuristic. It does not replace command-specific tests.

### 4.3 Contract tests

For every command, add tests that assert:
- stdout is valid JSON/JSONL in agent mode.
- stderr never contains required data.
- invalid input returns exit code 2 and a typed error.
- missing auth returns exit code 5 and a typed error.
- unsafe mutation without `--confirm` returns exit code 11.
- `--dry-run` causes no side effects.
- repeated execution with the same idempotency key is safe.

---

## Phase 5: Agent Evaluations

Create evals that test whether an agent can use the CLI without hidden knowledge.

Minimum eval set:

1. Discover available commands from `capabilities`.
2. Inspect command schema and construct a valid read command.
3. Handle malformed input using the typed error next action.
4. Paginate through a large result set.
5. Use `--fields` to reduce output.
6. Create a dry-run plan for a mutation.
7. Execute a previously generated plan with confirmation.
8. Abort a destructive command without confirmation.
9. Recover from missing auth instructions.
10. Produce an audit summary from artifacts.

Store eval prompts in `evals/evals.json`. See [references/evaluation.md](references/evaluation.md).

---

# Reference Files

Load these resources as needed:

## Core design reference

- [Agent CLI Best Practices](references/agent-cli-best-practices.md) — detailed contract for agent-native CLI design, output formats, errors, safety, and token efficiency.

## Architecture patterns

- [Architecture Patterns](references/architecture-patterns.md) — command archetypes, canonical command sets, risk models, plan/execute workflows, and output envelope variants.

## Implementation guides

- [Implementation Guides](references/implementation-guides.md) — minimal templates for Python, TypeScript, and Rust, plus testing patterns.

## Evaluation guide

- [Evaluation Guide](references/evaluation.md) — eval design, assertions, grading, and iteration loop for measuring agent CLI effectiveness.

## Assets and scripts

- [Success/contract schema](assets/agent_cli_contract.schema.json)
- [Error envelope schema](assets/error_envelope.schema.json)
- [Capabilities schema](assets/capabilities.schema.json)
- [Agent help template](assets/agent_help_template.md)
- [CLI validator](scripts/validate_agent_cli.py)
