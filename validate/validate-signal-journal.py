#!/usr/bin/env python3
"""Validate a signal journal and optionally resolve supplied context documents.

Version: 1.0.0. Uses the same environment and structured reports as other validators.
"""

import argparse
import json
from pathlib import Path
import sys

from _venv_bootstrap import ensure_dependencies

ensure_dependencies()

from signal_validation import SignalValidator  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('journal', type=Path)
    parser.add_argument('schema', type=Path)
    parser.add_argument('--document', action='append', default=[], type=Path,
                        help='Referenced mapping, methodology, project or ChangeRequest; repeatable')
    parser.add_argument('--strict', action='store_true', help='Treat unloaded external references as errors')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress messages')
    parser.add_argument('--brief', action='store_true')
    args = parser.parse_args()
    try:
        schema = json.loads(args.schema.read_text())
        journal = json.loads(args.journal.read_text())
        documents = [json.loads(path.read_text()) for path in args.document]
    except (OSError, ValueError) as exc:
        parser.exit(2, f'ERROR: {exc}\n')
    checker = SignalValidator(schema, documents, preflight=args.strict)
    checker.validate_journal(journal)
    report = {'valid': not checker.errors, 'file': str(args.journal),
              'error_count': len(checker.errors), 'warning_count': len(checker.warnings),
              'errors': checker.errors, 'warnings': checker.warnings}
    if args.brief:
        print(f"{'PASS' if report['valid'] else 'FAIL'} {report['error_count']} errors "
              f"({report['warning_count']} warnings) — {args.journal.name}")
    else:
        print(json.dumps(report, indent=2))
    sys.exit(0 if report['valid'] else 1)


if __name__ == '__main__':
    main()
