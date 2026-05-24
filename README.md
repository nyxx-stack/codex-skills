# codex-skills

A Codex skill repository for agent-native engineering workflows.

The `cli-builder` skill teaches an agent how to design, implement, review, and evaluate CLIs that other agents can use reliably: deterministic inputs, structured outputs, explicit risk boundaries, bounded context cost, safe retries, and auditable side effects.

Skills live under `skills/`.

## Install

Install the `cli-builder` skill with the open `skills` CLI:

```bash
npx skills add nyxx-stack/codex-skills --skill cli-builder
```

Install the strict Codex review skill:

```bash
npx skills add nyxx-stack/codex-skills --skill thermo-nuclear-simplify-review
```

Install the GPT bridge skill:

```bash
npx skills add nyxx-stack/codex-skills --skill gpt-pro-bridge
```

Add `-a codex` or `-a claude-code` to target a specific agent, and `-g` for a global install. The installer chooses the target skill directory for the selected agent and scope, such as Codex's `~/.codex/skills/` for global installs.

You can also copy any folder from `skills/<skill-name>/` directly into your agent's skills directory.

## Skills

| Skill | Path | Purpose |
|---|---|---|
| `cli-builder` | `skills/cli-builder/SKILL.md` | Build hyper-optimized, agent-native CLIs and command wrappers |
| `thermo-nuclear-simplify-review` | `skills/thermo-nuclear-simplify-review/SKILL.md` | Run a Codex-native multi-agent simplify review with strict maintainability standards |
| `gpt-pro-bridge` | `skills/gpt-pro-bridge/SKILL.md` | Package any git repo and generate a structured GPT 5.4 Pro prompt for external codebase analysis |

## When to use `cli-builder`

Activate this skill when creating or refactoring:

- CLIs and command wrappers
- Developer, deployment, or data tools
- API CLIs and batch processors
- Local utilities intended primarily for AI agents rather than humans

## What's inside `cli-builder`

| File | Purpose |
|---|---|
| `skills/cli-builder/SKILL.md` | Five-phase workflow: research -> contract -> implementation -> review -> evals |
| `skills/cli-builder/references/agent-cli-best-practices.md` | Full contract for inputs, outputs, errors, safety, tokens, introspection |
| `skills/cli-builder/references/architecture-patterns.md` | Command archetypes, plan/execute, long-running jobs, batch, API wrappers |
| `skills/cli-builder/references/implementation-guides.md` | Minimal Python/TypeScript/Rust templates and test patterns |
| `skills/cli-builder/references/evaluation.md` | Eval design, assertions, grading, iteration loop |
| `skills/cli-builder/assets/*.schema.json` | JSON Schemas for success envelope, error envelope, capabilities |
| `skills/cli-builder/assets/agent_help_template.md` | Template for `--help` and `help <command>` output |
| `skills/cli-builder/scripts/validate_agent_cli.py` | Heuristic validator for agent-readiness (Python 3.10+) |
| `skills/cli-builder/evals/evals.json` | Core agent evals for the skill |

## Validator

Run a quick readiness check against any CLI:

```bash
python3 skills/cli-builder/scripts/validate_agent_cli.py -- <your-cli>
```

The validator checks `--help` non-blocking exit, absence of ANSI escapes by default, non-interactive base command, presence of machine-readable discovery (`--help-json`, `capabilities`, or `schema`), and parseable JSON when `--format json` is supported.

## License

Apache 2.0. See [LICENSE](LICENSE).
