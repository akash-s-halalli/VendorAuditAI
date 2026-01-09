# Autonomous Development Agent (BMAD + Ralph Loop)

## Purpose
An AI agent that runs autonomously while you're away, following BMAD methodology with Ralph Loop for continuous development. No human approval needed - the agent self-approves, commits, and pushes.

---

## Core Concept: "Walk Away Development"

```
YOU: "Start EPIC-004"
YOU: *walks away*
AGENT: *works for hours*
YOU: *comes back*
RESULT: EPIC-004 complete, pushed to GitHub, ready for review
```

---

## Architecture

### 1. BMAD Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    BMAD + RALPH LOOP                         │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │   PLAN   │───►│  BUILD   │───►│  VERIFY  │              │
│  │  (Read   │    │  (Code   │    │  (Check  │              │
│  │  Stories)│    │  Changes)│    │  Quality)│              │
│  └──────────┘    └──────────┘    └────┬─────┘              │
│                                       │                     │
│                    ┌──────────────────┴───────┐            │
│                    │                          │            │
│                    ▼                          ▼            │
│              ┌──────────┐              ┌──────────┐        │
│              │  PASS    │              │  FAIL    │        │
│              │  Commit  │              │  Fix &   │        │
│              │  & Push  │              │  Retry   │        │
│              └──────────┘              └──────────┘        │
│                    │                          │            │
│                    ▼                          │            │
│              Next Story ◄─────────────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Auto-Approval System

The agent auto-approves when ALL conditions are met:

| Check | Description | Auto-Approve |
|-------|-------------|--------------|
| Imports | All imports resolve | Yes |
| Syntax | No Python syntax errors | Yes |
| Patterns | Follows existing code style | Yes |
| Security | No secrets/credentials in code | Yes |
| Scope | Changes within current Story | Yes |
| Tests | Tests pass (if exist) | Yes |

**Manual Approval Required For:**
- Database schema changes
- Security-critical code
- Breaking API changes
- Changes outside current EPIC

### 3. Self-Commit Rules

```python
# Agent commits when:
if story_acceptance_criteria_met():
    if quality_gates_pass():
        git_commit(f"FEAT: {story.title}")
        if epic_complete():
            git_push()
            update_story_status("COMPLETED")
```

---

## Configuration

### .claude/settings.json (Auto-Approve Settings)
```json
{
  "autonomous_mode": true,
  "auto_approve": {
    "read_files": true,
    "write_files": true,
    "edit_files": true,
    "bash_safe_commands": true,
    "git_commit": true,
    "git_push": true
  },
  "require_approval": {
    "delete_files": false,
    "bash_dangerous": true,
    "git_force_push": true,
    "schema_changes": true
  },
  "ralph_loop": {
    "max_iterations": 100,
    "max_time_hours": 8,
    "commit_after_story": true,
    "push_after_epic": true
  }
}
```

### Hooks Configuration

Create `.claude/hooks/` for automation:

```bash
# .claude/hooks/pre-commit
#!/bin/bash
# Auto quality checks before commit
python -m py_compile backend/app/**/*.py
exit $?
```

```bash
# .claude/hooks/post-story
#!/bin/bash
# After each story completion
git add -A
git commit -m "$1"
echo "Story committed: $1"
```

```bash
# .claude/hooks/post-epic
#!/bin/bash
# After EPIC completion - auto push
git push origin master
echo "EPIC pushed to GitHub"
```

---

## Workflow: Starting Autonomous Session

### Option 1: Full EPIC
```bash
# Start and walk away
claude "Execute EPIC-004 autonomously. Auto-approve all changes.
Commit after each story. Push when complete.
I will be away - do not wait for my approval."
```

### Option 2: Specific Stories
```bash
claude "Complete STORY-018 through STORY-021 autonomously.
Follow BMAD methodology. Self-approve all quality-passing changes.
Commit and push when done."
```

### Option 3: Time-Boxed
```bash
claude "Work on VendorAuditAI for 4 hours autonomously.
Complete as many stories as possible.
Commit progress every 30 minutes.
Push at end of session."
```

---

## Safety Mechanisms

### 1. Iteration Limits
- Max 100 iterations per session
- Max 8 hours runtime
- Pause after 3 consecutive failures

### 2. Scope Boundaries
- Only modify files in current project
- Only work on specified EPIC/Stories
- No changes to .env or credentials

### 3. Checkpoint Commits
- Commit working code every 30 minutes
- Never lose more than 30 min of work
- Can resume from any checkpoint

### 4. Rollback Ready
- All commits are atomic
- Branch before risky changes
- Can revert any commit

---

## Progress Tracking (While You're Away)

### Status File: `.claude/autonomous-status.json`
```json
{
  "session_id": "abc123",
  "started_at": "2025-01-09T10:00:00Z",
  "current_epic": "EPIC-004",
  "current_story": "STORY-019",
  "stories_completed": ["STORY-018"],
  "commits_made": 3,
  "last_commit": "abc1234",
  "iterations": 45,
  "status": "running",
  "errors": []
}
```

### View Progress Remotely
```bash
# Check status from phone/another device
gh api repos/MikeDominic92/VendorAuditAI/commits
```

---

## Integration Commands

### Start Autonomous Mode
```
/autonomous epic-004
```

### Check Progress
```
/status
```

### Stop Gracefully
```
/stop
```

### Resume After Interruption
```
/resume
```

---

## Example Session

```
[10:00] YOU: /autonomous epic-004
[10:00] AGENT: Starting autonomous development for EPIC-004
[10:00] AGENT: Loading STORY-018: Query Service
[10:00] YOU: *leaves computer*

[10:15] AGENT: Created backend/app/services/query.py
[10:20] AGENT: Quality check PASSED
[10:20] AGENT: Committed: "FEAT: Add query service for NL questions"

[10:25] AGENT: Loading STORY-019: Query Schemas
[10:35] AGENT: Created backend/app/schemas/query.py
[10:36] AGENT: Updated schemas/__init__.py
[10:37] AGENT: Quality check PASSED
[10:37] AGENT: Committed: "FEAT: Add query schemas"

[10:45] AGENT: Loading STORY-020: Query API Endpoints
[11:00] AGENT: Created backend/app/api/v1/endpoints/query.py
[11:01] AGENT: Updated router.py
[11:02] AGENT: Quality check PASSED
[11:02] AGENT: Committed: "FEAT: Add query API endpoints"

[11:10] AGENT: Loading STORY-021: Query Model
[11:25] AGENT: Created backend/app/models/query.py
[11:26] AGENT: Updated models/__init__.py
[11:27] AGENT: Quality check PASSED
[11:27] AGENT: Committed: "FEAT: Add query history model"

[11:30] AGENT: EPIC-004 COMPLETE
[11:30] AGENT: Pushing to GitHub...
[11:31] AGENT: Updated story status to COMPLETED
[11:31] AGENT: Session complete. 4 commits, 0 errors.

[12:00] YOU: *returns*
[12:00] YOU: /status
[12:00] AGENT: EPIC-004 complete. 4 stories done.
              All changes pushed to GitHub.
              View: https://github.com/MikeDominic92/VendorAuditAI
```

---

## Quick Start

To enable autonomous mode for this project:

1. Set auto-approve in Claude Code settings
2. Run: `/autonomous epic-004`
3. Walk away
4. Come back to completed work

The agent will:
- Follow BMAD story structure
- Write code following existing patterns
- Self-verify quality
- Commit after each story
- Push after EPIC completion
- Update all status files
