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


def validate(path, source_workspace=None, practice=None, require_fresh=False, project=None, methodology=None):
    catalog = read(path)
    kind = ("source" if "source" in catalog else "project" if "project" in catalog else
            "methodology" if "variants" in catalog else "practice")
    schema = read(ROOT / "schemas" / "catalogs" / f"{kind}-catalog.schema.json")
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
    if kind == "methodology":
        identities = [(variant["version"], variant["sha256"]) for variant in catalog["variants"]]
        if len(identities) != len(set(identities)):
            errors.append("Duplicate methodology variant")
        for variant in catalog["variants"]:
            if (variant["documentKind"] == "method") != (catalog["kind"] == "method"):
                errors.append(f"Methodology kind differs in {variant['version']}")
            pointers = [entry["pointer"] for entry in variant["elements"]]
            if len(pointers) != len(set(pointers)):
                errors.append(f"Duplicate methodology element pointers in {variant['version']}")
        if methodology:
            document = read(methodology)
            actual = hashlib.sha256(json.dumps(document, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            if not any(v["sha256"] == actual and (not document.get("version") or v["version"] == document["version"])
                       and v["documentKind"] == document.get("kind")
                       for v in catalog["variants"]):
                errors.append("Methodology changed since catalog build")
            if catalog["name"] != document.get("name") or catalog["kind"] != (
                    "method" if document.get("kind") == "method" else "practice"):
                errors.append("Methodology identity differs from catalog")
        return errors
    if kind == "project":
        if project and hashlib.sha256(project.read_bytes()).hexdigest() != catalog["project"]["sha256"]:
            errors.append("Project changed since catalog build")
        pointers = [entry["pointer"] for entry in catalog["elements"]]
        if len(pointers) != len(set(pointers)):
            errors.append("Duplicate Project element pointers")
        available = set(pointers)
        for method in catalog["methodologyCatalogs"]:
            method_path = Path(method)
            if not method_path.is_file():
                errors.append(f"Missing methodology catalog: {method}")
                continue
            linked = read(method_path)
            for variant in linked["variants"]:
                available.update(f"{method_path.name}@{variant['sha256']}:{entry['pointer']}"
                                 for entry in variant["elements"])
        sections = set()
        if source_workspace:
            for snapshot in source_workspace.glob("*/*.json"):
                if snapshot.name != "latest.json":
                    sections.update(section["id"] for section in read(snapshot)["sections"])
        for pointer, ids in catalog["sourceSections"].items():
            if pointer not in available:
                errors.append(f"Unknown catalog element: {pointer}")
            for identifier in ids:
                if identifier not in sections:
                    errors.append(f"Missing source section: {identifier}")
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
    parser.add_argument("--project", type=Path)
    parser.add_argument("--methodology", type=Path)
    parser.add_argument("--require-fresh", action="store_true")
    args = parser.parse_args()
    try:
        errors = validate(args.catalog, args.source_workspace, args.practice, args.require_fresh,
                          args.project, args.methodology)
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
