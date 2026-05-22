# Implementation Guides

## Contents

- Python default template
- TypeScript template
- Rust template
- Test patterns
- JSONL writer
- Help JSON guidance

## Python default template

Use this when constraints are unknown and minimal dependencies matter.

```python
#!/usr/bin/env python3
import argparse
import json
import sys
import time
from dataclasses import dataclass, asdict
from typing import Any

SCHEMA_VERSION = "1.0"

EXIT = {
    "success": 0,
    "runtime": 1,
    "invalid_arguments": 2,
    "validation_failed": 3,
    "not_found": 4,
    "auth": 5,
    "permission": 6,
    "conflict": 7,
    "rate_limited": 8,
    "timeout": 9,
    "dependency": 10,
    "unsafe": 11,
    "partial_success": 12,
}

def emit(obj: dict[str, Any]) -> None:
    print(json.dumps(obj, separators=(",", ":"), sort_keys=True))

def success(command: str, data: dict[str, Any], **extra: Any) -> int:
    emit({
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "command": command,
        "operation_id": extra.get("operation_id"),
        "data": data,
        "artifacts": extra.get("artifacts", []),
        "warnings": extra.get("warnings", []),
        "next_actions": extra.get("next_actions", []),
    })
    return EXIT["success"]

def error(command: str, code: str, message: str, expected=None, received=None, next_action=None, exit_code=1) -> int:
    emit({
        "schema_version": SCHEMA_VERSION,
        "ok": False,
        "command": command,
        "operation_id": None,
        "error": {
            "code": code,
            "message": message,
            "expected": expected,
            "received": received,
            "next_action": next_action,
        },
        "warnings": [],
    })
    return exit_code

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="example")
    p.add_argument("--format", choices=["json", "jsonl", "text"], default="json")
    p.add_argument("--quiet", action="store_true")
    sub = p.add_subparsers(dest="command")

    cap = sub.add_parser("capabilities")
    cap.set_defaults(handler=handle_capabilities)

    schema = sub.add_parser("schema")
    schema.add_argument("--command", required=True)
    schema.set_defaults(handler=handle_schema)

    return p

def handle_capabilities(args) -> int:
    return success("capabilities", {
        "tool": "example",
        "version": "0.1.0",
        "commands": [
            {
                "name": "capabilities",
                "risk": "read_only",
                "description": "List supported commands.",
                "examples": ["example capabilities --format json"]
            }
        ],
        "auth": {"required": False, "env": []}
    })

def handle_schema(args) -> int:
    if args.command != "capabilities":
        return error(
            "schema",
            "not_found",
            "Unknown command.",
            expected="capabilities",
            received=args.command,
            next_action="Run `example capabilities --format json` to list commands.",
            exit_code=EXIT["not_found"],
        )
    return success("schema", {"command": "capabilities", "input_schema": {}, "output_schema": {}})

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help(sys.stderr)
        return EXIT["invalid_arguments"]
    return args.handler(args)

if __name__ == "__main__":
    raise SystemExit(main())
```

## TypeScript template

Use when the surrounding project is TypeScript/Node.

Recommended libraries:
- Commander for command parsing.
- Zod for input/output validation.
- Native `JSON.stringify` for compact output.
- No chalk/spinners in agent mode.

Core pattern:

```ts
import { Command } from "commander";
import { z } from "zod";

const program = new Command();

function emit(obj: unknown) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

function ok(command: string, data: unknown) {
  emit({ schema_version: "1.0", ok: true, command, data, artifacts: [], warnings: [], next_actions: [] });
}

function fail(command: string, code: string, message: string, next_action: string, exitCode = 1) {
  emit({ schema_version: "1.0", ok: false, command, error: { code, message, next_action }, warnings: [] });
  process.exitCode = exitCode;
}

program
  .command("capabilities")
  .option("--format <format>", "json|jsonl|text", "json")
  .action(() => ok("capabilities", { tool: "example", version: "0.1.0", commands: [] }));

program.parse();
```

## Rust template

Use when distribution and cold-start performance dominate.

Recommended libraries:
- clap for parsing
- serde/serde_json for schemas and envelopes
- thiserror for error mapping

Core requirements:
- implement `--help`
- implement JSON envelope serialization
- map errors to documented exit codes
- avoid interactive crates in agent mode

## Test patterns

### Non-interactivity test

Run command with stdin closed and short timeout. It must not hang.

```bash
timeout 3s tool capabilities --format json < /dev/null
```

### JSON parse test

```bash
tool capabilities --format json | python3 -m json.tool >/dev/null
```

### No ANSI test

```bash
tool capabilities --format json | perl -ne 'exit 1 if /\e\[/'
```

### Dry-run no-side-effect test

1. snapshot target state
2. run mutation with `--dry-run`
3. verify target state unchanged
4. parse plan output

### Error contract test

```bash
tool resource get --format json
# expect exit 2 and error.code == "invalid_arguments"
```

## JSONL writer

JSONL must write one complete event per line:

```python
def emit_event(event: dict) -> None:
    print(json.dumps(event, separators=(",", ":"), sort_keys=True), flush=True)
```

## Help JSON guidance

`--help-json` should include:
- command name
- description
- arguments
- flags
- defaults
- required flags
- enum values
- examples
- output schema reference
- error codes
- risk tier
- whether dry-run/confirm is required
