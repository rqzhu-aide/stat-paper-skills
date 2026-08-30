from __future__ import annotations

import argparse
import io
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "writer_audit.py"
SPEC = importlib.util.spec_from_file_location("writer_audit_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
writer_audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = writer_audit
SPEC.loader.exec_module(writer_audit)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_bytes(writer_audit.canonical_json_bytes(value))


def issue_codes(result: dict) -> set[str]:
    return {item["code"] for item in result["errors"]}


class WriterAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.sources = self.base / "sources"
        self.sources.mkdir()
        self.source = self.sources / "paper.tex"
        self.source.write_text(
            "\\section{Method}\n"
            "We define $\\widehat\\theta_n$.\n"
            "The reported estimate is 1.25.\n",
            encoding="utf-8",
        )
        self.audit = self.base / "audit"
        self.initialize()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def initialize(
        self,
        audit_root: Path | None = None,
        sources: list[Path] | None = None,
        action: str = "audit",
        focused: list[str] | None = None,
        skill_root: Path = ROOT,
        source_kind: list[str] | None = None,
        pdf_page_count: list[str] | None = None,
        focus: str | None = "test audit scope",
    ) -> dict:
        audit_root = audit_root or self.audit
        args = argparse.Namespace(
            audit_root=audit_root,
            skill_root=skill_root,
            source=sources or [self.source],
            action=action,
            focus=focus,
            focused_pass=focused or [],
            source_kind=source_kind or [],
            pdf_page_count=pdf_page_count or [],
        )
        return writer_audit.initialize_audit(args)

    @staticmethod
    def anchor(
        source_id: str = "SRC-001",
        kind: str = "line",
        start: int | None = 2,
        end: int | None = 2,
        locator: str | None = None,
    ) -> dict:
        return {
            "source_id": source_id,
            "kind": kind,
            "start": start,
            "end": end,
            "locator": locator,
        }

    def finding(
        self,
        finding_id: str,
        priority: str,
        anchor: dict | None = None,
        remedy: str | None = None,
    ) -> dict:
        if priority == "Blocking":
            consequence = "Readers cannot identify the object used in the application."
            dependency = "The supplied artifacts conflict about the fitted estimator."
            question = (
                "Which named estimator did the authors use for the reported application?"
            )
            safe = False
            remedy = remedy or "author_decision"
        elif priority == "Material":
            consequence = "The current order obscures the paper-level interpretation."
            dependency = None
            question = None
            safe = True
            remedy = remedy or "safe_presentation_edit"
        else:
            consequence = None
            dependency = None
            question = None
            safe = True
            remedy = remedy or "safe_prose_edit"
        return {
            "id": finding_id,
            "priority": priority,
            "title": (
                "Presentation issue requiring clarification"
                if priority == "Blocking"
                else f"{priority} presentation issue"
            ),
            "anchors": [anchor or self.anchor()],
            "observed_evidence": "The supplied passage uses two different labels.",
            "inferred_consequence": consequence,
            "unverified_dependency": dependency,
            "author_question": question,
            "revision_direction": "Use the supported representation consistently.",
            "remedy_type": remedy,
            "safe_repair_available": safe,
        }

    @staticmethod
    def pass_reference(tag: str) -> str:
        return {
            "ORIENTATION": "references/revision-audit.md",
            "FORMAL_OBJECT_AND_CLAIM_CONTRACTS": (
                "references/support-and-author-decisions.md"
            ),
            "LOCAL_PRESENTATION": "references/polishing-protocol.md",
            "CONTRIBUTION_LEDGER": "references/argument-architecture.md",
            "WHOLE_PAPER_NARRATIVE": "references/argument-architecture.md",
            "REVISION_CLOSURE": "references/polishing-protocol.md",
        }.get(tag, "references/revision-audit.md")

    @classmethod
    def pass_references(cls, tag: str) -> list[str]:
        references = [cls.pass_reference(tag)]
        if tag in writer_audit.QUICK_SECTION_PASS_TAGS:
            references.append(writer_audit.QUICK_SECTION_REFERENCE)
        return references

    def complete_diagnosis(
        self,
        audit_root: Path | None = None,
        findings_records: list[dict] | None = None,
        contribution: str = "skip",
    ) -> None:
        audit_root = audit_root or self.audit
        state = read_json(audit_root / writer_audit.STATE_NAME)
        findings = read_json(audit_root / writer_audit.FINDINGS_NAME)
        manifest = read_json(audit_root / writer_audit.MANIFEST_NAME)
        closure_phase = (
            "audit"
            if manifest["scope"]["action"] == "audit"
            else "baseline"
        )
        records = findings_records or []
        for record in state["passes"]:
            tag = record["tag"]
            if tag == "REVISION_CLOSURE":
                continue
            if tag == "CONTRIBUTION_LEDGER" and contribution == "skip":
                if record["requirement"] == "conditional":
                    record.update(
                        status="not_required",
                        loaded_references=[],
                        checkpoint=None,
                        reason="The audit scope did not require a contribution ledger.",
                    )
                    continue
                contribution = "not_needed"
            record.update(
                status="completed",
                loaded_references=self.pass_references(tag),
                checkpoint=f"Completed {tag.lower()} against the bound sources.",
                reason=None,
            )
        state["reporting"].update(
            status="completed",
            loaded_references=list(writer_audit.REPORTING_REFERENCES),
            checkpoint="Structured findings and closure fields were resolved.",
        )
        state["closure"]["compile"] = {
            "phase": closure_phase,
            "status": "not_run",
            "evidence": "No LaTeX compiler was available in this test fixture.",
            "artifact": None,
        }
        state["closure"]["render"] = {
            "phase": closure_phase,
            "status": "not_run",
            "evidence": "No rendered output was required for this text fixture.",
            "artifact": None,
        }
        findings["assessment"] = {
            "status": "findings_recorded"
            if records
            else "no_consequential_findings",
            "boundary": "Author-side writing and presentation within supplied files.",
        }
        findings["findings"] = records
        ledger = findings["contribution_ledger"]
        ledger.update(reason=None, blocking_finding_ids=[], rows=[])
        if contribution == "included":
            ledger["status"] = "included"
            ledger["rows"] = [
                {
                    "identity_anchors": [self.anchor()],
                    "cells": {
                        "Rank": "1",
                        "Contribution": "A supplied estimator construction",
                        "Method object or construction": "The named estimator",
                        "Formal support": "Theorem 1 as attributed by the manuscript",
                        "Empirical support": "Simulation 1 as reported",
                        "Boundary": "Presentation assessment only",
                    },
                }
            ]
        elif contribution == "unavailable":
            ledger.update(
                status="unavailable",
                reason="Supplied contribution identities are insufficient.",
                blocking_finding_ids=[
                    item["id"] for item in records if item["priority"] == "Blocking"
                ],
            )
        else:
            ledger.update(
                status="not_needed",
                reason="A ledger would not clarify this audit scope.",
            )
        write_json(audit_root / writer_audit.STATE_NAME, state)
        write_json(audit_root / writer_audit.FINDINGS_NAME, findings)

    def finish_revision(self, audit_root: Path | None = None, applied: bool = False) -> None:
        audit_root = audit_root or self.audit
        state = read_json(audit_root / writer_audit.STATE_NAME)
        findings = read_json(audit_root / writer_audit.FINDINGS_NAME)
        revision = next(
            record for record in state["passes"] if record["tag"] == "REVISION_CLOSURE"
        )
        revision.update(
            status="completed",
            loaded_references=["references/polishing-protocol.md"],
            checkpoint="Affected contracts were rechecked after revision.",
            reason=None,
        )
        if applied:
            artifact = audit_root / "artifacts" / "revision.diff"
            artifact.parent.mkdir(exist_ok=True)
            artifact.write_text("supported revision\n", encoding="utf-8")
            binding = {
                "path": "artifacts/revision.diff",
                "sha256": writer_audit.sha256_file(artifact),
            }
            state["closure"]["edits"] = {
                "applied": True,
                "diff_status": "changed",
                "evidence": "The bound diff records the authorized revision.",
                "artifact": binding,
                "finding_dispositions": [
                    {
                        "finding_id": item["id"],
                        "outcome": "applied"
                        if item["priority"] in {"Material", "Local"}
                        else "unresolved",
                        "reason": "The authorized revision addressed this supported repair."
                        if item["priority"] in {"Material", "Local"}
                        else "The supplied revision did not resolve this author dependency.",
                    }
                    for item in sorted(
                        findings["findings"],
                        key=lambda value: writer_audit.finding_id_sort_key(value["id"]),
                    )
                ],
            }
            state["closure"]["compile"] = {
                "phase": "post_edit",
                "status": "not_run",
                "evidence": "The post-edit compiler was unavailable in this test fixture.",
                "artifact": None,
            }
            state["closure"]["render"] = {
                "phase": "post_edit",
                "status": "not_run",
                "evidence": "The post-edit rendering check was unavailable in this fixture.",
                "artifact": None,
            }
        else:
            state["closure"]["edits"] = {
                "applied": False,
                "diff_status": "clean",
                "evidence": "No supported manuscript edit was needed.",
                "artifact": None,
                "finding_dispositions": [
                    {
                        "finding_id": item["id"],
                        "outcome": "unresolved"
                        if item["priority"] == "Blocking"
                        else "unapplied",
                        "reason": "The author dependency remains unresolved."
                        if item["priority"] == "Blocking"
                        else "No edit was applied to this supported finding.",
                    }
                    for item in sorted(
                        findings["findings"],
                        key=lambda value: writer_audit.finding_id_sort_key(value["id"]),
                    )
                ],
            }
        write_json(audit_root / writer_audit.STATE_NAME, state)

    def check(self, audit_root: Path | None = None, publish: bool = False):
        return writer_audit.check_audit(
            argparse.Namespace(audit_root=audit_root or self.audit, publish=publish)
        )

    def status(self, audit_root: Path | None = None):
        return writer_audit.status_audit(
            argparse.Namespace(audit_root=audit_root or self.audit)
        )

    def freeze(self, audit_root: Path | None = None):
        return writer_audit.freeze_audit(
            argparse.Namespace(audit_root=audit_root or self.audit)
        )

    def test_initialization_is_self_contained_and_resumable(self) -> None:
        manifest = read_json(self.audit / writer_audit.MANIFEST_NAME)
        state = read_json(self.audit / writer_audit.STATE_NAME)
        self.assertEqual(manifest["schema_version"], "3.0")
        self.assertEqual(manifest["contract_version"], "writer-audit-2")
        self.assertEqual(manifest["scope"]["mode"], "Full")
        self.assertEqual(manifest["sources"][0]["snapshot_path"], "inputs/SRC-001.tex")
        self.assertEqual(
            (self.audit / "inputs" / "SRC-001.tex").read_bytes(),
            self.source.read_bytes(),
        )
        logical = {item["logical_path"] for item in manifest["protocol"]}
        snapshot_paths = [item["snapshot_path"] for item in manifest["protocol"]]
        self.assertIn("SKILL.md", logical)
        self.assertIn("scripts/writer_audit.py", logical)
        self.assertIn("references/argument-architecture.md", logical)
        self.assertIn("references/quick-section-audit.md", logical)
        self.assertIn("references/full-audit-data-contract.md", logical)
        self.assertEqual(
            snapshot_paths,
            [
                writer_audit.protocol_snapshot_path(item["logical_path"])
                for item in manifest["protocol"]
            ],
        )
        self.assertEqual(len(snapshot_paths), len(set(snapshot_paths)))
        self.assertTrue((self.audit / "artifacts").is_dir())
        self.assertEqual(list((self.audit / "artifacts").iterdir()), [])
        self.assertFalse((self.audit / writer_audit.REPORT_NAME).exists())
        self.assertFalse((self.audit / writer_audit.DIAGNOSIS_FREEZE_NAME).exists())
        self.assertEqual(state["closure"]["compile"]["phase"], "audit")
        self.assertEqual(state["closure"]["render"]["phase"], "audit")
        self.assertEqual(state["closure"]["edits"]["finding_dispositions"], [])
        result, code = self.status()
        self.assertEqual(code, 0)
        self.assertTrue(result["workspace_valid"])
        self.assertFalse(result["final"])

    def test_unicode_long_same_basename_and_common_text_suffixes(self) -> None:
        long_name = "paper_\u2013_" + "x" * 70 + ".Rmd"
        first_dir = self.base / "first space"
        second_dir = self.base / "second space"
        first_dir.mkdir()
        second_dir.mkdir()
        first = first_dir / long_name
        second = second_dir / long_name
        first.write_text("line one\nline two\n", encoding="utf-8")
        second.write_text("different\n", encoding="utf-8")
        audit = self.base / "unicode audit"
        self.initialize(audit, [first, second])
        manifest = read_json(audit / writer_audit.MANIFEST_NAME)
        self.assertEqual(
            [item["snapshot_path"] for item in manifest["sources"]],
            ["inputs/SRC-001.rmd", "inputs/SRC-002.rmd"],
        )
        self.assertEqual([item["kind"] for item in manifest["sources"]], ["text", "text"])
        self.assertIn("\u2013", manifest["sources"][0]["name"])
        self.complete_diagnosis(audit)
        result, code = self.check(audit)
        self.assertEqual(code, 0, result)
        report = writer_audit.render_report(
            manifest,
            read_json(audit / writer_audit.STATE_NAME),
            read_json(audit / writer_audit.FINDINGS_NAME),
        ).decode("utf-8")
        self.assertIn("\u2013", report)

    def test_source_kind_override_and_qmd_detection(self) -> None:
        unknown = self.sources / "notes.custom"
        qmd = self.sources / "analysis.qmd"
        binary = self.sources / "appendix.docx"
        unknown.write_text("alpha\nbeta\n", encoding="utf-8")
        qmd.write_text("---\ntitle: Test\n---\n", encoding="utf-8")
        binary.write_bytes(b"PK\x03\x04binary")
        audit = self.base / "kind audit"
        self.initialize(
            audit,
            [unknown, qmd, binary],
            source_kind=[f"{unknown}=text"],
        )
        manifest = read_json(audit / writer_audit.MANIFEST_NAME)
        self.assertEqual(
            [item["kind"] for item in manifest["sources"]],
            ["text", "text", "artifact"],
        )
        self.assertEqual(manifest["sources"][0]["line_count"], 2)

    def test_cli_init_and_snapshotted_status_json(self) -> None:
        source = self.sources / "notes with space.custom"
        source.write_text("one\ntwo\n", encoding="utf-8")
        audit = self.base / "CLI audit space"
        initialized = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "init",
                "--audit-root",
                str(audit),
                "--skill-root",
                str(ROOT),
                "--source",
                str(source),
                "--source-kind",
                f"{source}=text",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=self.base,
        )
        self.assertEqual(
            initialized.returncode, 0, initialized.stdout + initialized.stderr
        )
        self.assertTrue(json.loads(initialized.stdout)["initialized"])
        status = subprocess.run(
            [
                sys.executable,
                str(audit / "protocol" / "scripts" / "writer_audit.py"),
                "status",
                "--audit-root",
                str(audit),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=self.base,
        )
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        payload = json.loads(status.stdout)
        self.assertTrue(payload["workspace_valid"])
        self.assertFalse(payload["final"])

    def test_pdf_page_count_bounds_page_anchors(self) -> None:
        pdf = self.sources / "supplement.pdf"
        pdf.write_bytes(b"not parsed because count is authoritatively supplied")
        audit = self.base / "pdf audit"
        self.initialize(audit, [self.source, pdf], pdf_page_count=[f"{pdf}=2"])
        page_anchor = self.anchor("SRC-002", "page", 2, 2)
        self.complete_diagnosis(
            audit, [self.finding("F-001", "Local", page_anchor)]
        )
        result, code = self.check(audit)
        self.assertEqual(code, 0, result)
        findings = read_json(audit / writer_audit.FINDINGS_NAME)
        findings["findings"][0]["anchors"][0]["end"] = 3
        write_json(audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check(audit)
        self.assertEqual(code, 1)
        self.assertIn("ANCHOR_PAGE_RANGE", issue_codes(result))

    def test_pdf_page_count_uses_exact_captured_snapshot_bytes(self) -> None:
        pdf = self.sources / "changing.pdf"
        captured = b"captured one-page PDF bytes"
        later = b"later two-page PDF bytes"
        pdf.write_bytes(captured)
        audit = self.base / "captured pdf audit"

        def inspect_captured(
            data: bytes,
            source_label: Path,
            override: str | None,
        ) -> int:
            self.assertEqual(data, captured)
            self.assertIsNone(override)
            source_label.write_bytes(later)
            return 1

        with mock.patch.object(
            writer_audit,
            "detect_pdf_page_count",
            side_effect=inspect_captured,
        ):
            self.initialize(audit, [pdf])
        manifest = read_json(audit / writer_audit.MANIFEST_NAME)
        self.assertEqual((audit / "inputs" / "SRC-001.pdf").read_bytes(), captured)
        self.assertEqual(pdf.read_bytes(), later)
        self.assertEqual(manifest["sources"][0]["page_count"], 1)

        page_two = self.finding(
            "F-001",
            "Local",
            self.anchor("SRC-001", "page", 2, 2),
        )
        self.complete_diagnosis(audit, [page_two])
        result, code = self.check(audit)
        self.assertEqual(code, 1)
        self.assertIn("ANCHOR_PAGE_RANGE", issue_codes(result))

    def test_cr_only_text_uses_logical_line_anchors(self) -> None:
        source = self.sources / "cr-only.tex"
        source.write_bytes(b"first line\rsecond line\r")
        audit = self.base / "cr line audit"
        self.initialize(audit, [source])
        manifest = read_json(audit / writer_audit.MANIFEST_NAME)
        self.assertEqual(manifest["sources"][0]["line_count"], 2)
        finding = self.finding(
            "F-001",
            "Local",
            self.anchor("SRC-001", "line", 2, 2),
        )
        self.complete_diagnosis(audit, [finding])
        result, code = self.check(audit)
        self.assertEqual(code, 0, result)

    def test_existing_root_is_never_overwritten(self) -> None:
        audit = self.base / "occupied"
        audit.mkdir()
        marker = audit / "keep.txt"
        marker.write_text("keep", encoding="utf-8")
        with self.assertRaises(writer_audit.AuditError):
            self.initialize(audit)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_initialization_failure_is_transactional(self) -> None:
        audit = self.base / "retryable audit"
        original = writer_audit.write_exclusive
        calls = 0

        def fail_third(path: Path, data: bytes) -> str:
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError("injected write failure")
            return original(path, data)

        with mock.patch.object(writer_audit, "write_exclusive", side_effect=fail_third):
            with self.assertRaises(OSError):
                self.initialize(audit)
        self.assertFalse(audit.exists())
        self.assertEqual(list(self.base.glob(".writer-audit-stage-*")), [])
        self.initialize(audit)
        self.assertTrue((audit / writer_audit.MANIFEST_NAME).is_file())

    def test_exclusive_write_preserves_preexisting_file_on_open_error(self) -> None:
        target = self.base / "preexisting.txt"
        target.write_text("KEEP", encoding="utf-8")
        with mock.patch.object(
            Path,
            "open",
            side_effect=PermissionError("injected access failure"),
        ):
            with self.assertRaises(PermissionError):
                writer_audit.write_exclusive(target, b"NEW")
        self.assertEqual(target.read_text(encoding="utf-8"), "KEEP")

    def test_exclusive_write_removes_only_new_partial_file(self) -> None:
        target = self.base / "new-partial.txt"
        with mock.patch.object(
            writer_audit.os,
            "fsync",
            side_effect=OSError("injected fsync failure"),
        ):
            with self.assertRaises(OSError):
                writer_audit.write_exclusive(target, b"partial")
        self.assertFalse(target.exists())

    def test_moved_audit_ignores_original_paths(self) -> None:
        self.complete_diagnosis()
        result, code = self.check(publish=True)
        self.assertEqual(code, 0, result)
        self.source.write_text("changed original\n", encoding="utf-8")
        moved = self.base / "moved audit space"
        shutil.move(str(self.audit), str(moved))
        result, code = self.status(moved)
        self.assertEqual(code, 0, result)
        self.assertTrue(result["final"])

    def test_snapshotted_checker_survives_later_skill_change(self) -> None:
        skill_copy = self.base / "skill copy"
        shutil.copytree(ROOT, skill_copy)
        audit = self.base / "snapshot checker audit"
        self.initialize(audit, skill_root=skill_copy)
        self.complete_diagnosis(audit)
        with (skill_copy / "scripts" / "writer_audit.py").open(
            "a", encoding="utf-8"
        ) as handle:
            handle.write("\n# Later installed version changed.\n")
        command = [
            sys.executable,
            str(audit / "protocol" / "scripts" / "writer_audit.py"),
            "check",
            "--audit-root",
            str(audit),
            "--json",
        ]
        completed = subprocess.run(
            command, check=False, capture_output=True, text=True, cwd=self.base
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["valid"])

    def test_snapshot_and_protocol_drift_fail_closed(self) -> None:
        cases = [
            ("inputs/SRC-001.tex", "SOURCE_SNAPSHOT_DRIFT"),
            ("protocol/SKILL.md", "PROTOCOL_SNAPSHOT_DRIFT"),
        ]
        for index, (relative, expected_code) in enumerate(cases, start=1):
            with self.subTest(relative=relative):
                audit = self.base / f"drift-{index}"
                self.initialize(audit)
                path = audit / relative
                path.write_bytes(path.read_bytes() + b"drift")
                result, code = self.status(audit)
                self.assertEqual(code, 1)
                self.assertIn(expected_code, issue_codes(result))

    def test_protocol_logical_paths_map_one_to_one_to_snapshots(self) -> None:
        manifest = read_json(self.audit / writer_audit.MANIFEST_NAME)
        records = {record["logical_path"]: record for record in manifest["protocol"]}
        target = records["references/argument-architecture.md"]
        other = records["references/revision-audit.md"]
        fields = ("snapshot_path", "sha256", "byte_size")
        target_values = {field: target[field] for field in fields}
        other_values = {field: other[field] for field in fields}
        target.update(other_values)
        other.update(target_values)
        manifest["semantic_binding_sha256"] = writer_audit.semantic_binding(manifest)
        codes = {issue.code for issue in writer_audit.validate_manifest(manifest, self.audit)}
        self.assertIn("PROTOCOL_SNAPSHOT_PATH", codes)
        self.assertNotIn("PROTOCOL_SNAPSHOT_DUPLICATE", codes)

    def test_duplicate_protocol_snapshot_targets_are_rejected(self) -> None:
        manifest = read_json(self.audit / writer_audit.MANIFEST_NAME)
        manifest["protocol"].append(
            json.loads(json.dumps(manifest["protocol"][0]))
        )
        manifest["semantic_binding_sha256"] = writer_audit.semantic_binding(manifest)
        codes = {issue.code for issue in writer_audit.validate_manifest(manifest, self.audit)}
        self.assertIn("PROTOCOL_SNAPSHOT_DUPLICATE", codes)

    def test_hard_linked_protocol_snapshot_targets_are_rejected(self) -> None:
        source = self.audit / "protocol" / "SKILL.md"
        alias = self.audit / "protocol" / "alias.md"
        try:
            os.link(source, alias)
        except OSError as error:
            self.skipTest(f"Hard links are unavailable in this test environment: {error}")
        manifest = read_json(self.audit / writer_audit.MANIFEST_NAME)
        manifest["protocol"].append(
            {
                "logical_path": "alias.md",
                "snapshot_path": "protocol/alias.md",
                "sha256": writer_audit.sha256_file(alias),
                "byte_size": alias.stat().st_size,
            }
        )
        manifest["semantic_binding_sha256"] = writer_audit.semantic_binding(manifest)
        codes = {issue.code for issue in writer_audit.validate_manifest(manifest, self.audit)}
        self.assertIn("PROTOCOL_SNAPSHOT_DUPLICATE", codes)

    def test_protocol_logical_paths_require_canonical_portable_form(self) -> None:
        cases = [
            ("C:protocol/SKILL.md", "PATH_NONPORTABLE"),
            ("references/C:foo.md", "PATH_NONPORTABLE"),
            ("references\\foo.md", "PATH_NONPORTABLE"),
            ("../SKILL.md", "PATH_ESCAPE"),
            ("references//foo.md", "PATH_NONCANONICAL"),
        ]
        for logical_path, expected_code in cases:
            with self.subTest(logical_path=logical_path):
                manifest = read_json(self.audit / writer_audit.MANIFEST_NAME)
                record = manifest["protocol"][0]
                record["logical_path"] = logical_path
                record["snapshot_path"] = writer_audit.protocol_snapshot_path(
                    logical_path
                )
                manifest["semantic_binding_sha256"] = writer_audit.semantic_binding(
                    manifest
                )
                codes = {
                    issue.code
                    for issue in writer_audit.validate_manifest(manifest, self.audit)
                }
                self.assertIn(expected_code, codes)

    def test_required_protocol_set_includes_shared_audit_contracts(self) -> None:
        for index, logical_path in enumerate(
            (
                "references/argument-architecture.md",
                "references/quick-section-audit.md",
                "references/full-audit-operations.md",
                "references/full-audit-data-contract.md",
            ),
            start=1,
        ):
            with self.subTest(logical_path=logical_path):
                audit = self.base / f"missing-required-protocol-{index}"
                self.initialize(audit)
                manifest = read_json(audit / writer_audit.MANIFEST_NAME)
                manifest["protocol"] = [
                    record
                    for record in manifest["protocol"]
                    if record["logical_path"] != logical_path
                ]
                manifest["semantic_binding_sha256"] = writer_audit.semantic_binding(manifest)
                issues = writer_audit.validate_manifest(manifest, audit)
                self.assertIn("PROTOCOL_REQUIRED_MISSING", {item.code for item in issues})

    def test_malformed_nested_json_never_crashes(self) -> None:
        mutations = {
            "scope": lambda value: value.__setitem__("scope", None),
            "protocol": lambda value: value.__setitem__("protocol", None),
            "pass_plan": lambda value: value.__setitem__("pass_plan", [None]),
        }
        for index, (name, mutate) in enumerate(mutations.items(), start=1):
            with self.subTest(name=name):
                audit = self.base / f"malformed-{index}"
                self.initialize(audit)
                manifest = read_json(audit / writer_audit.MANIFEST_NAME)
                mutate(manifest)
                write_json(audit / writer_audit.MANIFEST_NAME, manifest)
                result, code = self.status(audit)
                self.assertEqual(code, 1)
                self.assertTrue(result["errors"])

    def test_unhashable_json_field_types_return_structured_cli_errors(self) -> None:
        mutations = [
            (
                writer_audit.MANIFEST_NAME,
                lambda value: value["scope"].__setitem__("action", []),
            ),
            (
                writer_audit.MANIFEST_NAME,
                lambda value: value["sources"][0].__setitem__("kind", {}),
            ),
            (
                writer_audit.MANIFEST_NAME,
                lambda value: value["protocol"][0].__setitem__("logical_path", []),
            ),
            (
                writer_audit.STATE_NAME,
                lambda value: value["passes"][0].__setitem__("status", []),
            ),
            (
                writer_audit.STATE_NAME,
                lambda value: value["closure"]["compile"].__setitem__("status", {}),
            ),
            (
                writer_audit.FINDINGS_NAME,
                lambda value: value["assessment"].__setitem__("status", []),
            ),
            (
                writer_audit.FINDINGS_NAME,
                lambda value: value["findings"][0].__setitem__("priority", {}),
            ),
            (
                writer_audit.FINDINGS_NAME,
                lambda value: value["findings"][0]["anchors"][0].__setitem__(
                    "source_id", []
                ),
            ),
            (
                writer_audit.FINDINGS_NAME,
                lambda value: value["contribution_ledger"].__setitem__("status", {}),
            ),
        ]
        for index, (filename, mutate) in enumerate(mutations, start=1):
            with self.subTest(index=index, filename=filename):
                audit = self.base / f"type-fuzz-{index}"
                self.initialize(audit)
                self.complete_diagnosis(
                    audit,
                    [self.finding("F-001", "Local")],
                )
                path = audit / filename
                value = read_json(path)
                mutate(value)
                write_json(path, value)
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "status",
                        "--audit-root",
                        str(audit),
                        "--json",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=self.base,
                )
                self.assertEqual(completed.returncode, 1)
                self.assertNotIn("Traceback", completed.stderr)
                payload = json.loads(completed.stdout)
                self.assertTrue(payload["errors"])

    def test_oversized_finding_id_is_structurally_rejected(self) -> None:
        finding = self.finding("F-" + "1" * 5000, "Local")
        self.complete_diagnosis(findings_records=[finding])
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "check",
                "--audit-root",
                str(self.audit),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=self.base,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertNotIn("Traceback", completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn("FINDING_ID", issue_codes(payload))

    def test_cli_fallback_serializes_unexpected_type_errors(self) -> None:
        with mock.patch.object(
            writer_audit,
            "status_audit",
            side_effect=TypeError("injected unexpected type failure"),
        ):
            with mock.patch("sys.stdout", new_callable=io.StringIO) as output:
                code = writer_audit.main(
                    [
                        "status",
                        "--audit-root",
                        str(self.audit),
                        "--json",
                    ]
                )
        self.assertEqual(code, 1)
        payload = json.loads(output.getvalue())
        self.assertIn("WORKFLOW_ERROR", issue_codes(payload))

    def test_duplicate_keys_and_nan_return_structured_cli_errors(self) -> None:
        cases = [
            '{"schema_version":"3.0","schema_version":"3.0"}',
            '{"schema_version":NaN}',
        ]
        for index, raw in enumerate(cases, start=1):
            with self.subTest(raw=raw):
                audit = self.base / f"invalid-json-{index}"
                self.initialize(audit)
                (audit / writer_audit.STATE_NAME).write_text(raw, encoding="utf-8")
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "status",
                        "--audit-root",
                        str(audit),
                        "--json",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=self.base,
                )
                self.assertEqual(completed.returncode, 1)
                payload = json.loads(completed.stdout)
                self.assertIn("STATE_JSON_INVALID", issue_codes(payload))

    def test_default_and_focused_pass_plans_are_exact(self) -> None:
        default = read_json(self.audit / writer_audit.MANIFEST_NAME)["pass_plan"]
        self.assertEqual(
            [item["tag"] for item in default], writer_audit.DEFAULT_PASS_PLAN
        )
        self.assertEqual(default[-1]["requirement"], "not_required")
        contribution = next(
            item for item in default if item["tag"] == "CONTRIBUTION_LEDGER"
        )
        self.assertEqual(contribution["requirement"], "conditional")

        audit = self.base / "focused"
        selected = ["WHOLE_PAPER_NARRATIVE", "CONTRIBUTION_LEDGER"]
        self.initialize(audit, focused=selected)
        plan = read_json(audit / writer_audit.MANIFEST_NAME)["pass_plan"]
        self.assertEqual(
            [item["tag"] for item in plan],
            ["ORIENTATION", *selected, "REVISION_CLOSURE"],
        )
        self.assertEqual(plan[1]["requirement"], "required")
        self.assertEqual(plan[2]["requirement"], "required")

    def test_focused_init_requires_focus_and_projects_scope_to_report(self) -> None:
        missing_focus = self.base / "focused without focus"
        with self.assertRaisesRegex(writer_audit.AuditError, "--focus is required"):
            self.initialize(
                missing_focus,
                focused=["WHOLE_PAPER_NARRATIVE"],
                focus=None,
            )
        self.assertFalse(missing_focus.exists())

        for index, control in enumerate(["\x00", "\r", "\n", "\t"], start=1):
            invalid_focus = self.base / f"focused invalid focus {index}"
            with self.subTest(control=repr(control)):
                with self.assertRaisesRegex(
                    writer_audit.AuditError, "single-line"
                ):
                    self.initialize(
                        invalid_focus,
                        focused=["WHOLE_PAPER_NARRATIVE"],
                        focus=f"whole paper{control}narrative",
                    )
                self.assertFalse(invalid_focus.exists())

        focused = self.base / "focused scope report"
        selected = ["WHOLE_PAPER_NARRATIVE", "CONTRIBUTION_LEDGER"]
        self.initialize(
            focused,
            action="audit",
            focused=selected,
            focus="abstract and introduction positioning",
        )
        self.complete_diagnosis(focused, contribution="not_needed")
        report = writer_audit.render_report(
            read_json(focused / writer_audit.MANIFEST_NAME),
            read_json(focused / writer_audit.STATE_NAME),
            read_json(focused / writer_audit.FINDINGS_NAME),
        ).decode("utf-8")
        self.assertIn("- Action: audit", report)
        self.assertIn("- Plan: focused", report)
        self.assertIn("- Focus: abstract and introduction positioning", report)
        self.assertIn(
            "- Selected evaluative passes: " + ", ".join(selected), report
        )
        self.assertNotIn("ATOMIC_DOCUMENTARY_CONSISTENCY", report)

    def test_incomplete_passes_findings_and_reporting_cannot_finalize(self) -> None:
        result, code = self.check()
        self.assertEqual(code, 1)
        codes = issue_codes(result)
        self.assertIn("STATE_PASS_PENDING", codes)
        self.assertIn("STATE_REPORTING_PENDING", codes)
        self.assertIn("ASSESSMENT_PENDING", codes)
        self.assertIn("LEDGER_PENDING", codes)
        self.complete_diagnosis()
        result, code = self.check()
        self.assertEqual(code, 0, result)
        self.assertTrue(result["valid"])
        self.assertFalse(result["final"])

    def test_orientation_loads_only_neutral_audit_guidance(self) -> None:
        self.complete_diagnosis()
        state = read_json(self.audit / writer_audit.STATE_NAME)
        state["passes"][0]["loaded_references"].append(
            "references/polishing-protocol.md"
        )
        write_json(self.audit / writer_audit.STATE_NAME, state)
        result, code = self.check()
        self.assertEqual(code, 1)
        self.assertIn("STATE_ORIENTATION_REFERENCES", issue_codes(result))

    def test_shared_passes_require_quick_section_reference(self) -> None:
        self.complete_diagnosis()
        base_state = read_json(self.audit / writer_audit.STATE_NAME)
        for tag in sorted(writer_audit.QUICK_SECTION_PASS_TAGS):
            with self.subTest(tag=tag):
                state = json.loads(json.dumps(base_state))
                record = next(item for item in state["passes"] if item["tag"] == tag)
                record["loaded_references"].remove(writer_audit.QUICK_SECTION_REFERENCE)
                write_json(self.audit / writer_audit.STATE_NAME, state)
                result, code = self.check()
                self.assertEqual(code, 1)
                self.assertIn(
                    "STATE_PASS_QUICK_SECTION_REFERENCE", issue_codes(result)
                )

    def test_argument_passes_require_owner_reference_in_default_and_focused_plans(
        self,
    ) -> None:
        contexts: list[tuple[Path, str]] = []
        self.complete_diagnosis(contribution="included")
        contexts.append((self.audit, "default"))

        focused = self.base / "focused argument owners"
        self.initialize(
            focused,
            focused=["CONTRIBUTION_LEDGER", "WHOLE_PAPER_NARRATIVE"],
            focus="contribution hierarchy and paper narrative",
        )
        self.complete_diagnosis(focused, contribution="not_needed")
        contexts.append((focused, "focused"))

        for audit, plan_kind in contexts:
            base_state = read_json(audit / writer_audit.STATE_NAME)
            for tag in ("CONTRIBUTION_LEDGER", "WHOLE_PAPER_NARRATIVE"):
                with self.subTest(plan_kind=plan_kind, tag=tag):
                    state = json.loads(json.dumps(base_state))
                    record = next(item for item in state["passes"] if item["tag"] == tag)
                    record["loaded_references"].remove(
                        writer_audit.ARGUMENT_ARCHITECTURE_REFERENCE
                    )
                    write_json(audit / writer_audit.STATE_NAME, state)
                    result, code = self.check(audit)
                    self.assertEqual(code, 1)
                    self.assertIn("STATE_PASS_OWNER_REFERENCE", issue_codes(result))
            write_json(audit / writer_audit.STATE_NAME, base_state)

    def test_completed_reporting_requires_all_contract_references(self) -> None:
        self.complete_diagnosis()
        base_state = read_json(self.audit / writer_audit.STATE_NAME)
        for missing in writer_audit.REPORTING_REFERENCES:
            with self.subTest(missing=missing):
                state = json.loads(json.dumps(base_state))
                state["reporting"]["loaded_references"].remove(missing)
                write_json(self.audit / writer_audit.STATE_NAME, state)
                result, code = self.check()
                self.assertEqual(code, 1)
                self.assertIn("STATE_REPORTING_REFERENCES", issue_codes(result))

    def test_audit_only_closure_states_are_exact(self) -> None:
        self.complete_diagnosis()
        state = read_json(self.audit / writer_audit.STATE_NAME)
        state["passes"][-1].update(
            status="completed",
            loaded_references=["references/polishing-protocol.md"],
            checkpoint="Improperly completed revision closure.",
            reason=None,
        )
        state["closure"]["edits"]["diff_status"] = "clean"
        write_json(self.audit / writer_audit.STATE_NAME, state)
        result, code = self.check()
        self.assertEqual(code, 1)
        codes = issue_codes(result)
        self.assertIn("STATE_DECLARED_SKIP_CHANGED", codes)
        self.assertIn("CLOSURE_AUDIT_ONLY_DIFF", codes)

    def test_closure_artifacts_are_required_and_hash_bound(self) -> None:
        self.complete_diagnosis()
        state = read_json(self.audit / writer_audit.STATE_NAME)
        state["closure"]["compile"] = {
            "phase": "audit",
            "status": "passed",
            "evidence": "The bound compiler log records a successful compile.",
            "artifact": None,
        }
        write_json(self.audit / writer_audit.STATE_NAME, state)
        result, code = self.check()
        self.assertEqual(code, 1)
        self.assertIn("ARTIFACT_REQUIRED", issue_codes(result))

        log = self.audit / "artifacts" / "compile.log"
        log.parent.mkdir(exist_ok=True)
        log.write_text("compile passed\n", encoding="utf-8")
        state["closure"]["compile"]["artifact"] = {
            "path": "artifacts/compile.log",
            "sha256": writer_audit.sha256_file(log),
        }
        write_json(self.audit / writer_audit.STATE_NAME, state)
        result, code = self.check()
        self.assertEqual(code, 0, result)
        log.write_text("changed log\n", encoding="utf-8")
        result, code = self.check()
        self.assertEqual(code, 1)
        self.assertIn("ARTIFACT_DRIFT", issue_codes(result))

    def test_artifact_paths_require_canonical_posix_relative_form(self) -> None:
        self.complete_diagnosis()
        artifact = self.audit / "artifacts" / "compile.log"
        artifact.parent.mkdir(exist_ok=True)
        artifact.write_text("compile passed\n", encoding="utf-8")
        base_state = read_json(self.audit / writer_audit.STATE_NAME)
        cases = [
            ("artifacts\\compile.log", "PATH_NONPORTABLE"),
            ("artifacts/C:compile.log", "PATH_NONPORTABLE"),
            ("../compile.log", "PATH_ESCAPE"),
            ("artifacts//compile.log", "PATH_NONCANONICAL"),
        ]
        for raw_path, expected_code in cases:
            with self.subTest(raw_path=raw_path):
                state = json.loads(json.dumps(base_state))
                state["closure"]["compile"] = {
                    "phase": "audit",
                    "status": "passed",
                    "evidence": "The bound compiler result was inspected.",
                    "artifact": {
                        "path": raw_path,
                        "sha256": writer_audit.sha256_file(artifact),
                    },
                }
                write_json(self.audit / writer_audit.STATE_NAME, state)
                result, code = self.check()
                self.assertEqual(code, 1)
                self.assertIn(expected_code, issue_codes(result))

        state = json.loads(json.dumps(base_state))
        state["closure"]["compile"] = {
            "phase": "audit",
            "status": "passed",
            "evidence": "The bound compiler result was inspected.",
            "artifact": {
                "path": "artifacts/compile.log",
                "sha256": writer_audit.sha256_file(artifact),
            },
        }
        write_json(self.audit / writer_audit.STATE_NAME, state)
        result, code = self.check()
        self.assertEqual(code, 0, result)

    def test_closure_evidence_must_be_bound_under_artifacts(self) -> None:
        self.complete_diagnosis()
        report = self.audit / writer_audit.REPORT_NAME
        report.write_text("orphan report fixture\n", encoding="utf-8")
        base_state = read_json(self.audit / writer_audit.STATE_NAME)
        candidates = [
            "inputs/SRC-001.tex",
            "protocol/SKILL.md",
            writer_audit.STATE_NAME,
            writer_audit.FINDINGS_NAME,
            writer_audit.REPORT_NAME,
        ]
        for relative in candidates:
            with self.subTest(relative=relative):
                artifact = self.audit / relative
                state = json.loads(json.dumps(base_state))
                state["closure"]["compile"] = {
                    "phase": "audit",
                    "status": "passed",
                    "evidence": "The candidate closure file was inspected.",
                    "artifact": {
                        "path": relative,
                        "sha256": writer_audit.sha256_file(artifact),
                    },
                }
                write_json(self.audit / writer_audit.STATE_NAME, state)
                result, code = self.check()
                self.assertEqual(code, 1)
                self.assertIn("ARTIFACT_LOCATION", issue_codes(result))

        write_json(self.audit / writer_audit.STATE_NAME, base_state)
        report.unlink()

    def test_finding_priority_and_remedy_relations(self) -> None:
        records = [
            self.finding("F-001", "Blocking"),
            self.finding("F-002", "Material"),
            self.finding("F-003", "Local", remedy="safe_presentation_edit"),
        ]
        self.complete_diagnosis(findings_records=records)
        result, code = self.check()
        self.assertEqual(code, 0, result)
        findings = read_json(self.audit / writer_audit.FINDINGS_NAME)
        material = findings["findings"][1]
        material["safe_repair_available"] = False
        material["remedy_type"] = "author_decision"
        write_json(self.audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check()
        self.assertEqual(code, 1)
        self.assertIn("FINDING_NONBLOCKING_REPAIR", issue_codes(result))

        self.complete_diagnosis(findings_records=records)
        findings = read_json(self.audit / writer_audit.FINDINGS_NAME)
        findings["findings"][0]["priority"] = "Author input required"
        write_json(self.audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check()
        self.assertEqual(code, 1)
        self.assertIn("FINDING_PRIORITY", issue_codes(result))

    def test_priority_display_labels_cover_canonical_priorities(self) -> None:
        self.assertEqual(
            set(writer_audit.PRIORITY_DISPLAY_LABELS),
            writer_audit.ALLOWED_PRIORITIES,
        )
        self.assertEqual(
            writer_audit.PRIORITY_DISPLAY_LABELS["Blocking"],
            "Author input required",
        )
        self.assertNotIn("Blocking", writer_audit.PRIORITY_DISPLAY_LABELS.values())

    def test_blocking_question_rejects_bare_deictic_reference(self) -> None:
        for question in [
            "Which estimator should replace this in the reported application section now?",
            "Which estimator should replace that in the reported application section now?",
        ]:
            with self.subTest(question=question):
                self.assertFalse(writer_audit.question_is_self_contained(question))
        for question in [
            "Should this estimator replace the oracle estimator in the application section?",
            "Could the authors confirm that the estimator was fitted in the application?",
        ]:
            with self.subTest(question=question):
                self.assertTrue(writer_audit.question_is_self_contained(question))
        self.assertFalse(
            writer_audit.question_is_self_contained(
                "Could the authors explain why that remains unresolved in the application?"
            )
        )
        self.assertTrue(
            writer_audit.question_is_self_contained(
                "Which theorem shows that the estimator converges under the stated assumptions?"
            )
        )
        self.assertFalse(
            writer_audit.question_is_self_contained(
                "Could the authors explain why it should change under the stated assumptions?"
            )
        )
        self.assertFalse(
            writer_audit.question_is_self_contained(
                "Could the authors explain it under the stated assumptions in Section 3?"
            )
        )
        self.assertTrue(
            writer_audit.question_is_self_contained(
                "Does the estimator T_n remain valid when it is used under Assumption 2?"
            )
        )
        finding = self.finding("F-001", "Blocking")
        finding["author_question"] = (
            "Could the authors clarify whether this should be changed in the paper?"
        )
        self.complete_diagnosis(
            findings_records=[finding],
            contribution="unavailable",
        )
        result, code = self.check(publish=True)
        self.assertEqual(code, 1)
        self.assertFalse(result["final"])
        self.assertIn("FINDING_AUTHOR_QUESTION", issue_codes(result))

        findings = read_json(self.audit / writer_audit.FINDINGS_NAME)
        findings["findings"][0]["author_question"] = (
            "Which named estimator did the authors use for the reported application?"
        )
        write_json(self.audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check()
        self.assertEqual(code, 0, result)

    def test_line_page_and_artifact_anchor_contracts(self) -> None:
        pdf = self.sources / "paper.pdf"
        image = self.sources / "figure.png"
        pdf.write_bytes(b"fixture pdf")
        image.write_bytes(b"fixture image")
        audit = self.base / "mixed anchors"
        self.initialize(
            audit,
            [self.source, pdf, image],
            pdf_page_count=[f"{pdf}=4"],
        )
        records = [
            self.finding("F-001", "Local", self.anchor("SRC-001", "line", 1, 1)),
            self.finding("F-002", "Local", self.anchor("SRC-002", "page", 4, 4)),
            self.finding(
                "F-003",
                "Local",
                self.anchor("SRC-003", "artifact", None, None, "panel A"),
            ),
        ]
        self.complete_diagnosis(audit, records)
        result, code = self.check(audit)
        self.assertEqual(code, 0, result)
        findings = read_json(audit / writer_audit.FINDINGS_NAME)
        findings["findings"][1]["anchors"][0]["kind"] = "line"
        write_json(audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check(audit)
        self.assertEqual(code, 1)
        self.assertIn("ANCHOR_KIND", issue_codes(result))

    def test_contribution_ledger_outcomes_are_distinct(self) -> None:
        included = self.base / "ledger included"
        self.initialize(included)
        self.complete_diagnosis(included, contribution="included")
        result, code = self.check(included)
        self.assertEqual(code, 0, result)

        not_needed = self.base / "ledger not needed"
        self.initialize(
            not_needed, focused=["CONTRIBUTION_LEDGER"]
        )
        self.complete_diagnosis(not_needed, contribution="not_needed")
        result, code = self.check(not_needed)
        self.assertEqual(code, 0, result)

        unavailable = self.base / "ledger unavailable"
        self.initialize(unavailable, focused=["CONTRIBUTION_LEDGER"])
        blocking = self.finding("F-010", "Blocking")
        self.complete_diagnosis(
            unavailable, [blocking], contribution="unavailable"
        )
        result, code = self.check(unavailable)
        self.assertEqual(code, 0, result)
        findings = read_json(unavailable / writer_audit.FINDINGS_NAME)
        self.assertEqual(findings["findings"][0]["priority"], "Blocking")
        report = writer_audit.render_report(
            read_json(unavailable / writer_audit.MANIFEST_NAME),
            read_json(unavailable / writer_audit.STATE_NAME),
            findings,
        ).decode("utf-8")
        self.assertIn("Findings requiring author input: F-010", report)
        self.assertNotIn("Blocking findings:", report)
        findings["contribution_ledger"]["blocking_finding_ids"] = [
            "F-010",
            "F-010",
        ]
        write_json(unavailable / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check(unavailable)
        self.assertEqual(code, 1)
        duplicate_errors = [
            item
            for item in result["errors"]
            if item["code"] == "LEDGER_BLOCKING_IDS_DUPLICATE"
        ]
        self.assertEqual(len(duplicate_errors), 1)
        self.assertEqual(
            duplicate_errors[0]["message"],
            "Ledger finding IDs requiring author input must be unique.",
        )
        self.assertNotIn("blocking", duplicate_errors[0]["message"].casefold())
        findings["contribution_ledger"]["blocking_finding_ids"] = []
        write_json(unavailable / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check(unavailable)
        self.assertEqual(code, 1)
        self.assertIn("LEDGER_BLOCKING_IDS_REQUIRED", issue_codes(result))

    def test_contribution_ranks_allow_only_factual_contract_values(self) -> None:
        self.complete_diagnosis(contribution="included")
        base_findings = read_json(self.audit / writer_audit.FINDINGS_NAME)
        for rank in ["1", "27", "Co-primary", "Unclear"]:
            with self.subTest(rank=rank):
                findings = json.loads(json.dumps(base_findings))
                findings["contribution_ledger"]["rows"][0]["cells"]["Rank"] = rank
                write_json(self.audit / writer_audit.FINDINGS_NAME, findings)
                result, code = self.check()
                self.assertEqual(code, 0, result)

        findings = json.loads(json.dumps(base_findings))
        findings["contribution_ledger"]["rows"][0]["cells"]["Rank"] = (
            "Candidate primary contribution"
        )
        write_json(self.audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check()
        self.assertEqual(code, 1)
        self.assertIn("LEDGER_RANK", issue_codes(result))

    def test_report_orders_by_consequence_and_renders_provenance(self) -> None:
        records = [
            self.finding("F-001", "Local"),
            self.finding("F-003", "Blocking"),
            self.finding("F-002", "Material"),
        ]
        self.complete_diagnosis(
            findings_records=records, contribution="included"
        )
        manifest = read_json(self.audit / writer_audit.MANIFEST_NAME)
        state = read_json(self.audit / writer_audit.STATE_NAME)
        findings = read_json(self.audit / writer_audit.FINDINGS_NAME)
        first = writer_audit.render_report(manifest, state, findings)
        second = writer_audit.render_report(manifest, state, findings)
        self.assertEqual(first, second)
        report = first.decode("utf-8")
        self.assertLess(report.index("F-003"), report.index("F-002"))
        self.assertLess(report.index("F-002"), report.index("F-001"))
        self.assertIn("Priority: Author input required", report)
        self.assertNotIn("Priority: Blocking", report)
        self.assertEqual(report.count(writer_audit.AUDIT_BOUNDARY), 1)
        self.assertIn("Identity anchors:", report)
        self.assertIn("SRC-001 line 2", report)
        self.assertIn("Compile [audit]:", report)

    def test_canonical_authored_report_fields_reject_controls(self) -> None:
        self.complete_diagnosis(findings_records=[self.finding("F-001", "Local")])
        base_state = read_json(self.audit / writer_audit.STATE_NAME)
        base_findings = read_json(self.audit / writer_audit.FINDINGS_NAME)
        for control in ["\x00", "\r", "\n", "\t", "\x85", "\u2028"]:
            with self.subTest(control=repr(control)):
                findings = json.loads(json.dumps(base_findings))
                findings["findings"][0]["title"] = f"unsafe{control}title"
                write_json(self.audit / writer_audit.STATE_NAME, base_state)
                write_json(self.audit / writer_audit.FINDINGS_NAME, findings)
                result, code = self.check()
                self.assertEqual(code, 1)
                self.assertIn("FORBIDDEN_CONTROL", issue_codes(result))

        findings = json.loads(json.dumps(base_findings))
        findings["findings"][0]["anchors"][0] = self.anchor(
            kind="artifact", start=None, end=None, locator="panel\nA"
        )
        write_json(self.audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check()
        self.assertEqual(code, 1)
        self.assertIn("FORBIDDEN_CONTROL", issue_codes(result))

        state = json.loads(json.dumps(base_state))
        state["passes"][0]["checkpoint"] = "orientation\tcomplete"
        write_json(self.audit / writer_audit.STATE_NAME, state)
        write_json(self.audit / writer_audit.FINDINGS_NAME, base_findings)
        result, code = self.check()
        self.assertEqual(code, 1)
        self.assertIn("FORBIDDEN_CONTROL", issue_codes(result))

        latex = r"The supplied macro $\widehat{\theta}_n$ is preserved."
        findings = json.loads(json.dumps(base_findings))
        findings["findings"][0]["observed_evidence"] = latex
        write_json(self.audit / writer_audit.STATE_NAME, base_state)
        write_json(self.audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check()
        self.assertEqual(code, 0, result)
        report = writer_audit.render_report(
            read_json(self.audit / writer_audit.MANIFEST_NAME),
            base_state,
            findings,
        ).decode("utf-8")
        self.assertIn(latex, report)

    def test_report_defensively_normalizes_all_free_text_including_locator_and_disposition(
        self,
    ) -> None:
        audit = self.base / "report controls"
        self.initialize(audit, action="audit-and-revise")
        self.complete_diagnosis(
            audit,
            findings_records=[self.finding("F-001", "Local")],
        )
        result, code = self.freeze(audit)
        self.assertEqual(code, 0, result)
        self.finish_revision(audit, applied=False)

        manifest = read_json(audit / writer_audit.MANIFEST_NAME)
        state = read_json(audit / writer_audit.STATE_NAME)
        findings = read_json(audit / writer_audit.FINDINGS_NAME)
        state["closure"]["edits"]["finding_dispositions"][0]["reason"] = (
            "unsafe\rdisposition"
        )
        write_json(audit / writer_audit.STATE_NAME, state)
        result, code = self.check(audit)
        self.assertEqual(code, 1)
        self.assertIn("FORBIDDEN_CONTROL", issue_codes(result))

        injected = "alpha\r\n\n## Injected\t\x00\x85\u2028" + r"$\widehat{\theta}_n$"
        manifest["scope"]["focus"] = injected
        state["passes"][0]["checkpoint"] = injected
        state["closure"]["compile"]["evidence"] = injected
        state["closure"]["render"]["evidence"] = injected
        state["closure"]["edits"]["evidence"] = injected
        state["closure"]["edits"]["finding_dispositions"][0]["reason"] = injected
        finding = findings["findings"][0]
        finding["title"] = injected
        finding["observed_evidence"] = injected
        finding["inferred_consequence"] = injected
        finding["revision_direction"] = injected
        finding["anchors"][0] = self.anchor(
            kind="artifact", start=None, end=None, locator=injected
        )
        findings["assessment"]["boundary"] = injected
        findings["contribution_ledger"]["reason"] = injected
        report = writer_audit.render_report(manifest, state, findings).decode("utf-8")
        self.assertNotIn("\r", report)
        self.assertNotIn("\t", report)
        self.assertNotIn("\x00", report)
        self.assertNotIn("\x85", report)
        self.assertNotIn("\u2028", report)
        self.assertNotIn("\n## Injected", report)
        self.assertIn(r"$\widehat{\theta}_n$", report)

    def test_report_orders_bounded_finding_ids_without_integer_conversion(self) -> None:
        records = [
            self.finding("F-1000", "Local"),
            self.finding("F-999", "Local"),
        ]
        self.complete_diagnosis(findings_records=records)
        report = writer_audit.render_report(
            read_json(self.audit / writer_audit.MANIFEST_NAME),
            read_json(self.audit / writer_audit.STATE_NAME),
            read_json(self.audit / writer_audit.FINDINGS_NAME),
        ).decode("utf-8")
        self.assertLess(report.index("F-999"), report.index("F-1000"))

    def test_source_dashes_are_preserved_and_authored_dashes_are_rejected(self) -> None:
        source = self.sources / "dash-source.tex"
        source.write_text(
            "The Neyman\u2013Pearson lemma is cited.\nA second anchored line follows.\n",
            encoding="utf-8",
        )
        audit = self.base / "dash scope audit"
        self.initialize(audit, [source])
        record = self.finding("F-001", "Local")
        record["observed_evidence"] = (
            "The supplied sentence names the Neyman\u2013Pearson lemma."
        )
        self.complete_diagnosis(audit, [record], contribution="included")
        findings = read_json(audit / writer_audit.FINDINGS_NAME)
        findings["contribution_ledger"]["rows"][0]["cells"][
            "Method object or construction"
        ] = "The Neyman\u2013Pearson construction"
        write_json(audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.check(audit)
        self.assertEqual(code, 0, result)
        self.assertIn(
            "\u2013",
            (audit / "inputs" / "SRC-001.tex").read_text(encoding="utf-8"),
        )
        report = writer_audit.render_report(
            read_json(audit / writer_audit.MANIFEST_NAME),
            read_json(audit / writer_audit.STATE_NAME),
            read_json(audit / writer_audit.FINDINGS_NAME),
        ).decode("utf-8")
        self.assertIn("Neyman\u2013Pearson lemma", report)
        self.assertIn("Neyman\u2013Pearson construction", report)

        record["title"] = "Invalid\u2014title"
        self.complete_diagnosis(audit, [record], contribution="included")
        result, code = self.check(audit)
        self.assertEqual(code, 1)
        self.assertIn("FORBIDDEN_DASH", issue_codes(result))

        record["title"] = "Valid title"
        self.complete_diagnosis(audit, [record], contribution="included")
        state = read_json(audit / writer_audit.STATE_NAME)
        state["passes"][0]["checkpoint"] = "Invalid\u2014checkpoint"
        write_json(audit / writer_audit.STATE_NAME, state)
        result, code = self.check(audit)
        self.assertEqual(code, 1)
        self.assertIn("FORBIDDEN_DASH", issue_codes(result))

    def test_freeze_requires_complete_pre_edit_diagnosis(self) -> None:
        audit = self.base / "revision audit"
        self.initialize(audit, action="audit-and-revise")
        result, code = self.freeze(audit)
        self.assertEqual(code, 1)
        self.assertIn("FREEZE_DIAGNOSTIC_PENDING", issue_codes(result))
        self.complete_diagnosis(audit)
        result, code = self.freeze(audit)
        self.assertEqual(code, 0, result)
        self.assertTrue(result["frozen"])

    def test_revision_dispositions_are_exact_and_rendered(self) -> None:
        audit = self.base / "revision dispositions"
        self.initialize(audit, action="audit-and-revise")
        records = [
            self.finding("F-001", "Material"),
            self.finding("F-002", "Blocking"),
        ]
        self.complete_diagnosis(audit, records)
        result, code = self.freeze(audit)
        self.assertEqual(code, 0, result)
        self.finish_revision(audit, applied=True)
        result, code = self.check(audit, publish=True)
        self.assertEqual(code, 0, result)
        self.assertTrue(result["final"])
        report = (audit / writer_audit.REPORT_NAME).read_text(encoding="utf-8")
        self.assertIn("Revision outcome: applied", report)
        self.assertIn("Revision outcome: unresolved", report)
        self.assertIn("Compile [post_edit]:", report)
        self.assertIn("Render [post_edit]:", report)

    def test_revision_disposition_contract_fails_closed(self) -> None:
        audit = self.base / "disposition failures"
        self.initialize(audit, action="audit-and-revise")
        records = [
            self.finding("F-001", "Material"),
            self.finding("F-002", "Local"),
        ]
        self.complete_diagnosis(audit, records)
        result, code = self.freeze(audit)
        self.assertEqual(code, 0, result)
        self.finish_revision(audit, applied=False)
        valid_state = read_json(audit / writer_audit.STATE_NAME)
        unused_diff = audit / "artifacts" / "unused.diff"
        unused_diff.parent.mkdir(exist_ok=True)
        unused_diff.write_text("unused diff\n", encoding="utf-8")
        unused_binding = {
            "path": "artifacts/unused.diff",
            "sha256": writer_audit.sha256_file(unused_diff),
        }

        def missing(value: dict) -> None:
            value["closure"]["edits"]["finding_dispositions"].pop()

        def reversed_order(value: dict) -> None:
            value["closure"]["edits"]["finding_dispositions"].reverse()

        def empty_reason(value: dict) -> None:
            value["closure"]["edits"]["finding_dispositions"][0]["reason"] = ""

        def invalid_nonblocking_outcome(value: dict) -> None:
            value["closure"]["edits"]["finding_dispositions"][0][
                "outcome"
            ] = "unresolved"

        def applied_without_edit(value: dict) -> None:
            value["closure"]["edits"]["finding_dispositions"][0][
                "outcome"
            ] = "applied"

        def unresolved_dispositions(value: dict) -> None:
            value["closure"]["edits"]["finding_dispositions"] = None

        def edit_without_applied_outcome(value: dict) -> None:
            value["closure"]["edits"].update(
                applied=True,
                diff_status="changed",
                evidence="A diff was recorded without an applied finding outcome.",
                artifact=unused_binding,
            )
            value["closure"]["compile"]["phase"] = "post_edit"
            value["closure"]["render"]["phase"] = "post_edit"

        def artifact_without_edit(value: dict) -> None:
            value["closure"]["edits"]["artifact"] = unused_binding

        cases = [
            (missing, "CLOSURE_DISPOSITION_COVERAGE"),
            (reversed_order, "CLOSURE_DISPOSITION_ORDER"),
            (empty_reason, "CLOSURE_DISPOSITION_REASON"),
            (invalid_nonblocking_outcome, "CLOSURE_DISPOSITION_PRIORITY"),
            (applied_without_edit, "CLOSURE_DISPOSITION_APPLIED_MISMATCH"),
            (unresolved_dispositions, "CLOSURE_DISPOSITIONS_PENDING"),
            (
                edit_without_applied_outcome,
                "CLOSURE_DISPOSITION_NO_APPLIED_MISMATCH",
            ),
            (artifact_without_edit, "CLOSURE_EDIT_ARTIFACT_UNEXPECTED"),
        ]
        for mutate, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                state = json.loads(json.dumps(valid_state))
                mutate(state)
                write_json(audit / writer_audit.STATE_NAME, state)
                result, code = self.check(audit)
                self.assertEqual(code, 1)
                self.assertIn(expected_code, issue_codes(result))

        write_json(audit / writer_audit.STATE_NAME, valid_state)
        result, code = self.check(audit)
        self.assertEqual(code, 0, result)

    def test_blocking_disposition_allows_each_documented_outcome(self) -> None:
        audit = self.base / "blocking dispositions"
        self.initialize(audit, action="audit-and-revise")
        self.complete_diagnosis(
            audit,
            [self.finding("F-001", "Blocking")],
        )
        result, code = self.freeze(audit)
        self.assertEqual(code, 0, result)
        self.finish_revision(audit, applied=False)
        state = read_json(audit / writer_audit.STATE_NAME)
        for outcome in ("unresolved", "unapplied"):
            with self.subTest(outcome=outcome):
                candidate = json.loads(json.dumps(state))
                candidate["closure"]["edits"]["finding_dispositions"][0][
                    "outcome"
                ] = outcome
                candidate["closure"]["edits"]["finding_dispositions"][0][
                    "reason"
                ] = f"The finding requiring author input remains {outcome}."
                write_json(audit / writer_audit.STATE_NAME, candidate)
                result, code = self.check(audit)
                self.assertEqual(code, 0, result)

        self.finish_revision(audit, applied=True)
        state = read_json(audit / writer_audit.STATE_NAME)
        state["closure"]["edits"]["finding_dispositions"][0] = {
            "finding_id": "F-001",
            "outcome": "applied",
            "reason": "The bound revision addressed the finding requiring author input.",
        }
        write_json(audit / writer_audit.STATE_NAME, state)
        result, code = self.check(audit)
        self.assertEqual(code, 0, result)

    def test_revision_requires_baseline_then_post_edit_phases(self) -> None:
        audit = self.base / "revision phases"
        self.initialize(audit, action="audit-and-revise")
        self.complete_diagnosis(
            audit,
            [self.finding("F-001", "Local")],
        )
        state = read_json(audit / writer_audit.STATE_NAME)
        baseline_compile = json.loads(json.dumps(state["closure"]["compile"]))
        baseline_render = json.loads(json.dumps(state["closure"]["render"]))
        state["closure"]["compile"]["phase"] = "post_edit"
        write_json(audit / writer_audit.STATE_NAME, state)
        result, code = self.freeze(audit)
        self.assertEqual(code, 1)
        self.assertIn("CLOSURE_PHASE_MISMATCH", issue_codes(result))

        state["closure"]["compile"]["phase"] = "baseline"
        write_json(audit / writer_audit.STATE_NAME, state)
        result, code = self.freeze(audit)
        self.assertEqual(code, 0, result)
        frozen_state = read_json(audit / writer_audit.STATE_NAME)
        drifted = json.loads(json.dumps(frozen_state))
        drifted["closure"]["compile"][
            "evidence"
        ] = "Changed baseline evidence after diagnosis freeze."
        write_json(audit / writer_audit.STATE_NAME, drifted)
        result, code = self.status(audit)
        self.assertEqual(code, 1)
        self.assertIn("FREEZE_BASELINE_DRIFT", issue_codes(result))
        write_json(audit / writer_audit.STATE_NAME, frozen_state)

        self.finish_revision(audit, applied=True)
        post_edit_state = read_json(audit / writer_audit.STATE_NAME)
        invalid = json.loads(json.dumps(post_edit_state))
        invalid["closure"]["compile"] = baseline_compile
        invalid["closure"]["render"] = baseline_render
        write_json(audit / writer_audit.STATE_NAME, invalid)
        result, code = self.check(audit)
        self.assertEqual(code, 1)
        self.assertIn("CLOSURE_PHASE_MISMATCH", issue_codes(result))

        write_json(audit / writer_audit.STATE_NAME, post_edit_state)
        result, code = self.check(audit)
        self.assertEqual(code, 0, result)

    def test_audit_only_rejects_revision_dispositions(self) -> None:
        self.complete_diagnosis(findings_records=[self.finding("F-001", "Local")])
        state = read_json(self.audit / writer_audit.STATE_NAME)
        state["closure"]["edits"]["finding_dispositions"] = [
            {
                "finding_id": "F-001",
                "outcome": "unapplied",
                "reason": "Audit-only work did not authorize revision.",
            }
        ]
        write_json(self.audit / writer_audit.STATE_NAME, state)
        result, code = self.check()
        self.assertEqual(code, 1)
        self.assertIn("CLOSURE_AUDIT_ONLY_DISPOSITIONS", issue_codes(result))

    def test_revision_progress_before_freeze_fails_closed(self) -> None:
        audit = self.base / "unfrozen revision"
        self.initialize(audit, action="audit-and-revise")
        self.complete_diagnosis(audit)
        self.finish_revision(audit, applied=False)
        result, code = self.status(audit)
        self.assertEqual(code, 1)
        self.assertIn("FREEZE_REQUIRED", issue_codes(result))

    def test_freeze_is_idempotent_and_detects_drift(self) -> None:
        audit = self.base / "frozen revision"
        self.initialize(audit, action="audit-and-revise")
        self.complete_diagnosis(audit)
        first, code = self.freeze(audit)
        self.assertEqual(code, 0, first)
        second, code = self.freeze(audit)
        self.assertEqual(code, 0, second)
        self.assertEqual(second["method"], "existing_identical")
        findings = read_json(audit / writer_audit.FINDINGS_NAME)
        findings["assessment"]["boundary"] = "A changed but otherwise valid boundary."
        write_json(audit / writer_audit.FINDINGS_NAME, findings)
        result, code = self.status(audit)
        self.assertEqual(code, 1)
        self.assertIn("FREEZE_MISMATCH", issue_codes(result))

    def test_frozen_revision_preserves_baseline_and_binds_finalization(self) -> None:
        audit = self.base / "completed revision"
        self.initialize(audit, action="audit-and-revise")
        self.complete_diagnosis(
            audit,
            [self.finding("F-001", "Local")],
        )
        result, code = self.freeze(audit)
        self.assertEqual(code, 0, result)
        freeze_before = read_json(audit / writer_audit.DIAGNOSIS_FREEZE_NAME)
        self.finish_revision(audit, applied=True)
        state = read_json(audit / writer_audit.STATE_NAME)
        state["closure"]["compile"] = {
            "phase": "post_edit",
            "status": "not_run",
            "evidence": "Post-edit compiler remained unavailable.",
            "artifact": None,
        }
        write_json(audit / writer_audit.STATE_NAME, state)
        result, code = self.check(audit, publish=True)
        self.assertEqual(code, 0, result)
        self.assertTrue(result["final"])
        freeze_after = read_json(audit / writer_audit.DIAGNOSIS_FREEZE_NAME)
        self.assertEqual(freeze_before, freeze_after)
        receipt = read_json(audit / writer_audit.FINALIZATION_NAME)
        self.assertEqual(
            receipt["diagnosis_freeze_sha256"],
            writer_audit.sha256_file(audit / writer_audit.DIAGNOSIS_FREEZE_NAME),
        )

    def test_audit_only_cannot_freeze(self) -> None:
        self.complete_diagnosis()
        result, code = self.freeze()
        self.assertEqual(code, 1)
        self.assertIn("FREEZE_ACTION", issue_codes(result))

    def test_publication_is_deterministic_and_idempotent(self) -> None:
        self.complete_diagnosis()
        first, code = self.check(publish=True)
        self.assertEqual(code, 0, first)
        report = (self.audit / writer_audit.REPORT_NAME).read_bytes()
        second, code = self.check(publish=True)
        self.assertEqual(code, 0, second)
        self.assertEqual(second["published"]["report"], "existing_identical")
        self.assertEqual((self.audit / writer_audit.REPORT_NAME).read_bytes(), report)
        status, code = self.status()
        self.assertEqual(code, 0, status)
        self.assertTrue(status["final"])

    def test_pending_state_cannot_use_a_fabricated_matching_receipt(self) -> None:
        self.complete_diagnosis()
        state = read_json(self.audit / writer_audit.STATE_NAME)
        state["passes"][0].update(
            status="pending", loaded_references=[], checkpoint=None, reason=None
        )
        write_json(self.audit / writer_audit.STATE_NAME, state)
        manifest = read_json(self.audit / writer_audit.MANIFEST_NAME)
        findings = read_json(self.audit / writer_audit.FINDINGS_NAME)
        report = writer_audit.render_report(manifest, state, findings)
        (self.audit / writer_audit.REPORT_NAME).write_bytes(report)
        write_json(
            self.audit / writer_audit.FINALIZATION_NAME,
            writer_audit.finalization_record(self.audit, manifest, report),
        )
        result, code = self.status()
        self.assertEqual(code, 1)
        self.assertFalse(result["final"])
        self.assertIn("STATE_PASS_PENDING", issue_codes(result))

    def test_publication_preflights_conflicting_receipt(self) -> None:
        self.complete_diagnosis()
        receipt = self.audit / writer_audit.FINALIZATION_NAME
        receipt.write_text("{}\n", encoding="utf-8")
        result, code = self.check(publish=True)
        self.assertEqual(code, 1)
        self.assertIn("PUBLICATION_CONFLICT", issue_codes(result))
        self.assertFalse((self.audit / writer_audit.REPORT_NAME).exists())
        self.assertEqual(receipt.read_text(encoding="utf-8"), "{}\n")

    def test_interrupted_identical_report_can_resume_publication(self) -> None:
        self.complete_diagnosis()
        manifest = read_json(self.audit / writer_audit.MANIFEST_NAME)
        state = read_json(self.audit / writer_audit.STATE_NAME)
        findings = read_json(self.audit / writer_audit.FINDINGS_NAME)
        report = writer_audit.render_report(manifest, state, findings)
        (self.audit / writer_audit.REPORT_NAME).write_bytes(report)
        result, code = self.check(publish=True)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["published"]["report"], "existing_identical")
        self.assertTrue((self.audit / writer_audit.FINALIZATION_NAME).is_file())

    def test_status_distinguishes_identical_and_conflicting_orphan_reports(self) -> None:
        self.complete_diagnosis()
        manifest = read_json(self.audit / writer_audit.MANIFEST_NAME)
        state = read_json(self.audit / writer_audit.STATE_NAME)
        findings = read_json(self.audit / writer_audit.FINDINGS_NAME)
        report_path = self.audit / writer_audit.REPORT_NAME
        report_path.write_bytes(writer_audit.render_report(manifest, state, findings))

        result, code = self.status()
        self.assertEqual(code, 0, result)
        self.assertTrue(result["workspace_valid"])
        self.assertFalse(result["final"])
        self.assertNotIn("FINAL_REPORT_CONFLICT", issue_codes(result))

        report_path.write_bytes(report_path.read_bytes() + b"conflicting bytes\n")
        result, code = self.status()
        self.assertEqual(code, 1)
        self.assertFalse(result["final"])
        self.assertIn("FINAL_REPORT_CONFLICT", issue_codes(result))

    def test_post_finalization_state_findings_and_report_drift(self) -> None:
        mutations = ["state", "findings", "report"]
        for index, kind in enumerate(mutations, start=1):
            with self.subTest(kind=kind):
                audit = self.base / f"final-drift-{index}"
                self.initialize(audit)
                self.complete_diagnosis(audit)
                result, code = self.check(audit, publish=True)
                self.assertEqual(code, 0, result)
                if kind == "state":
                    state = read_json(audit / writer_audit.STATE_NAME)
                    state["passes"][0]["checkpoint"] = "Changed checkpoint text."
                    write_json(audit / writer_audit.STATE_NAME, state)
                elif kind == "findings":
                    findings = read_json(audit / writer_audit.FINDINGS_NAME)
                    findings["assessment"]["boundary"] = "Changed valid boundary."
                    write_json(audit / writer_audit.FINDINGS_NAME, findings)
                else:
                    with (audit / writer_audit.REPORT_NAME).open(
                        "ab"
                    ) as handle:
                        handle.write(b"changed\n")
                status, code = self.status(audit)
                self.assertEqual(code, 1)
                self.assertFalse(status["final"])
                self.assertTrue(status["errors"])


if __name__ == "__main__":
    unittest.main()
