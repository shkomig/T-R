# MCP Report Template (Monitoring, Change, Process)
## Version 1.0 | For Trading System Stabilization Project

---

## What is an MCP Report?

The **MCP Report** (Monitoring, Change, Process) is a structured document used to track development progress, document changes, and maintain context across development cycles. It serves as:

- **Progress Tracker**: Monitor task completion and timelines
- **Change Log**: Document all modifications and their rationale
- **Knowledge Base**: Preserve context for future reference
- **Communication Tool**: Share updates with stakeholders
- **Audit Trail**: Track decisions and outcomes

---

## MCP Report Structure

Each MCP report should be created for:
- Individual tasks within a phase
- Weekly sprint cycles
- Significant feature implementations
- Bug fixes requiring multiple changes
- Incident responses

---

# MCP REPORT: [Task/Feature Name]

## Report Metadata

| Field | Value |
|-------|-------|
| **MCP ID** | MCP-YYYYMMDD-XXX |
| **Phase** | [Phase 1/2/3/4] |
| **Task ID** | [Task number from work plan] |
| **Created Date** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD HH:MM |
| **Status** | [Not Started / In Progress / Blocked / Under Review / Completed] |
| **Priority** | [Critical / High / Medium / Low] |
| **Owner(s)** | [Name(s)] |
| **Reviewer(s)** | [Name(s)] |

---

## 1. CHANGE OBJECTIVE

### 1.1 Purpose
**What**: Clear, concise statement of what is being changed or implemented.

**Why**: Business/technical justification for this change.

**Success Criteria**: Measurable outcomes that define completion.

### 1.2 Scope
**In Scope**:
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

**Out of Scope**:
- Item 1 (reason: deferred to Phase X)
- Item 2 (reason: not relevant)

### 1.3 Impact Assessment
| Area | Impact Level | Description |
|------|--------------|-------------|
| Code | [None/Low/Medium/High] | [Description] |
| Configuration | [None/Low/Medium/High] | [Description] |
| Database | [None/Low/Medium/High] | [Description] |
| Dependencies | [None/Low/Medium/High] | [Description] |
| Performance | [None/Low/Medium/High] | [Description] |
| Security | [None/Low/Medium/High] | [Description] |

---

## 2. IMPLEMENTATION DESCRIPTION

### 2.1 Technical Approach
[Detailed description of the technical solution, architecture decisions, and design patterns used]

### 2.2 Files Modified/Created
```
Modified:
  - path/to/file1.py (lines 123-145, 200-234)
  - path/to/file2.py (lines 56-89)

Created:
  - path/to/new_file1.py
  - path/to/new_file2.py

Deleted:
  - path/to/old_file.py (reason: replaced by new_file1.py)
```

### 2.3 Dependencies
**Prerequisites**:
- [ ] Dependency 1 (MCP-YYYYMMDD-XXX completed)
- [ ] Dependency 2 (Configuration updated)

**External Dependencies**:
- Library version X.Y.Z required
- API endpoint availability

### 2.4 Configuration Changes
```yaml
# Before
config:
  setting1: old_value

# After
config:
  setting1: new_value
  setting2: additional_value  # NEW
```

---

## 3. IMPLEMENTATION STEPS

### 3.1 Planned Steps
| Step | Description | Owner | Est. Hours | Status |
|------|-------------|-------|------------|--------|
| 1 | [Step description] | [Name] | [Hours] | [Not Started/In Progress/Done] |
| 2 | [Step description] | [Name] | [Hours] | [Not Started/In Progress/Done] |
| 3 | [Step description] | [Name] | [Hours] | [Not Started/In Progress/Done] |

### 3.2 Actual Progress
#### Step 1: [Name]
**Date**: YYYY-MM-DD
**Time Spent**: [Actual hours]
**Status**: [Completed/Blocked/In Progress]

**Actions Taken**:
- Action 1
- Action 2
- Action 3

**Outcome**:
[Description of result]

**Issues Encountered**:
- Issue 1: [Description] → [Resolution]
- Issue 2: [Description] → [Still investigating]

**Code Changes**:
```python
# Example code snippet
def new_function():
    # Implementation details
    pass
```

**Commit**: `git commit hash` - "commit message"

---

#### Step 2: [Name]
[Repeat format from Step 1]

---

## 4. TESTING & VALIDATION

### 4.1 Test Plan
**Unit Tests**:
- [ ] Test case 1: [Description]
- [ ] Test case 2: [Description]
- [ ] Test case 3: [Description]

**Integration Tests**:
- [ ] Integration scenario 1
- [ ] Integration scenario 2

**Manual Tests**:
- [ ] Manual test 1
- [ ] Manual test 2

### 4.2 Test Results
#### Unit Tests
```bash
$ pytest tests/unit/test_feature.py -v
================================ test session starts =================================
collected 12 items

tests/unit/test_feature.py::test_case_1 PASSED                             [  8%]
tests/unit/test_feature.py::test_case_2 PASSED                             [ 16%]
...
tests/unit/test_feature.py::test_case_12 PASSED                            [100%]

================================ 12 passed in 2.34s ==================================
```

**Coverage**:
```
Name                                Stmts   Miss  Cover
-------------------------------------------------------
module/feature.py                     156      8    95%
-------------------------------------------------------
TOTAL                                 156      8    95%
```

#### Integration Tests
| Test Case | Expected | Actual | Status | Notes |
|-----------|----------|--------|--------|-------|
| Test 1 | [Expected outcome] | [Actual outcome] | ✅ Pass | - |
| Test 2 | [Expected outcome] | [Actual outcome] | ❌ Fail | Bug #123 filed |

### 4.3 Performance Benchmarks
**Before**:
- Metric 1: [Value + unit]
- Metric 2: [Value + unit]

**After**:
- Metric 1: [Value + unit] ([+/- %] change)
- Metric 2: [Value + unit] ([+/- %] change)

---

## 5. SUCCESS CRITERIA & RESULTS

### 5.1 Success Criteria
| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| [Criterion 1] | [Target value] | [Actual value] | ✅/❌ |
| [Criterion 2] | [Target value] | [Actual value] | ✅/❌ |
| [Criterion 3] | [Target value] | [Actual value] | ✅/❌ |

### 5.2 Acceptance Criteria
- [x] Criterion 1: Description
- [x] Criterion 2: Description
- [ ] Criterion 3: Description (pending review)

### 5.3 Verification
**Code Review**:
- Reviewer: [Name]
- Date: YYYY-MM-DD
- Status: [Approved / Changes Requested / Rejected]
- Comments: [Feedback summary]

**QA Sign-off**:
- QA Engineer: [Name]
- Date: YYYY-MM-DD
- Status: [Approved / Conditional / Rejected]
- Comments: [Testing notes]

---

## 6. PROGRESS STATUS & LOG

### 6.1 Timeline
```
Planned:  [Start Date] ━━━━━━━━━━━━━━► [End Date] (X days)
Actual:   [Start Date] ━━━━━━━━━━━━━━━━━━━━━━► [End Date] (Y days)
```

**Estimated Hours**: [XX hours]
**Actual Hours**: [YY hours]
**Variance**: [+/- ZZ hours]

### 6.2 Status Updates

#### Update: YYYY-MM-DD HH:MM
**Status**: [In Progress]
**Progress**: [X%]
**Completed**:
- Item 1
- Item 2

**In Progress**:
- Item 3 (80% complete)

**Blocked**:
- None

**Next Steps**:
- Action 1
- Action 2

---

#### Update: YYYY-MM-DD HH:MM
[Repeat format]

---

### 6.3 Milestone Tracking
| Milestone | Planned Date | Actual Date | Status |
|-----------|--------------|-------------|--------|
| Development Complete | YYYY-MM-DD | YYYY-MM-DD | ✅ Done |
| Code Review | YYYY-MM-DD | YYYY-MM-DD | 🔄 In Progress |
| Testing Complete | YYYY-MM-DD | - | ⏳ Pending |
| Deployment | YYYY-MM-DD | - | ⏳ Pending |

---

## 7. NOTES & ISSUES

### 7.1 Technical Notes
**Design Decisions**:
- Decision 1: [Description of decision]
  - Rationale: [Why this approach was chosen]
  - Alternatives Considered: [Other options]
  - Trade-offs: [Pros and cons]

**Implementation Notes**:
- Note 1: [Important technical detail]
- Note 2: [Gotcha or workaround]

### 7.2 Issues & Risks
| ID | Type | Severity | Description | Status | Resolution |
|----|------|----------|-------------|--------|------------|
| I-001 | Issue | High | [Description] | Open | [Action plan] |
| R-001 | Risk | Medium | [Description] | Mitigated | [Mitigation] |
| B-001 | Blocker | Critical | [Description] | Resolved | [Resolution] |

### 7.3 Lessons Learned
**What Went Well**:
- Item 1
- Item 2

**What Could Be Improved**:
- Item 1: [Description + proposed improvement]
- Item 2: [Description + proposed improvement]

**Knowledge Gained**:
- Insight 1
- Insight 2

---

## 8. DEPLOYMENT & ROLLBACK

### 8.1 Deployment Plan
**Environment**: [Staging / Production]
**Deployment Method**: [Manual / Automated / CI/CD]
**Deployment Window**: [Date/Time]
**Approvers**: [Names]

**Pre-Deployment Checklist**:
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Configuration updated
- [ ] Backup taken
- [ ] Rollback plan documented

**Deployment Steps**:
1. Step 1
2. Step 2
3. Step 3

### 8.2 Rollback Plan
**Rollback Trigger Conditions**:
- Condition 1
- Condition 2

**Rollback Steps**:
1. Step 1
2. Step 2
3. Step 3

**Recovery Time Objective (RTO)**: [X minutes]

---

## 9. DOCUMENTATION UPDATES

### 9.1 Documentation Changed
- [ ] README.md updated
- [ ] API documentation updated
- [ ] Configuration guide updated
- [ ] Operations runbook updated
- [ ] Code comments added

### 9.2 Documentation Links
- [Link to updated doc 1](url)
- [Link to updated doc 2](url)

---

## 10. SIGN-OFF

### 10.1 Completion Checklist
- [ ] All implementation steps completed
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] QA verification complete
- [ ] Performance validated
- [ ] Security review (if applicable)

### 10.2 Approvals
| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | [Name] | YYYY-MM-DD | [Initials/Signature] |
| Code Reviewer | [Name] | YYYY-MM-DD | [Initials/Signature] |
| QA Engineer | [Name] | YYYY-MM-DD | [Initials/Signature] |
| Team Lead | [Name] | YYYY-MM-DD | [Initials/Signature] |

---

## 11. RELATED REFERENCES

### 11.1 Related MCPs
- MCP-YYYYMMDD-XXX: [Description]
- MCP-YYYYMMDD-YYY: [Description]

### 11.2 External References
- [Work Plan Task #X.Y](link)
- [GitHub Issue #123](link)
- [Confluence Page](link)
- [Design Document](link)

### 11.3 Code References
- Pull Request: [#123](link)
- Branch: `feature/task-name`
- Commits: `abc123...def456`

---

**Report Status**: [Draft / In Review / Approved / Completed / Archived]
**Last Updated**: YYYY-MM-DD HH:MM
**Next Review**: YYYY-MM-DD

---

# APPENDIX: MCP Report Usage Guide

## When to Create an MCP Report

Create a new MCP report for:
1. **Each work plan task** that takes >1 day
2. **Weekly development sprints**
3. **Significant bug fixes** requiring multiple changes
4. **Feature implementations**
5. **Architectural changes**
6. **Incident responses**
7. **Performance optimizations**

## MCP Report Naming Convention

```
MCP-YYYYMMDD-XXX-ShortDescription.md

Where:
  YYYYMMDD = Creation date
  XXX = Sequential number for that day
  ShortDescription = 2-4 word description

Examples:
  MCP-20251110-001-RemoveRandomSignals.md
  MCP-20251110-002-FixExposureCalculation.md
  MCP-20251115-001-RefactorDashboard.md
```

## MCP Report Workflow

### Step 1: Creation (Status: Not Started)
1. Copy this template
2. Rename with MCP naming convention
3. Fill in Sections 1-2 (Objective & Description)
4. Fill in Section 3.1 (Planned Steps)
5. Commit to repository: `git add` + `git commit`

### Step 2: Development (Status: In Progress)
1. Update Section 3.2 as you complete each step
2. Record issues in Section 7.2 as they arise
3. Add status updates to Section 6.2 (at least daily)
4. Commit updates regularly
5. Push to repository at end of each day

### Step 3: Testing (Status: Under Review)
1. Fill in Section 4 (Testing & Validation)
2. Record test results
3. Update Section 5 (Success Criteria)
4. Request code review
5. Address feedback and update MCP

### Step 4: Completion (Status: Completed)
1. Complete Section 8 (Deployment)
2. Update all documentation (Section 9)
3. Fill in Section 7.3 (Lessons Learned)
4. Get all sign-offs (Section 10)
5. Final commit and close

## Maintaining MCP Reports

### Daily Updates
```bash
# Pull latest changes
git pull origin main

# Edit your MCP report
nano docs/mcps/MCP-20251110-001-RemoveRandomSignals.md

# Add status update to Section 6.2
# Update progress in Section 3.2
# Record any issues in Section 7.2

# Commit changes
git add docs/mcps/MCP-20251110-001-RemoveRandomSignals.md
git commit -m "MCP-001: Daily update - completed step 3"
git push origin main
```

### Weekly Reviews
1. Review all active MCPs
2. Update timelines if needed
3. Escalate blockers
4. Report to stakeholders

### Phase Gate Reviews
1. Review all MCPs for the phase
2. Verify all marked as completed
3. Extract lessons learned
4. Archive completed MCPs

## MCP Report Repository Structure

```
docs/
├── mcps/
│   ├── active/                    # Currently in-progress MCPs
│   │   ├── MCP-20251110-001-RemoveRandomSignals.md
│   │   ├── MCP-20251110-002-FixExposureCalculation.md
│   │   └── MCP-20251115-001-RefactorDashboard.md
│   ├── completed/                 # Completed MCPs (by phase)
│   │   ├── phase1/
│   │   ├── phase2/
│   │   └── phase3/
│   ├── archived/                  # Cancelled or superseded MCPs
│   └── templates/
│       └── MCP_REPORT_TEMPLATE.md # This file
└── mcp_index.md                  # Index of all MCPs
```

## MCP Index File

Maintain an index file for quick reference:

```markdown
# MCP Report Index

## Active MCPs
| MCP ID | Task | Owner | Status | Priority | Started | Due |
|--------|------|-------|--------|----------|---------|-----|
| MCP-20251110-001 | Remove Random Signals | Alice | In Progress | Critical | 2025-11-10 | 2025-11-11 |
| MCP-20251110-002 | Fix Exposure Calc | Bob | Not Started | Critical | 2025-11-11 | 2025-11-13 |

## Completed MCPs (Last 10)
| MCP ID | Task | Owner | Completed | Duration |
|--------|------|-------|-----------|----------|
| MCP-20251109-001 | Setup CI/CD | Charlie | 2025-11-09 | 2 days |

## Statistics
- Total MCPs: 15
- Active: 2
- Completed: 12
- Cancelled: 1
- Average Duration: 2.5 days
- On-Time Completion: 85%
```

## Tips for Effective MCP Reports

### DO:
✅ Update daily, even if just a status note
✅ Be specific about issues and blockers
✅ Include code snippets for clarity
✅ Link to related resources
✅ Record lessons learned while fresh
✅ Keep language clear and concise
✅ Use checklists for tracking
✅ Commit changes to version control

### DON'T:
❌ Wait until task complete to fill in
❌ Use vague descriptions
❌ Skip sections (mark N/A if not applicable)
❌ Forget to update status
❌ Ignore blockers
❌ Write novel-length descriptions
❌ Keep only in local files (use git!)

## Integration with Development Tools

### Git Commit Messages
```bash
# Reference MCP in commit messages
git commit -m "MCP-001: Remove random signal fallbacks from dashboard (Step 1/6)"
git commit -m "MCP-001: Add error handling without fallbacks (Step 2/6)"
```

### Pull Requests
```markdown
## Pull Request: Fix Random Signal Generation

**Related MCP**: MCP-20251110-001-RemoveRandomSignals.md

**Changes**:
- Removed random.choice() fallbacks from signal generation
- Added proper error handling
- Updated tests

**Testing**:
See MCP report Section 4 for full test results

**Review Checklist**:
- [ ] Code follows style guide
- [ ] Tests pass
- [ ] MCP report updated
```

### Issue Tracking
Link issues to MCPs:
```markdown
**Issue #123**: Random signals generated on strategy failure

**Related MCP**: MCP-20251110-001
**Priority**: Critical
**Status**: In Progress
**Owner**: Alice

See MCP report for detailed progress and implementation plan.
```

## Reporting to Stakeholders

### Daily Standup Report
Extract from Section 6.2 (Status Updates):
- What was completed yesterday
- What's planned for today
- Any blockers

### Weekly Progress Report
Compile from all active MCPs:
- Phase progress percentage
- Completed tasks
- In-progress tasks
- Blockers and risks
- Next week's plan

### Phase Gate Report
Summarize from all phase MCPs:
- All deliverables status
- Success metrics achieved
- Issues encountered and resolved
- Lessons learned
- Readiness for next phase

---

## MCP Report Templates for Common Scenarios

### Quick-Start: Simple Bug Fix
```markdown
# MCP REPORT: [Bug #XXX - Description]

## 1. CHANGE OBJECTIVE
**What**: Fix [bug description]
**Why**: [Impact and urgency]
**Success**: Bug no longer reproducible

## 3. IMPLEMENTATION STEPS
- [x] Step 1: Identify root cause
- [x] Step 2: Implement fix
- [x] Step 3: Add regression test
- [ ] Step 4: Deploy and verify

## 4. TESTING
- [x] Test case reproduces bug
- [x] Test passes after fix
- [x] Regression test added

## 10. SIGN-OFF
- [x] All steps completed
- [x] Tests passing
- [x] Deployed
```

### Quick-Start: Feature Implementation
```markdown
# MCP REPORT: [Feature Name]

## 1. CHANGE OBJECTIVE
**What**: Implement [feature]
**Why**: [Business value]
**Success**: [Acceptance criteria]

## 2. IMPLEMENTATION DESCRIPTION
[Architecture and approach]

## 3. IMPLEMENTATION STEPS
[Detailed steps with owners and timelines]

## 4. TESTING
[Comprehensive test plan]

## 7. NOTES
[Design decisions and trade-offs]

## 10. SIGN-OFF
[All approvals]
```

---

**Template Version**: 1.0
**Last Updated**: 2025-11-10
**Maintained By**: Development Team
**Questions**: Contact [Team Lead Name]

---

*End of MCP Report Template and Usage Guide*
