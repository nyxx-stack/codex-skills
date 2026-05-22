---
name: thermo-nuclear-simplify-review
description: Run a Codex-native simplify review for explicit cleanup, maintainability, hardening, thermonuclear review, or code-quality audit requests.
---

# Thermo-Nuclear Simplify Review

Use this skill after implementation, before a commit or PR, or when the user asks to simplify, harden, clean up, or run a thermo-nuclear code-quality review.

The goal is not cosmetic cleanup. The goal is to find the smallest behavior-preserving structure that makes the change feel inevitable: fewer concepts, fewer branches, clearer ownership, stronger boundaries, and less incidental machinery.

## Codex Workflow

### Phase 1: Identify Changes

Run `git status --short` and `git --no-pager diff --color=never` to see what changed. If there are staged changes, also check `git --no-pager diff --cached --color=never`.

If there is no git diff, review the files the user mentioned or the files modified in the current session. Use `rg` to search for related helpers, patterns, and ownership boundaries. Preserve unrelated work.

### Phase 2: Launch Three Review Agents in Parallel

Use the subagent tool to launch all three review agents concurrently in one round. Pass each agent the full diff and enough file context to evaluate its pass.

Keep review agents read-only. They return findings only and must not edit files. If subagents are unavailable, run the same three passes locally and label the findings by pass.

### Phase 3: Synthesize Findings

Wait for all three agents to complete. Merge overlapping observations, discard low-confidence nits, and prioritize structural problems, missed simplifications, spaghetti growth, boundary/type issues, file-size growth, and efficiency/atomicity defects.

Prefer a few high-conviction findings over a long list.

### Phase 4: Review or Fix

If the user asked for review only, report findings first with file/line references and do not edit.

If the user asked to fix, apply behavior-preserving simplifications after synthesis, then verify. If a finding is a false positive or not worth addressing, note it and move on. Do not rewrite broad areas speculatively when the risk outweighs the simplification.

### Phase 5: Verify

Run the smallest meaningful formatter, typecheck, lint, or test command for the touched area. If verification is unavailable or too expensive, say exactly what was not run.

## Subagent Passes

Spawn all three in one round when possible:

### Pass A: Reuse and Canonicality

Mission: find duplicated logic, bespoke helpers, wrong-layer code, and missed canonical utilities.

Prompt shape:

```text
You are reviewing this change for reuse and canonicality only.

Look for:
- duplicated logic or near-duplicate helpers
- bespoke utilities where the repo already has a canonical helper
- feature logic leaking into shared/general modules
- code living in the wrong package, layer, service, route, component, or boundary
- wrappers or pass-through abstractions that do not earn their keep

Return only high-confidence findings with file/line evidence, why it matters, and the simplest behavior-preserving remedy.
Do not edit files.
```

### Pass B: Structural Thermo-Nuclear Maintainability

Mission: be ambitious about simplification. Find the code-judo move that deletes complexity instead of moving it around.

Prompt shape:

```text
You are running an unusually strict maintainability review.

Look for:
- a cleaner reframing that deletes branches, modes, helpers, layers, or state
- ad-hoc conditionals bolted onto busy flows
- one-off booleans, nullable modes, fallback paths, or special cases becoming permanent control-flow debt
- files pushed toward or past 1000 lines without a strong reason
- type-boundary drift: any/unknown/casts/optional fields hiding a clearer invariant
- magical generic handling where direct explicit code would be easier to reason about

Bias toward structural feedback over naming or style.
Return only high-conviction findings with file/line evidence, why the design regresses, and the smallest behavior-preserving simplification.
Do not edit files.
```

### Pass C: Efficiency, Orchestration, and Atomicity

Mission: find avoidable work and brittle orchestration where simpler structure also improves reliability.

Prompt shape:

```text
You are reviewing this change for efficiency, orchestration, and atomicity only.

Look for:
- independent work serialized for no reason
- repeated expensive computation, extra renders, redundant IO, or unnecessary network/database calls
- missed batching, pagination, field selection, or bounded-output controls
- partial updates that can leave state half-applied
- resource leaks, unbounded loops, polling, or log/result dumps
- retry/idempotency gaps around writes or external calls

Do not chase micro-optimizations.
Return only findings where the simpler structure is also clearer or safer, with file/line evidence and a concrete remedy.
Do not edit files.
```

## Thermo-Nuclear Standards

Apply these as the approval bar:

- Do not approve merely because behavior appears correct.
- Push for structural simplification when behavior can stay the same.
- Treat spaghetti growth as a design issue, not a style issue.
- Prefer direct, boring, maintainable code over hacky or magical code.
- Prefer deleting indirection over polishing indirection.
- Prefer explicit typed boundaries over casts, hidden optionality, and ad-hoc object shapes.
- Prefer canonical helpers and ownership boundaries over local one-offs.
- Prefer atomic, retry-safe, bounded workflows over partial or ambiguous execution.
- Treat a file crossing 1000 lines due to a change as a presumptive decomposition concern.

## Findings Format

For review-only output, lead with findings:

```text
- [P1] Structural issue title - path/to/file.ext:123
  Why this matters:
  Simplest remedy:
```

Severity guidance:

- `P0`: likely correctness, data-loss, security, or production-breaking risk.
- `P1`: structural regression, maintainability blocker, unsafe orchestration, or highly likely future bug.
- `P2`: meaningful simplification, boundary cleanup, reuse, or efficiency fix worth doing before merge.
- `P3`: optional cleanup. Avoid unless there are no larger findings.

If there are no findings, say that clearly and include any verification gaps.

## Fix Mode

When fixing:

- Keep edits scoped to high-confidence findings.
- Preserve public APIs and behavior unless the user explicitly asks to change them.
- Use existing local patterns before introducing new abstractions.
- Prefer extracting pure helpers, moving logic to the owning layer, deleting wrappers, collapsing duplicate branches, and making invariants explicit.
- Run verification after edits and report remaining risk.

Do not let the review become a broad rewrite. The right fix is the one that removes real complexity while keeping behavior obvious.
