---
name: recreate-anything
description: Orchestrate authorized pixel-only web and Android recreation benchmarks with isolated exploration, reproduction, evaluation, and PR-based delivery.
---

# Recreate Anything

Use for benchmark runs and the planned Meestakes Recreate dashboard (recreate.meestakes.app). This skill is an operating procedure, not a new runtime or a grant of tool permissions.

## Upstream
- https://github.com/recreate-anything/recreate-anything/tree/linux
- https://github.com/recreate-anything/recreate-anything/blob/linux/docs/api_contract.md
- https://github.com/recreate-anything/recreate-anything/blob/linux/docs/running_agent.md
- https://github.com/recreate-anything/recreate-anything/blob/linux/docs/security_model.md

Pin the upstream commit for each run. Read the API contract and available agent adapters at that revision before wiring tools. Do not assume Hermes is a supported launcher or that an Android local model supports vision or structured calls.

## Operator and explorer isolation
The operator may manage an explicitly authorized target, controller, sandbox, builds, metrics and PRs. The explorer must be a separate least-privilege process with only the session's /agent/{sid}/ channel. Never expose operator credentials, shell, GitHub, ADB, accessibility, DOM, URLs, source, storage, target network or logs to the explorer. Use controller-enforced isolation and synthetic test accounts; prompts alone are insufficient. Use authorized targets only; do not reproduce credentials, personal data or impersonation flows.

## Skill: visual exploration and topology
1. Operator creates a session and chooses platform and managed or nograph condition, budget and model.
2. Explorer observes the PNG; derive coordinates from actual image dimensions. Use the action schema in the pinned contract. Observe after each action; accepted input is not evidence of success.
3. Enumerate states, transitions, forms, empty/error states and persistence using safe synthetic inputs. Avoid repeated no-op actions. Track remaining time, actions and observations.
4. Managed mode only: record state, feature, data, edge and hypothesis incrementally with real step/frame evidence; resolve or revise uncertain findings. Nograph must not expose the seven discovery tools.
5. Finalize on budget exhaustion or when evidence is adequate. Label unknowns rather than fabricating them.

## Skill: clean-room reproduction
Use only permitted finalized topology, filtered traces and fictional materials in the isolated reproduction workspace. No access to the original target implementation. Build the runnable static web app or Kotlin/Compose APK as appropriate; implement state transitions and persistence. Keep build credentials outside agent context. Use independent pixel-only self-review; stop at configured budget/revision caps.

## Skill: evaluation and reporting
Use an independent judge and the upstream checklist and metric scripts. Preserve evaluation report, action trace, session summary, review summary, model identity, pinned commit, platform and condition. Distinguish pending, failed and measured runs; never invent scores. Expose only sanitized artifacts on the authenticated dashboard.

## Skill: Meestakes operator workflow
Dashboard needs run creation, budgets, model/runtime selection, statuses, traces, topology (managed only), build artifacts, metrics, and links to PRs. Keep the controller off the public internet; use an authenticated server-side operator gateway with scoped authorization and audit logs. A static frontend alone must not claim to run benchmarks. Do not expose APKs or private screenshots without authorization. Prefer a Linux Docker/emulator host; native Termux/proot may act as operator client after testing. Do not grant ADB/root to the explorer.

## Skill: GitHub and review handoff
Use topic branches and draft PRs for every change; include scope, tests, evidence and blockers. Do not merge or deploy production from a skill invocation without separate explicit authorization. For coding-agent handoff, include a PR link and branch, acceptance tests, and the boundaries above. Jules is read-only after November 11, 2026 per https://jules.google/docs/changelog/ ; do not claim a new session was submitted. Use a separately connected replacement coding agent if authorized.

## Acceptance checks
- A harmless sample app can be explored with valid screenshots and coordinate actions.
- Explorer cannot invoke shell, DOM, ADB, target network or operator endpoints; nograph has no discovery tools.
- Invalid evidence references are rejected and actual confirmed findings reference current-session frames.
- Budget exhaustion terminates exploration cleanly and allows finalization per upstream contract.
- Reproduction builds, independent judge emits a valid report, and dashboard shows actual artifacts with provenance.
- Check skill frontmatter, adapter schemas and least-privilege configuration; report each as pass, fail or not run.
