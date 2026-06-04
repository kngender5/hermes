---
name: project-scaffolding
description: >
  Set up organized project workspaces with Hermes profiles, AGENTS.md, SOUL.md,
  skill assignments, and cron schedules. Use when starting a new project,
  reorganizing existing workspaces, creating project-specific personas, or
  consolidating scattered sessions/tools into a coherent project structure.
  Triggers: new project, organize projects, create profile, set up workspace,
  project structure, reorganize, oppsett, prosjekt.
---

# Project Scaffolding — Workspace, Profiles & Personas

Create organized project workspaces that give each project its own identity, skills, and automation.

## When to Use

- Starting a new project area (infra, academic study, creative work, gaming)
- Reorganizing scattered files/sessions into coherent project folders
- Creating Hermes profiles with fitting personas
- Consolidating cron jobs and scripts per project
- Setting up AGENTS.md + SOUL.md per project

## Core Concept

```
~/projects/<project-name>/
    AGENTS.md          ← project-specific rules, skill priorities, constraints
    SOUL.md            ← persona definition (if different from profile)
    README.md          ← project overview

~/.hermes/profiles/<profile-name>/
    config.yaml        ← model, provider, context_length
    SOUL.md            ← profile persona (overrides default SOUL.md)
    skills/            ← skill symlinks or copies for this profile
    cron/              ← cron job definitions
    memories/          ← profile-specific memory entries
```

## Steps

### 1. Define the Project Domain

Ask (or infer from existing files):
- What is the project's purpose?
- What tools/APIs does it use?
- What's the user's communication style in this context?
- What are the key constraints/safety rules?

### 2. Create the Profile

```bash
mkdir -p ~/.hermes/profiles/<name>/{skills,plugins,cron,memories}
```

Write `config.yaml` (model, provider, context_length). Write `SOUL.md` with:
- **Identity**: Who is the agent in this context?
- **Expertise**: What domains does it cover?
- **Communication**: Tone, language, format preferences
- **Methodology**: How does it approach problems?
- **Projects**: What project folders belong to this profile?

### 3. Create the Project Folder

```bash
mkdir -p ~/projects/<project-name>/{docs,scripts,logs,config}
```

Write `AGENTS.md` with:
- Project purpose
- Active profiles for this project
- Skill priority order (most-used first)
- Working directory and key files
- Constraints and safety rules

### 4. Assign Skills

Either symlink relevant skills into the profile's `skills/` dir, or list priority skills in AGENTS.md. Not every skill needs to be in the profile — the `skills_list()` scan covers all skills. Profile skills are for *specialization*.

### 5. Set Up Cron Jobs

- Consolidate related periodic checks into unified scripts (see `security-monitor/references/cron-consolidation-pattern.md`)
- Use `deliver=origin` for daily/weekly summaries (arrives in chat)
- Use `deliver=local` for frequent checks that should stay silent unless alarming
- Set `enabled_toolsets` to reduce token overhead per job

### 6. Create the Project Index

Maintain `~/projects/PROJECTS.md` as a master index:

```
| Project | Path | Profile | Status | Description |
```

## SOUL.md Card Template

```markdown
# SOUL.md — <Persona Name>

## Kjerneidentitet
[Who is the agent in this context? One sentence.]

## Ekspertise
- **Domain 1:** details
- **Domain 2:** details

## Kommunikasjon
- [Tone, language, verbosity preferences]

## Arbeidsmetode
1. [Step 1]
2. [Step 2]

## Prosjekter
- `~/projects/<name>/` — description
```

## AGENTS.md Card Template

```markdown
# AGENTS.md — <Project Name>

## Formål
[One sentence]

## Aktive profiler
- **profile-name** — what it's used for here

## Skill-prioriteter
1. `skill-name` — why it's #1

## Arbeidsmappen
- `~/projects/<name>/`

## Constraints
- [Safety rule 1]
- [Safety rule 2]
```

## Safety Rules Per Project Type

### Infrastructure (infra)
- Never destroy VMs/LXC without snapshot first
- Always validate config before apply
- Log all changes to structured JSONL
- Dry-run before countermeasures auto
- Maintain rollback capability

### Academic (academic)
- Show all calculation steps
- Use LaTeX for equations, markdown for units
- IEEE citation style `[#]`
- Norwegian technical terms
- Verify against official sources

### Creative (creative)
- Prototype first, optimize later
- Document what works
- Don't restart game servers without permission
- Visual output preferred (images, diagrams)

## Checklist

- [ ] Profile created with SOUL.md + config.yaml
- [ ] Project folder created with AGENTS.md
- [ ] Skill priorities documented
- [ ] Cron jobs consolidated (not proliferated)
- [ ] Safety constraints written
- [ ] PROJECTS.md updated
- [ ] Team notified (if applicable)
