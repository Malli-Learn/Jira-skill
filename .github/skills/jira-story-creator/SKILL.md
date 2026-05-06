---
name: jira-story-creator
description: "Create JIRA stories from markdown files in the story-md folder. Use when: pushing stories to JIRA, creating JIRA tickets from md files, syncing story-md to JIRA, bulk creating issues, push story to jira."
argument-hint: "Optional: specific story file name(s) to push, or leave blank to push all stories"
---

# JIRA Story Creator

Creates JIRA Story issues from markdown files in the `story-md/` folder. Each `.md` file becomes one JIRA Story ticket. JIRA credentials are read from the `.env` file in the project root.

## ⚠️ Safety Constraints — NEVER Violate

> **This skill is CREATE-ONLY. It must never delete or update existing JIRA issues.**
>
> - **No DELETE** — never call the JIRA delete issue API (`DELETE /rest/api/3/issue/{issueId}`), regardless of user request.
> - **No UPDATE** — never call the JIRA edit/update API (`PUT /rest/api/3/issue/{issueId}`), even if a story with the same summary already exists.
> - If a story appears to already exist in JIRA, **skip it and warn the user** — do not overwrite it.
> - These constraints apply to production environments where accidental mutations cannot be undone.
>
> If the user asks to delete or update a JIRA story, **decline and explain** that this skill is intentionally restricted to creation only.

## When to Use
- "Push stories to JIRA"
- "Create JIRA tickets from markdown files"
- "Sync story-md folder to JIRA"
- "Create a JIRA story from [filename].md"
- "Push all stories to JIRA"

## Prerequisites
- `.env` file in the project root with JIRA credentials (already configured)
- Python 3.7+
- Packages: `requests`, `python-dotenv`

## Procedure

### Step 1: Install Dependencies

```bash
pip install -r .github/skills/jira-story-creator/requirements.txt
```

### Step 2: Run the Script

**Push all stories from `story-md/`:**
```bash
python .github/skills/jira-story-creator/scripts/create_jira_stories.py
```

**Push specific story file(s):**
```bash
python .github/skills/jira-story-creator/scripts/create_jira_stories.py story-md/story-send-money-estimate.md
```

### Step 3: Verify Output

The script prints a JIRA key and URL for each created ticket:
```
Processing: story-send-money-estimate.md
  Created: KAN-42 - Send Money Estimate
  URL: https://your-instance.atlassian.net/browse/KAN-42
```

## Markdown File Format

Each story file must follow this structure:

```markdown
# Story Title

## Summary
One-line summary (becomes JIRA ticket title)

## Description
Full description as user story and feature details...

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Dependencies
- Dependency 1
```

### Field Mapping

| Markdown Section      | JIRA Field              |
|-----------------------|-------------------------|
| `## Summary` content  | Summary (ticket title)  |
| Full file content     | Description (ADF)       |
| `JIRA_PROJECT` (.env) | Project key             |
| `JIRA_FEATURE` (.env) | Epic link (optional)    |
| Issue type            | Story (fixed)           |

## Environment Variables (`.env`)

| Variable         | Required | Description                                        |
|------------------|----------|----------------------------------------------------|
| `JIRA_BASE_URL`  | Yes      | Atlassian instance URL (no trailing slash)         |
| `JIRA_EMAIL`     | Yes      | Atlassian account email                            |
| `JIRA_API_TOKEN` | Yes      | API token from Atlassian security settings         |
| `JIRA_PROJECT`   | Yes      | Default project key (e.g. `KAN`)                  |
| `JIRA_FEATURE`   | No       | Epic key to link all stories (e.g. `KAN-10`)      |

## Script Reference

See [scripts/create_jira_stories.py](./scripts/create_jira_stories.py) for the full implementation.
