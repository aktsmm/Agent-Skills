#!/usr/bin/env python3
"""
Fetch descriptions from various GitHub repositories and update skill-index.json
"""

import json
import subprocess
import re
import time
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
INDEX_PATH = SCRIPT_DIR / ".." / "references" / "skill-index.json"

# Source configurations: (source_id, owner, repo, skill_path_prefix)
SOURCES = [
    ("composio-awesome", "ComposioHQ", "awesome-claude-skills", ""),
    ("claude-code-harness", "Chachamaru127", "claude-code-harness", "skills"),
    ("claude-command-control", "enuno", "claude-command-and-control", "skills"),
    ("claude-plugins-plus", "jeremylongshore", "claude-code-plugins-plus-skills", "skills"),
    ("aktsmm-agent-skills", "aktsmm", "Agent-Skills", ""),
]


def get_skill_description(owner: str, repo: str, skill_path: str) -> str | None:
    """Fetch description from SKILL.md frontmatter"""
    try:
        # Try SKILL.md first
        result = subprocess.run(
            [
                "gh", "api",
                f"repos/{owner}/{repo}/contents/{skill_path}/SKILL.md",
                "-H", "Accept: application/vnd.github.raw"
            ],
            capture_output=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            # Try README.md as fallback
            result = subprocess.run(
                [
                    "gh", "api",
                    f"repos/{owner}/{repo}/contents/{skill_path}/README.md",
                    "-H", "Accept: application/vnd.github.raw"
                ],
                capture_output=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                return None
        
        content = result.stdout
        
        # Extract description from YAML frontmatter
        match = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if match:
            desc = match.group(1).strip()
            # Remove trailing quote if present
            desc = desc.rstrip('"\'')
            # Truncate if too long
            if len(desc) > 100:
                desc = desc[:97] + "..."
            return desc
        
        # Fallback: try to get first sentence after # heading
        match = re.search(r'^#\s+.+?\n+(.+?)\.', content, re.MULTILINE)
        if match:
            desc = match.group(1).strip()
            if len(desc) > 100:
                desc = desc[:97] + "..."
            return desc
        
        return None
        
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f"    Error: {e}")
        return None


def main():
    # Load index
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    # Create source lookup
    source_lookup = {s["id"]: s for s in index["sources"]}
    
    updated = 0
    skipped = 0
    
    for skill in index["skills"]:
        current_desc = skill.get("description", "")
        
        # Skip if already has a good description
        if current_desc and not current_desc.endswith(" skill"):
            skipped += 1
            continue
        
        source_id = skill.get("source")
        source = source_lookup.get(source_id)
        
        if not source:
            continue
        
        # Parse owner/repo from source URL
        url = source.get("url", "")
        match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
        if not match:
            continue
        
        owner, repo = match.groups()
        skill_path = skill.get("path", skill["name"])
        
        print(f"Fetching: {source_id}/{skill['name']}...")
        desc = get_skill_description(owner, repo, skill_path)
        
        if desc:
            skill["description"] = desc
            print(f"  OK: {desc[:60]}...")
            updated += 1
        else:
            print(f"  SKIP: {current_desc}")
        
        # Rate limiting
        time.sleep(0.3)
    
    # Save updated index
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"\nUpdated {updated} skills, skipped {skipped}")


if __name__ == "__main__":
    main()
