#!/usr/bin/env python3
"""Validate and emit a v6 Project without modifying the input file."""

import argparse
import json
from pathlib import Path
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "validate"
SCHEMA = ROOT / "language.schema.json"


def move_threshold(record, path):
    if "priorityThreshold" not in record:
        return
    threshold = record.pop("priorityThreshold")
    policy = record.setdefault("assessmentPolicy", {})
    if not isinstance(policy, dict):
        raise ValueError(f"{path}.assessmentPolicy must be an object")
    if "priorityThreshold" in policy and policy["priorityThreshold"] != threshold:
        raise ValueError(f"{path} has conflicting priorityThreshold values")
    policy["priorityThreshold"] = threshold


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    try:
        project = json.loads(args.project.read_text(encoding="utf-8"))
        if not isinstance(project, dict):
            raise ValueError("Expected a Project object")
        version = project.get("schemaVersion")
        if not isinstance(version, str) or not re.fullmatch(r"5\.\d+\.\d+", version):
            raise ValueError("Expected a Project declaring a v5 schemaVersion")
        move_threshold(project, "project")
        cycles = project.get("cycles", [])
        if not isinstance(cycles, list):
            raise ValueError("cycles must be an array")
        for index, cycle in enumerate(cycles):
            if not isinstance(cycle, dict):
                raise ValueError(f"cycles[{index}] must be an object")
            move_threshold(cycle, f"cycles[{index}]")
        project["schemaVersion"] = "6.0.0"
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")

    sys.path.insert(0, str(VALIDATE))
    from _venv_bootstrap import ensure_dependencies

    ensure_dependencies()
    validator_class = runpy.run_path(str(VALIDATE / "validate-project.py"))["ProjectValidator"]
    validator = validator_class(args.project, SCHEMA, project=project)
    if not validator.validate_local():
        for error in validator.errors:
            print(f"{error['path']}: {error['issue']}", file=sys.stderr)
        return 1
    print(json.dumps(project, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
