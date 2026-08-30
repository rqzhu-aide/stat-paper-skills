"""Refresh the bundled reference audit after a validator change.

A validator edit changes the protocol identity, which is part of every
challenge packet's semantic binding, so the shipped audit's recorded
challenges (and the finalization) go stale by design. This helper performs
the mechanical part of the refresh on a COPY of the audit: revalidate the
protocol, rebind both challenges against freshly generated packets while
preserving the recorded verdicts and assessments verbatim, regenerate the
report's challenge rows, and re-run checkpoint plus finalize.

It never edits a mathematical judgment. Use it only for the bundled
reference audit (or a copy of it); a real audit whose validator changed must
have its affected judgments reconfirmed by a checker, not restamped.

Usage:
    python assets/reference-audit/refresh_reference_audit.py <audit-root-copy>
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "proofcheck.py"
_SPEC = importlib.util.spec_from_file_location("proofcheck_refresh", _SCRIPT)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot load {_SCRIPT}")
proofcheck = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(proofcheck)

UNITS = {
    "lem:growing-max": "lem-growing-max",
    "thm:main": "thm-main",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict, indent: int) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=indent) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _challenge_row(unit: str, check: dict) -> str:
    assessments = json.dumps(
        [
            {
                key: assessment[key]
                for key in (
                    "issue_id",
                    "target_contract_sha256",
                    "assessment",
                    "target_assessment",
                    "downstream_assessment",
                )
            }
            for assessment in check["issue_assessments"]
        ],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    disagreements = json.dumps(
        check["disagreements"], separators=(",", ":"), ensure_ascii=False
    )
    cells = [
        unit,
        check["status"],
        check["independence_level"],
        ", ".join(check["covered_issue_ids"]),
        assessments,
        check["challenger_verdict"],
        check["reconciled_verdict"],
        disagreements,
        check["artifact"],
        check["source_snapshot_sha256"],
        check["challenged_ledger_sha256"],
        check["challenge_context_sha256"],
        check["challenge_artifact_sha256"],
        check["generated_utc"],
        check["resolution"] or "none",
    ]
    return "| " + " | ".join(str(cell).replace("|", "\\|") for cell in cells) + " |"


def refresh(root: Path, *, quiet: bool = True) -> None:
    root = root.resolve()
    manifest = _read_json(root / "AUDIT_MANIFEST.json")
    current_validator = proofcheck.protocol_identity()["validator_sha256"]
    if manifest["protocol"]["validator_sha256"] != current_validator:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            status = proofcheck.cmd_revalidate_protocol(
                argparse.Namespace(root=root)
            )
        if status != 0:
            raise RuntimeError(f"revalidate-protocol failed: {buffer.getvalue()}")

    report_path = root / "audit" / "06_reports" / "FINAL_REPORT.md"
    report = report_path.read_text(encoding="utf-8")
    for unit_id, stem in UNITS.items():
        ledger_path = root / "audit" / "04_local_checks" / f"{stem}.ledger.json"
        ledger = _read_json(ledger_path)
        primary_packet = proofcheck.build_context_packet(
            root, unit_id, "primary"
        )
        ledger["work_context_sha256"] = primary_packet[
            "work_context_sha256"
        ]
        _write_json(ledger_path, ledger, indent=1)
        packet = proofcheck.build_context_packet(root, unit_id, "challenge")
        check = ledger["independent_check"]
        triggers = {
            row["id"]: row for row in packet.get("issue_triggers", [])
        }
        for assessment in check["issue_assessments"]:
            trigger = triggers.get(assessment["issue_id"])
            if trigger is None:
                raise RuntimeError(
                    f"{unit_id}: issue {assessment['issue_id']} is no longer a "
                    "challenge trigger; the refresh cannot proceed mechanically"
                )
            assessment["target_contract_sha256"] = trigger[
                "target_contract_sha256"
            ]
        check["challenge_context_sha256"] = packet["context_binding_sha256"]
        check["generated_utc"] = proofcheck.utc_now()
        check["challenge_artifact_sha256"] = "0" * 64
        check["challenged_ledger_sha256"] = (
            proofcheck.canonical_primary_ledger_sha256(ledger)
        )
        _write_json(ledger_path, ledger, indent=1)
        artifact_path = root / check["artifact"]
        artifact = artifact_path.read_text(encoding="utf-8")
        artifact = re.sub(
            r'"challenge_context_sha256": "[0-9a-f]{64}"',
            f'"challenge_context_sha256": "{packet["context_binding_sha256"]}"',
            artifact,
        )
        artifact_path.write_text(artifact, encoding="utf-8", newline="\n")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            proofcheck.cmd_bind_challenge(
                argparse.Namespace(root=root, unit_id=unit_id)
            )
        bound = _read_json(ledger_path)["independent_check"]
        report_lines = []
        for line in report.split("\n"):
            if line.startswith(f"| {unit_id} | agreed |"):
                report_lines.append(_challenge_row(unit_id, bound))
            else:
                report_lines.append(line)
        report = "\n".join(report_lines)
    report_path.write_text(report, encoding="utf-8", newline="\n")

    with contextlib.redirect_stdout(io.StringIO()):
        checkpoint_status = proofcheck.cmd_checkpoint(
            argparse.Namespace(
                root=root,
                active_unit=None,
                clear_active_unit=True,
                next_action="Run final issue reconciliation and finalization.",
            )
        )
    if checkpoint_status != 0:
        raise RuntimeError("checkpoint failed during reference-audit refresh")
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        finalize_status = proofcheck.cmd_finalize(argparse.Namespace(root=root))
    if finalize_status != 0:
        raise RuntimeError(
            "finalize failed during reference-audit refresh: "
            + buffer.getvalue()
        )
    if not quiet:
        print(f"reference audit refreshed and finalized at {root}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    refresh(args.root.resolve(), quiet=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
