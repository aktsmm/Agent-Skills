#!/usr/bin/env python3
"""
validate_drawio.py - Validate draw.io file mxCell structure

Usage:
    python validate_drawio.py <file.drawio>
    python validate_drawio.py <directory>

Checks:
- mxfile generator attribute
- Root cells (id=0, id=1) exist
- mxCell count >= 2 + vertices + edges
- Edge source/target references valid
"""

import xml.etree.ElementTree as ET
import sys
import os
from pathlib import Path


def validate_drawio(filepath: str) -> dict:
    """Validate a single .drawio file and return results."""
    result = {
        "file": os.path.basename(filepath),
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {}
    }
    
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as e:
        result["valid"] = False
        result["errors"].append(f"XML parse error: {e}")
        return result
    
    # Check generator attribute
    generator = root.get("generator", "")
    result["stats"]["generator"] = generator or "(not set)"
    if not generator:
        result["warnings"].append("generator attribute not set in mxfile")
    
    # Find all mxCells
    cells = root.findall(".//mxCell")
    cell_ids = {c.get("id") for c in cells}
    
    # Check for duplicate IDs
    from collections import Counter
    all_ids = [c.get("id") for c in cells if c.get("id")]
    id_counts = Counter(all_ids)
    duplicates = [id_ for id_, count in id_counts.items() if count > 1]
    if duplicates:
        result["valid"] = False
        result["errors"].append(
            f"Duplicate cell IDs found: {duplicates}"
        )
    
    vertices = [c for c in cells if c.get("vertex") == "1"]
    edges = [c for c in cells if c.get("edge") == "1"]
    
    result["stats"]["total_mxcells"] = len(cells)
    result["stats"]["vertices"] = len(vertices)
    result["stats"]["edges"] = len(edges)
    
    # Check root cells
    has_root_0 = "0" in cell_ids
    has_root_1 = "1" in cell_ids
    
    if not has_root_0:
        result["valid"] = False
        result["errors"].append("Missing root mxCell id='0'")
    if not has_root_1:
        result["valid"] = False
        result["errors"].append("Missing root mxCell id='1'")
    
    # Check mxCell completeness
    expected_min = 2 + len(vertices) + len(edges)
    if len(cells) < expected_min:
        result["warnings"].append(
            f"mxCell count ({len(cells)}) may be incomplete. "
            f"Expected >= {expected_min}"
        )
    
    # Check edge references
    for edge in edges:
        edge_id = edge.get("id", "unknown")
        source = edge.get("source")
        target = edge.get("target")
        
        if source and source not in cell_ids:
            result["valid"] = False
            result["errors"].append(
                f"Edge '{edge_id}' references invalid source '{source}'"
            )
        if target and target not in cell_ids:
            result["valid"] = False
            result["errors"].append(
                f"Edge '{edge_id}' references invalid target '{target}'"
            )
    
    # Check mxGeometry
    for cell in vertices + edges:
        cell_id = cell.get("id", "unknown")
        geom = cell.find("mxGeometry")
        if geom is None:
            result["warnings"].append(
                f"mxCell '{cell_id}' missing mxGeometry"
            )
    
    # Check for deprecated Azure icon format (mxgraph.azure.*)
    import re
    file_content = Path(filepath).read_text(encoding="utf-8")
    azure_old_pattern = re.findall(r'mxgraph\.azure[^2]', file_content)
    if azure_old_pattern:
        result["warnings"].append(
            f"Deprecated Azure format detected: 'mxgraph.azure.*' "
            f"Use 'img/lib/azure2/**/*.svg' instead for VS Code compatibility"
        )
    
    return result


def print_result(result: dict) -> None:
    """Print validation result in readable format."""
    status = "✅ VALID" if result["valid"] else "❌ INVALID"
    print(f"\n{'='*50}")
    print(f"File: {result['file']}")
    print(f"Status: {status}")
    print(f"{'='*50}")
    
    stats = result["stats"]
    print(f"\nStatistics:")
    print(f"  Generator: {stats.get('generator', 'N/A')}")
    print(f"  Total mxCells: {stats.get('total_mxcells', 0)}")
    print(f"  Vertices: {stats.get('vertices', 0)}")
    print(f"  Edges: {stats.get('edges', 0)}")
    
    if result["errors"]:
        print(f"\n🚨 Errors ({len(result['errors'])}):")
        for err in result["errors"]:
            print(f"  - {err}")
    
    if result["warnings"]:
        print(f"\n⚠️ Warnings ({len(result['warnings'])}):")
        for warn in result["warnings"]:
            print(f"  - {warn}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_drawio.py <file.drawio|directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    files = []
    
    if os.path.isdir(target):
        # Find all .drawio files in directory
        for ext in ["*.drawio", "*.drawio.svg"]:
            files.extend(Path(target).glob(ext))
    elif os.path.isfile(target):
        files = [Path(target)]
    else:
        print(f"Error: '{target}' not found")
        sys.exit(1)
    
    if not files:
        print(f"No .drawio files found in '{target}'")
        sys.exit(1)
    
    all_valid = True
    for filepath in files:
        result = validate_drawio(str(filepath))
        print_result(result)
        if not result["valid"]:
            all_valid = False
    
    print(f"\n{'='*50}")
    if all_valid:
        print("✅ All files validated successfully")
    else:
        print("❌ Some files have validation errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
