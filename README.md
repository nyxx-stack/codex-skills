# cli-builder

An Agent Skill for building hyper-optimized, agent-native command-line interfaces.

This skill teaches an agent how to design, implement, review, and evaluate CLIs that other agents can use reliably: deterministic inputs, structured outputs, explicit risk boundaries, bounded context cost, safe retries, and auditable side effects.

## Install

```bash
npx skills add nyxx-stack/cli-builder
```

This fetches `SKILL.md` plus the bundled `references/`, `assets/`, `scripts/`, and `evals/` directories into your agent's skills folder (`.claude/skills/` or `.agents/skills/`).

## When to use

Activate this skill when creating or refactoring:

- CLIs and command wrappers
- Developer, deployment, or data tools
- API CLIs and batch processors
- Local utilities intended primarily for AI agents rather than humans

## What's inside

| File | Purpose |
|---|---|
| `SKILL.md` | Five-phase workflow: research → contract → implementation → review → evals |
| `references/agent-cli-best-practices.md` | Full contract for inputs, outputs, errors, safety, tokens, introspection |
| `references/architecture-patterns.md` | Command archetypes, plan/execute, long-running jobs, batch, API wrappers |
| `references/implementation-guides.md` | Minimal Python/TypeScript/Rust templates and test patterns |
| `references/evaluation.md` | Eval design, assertions, grading, iteration loop |
| `assets/*.schema.json` | JSON Schemas for success envelope, error envelope, capabilities |
| `assets/agent_help_template.md` | Template for `--help` and `help <command>` output |
| `scripts/validate_agent_cli.py` | Heuristic validator for agent-readiness (Python 3.10+) |
| `evals/evals.json` | Core agent evals for the skill |

## Validator

Run a quick readiness check against any CLI:

```bash
python3 scripts/validate_agent_cli.py -- <your-cli>
```

The validator checks `--help` non-blocking exit, absence of ANSI escapes by default, non-interactive base command, presence of machine-readable discovery (`--help-json`, `capabilities`, or `schema`), and parseable JSON when `--format json` is supported.

## License

Apache 2.0. See [LICENSE](LICENSE).
