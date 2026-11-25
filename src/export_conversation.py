"""Exports the entire conversation trajectory into a single structured Markdown file."""

import json
from pathlib import Path
import re

TRANSCRIPT_PATH = Path(
    "/Users/chiraglamba/.gemini/antigravity/brain/409b60cf-2faa-4b03-9617-87b8b02040f6/.system_generated/logs/transcript_full.jsonl"
)
OUTPUT_FILE_1 = Path("/Users/chiraglamba/Documents/antigravity/SkillBridge/COMPLETE_CONVERSATION_HISTORY.md")
OUTPUT_FILE_2 = Path("/Users/chiraglamba/Documents/antigravity/SkillBridge /COMPLETE_CONVERSATION_HISTORY.md")


def clean_user_prompt(text: str) -> str:
    if not text:
        return ""
    # Extract request inside <USER_REQUEST> tags if present
    m = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", text, re.DOTALL)
    req = m.group(1).strip() if m else text.strip()

    # Extract attachments
    media_matches = re.findall(r"- \[Attachment: [^\]]+ \(([^)]+)\)\]", text)
    if media_matches:
        req += "\n\n**Attached Images / Files:**\n" + "\n".join([f"- `{m}`" for m in media_matches])
    return req


def main():
    if not TRANSCRIPT_PATH.exists():
        print(f"Error: {TRANSCRIPT_PATH} not found.")
        return

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        steps = [json.loads(line) for line in f]

    md_lines = [
        "# SkillBridge: Complete Conversation History & Trajectory",
        "",
        "**Conversation ID**: `409b60cf-2faa-4b03-9617-87b8b02040f6`  ",
        "**Platform**: Google Antigravity (DeepMind)  ",
        "**Project**: SkillBridge — Interpretable Graph-Theoretic Career Path & Skill-Gap Analyzer  ",
        f"**Total Captured Trajectory Steps**: {len(steps)}  ",
        "",
        "---",
        "",
    ]

    user_turn_counter = 0

    for step in steps:
        step_type = step.get("type")
        content = step.get("content", "")
        created_at = step.get("created_at", "")
        tool_calls = step.get("tool_calls", [])

        if step_type == "USER_INPUT":
            user_turn_counter += 1
            cleaned = clean_user_prompt(content)
            md_lines.append(f"## 👤 User Prompt #{user_turn_counter}")
            if created_at:
                md_lines.append(f"*Recorded At: {created_at}*\n")
            md_lines.append(cleaned)
            md_lines.append("\n---\n")

        elif step_type == "PLANNER_RESPONSE":
            # If model produced text content, record it
            if content and content.strip():
                md_lines.append(f"### 🤖 Antigravity Assistant Response (Turn #{user_turn_counter})")
                if created_at:
                    md_lines.append(f"*Recorded At: {created_at}*\n")
                md_lines.append(content.strip())
                md_lines.append("\n---\n")

    full_text = "\n".join(md_lines)

    OUTPUT_FILE_1.write_text(full_text, encoding="utf-8")
    OUTPUT_FILE_2.write_text(full_text, encoding="utf-8")

    print(f"Successfully generated {OUTPUT_FILE_1} ({len(full_text):,} characters, {len(full_text.splitlines()):,} lines).")


if __name__ == "__main__":
    main()
