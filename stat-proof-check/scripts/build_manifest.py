"""Refresh or verify this isolated candidate's runtime content manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from paper_core.bundle import MANIFEST_NAME, build_manifest, bundle_files, manifest_text, verify_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    core = Path(__file__).resolve().parent / "paper_core"
    if not args.check:
        (core / MANIFEST_NAME).write_text(manifest_text(build_manifest(bundle_files(core))), encoding="utf-8")
    result = verify_bundle(core)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
