# Agent CLI Architecture Patterns

## Contents

- Command archetypes
- Canonical command families
- Primitive vs workflow commands
- Plan/execute architecture
- Long-running jobs
- Batch operations
- Local file operations
- API wrappers
- Discovery interfaces
- Naming patterns

## Command archetypes

### Inspector

Read-only command that returns current state.

```bash
tool service get --id svc_123 --format json
tool service list --project proj_123 --limit 50 --format json
```

Requirements:
- no side effects
- bounded output
- pagination for lists
- `--fields` for token control

### Validator

Checks input without changing state.

```bash
tool config validate --input config.json --format json
```

Requirements:
- exit code 0 if valid
- exit code 3 if validation fails
- data includes precise issue locations

### Planner

Creates an execution plan.

```bash
tool deploy plan --project proj_123 --env staging --input deploy.json --output plan.json --format json
```

Requirements:
- no side effects except writing plan artifact
- includes risk tier and side-effect list
- validates scope and permissions when possible

### Executor

Executes a plan or direct command.

```bash
tool execute --plan plan.json --confirm --format json
```

Requirements:
- refuses missing confirmation when risk requires it
- emits operation ID
- writes audit artifact
- idempotent if retried with same plan/idempotency key

### Monitor

Reads status for long-running work.

```bash
tool status --operation-id op_123 --format json
tool logs --operation-id op_123 --limit 100 --format jsonl
```

Requirements:
- pollable
- JSON/JSONL
- bounded by default

### Exporter

Writes large output to files.

```bash
tool report export --scope proj_123 --output report.json --format json
```

Requirements:
- stdout returns artifact manifest, not full payload
- output file hash and byte count included

## Canonical command families

### Minimal universal surface

Every serious agent CLI should implement:

```bash
tool --version
tool --help
tool --help-json
tool capabilities --format json
tool schema --command <name> --format json
```

### Read/write resource surface

```bash
tool <resource> list
tool <resource> get
tool <resource> validate
tool <resource> create --dry-run
tool <resource> update --dry-run
tool <resource> delete --dry-run --confirm
```

### Workflow surface

Use for repeated multi-command tasks:

```bash
tool workflow plan <workflow-name> ...
tool workflow execute --plan plan.json --confirm
```

## Primitive vs workflow commands

Primitive commands:
- maximize composability
- map to resources
- lower implementation ambiguity
- are easier to test

Workflow commands:
- reduce command count
- encode domain procedures
- improve reliability for repeated tasks
- can overfit if added too early

Default rule:
1. Implement safe primitives.
2. Run agent evals.
3. Add workflow commands only where agents repeatedly waste steps or make predictable mistakes.

## Plan/execute architecture

Plan artifacts should be complete enough to execute later without recalculating intent.

Plan fields:
- `plan_id`
- `created_at`
- `schema_version`
- `cli_version`
- `intent`
- `scope`
- `risk`
- `inputs_hash`
- `operations`
- `expected_side_effects`
- `validations`
- `requires_confirm`
- `expires_at` when applicable

Execution should:
1. read plan
2. validate plan schema
3. verify plan is not expired
4. verify current state if stale-state risk exists
5. require confirmation if needed
6. execute operations
7. emit result and audit artifact

## Long-running jobs

For operations exceeding a few seconds:

- Start returns `operation_id`.
- `status` returns current state.
- `logs` streams bounded JSONL.
- `cancel` exists only if cancellation is safe and documented.
- Completion result includes final artifacts.

Example:

```bash
tool job start --input job.json --format json
tool status --operation-id op_123 --format json
tool logs --operation-id op_123 --limit 100 --format jsonl
```

## Batch operations

Batch commands must report partial success explicitly.

Output shape:

```json
{
  "schema_version": "1.0",
  "ok": false,
  "error": {
    "code": "partial_success",
    "message": "7 of 10 operations succeeded.",
    "next_action": "Inspect data.failures and retry failed items with the same idempotency key."
  },
  "data": {
    "success_count": 7,
    "failure_count": 3,
    "failures": []
  }
}
```

Use exit code 12 for partial success.

## Local file operations

For file-writing CLIs:

- require `--output` or explicit target path
- write temp file then atomic rename
- never overwrite unless `--overwrite` or `--confirm`
- include file hashes in artifacts
- support `--dry-run` with predicted paths

## API wrappers

For external APIs:

- expose auth requirements in `capabilities`
- use explicit env var names
- support rate-limit errors
- return request IDs when safe
- do not print tokens or secrets
- provide `--timeout`
- expose pagination cursors
- support idempotency keys for writes where possible

## Discovery interfaces

### `capabilities`

Returns broad command inventory.

### `schema`

Returns detailed contract for one command.

### `examples`

Optional command returning executable examples:

```bash
tool examples --command resource.create --format json
```

Each example should include:
- command
- stdin/file payload if needed
- expected output sketch
- risk tier
- required env vars

## Naming patterns

Use:
- lowercase subcommands
- hyphenated long flags
- resource nouns and action verbs
- stable names over clever names

Avoid:
- overloaded verbs
- abbreviations agents may misread
- flags whose meaning changes by command
- single-letter flags in generated agent plans
