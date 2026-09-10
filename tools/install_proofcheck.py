"""Install the validated proofcheck runtime in the selected user's Codex root."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone


SKILL_NAME = "stat-paper-proofcheck"
CACHES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git"}
DEVELOPMENT_ROOTS = {"tests", "evals"}


def excluded(path: Path, *, runtime: bool = False) -> bool:
    return (bool(CACHES.intersection(path.parts)) or path.suffix in {".pyc", ".pyo"}
            or (runtime and bool(path.parts) and path.parts[0] in DEVELOPMENT_ROOTS))


def files(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if excluded(relative):
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError(f"Package links are not supported: {path}")
        if path.is_file():
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            result[relative.as_posix()] = digest.hexdigest()
    if "SKILL.md" not in result or "scripts/proofcheck.py" not in result:
        raise ValueError(f"Not a complete proofcheck package: {root}")
    return result


def delivery(package: Path) -> dict:
    command = [sys.executable, "-X", "utf8", "-B",
               str(package / "scripts/proofcheck.py"), "delivery-check", "--root",
               str(package / "assets/reference-audit/proofcheck-audit")]
    run = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if run.returncode:
        raise ValueError(f"Bundled reference failed at {package}:\n{run.stdout}\n{run.stderr}")
    result = json.loads(run.stdout)
    if (result.get("delivery_status") != "FINAL"
            or result.get("usable_finalization") is not True
            or result.get("freshness") != "current"):
        raise ValueError(f"Bundled reference is not FINAL, current and usable: {result}")
    return result


def confined(path: Path, parent: Path) -> None:
    resolved = path.resolve()
    if resolved == parent or not resolved.is_relative_to(parent):
        raise ValueError(f"Installation path escapes the selected directory: {path}")


def install(source: Path, user_root: Path, upgrade: bool = False) -> dict:
    source, user_root = source.resolve(), user_root.resolve()
    if user_root == source or user_root.is_relative_to(source):
        raise ValueError("The selected user root must be outside the source package.")
    codex = user_root / ".codex"
    target = codex / "skills" / SKILL_NAME
    for path in (codex, target.parent, target):
        if path.is_symlink():
            raise ValueError(f"Installation links are not supported: {path}")
        confined(path, user_root)
    duplicates = [user_root / root / "skills" / SKILL_NAME
                  for root in (".agents", ".claude")]
    found = [str(path) for path in duplicates if os.path.lexists(path)]
    if found:
        raise ValueError("Other discoverable copies exist; preserve and relocate them first: "
                         + ", ".join(found))
    if target.exists() and not upgrade:
        raise ValueError(f"Installation exists at {target}; use --upgrade to archive and replace it.")
    if source == target or source.is_relative_to(target):
        raise ValueError("Choose a separate validated source package, not the installation.")
    previous = files(target) if target.exists() else None
    source_before = files(source)
    expected = {name: digest for name, digest in source_before.items()
                if not excluded(Path(name), runtime=True)}
    source_delivery = delivery(source)
    codex.mkdir(parents=True, exist_ok=True)
    stage_parent = Path(tempfile.mkdtemp(prefix="proofcheck-install-", dir=codex))
    stage = stage_parent / SKILL_NAME
    backup = None
    published = False
    try:
        shutil.copytree(source, stage, ignore=lambda folder, names: [
            name for name in names
            if excluded((Path(folder) / name).relative_to(source), runtime=True)])
        if files(stage) != expected or files(source) != source_before:
            raise ValueError("Package changed during copying; installation was not replaced.")
        delivery(stage)
        if files(source) != source_before or files(stage) != expected:
            raise ValueError("Package changed during validation; installation was not replaced.")
        target.parent.mkdir(parents=True, exist_ok=True)
        confined(target, codex.resolve())
        if previous is not None:
            if not target.exists() or files(target) != previous:
                raise ValueError("Installation changed during preparation; retry from current state.")
            backup_candidate = codex / "skill-backups" / SKILL_NAME / (
                datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
            backup_candidate.parent.mkdir(parents=True, exist_ok=True)
            confined(backup_candidate, codex.resolve())
            target.rename(backup_candidate)
            backup = backup_candidate
        elif os.path.lexists(target):
            raise ValueError(f"Installation appeared during preparation: {target}")
        stage.rename(target)
        published = True
        installed_delivery = delivery(target)
        if files(target) != expected:
            raise ValueError("Installed files differ from the validated package.")
        return {"installed": str(target), "backup": str(backup) if backup else None,
                "runtime_files_match": True, "files": expected,
                "excluded_top_level_directories": sorted(DEVELOPMENT_ROOTS),
                "source_non_bytecode_file_count": len(source_before),
                "duplicate_locations_checked": [str(path) for path in duplicates],
                "source_delivery": source_delivery, "installed_delivery": installed_delivery,
                "python": sys.executable}
    except Exception:
        if published:
            # Retain a failed candidate outside skill discovery for diagnosis.
            confined(target, codex.resolve())
            target.rename(stage)
        if backup is not None:
            confined(backup, codex.resolve())
            backup.rename(target)
        raise
    finally:
        # Remove only an empty staging directory. Failed candidates stay available.
        if stage_parent.exists() and not any(stage_parent.iterdir()):
            stage_parent.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=Path(__file__).resolve().parents[1] / SKILL_NAME)
    parser.add_argument("--user-root", type=Path, default=Path.home(),
                        help="Selected user's home directory; override for a temporary exercise")
    parser.add_argument("--upgrade", action="store_true",
                        help="Preserve an existing Codex copy outside discovery, then replace it")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.source, args.user_root, args.upgrade), indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
