# Agent Help Template

Use this structure for `--help` or `help <command>`.

```text
Usage:
  {tool} {command} [OPTIONS]

Purpose:
  {one_sentence_purpose}

Risk:
  {read_only|local_write|remote_write|destructive|regulated}

Required:
  --scope <scope>          Explain scope.
  --input <file>           JSON input file.

Options:
  --format json|jsonl|text Default: json.
  --output <file>          Write large output to file.
  --limit <n>              Bound output.
  --dry-run                Preview side effects.
  --confirm                Required for execution when risk is destructive.
  --idempotency-key <key>  Deduplicate retries.

Exit codes:
  0 success
  2 invalid arguments/input
  5 auth failure
  11 unsafe operation blocked

Examples:
  {tool} {command} --scope example --input request.json --dry-run --format json
  cat request.json | {tool} {command} --stdin-json --scope example --format json

Output:
  stdout: JSON envelope
  stderr: diagnostics only
```
