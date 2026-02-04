# -*- coding: utf-8 -*-
# =============================================================================
# Ag-ppt-create - AI-powered PPTX generation pipeline
# https://github.com/aktsmm/Ag-ppt-create
# 
# Copyright (c) aktsmm. Licensed under CC BY-NC-SA 4.0.
# DO NOT MODIFY THIS HEADER BLOCK.
# =============================================================================
"""
Summarize content.json by understanding full context and restructuring.

Unlike extract_main_slides.py which mechanically filters slides,
this script is designed to work WITH an AI agent that:
1. Reads ALL slides to understand the full narrative
2. Identifies key sections and messages
3. Restructures into a coherent summary with specified slide count

This script provides helper functions for the AI agent workflow.

Usage:
    # Analyze mode: Output structure analysis for AI to process
    python scripts/summarize_content.py analyze <input_content.json>
    
    # Validate mode: Check if summary content.json is valid
    python scripts/summarize_content.py validate <summary_content.json>

AI Agent Workflow:
    1. Run: python scripts/summarize_content.py analyze content.json
    2. AI reads full content and analysis output
    3. AI creates summarized content_summary.json (target slides)
    4. Run: python scripts/summarize_content.py validate content_summary.json
    5. Build PPTX from summary
"""

import json
import sys
import io
import argparse
from pathlib import Path
from collections import Counter

# Fix Windows console encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def analyze_content(input_path: str) -> dict:
    """
    Analyze content.json and output structure for AI agent.
    
    Returns a summary of:
    - Total slides and types
    - Section structure
    - Key themes/topics from titles and notes
    - Recommended summary structure
    """
    with open(input_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    
    slides = content.get("slides", [])
    total = len(slides)
    
    # Count slide types
    type_counts = Counter(slide.get("type", "unknown") for slide in slides)
    
    # Identify sections
    sections = []
    current_section = {"name": "Introduction", "slides": [], "start": 0}
    
    for i, slide in enumerate(slides):
        slide_type = slide.get("type", "")
        title = slide.get("title", "")
        
        # Section break detection
        if slide_type == "section" or (slide_type == "title" and i > 0):
            if current_section["slides"]:
                current_section["end"] = i - 1
                current_section["count"] = len(current_section["slides"])
                sections.append(current_section)
            current_section = {
                "name": title or f"Section {len(sections) + 1}",
                "slides": [],
                "start": i
            }
        
        current_section["slides"].append({
            "index": i + 1,
            "type": slide_type,
            "title": title[:50] + "..." if len(title) > 50 else title,
            "has_notes": bool(slide.get("notes")),
            "has_image": bool(slide.get("image")),
            "items_count": len(slide.get("items", []))
        })
    
    # Add last section
    if current_section["slides"]:
        current_section["end"] = total - 1
        current_section["count"] = len(current_section["slides"])
        sections.append(current_section)
    
    # Extract key topics from titles
    all_titles = [s.get("title", "") for s in slides if s.get("title")]
    
    # Calculate recommended summary sizes
    recommendations = {
        "executive_summary": max(7, total // 20),  # ~5% of slides
        "short_summary": max(15, total // 8),      # ~12% of slides
        "standard_summary": max(25, total // 4),   # ~25% of slides
        "detailed_summary": max(40, total // 2),   # ~50% of slides
    }
    
    # Count empty slides (notes-only or blank)
    empty_slides = []
    for i, slide in enumerate(slides):
        slide_type = slide.get("type", "")
        has_title = bool(slide.get("title", "").strip())
        has_items = bool(slide.get("items") or slide.get("bullets") or slide.get("content"))
        has_image = bool(slide.get("image"))
        has_notes = bool(slide.get("notes", "").strip())
        
        # Notes-only = empty
        if has_notes and not has_title and not has_items and not has_image:
            empty_slides.append({"index": i + 1, "reason": "notes_only"})
        # Completely blank
        elif not has_title and not has_items and not has_image and not has_notes:
            empty_slides.append({"index": i + 1, "reason": "blank"})
    
    # Check for agenda slide
    has_agenda = any(
        slide.get("type") == "agenda" or 
        any(kw in (slide.get("title") or "").lower() for kw in ["agenda", "目次", "outline", "contents", "アジェンダ"])
        for slide in slides
    )
    
    analysis = {
        "source": {
            "file": input_path,
            "title": content.get("title", ""),
            "total_slides": total,
            "slide_types": dict(type_counts),
            "empty_slides": empty_slides,
            "has_agenda": has_agenda,
        },
        "source": {
            "file": input_path,
            "title": content.get("title", ""),
            "total_slides": total,
            "slide_types": dict(type_counts)
        },
        "sections": [
            {
                "name": s["name"],
                "slide_range": f"{s['start'] + 1}-{s['end'] + 1}",
                "slide_count": s["count"],
                "key_slides": [
                    sl for sl in s["slides"] 
                    if sl["type"] in ("title", "section", "content") or sl["has_notes"]
                ][:5]  # Top 5 key slides per section
            }
            for s in sections
        ],
        "recommendations": recommendations,
        "instructions": {
            "mandatory": [
                "★ MUST include Agenda slide (type='agenda') after title slide",
                "★ MUST include Summary/Conclusion slide before closing",
                "★ EXCLUDE empty slides (notes-only or blank) - they are useless",
                "★ Every content slide MUST have visible content (title + items)",
                "★ Screenshot slides: short title + large image + detailed notes",
            ],
            "workflow": [
                "1. Read the full content.json to understand the complete narrative",
                "2. EXCLUDE empty slides (notes-only slides are NOT useful)",
                "3. Identify the main storyline and key messages",
                "4. Group related slides into logical sections",
                "5. For each section, extract essential points (not just copy slides)",
                "6. Create Agenda slide (type='agenda') listing main sections",
                "7. Create new slides that SUMMARIZE the section content",
                "8. Ensure smooth narrative flow between sections",
                "9. Include Summary slide before closing",
                "10. Speaker notes should summarize, not copy original"
            ],
            "guidelines": [
                "Do NOT just filter/remove slides - restructure and summarize",
                "Do NOT include slides with only speaker notes (no visible content)",
                "Combine related content from multiple slides into single slides",
                "Preserve key statistics, quotes, and data points",
                "Maintain product names in English (Microsoft Purview, Azure, etc.)",
                "Keep section transitions clear",
                "Summarize speaker notes, don't just copy or drop them"
            ],
            "image_handling": [
                "Keep original image size proportions",
                "Do NOT enlarge small images (causes blurry output)",
                "DYNAMIC SIZING based on text content:",
                "  - If slide has bullet items: width_percent 30-45 (image on right)",
                "  - If slide has only title (no bullets): width_percent 60-80 (larger image)",
                "  - For screenshots with UI details: prefer larger size for readability",
                "For small icons/logos, use 'width_percent': 20-30",
                "Only full-screen for high-resolution photos",
                "★ Screenshot slides: put detailed explanation in speaker NOTES, not title"
            ]
        }
    }
    
    return analysis


def validate_summary(summary_path: str) -> dict:
    """
    Validate a summary content.json file.
    
    Checks:
    - JSON validity
    - Required fields
    - Slide structure
    - Content presence
    - Agenda slide exists
    - No empty slides (notes-only)
    """
    errors = []
    warnings = []
    
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            content = json.load(f)
    except json.JSONDecodeError as e:
        return {"valid": False, "errors": [f"JSON parse error: {e}"], "warnings": []}
    
    # Check required fields
    if "slides" not in content:
        errors.append("Missing 'slides' array")
        return {"valid": False, "errors": errors, "warnings": warnings}
    
    slides = content.get("slides", [])
    
    if not slides:
        errors.append("Empty slides array")
    
    # Validate each slide
    valid_types = {"title", "section", "content", "two_column", "photo", "agenda", "closing", "blank", "summary"}
    has_agenda = False
    has_summary = False
    empty_slide_indices = []
    
    for i, slide in enumerate(slides):
        slide_num = i + 1
        
        # Check type
        slide_type = slide.get("type")
        if not slide_type:
            errors.append(f"Slide {slide_num}: Missing 'type' field")
        elif slide_type not in valid_types:
            warnings.append(f"Slide {slide_num}: Unusual type '{slide_type}'")
        
        # Track agenda and summary
        if slide_type == "agenda":
            has_agenda = True
        if slide_type == "summary" or "まとめ" in (slide.get("title") or "").lower() or "summary" in (slide.get("title") or "").lower():
            has_summary = True
        
        # Check content slides have items
        if slide_type == "content":
            if not slide.get("items") and not slide.get("bullets"):
                errors.append(f"Slide {slide_num}: Content slide without items/bullets")
        
        # Check title presence for most types
        if slide_type in ("content", "section", "two_column") and not slide.get("title"):
            warnings.append(f"Slide {slide_num}: {slide_type} slide without title")
        
        # Detect empty slides (notes-only)
        has_title = bool(slide.get("title", "").strip())
        has_items = bool(slide.get("items") or slide.get("bullets") or slide.get("content"))
        has_image = bool(slide.get("image"))
        has_notes = bool(slide.get("notes", "").strip())
        
        if has_notes and not has_title and not has_items and not has_image:
            errors.append(f"Slide {slide_num}: EMPTY (only speaker notes - no visible content)")
            empty_slide_indices.append(slide_num)
        elif not has_title and not has_items and not has_image and not has_notes:
            warnings.append(f"Slide {slide_num}: Blank slide (no content at all)")
            empty_slide_indices.append(slide_num)
    
    # Check for narrative flow
    if slides:
        first_type = slides[0].get("type")
        if first_type not in ("title", "section"):
            warnings.append("First slide should be 'title' or 'section' type")
        
        last_type = slides[-1].get("type")
        if last_type not in ("closing", "section", "content", "summary"):
            warnings.append("Last slide should be 'closing', 'section', 'content', or 'summary'")
    
    # Mandatory checks
    if not has_agenda:
        errors.append("Missing Agenda slide (type='agenda' or title containing 'agenda/目次')")
    
    if not has_summary and len(slides) > 5:
        warnings.append("Consider adding a Summary/まとめ slide before closing")
    
    if empty_slide_indices:
        errors.append(f"Found {len(empty_slide_indices)} empty slides that should be removed: {empty_slide_indices}")
    
    return {
        "valid": len(errors) == 0,
        "slide_count": len(slides),
        "has_agenda": has_agenda,
        "has_summary": has_summary,
        "errors": errors,
        "warnings": warnings
    }


def print_analysis(analysis: dict) -> None:
    """Pretty print analysis for AI agent."""
    print("\n" + "=" * 60)
    print("CONTENT ANALYSIS FOR AI SUMMARIZATION")
    print("=" * 60)
    
    src = analysis["source"]
    print(f"\n📄 Source: {src['file']}")
    print(f"   Title: {src['title']}")
    print(f"   Total Slides: {src['total_slides']}")
    print(f"   Types: {src['slide_types']}")
    
    # Show empty slides warning
    if src.get('empty_slides'):
        print(f"\n⚠️  Empty Slides Found ({len(src['empty_slides'])}): MUST EXCLUDE THESE")
        for empty in src['empty_slides']:
            reason = "notes-only" if empty['reason'] == 'notes_only' else "blank"
            print(f"   - Slide {empty['index']}: {reason}")
    
    # Agenda check
    if not src.get('has_agenda'):
        print(f"\n❌ No Agenda slide found - YOU MUST ADD ONE!")
    else:
        print(f"\n✅ Agenda slide exists")
    
    print(f"\n📑 Sections ({len(analysis['sections'])}):")  
    for sec in analysis["sections"]:
        print(f"\n   [{sec['slide_range']}] {sec['name']} ({sec['slide_count']} slides)")
        for sl in sec["key_slides"][:3]:
            icon = "📷" if sl["has_image"] else "📝" if sl["has_notes"] else "  "
            print(f"      {icon} {sl['index']:3d}. [{sl['type']:12s}] {sl['title']}")
    
    print(f"\n📊 Recommended Summary Sizes:")
    for name, count in analysis["recommendations"].items():
        label = name.replace("_", " ").title()
        print(f"   {label}: {count} slides")
    
    # Print mandatory rules first
    print(f"\n🚨 MANDATORY RULES:")
    for rule in analysis["instructions"]["mandatory"]:
        print(f"   {rule}")
    
    print(f"\n📋 Summarization Instructions:")
    for step in analysis["instructions"]["workflow"]:
        print(f"   {step}")
    
    print(f"\n⚠️  Guidelines:")
    for guideline in analysis["instructions"]["guidelines"]:
        print(f"   • {guideline}")
    
    print(f"\n🖼️  Image Handling:")
    for rule in analysis["instructions"]["image_handling"]:
        print(f"   • {rule}")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize content.json with AI agent assistance"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", 
        help="Analyze content.json structure for AI summarization"
    )
    analyze_parser.add_argument("input", help="Input content.json path")
    analyze_parser.add_argument(
        "--json", 
        action="store_true", 
        help="Output as JSON instead of formatted text"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a summary content.json file"
    )
    validate_parser.add_argument("input", help="Summary content.json to validate")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        analysis = analyze_content(args.input)
        if args.json:
            print(json.dumps(analysis, ensure_ascii=False, indent=2))
        else:
            print_analysis(analysis)
    
    elif args.command == "validate":
        result = validate_summary(args.input)
        if result["valid"]:
            print(f"✅ Valid summary with {result['slide_count']} slides")
            if result.get("has_agenda"):
                print(f"   ✅ Has Agenda slide")
            if result.get("has_summary"):
                print(f"   ✅ Has Summary slide")
        else:
            print("❌ Invalid summary:")
            for err in result["errors"]:
                print(f"   ERROR: {err}")
        
        for warn in result.get("warnings", []):
            print(f"   ⚠️  {warn}")
        
        sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
