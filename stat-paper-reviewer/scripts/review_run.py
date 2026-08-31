#!/usr/bin/env python3
"""Portable run-state helper for stat-paper-reviewer.

The helper uses only the Python standard library. It copies inputs and stage
artifacts into a self-contained review bundle, records only POSIX-style
bundle-relative paths, verifies SHA-256 hashes, and prevents finalization until
all required stages have durable completion records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
from datetime import datetime, timezone
import unicodedata


SCHEMA_VERSION = 2
RUNNER_VERSION = "1.2"
MANIFEST_NAME = "review_run.json"
SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "stat-paper-reviewer"
PROFILES = {
    "full": [
        "intake",
        "source_map",
        "first_reader",
        "fact_base",
        "claim_chain",
        "literature",
        "patterned_prose",
        "synthesis",
        "qa",
    ],
    "focused": [
        "intake",
        "source_map",
        "fact_base",
        "synthesis",
        "qa",
    ],
}
KNOWN_STAGES = {
    "intake",
    "source_map",
    "first_reader",
    "fact_base",
    "claim_chain",
    "literature",
    "patterned_prose",
    "synthesis",
    "qa",
}
OUTCOMES = {"complete", "limited", "not_assessable"}


class RunError(RuntimeError):
    """Expected validation or lifecycle failure."""


def required_stages_for(profile: str, declared: list[str] | None = None) -> list[str]:
    """Return the canonical profile stages plus validated extra stages."""
    required = list(PROFILES[profile])
    for stage in declared or []:
        if stage not in required:
            required.insert(required.index("synthesis"), stage)
    return required


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_skill_identity(path: Path | None = None) -> tuple[str, str]:
    """Read the skill name and release version from SKILL.md frontmatter."""
    skill_path = path or SKILL_ROOT / "SKILL.md"
    try:
        text = skill_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RunError(f"cannot read skill identity from {skill_path}: {exc}") from exc
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise RunError(f"SKILL.md has invalid frontmatter: {skill_path}")
    name_match = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", parts[1])
    version_match = re.search(r'(?m)^\s+version:\s*"([^"]+)"\s*$', parts[1])
    if not name_match or not version_match:
        raise RunError(f"SKILL.md is missing name or metadata.version: {skill_path}")
    return name_match.group(1), version_match.group(1)


def protocol_sources() -> list[tuple[str, Path]]:
    """Return the exact reviewer instructions and helpers to snapshot."""
    references = sorted(
        (SKILL_ROOT / "references").glob("*.md"),
        key=lambda path: path.name.casefold(),
    )
    candidates = [
        SKILL_ROOT / "SKILL.md",
        *references,
        SKILL_ROOT / "scripts" / "academic_search.py",
        Path(__file__).resolve(),
    ]
    sources: list[tuple[str, Path]] = []
    for source in candidates:
        try:
            relative = source.resolve().relative_to(SKILL_ROOT.resolve()).as_posix()
        except (OSError, ValueError) as exc:
            raise RunError(f"protocol source is outside the skill root: {source}") from exc
        if not source.is_file():
            raise RunError(f"protocol source is not a regular file: {source}")
        sources.append((relative, source))
    return sources


def combined_protocol_digest(records: list[dict]) -> str:
    """Hash the ordered source paths and file hashes in a protocol snapshot."""
    digest = hashlib.sha256()
    for record in sorted(records, key=lambda item: item["source_path"]):
        digest.update(record["source_path"].encode("utf-8"))
        digest.update(b"\x00")
        digest.update(record["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def portable_name(name: str) -> str:
    """Return a filename safe on Windows, macOS, and Linux."""
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).rstrip(" .")
    if not name:
        name = "input"
    return name[:180]


def relative_text(path: Path, root: Path) -> str:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise RunError(f"path is outside the review bundle: {path}") from exc
    text = relative.as_posix()
    if text.startswith("../") or "\\" in text or Path(text).is_absolute():
        raise RunError(f"nonportable bundle path: {text}")
    return text


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output_handle:
            with source.open("rb") as input_handle:
                shutil.copyfileobj(input_handle, output_handle, length=1024 * 1024)
            output_handle.flush()
            os.fsync(output_handle.fileno())
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def manifest_path(root: Path) -> Path:
    return root / MANIFEST_NAME


def load_manifest(root: Path) -> dict:
    path = manifest_path(root)
    if not path.is_file():
        raise RunError(f"review manifest not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RunError(f"review manifest is unreadable or invalid: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RunError(f"review manifest must contain a JSON object: {path}")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise RunError(
            f"unsupported schema_version: {payload.get('schema_version')!r}; "
            f"expected {SCHEMA_VERSION}"
        )
    expected_types = {
        "workflow_version": str,
        "protocol": dict,
        "profile": str,
        "delegated": bool,
        "status": str,
        "required_stages": list,
        "inputs": list,
        "stages": dict,
    }
    for field, expected_type in expected_types.items():
        if not isinstance(payload.get(field), expected_type):
            raise RunError(
                f"review manifest field {field!r} must be {expected_type.__name__}"
            )
    if not all(isinstance(item, dict) for item in payload["inputs"]):
        raise RunError("review manifest inputs must contain only objects")
    if not all(
        isinstance(name, str) and isinstance(record, dict)
        for name, record in payload["stages"].items()
    ):
        raise RunError("review manifest stages must map names to objects")
    if not all(isinstance(item, str) for item in payload["required_stages"]):
        raise RunError("review manifest required_stages must contain only strings")
    protocol = payload["protocol"]
    protocol_types = {
        "skill_name": str,
        "skill_version": str,
        "sha256": str,
        "files": list,
    }
    for field, expected_type in protocol_types.items():
        if not isinstance(protocol.get(field), expected_type):
            raise RunError(
                f"review manifest protocol field {field!r} must be "
                f"{expected_type.__name__}"
            )
    if not protocol["skill_name"] or not protocol["skill_version"]:
        raise RunError("review manifest protocol skill identity cannot be empty")
    if protocol["skill_name"] != SKILL_NAME:
        raise RunError(
            f"review manifest protocol skill must be {SKILL_NAME!r}"
        )
    if not re.fullmatch(r"[0-9a-f]{64}", protocol["sha256"]):
        raise RunError("review manifest protocol sha256 is invalid")
    if not protocol["files"] or not all(
        isinstance(item, dict) for item in protocol["files"]
    ):
        raise RunError("review manifest protocol files must contain objects")
    protocol_sources_seen: set[str] = set()
    for record in protocol["files"]:
        source_path = record.get("source_path")
        if (
            not isinstance(source_path, str)
            or not source_path
            or "\\" in source_path
            or source_path.startswith("/")
            or ":" in source_path
            or ".." in Path(source_path).parts
        ):
            raise RunError("review manifest protocol contains an unsafe source_path")
        if source_path in protocol_sources_seen:
            raise RunError("review manifest protocol contains duplicate source paths")
        protocol_sources_seen.add(source_path)
        if not isinstance(record.get("path"), str):
            raise RunError("review manifest protocol file path must be a string")
        if not isinstance(record.get("size"), int):
            raise RunError("review manifest protocol file size must be an integer")
        if not isinstance(record.get("sha256"), str) or not re.fullmatch(
            r"[0-9a-f]{64}", record["sha256"]
        ):
            raise RunError("review manifest protocol file sha256 is invalid")
    if "SKILL.md" not in protocol_sources_seen:
        raise RunError("review manifest protocol snapshot is missing SKILL.md")
    if payload["profile"] not in PROFILES:
        raise RunError(f"review manifest profile is unsupported: {payload['profile']!r}")
    if payload["status"] not in {"in_progress", "finalized"}:
        raise RunError(f"review manifest status is invalid: {payload['status']!r}")
    if any(stage not in KNOWN_STAGES for stage in payload["required_stages"]):
        raise RunError("review manifest required_stages contains an unknown stage")
    if len(payload["required_stages"]) != len(set(payload["required_stages"])):
        raise RunError("review manifest required_stages contains duplicates")
    canonical_required = required_stages_for(
        payload["profile"], payload["required_stages"]
    )
    if payload["required_stages"] != canonical_required:
        raise RunError(
            "review manifest required_stages does not match the selected profile "
            "and validated extra stages"
        )
    final_report = payload.get("final_report")
    if final_report is not None and not isinstance(final_report, dict):
        raise RunError("review manifest final_report must be null or an object")
    if not isinstance(payload.get("limits_acknowledged"), bool):
        raise RunError("review manifest limits_acknowledged must be boolean")
    for stage_name, record in payload["stages"].items():
        outcome = record.get("outcome")
        if not isinstance(outcome, str):
            raise RunError(f"review stage {stage_name!r} outcome must be a string")
        artifacts = record.get("artifacts", [])
        if not isinstance(artifacts, list) or not all(
            isinstance(item, dict) for item in artifacts
        ):
            raise RunError(
                f"review stage {stage_name!r} artifacts must be a list of objects"
            )
    return payload


def input_specs(args: argparse.Namespace) -> list[tuple[str, Path]]:
    specs = [("main", Path(args.main).expanduser())]
    specs.extend(("supplement", Path(item).expanduser()) for item in args.supplement)
    specs.extend(("companion", Path(item).expanduser()) for item in args.companion)
    return specs


def check_source(path: Path) -> tuple[int, str]:
    if not path.is_file():
        raise RunError(f"input is not a readable regular file: {path}")
    try:
        with path.open("rb") as handle:
            handle.read(1)
        return path.stat().st_size, sha256(path)
    except OSError as exc:
        raise RunError(f"input-read failure for {path}: {exc}") from exc


def writable_probe(root: Path) -> None:
    probe_dir = root if root.is_dir() else root.parent
    while not probe_dir.exists() and probe_dir != probe_dir.parent:
        probe_dir = probe_dir.parent
    if not probe_dir.is_dir():
        raise RunError(f"no existing output parent for write probe: {root}")
    try:
        descriptor, name = tempfile.mkstemp(prefix=".review-write-probe.", dir=probe_dir)
        os.close(descriptor)
        Path(name).unlink()
    except OSError as exc:
        raise RunError(f"output-write failure under {probe_dir}: {exc}") from exc


def remove_init_staging(staging: Path, parent: Path, prefix: str) -> None:
    """Remove only a staging entry created for this initialization attempt."""
    try:
        resolved_parent = parent.resolve()
        resolved_staging = staging.resolve()
        resolved_staging.relative_to(resolved_parent)
    except (OSError, ValueError) as exc:
        raise RunError(f"refusing to clean unconfined staging path: {staging}") from exc
    if resolved_staging.parent != resolved_parent or not staging.name.startswith(prefix):
        raise RunError(f"refusing to clean unexpected staging path: {staging}")
    if staging.is_symlink():
        staging.unlink(missing_ok=True)
    elif staging.exists():
        shutil.rmtree(staging)


def doctor(args: argparse.Namespace) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, str] = {}
    records: list[dict] = []
    if sys.version_info < (3, 10):
        errors.append("Python 3.10 or later is required")
    protocol_summary: dict | None = None
    try:
        skill_name, skill_version = read_skill_identity()
        if skill_name != SKILL_NAME:
            raise RunError(
                f"loaded skill name is {skill_name!r}; expected {SKILL_NAME!r}"
            )
        protocol_records: list[dict] = []
        for source_path, source in protocol_sources():
            size, digest = check_source(source)
            protocol_records.append(
                {
                    "source_path": source_path,
                    "size": size,
                    "sha256": digest,
                }
            )
        protocol_summary = {
            "skill_name": skill_name,
            "skill_version": skill_version,
            "sha256": combined_protocol_digest(protocol_records),
            "file_count": len(protocol_records),
        }
    except RunError as exc:
        errors.append(str(exc))
    for role, path in input_specs(args):
        try:
            size, digest = check_source(path)
            record = {
                "role": role,
                "name": path.name,
                "size": size,
                "sha256": digest,
            }
            if digest in seen:
                record["duplicate_of"] = seen[digest]
                warnings.append(f"{path.name} duplicates {seen[digest]} byte for byte")
            else:
                seen[digest] = path.name
            records.append(record)
        except RunError as exc:
            errors.append(str(exc))
    try:
        writable_probe(Path(args.root).expanduser())
    except RunError as exc:
        errors.append(str(exc))
    payload = {
        "ok": not errors,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "protocol": protocol_summary,
        "inputs": records,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


def init_run(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if manifest_path(root).exists():
        raise RunError(f"review run already initialized: {manifest_path(root)}")
    if root.exists() and any(root.iterdir()):
        raise RunError(f"review root must be empty before initialization: {root}")
    writable_probe(root)
    root.parent.mkdir(parents=True, exist_ok=True)
    required = required_stages_for(args.profile, args.require_stage)

    skill_name, skill_version = read_skill_identity()
    if skill_name != SKILL_NAME:
        raise RunError(
            f"loaded skill name is {skill_name!r}; expected {SKILL_NAME!r}"
        )
    checked_protocol: list[tuple[str, Path, int, str]] = []
    for source_path, source in protocol_sources():
        size, digest = check_source(source)
        checked_protocol.append((source_path, source, size, digest))

    checked_sources: list[tuple[str, Path, int, str]] = []
    for role, source in input_specs(args):
        size, digest = check_source(source)
        checked_sources.append((role, source, size, digest))

    prefix = f".{portable_name(root.name)}.init-"
    staging = Path(tempfile.mkdtemp(prefix=prefix, dir=root.parent))
    removed_empty_root = False
    try:
        records: list[dict] = []
        digest_to_id: dict[str, str] = {}
        role_counts: dict[str, int] = {}
        for role, source, size, digest in checked_sources:
            role_counts[role] = role_counts.get(role, 0) + 1
            input_id = f"{role}-{role_counts[role]:03d}"
            destination = staging / "inputs" / f"{input_id}-{portable_name(source.name)}"
            atomic_copy(source, destination)
            copied_digest = sha256(destination)
            if copied_digest != digest:
                raise RunError(f"copied input hash mismatch: {source.name}")
            record = {
                "id": input_id,
                "role": role,
                "original_name": source.name,
                "path": relative_text(destination, staging),
                "size": size,
                "sha256": digest,
            }
            if digest in digest_to_id:
                record["duplicate_of"] = digest_to_id[digest]
            else:
                digest_to_id[digest] = input_id
            records.append(record)

        protocol_records: list[dict] = []
        for source_path, source, size, digest in checked_protocol:
            destination = staging / "protocol" / Path(*source_path.split("/"))
            atomic_copy(source, destination)
            if sha256(destination) != digest:
                raise RunError(f"copied protocol file hash mismatch: {source_path}")
            protocol_records.append(
                {
                    "source_path": source_path,
                    "path": relative_text(destination, staging),
                    "size": size,
                    "sha256": digest,
                }
            )

        created = utc_now()
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "workflow_version": RUNNER_VERSION,
            "protocol": {
                "skill_name": skill_name,
                "skill_version": skill_version,
                "sha256": combined_protocol_digest(protocol_records),
                "files": protocol_records,
            },
            "profile": args.profile,
            "delegated": bool(args.delegated),
            "status": "in_progress",
            "created_at": created,
            "updated_at": created,
            "required_stages": required,
            "inputs": records,
            "stages": {
                "intake": {
                    "outcome": "complete",
                    "completed_at": created,
                    "producer": "review_run.py",
                    "note": "Inputs copied and hash-locked into the review bundle.",
                    "artifacts": [
                        {
                            "path": record["path"],
                            "size": record["size"],
                            "sha256": record["sha256"],
                        }
                        for record in records
                    ],
                }
            },
            "final_report": None,
            "limits_acknowledged": False,
        }
        atomic_json(manifest_path(staging), manifest)
        if root.exists():
            root.rmdir()
            removed_empty_root = True
        os.replace(staging, root)
    except Exception:
        if staging.exists() or staging.is_symlink():
            remove_init_staging(staging, root.parent, prefix)
        if removed_empty_root and not root.exists():
            root.mkdir()
        raise
    print(f"initialized {manifest_path(root)}")
    return 0


def stage_dependencies(manifest: dict, name: str) -> list[str]:
    if name == "source_map":
        return ["intake"]
    if name == "first_reader":
        return ["source_map"]
    if name == "fact_base":
        return ["first_reader"] if manifest["profile"] == "full" else ["source_map"]
    if name == "claim_chain":
        return ["fact_base"]
    if name in {"literature", "patterned_prose"}:
        return ["first_reader"]
    if name == "synthesis":
        return [
            stage
            for stage in manifest["required_stages"]
            if stage not in {"intake", "synthesis", "qa"}
        ]
    if name == "qa":
        return ["synthesis"]
    return []


def downstream_stages(manifest: dict, changed_stage: str) -> list[str]:
    """Return recorded stages made stale by replacing one upstream stage."""
    stages = manifest["stages"]
    stale = {changed_stage}
    ordered: list[str] = []
    while True:
        added = False
        for candidate in sorted(KNOWN_STAGES):
            if candidate in stale or candidate not in stages:
                continue
            dependencies = set(stage_dependencies(manifest, candidate))
            if candidate == "synthesis":
                dependencies.update(
                    name
                    for name in stages
                    if name not in {"intake", "synthesis", "qa"}
                )
            if dependencies & stale:
                stale.add(candidate)
                ordered.append(candidate)
                added = True
        if not added:
            return ordered


def is_closed(stage_record: dict | None) -> bool:
    return bool(stage_record and stage_record.get("outcome") in OUTCOMES)


def verify_record(root: Path, record: dict, label: str) -> list[str]:
    errors: list[str] = []
    relative = record.get("path")
    if not isinstance(relative, str) or not relative:
        return [f"{label}: missing path"]
    if "\\" in relative or relative.startswith("/") or ".." in Path(relative).parts:
        return [f"{label}: nonportable or unsafe path: {relative}"]
    target = root.joinpath(*relative.split("/"))
    if not target.is_file():
        return [f"{label}: missing file: {relative}"]
    resolved_root = root.resolve()
    try:
        resolved_target = target.resolve(strict=True)
        resolved_target.relative_to(resolved_root)
    except (OSError, ValueError):
        return [f"{label}: redirected path leaves the review bundle: {relative}"]
    current = resolved_root
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    for part in Path(relative).parts:
        current = current / part
        try:
            metadata = os.lstat(current)
        except OSError as exc:
            return [f"{label}: unreadable path component {relative}: {exc}"]
        if current.is_symlink() or (
            reparse_flag
            and getattr(metadata, "st_file_attributes", 0) & reparse_flag
        ):
            return [f"{label}: redirected path component is forbidden: {relative}"]
    try:
        size = target.stat().st_size
        digest = sha256(target)
    except OSError as exc:
        return [f"{label}: unreadable file {relative}: {exc}"]
    if size != record.get("size"):
        errors.append(f"{label}: size changed: {relative}")
    if digest != record.get("sha256"):
        errors.append(f"{label}: hash changed: {relative}")
    return errors


def validate_run(root: Path, manifest: dict) -> dict:
    errors: list[str] = []
    protocol = manifest["protocol"]
    protocol_files = protocol["files"]
    for index, record in enumerate(protocol_files, start=1):
        errors.extend(verify_record(root, record, f"protocol file {index}"))
    if combined_protocol_digest(protocol_files) != protocol["sha256"]:
        errors.append("protocol snapshot digest does not match its file records")
    skill_record = next(
        (record for record in protocol_files if record["source_path"] == "SKILL.md"),
        None,
    )
    if skill_record is not None:
        skill_path = root.joinpath(*skill_record["path"].split("/"))
        if skill_path.is_file():
            try:
                snapshot_name, snapshot_version = read_skill_identity(skill_path)
            except RunError as exc:
                errors.append(str(exc))
            else:
                if snapshot_name != protocol["skill_name"]:
                    errors.append("protocol skill name does not match snapshotted SKILL.md")
                if snapshot_version != protocol["skill_version"]:
                    errors.append(
                        "protocol skill version does not match snapshotted SKILL.md"
                    )
    for item in manifest.get("inputs", []):
        errors.extend(verify_record(root, item, f"input {item.get('id', '?')}"))
    stages = manifest.get("stages", {})
    for stage_name, record in stages.items():
        if record.get("outcome") not in OUTCOMES:
            errors.append(f"stage {stage_name}: invalid outcome")
        for index, artifact in enumerate(record.get("artifacts", []), start=1):
            errors.extend(verify_record(root, artifact, f"stage {stage_name} artifact {index}"))
    final_report = manifest.get("final_report")
    if final_report:
        errors.extend(verify_record(root, final_report, "final report"))
    required = required_stages_for(
        manifest["profile"], manifest.get("required_stages", [])
    )
    missing = [stage for stage in required if not is_closed(stages.get(stage))]
    limited = [
        stage
        for stage in required
        if is_closed(stages.get(stage)) and stages[stage]["outcome"] != "complete"
    ]
    if manifest.get("status") == "finalized":
        if missing:
            errors.append("finalized run has incomplete required stages")
        if not final_report:
            errors.append("finalized run has no final report")
        if limited and not manifest.get("limits_acknowledged"):
            errors.append("finalized run has unacknowledged stage limitations")
    return {"errors": errors, "missing_stages": missing, "limited_stages": limited}


def copy_stage_artifacts(root: Path, name: str, sources: list[str]) -> list[dict]:
    records: list[dict] = []
    stage_dir = root / "artifacts" / name
    for index, raw_source in enumerate(sources, start=1):
        source = Path(raw_source).expanduser()
        size, digest = check_source(source)
        destination = stage_dir / f"artifact-{index:03d}-{portable_name(source.name)}"
        counter = index
        while destination.exists():
            counter += 1
            destination = stage_dir / f"artifact-{counter:03d}-{portable_name(source.name)}"
        atomic_copy(source, destination)
        if sha256(destination) != digest:
            raise RunError(f"copied stage artifact hash mismatch: {source}")
        records.append(
            {
                "path": relative_text(destination, root),
                "size": size,
                "sha256": digest,
            }
        )
    return records


def record_stage(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    manifest = load_manifest(root)
    if manifest.get("status") == "finalized":
        raise RunError("cannot change a finalized review run")
    validation = validate_run(root, manifest)
    if validation["errors"]:
        raise RunError("run integrity check failed: " + "; ".join(validation["errors"]))
    if args.name == "intake":
        raise RunError("intake is completed by init and cannot be overwritten")
    if manifest.get("delegated") and not args.producer:
        raise RunError("--producer is required for a delegated review stage")
    if args.outcome != "complete" and not (args.note and args.note.strip()):
        raise RunError("--note is required for a limited or not_assessable stage")
    stages = manifest["stages"]
    missing_dependencies: list[str] = []
    blocked_dependencies: list[str] = []
    for dependency in stage_dependencies(manifest, args.name):
        record = stages.get(dependency)
        if not is_closed(record):
            missing_dependencies.append(dependency)
        elif dependency in {"intake", "source_map"} and record["outcome"] == "not_assessable":
            blocked_dependencies.append(dependency)
    if missing_dependencies:
        raise RunError(
            f"stage {args.name} is blocked by incomplete dependencies: "
            + ", ".join(missing_dependencies)
        )
    if blocked_dependencies:
        raise RunError(
            f"stage {args.name} is blocked by unusable dependencies: "
            + ", ".join(blocked_dependencies)
        )
    artifacts = copy_stage_artifacts(root, args.name, args.artifact)
    invalidated = downstream_stages(manifest, args.name)
    for stage_name in invalidated:
        stages.pop(stage_name, None)
    stages[args.name] = {
        "outcome": args.outcome,
        "completed_at": utc_now(),
        "producer": args.producer or "primary",
        "note": args.note or "",
        "artifacts": artifacts,
    }
    manifest["updated_at"] = utc_now()
    manifest["final_report"] = None
    manifest["limits_acknowledged"] = False
    atomic_json(manifest_path(root), manifest)
    print(f"recorded stage {args.name}: {args.outcome}")
    if invalidated:
        print("invalidated downstream stages: " + ", ".join(invalidated))
    return 0


def status(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    manifest = load_manifest(root)
    validation = validate_run(root, manifest)
    payload = {
        "status": manifest.get("status"),
        "workflow_version": manifest.get("workflow_version"),
        "skill": {
            "name": manifest["protocol"]["skill_name"],
            "version": manifest["protocol"]["skill_version"],
            "protocol_sha256": manifest["protocol"]["sha256"],
        },
        "profile": manifest.get("profile"),
        "delegated": manifest.get("delegated"),
        "integrity": "ok" if not validation["errors"] else "failed",
        "missing_stages": validation["missing_stages"],
        "limited_stages": validation["limited_stages"],
        "errors": validation["errors"],
        "final_report": manifest.get("final_report", {}).get("path")
        if manifest.get("final_report")
        else None,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not validation["errors"] else 1


def finalize(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    manifest = load_manifest(root)
    if manifest.get("status") == "finalized":
        raise RunError("review run is already finalized")
    validation = validate_run(root, manifest)
    if validation["errors"]:
        raise RunError("run integrity check failed: " + "; ".join(validation["errors"]))
    if validation["missing_stages"]:
        raise RunError(
            "cannot finalize; incomplete required stages: "
            + ", ".join(validation["missing_stages"])
        )
    if validation["limited_stages"] and not args.acknowledge_limits:
        raise RunError(
            "cannot finalize without --acknowledge-limits; limited stages: "
            + ", ".join(validation["limited_stages"])
        )
    report = Path(args.report).expanduser()
    size, digest = check_source(report)
    destination = root / "reports" / f"final-{portable_name(report.name)}"
    atomic_copy(report, destination)
    if sha256(destination) != digest:
        raise RunError("copied final report hash mismatch")
    manifest["final_report"] = {
        "path": relative_text(destination, root),
        "size": size,
        "sha256": digest,
        "finalized_at": utc_now(),
    }
    manifest["status"] = "finalized"
    manifest["limits_acknowledged"] = bool(args.acknowledge_limits)
    manifest["updated_at"] = utc_now()
    atomic_json(manifest_path(root), manifest)
    print(f"finalized {manifest_path(root)}")
    return 0


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", required=True, help="Review bundle directory")
    parser.add_argument("--main", required=True, help="Main manuscript file")
    parser.add_argument(
        "--supplement", action="append", default=[], help="Supplement file; repeat as needed"
    )
    parser.add_argument(
        "--companion",
        action="append",
        default=[],
        help="Other supplied source, bibliography, or response file; repeat as needed",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="Check input reads and output writes")
    add_input_arguments(doctor_parser)
    doctor_parser.set_defaults(func=doctor)

    init_parser = subparsers.add_parser("init", help="Create a portable, hash-locked run bundle")
    add_input_arguments(init_parser)
    init_parser.add_argument("--profile", choices=sorted(PROFILES), default="full")
    init_parser.add_argument(
        "--require-stage",
        action="append",
        choices=sorted(KNOWN_STAGES - {"intake"}),
        default=[],
        help="Add a required stage, for example literature",
    )
    init_parser.add_argument(
        "--delegated", action="store_true", help="Require a producer label for each stage"
    )
    init_parser.set_defaults(func=init_run)

    stage_parser = subparsers.add_parser("stage", help="Hash-lock a completed stage artifact")
    stage_parser.add_argument("--root", required=True)
    stage_parser.add_argument("--name", required=True, choices=sorted(KNOWN_STAGES))
    stage_parser.add_argument("--artifact", action="append", required=True)
    stage_parser.add_argument("--outcome", choices=sorted(OUTCOMES), default="complete")
    stage_parser.add_argument("--producer", default=None)
    stage_parser.add_argument("--note", default=None)
    stage_parser.set_defaults(func=record_stage)

    status_parser = subparsers.add_parser("status", help="Verify hashes and completion state")
    status_parser.add_argument("--root", required=True)
    status_parser.set_defaults(func=status)

    finalize_parser = subparsers.add_parser("finalize", help="Gate and hash-lock the final report")
    finalize_parser.add_argument("--root", required=True)
    finalize_parser.add_argument("--report", required=True)
    finalize_parser.add_argument("--acknowledge-limits", action="store_true")
    finalize_parser.set_defaults(func=finalize)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except RunError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: filesystem operation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
