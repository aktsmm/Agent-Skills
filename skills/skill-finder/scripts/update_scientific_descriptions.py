#!/usr/bin/env python3
"""
Fetch descriptions from K-Dense-AI/claude-scientific-skills SKILL.md files
and update skill-index.json
"""

import json
import subprocess
import re
import time
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
INDEX_PATH = SCRIPT_DIR / ".." / "references" / "skill-index.json"

def get_skill_description(skill_name: str) -> str | None:
    """Fetch description from SKILL.md frontmatter"""
    try:
        result = subprocess.run(
            [
                "gh", "api",
                f"repos/K-Dense-AI/claude-scientific-skills/contents/scientific-skills/{skill_name}/SKILL.md",
                "-H", "Accept: application/vnd.github.raw"
            ],
            capture_output=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"  ⚠️ Failed to fetch {skill_name}: {result.stderr[:100]}")
            return None
        
        content = result.stdout
        
        # Extract description from YAML frontmatter
        # Pattern: description: "..." or description: '...' or description: ...
        match = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if match:
            desc = match.group(1).strip()
            # Truncate if too long
            if len(desc) > 100:
                desc = desc[:97] + "..."
            return desc
        
        return None
        
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ Timeout fetching {skill_name}")
        return None
    except Exception as e:
        print(f"  ⚠️ Error fetching {skill_name}: {e}")
        return None


def main():
    # Load index
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    # Find all claude-scientific-skills skills
    updated = 0
    skipped = 0
    
    for skill in index["skills"]:
        if skill.get("source") != "claude-scientific-skills":
            continue
        
        name = skill["name"]
        current_desc = skill.get("description", "")
        
        # Skip if already has a good description (not "xxx skill" pattern)
        if current_desc and not current_desc.endswith(" skill"):
            skipped += 1
            continue
        
        print(f"Fetching: {name}...")
        desc = get_skill_description(name)
        
        if desc:
            skill["description"] = desc
            # Also update categories based on description keywords
            if "community" in skill.get("categories", []):
                skill["categories"] = infer_categories(name, desc)
            print(f"  OK: {desc[:60]}...")
            updated += 1
        else:
            print(f"  SKIP: {current_desc}")
        
        # Rate limiting - 1 request per 0.5 seconds
        time.sleep(0.5)
    
    # Save updated index
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"\nUpdated {updated} skills, skipped {skipped}")


def infer_categories(name: str, desc: str) -> list[str]:
    """Infer categories from skill name and description"""
    categories = ["science"]
    
    text = (name + " " + desc).lower()
    
    if any(kw in text for kw in ["bio", "protein", "dna", "rna", "gene", "cell", "molecular", "sequence"]):
        categories.append("biology")
    if any(kw in text for kw in ["chem", "molecule", "compound", "drug"]):
        categories.append("chemistry")
    if any(kw in text for kw in ["data", "analysis", "visualization", "plot", "statistics"]):
        categories.append("data-science")
    if any(kw in text for kw in ["database", "db", "query"]):
        categories.append("database")
    if any(kw in text for kw in ["machine learning", "ml", "deep", "neural", "ai"]):
        categories.append("ml")
    if any(kw in text for kw in ["quantum", "physics"]):
        categories.append("physics")
    if any(kw in text for kw in ["clinical", "medical", "patient", "health"]):
        categories.append("medical")
    if any(kw in text for kw in ["paper", "publication", "citation", "literature"]):
        categories.append("research")
    
    return categories


if __name__ == "__main__":
    main()
