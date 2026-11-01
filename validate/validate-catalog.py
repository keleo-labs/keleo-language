#!/usr/bin/env python3
"""Validate local source and practice catalogs and their cross-references."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv_bootstrap import ensure_dependencies  # noqa: E402

ensure_dependencies()
from jsonschema import Draft202012Validator  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(path, source_workspace=None, practice=None, require_fresh=False):
    catalog = read(path)
    kind = "source" if "source" in catalog else "practice"
    schema = read(ROOT / f"{kind}-catalog.schema.json")
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(catalog)]
    if errors:
        return errors
    if kind == "source":
        source = catalog["source"]
        ids = [section["id"] for section in catalog["sections"]]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate source section IDs")
        if any(not identifier.startswith(f"{source['id']}@{source['revision']}#") for identifier in ids):
            errors.append("Section ID does not match source identity and revision")
        return errors
    if practice:
        raw = practice.read_bytes()
        document = json.loads(raw)
        identity = catalog["practice"]
        if identity["sha256"] != hashlib.sha256(raw).hexdigest():
            errors.append("Practice changed since catalog build")
        if any(identity[key] != document.get(key) for key in ("kind", "name", "version")):
            errors.append("Practice identity differs from catalog")
        for entry in catalog["elements"]:
            try:
                value = document
                for token in entry["pointer"].split("/")[1:]:
                    token = token.replace("~1", "/").replace("~0", "~")
                    value = value[int(token)] if isinstance(value, list) else value[token]
                if value.get("name") != entry["name"]:
                    errors.append(f"Element changed: {entry['pointer']}")
            except (KeyError, IndexError, ValueError, TypeError, AttributeError):
                errors.append(f"Element missing: {entry['pointer']}")
    pointers = [entry["pointer"] for entry in catalog["elements"]]
    if len(pointers) != len(set(pointers)):
        errors.append("Duplicate practice element pointers")
    if source_workspace:
        sections, fresh = set(), set()
        for pointer in source_workspace.glob("*/latest.json"):
            state = read(pointer)
            for snapshot in pointer.parent.glob("*.json"):
                if snapshot.name == "latest.json":
                    continue
                item = read(snapshot)
                ids = {section["id"] for section in item["sections"]}
                sections.update(ids)
                if snapshot.name == state["snapshot"] and state["status"] == "fresh":
                    uri = item["source"]["uri"]
                    if uri.startswith(("http://", "https://")):
                        fresh.update(ids)
                    else:
                        try:
                            if hashlib.sha256(Path(uri).expanduser().read_bytes()).hexdigest() == item["source"]["inputSha256"]:
                                fresh.update(ids)
                        except OSError:
                            pass
        for entry in catalog["elements"]:
            for identifier in entry["sourceSections"]:
                if identifier not in sections:
                    errors.append(f"Missing source section: {identifier}")
                elif require_fresh and identifier not in fresh:
                    errors.append(f"Stale source section: {identifier}")
    elif any(entry["sourceSections"] for entry in catalog["elements"]):
        errors.append("Source workspace required to validate section links")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--source-workspace", type=Path)
    parser.add_argument("--practice", type=Path)
    parser.add_argument("--require-fresh", action="store_true")
    args = parser.parse_args()
    try:
        errors = validate(args.catalog, args.source_workspace, args.practice, args.require_fresh)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors = [str(error)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("catalog valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
