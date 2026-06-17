# -*- coding: utf-8 -*-
# =============================================================================
# Ag-ppt-create - AI-powered PPTX generation pipeline
# https://github.com/aktsmm/Ag-ppt-create
# 
# Copyright (c) aktsmm. Licensed under CC BY-NC-SA 4.0.
# DO NOT MODIFY THIS HEADER BLOCK.
# =============================================================================
"""
Workflow tracer for observability and debugging.

Provides structured logging for each phase of the PPTX generation workflow.
Logs are appended to {base}_trace.jsonl for post-mortem analysis.

Usage:
    from workflow_tracer import WorkflowTracer
    
    tracer = WorkflowTracer("20251214_example_report")
    tracer.start_phase("EXTRACT")
    # ... do work ...
    tracer.end_phase("EXTRACT", status="success", metrics={"slides": 45})
    tracer.save()

Trace file format (JSONL):
    {"trace_id": "...", "phase": "INIT", "status": "success", ...}
    {"trace_id": "...", "phase": "EXTRACT", "status": "success", ...}
"""

import json
import sys
import io
import uuid
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

# Fix Windows console encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class WorkflowTracer:
    """
    Trace workflow execution for observability.
    """
    
    PHASES = [
        "INIT",
        "PLAN", 
        "PREPARE_TEMPLATE",  # Template diagnosis & cleaning
        "EXTRACT",
        "SUMMARIZE",         # Summarizer agent phase
        "TRANSLATE",
        "REVIEW_JSON",
        "BUILD",
        "REVIEW_PPTX",
        "DONE",
        "ESCALATE"
    ]
    
    def __init__(self, base_name: str, output_dir: str = "output_manifest"):
        """
        Initialize tracer.
        
        Args:
            base_name: Base name for the workflow (e.g., "20251214_example_report")
            output_dir: Directory to save trace file
        """
        self.base_name = base_name
        self.trace_id = f"{base_name}_{uuid.uuid4().hex[:8]}"
        self.output_dir = Path(output_dir)
        self.trace_file = self.output_dir / f"{base_name}_trace.jsonl"
        self.entries: List[Dict[str, Any]] = []
        self.current_phase: Optional[str] = None
        self.phase_start_time: Optional[datetime] = None
        self.retry_counts: Dict[str, int] = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, phase: str, status: str, message: str = "", 
            metrics: Optional[Dict[str, Any]] = None,
            input_file: str = "", output_file: str = "",
            error: str = "") -> Dict[str, Any]:
        """
        Log a trace entry.
        
        Args:
            phase: Workflow phase (INIT, PLAN, EXTRACT, etc.)
            status: Status (started, success, failed, warning, escalated)
            message: Human-readable message
            metrics: Optional metrics dictionary
            input_file: Input file for this phase
            output_file: Output file for this phase
            error: Error message if failed
            
        Returns:
            The logged entry dictionary
        """
        entry = {
            "trace_id": self.trace_id,
            "base_name": self.base_name,
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "status": status,
            "message": message,
        }
        
        if input_file:
            entry["input"] = input_file
        if output_file:
            entry["output"] = output_file
        if metrics:
            entry["metrics"] = metrics
        if error:
            entry["error"] = error
        if phase in self.retry_counts:
            entry["retry_count"] = self.retry_counts[phase]
        
        self.entries.append(entry)
        
        # Also print to console
        status_icon = {
            "started": "🚀",
            "success": "✅",
            "failed": "❌",
            "warning": "⚠️",
            "escalated": "🆘",
        }.get(status, "ℹ️")
        
        print(f"{status_icon} [{phase}] {status}: {message}")
        
        return entry
    
    def start_phase(self, phase: str, input_file: str = "", message: str = "") -> None:
        """Start a new phase."""
        self.current_phase = phase
        self.phase_start_time = datetime.now()
        self.log(phase, "started", message or f"Starting {phase} phase", input_file=input_file)
    
    def end_phase(self, phase: str, status: str = "success", 
                  output_file: str = "", message: str = "",
                  metrics: Optional[Dict[str, Any]] = None,
                  error: str = "") -> None:
        """End the current phase."""
        duration_ms = 0
        if self.phase_start_time:
            duration_ms = int((datetime.now() - self.phase_start_time).total_seconds() * 1000)
        
        final_metrics = metrics or {}
        final_metrics["duration_ms"] = duration_ms
        
        self.log(
            phase, status, 
            message or f"{phase} phase completed",
            metrics=final_metrics,
            output_file=output_file,
            error=error
        )
        
        self.current_phase = None
        self.phase_start_time = None
    
    def record_retry(self, phase: str, reason: str, retry_num: int) -> None:
        """Record a retry attempt."""
        self.retry_counts[phase] = retry_num
        self.log(
            phase, "warning",
            f"Retry #{retry_num}: {reason}",
            metrics={"retry_number": retry_num}
        )
    
    def escalate(self, phase: str, reason: str, retry_count: int = 0) -> Dict[str, Any]:
        """
        Record escalation to human.
        
        Creates escalation file for resumption.
        """
        entry = self.log(
            phase, "escalated",
            f"Escalated to human: {reason}",
            metrics={"total_retries": retry_count},
            error=reason
        )
        
        # Create escalation file
        escalation_file = self.output_dir / f"{self.base_name}_escalation.json"
        escalation_data = {
            "trace_id": self.trace_id,
            "base_name": self.base_name,
            "escalated_at": datetime.now().isoformat(),
            "phase": phase,
            "reason": reason,
            "retry_count": retry_count,
            "resume_command": f"python scripts/resume_workflow.py {self.base_name} --from {phase}",
            "status": "pending_human_action"
        }
        
        with open(escalation_file, "w", encoding="utf-8") as f:
            json.dump(escalation_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n🆘 ESCALATION: {reason}")
        print(f"   Escalation file: {escalation_file}")
        print(f"   Resume with: {escalation_data['resume_command']}")
        
        return entry
    
    def save(self) -> None:
        """Save trace entries to JSONL file."""
        with open(self.trace_file, "a", encoding="utf-8") as f:
            for entry in self.entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        # Clear saved entries
        saved_count = len(self.entries)
        self.entries = []
        print(f"📝 Trace saved: {self.trace_file} ({saved_count} entries)")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the workflow execution."""
        # Read all entries from file
        all_entries = []
        if self.trace_file.exists():
            with open(self.trace_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        all_entries.append(json.loads(line))
        
        # Add current unsaved entries
        all_entries.extend(self.entries)
        
        # Calculate summary
        phases_completed = set()
        total_duration = 0
        errors = []
        
        for entry in all_entries:
            if entry.get("status") == "success":
                phases_completed.add(entry.get("phase"))
            if entry.get("metrics", {}).get("duration_ms"):
                total_duration += entry["metrics"]["duration_ms"]
            if entry.get("error"):
                errors.append(entry["error"])
        
        return {
            "trace_id": self.trace_id,
            "base_name": self.base_name,
            "phases_completed": list(phases_completed),
            "total_duration_ms": total_duration,
            "total_entries": len(all_entries),
            "errors": errors,
            "has_escalation": any(e.get("status") == "escalated" for e in all_entries)
        }


def create_tracer_for_script(base_name: str) -> WorkflowTracer:
    """
    Convenience function to create a tracer for a script.
    
    Usage in scripts:
        from workflow_tracer import create_tracer_for_script
        tracer = create_tracer_for_script("20251214_example")
        tracer.start_phase("EXTRACT")
        # ... work ...
        tracer.end_phase("EXTRACT", status="success")
        tracer.save()
    """
    return WorkflowTracer(base_name)


# Example usage
if __name__ == "__main__":
    # Demo usage
    tracer = WorkflowTracer("20251214_demo_report")
    
    tracer.start_phase("INIT", message="Initializing workflow")
    tracer.end_phase("INIT", status="success", metrics={"input_type": "pptx_en"})
    
    tracer.start_phase("EXTRACT", input_file="input/demo.pptx")
    tracer.end_phase("EXTRACT", status="success", 
                     output_file="output_manifest/20251214_demo_report_content.json",
                     metrics={"slides_extracted": 45, "images_extracted": 12})
    
    tracer.start_phase("TRANSLATE")
    tracer.record_retry("TRANSLATE", "Rate limit exceeded", 1)
    tracer.end_phase("TRANSLATE", status="success",
                     output_file="output_manifest/20251214_demo_report_content_ja.json",
                     metrics={"slides_translated": 45})
    
    tracer.save()
    
    print("\n📊 Summary:")
    print(json.dumps(tracer.get_summary(), indent=2, ensure_ascii=False))
