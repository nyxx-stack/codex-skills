#!/usr/bin/env python3
"""Heuristic validator for agent-native CLI readiness.

Usage:
  python3 scripts/validate_agent_cli.py -- <cli> [default args...]

Examples:
  python3 scripts/validate_agent_cli.py -- mytool
  python3 scripts/validate_agent_cli.py -- python3 -m mytool
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from typing import List, Optional

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    exit_code: Optional[int] = None
    duration_ms: Optional[int] = None

def run_cmd(cmd: List[str], timeout: float = 5.0, stdin: bytes = b"") -> tuple[int, str, str, int, bool]:
    start = time.time()
    try:
        p = subprocess.run(
            cmd,
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env={**os.environ, "NO_COLOR": "1", "CLICOLOR": "0"},
        )
        dur = int((time.time() - start) * 1000)
        return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), dur, False
    except subprocess.TimeoutExpired as e:
        dur = int((time.time() - start) * 1000)
        out = (e.stdout or b"").decode("utf-8", "replace")
        err = (e.stderr or b"").decode("utf-8", "replace")
        return 124, out, err, dur, True

def parses_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except Exception:
        return False

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate basic agent CLI readiness.")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--json", action="store_true", help="Only emit JSON summary.")
    parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Command after --")
    args = parser.parse_args(argv)

    cmd = args.cmd
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        print("Error: provide a command after --", file=sys.stderr)
        return 2

    checks: List[Check] = []

    # 1. --help should exit and not hang.
    rc, out, err, dur, timed_out = run_cmd(cmd + ["--help"], timeout=args.timeout)
    checks.append(Check(
        name="help_exits",
        ok=(not timed_out and rc in (0, 2)),  # Some CLIs use 2 for help via argparse misuse; flag as weak but not fatal.
        detail="--help returned without timeout" if not timed_out else "--help timed out; possible prompt or blocked execution",
        exit_code=rc,
        duration_ms=dur,
    ))

    combined = out + err
    checks.append(Check(
        name="help_has_usage",
        ok=("usage" in combined.lower() or "options" in combined.lower() or "commands" in combined.lower()),
        detail="help output includes usage/options/commands" if combined else "no help output captured",
        exit_code=rc,
        duration_ms=dur,
    ))

    checks.append(Check(
        name="help_no_ansi",
        ok=(ANSI_RE.search(combined) is None),
        detail="no ANSI escape sequences in help output" if ANSI_RE.search(combined) is None else "ANSI escape sequences found",
        exit_code=rc,
        duration_ms=dur,
    ))

    # 2. Check non-interactivity with no stdin for base command.
    rc, out, err, dur, timed_out = run_cmd(cmd, timeout=args.timeout, stdin=b"")
    checks.append(Check(
        name="base_no_prompt_timeout",
        ok=not timed_out,
        detail="base command returned without timeout" if not timed_out else "base command timed out; may be waiting for interactive input",
        exit_code=rc,
        duration_ms=dur,
    ))

    # 3. Try discovery commands.
    discovery_attempts = [
        cmd + ["--help-json"],
        cmd + ["capabilities", "--format", "json"],
        cmd + ["schema", "--format", "json"],
    ]
    discovery_ok = False
    discovery_details = []
    for attempt in discovery_attempts:
        rc, out, err, dur, timed_out = run_cmd(attempt, timeout=args.timeout)
        label = " ".join(attempt[len(cmd):]) or "(base)"
        if not timed_out and rc == 0 and parses_json(out.strip()):
            discovery_ok = True
            discovery_details.append(f"{label}: JSON discovery OK")
            break
        discovery_details.append(f"{label}: rc={rc}, timeout={timed_out}, json={parses_json(out.strip())}")
    checks.append(Check(
        name="machine_readable_discovery",
        ok=discovery_ok,
        detail="; ".join(discovery_details),
    ))

    # 4. Try explicit JSON on base command if it exits successfully.
    rc, out, err, dur, timed_out = run_cmd(cmd + ["--format", "json"], timeout=args.timeout)
    json_base = (not timed_out and rc == 0 and parses_json(out.strip()))
    checks.append(Check(
        name="format_json_parseable_when_supported",
        ok=json_base or rc != 0,
        detail="--format json produced parseable JSON" if json_base else f"--format json rc={rc}; acceptable only if unsupported or command requires subcommand",
        exit_code=rc,
        duration_ms=dur,
    ))

    passed = sum(1 for c in checks if c.ok)
    failed = len(checks) - passed
    result = {
        "schema_version": "1.0",
        "ok": failed == 0,
        "summary": {"passed": passed, "failed": failed},
        "checks": [asdict(c) for c in checks],
        "next_actions": [
            "Add --help-json or capabilities if machine_readable_discovery failed.",
            "Ensure agent mode never prompts and always supports structured output.",
            "Keep stdout parseable and diagnostics on stderr.",
        ] if failed else [],
    }

    print(json.dumps(result, indent=None if args.json else 2, sort_keys=True))
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
