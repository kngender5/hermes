---
name: skill-auditor
description: Post-task audit skill — reviews completed tasks, evaluates results and workflow efficiency, identifies if a better skill should have been used, improves execution commands, and optimizes skill trigger patterns. Run after complex multi-step tasks to improve future performance.
---

# Skill Auditor — Post-Task Review & Optimization

Analyzes completed tasks to find inefficiencies, missed skill opportunities, and execution improvements.

## When to Run

- After completing a task with 3+ tool calls
- After any task that felt inefficient
- When a task failed or produced poor results
- Periodically (e.g., weekly) to audit recent sessions
- When the user asks "could that have been done better?"

## Audit Process

### Step 1: Reconstruct the Task

```python
audit = {
    "task": "What was the user asking for?",
    "goal": "What was the intended outcome?",
    "steps_taken": [],
    "tools_used": [],
    "skills_loaded": [],
    "result": "Was the goal achieved?",
    "time_estimate": "How many tool calls / minutes?",
}
```

### Step 2: Evaluate Against Available Skills

Cross-reference the task against `skills_list()`. Key questions:

| Question | If Yes → Action |
|----------|-----------------|
| Was there a skill that directly matched the task? | Note: should have loaded it first |
| Was there a partial-match skill that could have helped? | Note: could have combined skills |
| Did I use generic tools (terminal, browser) where a skill had optimized commands? | Note: skill commands would be faster |
| Did I repeat a workflow that should be a skill? | Recommend: create new skill |
| Did I miss a tool/technique the skill would have suggested? | Note: add to skill pitfalls |

### Step 3: Analyze Command Efficiency

For each tool call, evaluate:

```python
command_analysis = {
    "tool": "terminal / browser / execute_code / etc.",
    "command": "What was run",
    "could_skill_improve": True/False,
    "better_approach": "What the skill would have done",
    "tokens_used": "Estimated input/output tokens",
    "roundtrips": "How many back-and-forth calls?",
}
```

### Step 4: Check Trigger Pattern Gaps

Skills have `description` fields that act as triggers. Check:

| Trigger Gap | Example |
|-------------|---------|
| **Synonym mismatch** | User says "prosjektering" but skill triggers on "project planning" |
| **Too narrow trigger** | Skill only triggers on exact phrase, misses variations |
| **Missing trigger words** | Common user phrases not in description |
| **Wrong category** | Skill in "devops" but user asks in "productivity" context |
| **Overlapping triggers** | Two skills compete, wrong one loads |

## Audit Report Format

```
=== SKILL AUDIT REPORT ===

TASK: <what was asked>
RESULT: ✅ Success / ⚠️ Partial / ❌ Failed

── WORKFLOW ANALYSIS ──
Steps taken: <N>
Tool calls: <N>
Skills loaded: <list>
Redundant steps: <N>
Inefficient patterns: <list>

── MISSED SKILL OPPORTUNITIES ──
1. <skill-name>: <why it should have been used>
2. <skill-name>: <why it would have helped>

── COMMAND IMPROVEMENTS ──
1. Instead of: <command>
   Use: <skill-optimized command>
   Why: <reason>

── TRIGGER OPTIMIZATIONS ──
1. Skill: <name>
   Missing triggers: <words/phrases>
   Current description: <excerpt>
   Suggested improvement: <text>

── NEW SKILL RECOMMENDATIONS ──
1. <skill-name>: <what it should do>
   Trigger: <when to load it>
   Category: <where to put it>

── WORKFLOW REWRITE (optimal) ──
1. Load skill: <name>
2. <step using skill>
3. <step using skill>
...

Token savings estimate: <X% reduction>
Time savings estimate: <X fewer roundtrips>
```

## Common Anti-Patterns to Flag

### Anti-Pattern 1: "Reinventing the Wheel"
```
BAD:  10 terminal commands to set up a Docker container
GOOD: Load docker-management skill → skill provides proven commands
```

### Anti-Pattern 2: "Wrong Tool for the Job"
```
BAD:  Manually typing G-code line by line
GOOD: Load gcode-3d-printing skill → skill provides templates + macros
```

### Anti-Pattern 3: "Blind Execute"
```
BAD:  Running commands without checking if a skill has validated them
GOOD: Load relevant skill first → check pitfalls section → execute
```

### Anti-Pattern 4: "Session Amnesia"
```
BAD:  Solving the same problem differently each session
GOOD: Skill captures the correct approach → consistent execution
```

### Anti-Pattern 5: "Over-General Toolload"
```
BAD:  Loading all tools when task needs 2-3
GOOD: Infer toolset from task → tools parameter in cron/delegate
Token savings: ~60-80% reduction
```

### Anti-Pattern 7: "Cron Proliferation"
```
BAD:  6 cron jobs for staggered security checks (5/10/15/30min + hourly + daily)
GOOD: 3-4 jobs with unified scripts that combine related checks, filter noise, and alert only on real issues
```

**How to detect during audit:** Count cron jobs via `cronjob(action='list')`. If >5 jobs exist and ≥3 are in the same domain (security, monitoring, infrastructure) with staggered intervals, flag for consolidation.

**Fix:** Combine related checks into unified scripts with smart filtering. Use `deliver=origin` for daily/weekly summaries instead of `deliver=local` for every run. Reference: `security-monitor/references/cron-consolidation-pattern.md`

## Skill Trigger Optimization Guide

### How Skills Are Triggered

Skills match based on their `description` field in YAML frontmatter. The agent scans descriptions for relevance to the user's request.

### Trigger Quality Checklist

A good skill description triggers on:

- [ ] Core task type ("build PC", "configure Docker", "fine-tune LLM")
- [ ] Synonyms in both English and Norwegian (if applicable)
- [ ] Common misspellings and abbreviations
- [ ] Tool names the skill wraps ("G-code", "SSH", "API")
- [ ] Problem descriptions ("OVOM", "slow inference", "container won't start")
- [ ] Related services/tiers ("T4", "L4", "A100" for GPU tasks)

### Improving Trigger Coverage

**Before** (too narrow):
```
description: Manage Docker containers
```

**After** (broader):
```
description: Manage Docker containers, images, volumes, networks, and Compose stacks — lifecycle ops, debugging, cleanup, and Dockerfile optimization.
```

**Norwegian add** (if user is Norwegian):
```
description: "Manage Docker containers... Triggers: docker, containere, kjøre containere, docker compose, dockerfile, bygge image"
```

## Execution Flow Optimization

### Before (unoptimized):
```
User: "Set up Hermes Agent on Proxmox"
1. web_search("proxmox hermes agent install")     → 3 calls parsing results
2. terminal("apt install docker")                   → manual Docker setup
3. terminal("docker pull hermes-agent")            → wrong image name
4. web_search("hermes agent docker image correct")  → correction loop
5. terminal("docker pull nousresearch/hermes-agent") → correct
6. terminal("docker run ...")                       → missing Redis, compose
7. web_search("hermes agent docker compose")        → more searching
8. write_file("docker-compose.yml")                 → manual compose
```

**Total: 8 tool calls, high token usage, error-prone**

### After (optimized with skill):
```
User: "Set up Hermes Agent on Proxmox"
1. Load skill: proxmox-admin                        → references/hermes-agent-install.sh
2. terminal("bash <(curl ...hermes-agent-install.sh)") → one-shot install
3. Verify: pct exec <CTID> -- docker compose ps
```

**Total: 3 tool calls, minimal token usage, validated workflow**

## Scoring System

Score each completed task on efficiency:

| Metric | Score 1-5 | Criteria |
|--------|-----------|----------|
| **Skill Coverage** | 1-5 | Were all relevant skills loaded? |
| **Command Efficiency** | 1-5 | Minimal roundtrips? Optimal commands? |
| **Token Efficiency** | 1-5 | Minimal tool output in context? |
| **Error Rate** | 1-5 | No retry loops? No corrections needed? |
| **Result Quality** | 1-5 | Complete, correct, well-formatted? |

**Overall Score = average of 5 metrics**

| Score | Rating | Action |
|-------|--------|--------|
| 4.5-5.0 | ⭐ Excellent | Save workflow as reference |
| 3.5-4.4 | ✅ Good | Minor improvements noted |
| 2.5-3.4 | ⚠️ Fair | Update skill triggers or commands |
| 1.0-2.4 | ❌ Poor | Redesign approach, create new skill |

## Skill Improvement Actions

Based on audit findings, take ONE of these actions:

### Action 1: Patch Existing Skill
```
When: Skill exists but commands are outdated or incomplete
Action: skill_manage(action='patch', name=<skill>, old_string=..., new_string=...)
```

### Action 2: Create New Skill
```
When: Repeated workflow pattern discovered (5+ calls)
Action: skill_manage(action='create', name=<skill>, content=...)
```

### Action 3: Add Alternative Skill
```
When: Similar to existing skill but different domain
Action: skill_manage(action='create', name=<skill>, absorbed_into=<umbrella>)
```

### Action 4: Update Memory
```
When: Environment detail discovered (new tool, path, config)
Action: memory(action='add', target='memory', content=...)
```

### Action 5: Update User Profile
```
When: User preference or habit discovered
Action: memory(action='add', target='user', content=...)
```

## Quick Audit Template

For fast audits (after every 3+ call task), just check:

```
□ Did I load the most relevant skill?
□ Did I repeat any commands that a skill could have provided?
□ Did I use terminal where a skill had a script?
□ Did I search the web where a skill had the answer?
□ Could this task be done in fewer than N steps?
□ Should I save this workflow as a skill or memory?
```

If any box is unchecked → improvement opportunity exists.

## Automated Audit (Python)

```python
def audit_task(tool_calls, skills_available, user_request):
    """Quick audit of a completed task."""
    issues = []
    
    # Check: was a skill available but not loaded?
    for skill in skills_available:
        if skill_matches(skill, user_request) and skill not in loaded_skills:
            issues.append(f"Skill '{skill}' matched but was not loaded")
    
    # Check: redundant tool calls
    tools = [call['tool'] for call in tool_calls]
    if tools.count('terminal') > 3:
        issues.append(f"Excessive terminal calls ({tools.count('terminal')}) — consider execute_code script")
    
    # Check: web search where skill might have answer
    if 'web_search' in tools and any(s.startswith('configure') or s.startswith('install') for s in tools):
        issues.append("Web search used for config/install — check if skill has commands")
    
    # Check: repeated patterns
    commands = [call.get('command', '') for call in tool_calls]
    if len(commands) != len(set(commands)):
        issues.append("Repeated identical commands — could be looped")
    
    # Check: error handling
    errors = [call for call in tool_calls if call.get('error')]
    if len(errors) > 1:
        issues.append(f"{len(errors)} errors — workflow needs improvement")
    
    score = max(1, 5 - len(issues))
    
    return {
        "score": score,
        "issues": issues,
        "recommendations": [f"Fix: {i}" for i in issues],
    }
```
