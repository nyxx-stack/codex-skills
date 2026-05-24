---
name: gpt-pro-bridge
description: Package the repo and generate an optimized prompt for GPT 5.5 Pro (web) to analyze the codebase — for audits, debugging, refactors, architecture reviews, or any analysis task. GPT's output is constrained to produce a structured Claude Code execution prompt that can be pasted back and run locally. Use this when the user explicitly mentions GPT, ChatGPT, or GPT 5.5 Pro, says things like "ask GPT", "bridge to GPT", "GPT review", or wants to upload the repo to ChatGPT for analysis. Do NOT trigger for "second opinion" or "external review" requests that don't mention GPT specifically — those likely want a Codex or code-review workflow instead.
metadata:
  version: "1.0.0"
---

# GPT Pro Bridge

Package the codebase and generate a prompt for GPT 5.5 Pro's web interface. GPT analyzes the code and outputs a structured execution plan formatted as a Claude Code prompt that can be run locally.

## Why this exists

GPT 5.5 Pro is only available through the ChatGPT web interface — it can read uploaded files but can't modify local code. This skill bridges that gap: GPT does the analysis, Claude Code does the execution.

## Workflow

### 1. Package the repo (ALWAYS run this first)

**MANDATORY first step — run this before anything else, every time:**

The packaging script ships with this skill. Check the skill context header ("Base directory for this skill: ...") to find it, or use one of the standard install paths:

- Claude Code global: `~/.claude/skills/gpt-pro-bridge/scripts/package-repo.sh`
- Codex global: `~/.codex/skills/gpt-pro-bridge/scripts/package-repo.sh`
- Project-local: `.claude/skills/gpt-pro-bridge/scripts/package-repo.sh` (relative to repo root)

Run whichever path exists. From anywhere inside the target git repo:

```bash
bash ~/.claude/skills/gpt-pro-bridge/scripts/package-repo.sh
```

This produces a fresh zip at `~/Downloads/gpt-pro-bridge/`. Do not skip this step even if a zip already exists — it will be stale.

- Uses `git archive` — only tracked files, no node_modules/dist/build artifacts
- Always zips the entire repo — GPT needs full codebase context even when analysis is focused on one area
- Accepts `--scope path/to/subdir` to zip only a subdirectory when the repo is large

### 2. Generate the GPT prompt

Build a prompt with three parts:

**Part A — Project briefing** (always include):
- Stack, package manager, key dependencies (read from `package.json`, `pyproject.toml`, `go.mod`, etc.)
- Directory structure: **first level only**. Exclude lock files, build artifacts, migration directories, test fixtures. The zip already contains the full tree — GPT can explore deeper. A compact tree keeps the prompt short.
- Build/test commands
- Key constraints or patterns from `CLAUDE.md` or `AGENTS.md` if present

**Part B — The goal** (one of the modes below, or custom):
- **audit** — Security, code quality, or complexity audit
- **debug** — Diagnose a specific bug or failure
- **refactor** — Identify refactoring opportunities
- **review** — Code review of recent changes
- **architecture** — Architecture review and improvement suggestions
- **custom** — User-defined analysis goal

**Part B.5 — Documentation verification directive** (always include):

GPT has web browsing — use it. Before making any code recommendations, GPT must look up the current documentation for the libraries and frameworks involved. Training data goes stale; the only way to avoid recommending deprecated APIs, removed methods, or old patterns is to check the actual docs.

Include this verbatim in every prompt:

```
## Documentation Requirement — CRITICAL

Before recommending ANY code changes, you MUST:

1. **Check `package.json` / lock files** in the uploaded zip to identify the EXACT versions of all relevant dependencies
2. **Search the official documentation** for each library/framework you're about to reference. Use your web browsing to pull up the current docs — do NOT rely on your training data for API specifics
3. **Verify every API, method, hook, config option, and pattern** you recommend actually exists in the version the project uses. If the project is on an older version, recommend the API for THAT version, not the latest
4. **Flag version mismatches**: If you notice a dependency is significantly outdated and your recommendation depends on a newer version, call this out explicitly and provide both the current-version approach and the upgrade path

This matters because outdated recommendations waste hours of debugging. When in doubt, open the docs page and verify.
```

**Part C — Output format constraint** (critical — always include):

This is the most important part. GPT must output a well-structured markdown document that serves as agent instructions — not just analysis prose. Include this verbatim (adapted for the goal):

```
## Output Format — IMPORTANT

You are analyzing this codebase to produce an EXECUTION PLAN, not just observations.

Your entire response must be a single, well-structured **markdown document** that I will save as a `.md` file and give to an AI coding agent (Claude Code) with full file read/write access to this repo.

Write the document as direct instructions to the agent — imperative voice, no fluff. The agent will read this markdown file and execute every instruction in it.

Structure your markdown output EXACTLY like this:

# [Goal]: [Short title]

## Task
[1-2 sentence summary of what needs to be done]

## Context
[Key findings from your analysis that the executing agent needs to know — be specific with file paths, line numbers, function names. This is the "briefing" so the agent understands the codebase state before making changes.]

## Instructions

### [Group 1: descriptive name]

**`path/to/file.ts`**
- [ ] [Specific change with enough detail to implement without ambiguity]
- [ ] [Another change]

**`path/to/other.ts`**
- [ ] [Change description]

### [Group 2: descriptive name]
...

## Verification
- [ ] [How to verify the changes work — test commands, manual checks, expected behavior]

## Warnings
[Anything the executing agent should be careful about — breaking changes, migration needs, env vars, etc.]

Rules for your output:
1. Write in markdown — the output will be saved directly as a .md file
2. Every file path must be relative to the repo root and accurate
3. Every instruction must be specific enough to implement without seeing surrounding code context
4. Group instructions logically (by feature, by file area, by priority)
5. Include the reasoning for WHY each change matters — the executing agent makes better decisions with context
6. If you find nothing actionable, say so explicitly rather than inventing busywork
7. Do NOT include code blocks with full file rewrites — describe the changes precisely instead
8. For bug fixes: include the root cause analysis and the specific fix
9. For refactors: explain the before/after pattern so the agent understands the transformation
10. For every library/API you reference, note the version you verified against (e.g., "Next.js 16.x docs" or "Prisma 6.x docs"). If you did NOT verify, say so — never silently guess at APIs
```

### 3. Save the prompt and present to user

Save the generated prompt as a markdown file at `.gpt-pro-bridge/<mode>-<short-description>-<YYYYMMDD>.md` in the repo root. Auto-create the directory if it doesn't exist (`mkdir -p .gpt-pro-bridge`). This keeps prompts alongside the code they describe — version-controllable, shareable, and reusable.

```
.gpt-pro-bridge/<mode>-<short-description>-<YYYYMMDD>.md
```

Examples:
- `.gpt-pro-bridge/audit-security-workers-20260310.md`
- `.gpt-pro-bridge/debug-ws-reconnect-20260310.md`
- `.gpt-pro-bridge/refactor-copy-execution-20260310.md`

The prompt file is a reusable record: the user can re-run it against a future version of the codebase, share it with teammates, or tweak it for a follow-up. Add `.gpt-pro-bridge/` to `.gitignore` if prompts should stay local-only.

After saving:

1. Tell the user where the zip (`~/Downloads/gpt-pro-bridge/`) and prompt (`.gpt-pro-bridge/`) files are
2. Copy the full prompt to clipboard via `pbcopy` (macOS) or `xclip -sel clip` (Linux)
3. Give them clear instructions:
   - Upload the zip to ChatGPT (GPT 5.5 Pro)
   - Paste the prompt (already on clipboard)
   - Copy GPT's response
   - Paste it back into Claude Code to execute

## Prompt templates by mode

### Audit mode

```
I'm uploading a zip of my codebase for a [security/quality/complexity] audit.

[Project briefing...]

## Your task
Audit this codebase for [specific audit focus]. Look at:
- [specific areas of concern]
- [patterns to check for]
- [anything the user mentioned]

Focus on issues that are ACTIONABLE — not style preferences or theoretical concerns. Prioritize by severity: critical > high > medium. Ignore low/informational unless they indicate a pattern.

[Output format constraint from above]
```

### Debug mode

```
I'm uploading a zip of my codebase. I need help diagnosing a bug.

[Project briefing...]

## The problem
[Bug description, error messages, reproduction steps, what was tried]

## Relevant files
[Point GPT to the most relevant files/directories]

## Your task
Trace the root cause of this bug. Start from the error/symptom and work backwards through the code. Identify the exact failure point and produce a fix.

[Output format constraint from above]
```

### Refactor mode

```
I'm uploading a zip of my codebase for refactoring analysis.

[Project briefing...]

## Your task
Analyze [specific area or the whole codebase] for refactoring opportunities. Focus on:
- Code duplication that should be extracted
- Complex functions that should be broken down
- Abstractions that are at the wrong level
- Patterns that are inconsistent across the codebase

Only suggest refactors that improve maintainability without changing behavior. Each suggestion must be specific and implementable.

[Output format constraint from above]
```

### Architecture review mode

```
I'm uploading a zip of my codebase for an architecture review.

[Project briefing...]

## Your task
Review the overall architecture. Evaluate:
- Package boundaries and dependency flow
- Separation of concerns
- Error handling patterns
- Data flow and state management
- Scalability considerations

[Output format constraint from above]
```

## Tips for better results

- **Be specific about the goal**: "Audit the workers package for race conditions in BullMQ job handlers" beats "audit the code".
- **Include error context**: For debug mode, paste exact error messages and stack traces into the prompt.
- **Mention what you've tried**: GPT wastes less time on dead ends if you tell it what didn't work.
- **Iterate**: If GPT's first pass misses the mark, refine the prompt rather than starting over. The zip stays the same.
- **Use `--scope`**: For large repos, pass `--scope path/to/subdir` to the packaging script to keep the zip small and focused.
