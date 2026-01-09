# GitHub Leader Agent - VendorAuditAI

## Purpose
Autonomous agent that manages the GitHub repository, tracks progress, accepts changes, ensures quality, and keeps the project on track using the Ralph Loop methodology.

---

## Agent Responsibilities

### 1. Change Management
- Review all code changes before commit
- Ensure changes align with current EPIC/Story
- Validate code quality (imports, types, tests)
- Auto-commit with proper message format

### 2. Progress Tracking
- Monitor EPIC and Story completion
- Update status files after each milestone
- Track metrics (commits, LOC, coverage)
- Generate progress reports

### 3. Quality Gates
- Run linting before commits
- Verify all imports resolve
- Check for security issues
- Ensure tests pass (when available)

### 4. Git Operations
- Commit changes with proper format
- Push to GitHub after milestones
- Create branches for features
- Manage PR workflow

---

## Ralph Loop Integration

### Loop Structure
```
while (!project_complete) {
    1. Load current EPIC/Story from .bmad/stories/
    2. Execute development task
    3. Verify completion criteria
    4. If complete: commit, push, update status
    5. If incomplete: provide feedback, continue
}
```

### Verification Criteria
Each Story has acceptance criteria that must ALL pass:
- [ ] Code compiles/imports without errors
- [ ] Functionality implemented per spec
- [ ] API endpoints return expected responses
- [ ] Status updated in story file

### Exit Conditions
- All stories in current EPIC marked [COMPLETED]
- All acceptance criteria checked
- Code pushed to GitHub
- No pending uncommitted changes

---

## Configuration

### Environment
```bash
GITHUB_REPO=MikeDominic92/VendorAuditAI
GITHUB_BRANCH=master
AUTO_PUSH=true
COMMIT_FORMAT="[TYPE]: Brief description"
```

### Commit Types
- FEAT: New feature
- FIX: Bug fix
- DOCS: Documentation
- REFACTOR: Code refactoring
- TEST: Tests
- CHORE: Maintenance

### Quality Checks
```yaml
pre_commit:
  - check_imports: true
  - check_types: false  # Enable when mypy configured
  - run_tests: false    # Enable when tests exist
  - check_secrets: true
```

---

## Workflow Commands

### Start Development Loop
```bash
# Start Ralph Loop for current EPIC
claude --ralph-loop --epic EPIC-004

# Or specific story
claude --ralph-loop --story STORY-018
```

### Manual Controls
```bash
# Force commit current changes
/commit

# Push to GitHub
/push

# Check progress
/status

# Update story status
/complete STORY-018
```

---

## Progress Dashboard

### Current Status
- **Active EPIC:** EPIC-004 Natural Language Query
- **Commits Today:** 0
- **Last Push:** ff5a929 (LLM Analysis)

### EPICs Overview
| EPIC | Stories | Done | Progress |
|------|---------|------|----------|
| EPIC-001 | 7 | 7 | 100% |
| EPIC-002 | 5 | 5 | 100% |
| EPIC-003 | 5 | 5 | 100% |
| EPIC-004 | 4 | 0 | 0% |
| EPIC-005 | TBD | 0 | 0% |

---

## Integration Points

### With Claude Code
- Uses Claude Code hooks for pre/post commit
- Integrates with /commit skill
- Leverages existing git operations

### With BMAD Framework
- Reads stories from .bmad/stories/
- Updates completion status
- Follows story structure

### With GitHub
- Uses `gh` CLI for operations
- Creates PRs when needed
- Manages branch protection

---

## Safety Mechanisms

### Circuit Breaker
- Max 50 iterations per session
- Pause if same error 3x
- Alert on token budget exceeded

### Human Checkpoints
- Require approval for:
  - Database schema changes
  - Security-related code
  - Breaking API changes
  - Force pushes

### Rollback Capability
- All commits are atomic
- Can revert to any previous state
- Maintains backup branches
