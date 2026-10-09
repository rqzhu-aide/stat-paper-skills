#!/usr/bin/env python3
"""Command entry for the paper audit database (implementation-handoff 5).

Runs the isolated v3 ``paper_core`` shipped next to this file. Its manifest is
maintained with ``scripts/build_manifest.py``. This wrapper never imports the legacy monolith, never looks up a
sibling skill, and never imports from the repository tree.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from paper_core.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
