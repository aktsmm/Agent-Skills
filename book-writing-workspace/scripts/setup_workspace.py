#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Writing Workspace Setup Script

Creates a complete book writing workspace with:
- Directory structure for manuscripts, images, materials
- AI agent configurations
- Writing instructions and guidelines
- Utility scripts

Usage:
    python setup_workspace.py --name "my-book" --title "My Book Title" --path "D:\\projects"
"""

import argparse
import shutil
from pathlib import Path
from typing import List

# Script location (for finding templates)
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
ASSETS_DIR = SKILL_DIR / "assets"


def create_directory_structure(
    base_path: Path,
    chapters: List[str],
    include_review: bool = False,
    include_materials: bool = True
) -> None:
    """Create the complete directory structure."""
    
    # Main content directories
    dirs = [
        ".github/agents",
        ".github/instructions/writing",
        "docs",
        "docs/templates",
        "scripts",
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
            "config/review-metadata",
            "03_re-view_output/output_re",
            "03_re-view_output/output_pdf",
            "03_re-view_output/images",
            "03_re-view_output/sty",
        ])
    
    # Optional: Materials
    if include_materials:
        dirs.extend([
            "99_material/references",
        ])
    
    # Create all directories
    for dir_path in dirs:
        (base_path / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {dir_path}")


def copy_template_files(base_path: Path, book_title: str, include_review: bool = False) -> None:
    """Copy and customize template files."""
    
    # Copy from references directory
    templates = {
        "agents/writing.agent.md": ".github/agents/writing.agent.md",
        "agents/writing-reviewer.agent.md": ".github/agents/writing-reviewer.agent.md",
        "instructions/writing.instructions.md": ".github/instructions/writing/writing.instructions.md",
        "instructions/writing-heading.instructions.md": ".github/instructions/writing/writing-heading.instructions.md",
        "instructions/writing-notation.instructions.md": ".github/instructions/writing/writing-notation.instructions.md",
        "docs/writing-guide.md": "docs/writing-guide.md",
        "docs/naming-conventions.md": "docs/naming-conventions.md",
        "docs/page-allocation.md": "docs/page-allocation.md",
        "docs/schedule.md": "docs/schedule.md",
        "docs/templates/template-chapter-intro.md": "docs/templates/template-chapter-intro.md",
        "docs/templates/template-section.md": "docs/templates/template-section.md",
        "copilot-instructions.md": ".github/copilot-instructions.md",
        "AGENTS.md": "AGENTS.md",
        "README.md": "README.md",
    }
    
    for src, dst in templates.items():
        src_path = TEMPLATES_DIR / src
        dst_path = base_path / dst
        
        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            # Read, customize, and write
            content = src_path.read_text(encoding="utf-8")
            content = content.replace("{{BOOK_TITLE}}", book_title)
            content = content.replace("{{PROJECT_PATH}}", str(base_path))
            dst_path.write_text(content, encoding="utf-8")
            print(f"  ✅ Created: {dst}")
        else:
            print(f"  ⚠️ Template not found: {src}")

    review_templates = {}
    if include_review:
        review_templates = {
            "agents/converter.agent.md": ".github/agents/converter.agent.md",
            "custom-titlepage.tex": "03_re-view_output/custom-titlepage.tex",
            "review-ext.rb": "03_re-view_output/review-ext.rb",
            "sty/review-custom.sty": "03_re-view_output/sty/review-custom.sty",
            "sty/review-style.sty": "03_re-view_output/sty/review-style.sty",
            "review-metadata/common.yml": "config/review-metadata/common.yml",
            "review-metadata/project.yml": "config/review-metadata/project.yml",
        }

    for src, dst in review_templates.items():
        src_path = TEMPLATES_DIR / src
        dst_path = base_path / dst
        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            content = src_path.read_text(encoding="utf-8")
            content = content.replace("{{BOOK_TITLE}}", book_title)
            dst_path.write_text(content, encoding="utf-8")
            print(f"  ✅ Created: {dst}")
        else:
            print(f"  ⚠️ Template not found: {src}")


def copy_scripts(base_path: Path, include_review: bool = False) -> None:
    """Copy utility scripts."""
    
    scripts = [
        "count_chars.py",
    ]
    if include_review:
        scripts.extend([
            "convert_md_to_review.py",
            "build_review_pdf.py",
            "inspect_pdf.py",
            "review_metadata.py",
        ])
    
    for script in scripts:
        src_path = TEMPLATES_DIR / "scripts" / script
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
) -> None:
    """Create initial chapter introduction files."""
    
    for i, chapter in enumerate(chapters):
        chapter_folder = f"{i}. {chapter}"
        
        # Create intro file in keypoints
        keypoints_file = base_path / f"01_contents_keyPoints/{chapter_folder}/ch{i}-00_{chapter}.md"
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
        contents_file = base_path / f"02_contents/{chapter_folder}/ch{i}-00_{chapter}.md"
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
        "--with-review",
        "--include-review",
        dest="include_review",
        action="store_true",
        help="Include optional Re:VIEW/PDF scaffolding"
    )
    parser.add_argument(
        "--no-review",
        dest="include_review",
        action="store_false",
        help="Exclude Re:VIEW/PDF scaffolding"
    )
    parser.set_defaults(include_review=False)
    parser.add_argument(
        "--with-materials",
        "--include-materials",
        dest="include_materials",
        action="store_true",
        help="Include a reference materials directory"
    )
    parser.add_argument(
        "--no-materials",
        dest="include_materials",
        action="store_false",
        help="Exclude reference materials directory"
    )
    parser.set_defaults(include_materials=True)

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
    include_review = args.include_review
    include_materials = args.include_materials
    
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
    copy_template_files(base_path, args.title, include_review)
    
    print("\n📜 Copying utility scripts...")
    copy_scripts(base_path, include_review)
    
    print("\n📦 Copying asset files...")
    copy_assets(base_path)
    
    print("\n✏️ Creating chapter intro files...")
    create_chapter_intro_files(base_path, chapters)
    
    print(f"\n✅ Workspace created successfully at: {base_path}")
    print("\n📋 Next steps:")
    print(f"   1. cd \"{base_path}\"")
    print(f"   2. code \"{base_path}\"")
    print("   3. Edit docs/page-allocation.md to set word count targets")
    print("   4. Start writing in 01_contents_keyPoints/")
    print("   5. Follow your repository's existing Git workflow when saving changes")
    
    return 0


if __name__ == "__main__":
    exit(main())
