from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "proofcheck.py"
SPEC = importlib.util.spec_from_file_location("proofcheck_compiler", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT}")
proofcheck = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proofcheck)


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalization_checks() -> list[dict[str, str]]:
    rows = {
        "quantifiers_and_domains": (
            "checked",
            "The universal real-number quantifier is explicit in the locked statement.",
        ),
        "probability_model": (
            "not_applicable",
            "The locked equality contains no random object or probability statement.",
        ),
        "hypotheses": (
            "not_applicable",
            "The theorem has no hypotheses beyond the quantified real-number domain.",
        ),
        "definitions": (
            "checked",
            "Equality has its ordinary meaning on the real numbers.",
        ),
        "conclusion": (
            "checked",
            "The normalized conclusion is exactly the displayed equality x equals x.",
        ),
        "uniformity": (
            "not_applicable",
            "The locked claim contains no indexed bound or convergence statement.",
        ),
        "regime": (
            "not_applicable",
            "The locked claim is neither finite-sample nor asymptotic.",
        ),
        "constant_dependencies": (
            "not_applicable",
            "No named or hidden constant occurs in the locked equality.",
        ),
    }
    return [
        {"aspect": aspect, "status": status, "evidence": evidence}
        for aspect, (status, evidence) in rows.items()
    ]


def risks(prefix: str) -> dict[str, dict[str, str]]:
    statuses = {
        "domain": "passed",
        "dimension": "not_applicable",
        "sign": "not_applicable",
        "constant": "not_applicable",
        "rate": "not_applicable",
        "probability": "not_applicable",
        "quantifier": "passed",
        "limit": "not_applicable",
    }
    descriptions = {
        "domain": "the current x remains in the real-number domain",
        "dimension": "the scalar equality has no dimension-sensitive operation",
        "sign": "the equality uses no order or sign argument",
        "constant": "the move introduces no explicit or hidden constant",
        "rate": "the move states no stochastic or asymptotic rate",
        "probability": "the move contains no event, measure, or conditioning",
        "quantifier": "the move retains the arbitrary real x fixed by the statement",
        "limit": "the move performs no limiting or exchange operation",
    }
    return {
        aspect: {
            "status": statuses[aspect],
            "evidence": f"{prefix}: {descriptions[aspect]}.",
        }
        for aspect in proofcheck.RISK_ASPECTS
    }


class CompileAnnotationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name) / "workspace with spaces" / "理论"
        self.base.mkdir(parents=True)
        self.paper = self.base / "paper source.tex"
        self.paper.write_text(
            "\\begin{lemma}\\label{lem:compact}\n"
            "For every real $x$, $x=x$.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\n"
            "For the object in \\ref{lem:compact}, reflexivity gives $x=x$.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        self.audit = self.base / "canonical audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(paper=self.paper, output=self.audit)
            )
        self.ledger = (
            self.audit
            / "audit"
            / "04_local_checks"
            / "unit.skeleton.json"
        )
        self.output = self.ledger.with_name("unit.ledger.json")
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=self.paper,
                    start=1,
                    end=6,
                    statement_file=self.paper,
                    statement_start=1,
                    statement_end=3,
                    separate_statement_reason=None,
                    unit_id="lem:compact",
                    output=self.ledger,
                    force=False,
                )
            )
        ledger = read_json(self.ledger)
        statement_span = ledger["obligation"]["statement_spans"][0]
        ledger["obligation"] = {
            "statement_spans": [statement_span],
            "quantified_variables": [
                {
                    "symbol": "x",
                    "type": "real number",
                    "domain": "R",
                    "quantifier": "forall",
                }
            ],
            "quantifier_scope": "For every real x.",
            "probability_model": "not applicable",
            "hypotheses": ["none"],
            "definitions": ["equality on the real numbers"],
            "conclusion": "x equals x",
            "conclusions": [
                {
                    "id": "C001",
                    "claim": "x equals x",
                    "source_spans": [dict(statement_span)],
                    "applies_under": ["/quantifier_scope"],
                    "normalization": {
                        "status": "checked",
                        "evidence": (
                            "The statement gives exactly x equals x for every real x."
                        ),
                    },
                }
            ],
            "uniformity": "not_applicable",
            "regime": "not_applicable",
            "constant_dependencies": ["none"],
            "context_spans": [],
            "normalization_checks": normalization_checks(),
        }
        write_json(self.ledger, ledger)
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["status"] = "reviewed"
        manifest["audit_scope"]["target_units"] = ["lem:compact"]
        manifest["audit_scope"]["in_scope_units"] = ["lem:compact"]
        manifest["audit_scope"]["critical_units"] = []
        write_json(manifest_path, manifest)
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["review"] = {
            "status": "reviewed",
            "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
            "inventory_sha256": proofcheck.sha256_file(inventory_path),
            "in_scope_units": ["lem:compact"],
            "evidence": [
                "The compact fixture has no direct result dependency."
            ],
        }
        write_json(registry_path, registry)
        self.packet = self.base / "primary packet.json"
        self.regenerate_packet()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def regenerate_packet(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_packet(
                argparse.Namespace(
                    root=self.audit,
                    unit_id="lem:compact",
                    mode="primary",
                    output=self.packet,
                    force=self.packet.exists(),
                )
            )

    def annotations(self) -> dict:
        ledger = read_json(self.ledger)
        packet = read_json(self.packet)
        occurrence = packet["inventory"]["reference_occurrences"][0]
        annotations = {
            "annotation_schema_version": 1,
            "unit_id": "lem:compact",
            "source_unit_sha256": ledger["source"]["unit_sha256"],
            "obligation_sha256": proofcheck.canonical_sha256(
                ledger["obligation"]
            ),
            "context_binding_sha256": read_json(self.packet)[
                "context_binding_sha256"
            ],
            "source_groups": [
                {
                    "lines": [1, 3],
                    "kind": "continued_sentence",
                    "partition_evidence": (
                        "Lines 1-3 are the single locked formal statement environment."
                    ),
                }
            ],
            "dependencies": [],
            "steps": [
                {
                    "key": "statement",
                    "lines": [1, 3],
                    "mode": "noninferential",
                    "kind": "statement",
                    "goal": "Identify the exact theorem obligation.",
                    "claim": "For every real x, x equals x.",
                    "literal": (
                        "The locked statement quantifies over every real x and states x equals x."
                    ),
                    "atomicity_evidence": (
                        "This row records the statement and performs no inference."
                    ),
                    "adversarial": [
                        "The normalized statement retains the same domain and quantifier."
                    ],
                    "risks": risks("statement"),
                    "inputs": [],
                    "side_conditions": [],
                    "status": "verified",
                    "issue_ids": [],
                },
                {
                    "key": "conclusion",
                    "lines": [5, 5],
                    "mode": "derivation",
                    "kind": "conclusion",
                    "goal": "Establish x equals x for the arbitrary real x.",
                    "claim": "x equals x",
                    "literal": (
                        "Locked line 5 explicitly invokes reflexivity to obtain x equals x."
                    ),
                    "atomicity_evidence": (
                        "The line contains one application of reflexivity."
                    ),
                    "adversarial": [
                        "No real-number boundary case violates reflexivity of equality."
                    ],
                    "risks": risks("conclusion"),
                    "inputs": [
                        {
                            "kind": "obligation",
                            "reference": "/quantifier_scope",
                            "role": "fact",
                            "evidence": (
                                "The locked statement fixes an arbitrary real x."
                            ),
                            "anchor": {"kind": "statement_span", "index": 1},
                            "source_reference_id": occurrence["target"],
                            "source_reference_occurrence_id": occurrence[
                                "occurrence_id"
                            ],
                        }
                    ],
                    "side_conditions": [],
                    "status": "verified",
                    "issue_ids": [],
                    "rule": "Reflexivity of equality",
                    "justification": (
                        "Reflexivity gives x equals x for the arbitrary real x."
                    ),
                },
            ],
            "conclusions": [
                {
                    "conclusion_id": "C001",
                    "support_step": "conclusion",
                    "contract_fidelity": "verified",
                    "statement_status": "established",
                    "use_site_sufficiency": "not_applicable",
                    "issue_ids": [],
                }
            ],
            "review": {
                "explicit_assumptions": [],
                "inherited_assumptions": [],
                "source_reference_dispositions": [],
                "candidate_dependency_dispositions": [],
                "citation_dispositions": [],
                "verification_basis": [
                    "Exact locked source and authored atomic semantic annotations."
                ],
                "reviewer_notes": [],
            },
        }
        annotations["review"]["source_reference_dispositions"] = [
            {
                "occurrence_id": occurrence["occurrence_id"],
                "target": occurrence["target"],
                "command": occurrence["command"],
                "disposition": "obligation_context",
                "evidence": (
                    "The proof reference identifies this lemma's locked "
                    "statement and quantified domain."
                ),
            }
        ]
        return annotations

    def matching_skeleton(self, output: Path) -> Path:
        self.assertEqual(self.output, output)
        return self.ledger

    def compile(self, annotations: dict, output: Path, *, force: bool = False) -> dict:
        annotation_path = self.base / "semantic.annotations.json"
        write_json(annotation_path, annotations)
        skeleton = self.matching_skeleton(output)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            status = proofcheck.cmd_compile_annotations(
                argparse.Namespace(
                    ledger=skeleton,
                    annotations=annotation_path,
                    packet=self.packet,
                    output=output,
                    force=force,
                )
            )
        self.assertEqual(0, status)
        return json.loads(stdout.getvalue())

    def test_compiles_valid_schema5_ledger_with_mechanical_coverage(self) -> None:
        output = self.output

        summary = self.compile(self.annotations(), output)

        self.assertEqual("passed", summary["validation"])
        self.assertEqual(
            self.annotations()["obligation_sha256"],
            summary["obligation_sha256"],
        )
        compiled = read_json(output)
        errors, validation = proofcheck.check_ledger_data(output, True)
        self.assertEqual([], errors)
        self.assertEqual("verified", validation["declared_unit_status"])
        self.assertNotIn("annotation_schema_version", compiled)
        self.assertEqual(
            [
                ("U001", [1, 3], "continued_sentence"),
                ("U002", [4, 4], "non_substantive"),
                ("U003", [5, 5], "one_line"),
                ("U004", [6, 6], "non_substantive"),
            ],
            [
                (row["id"], row["lines"], row["kind"])
                for row in compiled["source_units"]
            ],
        )
        self.assertEqual(
            ["S001", "S002", "S003", "S004"],
            [row["id"] for row in compiled["steps"]],
        )
        conclusion = compiled["steps"][2]
        self.assertEqual(
            "For every real x.", conclusion["premise_uses"][0]["claim"]
        )
        self.assertEqual(
            list(proofcheck.RISK_ASPECTS),
            [row["aspect"] for row in conclusion["risk_checks"]],
        )

    def test_cli_is_registered_and_output_is_deterministic(self) -> None:
        annotations = self.annotations()
        annotation_path = self.base / "semantic.annotations.json"
        write_json(annotation_path, annotations)
        output = self.output
        parser = proofcheck.build_parser()
        rendered: list[bytes] = []
        for _ in range(2):
            skeleton = self.matching_skeleton(output)
            args = parser.parse_args(
                [
                    "compile-annotations",
                    str(skeleton),
                    "--annotations",
                    str(annotation_path),
                    "--packet",
                    str(self.packet),
                    "--output",
                    str(output),
                ]
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, args.func(args))
            rendered.append(output.read_bytes())
            output.unlink()

        self.assertEqual(rendered[0], rendered[1])
        text = rendered[0].decode("utf-8")
        self.assertNotIn(str(annotation_path), text)

    def test_invalid_annotation_never_replaces_existing_output(self) -> None:
        annotations = self.annotations()
        annotations["source_unit_sha256"] = "0" * 64
        annotation_path = self.base / "bad.annotations.json"
        write_json(annotation_path, annotations)
        output = self.output
        skeleton = self.matching_skeleton(output)
        original = b"existing output must survive\n"
        output.write_bytes(original)

        with self.assertRaisesRegex(FileExistsError, "cannot be overwritten"):
            proofcheck.cmd_compile_annotations(
                argparse.Namespace(
                    ledger=skeleton,
                    annotations=annotation_path,
                    packet=self.packet,
                    output=output,
                    force=True,
                )
            )

        self.assertEqual(original, output.read_bytes())
        self.assertEqual([], list(self.base.glob(".*.proofcheck.tmp")))

    def test_concurrent_output_creation_is_never_overwritten(self) -> None:
        annotation_path = self.base / "semantic.annotations.json"
        write_json(annotation_path, self.annotations())
        output = self.output
        concurrent = b"concurrent creator owns this output\n"
        real_link = os.link

        def create_then_link(source: str | Path, destination: str | Path) -> None:
            Path(destination).write_bytes(concurrent)
            real_link(source, destination)

        with mock.patch.object(
            proofcheck.os, "link", side_effect=create_then_link
        ):
            with self.assertRaisesRegex(
                FileExistsError, "appeared during validation"
            ):
                proofcheck.cmd_compile_annotations(
                    argparse.Namespace(
                        ledger=self.ledger,
                        annotations=annotation_path,
                        packet=self.packet,
                        output=output,
                        force=False,
                    )
                )

        self.assertEqual(concurrent, output.read_bytes())
        self.assertEqual([], list(self.base.glob(".*.proofcheck.tmp")))

    def test_compact_schema_rejects_missing_semantics_and_unknown_fields(self) -> None:
        cases: list[tuple[str, dict, str]] = []
        missing_risk = self.annotations()
        del missing_risk["steps"][1]["risks"]["limit"]
        cases.append(("missing-risk", missing_risk, "missing fields: limit"))
        missing_rule = self.annotations()
        del missing_rule["steps"][1]["rule"]
        cases.append(("missing-rule", missing_rule, "rule must be authored"))
        unknown_field = self.annotations()
        unknown_field["steps"][1]["verdict_note"] = "A misspelled field."
        cases.append(("unknown-field", unknown_field, "unknown fields: verdict_note"))

        for name, annotations, message in cases:
            with self.subTest(case=name):
                annotation_path = self.base / f"{name}.annotations.json"
                output = self.output
                skeleton = self.matching_skeleton(output)
                write_json(annotation_path, annotations)
                with self.assertRaisesRegex(ValueError, message):
                    proofcheck.cmd_compile_annotations(
                        argparse.Namespace(
                            ledger=skeleton,
                            annotations=annotation_path,
                            packet=self.packet,
                            output=output,
                            force=False,
                        )
                    )
                self.assertFalse(output.exists())

    def test_completed_ledger_cannot_be_recompiled_as_a_fresh_skeleton(self) -> None:
        compiled = self.output
        self.compile(self.annotations(), compiled)
        completed_skeleton = self.base / "completed.skeleton.json"
        completed_skeleton.write_bytes(compiled.read_bytes())

        with self.assertRaisesRegex(ValueError, "fresh extracted skeleton"):
            proofcheck.validate_compile_skeleton(
                read_json(completed_skeleton), completed_skeleton
            )

    def test_compiler_never_overwrites_the_extracted_skeleton(self) -> None:
        annotation_path = self.base / "semantic.annotations.json"
        write_json(annotation_path, self.annotations())
        original = self.ledger.read_bytes()

        with self.assertRaisesRegex(ValueError, "Compiled output must end"):
            proofcheck.cmd_compile_annotations(
                argparse.Namespace(
                    ledger=self.ledger,
                    annotations=annotation_path,
                    packet=self.packet,
                    output=self.ledger,
                    force=True,
                )
            )

        self.assertEqual(original, self.ledger.read_bytes())

    def test_compiler_rejects_stale_obligation_binding(self) -> None:
        annotations = self.annotations()
        ledger = read_json(self.ledger)
        ledger["obligation"]["quantifier_scope"] = "For every complex x."
        write_json(self.ledger, ledger)
        annotation_path = self.base / "semantic.annotations.json"
        write_json(annotation_path, annotations)
        output = self.output

        with self.assertRaisesRegex(ValueError, "obligation_sha256"):
            proofcheck.cmd_compile_annotations(
                argparse.Namespace(
                    ledger=self.ledger,
                    annotations=annotation_path,
                    packet=self.packet,
                    output=output,
                    force=False,
                )
            )

        self.assertFalse(output.exists())

    def test_compiler_rejects_mismatched_output_basename(self) -> None:
        annotation_path = self.base / "semantic.annotations.json"
        write_json(annotation_path, self.annotations())
        output = self.output.parent / "different.ledger.json"

        with self.assertRaisesRegex(ValueError, "output basename"):
            proofcheck.cmd_compile_annotations(
                argparse.Namespace(
                    ledger=self.ledger,
                    annotations=annotation_path,
                    packet=self.packet,
                    output=output,
                    force=False,
                )
            )

        self.assertFalse(output.exists())

    def test_compiler_summary_is_ascii_console_safe(self) -> None:
        annotation_path = self.base / "semantic.annotations.json"
        write_json(annotation_path, self.annotations())
        output = self.output
        raw = io.BytesIO()
        stream = io.TextIOWrapper(raw, encoding="ascii", errors="strict")
        try:
            with contextlib.redirect_stdout(stream):
                status = proofcheck.cmd_compile_annotations(
                    argparse.Namespace(
                        ledger=self.ledger,
                        annotations=annotation_path,
                        packet=self.packet,
                        output=output,
                        force=False,
                    )
                )
            stream.flush()
            rendered = raw.getvalue().decode("ascii")
        finally:
            stream.detach()

        self.assertEqual(0, status)
        self.assertEqual("compile-annotations", json.loads(rendered)["command"])
        self.assertTrue(output.is_file())

    def install_external_dependency(self, status: str) -> None:
        source_path = self.base / "external reflexivity.txt"
        source_path.write_text(
            "External Result 1\nEquality is reflexive on the real numbers.\n",
            encoding="utf-8",
            newline="\n",
        )
        exact_statement = "Equality is reflexive on the real numbers."
        source_evidence = [
            {
                "file": proofcheck.relative_or_absolute(
                    source_path, self.audit
                ),
                "sha256": proofcheck.sha256_file(source_path),
                "locator": "External Result 1, line 2",
                "role": "authoritative_theorem_source",
            }
        ]
        contract_payload = {
            "source_identity": "doi:10.0000/reflexivity",
            "version": "version 1",
            "theorem_location": "External Result 1",
            "exact_statement": exact_statement,
            "source_evidence": source_evidence,
        }
        needed_form = "Equality is reflexive on the real numbers."
        compatibility = (
            "The external fact applies to the current real x without a "
            "domain change."
        )
        use = {
            "dependent_unit": "lem:compact",
            "use_id": "D001",
            "dependency_id": "ext:reflexivity",
            "step_ids": ["S003.1"],
            "needed_form": needed_form,
            "dependency_conclusion": exact_statement,
            "dependency_contract_sha256": proofcheck.canonical_sha256(
                contract_payload
            ),
            "compatibility_check": compatibility,
            "compatibility_checks": [
                {
                    "aspect": aspect,
                    "status": "passed",
                    "evidence": (
                        f"The external result is compatible on {aspect}."
                    ),
                    "issue_ids": [],
                }
                for aspect in proofcheck.NORMALIZATION_ASPECTS
            ],
            "status": status,
            "issue_ids": [],
            "citation_keys": [],
            "prerequisite_map": [
                {
                    "prerequisite": "The current object x is real.",
                    "manuscript_evidence": (
                        "The locked statement quantifies x over the real numbers."
                    ),
                    "status": "satisfied",
                    "evidence_spans": [
                        proofcheck.locked_span(
                            self.paper,
                            1,
                            3,
                            self.audit,
                            role="manuscript_prerequisite",
                        )
                    ],
                    "issue_ids": [],
                }
            ],
        }
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["external_results"] = [
            {
                "id": "ext:reflexivity",
                "status": "verified",
                **contract_payload,
                "issue_ids": [],
                "uses": [use],
            }
        ]
        write_json(registry_path, registry)
        self.regenerate_packet()

    def dependency_annotations(self, status: str = "verified") -> dict:
        self.install_external_dependency(status)
        annotations = self.annotations()
        source_disposition = annotations["review"][
            "source_reference_dispositions"
        ][0]
        annotations["dependencies"] = [
            {
                "id": "ext:reflexivity",
                "use_id": "D001",
                "kind": "external_result",
                "status": status,
                "needed_form": "Equality is reflexive on the real numbers.",
                "compatibility_check": (
                    "The external fact applies to the current real x without a domain change."
                ),
            }
        ]
        annotations["steps"] = [
            annotations["steps"][0],
            {
                "key": "domain",
                "lines": [5, 5],
                "mode": "derivation",
                "kind": "setup",
                "goal": "Record the domain of the arbitrary element.",
                "claim": "x is a real number.",
                "literal": "Locked line 5 identifies x as real before using reflexivity.",
                "atomicity_evidence": (
                    "This annotation isolates only the domain specialization."
                ),
                "adversarial": [
                    "The specialization does not change the universal scope of x."
                ],
                "risks": risks("domain step"),
                "inputs": [
                    {
                        "kind": "obligation",
                        "reference": "/quantifier_scope",
                        "role": "fact",
                        "evidence": "The statement fixes x as an arbitrary real number.",
                        "anchor": {"kind": "statement_span", "index": 1},
                        "source_reference_id": source_disposition["target"],
                        "source_reference_occurrence_id": source_disposition[
                            "occurrence_id"
                        ],
                    }
                ],
                "side_conditions": [],
                "status": "verified",
                "issue_ids": [],
                "rule": "Universal specialization",
                "justification": (
                    "Specializing the universal statement records that the current x is real."
                ),
            },
            {
                "key": "conclusion",
                "lines": [5, 5],
                "mode": "derivation",
                "kind": "conclusion",
                "goal": "Apply reflexivity to the current real x.",
                "claim": "x equals x",
                "literal": "Locked line 5 concludes x equals x by reflexivity.",
                "atomicity_evidence": (
                    "This annotation isolates the single reflexivity move."
                ),
                "adversarial": [
                    "The imported reflexivity fact is used only on its real-number domain."
                ],
                "risks": risks("dependency conclusion"),
                "inputs": [
                    {
                        "kind": "prior_step",
                        "reference": "domain",
                        "role": "fact",
                        "evidence": "The immediately prior atomic step establishes x is real.",
                        "compatibility_check": (
                            "The prior domain claim is used without strengthening."
                        ),
                    },
                    {
                        "kind": "dependency",
                        "reference": "D001",
                        "role": "fact",
                        "evidence": (
                            "The checked external dependency supplies reflexivity on the real numbers."
                        ),
                    },
                ],
                "side_conditions": [],
                "status": "verified",
                "issue_ids": [],
                "rule": "Apply reflexivity on the recorded domain",
                "justification": (
                    "The current x is real and the external dependency gives reflexivity there."
                ),
            },
        ]
        return annotations

    def test_same_source_unit_steps_get_stable_ids_and_exact_dependency_closure(
        self,
    ) -> None:
        output = self.output

        self.compile(self.dependency_annotations(), output)

        compiled = read_json(output)
        errors, _ = proofcheck.check_ledger_data(output, True)
        self.assertEqual([], errors)
        self.assertEqual(
            ["S001", "S002", "S003", "S003.1", "S004"],
            [row["id"] for row in compiled["steps"]],
        )
        conclusion = next(row for row in compiled["steps"] if row["id"] == "S003.1")
        self.assertEqual(
            ["S003", "D001"],
            [
                row["id"] if row["kind"] == "step" else row["use_id"]
                for row in conclusion["dependencies"]
            ],
        )
        self.assertEqual(
            compiled["review"]["direct_dependencies"][0],
            conclusion["dependencies"][1],
        )
        result = compiled["review"]["conclusion_results"][0]
        self.assertEqual({"step_id": "S003.1", "move_id": "M001"}, result["support"])
        self.assertEqual(["D001"], result["dependency_use_ids"])
        self.assertEqual("verified", result["dependency_closure"])

    def test_conditional_causes_are_derived_without_reauthoring_mirrors(self) -> None:
        annotations = self.dependency_annotations("conditional")
        conclusion = annotations["steps"][2]
        conclusion["status"] = "conditionally_verified"
        conclusion["risks"]["domain"] = {
            "status": "open",
            "evidence": (
                "The application remains conditional on the external result covering the current domain."
            ),
        }
        conclusion["side_conditions"] = [
            {
                "condition": "The external reflexivity statement covers the current presentation of x.",
                "status": "open",
            }
        ]
        annotations["conclusions"][0]["statement_status"] = "conditional"
        output = self.output

        self.compile(annotations, output)

        compiled = read_json(output)
        errors, _ = proofcheck.check_ledger_data(output, True)
        self.assertEqual([], errors)
        final_step = next(row for row in compiled["steps"] if row["id"] == "S003.1")
        self.assertEqual(
            [
                ("side_condition", "SC001"),
                ("dependency", "D001"),
                ("risk_check", "domain"),
            ],
            [(row["kind"], row["reference"]) for row in final_step["conditions"]],
        )
        result = compiled["review"]["conclusion_results"][0]
        self.assertEqual("conditionally_verified", result["dependency_closure"])
        self.assertEqual("conditional", result["argument_status"])
        self.assertEqual("conditionally_verified", compiled["review"]["unit_status"])

    def test_authored_zero_input_failure_is_preserved_and_propagated(self) -> None:
        annotations = self.annotations()
        conclusion = annotations["steps"][1]
        conclusion["inputs"] = []
        conclusion["status"] = "gap"
        conclusion["issue_ids"] = ["I-001"]
        conclusion["failure"] = {
            "kind": "missing_premise",
            "issue_id": "I-001",
            "evidence": (
                "The source invokes reflexivity without establishing that its object lies in the required domain."
            ),
        }
        annotations["conclusions"][0]["statement_status"] = "not_established"
        annotations["conclusions"][0]["issue_ids"] = []
        annotations["review"]["source_reference_dispositions"][0][
            "disposition"
        ] = "unresolved"
        annotations["review"]["source_reference_dispositions"][0][
            "evidence"
        ] = (
            "The failed zero-input audit leaves the source reference "
            "unresolved instead of treating it as an established premise."
        )
        output = self.output

        self.compile(annotations, output)

        compiled = read_json(output)
        errors, _ = proofcheck.check_ledger_data(output, True)
        self.assertEqual([], errors)
        move = compiled["steps"][2]["inference"]["moves"][0]
        self.assertEqual(conclusion["failure"], move["failure"])
        result = compiled["review"]["conclusion_results"][0]
        self.assertEqual(["I-001"], result["issue_ids"])
        self.assertEqual("gap", compiled["review"]["unit_status"])

    def test_source_occurrence_links_are_mirrored_to_generated_premise_ids(
        self,
    ) -> None:
        annotations = self.annotations()
        occurrence = proofcheck.scan_span_evidence(
            self.paper, 1, 6, self.base
        )["reference_occurrences"][0]
        premise = annotations["steps"][1]["inputs"][0]
        premise["source_reference_id"] = occurrence["target"]
        premise["source_reference_occurrence_id"] = occurrence["occurrence_id"]
        annotations["review"]["source_reference_dispositions"] = [
            {
                "occurrence_id": occurrence["occurrence_id"],
                "target": occurrence["target"],
                "command": occurrence["command"],
                "disposition": "obligation_context",
                "evidence": (
                    "The occurrence identifies the locked theorem context supplying the quantified domain."
                ),
            }
        ]
        output = self.output

        self.compile(annotations, output)

        compiled = read_json(output)
        errors, _ = proofcheck.check_ledger_data(output, True)
        self.assertEqual([], errors)
        disposition = compiled["review"]["source_reference_dispositions"][0]
        self.assertEqual(
            [{"step_id": "S003", "premise_id": "P001"}],
            disposition["premise_links"],
        )
