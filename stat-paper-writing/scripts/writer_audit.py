#!/usr/bin/env python3
"""Create, resume, validate, and publish full stat-paper-writing audits.

The harness validates editorial workflow contracts and provenance. It does not
assess mathematical correctness, source truth, code behavior, numerical
results, novelty, or scientific merit.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = "3.0"
CONTRACT_VERSION = "writer-audit-2"
SKILL_NAME = "stat-paper-writing"
DEFAULT_FOCUS = "default fine-to-coarse audit"
MANIFEST_NAME = "AUDIT_MANIFEST.json"
STATE_NAME = "AUDIT_STATE.json"
FINDINGS_NAME = "FINDINGS.json"
ORIGIN_NAME = "ORIGIN.json"
REPORT_NAME = "FINAL_REPORT.md"
FINALIZATION_NAME = "FINALIZATION.json"
DIAGNOSIS_FREEZE_NAME = "DIAGNOSIS_FREEZE.json"
AUDIT_BOUNDARY = (
    "This editorial audit did not independently validate proof correctness, "
    "source truth, code behavior, numerical correctness, novelty, scientific "
    "merit, or publication suitability."
)

DIAGNOSTIC_PASSES = [
    "ATOMIC_DOCUMENTARY_CONSISTENCY",
    "FORMAL_OBJECT_AND_CLAIM_CONTRACTS",
    "LOCAL_PRESENTATION",
    "SECTION_JOBS_AND_TRANSITIONS",
    "CROSS_SECTION_CONSISTENCY",
    "CONTRIBUTION_LEDGER",
    "EVALUATIVE_READER_WALKTHROUGH",
    "WHOLE_PAPER_NARRATIVE",
]
DEFAULT_PASS_PLAN = ["ORIENTATION", *DIAGNOSTIC_PASSES, "REVISION_CLOSURE"]
QUICK_SECTION_REFERENCE = "references/quick-section-audit.md"
ARGUMENT_ARCHITECTURE_REFERENCE = "references/argument-architecture.md"
QUICK_SECTION_PASS_TAGS = frozenset(
    {
        "ATOMIC_DOCUMENTARY_CONSISTENCY",
        "FORMAL_OBJECT_AND_CLAIM_CONTRACTS",
        "LOCAL_PRESENTATION",
        "SECTION_JOBS_AND_TRANSITIONS",
    }
)
REPORTING_REFERENCES = (
    "references/reporting-and-validation.md",
    "references/full-audit-operations.md",
    "references/full-audit-data-contract.md",
)
PASS_REQUIRED_REFERENCES = {
    "CONTRIBUTION_LEDGER": (ARGUMENT_ARCHITECTURE_REFERENCE,),
    "WHOLE_PAPER_NARRATIVE": (ARGUMENT_ARCHITECTURE_REFERENCE,),
}
REQUIRED_PROTOCOL_PATHS = frozenset(
    {
        "SKILL.md",
        "references/argument-architecture.md",
        "references/full-audit-data-contract.md",
        "references/full-audit-operations.md",
        "references/quick-section-audit.md",
        "references/reporting-and-validation.md",
        "references/revision-audit.md",
        "references/support-and-author-decisions.md",
        "scripts/writer_audit.py",
    }
)
ALLOWED_PRIORITIES = {"Blocking", "Material", "Local"}
PRIORITY_DISPLAY_LABELS = {
    "Blocking": "Author input required",
    "Material": "Material",
    "Local": "Local",
}
SAFE_EDIT_REMEDIES = {"safe_prose_edit", "safe_presentation_edit"}
ALLOWED_REMEDIES = {*SAFE_EDIT_REMEDIES, "author_decision", "additional_support"}
EXPECTED_LEDGER_HEADERS = [
    "Rank",
    "Contribution",
    "Method object or construction",
    "Formal support",
    "Empirical support",
    "Boundary",
]
ALLOWED_LEDGER_RANKS = {"Co-primary", "Unclear"}
TEXT_SUFFIXES = {
    ".bib",
    ".cls",
    ".csv",
    ".json",
    ".jl",
    ".lyx",
    ".md",
    ".org",
    ".py",
    ".qmd",
    ".r",
    ".rmd",
    ".rnw",
    ".ris",
    ".sty",
    ".tex",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}
IMAGE_SUFFIXES = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".tif", ".tiff"}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
FINDING_ID_RE = re.compile(r"^F-[0-9]{3,9}$")
FORBIDDEN_DASHES = {"\u2013": "U+2013", "\u2014": "U+2014"}


@dataclass(frozen=True)
class Issue:
    code: str
    location: str
    message: str


class AuditError(RuntimeError):
    pass


class AuditJSONError(ValueError):
    pass


def add_issue(issues: list[Issue], code: str, location: str, message: str) -> None:
    issue = Issue(code=code, location=location, message=message)
    if issue not in issues:
        issues.append(issue)


def sorted_issues(issues: Iterable[Issue]) -> list[Issue]:
    return sorted(set(issues), key=lambda item: (item.location, item.code, item.message))


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
        )
        + "\n"
    ).encode("utf-8")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise AuditJSONError(f"Duplicate JSON object key: {key}")
        value[key] = item
    return value


def reject_json_constant(value: str) -> None:
    raise AuditJSONError(f"Non-finite JSON number is not allowed: {value}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_text_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8-sig")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def byte_line_count(data: bytes) -> int:
    normalized = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if not normalized:
        return 0
    return normalized.count(b"\n") + (0 if normalized.endswith(b"\n") else 1)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and HASH_RE.fullmatch(value) is not None


def finding_id_sort_key(value: str) -> tuple[int, str, int, str]:
    digits = value[2:]
    significant = digits.lstrip("0") or "0"
    return len(significant), significant, len(digits), digits


def iter_strings(value: Any, location: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield location, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{location}[{index}]")


def check_forbidden_dashes(value: Any, location: str, issues: list[Issue]) -> None:
    if not isinstance(value, str):
        return
    for character, name in FORBIDDEN_DASHES.items():
        if character in value:
            add_issue(
                issues,
                "FORBIDDEN_DASH",
                location,
                f"Replace forbidden {name} with punctuation or an ordinary hyphen.",
            )


def contains_report_control(text: str) -> bool:
    return any(
        ord(character) < 32
        or 127 <= ord(character) <= 159
        or character in {"\u2028", "\u2029"}
        for character in text
    )


def check_report_controls(value: Any, issues: list[Issue]) -> None:
    for location, text in iter_strings(value):
        if contains_report_control(text):
            add_issue(
                issues,
                "FORBIDDEN_CONTROL",
                location,
                "Authored report text must be single-line and contain no control characters.",
            )


def check_exact_keys(
    value: dict[str, Any],
    expected: set[str],
    location: str,
    issues: list[Issue],
) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    for key in missing:
        add_issue(issues, "FIELD_MISSING", f"{location}.{key}", "Required field is missing.")
    for key in extra:
        add_issue(issues, "FIELD_UNKNOWN", f"{location}.{key}", "Unknown field is not allowed.")


def safe_relative_path(root: Path, raw: str, location: str, issues: list[Issue]) -> Path | None:
    if not is_nonempty_string(raw):
        add_issue(issues, "PATH_REQUIRED", location, "Record a nonempty relative path.")
        return None
    if "\\" in raw or "\x00" in raw or re.search(r"(?:^|/)[A-Za-z]:", raw):
        add_issue(
            issues,
            "PATH_NONPORTABLE",
            location,
            "Use a canonical POSIX-style relative path with forward slashes.",
        )
        return None
    candidate = PurePosixPath(raw)
    if candidate.is_absolute():
        add_issue(issues, "PATH_ABSOLUTE", location, "Audit records must use relative paths.")
        return None
    if not candidate.parts or ".." in candidate.parts:
        add_issue(issues, "PATH_ESCAPE", location, "Recorded path escapes the audit root.")
        return None
    if candidate.as_posix() != raw or any(part in {"", "."} for part in candidate.parts):
        add_issue(
            issues,
            "PATH_NONCANONICAL",
            location,
            "Use a normalized POSIX-style relative path.",
        )
        return None
    resolved_root = root.resolve()
    resolved = resolved_root.joinpath(*candidate.parts).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        add_issue(issues, "PATH_ESCAPE", location, "Recorded path escapes the audit root.")
        return None
    return resolved


def write_exclusive(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    created_here = False
    try:
        with path.open("xb") as handle:
            created_here = True
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return "created"
    except FileExistsError:
        if path.is_file() and path.read_bytes() == data:
            return "existing_identical"
        raise AuditError(f"Refusing to overwrite existing different file: {path}")
    except OSError:
        try:
            if created_here and path.is_file():
                path.unlink()
        except OSError:
            pass
        raise


def preflight_exclusive(path: Path, data: bytes) -> str:
    if not path.exists():
        return "created"
    if path.is_file() and path.read_bytes() == data:
        return "existing_identical"
    raise AuditError(f"Refusing to overwrite existing different file: {path}")


def read_json(path: Path, issues: list[Issue], label: str) -> Any | None:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(
                handle,
                object_pairs_hook=reject_duplicate_keys,
                parse_constant=reject_json_constant,
            )
    except FileNotFoundError:
        add_issue(issues, f"{label}_MISSING", str(path), "Required audit file is missing.")
    except json.JSONDecodeError as exc:
        add_issue(
            issues,
            f"{label}_JSON_INVALID",
            f"{path}:{exc.lineno}:{exc.colno}",
            exc.msg,
        )
    except AuditJSONError as exc:
        add_issue(issues, f"{label}_JSON_INVALID", str(path), str(exc))
    except OSError as exc:
        add_issue(issues, f"{label}_READ", str(path), str(exc))
    return None


def source_kind(path: Path, override: str | None = None) -> str:
    if override is not None:
        return override
    suffix = path.suffix.casefold()
    if suffix in TEXT_SUFFIXES:
        return "text"
    if suffix == ".pdf":
        return "pdf"
    if suffix in IMAGE_SUFFIXES:
        return "image"
    return "artifact"


def parse_path_assignments(
    values: Sequence[str], label: str, allowed: set[str] | None = None
) -> dict[Path, str]:
    result: dict[Path, str] = {}
    for raw in values:
        path_text, separator, value = raw.rpartition("=")
        if not separator or not path_text.strip() or not value.strip():
            raise AuditError(f"{label} must use SOURCE=VALUE: {raw}")
        path = Path(path_text).resolve()
        value = value.strip()
        if allowed is not None and value not in allowed:
            raise AuditError(
                f"{label} value must be one of {', '.join(sorted(allowed))}: {value}"
            )
        if path in result:
            raise AuditError(f"Duplicate {label} override for source: {path}")
        result[path] = value
    return result


def detect_pdf_page_count(data: bytes, source_label: Path, override: str | None) -> int:
    if override is not None:
        try:
            count = int(override)
        except ValueError as exc:
            raise AuditError(f"PDF page count must be a positive integer: {override}") from exc
        if count < 1:
            raise AuditError(f"PDF page count must be positive: {override}")
        return count
    reader_class: Any | None = None
    try:
        from pypdf import PdfReader as reader_class
    except ModuleNotFoundError:
        try:
            from PyPDF2 import PdfReader as reader_class
        except ModuleNotFoundError:
            reader_class = None
    if reader_class is None:
        raise AuditError(
            "A PDF source requires pypdf, PyPDF2, or "
            f"--pdf-page-count \"{source_label}=N\"."
        )
    try:
        count = len(reader_class(io.BytesIO(data)).pages)
    except Exception as exc:
        raise AuditError(
            "Could not verify PDF page count for "
            f"{source_label}: {exc}. Supply --pdf-page-count \"{source_label}=N\"."
        ) from exc
    if count < 1:
        raise AuditError(f"PDF source has no readable pages: {source_label}")
    return count


def snapshot_path(source_id: str, path: Path, kind: str) -> str:
    suffix = path.suffix.casefold()
    if re.fullmatch(r"\.[a-z0-9]{1,16}", suffix) is None:
        suffix = {"text": ".txt", "pdf": ".pdf", "image": ".img"}.get(
            kind, ".bin"
        )
    return f"inputs/{source_id}{suffix}"


def protocol_snapshot_path(logical_path: str) -> str:
    return (PurePosixPath("protocol") / PurePosixPath(logical_path)).as_posix()


def display_text(value: str) -> str:
    normalized = "".join(
        " " if contains_report_control(character) else character
        for character in value
    )
    return " ".join(normalized.split())


def protocol_files(skill_root: Path) -> list[tuple[str, Path]]:
    files = [("SKILL.md", skill_root / "SKILL.md")]
    files.extend(
        (f"references/{path.name}", path)
        for path in sorted((skill_root / "references").glob("*.md"))
    )
    files.append(("scripts/writer_audit.py", skill_root / "scripts" / "writer_audit.py"))
    missing = [logical for logical, path in files if not path.is_file()]
    if missing:
        raise AuditError("Missing required protocol files: " + ", ".join(missing))
    return files


def build_pass_plan(action: str, focused_passes: Sequence[str]) -> list[dict[str, str]]:
    if focused_passes:
        if len(set(focused_passes)) != len(focused_passes):
            raise AuditError("Focused pass tags must be unique.")
        unknown = [tag for tag in focused_passes if tag not in DIAGNOSTIC_PASSES]
        if unknown:
            raise AuditError("Unknown focused pass tag(s): " + ", ".join(unknown))
        diagnostic = list(focused_passes)
    else:
        diagnostic = list(DIAGNOSTIC_PASSES)

    plan = [{"tag": "ORIENTATION", "kind": "descriptive", "requirement": "required"}]
    for tag in diagnostic:
        requirement = (
            "conditional"
            if not focused_passes and tag == "CONTRIBUTION_LEDGER"
            else "required"
        )
        plan.append({"tag": tag, "kind": "evaluative", "requirement": requirement})
    plan.append(
        {
            "tag": "REVISION_CLOSURE",
            "kind": "evaluative",
            "requirement": "required" if action == "audit-and-revise" else "not_required",
        }
    )
    return plan


def manifest_projection(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": manifest.get("schema_version"),
        "contract_version": manifest.get("contract_version"),
        "scope": manifest.get("scope"),
        "sources": manifest.get("sources"),
        "protocol": manifest.get("protocol"),
        "pass_plan": manifest.get("pass_plan"),
    }


def semantic_binding(manifest: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(manifest_projection(manifest)))


def initial_state(
    binding: str,
    action: str,
    pass_plan: Sequence[dict[str, str]],
) -> dict[str, Any]:
    passes: list[dict[str, Any]] = []
    for entry in pass_plan:
        not_required = entry["requirement"] == "not_required"
        passes.append(
            {
                "tag": entry["tag"],
                "kind": entry["kind"],
                "requirement": entry["requirement"],
                "status": "not_required" if not_required else "pending",
                "binding_sha256": binding,
                "loaded_references": [],
                "checkpoint": None,
                "reason": "Audit-only run; manuscript revision was not authorized."
                if not_required
                else None,
            }
        )
    edits = (
        {
            "applied": False,
            "diff_status": "not_applicable",
            "evidence": "Audit-only run; no manuscript files were changed.",
            "artifact": None,
            "finding_dispositions": [],
        }
        if action == "audit"
        else {
            "applied": None,
            "diff_status": None,
            "evidence": None,
            "artifact": None,
            "finding_dispositions": None,
        }
    )
    closure_phase = "audit" if action == "audit" else "baseline"
    return {
        "schema_version": SCHEMA_VERSION,
        "semantic_binding_sha256": binding,
        "passes": passes,
        "reporting": {
            "status": "pending",
            "binding_sha256": binding,
            "loaded_references": [],
            "checkpoint": None,
        },
        "closure": {
            "compile": {
                "phase": closure_phase,
                "status": None,
                "evidence": None,
                "artifact": None,
            },
            "render": {
                "phase": closure_phase,
                "status": None,
                "evidence": None,
                "artifact": None,
            },
            "edits": edits,
        },
    }


def initial_findings(binding: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "semantic_binding_sha256": binding,
        "assessment": {"status": None, "boundary": None},
        "findings": [],
        "contribution_ledger": {
            "status": None,
            "reason": None,
            "blocking_finding_ids": [],
            "rows": [],
        },
    }


def initialize_audit(args: argparse.Namespace) -> dict[str, Any]:
    audit_root = args.audit_root.resolve()
    skill_root = args.skill_root.resolve()
    sources = [path.resolve() for path in args.source]
    if not sources:
        raise AuditError("At least one --source is required.")
    missing = [str(path) for path in sources if not path.is_file()]
    if missing:
        raise AuditError("Source file(s) do not exist: " + ", ".join(missing))
    if len(set(sources)) != len(sources):
        raise AuditError("The same source path was supplied more than once.")
    if audit_root.exists():
        raise AuditError(f"Refusing to scaffold over existing path: {audit_root}")

    kind_overrides = parse_path_assignments(
        getattr(args, "source_kind", []),
        "--source-kind",
        {"text", "pdf", "image", "artifact"},
    )
    page_overrides = parse_path_assignments(
        getattr(args, "pdf_page_count", []), "--pdf-page-count"
    )
    for override_path in {*kind_overrides, *page_overrides}:
        if override_path not in sources:
            raise AuditError(f"Override path is not a declared --source: {override_path}")

    if args.focused_pass and not is_nonempty_string(args.focus):
        raise AuditError("--focus is required when --focused-pass is used.")
    focus = args.focus if is_nonempty_string(args.focus) else DEFAULT_FOCUS
    if contains_report_control(focus):
        raise AuditError("--focus must be single-line and contain no control characters.")

    protocol_inputs = protocol_files(skill_root)
    pass_plan = build_pass_plan(args.action, args.focused_pass)
    scope = {
        "mode": "Full",
        "action": args.action,
        "focus": focus,
        "plan_kind": "focused" if args.focused_pass else "default",
        "order_override": bool(args.focused_pass),
        "focused_passes": list(args.focused_pass),
        "source_ids": [f"SRC-{index:03d}" for index in range(1, len(sources) + 1)],
    }

    source_records: list[dict[str, Any]] = []
    origins: list[dict[str, str]] = []
    source_payloads: list[tuple[str, bytes]] = []
    for index, source in enumerate(sources, start=1):
        source_id = f"SRC-{index:03d}"
        data = source.read_bytes()
        kind = source_kind(source, kind_overrides.get(source))
        page_count = (
            detect_pdf_page_count(data, source, page_overrides.get(source))
            if kind == "pdf"
            else None
        )
        if source in page_overrides and kind != "pdf":
            raise AuditError(f"PDF page-count override targets a non-PDF source: {source}")
        snapshot_rel = snapshot_path(source_id, source, kind)
        source_payloads.append((snapshot_rel, data))
        record: dict[str, Any] = {
            "source_id": source_id,
            "kind": kind,
            "name": source.name,
            "snapshot_path": snapshot_rel,
            "sha256": sha256_bytes(data),
            "byte_size": len(data),
            "line_count": byte_line_count(data) if kind == "text" else None,
            "page_count": page_count,
        }
        source_records.append(record)
        origins.append({"source_id": source_id, "original_path": str(source)})

    protocol_records: list[dict[str, Any]] = []
    protocol_payloads: list[tuple[str, bytes]] = []
    for logical_path, source in protocol_inputs:
        data = normalized_text_bytes(source)
        snapshot_rel = protocol_snapshot_path(logical_path)
        protocol_payloads.append((snapshot_rel, data))
        protocol_records.append(
            {
                "logical_path": logical_path,
                "snapshot_path": snapshot_rel,
                "sha256": sha256_bytes(data),
                "byte_size": len(data),
            }
        )

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "scope": scope,
        "sources": source_records,
        "protocol": protocol_records,
        "pass_plan": pass_plan,
        "semantic_binding_sha256": None,
    }
    binding = semantic_binding(manifest)
    manifest["semantic_binding_sha256"] = binding
    state = initial_state(binding, args.action, pass_plan)
    findings = initial_findings(binding)
    origin = {
        "schema_version": SCHEMA_VERSION,
        "audit_root_at_init": str(audit_root),
        "skill_root_at_init": str(skill_root),
        "sources": origins,
    }

    audit_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".writer-audit-stage-", dir=audit_root.parent))
    try:
        (stage / "inputs").mkdir()
        (stage / "protocol").mkdir()
        (stage / "artifacts").mkdir()
        for relative, data in source_payloads:
            write_exclusive(stage / relative, data)
        for relative, data in protocol_payloads:
            write_exclusive(stage / relative, data)
        write_exclusive(stage / MANIFEST_NAME, canonical_json_bytes(manifest))
        write_exclusive(stage / STATE_NAME, canonical_json_bytes(state))
        write_exclusive(stage / FINDINGS_NAME, canonical_json_bytes(findings))
        write_exclusive(stage / ORIGIN_NAME, canonical_json_bytes(origin))
        stage.rename(audit_root)
        stage = None
    finally:
        if stage is not None and stage.exists():
            resolved_stage = stage.resolve()
            resolved_parent = audit_root.parent.resolve()
            if (
                resolved_stage.parent == resolved_parent
                and resolved_stage.name.startswith(".writer-audit-stage-")
            ):
                shutil.rmtree(resolved_stage)
    return {
        "initialized": True,
        "audit_root": str(audit_root),
        "semantic_binding_sha256": binding,
        "sources": len(source_records),
        "protocol_files": len(protocol_records),
        "pass_plan": [entry["tag"] for entry in pass_plan],
    }


def validate_manifest(manifest: Any, audit_root: Path) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(manifest, dict):
        add_issue(issues, "MANIFEST_ROOT", "$", "Manifest must be a JSON object.")
        return issues
    check_exact_keys(
        manifest,
        {
            "schema_version",
            "contract_version",
            "scope",
            "sources",
            "protocol",
            "pass_plan",
            "semantic_binding_sha256",
        },
        "$",
        issues,
    )
    if manifest.get("schema_version") != SCHEMA_VERSION:
        add_issue(
            issues,
            "MANIFEST_SCHEMA",
            "$.schema_version",
            f"Expected schema_version {SCHEMA_VERSION}.",
        )
    if manifest.get("contract_version") != CONTRACT_VERSION:
        add_issue(
            issues,
            "MANIFEST_CONTRACT",
            "$.contract_version",
            f"Expected contract_version {CONTRACT_VERSION}.",
        )

    scope = manifest.get("scope")
    if not isinstance(scope, dict):
        add_issue(issues, "MANIFEST_SCOPE", "$.scope", "scope must be an object.")
        scope = {}
    else:
        check_exact_keys(
            scope,
            {
                "mode",
                "action",
                "focus",
                "plan_kind",
                "order_override",
                "focused_passes",
                "source_ids",
            },
            "$.scope",
            issues,
        )
    if scope.get("mode") != "Full":
        add_issue(issues, "MANIFEST_MODE", "$.scope.mode", "Harness mode must be Full.")
    action = scope.get("action")
    if not isinstance(action, str) or action not in ("audit", "audit-and-revise"):
        add_issue(
            issues,
            "MANIFEST_ACTION",
            "$.scope.action",
            "action must be audit or audit-and-revise.",
        )
    if not is_nonempty_string(scope.get("focus")):
        add_issue(issues, "MANIFEST_FOCUS", "$.scope.focus", "Record the audit focus.")
    elif contains_report_control(scope["focus"]):
        add_issue(
            issues,
            "FORBIDDEN_CONTROL",
            "$.scope.focus",
            "Audit focus must be single-line and contain no control characters.",
        )
    focused = scope.get("focused_passes")
    if not isinstance(focused, list) or any(not is_nonempty_string(tag) for tag in focused):
        add_issue(
            issues,
            "MANIFEST_FOCUSED_PASSES",
            "$.scope.focused_passes",
            "focused_passes must be a list of pass tags.",
        )
        focused = []
    plan_kind = scope.get("plan_kind")
    expected_kind = "focused" if focused else "default"
    if plan_kind != expected_kind:
        add_issue(
            issues,
            "MANIFEST_PLAN_KIND",
            "$.scope.plan_kind",
            f"plan_kind must be {expected_kind}.",
        )
    if scope.get("order_override") != bool(focused):
        add_issue(
            issues,
            "MANIFEST_ORDER_OVERRIDE",
            "$.scope.order_override",
            "order_override must match whether focused passes were selected.",
        )

    sources = manifest.get("sources")
    source_ids: list[str] = []
    if not isinstance(sources, list) or not sources:
        add_issue(issues, "MANIFEST_SOURCES", "$.sources", "Record at least one source.")
        sources = []
    for index, source in enumerate(sources):
        location = f"$.sources[{index}]"
        if not isinstance(source, dict):
            add_issue(issues, "SOURCE_RECORD", location, "Source record must be an object.")
            continue
        check_exact_keys(
            source,
            {
                "source_id",
                "kind",
                "name",
                "snapshot_path",
                "sha256",
                "byte_size",
                "line_count",
                "page_count",
            },
            location,
            issues,
        )
        source_id = source.get("source_id")
        expected_source_id = f"SRC-{index + 1:03d}"
        if source_id != expected_source_id:
            add_issue(
                issues,
                "SOURCE_ID",
                f"{location}.source_id",
                f"Source ID must be {expected_source_id}.",
            )
        else:
            source_ids.append(source_id)
        kind = source.get("kind")
        if not isinstance(kind, str) or kind not in ("text", "pdf", "image", "artifact"):
            add_issue(
                issues,
                "SOURCE_KIND",
                f"{location}.kind",
                "kind must be text, pdf, image, or artifact.",
            )
        if not is_nonempty_string(source.get("name")):
            add_issue(issues, "SOURCE_NAME", f"{location}.name", "Record the source name.")
        if not is_sha256(source.get("sha256")):
            add_issue(issues, "SOURCE_HASH", f"{location}.sha256", "Record a SHA-256 hash.")
        if not isinstance(source.get("byte_size"), int) or isinstance(
            source.get("byte_size"), bool
        ) or source.get("byte_size", -1) < 0:
            add_issue(
                issues,
                "SOURCE_SIZE",
                f"{location}.byte_size",
                "byte_size must be a nonnegative integer.",
            )
        line_count = source.get("line_count")
        if kind == "text":
            if not isinstance(line_count, int) or isinstance(line_count, bool) or line_count < 0:
                add_issue(
                    issues,
                    "SOURCE_LINE_COUNT",
                    f"{location}.line_count",
                    "Text sources require a nonnegative line_count.",
                )
        elif line_count is not None:
            add_issue(
                issues,
                "SOURCE_LINE_COUNT_KIND",
                f"{location}.line_count",
                "Nontext sources must use null line_count.",
            )
        page_count = source.get("page_count")
        if kind == "pdf":
            if (
                not isinstance(page_count, int)
                or isinstance(page_count, bool)
                or page_count < 1
            ):
                add_issue(
                    issues,
                    "SOURCE_PAGE_COUNT",
                    f"{location}.page_count",
                    "PDF sources require a positive page_count.",
                )
        elif page_count is not None:
            add_issue(
                issues,
                "SOURCE_PAGE_COUNT_KIND",
                f"{location}.page_count",
                "Non-PDF sources must use null page_count.",
            )
        if (
            source_id == expected_source_id
            and isinstance(kind, str)
            and kind in ("text", "pdf", "image", "artifact")
            and is_nonempty_string(source.get("name"))
        ):
            expected_snapshot = snapshot_path(source_id, Path(source["name"]), kind)
            if source.get("snapshot_path") != expected_snapshot:
                add_issue(
                    issues,
                    "SOURCE_SNAPSHOT_PATH",
                    f"{location}.snapshot_path",
                    f"Snapshot path must be {expected_snapshot}.",
                )
        path = safe_relative_path(
            audit_root, source.get("snapshot_path"), f"{location}.snapshot_path", issues
        )
        if path is not None:
            if not path.is_file():
                add_issue(issues, "SOURCE_SNAPSHOT_MISSING", str(path), "Snapshot is missing.")
            else:
                data = path.read_bytes()
                if is_sha256(source.get("sha256")) and sha256_bytes(data) != source["sha256"]:
                    add_issue(
                        issues,
                        "SOURCE_SNAPSHOT_DRIFT",
                        f"{location}.sha256",
                        "Source snapshot hash does not match the manifest.",
                    )
                if isinstance(source.get("byte_size"), int) and len(data) != source["byte_size"]:
                    add_issue(
                        issues,
                        "SOURCE_SIZE_DRIFT",
                        f"{location}.byte_size",
                        "Source snapshot size does not match the manifest.",
                    )
                if kind == "text" and isinstance(line_count, int):
                    if byte_line_count(data) != line_count:
                        add_issue(
                            issues,
                            "SOURCE_LINE_DRIFT",
                            f"{location}.line_count",
                            "Source snapshot line count does not match the manifest.",
                        )
    if len(source_ids) != len(set(source_ids)):
        add_issue(issues, "SOURCE_ID_DUPLICATE", "$.sources", "Source IDs must be unique.")
    if scope.get("source_ids") != source_ids:
        add_issue(
            issues,
            "SOURCE_SCOPE_MISMATCH",
            "$.scope.source_ids",
            "scope.source_ids must exactly match the source records in order.",
        )

    protocol = manifest.get("protocol")
    logical_paths: list[str] = []
    protocol_snapshot_targets: list[str] = []
    protocol_snapshot_identities: list[tuple[int, int]] = []
    if not isinstance(protocol, list) or not protocol:
        add_issue(
            issues,
            "MANIFEST_PROTOCOL",
            "$.protocol",
            "Record the protocol snapshot set.",
        )
        protocol = []
    for index, record in enumerate(protocol):
        location = f"$.protocol[{index}]"
        if not isinstance(record, dict):
            add_issue(issues, "PROTOCOL_RECORD", location, "Protocol record must be an object.")
            continue
        check_exact_keys(
            record,
            {"logical_path", "snapshot_path", "sha256", "byte_size"},
            location,
            issues,
        )
        logical = record.get("logical_path")
        logical_target: Path | None = None
        if not is_nonempty_string(logical):
            add_issue(
                issues,
                "PROTOCOL_LOGICAL_PATH",
                f"{location}.logical_path",
                "Record the logical protocol path.",
            )
        else:
            logical_target = safe_relative_path(
                audit_root / "protocol",
                logical,
                f"{location}.logical_path",
                issues,
            )
        if is_nonempty_string(logical) and logical_target is not None:
            logical_paths.append(logical)
            expected_snapshot = protocol_snapshot_path(logical)
            if record.get("snapshot_path") != expected_snapshot:
                add_issue(
                    issues,
                    "PROTOCOL_SNAPSHOT_PATH",
                    f"{location}.snapshot_path",
                    f"Snapshot path must be {expected_snapshot}.",
                )
        if not is_sha256(record.get("sha256")):
            add_issue(issues, "PROTOCOL_HASH", f"{location}.sha256", "Record a SHA-256 hash.")
        if not isinstance(record.get("byte_size"), int) or isinstance(
            record.get("byte_size"), bool
        ) or record.get("byte_size", -1) < 0:
            add_issue(
                issues,
                "PROTOCOL_SIZE",
                f"{location}.byte_size",
                "byte_size must be a nonnegative integer.",
            )
        path = safe_relative_path(
            audit_root, record.get("snapshot_path"), f"{location}.snapshot_path", issues
        )
        if path is not None:
            protocol_snapshot_targets.append(os.path.normcase(os.fspath(path)))
            if not path.is_file():
                add_issue(issues, "PROTOCOL_SNAPSHOT_MISSING", str(path), "Snapshot is missing.")
            else:
                snapshot_stat = path.stat()
                protocol_snapshot_identities.append(
                    (snapshot_stat.st_dev, snapshot_stat.st_ino)
                )
                data = path.read_bytes()
                if is_sha256(record.get("sha256")) and sha256_bytes(data) != record["sha256"]:
                    add_issue(
                        issues,
                        "PROTOCOL_SNAPSHOT_DRIFT",
                        f"{location}.sha256",
                        "Protocol snapshot hash does not match the manifest.",
                    )
                if isinstance(record.get("byte_size"), int) and len(data) != record["byte_size"]:
                    add_issue(
                        issues,
                        "PROTOCOL_SIZE_DRIFT",
                        f"{location}.byte_size",
                        "Protocol snapshot size does not match the manifest.",
                    )
    if len(logical_paths) != len(set(logical_paths)):
        add_issue(
            issues,
            "PROTOCOL_PATH_DUPLICATE",
            "$.protocol",
            "Protocol logical paths must be unique.",
        )
    if (
        len(protocol_snapshot_targets) != len(set(protocol_snapshot_targets))
        or len(protocol_snapshot_identities) != len(set(protocol_snapshot_identities))
    ):
        add_issue(
            issues,
            "PROTOCOL_SNAPSHOT_DUPLICATE",
            "$.protocol",
            "Protocol snapshot paths must resolve to unique files.",
        )
    for required in REQUIRED_PROTOCOL_PATHS:
        if required not in logical_paths:
            add_issue(
                issues,
                "PROTOCOL_REQUIRED_MISSING",
                "$.protocol",
                f"Required protocol snapshot is missing: {required}.",
            )

    pass_plan = manifest.get("pass_plan")
    if not isinstance(pass_plan, list):
        add_issue(issues, "MANIFEST_PASS_PLAN", "$.pass_plan", "pass_plan must be a list.")
        pass_plan = []
    try:
        expected_plan = (
            build_pass_plan(action, focused)
            if isinstance(action, str) and action in ("audit", "audit-and-revise")
            else []
        )
    except AuditError as exc:
        add_issue(issues, "MANIFEST_PASS_PLAN", "$.pass_plan", str(exc))
        expected_plan = []
    if pass_plan != expected_plan:
        add_issue(
            issues,
            "MANIFEST_PASS_PLAN",
            "$.pass_plan",
            "pass_plan does not match the declared action and focus.",
        )

    binding = manifest.get("semantic_binding_sha256")
    if not is_sha256(binding):
        add_issue(
            issues,
            "MANIFEST_BINDING",
            "$.semantic_binding_sha256",
            "Record the semantic binding SHA-256.",
        )
    elif binding != semantic_binding(manifest):
        add_issue(
            issues,
            "MANIFEST_BINDING_DRIFT",
            "$.semantic_binding_sha256",
            "Semantic binding does not match the manifest projection.",
        )
    return issues


def validate_bound_artifact(
    value: Any,
    audit_root: Path,
    location: str,
    issues: list[Issue],
    required: bool,
) -> None:
    if value is None:
        if required:
            add_issue(issues, "ARTIFACT_REQUIRED", location, "A bound artifact is required.")
        return
    if not isinstance(value, dict):
        add_issue(issues, "ARTIFACT_TYPE", location, "Artifact binding must be an object.")
        return
    check_exact_keys(value, {"path", "sha256"}, location, issues)
    if not is_sha256(value.get("sha256")):
        add_issue(issues, "ARTIFACT_HASH", f"{location}.sha256", "Record a SHA-256 hash.")
    path = safe_relative_path(audit_root, value.get("path"), f"{location}.path", issues)
    if path is not None:
        try:
            path.relative_to((audit_root / "artifacts").resolve())
        except ValueError:
            add_issue(
                issues,
                "ARTIFACT_LOCATION",
                f"{location}.path",
                "Closure evidence must be a file under artifacts/.",
            )
        if not path.is_file():
            add_issue(issues, "ARTIFACT_MISSING", str(path), "Bound artifact is missing.")
        elif is_sha256(value.get("sha256")) and sha256_file(path) != value["sha256"]:
            add_issue(
                issues,
                "ARTIFACT_DRIFT",
                f"{location}.sha256",
                "Bound artifact hash does not match the record.",
            )


def validate_stage(
    value: Any,
    stage: str,
    audit_root: Path,
    issues: list[Issue],
    final: bool,
    location_root: str = "$.closure",
    expected_phase: str | None = None,
) -> None:
    location = f"{location_root}.{stage}"
    if not isinstance(value, dict):
        add_issue(issues, "CLOSURE_STAGE", location, "Closure stage must be an object.")
        return
    check_exact_keys(value, {"phase", "status", "evidence", "artifact"}, location, issues)
    check_forbidden_dashes(value.get("evidence"), f"{location}.evidence", issues)
    phase = value.get("phase")
    if not isinstance(phase, str) or phase not in ("audit", "baseline", "post_edit"):
        add_issue(
            issues,
            "CLOSURE_PHASE",
            f"{location}.phase",
            "phase must be audit, baseline, or post_edit.",
        )
    elif expected_phase is not None and phase != expected_phase:
        add_issue(
            issues,
            "CLOSURE_PHASE_MISMATCH",
            f"{location}.phase",
            f"{stage} phase must be {expected_phase}.",
        )
    allowed = (
        {"passed", "failed", "not_run", "unavailable"}
        if stage == "compile"
        else {"inspected", "failed", "not_run", "unavailable"}
    )
    status = value.get("status")
    if status is None:
        if final:
            add_issue(issues, "CLOSURE_PENDING", f"{location}.status", "Resolve closure status.")
        return
    if not isinstance(status, str) or status not in allowed:
        add_issue(
            issues,
            "CLOSURE_STATUS",
            f"{location}.status",
            "Invalid closure status.",
        )
        return
    if not is_nonempty_string(value.get("evidence")):
        add_issue(
            issues,
            "CLOSURE_EVIDENCE",
            f"{location}.evidence",
            "Record an artifact result or substantive reason.",
        )
    if status == "failed":
        add_issue(
            issues,
            f"CLOSURE_{stage.upper()}_FAILED",
            f"{location}.status",
            f"{stage} failed; the audit cannot be final.",
        )
    require_artifact = status in ("passed", "inspected")
    if status in ("not_run", "unavailable") and value.get("artifact") is not None:
        add_issue(
            issues,
            "CLOSURE_ARTIFACT_UNEXPECTED",
            f"{location}.artifact",
            "not_run and unavailable stages must not bind an artifact.",
        )
    validate_bound_artifact(
        value.get("artifact"), audit_root, f"{location}.artifact", issues, require_artifact
    )


def validate_disposition_records(
    value: Any,
    action: str | None,
    final: bool,
    issues: list[Issue],
) -> list[dict[str, Any]]:
    location = "$.closure.edits.finding_dispositions"
    if action == "audit":
        if value != []:
            add_issue(
                issues,
                "CLOSURE_AUDIT_ONLY_DISPOSITIONS",
                location,
                "Audit-only scope must use an empty finding-disposition list.",
            )
        return []
    if value is None:
        if final and action == "audit-and-revise":
            add_issue(
                issues,
                "CLOSURE_DISPOSITIONS_PENDING",
                location,
                "Resolve finding dispositions before finalization.",
            )
        return []
    if not isinstance(value, list):
        add_issue(
            issues,
            "CLOSURE_DISPOSITIONS_TYPE",
            location,
            "finding_dispositions must be null or a list.",
        )
        return []

    records: list[dict[str, Any]] = []
    valid_ids: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(value):
        record_location = f"{location}[{index}]"
        if not isinstance(record, dict):
            add_issue(
                issues,
                "CLOSURE_DISPOSITION_TYPE",
                record_location,
                "A finding disposition must be an object.",
            )
            continue
        records.append(record)
        check_exact_keys(
            record,
            {"finding_id", "outcome", "reason"},
            record_location,
            issues,
        )
        check_forbidden_dashes(
            record.get("reason"), f"{record_location}.reason", issues
        )
        finding_id = record.get("finding_id")
        if not isinstance(finding_id, str) or FINDING_ID_RE.fullmatch(finding_id) is None:
            add_issue(
                issues,
                "CLOSURE_DISPOSITION_ID",
                f"{record_location}.finding_id",
                "Disposition finding_id must use the canonical bounded finding-ID form.",
            )
        elif finding_id in seen:
            add_issue(
                issues,
                "CLOSURE_DISPOSITION_ID_DUPLICATE",
                f"{record_location}.finding_id",
                "Disposition finding IDs must be unique.",
            )
        else:
            seen.add(finding_id)
            valid_ids.append(finding_id)
        outcome = record.get("outcome")
        if not isinstance(outcome, str) or outcome not in (
            "applied",
            "unapplied",
            "unresolved",
        ):
            add_issue(
                issues,
                "CLOSURE_DISPOSITION_OUTCOME",
                f"{record_location}.outcome",
                "outcome must be applied, unapplied, or unresolved.",
            )
        if not is_nonempty_string(record.get("reason")):
            add_issue(
                issues,
                "CLOSURE_DISPOSITION_REASON",
                f"{record_location}.reason",
                "Every finding disposition needs a substantive reason.",
            )
    if valid_ids != sorted(valid_ids, key=finding_id_sort_key):
        add_issue(
            issues,
            "CLOSURE_DISPOSITION_ORDER",
            location,
            "Finding dispositions must use canonical finding-ID order.",
        )
    return records


def validate_state(
    state: Any,
    manifest: dict[str, Any],
    audit_root: Path,
    final: bool,
) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(state, dict):
        add_issue(issues, "STATE_ROOT", "$", "State must be a JSON object.")
        return issues
    check_report_controls(state, issues)
    check_exact_keys(
        state,
        {"schema_version", "semantic_binding_sha256", "passes", "reporting", "closure"},
        "$",
        issues,
    )
    if state.get("schema_version") != SCHEMA_VERSION:
        add_issue(issues, "STATE_SCHEMA", "$.schema_version", "State schema is invalid.")
    binding = manifest.get("semantic_binding_sha256")
    if state.get("semantic_binding_sha256") != binding:
        add_issue(
            issues,
            "STATE_BINDING",
            "$.semantic_binding_sha256",
            "State binding does not match the manifest.",
        )

    protocol_records = manifest.get("protocol")
    if not isinstance(protocol_records, list):
        protocol_records = []
    protocol_paths = {
        item.get("logical_path")
        for item in protocol_records
        if isinstance(item, dict) and is_nonempty_string(item.get("logical_path"))
    }
    plan = manifest.get("pass_plan")
    if not isinstance(plan, list):
        plan = []
    passes = state.get("passes")
    if not isinstance(passes, list):
        add_issue(issues, "STATE_PASSES", "$.passes", "passes must be a list.")
        passes = []
    if len(passes) != len(plan):
        add_issue(
            issues,
            "STATE_PASS_COUNT",
            "$.passes",
            "State passes must exactly mirror the manifest pass plan.",
        )
    for index, expected in enumerate(plan):
        location = f"$.passes[{index}]"
        if not isinstance(expected, dict):
            add_issue(
                issues,
                "STATE_PASS_PLAN_RECORD",
                location,
                "Manifest pass-plan record must be an object.",
            )
            continue
        if index >= len(passes) or not isinstance(passes[index], dict):
            add_issue(issues, "STATE_PASS_RECORD", location, "Pass record is missing.")
            continue
        record = passes[index]
        check_exact_keys(
            record,
            {
                "tag",
                "kind",
                "requirement",
                "status",
                "binding_sha256",
                "loaded_references",
                "checkpoint",
                "reason",
            },
            location,
            issues,
        )
        for field in ("checkpoint", "reason"):
            check_forbidden_dashes(
                record.get(field), f"{location}.{field}", issues
            )
        for key in {"tag", "kind", "requirement"}:
            if record.get(key) != expected.get(key):
                add_issue(
                    issues,
                    "STATE_PASS_PLAN_MISMATCH",
                    f"{location}.{key}",
                    "Pass record does not match the manifest plan.",
                )
        if record.get("binding_sha256") != binding:
            add_issue(
                issues,
                "STATE_PASS_BINDING",
                f"{location}.binding_sha256",
                "Pass binding does not match the manifest.",
            )
        status = record.get("status")
        if not isinstance(status, str) or status not in (
            "pending",
            "completed",
            "not_required",
        ):
            add_issue(
                issues,
                "STATE_PASS_STATUS",
                f"{location}.status",
                "status must be pending, completed, or not_required.",
            )
            continue
        if final and status == "pending":
            add_issue(
                issues,
                "STATE_PASS_PENDING",
                f"{location}.status",
                "Resolve every selected or conditional pass before finalization.",
            )
        if expected.get("requirement") == "required" and status == "not_required":
            add_issue(
                issues,
                "STATE_REQUIRED_PASS_SKIPPED",
                f"{location}.status",
                "A required pass cannot be not_required.",
            )
        if expected.get("requirement") == "not_required" and status != "not_required":
            add_issue(
                issues,
                "STATE_DECLARED_SKIP_CHANGED",
                f"{location}.status",
                "A pass declared not_required in the manifest must remain not_required.",
            )
        references = record.get("loaded_references")
        if not isinstance(references, list) or any(
            not is_nonempty_string(item) for item in references
        ):
            add_issue(
                issues,
                "STATE_PASS_REFERENCES",
                f"{location}.loaded_references",
                "loaded_references must be a list of logical reference paths.",
            )
            references = []
        if len(references) != len(set(references)):
            add_issue(
                issues,
                "STATE_PASS_REFERENCE_DUPLICATE",
                f"{location}.loaded_references",
                "Loaded references must be unique.",
            )
        for reference in references:
            if reference not in protocol_paths or not reference.startswith("references/"):
                add_issue(
                    issues,
                    "STATE_PASS_REFERENCE_UNKNOWN",
                    f"{location}.loaded_references",
                    f"Unknown loaded reference: {reference}.",
                )
        if status == "completed":
            if not is_nonempty_string(record.get("checkpoint")):
                add_issue(
                    issues,
                    "STATE_PASS_CHECKPOINT",
                    f"{location}.checkpoint",
                    "A completed pass needs a compact checkpoint.",
                )
            if not references:
                add_issue(
                    issues,
                    "STATE_PASS_REFERENCES_EMPTY",
                    f"{location}.loaded_references",
                    "A completed pass must record references actually loaded.",
                )
            if record.get("reason") is not None:
                add_issue(
                    issues,
                    "STATE_PASS_REASON_UNEXPECTED",
                    f"{location}.reason",
                    "A completed pass must use null reason.",
                )
        elif status == "not_required":
            if expected.get("requirement") not in ("conditional", "not_required"):
                add_issue(
                    issues,
                    "STATE_PASS_NOT_REQUIRED",
                    f"{location}.status",
                    "Only conditional or declared not-required passes may be skipped.",
                )
            if not is_nonempty_string(record.get("reason")):
                add_issue(
                    issues,
                    "STATE_PASS_REASON",
                    f"{location}.reason",
                    "A not-required pass needs a substantive reason.",
                )
            if references or record.get("checkpoint") is not None:
                add_issue(
                    issues,
                    "STATE_PASS_NOT_REQUIRED_CONTENT",
                    location,
                    "A not-required pass must have no loaded references or checkpoint.",
                )
        if expected.get("tag") == "ORIENTATION" and status == "completed":
            if references != ["references/revision-audit.md"]:
                add_issue(
                    issues,
                    "STATE_ORIENTATION_REFERENCES",
                    f"{location}.loaded_references",
                    "ORIENTATION must load only references/revision-audit.md.",
                )
        if (
            expected.get("tag") in QUICK_SECTION_PASS_TAGS
            and status == "completed"
            and QUICK_SECTION_REFERENCE not in references
        ):
            add_issue(
                issues,
                "STATE_PASS_QUICK_SECTION_REFERENCE",
                f"{location}.loaded_references",
                f"{expected.get('tag')} must load {QUICK_SECTION_REFERENCE}.",
            )
        if status == "completed":
            for required_reference in PASS_REQUIRED_REFERENCES.get(
                expected.get("tag"), ()
            ):
                if required_reference not in references:
                    add_issue(
                        issues,
                        "STATE_PASS_OWNER_REFERENCE",
                        f"{location}.loaded_references",
                        f"{expected.get('tag')} must load {required_reference}.",
                    )

    reporting = state.get("reporting")
    if not isinstance(reporting, dict):
        add_issue(issues, "STATE_REPORTING", "$.reporting", "reporting must be an object.")
    else:
        check_exact_keys(
            reporting,
            {"status", "binding_sha256", "loaded_references", "checkpoint"},
            "$.reporting",
            issues,
        )
        check_forbidden_dashes(
            reporting.get("checkpoint"), "$.reporting.checkpoint", issues
        )
        if reporting.get("binding_sha256") != binding:
            add_issue(
                issues,
                "STATE_REPORTING_BINDING",
                "$.reporting.binding_sha256",
                "Reporting binding does not match the manifest.",
            )
        status = reporting.get("status")
        if not isinstance(status, str) or status not in ("pending", "completed"):
            add_issue(
                issues,
                "STATE_REPORTING_STATUS",
                "$.reporting.status",
                "reporting status must be pending or completed.",
            )
        if final and status != "completed":
            add_issue(
                issues,
                "STATE_REPORTING_PENDING",
                "$.reporting.status",
                "Complete reporting before finalization.",
            )
        references = reporting.get("loaded_references")
        if status == "completed":
            if references != list(REPORTING_REFERENCES):
                add_issue(
                    issues,
                    "STATE_REPORTING_REFERENCES",
                    "$.reporting.loaded_references",
                    "Reporting must load reporting-and-validation.md followed by "
                    "full-audit-data-contract.md.",
                )
            if not is_nonempty_string(reporting.get("checkpoint")):
                add_issue(
                    issues,
                    "STATE_REPORTING_CHECKPOINT",
                    "$.reporting.checkpoint",
                    "Completed reporting needs a compact checkpoint.",
                )

    closure = state.get("closure")
    if not isinstance(closure, dict):
        add_issue(issues, "CLOSURE_ROOT", "$.closure", "closure must be an object.")
        return issues
    check_exact_keys(closure, {"compile", "render", "edits"}, "$.closure", issues)
    edits = closure.get("edits")
    applied = edits.get("applied") if isinstance(edits, dict) else None
    action = manifest_action(manifest)
    expected_phase = (
        "audit"
        if action == "audit"
        else "post_edit"
        if action == "audit-and-revise" and applied is True
        else "baseline"
        if action == "audit-and-revise"
        else None
    )
    validate_stage(
        closure.get("compile"),
        "compile",
        audit_root,
        issues,
        final,
        expected_phase=expected_phase,
    )
    validate_stage(
        closure.get("render"),
        "render",
        audit_root,
        issues,
        final,
        expected_phase=expected_phase,
    )

    if not isinstance(edits, dict):
        add_issue(issues, "CLOSURE_EDITS", "$.closure.edits", "edits must be an object.")
        return issues
    check_exact_keys(
        edits,
        {
            "applied",
            "diff_status",
            "evidence",
            "artifact",
            "finding_dispositions",
        },
        "$.closure.edits",
        issues,
    )
    check_forbidden_dashes(edits.get("evidence"), "$.closure.edits.evidence", issues)
    diff_status = edits.get("diff_status")
    if applied is None or diff_status is None:
        if final:
            add_issue(
                issues,
                "CLOSURE_EDITS_PENDING",
                "$.closure.edits",
                "Resolve edit and diff status before finalization.",
            )
    elif not isinstance(applied, bool):
        add_issue(
            issues,
            "CLOSURE_EDITS_APPLIED",
            "$.closure.edits.applied",
            "applied must be true or false.",
        )
    if diff_status is not None and (
        not isinstance(diff_status, str)
        or diff_status not in ("changed", "clean", "not_applicable", "unavailable")
    ):
        add_issue(
            issues,
            "CLOSURE_DIFF_STATUS",
            "$.closure.edits.diff_status",
            "Invalid diff_status.",
        )
    if applied is True and diff_status != "changed":
        add_issue(
            issues,
            "CLOSURE_DIFF_INCONSISTENT",
            "$.closure.edits",
            "Applied edits require diff_status changed.",
        )
    if applied is False and diff_status == "changed":
        add_issue(
            issues,
            "CLOSURE_DIFF_INCONSISTENT",
            "$.closure.edits",
            "No edits were applied, so diff_status cannot be changed.",
        )
    if applied is not None and not is_nonempty_string(edits.get("evidence")):
        add_issue(
            issues,
            "CLOSURE_DIFF_EVIDENCE",
            "$.closure.edits.evidence",
            "Record a diff artifact or substantive reason.",
        )
    validate_bound_artifact(
        edits.get("artifact"),
        audit_root,
        "$.closure.edits.artifact",
        issues,
        applied is True,
    )
    disposition_value = edits.get("finding_dispositions")
    disposition_records = validate_disposition_records(
        disposition_value,
        action,
        final,
        issues,
    )
    has_applied_disposition = any(
        record.get("outcome") == "applied" for record in disposition_records
    )
    if has_applied_disposition and (
        applied is not True
        or diff_status != "changed"
        or not isinstance(edits.get("artifact"), dict)
    ):
        add_issue(
            issues,
            "CLOSURE_DISPOSITION_APPLIED_MISMATCH",
            "$.closure.edits",
            "Applied finding dispositions require applied edits, a changed diff, and a bound artifact.",
        )
    if (
        action == "audit-and-revise"
        and isinstance(disposition_value, list)
        and not has_applied_disposition
        and applied is not False
    ):
        add_issue(
            issues,
            "CLOSURE_DISPOSITION_NO_APPLIED_MISMATCH",
            "$.closure.edits",
            "When no finding outcome is applied, applied must be false.",
        )
    if applied is False and edits.get("artifact") is not None:
        add_issue(
            issues,
            "CLOSURE_EDIT_ARTIFACT_UNEXPECTED",
            "$.closure.edits.artifact",
            "No-edit closure must use a null diff artifact.",
        )
    if action == "audit":
        if applied is not False:
            add_issue(
                issues,
                "CLOSURE_AUDIT_ONLY_EDIT",
                "$.closure.edits.applied",
                "Audit-only scope cannot record applied manuscript edits.",
            )
        if diff_status != "not_applicable":
            add_issue(
                issues,
                "CLOSURE_AUDIT_ONLY_DIFF",
                "$.closure.edits.diff_status",
                "Audit-only scope must use diff_status not_applicable.",
            )
        if edits.get("artifact") is not None:
            add_issue(
                issues,
                "CLOSURE_AUDIT_ONLY_ARTIFACT",
                "$.closure.edits.artifact",
                "Audit-only scope must not bind an edit artifact.",
            )
    return issues


def question_is_self_contained(question: str) -> bool:
    if not question.endswith("?"):
        return False
    words = re.findall(r"[A-Za-z0-9_\\]+", question)
    if len(words) < 8:
        return False
    request_frame = re.compile(
        r"(?i)^\s*(?:can|could|would|will|should|may|might|must|do|does|did|"
        r"is|are|was|were)\s+(?:the\s+authors?\s+)?(?:please\s+)?"
        r"(?:clarify|confirm|resolve|check|verify|explain|state|show|justify|"
        r"specify|identify|describe|indicate|discuss|determine)\b"
    )
    explicit_antecedent = re.compile(
        r"(?i)\b(?:the|a|an|each|every|either|neither|both|all|some|any|"
        r"these|those)\s+(?!authors?\b)[A-Za-z0-9_\\-]+\b|"
        r"\b(?:theorem|lemma|proposition|corollary|equation|figure|table|"
        r"section|appendix|algorithm)\s+[A-Za-z0-9_.\\-]+\b"
    )
    for pronoun in re.finditer(r"(?i)\b(?:it|them)\b", question):
        prefix = request_frame.sub("", question[: pronoun.start()], count=1)
        if explicit_antecedent.search(prefix) is None:
            return False
    if re.search(
        r"(?i)\b(?:this|that|these|those)\s+"
        r"(?:is|are|was|were|should|would|could|can|will|may|might|must|"
        r"do|does|did|has|have|had|be|been|need|needs|require|requires|"
        r"mean|means|refer|refers|apply|applies|change|changes|affect|affects|"
        r"concern|concerns|represent|represents|denote|denotes|use|uses|"
        r"include|includes|exclude|excludes|remain|remains|hold|holds|"
        r"follow|follows|conflict|conflicts|differ|differs|fail|fails|"
        r"work|works|occur|occurs|happen|happens)\b",
        question,
    ):
        return False
    if re.search(
        r"(?i)\b(?:this|that|these|those)\b(?=\s*(?:[?.,;:]|"
        r"\b(?:in|under|over|for|with|without|from|to|before|after|during|"
        r"within|outside|now|here|there|instead|again|as)\b))",
        question,
    ):
        return False
    if re.search(
        r"(?i)\b(?:this|that|these|those)\s+"
        r"(?:issue|point|choice|matter|claim|statement|problem|question|case|thing)s?\b",
        question,
    ):
        return False
    ambiguous = re.fullmatch(
        r"(?i)(?:can|could|would|will|should|is|are|was|were|do|does|did)\s+"
        r"(?:the\s+authors?\s+)?(?:clarify|confirm|resolve|check|verify)?\s*"
        r"(?:this|that|it|these|those|them)"
        r"(?:\s+(?:issue|point|choice|matter|claim|statement))?\?",
        question.strip(),
    )
    return ambiguous is None


def source_record_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources = manifest.get("sources")
    if not isinstance(sources, list):
        return {}
    return {
        item["source_id"]: item
        for item in sources
        if isinstance(item, dict) and is_nonempty_string(item.get("source_id"))
    }


def validate_anchor(
    value: Any,
    manifest: dict[str, Any],
    location: str,
    issues: list[Issue],
) -> None:
    if not isinstance(value, dict):
        add_issue(issues, "ANCHOR_TYPE", location, "Anchor must be an object.")
        return
    check_exact_keys(
        value, {"source_id", "kind", "start", "end", "locator"}, location, issues
    )
    sources = source_record_map(manifest)
    source_id = value.get("source_id")
    source = sources.get(source_id) if isinstance(source_id, str) else None
    if source is None:
        add_issue(
            issues,
            "ANCHOR_SOURCE",
            f"{location}.source_id",
            "Anchor source_id is not in the manifest.",
        )
        return
    kind = value.get("kind")
    source_kind_value = source.get("kind")
    expected_kind = (
        {
            "text": "line",
            "pdf": "page",
            "image": "artifact",
            "artifact": "artifact",
        }.get(source_kind_value)
        if isinstance(source_kind_value, str)
        else None
    )
    if kind != expected_kind:
        add_issue(
            issues,
            "ANCHOR_KIND",
            f"{location}.kind",
            f"Source {source_id} requires a {expected_kind} anchor.",
        )
        return
    start = value.get("start")
    end = value.get("end")
    locator = value.get("locator")
    if kind in ("line", "page"):
        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
            or start < 1
            or end < start
        ):
            add_issue(
                issues,
                "ANCHOR_RANGE",
                location,
                "Line and page anchors require integers with 1 <= start <= end.",
            )
        if locator is not None:
            add_issue(
                issues,
                "ANCHOR_LOCATOR_UNEXPECTED",
                f"{location}.locator",
                "Line and page anchors must use null locator.",
            )
        if kind == "line" and isinstance(end, int):
            line_count = source.get("line_count")
            if isinstance(line_count, int) and end > line_count:
                add_issue(
                    issues,
                    "ANCHOR_LINE_RANGE",
                    f"{location}.end",
                    "Line anchor exceeds the source snapshot.",
                )
        if kind == "page" and isinstance(end, int):
            page_count = source.get("page_count")
            if isinstance(page_count, int) and end > page_count:
                add_issue(
                    issues,
                    "ANCHOR_PAGE_RANGE",
                    f"{location}.end",
                    "Page anchor exceeds the source snapshot.",
                )
    else:
        if start is not None or end is not None:
            add_issue(
                issues,
                "ANCHOR_RANGE_UNEXPECTED",
                location,
                "Artifact anchors must use null start and end.",
            )
        if not is_nonempty_string(locator):
            add_issue(
                issues,
                "ANCHOR_LOCATOR",
                f"{location}.locator",
                "Artifact anchors require a substantive locator.",
            )


def validate_findings(
    findings: Any,
    manifest: dict[str, Any],
    state: dict[str, Any],
    final: bool,
) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(findings, dict):
        add_issue(issues, "FINDINGS_ROOT", "$", "Findings must be a JSON object.")
        return issues
    check_report_controls(findings, issues)
    check_exact_keys(
        findings,
        {
            "schema_version",
            "semantic_binding_sha256",
            "assessment",
            "findings",
            "contribution_ledger",
        },
        "$",
        issues,
    )
    if findings.get("schema_version") != SCHEMA_VERSION:
        add_issue(issues, "FINDINGS_SCHEMA", "$.schema_version", "Findings schema is invalid.")
    binding = manifest.get("semantic_binding_sha256")
    if findings.get("semantic_binding_sha256") != binding:
        add_issue(
            issues,
            "FINDINGS_BINDING",
            "$.semantic_binding_sha256",
            "Findings binding does not match the manifest.",
        )

    assessment = findings.get("assessment")
    assessment_status = None
    if not isinstance(assessment, dict):
        add_issue(
            issues, "ASSESSMENT_TYPE", "$.assessment", "assessment must be an object."
        )
    else:
        check_exact_keys(assessment, {"status", "boundary"}, "$.assessment", issues)
        check_forbidden_dashes(
            assessment.get("boundary"), "$.assessment.boundary", issues
        )
        assessment_status = assessment.get("status")
        if assessment_status is None:
            if final:
                add_issue(
                    issues,
                    "ASSESSMENT_PENDING",
                    "$.assessment.status",
                    "Resolve the audit assessment.",
                )
        elif not isinstance(assessment_status, str) or assessment_status not in (
            "findings_recorded",
            "no_consequential_findings",
        ):
            add_issue(
                issues,
                "ASSESSMENT_STATUS",
                "$.assessment.status",
                "Invalid assessment status.",
            )
        if final and not is_nonempty_string(assessment.get("boundary")):
            add_issue(
                issues,
                "ASSESSMENT_BOUNDARY",
                "$.assessment.boundary",
                "Record the assessment boundary.",
            )

    records = findings.get("findings")
    if not isinstance(records, list):
        add_issue(issues, "FINDING_LIST", "$.findings", "findings must be a list.")
        records = []
    if assessment_status == "findings_recorded" and not records:
        add_issue(
            issues,
            "FINDING_REQUIRED",
            "$.findings",
            "findings_recorded requires at least one finding.",
        )
    if assessment_status == "no_consequential_findings" and records:
        add_issue(
            issues,
            "FINDING_UNEXPECTED",
            "$.findings",
            "no_consequential_findings requires an empty finding list.",
        )

    seen_ids: set[str] = set()
    finding_priorities: dict[str, Any] = {}
    for index, finding in enumerate(records):
        location = f"$.findings[{index}]"
        if not isinstance(finding, dict):
            add_issue(issues, "FINDING_TYPE", location, "Finding must be an object.")
            continue
        check_exact_keys(
            finding,
            {
                "id",
                "priority",
                "title",
                "anchors",
                "observed_evidence",
                "inferred_consequence",
                "unverified_dependency",
                "author_question",
                "revision_direction",
                "remedy_type",
                "safe_repair_available",
            },
            location,
            issues,
        )
        for field in (
            "title",
            "inferred_consequence",
            "unverified_dependency",
            "author_question",
            "revision_direction",
        ):
            check_forbidden_dashes(
                finding.get(field), f"{location}.{field}", issues
            )
        finding_id = finding.get("id")
        if not isinstance(finding_id, str) or FINDING_ID_RE.fullmatch(finding_id) is None:
            add_issue(
                issues,
                "FINDING_ID",
                f"{location}.id",
                "Finding ID must use 3 to 9 canonical digits after F-.",
            )
        elif finding_id in seen_ids:
            add_issue(
                issues,
                "FINDING_ID_DUPLICATE",
                f"{location}.id",
                "Finding IDs must be unique.",
            )
        else:
            seen_ids.add(finding_id)
            finding_priorities[finding_id] = finding.get("priority")
        for field in {"title", "observed_evidence", "revision_direction"}:
            if not is_nonempty_string(finding.get(field)):
                add_issue(
                    issues,
                    "FINDING_TEXT",
                    f"{location}.{field}",
                    "Field requires substantive text.",
                )
        priority = finding.get("priority")
        if not isinstance(priority, str) or priority not in ALLOWED_PRIORITIES:
            add_issue(
                issues,
                "FINDING_PRIORITY",
                f"{location}.priority",
                "Canonical JSON priority must be Blocking (displayed as Author input required), Material, or Local.",
            )
        anchors = finding.get("anchors")
        if not isinstance(anchors, list) or not anchors:
            add_issue(
                issues,
                "FINDING_ANCHORS",
                f"{location}.anchors",
                "Each finding needs at least one source anchor.",
            )
        else:
            for anchor_index, anchor in enumerate(anchors):
                validate_anchor(
                    anchor,
                    manifest,
                    f"{location}.anchors[{anchor_index}]",
                    issues,
                )
        consequence = finding.get("inferred_consequence")
        dependency = finding.get("unverified_dependency")
        question = finding.get("author_question")
        remedy = finding.get("remedy_type")
        safe = finding.get("safe_repair_available")
        if consequence is not None and not is_nonempty_string(consequence):
            add_issue(
                issues,
                "FINDING_CONSEQUENCE",
                f"{location}.inferred_consequence",
                "Use substantive text or null.",
            )
        if dependency is not None and not is_nonempty_string(dependency):
            add_issue(
                issues,
                "FINDING_DEPENDENCY",
                f"{location}.unverified_dependency",
                "Use substantive text or null.",
            )
        if question is not None and not is_nonempty_string(question):
            add_issue(
                issues,
                "FINDING_QUESTION",
                f"{location}.author_question",
                "Use a substantive question or null.",
            )
        if not isinstance(remedy, str) or remedy not in ALLOWED_REMEDIES:
            add_issue(
                issues,
                "FINDING_REMEDY",
                f"{location}.remedy_type",
                "Invalid remedy_type.",
            )
        if not isinstance(safe, bool):
            add_issue(
                issues,
                "FINDING_SAFE_REPAIR",
                f"{location}.safe_repair_available",
                "safe_repair_available must be true or false.",
            )
        if priority in ("Blocking", "Material") and not is_nonempty_string(consequence):
            add_issue(
                issues,
                "FINDING_CONSEQUENCE_REQUIRED",
                f"{location}.inferred_consequence",
                f"A finding marked {PRIORITY_DISPLAY_LABELS.get(priority, priority)} must state an inferred consequence.",
            )
        if priority == "Blocking":
            if not is_nonempty_string(dependency):
                add_issue(
                    issues,
                    "FINDING_DEPENDENCY_REQUIRED",
                    f"{location}.unverified_dependency",
                    "A finding requiring author input must state an unverified dependency.",
                )
            if not is_nonempty_string(question) or not question_is_self_contained(question):
                add_issue(
                    issues,
                    "FINDING_AUTHOR_QUESTION",
                    f"{location}.author_question",
                    "A finding requiring author input must include a self-contained question ending in ?.",
                )
            if safe is not False:
                add_issue(
                    issues,
                    "FINDING_BLOCKING_SAFE",
                    f"{location}.safe_repair_available",
                    "A finding requiring author input cannot have a safe repair now.",
                )
            if remedy not in ("author_decision", "additional_support"):
                add_issue(
                    issues,
                    "FINDING_BLOCKING_REMEDY",
                    f"{location}.remedy_type",
                    "A finding requiring author input must use author_decision or additional_support.",
                )
        elif priority in ("Material", "Local"):
            if dependency is not None or question is not None:
                add_issue(
                    issues,
                    "FINDING_NONBLOCKING_DEPENDENCY",
                    location,
                    "Material and Local findings cannot contain an unresolved dependency.",
                )
            if (
                safe is not True
                or not isinstance(remedy, str)
                or remedy not in SAFE_EDIT_REMEDIES
            ):
                add_issue(
                    issues,
                    "FINDING_NONBLOCKING_REPAIR",
                    location,
                    "Material and Local findings require a supported safe edit.",
                )
        if dependency is not None and priority != "Blocking":
            add_issue(
                issues,
                "FINDING_DEPENDENCY_PRIORITY",
                f"{location}.priority",
                "An unverified dependency requires Author input required priority.",
            )

    action = manifest_action(manifest)
    closure = state.get("closure")
    edits = closure.get("edits") if isinstance(closure, dict) else None
    dispositions = (
        edits.get("finding_dispositions") if isinstance(edits, dict) else None
    )
    if action == "audit-and-revise" and isinstance(dispositions, list):
        expected_ids = sorted(seen_ids, key=finding_id_sort_key)
        actual_ids = [
            record.get("finding_id")
            for record in dispositions
            if isinstance(record, dict)
            and isinstance(record.get("finding_id"), str)
            and FINDING_ID_RE.fullmatch(record["finding_id"]) is not None
        ]
        if actual_ids != expected_ids:
            add_issue(
                issues,
                "CLOSURE_DISPOSITION_COVERAGE",
                "$.closure.edits.finding_dispositions",
                "Dispositions must cover every finding exactly once in canonical finding-ID order.",
            )
        for index, disposition in enumerate(dispositions):
            if not isinstance(disposition, dict):
                continue
            finding_id = disposition.get("finding_id")
            outcome = disposition.get("outcome")
            priority = (
                finding_priorities.get(finding_id)
                if isinstance(finding_id, str)
                else None
            )
            if priority is None and isinstance(finding_id, str):
                add_issue(
                    issues,
                    "CLOSURE_DISPOSITION_UNKNOWN_FINDING",
                    f"$.closure.edits.finding_dispositions[{index}].finding_id",
                    f"Disposition does not identify a recorded finding: {finding_id}.",
                )
            elif priority in ("Material", "Local") and outcome not in (
                "applied",
                "unapplied",
            ):
                add_issue(
                    issues,
                    "CLOSURE_DISPOSITION_PRIORITY",
                    f"$.closure.edits.finding_dispositions[{index}].outcome",
                    "Material and Local findings must be applied or unapplied.",
                )
            elif priority == "Blocking" and outcome not in (
                "applied",
                "unapplied",
                "unresolved",
            ):
                add_issue(
                    issues,
                    "CLOSURE_DISPOSITION_PRIORITY",
                    f"$.closure.edits.finding_dispositions[{index}].outcome",
                    "Findings requiring author input must be applied, unapplied, or unresolved.",
                )

    ledger = findings.get("contribution_ledger")
    ledger_status = None
    if not isinstance(ledger, dict):
        add_issue(
            issues,
            "LEDGER_TYPE",
            "$.contribution_ledger",
            "contribution_ledger must be an object.",
        )
        ledger = {}
    else:
        check_exact_keys(
            ledger,
            {"status", "reason", "blocking_finding_ids", "rows"},
            "$.contribution_ledger",
            issues,
        )
        check_forbidden_dashes(
            ledger.get("reason"), "$.contribution_ledger.reason", issues
        )
    ledger_status = ledger.get("status")
    rows = ledger.get("rows")
    blocking_ids = ledger.get("blocking_finding_ids")
    if ledger_status is None:
        if final:
            add_issue(
                issues,
                "LEDGER_PENDING",
                "$.contribution_ledger.status",
                "Resolve contribution_ledger as included, not_needed, or unavailable.",
            )
    elif not isinstance(ledger_status, str) or ledger_status not in (
        "included",
        "not_needed",
        "unavailable",
    ):
        add_issue(
            issues,
            "LEDGER_STATUS",
            "$.contribution_ledger.status",
            "Ledger status must be included, not_needed, or unavailable.",
        )
    if not isinstance(blocking_ids, list) or any(
        not is_nonempty_string(item) for item in blocking_ids
    ):
        add_issue(
            issues,
            "LEDGER_BLOCKING_IDS",
            "$.contribution_ledger.blocking_finding_ids",
            "blocking_finding_ids must be a list of finding IDs.",
        )
        blocking_ids = []
    if len(blocking_ids) != len(set(blocking_ids)):
        add_issue(
            issues,
            "LEDGER_BLOCKING_IDS_DUPLICATE",
            "$.contribution_ledger.blocking_finding_ids",
            "Ledger finding IDs requiring author input must be unique.",
        )
    if not isinstance(rows, list):
        add_issue(
            issues,
            "LEDGER_ROWS",
            "$.contribution_ledger.rows",
            "rows must be a list.",
        )
        rows = []
    if ledger_status == "included":
        if not rows:
            add_issue(
                issues,
                "LEDGER_ROW_REQUIRED",
                "$.contribution_ledger.rows",
                "An included ledger requires at least one row.",
            )
        if ledger.get("reason") is not None:
            add_issue(
                issues,
                "LEDGER_REASON_UNEXPECTED",
                "$.contribution_ledger.reason",
                "An included ledger must use null reason.",
            )
        if blocking_ids:
            add_issue(
                issues,
                "LEDGER_BLOCKING_IDS_UNEXPECTED",
                "$.contribution_ledger.blocking_finding_ids",
                "An included ledger must not cite findings requiring author input.",
            )
    if ledger_status in ("not_needed", "unavailable"):
        if not is_nonempty_string(ledger.get("reason")):
            add_issue(
                issues,
                "LEDGER_REASON",
                "$.contribution_ledger.reason",
                "A nonincluded ledger needs a substantive reason.",
            )
        if rows:
            add_issue(
                issues,
                "LEDGER_ROWS_UNEXPECTED",
                "$.contribution_ledger.rows",
                "A nonincluded ledger must have no rows.",
            )
    if ledger_status == "not_needed" and blocking_ids:
        add_issue(
            issues,
            "LEDGER_BLOCKING_IDS_UNEXPECTED",
            "$.contribution_ledger.blocking_finding_ids",
            "A not_needed ledger must not cite findings requiring author input.",
        )
    if ledger_status == "unavailable":
        if not blocking_ids:
            add_issue(
                issues,
                "LEDGER_BLOCKING_IDS_REQUIRED",
                "$.contribution_ledger.blocking_finding_ids",
                "An unavailable ledger must cite a finding requiring author input.",
            )
        for finding_id in blocking_ids:
            if finding_priorities.get(finding_id) != "Blocking":
                add_issue(
                    issues,
                    "LEDGER_BLOCKING_ID_INVALID",
                    "$.contribution_ledger.blocking_finding_ids",
                    f"Ledger dependency must cite a finding requiring author input: {finding_id}.",
                )
    for index, row in enumerate(rows):
        location = f"$.contribution_ledger.rows[{index}]"
        if not isinstance(row, dict):
            add_issue(issues, "LEDGER_ROW_TYPE", location, "Ledger row must be an object.")
            continue
        check_exact_keys(row, {"identity_anchors", "cells"}, location, issues)
        anchors = row.get("identity_anchors")
        if not isinstance(anchors, list) or not anchors:
            add_issue(
                issues,
                "LEDGER_IDENTITY_ANCHOR",
                f"{location}.identity_anchors",
                "Every contribution row needs a supplied identity anchor.",
            )
        else:
            for anchor_index, anchor in enumerate(anchors):
                validate_anchor(
                    anchor,
                    manifest,
                    f"{location}.identity_anchors[{anchor_index}]",
                    issues,
                )
        cells = row.get("cells")
        if not isinstance(cells, dict):
            add_issue(issues, "LEDGER_CELLS", f"{location}.cells", "cells must be an object.")
        else:
            check_exact_keys(cells, set(EXPECTED_LEDGER_HEADERS), f"{location}.cells", issues)
            for header in EXPECTED_LEDGER_HEADERS:
                if not is_nonempty_string(cells.get(header)):
                    add_issue(
                        issues,
                        "LEDGER_CELL",
                        f"{location}.cells.{header}",
                        "Every displayed ledger cell requires substantive text.",
                    )
            rank = cells.get("Rank")
            if is_nonempty_string(rank) and not (
                rank in ALLOWED_LEDGER_RANKS or re.fullmatch(r"[1-9][0-9]*", rank)
            ):
                add_issue(
                    issues,
                    "LEDGER_RANK",
                    f"{location}.cells.Rank",
                    "Rank must be a positive integer, Co-primary, or Unclear.",
                )

    state_passes = state.get("passes")
    if not isinstance(state_passes, list):
        state_passes = []
    contribution_pass = next(
        (
            item
            for item in state_passes
            if isinstance(item, dict) and item.get("tag") == "CONTRIBUTION_LEDGER"
        ),
        None,
    )
    if contribution_pass is None:
        if ledger_status != "not_needed":
            add_issue(
                issues,
                "LEDGER_PASS_MISSING",
                "$.contribution_ledger.status",
                "An unselected contribution pass requires a not_needed ledger.",
            )
    elif contribution_pass.get("status") == "completed" and ledger_status not in (
        "included",
        "not_needed",
        "unavailable",
    ):
        add_issue(
            issues,
            "LEDGER_PASS_MISMATCH",
            "$.contribution_ledger.status",
            "A completed contribution pass requires a resolved ledger outcome.",
        )
    elif contribution_pass.get("status") == "not_required" and ledger_status != "not_needed":
        add_issue(
            issues,
            "LEDGER_PASS_MISMATCH",
            "$.contribution_ledger.status",
            "A skipped contribution pass requires a not_needed ledger.",
        )
    return issues


def manifest_action(manifest: dict[str, Any]) -> str | None:
    scope = manifest.get("scope")
    return scope.get("action") if isinstance(scope, dict) else None


def diagnostic_state_projection(state: dict[str, Any]) -> dict[str, Any]:
    passes = state.get("passes")
    if not isinstance(passes, list):
        passes = []
    return {
        "semantic_binding_sha256": state.get("semantic_binding_sha256"),
        "passes": [
            record
            for record in passes
            if isinstance(record, dict) and record.get("tag") != "REVISION_CLOSURE"
        ],
        "reporting": state.get("reporting"),
    }


def diagnosis_freeze_record(
    audit_root: Path,
    manifest: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    closure = state["closure"]
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "semantic_binding_sha256": manifest["semantic_binding_sha256"],
        "manifest_sha256": sha256_file(audit_root / MANIFEST_NAME),
        "findings_sha256": sha256_file(audit_root / FINDINGS_NAME),
        "diagnostic_state_sha256": sha256_bytes(
            canonical_json_bytes(diagnostic_state_projection(state))
        ),
        "baseline": {
            "compile": closure["compile"],
            "render": closure["render"],
        },
    }


def revision_progress_started(state: dict[str, Any]) -> bool:
    passes = state.get("passes")
    if isinstance(passes, list):
        for record in passes:
            if isinstance(record, dict) and record.get("tag") == "REVISION_CLOSURE":
                if record.get("status") != "pending":
                    return True
    closure = state.get("closure")
    if not isinstance(closure, dict):
        return False
    edits = closure.get("edits")
    if not isinstance(edits, dict):
        return False
    return any(edits.get(key) is not None for key in edits)


def validate_diagnosis_ready(
    audit_root: Path,
    manifest: dict[str, Any],
    state: dict[str, Any],
    findings: dict[str, Any],
) -> list[Issue]:
    issues: list[Issue] = []
    if manifest_action(manifest) != "audit-and-revise":
        add_issue(
            issues,
            "FREEZE_ACTION",
            "$.scope.action",
            "Diagnosis freeze is only for audit-and-revise.",
        )
        return issues
    passes = state.get("passes")
    if not isinstance(passes, list):
        passes = []
    for index, record in enumerate(passes):
        if not isinstance(record, dict):
            continue
        location = f"$.passes[{index}].status"
        if record.get("tag") == "REVISION_CLOSURE":
            if record.get("status") != "pending":
                add_issue(
                    issues,
                    "FREEZE_REVISION_STARTED",
                    location,
                    "Freeze diagnosis before completing revision closure.",
                )
        elif record.get("status") == "pending":
            add_issue(
                issues,
                "FREEZE_DIAGNOSTIC_PENDING",
                location,
                "Resolve every diagnostic pass before freezing findings.",
            )
    reporting = state.get("reporting")
    if not isinstance(reporting, dict) or reporting.get("status") != "completed":
        add_issue(
            issues,
            "FREEZE_REPORTING_PENDING",
            "$.reporting.status",
            "Complete structured reporting before freezing findings.",
        )
    issues.extend(validate_findings(findings, manifest, state, final=True))
    closure = state.get("closure")
    if isinstance(closure, dict):
        validate_stage(
            closure.get("compile"),
            "compile",
            audit_root,
            issues,
            True,
            expected_phase="baseline",
        )
        validate_stage(
            closure.get("render"),
            "render",
            audit_root,
            issues,
            True,
            expected_phase="baseline",
        )
        edits = closure.get("edits")
        if not isinstance(edits, dict) or any(
            edits.get(key) is not None
            for key in {
                "applied",
                "diff_status",
                "evidence",
                "artifact",
                "finding_dispositions",
            }
        ):
            add_issue(
                issues,
                "FREEZE_EDITS_STARTED",
                "$.closure.edits",
                "Freeze diagnosis before recording any manuscript edit or diff.",
            )
    if (audit_root / REPORT_NAME).exists() or (audit_root / FINALIZATION_NAME).exists():
        add_issue(
            issues,
            "FREEZE_AFTER_PUBLICATION",
            str(audit_root),
            "Diagnosis cannot be frozen after publication artifacts exist.",
        )
    return sorted_issues(issues)


def validate_diagnosis_freeze(
    receipt: Any,
    audit_root: Path,
    manifest: dict[str, Any],
    state: dict[str, Any],
) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(receipt, dict):
        add_issue(issues, "FREEZE_ROOT", "$", "Diagnosis freeze must be an object.")
        return issues
    check_report_controls(receipt, issues)
    check_exact_keys(
        receipt,
        {
            "schema_version",
            "contract_version",
            "semantic_binding_sha256",
            "manifest_sha256",
            "findings_sha256",
            "diagnostic_state_sha256",
            "baseline",
        },
        "$",
        issues,
    )
    expected = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "semantic_binding_sha256": manifest.get("semantic_binding_sha256"),
        "manifest_sha256": sha256_file(audit_root / MANIFEST_NAME),
        "findings_sha256": sha256_file(audit_root / FINDINGS_NAME),
        "diagnostic_state_sha256": sha256_bytes(
            canonical_json_bytes(diagnostic_state_projection(state))
        ),
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            add_issue(
                issues,
                "FREEZE_MISMATCH",
                f"$.{key}",
                "Diagnosis freeze does not match the current pre-edit record.",
            )
    baseline = receipt.get("baseline")
    if not isinstance(baseline, dict):
        add_issue(issues, "FREEZE_BASELINE", "$.baseline", "baseline must be an object.")
    else:
        check_exact_keys(baseline, {"compile", "render"}, "$.baseline", issues)
        validate_stage(
            baseline.get("compile"),
            "compile",
            audit_root,
            issues,
            True,
            "$.baseline",
            expected_phase="baseline",
        )
        validate_stage(
            baseline.get("render"),
            "render",
            audit_root,
            issues,
            True,
            "$.baseline",
            expected_phase="baseline",
        )
        closure = state.get("closure")
        edits = closure.get("edits") if isinstance(closure, dict) else None
        if isinstance(closure, dict) and (
            not isinstance(edits, dict) or edits.get("applied") is not True
        ):
            for stage in ("compile", "render"):
                if closure.get(stage) != baseline.get(stage):
                    add_issue(
                        issues,
                        "FREEZE_BASELINE_DRIFT",
                        f"$.closure.{stage}",
                        "Unedited closure evidence must match the frozen baseline.",
                    )
    return sorted_issues(issues)


def diagnosis_freeze_status(
    audit_root: Path,
    manifest: dict[str, Any],
    state: dict[str, Any],
    require: bool,
) -> tuple[bool, list[Issue]]:
    issues: list[Issue] = []
    path = audit_root / DIAGNOSIS_FREEZE_NAME
    action = manifest_action(manifest)
    if action == "audit":
        if path.exists():
            add_issue(
                issues,
                "FREEZE_UNEXPECTED",
                str(path),
                "Audit-only scope must not contain a diagnosis freeze.",
            )
        return False, issues
    if action != "audit-and-revise":
        return False, issues
    if not path.exists():
        if require or revision_progress_started(state):
            add_issue(
                issues,
                "FREEZE_REQUIRED",
                str(path),
                "Freeze diagnosis before revision closure or manuscript edits.",
            )
        return False, issues
    receipt = read_json(path, issues, "FREEZE")
    if receipt is not None:
        issues.extend(validate_diagnosis_freeze(receipt, audit_root, manifest, state))
    return not issues, sorted_issues(issues)


def freeze_audit(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    audit_root = args.audit_root.resolve()
    manifest, state, findings, issues = load_workspace(audit_root, final=False)
    if not issues:
        issues.extend(validate_diagnosis_ready(audit_root, manifest, state, findings))
    method: str | None = None
    receipt_bytes: bytes | None = None
    if not issues:
        try:
            receipt_bytes = canonical_json_bytes(
                diagnosis_freeze_record(audit_root, manifest, state)
            )
            method = write_exclusive(audit_root / DIAGNOSIS_FREEZE_NAME, receipt_bytes)
        except AuditError as exc:
            add_issue(issues, "FREEZE_CONFLICT", str(audit_root), str(exc))
    issues = sorted_issues(issues)
    result = {
        "valid": not issues,
        "frozen": not issues,
        "method": method,
        "semantic_binding_sha256": manifest.get("semantic_binding_sha256"),
        "diagnosis_freeze_sha256": sha256_bytes(receipt_bytes)
        if receipt_bytes is not None
        else None,
        "errors": [asdict(issue) for issue in issues],
    }
    return result, 0 if not issues else 1


def anchor_text(anchor: dict[str, Any]) -> str:
    source_id = anchor["source_id"]
    if anchor["kind"] == "line":
        label = "line" if anchor["start"] == anchor["end"] else "lines"
        span = (
            str(anchor["start"])
            if anchor["start"] == anchor["end"]
            else f"{anchor['start']}-{anchor['end']}"
        )
        return f"{source_id} {label} {span}"
    if anchor["kind"] == "page":
        label = "page" if anchor["start"] == anchor["end"] else "pages"
        span = (
            str(anchor["start"])
            if anchor["start"] == anchor["end"]
            else f"{anchor['start']}-{anchor['end']}"
        )
        return f"{source_id} {label} {span}"
    return f"{source_id} artifact {display_text(anchor['locator'])}"


def escape_table_cell(value: str) -> str:
    return display_text(value).replace("|", "\\|")


def render_report(
    manifest: dict[str, Any],
    state: dict[str, Any],
    findings: dict[str, Any],
) -> bytes:
    scope = manifest["scope"]
    selected_passes = scope["focused_passes"] or [
        item["tag"]
        for item in manifest["pass_plan"]
        if item["tag"] not in {"ORIENTATION", "REVISION_CLOSURE"}
    ]
    lines: list[str] = [
        "# Full writing and presentation audit",
        "",
        "## Audit scope",
        "",
        f"- Action: {scope['action']}",
        f"- Plan: {scope['plan_kind']}",
        f"- Focus: {display_text(scope['focus'])}",
        "- Selected evaluative passes: " + ", ".join(selected_passes),
        "",
        "## Assessment boundary",
        "",
        AUDIT_BOUNDARY,
        "",
        display_text(findings["assessment"]["boundary"]),
        "",
        "## Audit result",
        "",
    ]
    priority_order = {"Blocking": 0, "Material": 1, "Local": 2}
    records = sorted(
        findings["findings"],
        key=lambda item: (
            priority_order[item["priority"]],
            finding_id_sort_key(item["id"]),
        ),
    )
    disposition_map: dict[str, dict[str, Any]] = {}
    if manifest_action(manifest) == "audit-and-revise":
        dispositions = state["closure"]["edits"]["finding_dispositions"]
        disposition_map = {
            record["finding_id"]: record
            for record in dispositions
            if isinstance(record, dict)
        }
    if findings["assessment"]["status"] == "no_consequential_findings":
        lines.extend(
            [
                "No consequential writing or presentation findings were recorded "
                "within the stated assessment boundary.",
                "",
            ]
        )
    else:
        lines.extend([f"{len(records)} consequential finding(s) were recorded.", ""])

    if records:
        lines.extend(["## Findings", ""])
        for finding in records:
            lines.extend(
                [
                    f"### {finding['id']}: {display_text(finding['title'])}",
                    "",
                    f"Priority: {PRIORITY_DISPLAY_LABELS[finding['priority']]}",
                    "",
                    "Location: "
                    + "; ".join(anchor_text(anchor) for anchor in finding["anchors"]),
                    "",
                    f"Observed evidence: {display_text(finding['observed_evidence'])}",
                    "",
                ]
            )
            disposition = disposition_map.get(finding["id"])
            if disposition is not None:
                lines.extend(
                    [
                        f"Revision outcome: {disposition['outcome']}",
                        "",
                        f"Disposition reason: {display_text(disposition['reason'])}",
                        "",
                    ]
                )
            if finding["inferred_consequence"] is not None:
                lines.extend(
                    [
                        "Inferred consequence: "
                        + display_text(finding["inferred_consequence"]),
                        "",
                    ]
                )
            if finding["unverified_dependency"] is not None:
                lines.extend(
                    [
                        "Unverified dependency: "
                        + display_text(finding["unverified_dependency"]),
                        "",
                        f"Author question: {display_text(finding['author_question'])}",
                        "",
                    ]
                )
            lines.extend(
                [
                    f"Revision direction: {display_text(finding['revision_direction'])}",
                    "",
                    f"Remedy type: {finding['remedy_type']}",
                    "",
                    "Safe repair available now: "
                    + ("yes" if finding["safe_repair_available"] else "no"),
                    "",
                ]
            )

    ledger = findings["contribution_ledger"]
    if ledger["status"] == "included":
        lines.extend(
            [
                "## Contribution ledger",
                "",
                "| " + " | ".join(EXPECTED_LEDGER_HEADERS) + " |",
                "| " + " | ".join(["---"] * len(EXPECTED_LEDGER_HEADERS)) + " |",
            ]
        )
        for row in ledger["rows"]:
            lines.append(
                "| "
                + " | ".join(
                    escape_table_cell(row["cells"][header])
                    for header in EXPECTED_LEDGER_HEADERS
                )
                + " |"
            )
        lines.extend(["", "Identity anchors:", ""])
        for row in ledger["rows"]:
            contribution = display_text(row["cells"]["Contribution"])
            anchors = "; ".join(
                anchor_text(anchor) for anchor in row["identity_anchors"]
            )
            lines.append(f"- {contribution}: {anchors}")
        lines.append("")
    else:
        lines.extend(
            [
                "## Contribution ledger",
                "",
                f"Status: {ledger['status']}",
                "",
                f"Reason: {display_text(ledger['reason'])}",
                "",
            ]
        )
        if ledger["blocking_finding_ids"]:
            lines.extend(
                [
                    "Findings requiring author input: "
                    + ", ".join(ledger["blocking_finding_ids"]),
                    "",
                ]
            )

    lines.extend(["## Pass coverage", ""])
    for record in state["passes"]:
        if record["status"] == "completed":
            detail = record["checkpoint"]
        elif record["status"] == "not_required":
            detail = f"not required: {record['reason']}"
        else:
            detail = record["status"]
        lines.append(
            f"- {record['tag']}: {record['kind']}: {display_text(detail)}"
        )
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- Compile [{state['closure']['compile']['phase']}]: "
            f"{state['closure']['compile']['status']}: "
            f"{display_text(state['closure']['compile']['evidence'])}",
            f"- Render [{state['closure']['render']['phase']}]: "
            f"{state['closure']['render']['status']}: "
            f"{display_text(state['closure']['render']['evidence'])}",
            f"- Edits and diff: {state['closure']['edits']['diff_status']}: "
            f"{display_text(state['closure']['edits']['evidence'])}",
            "",
            "## Provenance",
            "",
            f"- Semantic binding: {manifest['semantic_binding_sha256']}",
        ]
    )
    for source in manifest["sources"]:
        lines.append(
            f"- {source['source_id']}: {display_text(source['name'])}: "
            f"{source['sha256']}"
        )
    lines.append("")
    return ("\n".join(lines)).encode("utf-8")


def finalization_record(
    audit_root: Path,
    manifest: dict[str, Any],
    report_bytes: bytes,
) -> dict[str, Any]:
    freeze_hash = (
        sha256_file(audit_root / DIAGNOSIS_FREEZE_NAME)
        if manifest_action(manifest) == "audit-and-revise"
        else None
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "semantic_binding_sha256": manifest["semantic_binding_sha256"],
        "manifest_sha256": sha256_file(audit_root / MANIFEST_NAME),
        "state_sha256": sha256_file(audit_root / STATE_NAME),
        "findings_sha256": sha256_file(audit_root / FINDINGS_NAME),
        "diagnosis_freeze_sha256": freeze_hash,
        "report_path": REPORT_NAME,
        "report_sha256": sha256_bytes(report_bytes),
    }


def validate_finalization(
    receipt: Any,
    audit_root: Path,
    manifest: dict[str, Any],
    report_bytes: bytes,
) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(receipt, dict):
        add_issue(issues, "FINALIZATION_ROOT", "$", "Finalization must be an object.")
        return issues
    check_exact_keys(
        receipt,
        {
            "schema_version",
            "contract_version",
            "semantic_binding_sha256",
            "manifest_sha256",
            "state_sha256",
            "findings_sha256",
            "diagnosis_freeze_sha256",
            "report_path",
            "report_sha256",
        },
        "$",
        issues,
    )
    expected = finalization_record(audit_root, manifest, report_bytes)
    for key, value in expected.items():
        if receipt.get(key) != value:
            add_issue(
                issues,
                "FINALIZATION_MISMATCH",
                f"$.{key}",
                "Finalization receipt does not match current canonical state.",
            )
    report_path = safe_relative_path(
        audit_root, receipt.get("report_path"), "$.report_path", issues
    )
    if report_path is not None:
        if not report_path.is_file():
            add_issue(
                issues,
                "FINAL_REPORT_MISSING",
                str(report_path),
                "Final report recorded by the receipt is missing.",
            )
        elif report_path.read_bytes() != report_bytes:
            add_issue(
                issues,
                "FINAL_REPORT_DRIFT",
                str(report_path),
                "Final report bytes do not match canonical findings.",
            )
    return issues


def load_workspace(
    audit_root: Path,
    final: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[Issue]]:
    issues: list[Issue] = []
    manifest_raw = read_json(audit_root / MANIFEST_NAME, issues, "MANIFEST")
    state_raw = read_json(audit_root / STATE_NAME, issues, "STATE")
    findings_raw = read_json(audit_root / FINDINGS_NAME, issues, "FINDINGS")
    manifest = manifest_raw if isinstance(manifest_raw, dict) else {}
    state = state_raw if isinstance(state_raw, dict) else {}
    findings = findings_raw if isinstance(findings_raw, dict) else {}
    if manifest_raw is not None:
        issues.extend(validate_manifest(manifest_raw, audit_root))
    if state_raw is not None:
        issues.extend(validate_state(state_raw, manifest, audit_root, final))
    if findings_raw is not None:
        issues.extend(validate_findings(findings_raw, manifest, state, final))
    return manifest, state, findings, sorted_issues(issues)


def pending_passes(state: dict[str, Any]) -> list[str]:
    passes = state.get("passes")
    if not isinstance(passes, list):
        return []
    return [
        item.get("tag", "UNKNOWN")
        for item in passes
        if isinstance(item, dict) and item.get("status") == "pending"
    ]


def current_final_status(
    audit_root: Path,
    manifest: dict[str, Any],
    state: dict[str, Any],
    findings: dict[str, Any],
    core_issues: Sequence[Issue],
) -> tuple[bool, list[Issue]]:
    receipt_path = audit_root / FINALIZATION_NAME
    report_path = audit_root / REPORT_NAME
    if not receipt_path.exists():
        if not report_path.exists():
            return False, []
        issues: list[Issue] = []
        if core_issues:
            add_issue(
                issues,
                "FINAL_REPORT_ORPHAN",
                str(report_path),
                "A report exists without a receipt and canonical state is incomplete.",
            )
            return False, issues
        try:
            report_bytes = render_report(manifest, state, findings)
        except (KeyError, TypeError, ValueError, UnicodeError) as exc:
            add_issue(
                issues,
                "FINALIZATION_RENDER",
                str(report_path),
                f"Cannot render canonical report: {exc}.",
            )
            return False, issues
        if not report_path.is_file() or report_path.read_bytes() != report_bytes:
            add_issue(
                issues,
                "FINAL_REPORT_CONFLICT",
                str(report_path),
                "Report bytes conflict with canonical state and no receipt exists.",
            )
        return False, sorted_issues(issues)
    issues: list[Issue] = []
    if core_issues:
        add_issue(
            issues,
            "FINALIZATION_CORE_INVALID",
            str(receipt_path),
            "Finalization exists but canonical state is invalid or incomplete.",
        )
        return False, issues
    try:
        report_bytes = render_report(manifest, state, findings)
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        add_issue(
            issues,
            "FINALIZATION_RENDER",
            str(report_path),
            f"Cannot render canonical report: {exc}.",
        )
        return False, issues
    receipt = read_json(receipt_path, issues, "FINALIZATION")
    if receipt is not None:
        issues.extend(validate_finalization(receipt, audit_root, manifest, report_bytes))
    return not issues, sorted_issues(issues)


def status_audit(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    audit_root = args.audit_root.resolve()
    require_final = (audit_root / FINALIZATION_NAME).exists()
    manifest, state, findings, issues = load_workspace(audit_root, final=require_final)
    frozen = False
    if not issues:
        frozen, freeze_issues = diagnosis_freeze_status(
            audit_root, manifest, state, require=require_final
        )
        issues.extend(freeze_issues)
    final_ready, final_issues = current_final_status(
        audit_root, manifest, state, findings, issues
    )
    all_issues = sorted_issues([*issues, *final_issues])
    result = {
        "workspace_valid": not all_issues,
        "final": final_ready,
        "semantic_binding_sha256": manifest.get("semantic_binding_sha256"),
        "pending_passes": pending_passes(state),
        "reporting_status": state.get("reporting", {}).get("status")
        if isinstance(state.get("reporting"), dict)
        else None,
        "assessment_status": findings.get("assessment", {}).get("status")
        if isinstance(findings.get("assessment"), dict)
        else None,
        "diagnosis_frozen": frozen,
        "errors": [asdict(issue) for issue in all_issues],
    }
    return result, 0 if not all_issues else 1


def check_audit(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    audit_root = args.audit_root.resolve()
    manifest, state, findings, issues = load_workspace(audit_root, final=True)
    frozen = False
    if not issues:
        frozen, freeze_issues = diagnosis_freeze_status(
            audit_root, manifest, state, require=True
        )
        issues.extend(freeze_issues)
    publication: dict[str, str] | None = None
    report_bytes: bytes | None = None
    if not issues:
        try:
            report_bytes = render_report(manifest, state, findings)
        except (KeyError, TypeError, ValueError, UnicodeError) as exc:
            add_issue(
                issues,
                "REPORT_RENDER",
                str(audit_root / REPORT_NAME),
                f"Cannot render canonical report: {exc}.",
            )
    if not issues and report_bytes is not None and args.publish:
        try:
            receipt = finalization_record(audit_root, manifest, report_bytes)
            receipt_bytes = canonical_json_bytes(receipt)
            preflight_exclusive(audit_root / REPORT_NAME, report_bytes)
            preflight_exclusive(audit_root / FINALIZATION_NAME, receipt_bytes)
            report_method = write_exclusive(audit_root / REPORT_NAME, report_bytes)
            receipt_method = write_exclusive(
                audit_root / FINALIZATION_NAME, receipt_bytes
            )
            publication = {
                "report": report_method,
                "finalization": receipt_method,
            }
        except AuditError as exc:
            add_issue(issues, "PUBLICATION_CONFLICT", str(audit_root), str(exc))

    final_ready = False
    if not issues:
        final_ready, final_issues = current_final_status(
            audit_root, manifest, state, findings, []
        )
        issues.extend(final_issues)
    issues = sorted_issues(issues)
    result = {
        "valid": not issues,
        "final": final_ready,
        "published": publication,
        "semantic_binding_sha256": manifest.get("semantic_binding_sha256"),
        "report_sha256": sha256_bytes(report_bytes) if report_bytes is not None else None,
        "diagnosis_frozen": frozen,
        "errors": [asdict(issue) for issue in issues],
    }
    return result, 0 if not issues else 1


def emit_result(result: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
        return
    if result.get("initialized"):
        print(f"INITIALIZED: {result['audit_root']}")
        print(f"BINDING: {result['semantic_binding_sha256']}")
        return
    if result.get("frozen") and not result.get("errors"):
        print("FROZEN: pre-edit diagnosis is bound")
        print(f"BINDING: {result['semantic_binding_sha256']}")
        return
    errors = result.get("errors", [])
    if errors:
        print(f"INVALID: {len(errors)} issue(s)")
        for issue in errors:
            print(f"{issue['code']} {issue['location']}: {issue['message']}")
        return
    if result.get("final"):
        print("FINAL: audit is valid and finalized")
    elif result.get("valid") is True:
        print("VALID: audit is ready for publication")
    else:
        print("RESUMABLE: audit workspace is valid but incomplete")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create and validate self-contained full stat-paper-writing audits. "
            "This harness does not validate mathematics or science."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a new no-overwrite audit workspace.")
    init.add_argument("--audit-root", type=Path, required=True)
    init.add_argument(
        "--skill-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    init.add_argument("--source", type=Path, action="append", required=True)
    init.add_argument(
        "--source-kind",
        action="append",
        default=[],
        metavar="SOURCE=KIND",
        help="Override one source as text, pdf, image, or artifact.",
    )
    init.add_argument(
        "--pdf-page-count",
        action="append",
        default=[],
        metavar="SOURCE=N",
        help="Verified PDF page count when automatic inspection is unavailable.",
    )
    init.add_argument(
        "--action",
        choices=["audit", "audit-and-revise"],
        default="audit",
    )
    init.add_argument("--focus")
    init.add_argument(
        "--focused-pass",
        action="append",
        default=[],
        choices=DIAGNOSTIC_PASSES,
        help="Select an explicit evaluative pass after neutral orientation.",
    )
    init.add_argument("--json", action="store_true", dest="json_output")

    freeze = subparsers.add_parser(
        "freeze", help="Bind completed diagnosis before audit-and-revise edits."
    )
    freeze.add_argument("--audit-root", type=Path, required=True)
    freeze.add_argument("--json", action="store_true", dest="json_output")

    status = subparsers.add_parser("status", help="Inspect resumability and final status.")
    status.add_argument("--audit-root", type=Path, required=True)
    status.add_argument("--json", action="store_true", dest="json_output")

    check = subparsers.add_parser(
        "check", help="Validate a complete audit and optionally publish it."
    )
    check.add_argument("--audit-root", type=Path, required=True)
    check.add_argument("--publish", action="store_true")
    check.add_argument("--json", action="store_true", dest="json_output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = initialize_audit(args)
            code = 0
        elif args.command == "freeze":
            result, code = freeze_audit(args)
        elif args.command == "status":
            result, code = status_audit(args)
        else:
            result, code = check_audit(args)
    except (
        AuditError,
        OSError,
        UnicodeError,
        TypeError,
        ValueError,
        AttributeError,
    ) as exc:
        result = {
            "valid": False,
            "final": False,
            "errors": [
                asdict(Issue(code="WORKFLOW_ERROR", location="$", message=str(exc)))
            ],
        }
        code = 1
    emit_result(result, args.json_output)
    return code


if __name__ == "__main__":
    sys.exit(main())
