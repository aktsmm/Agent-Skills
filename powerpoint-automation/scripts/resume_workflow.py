# -*- coding: utf-8 -*-
# =============================================================================
# Ag-ppt-create - AI-powered PPTX generation pipeline
# https://github.com/aktsmm/Ag-ppt-create
# 
# Copyright (c) aktsmm. Licensed under CC BY-NC-SA 4.0.
# DO NOT MODIFY THIS HEADER BLOCK.
# =============================================================================
"""
Resume workflow from a specific phase after escalation.

Usage:
    python scripts/resume_workflow.py <base_name> --from <phase>
    python scripts/resume_workflow.py <base_name> --from BUILD --skip-validation

Examples:
    # Resume from TRANSLATE phase
    python scripts/resume_workflow.py 20251214_purview_ignite --from TRANSLATE
    
    # Skip validation and go directly to BUILD
    python scripts/resume_workflow.py 20251214_purview_ignite --from BUILD --skip-validation
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

from workflow_tracer import WorkflowTracer


PHASES = ["INIT", "PLAN", "EXTRACT", "TRANSLATE", "REVIEW_JSON", "BUILD", "REVIEW_PPTX", "DONE"]


def load_escalation(base_name: str) -> dict:
    """Load escalation file if exists."""
    escalation_file = Path(f"output_manifest/{base_name}_escalation.json")
    if escalation_file.exists():
        with open(escalation_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def find_files(base_name: str) -> dict:
    """Find existing files for the workflow."""
    files = {
        "content": None,
        "content_ja": None,
        "pptx": None,
        "escalation": None,
        "trace": None,
    }
    
    manifest_dir = Path("output_manifest")
    output_dir = Path("output_ppt")
    
    # Check for content files
    content_path = manifest_dir / f"{base_name}_content.json"
    if content_path.exists():
        files["content"] = str(content_path)
    
    content_ja_path = manifest_dir / f"{base_name}_content_ja.json"
    if content_ja_path.exists():
        files["content_ja"] = str(content_ja_path)
    
    # Check for PPTX
    pptx_path = output_dir / f"{base_name}.pptx"
    if pptx_path.exists():
        files["pptx"] = str(pptx_path)
    
    # Check for escalation
    escalation_path = manifest_dir / f"{base_name}_escalation.json"
    if escalation_path.exists():
        files["escalation"] = str(escalation_path)
    
    # Check for trace
    trace_path = manifest_dir / f"{base_name}_trace.jsonl"
    if trace_path.exists():
        files["trace"] = str(trace_path)
    
    return files


def run_phase(phase: str, base_name: str, tracer: WorkflowTracer, 
              skip_validation: bool = False, template: str = None) -> bool:
    """
    Run a specific phase.
    
    Returns True if successful, False otherwise.
    """
    files = find_files(base_name)
    
    if phase == "TRANSLATE":
        tracer.start_phase("TRANSLATE")
        
        content_file = files.get("content")
        if not content_file:
            tracer.end_phase("TRANSLATE", status="failed", 
                           error="content.json not found")
            return False
        
        output_file = f"output_manifest/{base_name}_content_ja.json"
        
        # Translation requires Localizer agent (not automated script)
        tracer.end_phase("TRANSLATE", status="failed", 
                       error="TRANSLATE phase requires Localizer agent. "
                             "Script-based translation is deprecated. "
                             "Please use Localizer agent to translate content.json.")
        print("\n⚠️ TRANSLATE phase requires Localizer agent.")
        print(f"   Input:  {content_file}")
        print(f"   Output: {output_file}")
        print("\nPlease invoke Localizer agent to translate, then resume from REVIEW_JSON:")
        print(f"   python scripts/resume_workflow.py {base_name} --from REVIEW_JSON")
        return False
        return True
    
    elif phase == "REVIEW_JSON":
        if skip_validation:
            tracer.log("REVIEW_JSON", "warning", "Validation skipped by user")
            return True
        
        tracer.start_phase("REVIEW_JSON")
        
        content_ja_file = files.get("content_ja")
        if not content_ja_file:
            tracer.end_phase("REVIEW_JSON", status="failed",
                           error="content_ja.json not found")
            return False
        
        # Run validate_content.py
        cmd = ["python", "scripts/validate_content.py", content_ja_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 1:  # FAIL
            tracer.end_phase("REVIEW_JSON", status="failed",
                           error="Validation failed")
            return False
        elif result.returncode == 2:  # WARN
            tracer.end_phase("REVIEW_JSON", status="warning",
                           message="Validation passed with warnings")
        else:
            tracer.end_phase("REVIEW_JSON", status="success")
        
        return True
    
    elif phase == "BUILD":
        tracer.start_phase("BUILD")
        
        content_ja_file = files.get("content_ja")
        if not content_ja_file:
            tracer.end_phase("BUILD", status="failed",
                           error="content_ja.json not found")
            return False
        
        # Find template
        template_file = template
        if not template_file:
            # Try to find original PPTX in input/
            input_dir = Path("input")
            pptx_files = list(input_dir.glob("*.pptx"))
            if pptx_files:
                template_file = str(pptx_files[0])
            else:
                tracer.end_phase("BUILD", status="failed",
                               error="No template PPTX found")
                return False
        
        output_file = f"output_ppt/{base_name}.pptx"
        
        # Run create_from_template.py
        cmd = ["python", "scripts/create_from_template.py", 
               template_file, content_ja_file, output_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            tracer.end_phase("BUILD", status="failed",
                           error=result.stderr[:500])
            return False
        
        tracer.end_phase("BUILD", status="success", output_file=output_file)
        return True
    
    elif phase == "DONE":
        tracer.log("DONE", "success", "Workflow completed")
        
        # Mark escalation as resolved
        escalation_file = Path(f"output_manifest/{base_name}_escalation.json")
        if escalation_file.exists():
            with open(escalation_file, "r", encoding="utf-8") as f:
                escalation = json.load(f)
            escalation["status"] = "resolved"
            escalation["resolved_at"] = datetime.now().isoformat()
            with open(escalation_file, "w", encoding="utf-8") as f:
                json.dump(escalation, f, indent=2, ensure_ascii=False)
        
        # Open PPTX
        pptx_file = files.get("pptx")
        if pptx_file:
            print(f"\n🎉 PPTX generated: {pptx_file}")
            print(f"   Opening in PowerPoint...")
            subprocess.run(["start", pptx_file], shell=True)
        
        return True
    
    else:
        print(f"Phase {phase} not implemented in resume script")
        return False


def main():
    parser = argparse.ArgumentParser(description="Resume workflow from a specific phase")
    parser.add_argument("base_name", help="Base name of the workflow")
    parser.add_argument("--from", dest="from_phase", required=True,
                       choices=PHASES, help="Phase to resume from")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip REVIEW_JSON phase")
    parser.add_argument("--template", help="Template PPTX file path")
    
    args = parser.parse_args()
    
    base_name = args.base_name
    from_phase = args.from_phase
    
    print(f"\n📋 Resuming workflow: {base_name}")
    print(f"   From phase: {from_phase}")
    
    # Check for escalation
    escalation = load_escalation(base_name)
    if escalation:
        print(f"   Previous escalation: {escalation.get('phase')} - {escalation.get('reason')}")
    
    # Check existing files
    files = find_files(base_name)
    print(f"\n📁 Found files:")
    for key, path in files.items():
        if path:
            print(f"   {key}: {path}")
    
    # Initialize tracer
    tracer = WorkflowTracer(base_name)
    tracer.log("RESUME", "started", f"Resuming from {from_phase}")
    
    # Determine phases to run
    start_idx = PHASES.index(from_phase)
    phases_to_run = PHASES[start_idx:]
    
    print(f"\n🚀 Phases to run: {' → '.join(phases_to_run)}")
    
    # Run phases
    for phase in phases_to_run:
        if phase == "INIT" or phase == "PLAN" or phase == "EXTRACT":
            print(f"   Skipping {phase} (already completed)")
            continue
        
        skip_val = args.skip_validation and phase == "REVIEW_JSON"
        success = run_phase(phase, base_name, tracer, skip_val, args.template)
        
        if not success:
            print(f"\n❌ Phase {phase} failed. Check trace for details.")
            tracer.save()
            sys.exit(1)
    
    tracer.save()
    print("\n✅ Workflow resumed and completed successfully!")


if __name__ == "__main__":
    main()
