# -*- coding: utf-8 -*-
"""
Character Counter Script

Count characters in Markdown files under 02_contents/.
Excludes Markdown syntax (headings, code blocks, links, etc.)

Usage:
    python scripts/count_chars.py [path]

Arguments:
    path    Optional. Specific folder to count (default: 02_contents/)
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict


def clean_markdown(text: str) -> str:
    """Remove Markdown syntax, keep only prose content."""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    # Remove heading markers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # Remove table syntax
    text = re.sub(r'\|', '', text)
    text = re.sub(r'^[-:]+$', '', text, flags=re.MULTILINE)
    # Remove list markers
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Remove links (keep text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove images
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    # Remove whitespace
    text = re.sub(r'[\s\r\n\t　]', '', text)
    return text


def get_file_type(filename: str) -> tuple:
    """Determine file type and target range."""
    if 'Column' in filename or 'コラム' in filename:
        return 'Column', '2,000-3,000'
    elif re.match(r'^\d+-\d+-0-00', filename):
        return 'Intro', '300-500'
    else:
        return 'Main', '3,000-5,000'


def check_status(char_count: int, file_type: str) -> str:
    """Check if count is within acceptable range."""
    ranges = {
        'Column': (1500, 3500),
        'Intro': (200, 700),
        'Main': (2000, 6000)
    }
    min_val, max_val = ranges.get(file_type, (2000, 6000))
    
    if char_count < min_val:
        return '⚠️ Under'
    elif char_count > max_val:
        return '⚠️ Over'
    else:
        return '✅ OK'


def main():
    # Determine base path
    if len(sys.argv) > 1:
        base_path = Path(sys.argv[1])
    else:
        # Find 02_contents in current or parent directories
        cwd = Path.cwd()
        if (cwd / "02_contents").exists():
            base_path = cwd / "02_contents"
        elif (cwd.parent / "02_contents").exists():
            base_path = cwd.parent / "02_contents"
        else:
            print("❌ Error: Could not find 02_contents/ folder")
            print("Usage: python count_chars.py [path]")
            return 1
    
    if not base_path.exists():
        print(f"❌ Error: Path not found: {base_path}")
        return 1
    
    results = []
    chapter_totals = defaultdict(lambda: {'count': 0, 'files': 0})
    
    # Find all Markdown files
    for md_file in sorted(base_path.rglob("*.md")):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        clean_content = clean_markdown(content)
        char_count = len(clean_content)
        
        relative_path = md_file.relative_to(base_path)
        parts = str(relative_path).replace('\\', '/').split('/')
        chapter = parts[0] if parts else 'Unknown'
        
        file_type, target = get_file_type(md_file.name)
        status = check_status(char_count, file_type)
        
        results.append({
            'chapter': chapter,
            'filename': md_file.name,
            'file_type': file_type,
            'char_count': char_count,
            'target': target,
            'status': status,
            'relative_path': str(relative_path)
        })
        
        chapter_totals[chapter]['count'] += char_count
        chapter_totals[chapter]['files'] += 1
    
    # Print chapter summary
    print("## Chapter Summary\n")
    print("| Chapter | Files | Characters | Status |")
    print("|:--------|------:|-----------:|:-------|")
    
    total_chars = 0
    total_files = 0
    
    for chapter in sorted(chapter_totals.keys()):
        data = chapter_totals[chapter]
        total_chars += data['count']
        total_files += data['files']
        
        if data['count'] < 5000:
            note = '⚠️ Under (in progress?)'
        elif data['count'] < 15000:
            note = 'Low'
        elif data['count'] > 40000:
            note = '⚠️ Over'
        else:
            note = '✅ OK'
        
        print(f"| {chapter} | {data['files']} | {data['count']:,} | {note} |")
    
    print(f"\n## Total\n")
    print(f"- Total files: {total_files}")
    print(f"- Total characters: **{total_chars:,}**")
    
    # Print issues
    issues = [r for r in results if '⚠️' in r['status']]
    if issues:
        print(f"\n## Issues ({len(issues)} files)\n")
        print("| File | Type | Count | Target | Status |")
        print("|:-----|:----:|------:|:-------|:------:|")
        for r in issues:
            print(f"| {r['relative_path']} | {r['file_type']} | {r['char_count']:,} | {r['target']} | {r['status']} |")
    
    return 0


if __name__ == "__main__":
    exit(main())
