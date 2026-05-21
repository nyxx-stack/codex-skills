# Agent CLI Best Practices

## Contents

- Design target
- Non-negotiable rules
- Input contract
- Output contract
- Error contract
- Safety contract
- Token-efficiency contract
- Introspection contract
- Anti-patterns
- Research sources

## Design target

An agent-native CLI is a process-execution API. It may be typed by text, but it should behave like a structured protocol.

Optimize for:
- deterministic command construction
- stable schemas
- explicit risk boundaries
- small parseable outputs
- safe retries
- auditability
- low agent context cost

Do not optimize for:
- conversational prompts
- colorful terminal UI
- animated progress
- implicit human assumptions
- clever abbreviations
- hidden defaults with side effects

## Non-negotiable rules

1. No interactivity in agent mode.
2. stdout contains final structured data only.
3. stderr contains diagnostics, progress, warnings, and debug output.
4. Every output envelope includes `schema_version`.
5. Every error has a stable code and next action.
6. Every mutation has explicit scope.
7. Every risky mutation has dry-run or plan mode.
8. Destructive operations require `--confirm`.
9. Large outputs are paginated, summarized, or written to files.
10. Capabilities and schemas are discoverable offline.

## Input contract

### Prefer explicit flags

Good:

```bash
deployctl release create \
  --project proj_123 \
  --env staging \
  --input release.json \
  --dry-run \
  --format json
```

Bad:

```bash
deployctl create release
```

### Use stdin for complex JSON

Avoid shell-escaped JSON strings.

Good:

```bash
cat request.json | tool resource create --stdin-json --dry-run --format json
```

Bad:

```bash
tool resource create --payload '{"name":"x","rules":["a","b"]}'
```

### Use files for large inputs

Use `--input FILE` and `--output FILE` to avoid context-heavy terminal streams.

### Validate before side effects

Argument and input validation must run before network calls or filesystem writes when possible.

### Reject ambiguity

When several scopes are plausible, fail with `invalid_scope` rather than guessing.

## Output contract

### Default JSON envelope

Use a single envelope for all commands unless streaming.

```json
{
  "schema_version": "1.0",
  "ok": true,
  "command": "resource.list",
  "operation_id": "op_123",
  "data": {
    "items": [],
    "next_cursor": null
  },
  "artifacts": [],
  "warnings": [],
  "next_actions": []
}
```

### JSONL for streaming

Each line must be a complete JSON object.

```jsonl
{"schema_version":"1.0","event":"started","operation_id":"op_123"}
{"schema_version":"1.0","event":"progress","step":"validate","ok":true}
{"schema_version":"1.0","event":"completed","ok":true}
```

### Artifact manifest

Use artifacts for large outputs:

```json
{
  "path": "artifacts/plan-123.json",
  "type": "plan",
  "bytes": 2048,
  "sha256": "..."
}
```

### Stable fields

Do:
- use snake_case or camelCase consistently
- include null for known-but-empty fields
- keep key names stable across versions
- add fields backward-compatibly

Do not:
- emit tables in agent mode
- depend on color
- mix prose with JSON in stdout
- reorder arrays nondeterministically
- change meanings without schema version bump

## Error contract

Error envelope:

```json
{
  "schema_version": "1.0",
  "ok": false,
  "command": "resource.update",
  "operation_id": null,
  "error": {
    "code": "invalid_arguments",
    "message": "--resource-id is required.",
    "expected": "--resource-id <id>",
    "received": null,
    "next_action": "Retry with --resource-id set to the target resource."
  },
  "warnings": []
}
```

Error qualities:
- precise
- bounded
- non-secret-leaking
- retry guidance included
- mapped to documented exit code

Recommended error codes:
- `invalid_arguments`
- `invalid_input`
- `invalid_scope`
- `validation_failed`
- `not_found`
- `auth_missing`
- `auth_invalid`
- `permission_denied`
- `conflict`
- `rate_limited`
- `timeout`
- `dependency_unavailable`
- `unsafe_operation_blocked`
- `partial_success`
- `internal_error`

## Safety contract

### Risk tiers

| Tier | Meaning | Required controls |
|---|---|---|
| read_only | no state change | bounded output |
| local_write | writes local files | explicit output path |
| remote_write | changes external state | explicit scope + dry-run |
| destructive | delete/overwrite/deploy/secrets | dry-run + confirm + audit |
| regulated | money/legal/security/PII/prod | destructive controls + provenance |

### Plan object

Plan output should include:

```json
{
  "plan_id": "plan_123",
  "risk": "remote_write",
  "scope": {
    "project": "proj_123",
    "env": "staging"
  },
  "operations": [
    {
      "type": "update",
      "target": "resource_456",
      "before": {},
      "after": {},
      "reversible": true
    }
  ],
  "external_calls": [],
  "validations": [],
  "requires_confirm": true
}
```

### Confirmation

Use an explicit flag:

```bash
tool execute --plan plan.json --confirm --format json
```

Do not prompt:

```text
Are you sure? [y/N]
```

## Token-efficiency contract

Agent outputs compete for context. Keep outputs bounded.

Required controls:
- `--limit`
- `--cursor`
- `--fields`
- `--summary`
- `--output FILE`
- compact JSON by default
- `--pretty` only when requested
- log streaming via JSONL
- default log limits

For large inspect/list operations, return:
- summary counts
- top N items
- cursor for continuation
- artifact path for full output

## Introspection contract

`capabilities` should return:

```json
{
  "schema_version": "1.0",
  "tool": "example",
  "version": "1.2.3",
  "commands": [
    {
      "name": "resource.list",
      "risk": "read_only",
      "description": "List resources.",
      "input_schema_ref": "schema://resource.list.input",
      "output_schema_ref": "schema://resource.list.output",
      "examples": [
        "example resource list --limit 20 --format json"
      ]
    }
  ],
  "auth": {
    "required": true,
    "env": ["EXAMPLE_API_KEY"]
  }
}
```

`schema --command X` should return:
- input schema
- output schema
- error schema
- exit-code mapping
- examples
- risk tier
- dry-run/confirm requirements

## Anti-patterns

Avoid:
- interactive prompts
- progress spinners
- colored tables in agent mode
- human-only doc pages as the only source of truth
- required browser login in the middle of execution
- implicit current directory as mutation scope unless clearly documented
- position-dependent magic arguments
- unbounded stdout logs
- returning success with warnings that imply failure
- non-deterministic output ordering
- generic exit code 1 for all failures
- hidden retries with invisible side effects
- destructive defaults
- silent partial success
- changing schema without versioning

## Research sources

This reference was designed from current Agent Skills guidance, public agent-friendly CLI design writeups, and traditional CLI conventions. Re-check current primary docs during implementation because specific libraries and platform behaviors change.
