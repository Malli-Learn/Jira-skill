#!/usr/bin/env python3
"""
Create JIRA Stories from markdown files in the story-md folder.

Usage:
    # Push all stories in story-md/
    python create_jira_stories.py

    # Push specific file(s)
    python create_jira_stories.py story-md/story-send-money-estimate.md

Credentials are read from .env in the project root.
"""

import os
import re
import sys
import base64
import json
from pathlib import Path

import requests
from dotenv import load_dotenv


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

# Resolve project root (script lives at .github/skills/jira-story-creator/scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
STORY_DIR = PROJECT_ROOT / "story-md"


def load_config() -> dict:
    """Load and validate JIRA config from .env."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        raise FileNotFoundError(f".env file not found at: {env_path}")

    load_dotenv(env_path)

    required = ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT"]
    config = {}
    missing = []

    for key in required:
        val = os.getenv(key, "").strip()
        if not val:
            missing.append(key)
        else:
            config[key] = val

    if missing:
        raise EnvironmentError(
            f"Missing required variables in .env: {', '.join(missing)}"
        )

    config["JIRA_BASE_URL"] = config["JIRA_BASE_URL"].rstrip("/")
    config["JIRA_FEATURE"] = os.getenv("JIRA_FEATURE", "").strip()
    return config


# ─────────────────────────────────────────────
# Markdown Parsing
# ─────────────────────────────────────────────

def parse_story(filepath: Path) -> dict:
    """
    Parse a story markdown file into structured fields.

    Returns:
        dict with keys: summary, description, acceptance_criteria
    """
    text = filepath.read_text(encoding="utf-8")

    # --- Summary (## Summary section content) ---
    summary_match = re.search(
        r"##\s+Summary\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL
    )
    if summary_match:
        summary = summary_match.group(1).strip()
        # Take only the first non-empty line as the JIRA summary
        for line in summary.splitlines():
            line = line.strip()
            if line:
                summary = line
                break
    else:
        # Fall back to H1 title
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        summary = title_match.group(1).strip() if title_match else filepath.stem

    # --- Acceptance Criteria ---
    ac_match = re.search(
        r"###\s+Acceptance Criteria\s*\n(.*?)(?=\n###|\n##|\Z)", text, re.DOTALL
    )
    acceptance_criteria = []
    if ac_match:
        for line in ac_match.group(1).splitlines():
            cb = re.match(r"\s*-\s*\[[ xX]\]\s+(.+)", line)
            if cb:
                acceptance_criteria.append(cb.group(1).strip())

    description_text = text
    # Strip H1 title line (already used as JIRA ticket summary)
    description_text = re.sub(r"^#\s+.+$\n?", "", description_text, flags=re.MULTILINE)
    # Strip ## Summary section (heading + its content until the next ##)
    description_text = re.sub(
        r"##\s+Summary\s*\n.*?(?=\n##|\Z)", "", description_text, flags=re.DOTALL
    )
    # Strip ## Description heading line (the JIRA field itself is already "Description")
    description_text = re.sub(r"^##\s+Description\s*$\n?", "", description_text, flags=re.MULTILINE)
    # Strip "As a [role], I want to ..." user story opening lines
    description_text = re.sub(
        r"^As an? .+?,?\s+I want to .+$\n?", "", description_text, flags=re.MULTILINE
    )

    return {
        "summary": summary,
        "description": description_text,
        "acceptance_criteria": acceptance_criteria,
        "filename": filepath.name,
    }


# ─────────────────────────────────────────────
# Markdown → ADF Conversion
# ─────────────────────────────────────────────

def _strip_inline(text: str) -> str:
    """Remove common inline markdown formatting."""
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)   # links
    text = re.sub(r"\*\*\*([^*]+)\*\*\*", r"\1", text)      # bold+italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)           # bold
    text = re.sub(r"\*([^*]+)\*", r"\1", text)               # italic
    text = re.sub(r"`([^`]+)`", r"\1", text)                 # inline code
    return text.strip()


def _criterion_to_gherkin_scenario(criterion: str) -> str:
    """Convert a single acceptance criterion string into a Gherkin Scenario block."""
    lines = [f"  Scenario: {criterion}"]
    lines.append("    Given the user is on the Send Money screen")

    # Pattern: "X when Y" → When Y, Then X
    m = re.match(r"^(.+?)\s+when\s+(.+)$", criterion, re.IGNORECASE)
    if m:
        then_part = m.group(1).strip()
        when_part = m.group(2).strip()
        lines.append(f"    When {when_part}")
        lines.append(f"    Then {then_part}")

    # Pattern: "Users can X" → When the user X, Then the action succeeds
    elif re.match(r"^Users? can ", criterion, re.IGNORECASE):
        action = re.sub(r"^Users? can ", "", criterion, flags=re.IGNORECASE)
        lines.append(f"    When the user {action}")
        lines.append(f"    Then the action should complete successfully")

    # Pattern: subject starts with known display/enforcement nouns
    elif re.match(
        r"^(All |Payment |Delivery |Transaction |Estimate |Promotional )",
        criterion, re.IGNORECASE
    ):
        lowered = criterion[0].lower() + criterion[1:]
        lines.append("    When the user views the estimate details")
        lines.append(f"    Then {lowered}")

    # Generic fallback
    else:
        lowered = criterion[0].lower() + criterion[1:]
        lines.append("    When the user interacts with the feature")
        lines.append(f"    Then {lowered}")

    return "\n".join(lines)


def _build_gherkin_adf_block(criteria: list, feature_name: str) -> dict:
    """Return an ADF codeBlock node with Gherkin for the given criteria list."""
    gherkin_lines = [f"Feature: {feature_name}", ""]
    for criterion in criteria:
        gherkin_lines.append(_criterion_to_gherkin_scenario(criterion))
        gherkin_lines.append("")
    gherkin_text = "\n".join(gherkin_lines).rstrip() + "\n"
    return {
        "type": "codeBlock",
        "attrs": {"language": "gherkin"},
        "content": [{"type": "text", "text": gherkin_text}],
    }


def md_to_adf(markdown: str) -> dict:
    """
    Convert basic markdown to Atlassian Document Format (ADF).

    Handles: headings, bullet lists, checkboxes, paragraphs.
    The Acceptance Criteria section is rendered as a Gherkin code block.
    """
    # Extract feature name for the Gherkin Feature header
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    feature_name = title_match.group(1).strip() if title_match else "Feature"

    lines = markdown.splitlines()
    content = []
    i = 0
    in_ac_section = False   # True while inside "### Acceptance Criteria"
    ac_items: list = []     # Collected criteria text for Gherkin

    def flush_ac():
        """Emit collected acceptance criteria as a Gherkin code block."""
        if ac_items:
            content.append(_build_gherkin_adf_block(ac_items, feature_name))
            ac_items.clear()

    while i < len(lines):
        line = lines[i]

        # --- Heading ---
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            # Leaving AC section — flush collected items first
            if in_ac_section:
                flush_ac()
                in_ac_section = False

            level = min(len(heading_match.group(1)), 6)
            heading_text = _strip_inline(heading_match.group(2))

            # Detect Acceptance Criteria heading
            if re.search(r"acceptance criteria", heading_text, re.IGNORECASE):
                in_ac_section = True

            content.append({
                "type": "heading",
                "attrs": {"level": level},
                "content": [{"type": "text", "text": heading_text}],
            })
            i += 1
            continue

        # --- Inside Acceptance Criteria: collect checkbox items ---
        if in_ac_section:
            if re.match(r"^\s*[-*]\s+\[[ xX]\]\s+", line):
                raw = re.sub(r"^\s*[-*]\s+\[[ xX]\]\s+", "", line).strip()
                ac_items.append(_strip_inline(raw))
                i += 1
                continue
            # Non-checkbox content ends the AC collection
            if line.strip() and not re.match(r"^\s*[-*]\s+", line):
                flush_ac()
                in_ac_section = False
            elif not line.strip():
                i += 1
                continue

        # --- Bullet / checkbox list (outside AC section) ---
        if re.match(r"^\s*[-*]\s+", line):
            list_items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                raw = re.sub(r"^\s*[-*]\s+", "", lines[i])
                raw = re.sub(r"^\[[ xX]\]\s+", "", raw)   # strip checkbox marker
                item_text = _strip_inline(raw)
                list_items.append({
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": item_text}],
                    }],
                })
                i += 1
            content.append({"type": "bulletList", "content": list_items})
            continue

        # --- Horizontal rule ---
        if re.match(r"^---+$", line.strip()):
            content.append({"type": "rule"})
            i += 1
            continue

        # --- Empty line ---
        if not line.strip():
            i += 1
            continue

        # --- Regular paragraph ---
        paragraph_text = _strip_inline(line)
        if paragraph_text:
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": paragraph_text}],
            })
        i += 1

    # Flush any remaining AC items at end of file
    flush_ac()

    if not content:
        content = [{"type": "paragraph", "content": [{"type": "text", "text": " "}]}]

    return {"version": 1, "type": "doc", "content": content}


# ─────────────────────────────────────────────
# JIRA API
# ─────────────────────────────────────────────

def _auth_header(email: str, token: str) -> str:
    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
    return f"Basic {credentials}"


def create_jira_story(config: dict, story: dict) -> tuple[str, str]:
    """
    POST a new JIRA Story issue.

    Returns:
        (issue_key, issue_url)
    """
    url = f"{config['JIRA_BASE_URL']}/rest/api/3/issue"

    headers = {
        "Authorization": _auth_header(config["JIRA_EMAIL"], config["JIRA_API_TOKEN"]),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    description_adf = md_to_adf(story["description"])

    payload: dict = {
        "fields": {
            "project": {"key": config["JIRA_PROJECT"]},
            "summary": story["summary"],
            "description": description_adf,
            "issuetype": {"name": "Story"},
        }
    }

    # Link to epic if JIRA_FEATURE is set
    if config.get("JIRA_FEATURE"):
        # customfield_10014 is the standard Epic Link field for Atlassian Cloud
        payload["fields"]["customfield_10014"] = config["JIRA_FEATURE"]

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code in (200, 201):
        data = response.json()
        key = data.get("key", "UNKNOWN")
        issue_url = f"{config['JIRA_BASE_URL']}/browse/{key}"
        return key, issue_url

    # Surface a helpful error message
    try:
        error_detail = response.json()
        messages = error_detail.get("errorMessages", [])
        errors = error_detail.get("errors", {})
        detail = "; ".join(messages) or json.dumps(errors)
    except Exception:
        detail = response.text[:300]

    raise RuntimeError(
        f"JIRA API error {response.status_code}: {detail}"
    )


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

def main():
    try:
        config = load_config()
    except (FileNotFoundError, EnvironmentError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    # Resolve files to process
    if len(sys.argv) > 1:
        files = [Path(f).resolve() for f in sys.argv[1:]]
        missing = [f for f in files if not f.exists()]
        if missing:
            for m in missing:
                print(f"File not found: {m}", file=sys.stderr)
            sys.exit(1)
    else:
        files = sorted(STORY_DIR.glob("*.md"))
        if not files:
            print(f"No markdown files found in: {STORY_DIR}", file=sys.stderr)
            sys.exit(1)

    print(f"Found {len(files)} story file(s) → project {config['JIRA_PROJECT']}\n")
    if config.get("JIRA_FEATURE"):
        print(f"Linking to epic: {config['JIRA_FEATURE']}\n")

    results = []
    for filepath in files:
        print(f"  Processing: {filepath.name}")
        try:
            story = parse_story(filepath)
            key, issue_url = create_jira_story(config, story)
            print(f"  ✓ Created {key}: {story['summary']}")
            print(f"    {issue_url}\n")
            results.append({"file": filepath.name, "key": key, "status": "created"})
        except Exception as exc:
            print(f"  ✗ Failed: {exc}\n")
            results.append({"file": filepath.name, "key": None, "status": f"error: {exc}"})

    # Summary table
    print("=" * 50)
    print("Summary")
    print("=" * 50)
    for r in results:
        badge = f"[{r['key']}]" if r["key"] else "[FAILED]"
        print(f"  {badge:<12} {r['file']} — {r['status']}")

    failed = [r for r in results if not r["key"]]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
