#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Writing Workspace Setup Script

Creates a complete book writing workspace with:
- Directory structure for manuscripts, images, materials
- AI agent configurations
- Writing instructions and guidelines
- Git prompts
- Utility scripts

Usage:
    python setup_workspace.py --name "my-book" --title "My Book Title" --path "D:\\projects"
"""

import argparse
import os
import shutil
from pathlib import Path
from typing import List, Optional

# Script location (for finding templates)
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_DIR / "references"
ASSETS_DIR = SKILL_DIR / "assets"


def create_directory_structure(
    base_path: Path,
    chapters: List[str],
    include_review: bool = True,
    include_materials: bool = True
) -> None:
    """Create the complete directory structure."""
    
    # Main content directories
    dirs = [
        ".github/agents",
        ".github/instructions/writing",
        ".github/instructions/git",
        ".github/prompts",
        "docs",
        "scripts",
        "output_sessions",
    ]
    
    # Chapter-based directories
    for i, chapter in enumerate(chapters):
        chapter_folder = f"{i}. {chapter}"
        dirs.append(f"01_contents_keyPoints/{chapter_folder}")
        dirs.append(f"02_contents/{chapter_folder}")
        dirs.append(f"04_images/{i}_{chapter.replace(' ', '_')}")
    
    # Optional: Re:VIEW output
    if include_review:
        dirs.extend([
            "03_re-view_output/output_re",
            "03_re-view_output/output_pdf",
            "03_re-view_output/images",
        ])
    
    # Optional: Materials
    if include_materials:
        dirs.extend([
            "99_material/01_contracts",
            "99_material/02_proposals",
            "99_material/03_references",
        ])
    
    # Create all directories
    for dir_path in dirs:
        (base_path / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {dir_path}")


def copy_template_files(base_path: Path, book_title: str) -> None:
    """Copy and customize template files."""
    
    # Copy from references directory
    templates = {
        "agents/writing.agent.md": ".github/agents/writing.agent.md",
        "agents/writing-reviewer.agent.md": ".github/agents/writing-reviewer.agent.md",
        "agents/converter.agent.md": ".github/agents/converter.agent.md",
        "agents/orchestrator.agent.md": ".github/agents/orchestrator.agent.md",
        "instructions/writing.instructions.md": ".github/instructions/writing/writing.instructions.md",
        "instructions/writing-heading.instructions.md": ".github/instructions/writing/writing-heading.instructions.md",
        "instructions/writing-notation.instructions.md": ".github/instructions/writing/writing-notation.instructions.md",
        "instructions/commit-format.instructions.md": ".github/instructions/git/commit-format.instructions.md",
        "prompts/gc_Commit.prompt.md": ".github/prompts/gc_Commit.prompt.md",
        "prompts/gcp_Commit_Push.prompt.md": ".github/prompts/gcp_Commit_Push.prompt.md",
        "prompts/gpull.prompt.md": ".github/prompts/gpull.prompt.md",
        "docs/writing-guide.md": "docs/writing-guide.md",
        "docs/naming-conventions.md": "docs/naming-conventions.md",
        "docs/page-allocation.md": "docs/page-allocation.md",
        "docs/schedule.md": "docs/schedule.md",
        "copilot-instructions.md": ".github/copilot-instructions.md",
        "AGENTS.md": "AGENTS.md",
        "README.md": "README.md",
    }
    
    for src, dst in templates.items():
        src_path = REFERENCES_DIR / src
        dst_path = base_path / dst
        
        if src_path.exists():
            # Read, customize, and write
            content = src_path.read_text(encoding="utf-8")
            content = content.replace("{{BOOK_TITLE}}", book_title)
            content = content.replace("{{PROJECT_PATH}}", str(base_path))
            dst_path.write_text(content, encoding="utf-8")
            print(f"  ✅ Created: {dst}")
        else:
            print(f"  ⚠️ Template not found: {src}")


def copy_scripts(base_path: Path) -> None:
    """Copy utility scripts."""
    
    scripts = [
        "count_chars.py",
        "convert_md_to_review.py",
    ]
    
    for script in scripts:
        src_path = REFERENCES_DIR / "scripts" / script
        dst_path = base_path / "scripts" / script
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"  ✅ Copied: scripts/{script}")
        else:
            print(f"  ⚠️ Script not found: {script}")


def copy_assets(base_path: Path) -> None:
    """Copy static asset files."""
    
    assets = [
        (".gitignore", ".gitignore"),
    ]
    
    for src, dst in assets:
        src_path = ASSETS_DIR / src
        dst_path = base_path / dst
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"  ✅ Copied: {dst}")
        else:
            print(f"  ⚠️ Asset not found: {src}")


def create_chapter_intro_files(
    base_path: Path,
    chapters: List[str],
    prefix: str = "01"
) -> None:
    """Create initial chapter introduction files."""
    
    for i, chapter in enumerate(chapters):
        chapter_folder = f"{i}. {chapter}"
        
        # Create intro file in keypoints
        keypoints_file = base_path / f"01_contents_keyPoints/{chapter_folder}/{prefix}-{i}-0-00_{chapter}.md"
        keypoints_content = f"""# {chapter}

## Overview

(Write the overview of this chapter here)

## Key Points

- Point 1
- Point 2
- Point 3

## Sections

- a. Section A Title
- b. Section B Title
"""
        keypoints_file.write_text(keypoints_content, encoding="utf-8")
        
        # Create intro file in contents
        contents_file = base_path / f"02_contents/{chapter_folder}/{prefix}-{i}-0-00_{chapter}.md"
        contents_content = f"""# {chapter}

(Write the introduction paragraph here)
"""
        contents_file.write_text(contents_content, encoding="utf-8")
    
    print(f"  ✅ Created chapter intro files for {len(chapters)} chapters")


def main():
    parser = argparse.ArgumentParser(
        description="Set up a book writing workspace"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Project folder name (e.g., 'my-book-project')"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Book title (e.g., 'Introduction to Cloud Security')"
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Parent directory path (e.g., 'D:\\projects')"
    )
    parser.add_argument(
        "--chapters",
        type=int,
        default=8,
        help="Number of chapters (default: 8)"
    )
    parser.add_argument(
        "--chapter-titles",
        nargs="*",
        help="Custom chapter titles (space-separated)"
    )
    parser.add_argument(
        "--include-review",
        action="store_true",
        default=True,
        help="Include Re:VIEW output directory"
    )
    parser.add_argument(
        "--no-review",
        action="store_true",
        help="Exclude Re:VIEW output directory"
    )
    parser.add_argument(
        "--include-materials",
        action="store_true",
        default=True,
        help="Include materials directory"
    )
    parser.add_argument(
        "--no-materials",
        action="store_true",
        help="Exclude materials directory"
    )
    
    args = parser.parse_args()
    
    # Determine chapter titles
    if args.chapter_titles:
        chapters = args.chapter_titles
    else:
        # Default chapter structure
        chapters = [
            "Introduction",
        ]
        for i in range(1, args.chapters - 1):
            chapters.append(f"Chapter {i}")
        chapters.append("Conclusion")
    
    # Resolve options
    include_review = not args.no_review
    include_materials = not args.no_materials
    
    # Create base path
    base_path = Path(args.path) / args.name
    
    print(f"\n📚 Setting up Book Writing Workspace")
    print(f"   Project: {args.name}")
    print(f"   Title: {args.title}")
    print(f"   Location: {base_path}")
    print(f"   Chapters: {len(chapters)}")
    print(f"   Re:VIEW: {'Yes' if include_review else 'No'}")
    print(f"   Materials: {'Yes' if include_materials else 'No'}")
    print()
    
    # Check if directory exists
    if base_path.exists():
        print(f"❌ Error: Directory already exists: {base_path}")
        return 1
    
    # Create workspace
    print("📁 Creating directory structure...")
    create_directory_structure(base_path, chapters, include_review, include_materials)
    
    print("\n📄 Creating template files...")
    copy_template_files(base_path, args.title)
    
    print("\n📜 Copying utility scripts...")
    copy_scripts(base_path)
    
    print("\n📦 Copying asset files...")
    copy_assets(base_path)
    
    print("\n✏️ Creating chapter intro files...")
    create_chapter_intro_files(base_path, chapters)
    
    print(f"\n✅ Workspace created successfully at: {base_path}")
    print("\n📋 Next steps:")
    print(f"   1. cd \"{base_path}\"")
    print("   2. git init && git add . && git commit -m 'Initial commit'")
    print(f"   3. code \"{base_path}\"")
    print("   4. Edit docs/page-allocation.md to set word count targets")
    print("   5. Start writing in 01_contents_keyPoints/")
    
    return 0


if __name__ == "__main__":
    exit(main())
