from __future__ import annotations

import argparse
import base64
import contextlib
import importlib.util
import io
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "proofcheck.py"
SPEC = importlib.util.spec_from_file_location("proofcheck", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT}")
proofcheck = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proofcheck)


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_normalization_checks() -> list[dict[str, str]]:
    statuses = {
        "quantifiers_and_domains": (
            "checked",
            "The universal quantifier and real-number domain are explicit.",
        ),
        "probability_model": (
            "not_applicable",
            "The claim contains no random quantity or probability statement.",
        ),
        "hypotheses": (
            "not_applicable",
            "The theorem has no hypotheses beyond its quantified domain.",
        ),
        "definitions": (
            "checked",
            "Equality has its standard meaning on the stated domain.",
        ),
        "conclusion": (
            "checked",
            "The normalized conclusion is exactly x equals x.",
        ),
        "uniformity": (
            "not_applicable",
            "The claim has no indexed convergence or bound.",
        ),
        "regime": (
            "not_applicable",
            "The claim is neither finite-sample nor asymptotic.",
        ),
        "constant_dependencies": (
            "not_applicable",
            "No hidden or named constants occur.",
        ),
    }
    return [
        {"aspect": aspect, "status": status, "evidence": evidence}
        for aspect, (status, evidence) in statuses.items()
    ]


def make_risk_checks() -> list[dict[str, str]]:
    statuses = {
        "domain": (
            "passed",
            "The only object is the real number x from the locked statement.",
        ),
        "dimension": (
            "not_applicable",
            "No vector, matrix, or dimension-sensitive operation occurs.",
        ),
        "sign": (
            "not_applicable",
            "No inequality, monotonicity, or sign argument occurs.",
        ),
        "constant": (
            "not_applicable",
            "No explicit or hidden constant occurs.",
        ),
        "rate": (
            "not_applicable",
            "No stochastic or asymptotic rate occurs.",
        ),
        "probability": (
            "not_applicable",
            "No event, measure, conditioning, or independence claim occurs.",
        ),
        "quantifier": (
            "passed",
            "The move applies to the arbitrary x fixed by the theorem statement.",
        ),
        "limit": (
            "not_applicable",
            "No limiting or exchange operation occurs.",
        ),
    }
    return [
        {"aspect": aspect, "status": status, "evidence": evidence}
        for aspect, (status, evidence) in statuses.items()
    ]


GLOBAL_CONSISTENCY_ASPECTS = (
    "source_resolution",
    "assumption_and_definition_propagation",
    "notation_domain_and_dimension",
    "constants_and_rates",
    "probability_events_and_conditioning",
    "quantifiers_uniformity_and_regime",
    "use_site_sufficiency",
    "issue_propagation",
)


def make_global_consistency_checks() -> list[dict]:
    return [
        {
            "aspect": aspect,
            "status": "passed",
            "evidence": f"The clean focused audit passed the {aspect} check.",
            "affected_units": [],
            "issue_ids": [],
        }
        for aspect in GLOBAL_CONSISTENCY_ASPECTS
    ]


def make_compatibility_checks() -> list[dict]:
    return [
        {
            "aspect": aspect,
            "status": "passed",
            "evidence": f"The dependency is compatible on the {aspect} aspect.",
            "issue_ids": [],
        }
        for aspect in proofcheck.NORMALIZATION_ASPECTS
    ]


class FinalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.paper = self.base / "paper.tex"
        self.definitions = self.base / "definitions.tex"
        self.definitions.write_text(
            "\\newtheorem{lemma}{Lemma}\n", encoding="utf-8", newline="\n"
        )
        self.paper.write_text(
            "\\input{definitions}\n"
            "\\begin{lemma}\\label{lem:main}\n"
            "$x=x$ for every real $x$.\\label{eq:reflexive}\n"
            "\\end{lemma}\n"
            "\\begin{proof}\n"
            "The conclusion follows by reflexivity; see \\ref{eq:reflexive} and \\cite{smith}.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        self.audit = self.base / "audit-root"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(paper=self.paper, output=self.audit)
            )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_complete_audit(self) -> Path:
        ledger_path = (
            self.audit / "audit" / "04_local_checks" / "lem-main.ledger.json"
        )
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=self.paper,
                    start=2,
                    end=7,
                    statement_file=self.paper,
                    statement_start=2,
                    statement_end=4,
                    separate_statement_reason=None,
                    unit_id="lem:main",
                    output=ledger_path,
                    force=False,
                )
        )
        ledger = read_json(ledger_path)
        inventory = read_json(
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        source_occurrences = inventory["units"][0]["reference_occurrences"]
        source_occurrence = source_occurrences[0] if source_occurrences else None
        conclusion_span = proofcheck.locked_span(
            self.paper, 2, 4, ledger_path.parent
        )
        ledger["obligation"] = {
            "statement_spans": [conclusion_span],
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
                    "source_spans": [dict(conclusion_span)],
                    "applies_under": ["/quantifier_scope"],
                    "normalization": {
                        "status": "checked",
                        "evidence": (
                            "The source states the reflexive equality under the "
                            "universal real-number quantifier."
                        ),
                    },
                }
            ],
            "uniformity": "not_applicable",
            "regime": "not_applicable",
            "constant_dependencies": ["none"],
            "context_spans": [],
            "normalization_checks": make_normalization_checks(),
        }
        ledger["review"] = {
            "unit_status": "verified",
            "conclusion_step_id": "S003",
            "conclusion_results": [
                {
                    "conclusion_id": "C001",
                    "support": {"step_id": "S003", "move_id": "M001"},
                    "contract_fidelity": "verified",
                    "argument_status": "valid",
                    "statement_status": "established",
                    "dependency_closure": "verified",
                    "use_site_sufficiency": "not_applicable",
                    "dependency_use_ids": [],
                    "issue_ids": [],
                }
            ],
            "contract_fidelity": "verified",
            "argument_status": "valid",
            "statement_status": "established",
            "dependency_closure": "verified",
            "use_site_sufficiency": "not_applicable",
            "explicit_assumptions": [],
            "inherited_assumptions": [],
            "direct_dependencies": [],
            "source_reference_dispositions": (
                [
                    {
                        "occurrence_id": source_occurrence["occurrence_id"],
                        "id": source_occurrence["target"],
                        "target": source_occurrence["target"],
                        "command": source_occurrence["command"],
                        "disposition": "non_load_bearing",
                        "evidence": "The proof is reconstructed from reflexivity; this self-reference supplies no premise."
                    }
                ]
                if source_occurrence is not None
                else []
            ),
            "citation_dispositions": [
                {
                    "key": "smith",
                    "disposition": "bibliographic_only",
                    "evidence": "The citation supplies attribution and no proof premise."
                }
            ],
            "use_sites": [],
            "verification_basis": [
                "Exact source ledger and direct reconstruction"
            ],
            "reviewer_notes": [],
        }
        ledger["independent_check"] = {
            "required": True,
            "status": "agreed",
            "independence_level": "fresh_context_same_model",
            "challenger_verdict": "verified",
            "reconciled_verdict": "verified",
            "artifact": "audit/05_adversarial/lem-main-challenge.md",
            "disagreements": [],
            "resolution": "",
        }
        ledger["steps"] = [
            {
                "id": "S001",
                "source_unit_id": "U001",
                "kind": "statement",
                "goal": "Identify the exact theorem obligation.",
                "restatement": "For every real x, x equals x.",
                "premise_uses": [],
                "dependencies": [],
                "inference": {
                    "moves": [],
                    "conclusion_move": None,
                },
                "checks": {
                    "literal": "The quantifier, domain, and equality are explicit.",
                    "atomicity": {
                        "status": "non_inferential",
                        "evidence": (
                            "This row source-locks the theorem statement and derives "
                            "no new claim."
                        ),
                    },
                    "adversarial": [
                        "The normalized contract has the same quantifier and domain."
                    ],
                },
                "side_conditions": [],
                "risk_checks": make_risk_checks(),
                "status": "verified",
                "issue_ids": [],
            },
            {
                "id": "S002",
                "source_unit_id": "U002",
                "kind": "other",
                "status": "non_substantive",
                "issue_ids": [],
            },
            {
                "id": "S003",
                "source_unit_id": "U003",
                "support_role": "derivation",
                "kind": "conclusion",
                "goal": "Establish x = x for an arbitrary real x.",
                "restatement": "x equals x",
                "premise_uses": [
                    {
                        "id": "P001",
                        "role": "fact",
                        "claim": "For every real x.",
                        "origin": {
                            "kind": "obligation",
                            "reference": "/quantifier_scope",
                            "anchor": {
                                "kind": "statement_span",
                                "index": 1,
                            },
                        },
                        "evidence": (
                            "The locked theorem statement supplies this exact "
                            "quantifier scope."
                        ),
                    }
                ],
                "dependencies": [],
                "inference": {
                    "moves": [
                        {
                            "id": "M001",
                            "claim": "x equals x",
                            "rule": "Reflexivity of equality",
                            "premise_ids": ["P001"],
                            "prior_move_ids": [],
                            "justification": (
                                "Reflexivity gives x = x for the arbitrary real x."
                            ),
                        }
                    ],
                    "conclusion_move": "M001",
                },
                "checks": {
                    "literal": "The line claims that reflexivity closes the goal.",
                    "atomicity": {
                        "status": "single_move",
                        "evidence": "The line contains one application of reflexivity.",
                    },
                    "adversarial": [
                        "No boundary value or domain element violates reflexivity."
                    ],
                },
                "side_conditions": [],
                "risk_checks": make_risk_checks(),
                "status": "verified",
                "issue_ids": [],
            },
            {
                "id": "S004",
                "source_unit_id": "U004",
                "kind": "other",
                "status": "non_substantive",
                "issue_ids": [],
            },
        ]
        ledger["schema_version"] = 5
        ledger["evidence_contract_version"] = 4
        ledger["source_units"] = [
            {
                "id": "U001",
                "lines": [2, 4],
                "kind": "continued_sentence",
                "source_sha256": proofcheck.source_span_sha256(
                    self.paper, 2, 4
                ),
                "partition_evidence": (
                    "Lines 2-4 are the single formal statement environment."
                ),
            },
            {
                "id": "U002",
                "lines": [5, 5],
                "kind": "non_substantive",
                "source_sha256": proofcheck.source_span_sha256(
                    self.paper, 5, 5
                ),
                "partition_evidence": "Line 5 only opens the proof environment.",
            },
            {
                "id": "U003",
                "lines": [6, 6],
                "kind": "one_line",
                "source_sha256": proofcheck.source_span_sha256(
                    self.paper, 6, 6
                ),
                "partition_evidence": (
                    "Line 6 is one source sentence containing one inference."
                ),
            },
            {
                "id": "U004",
                "lines": [7, 7],
                "kind": "non_substantive",
                "source_sha256": proofcheck.source_span_sha256(
                    self.paper, 7, 7
                ),
                "partition_evidence": "Line 7 only closes the proof environment.",
            },
        ]
        write_json(ledger_path, ledger)

        challenge = self.audit / "audit" / "05_adversarial" / "lem-main-challenge.md"
        challenge.write_text(
            "# Blinded challenge\n\nVerdict: verified.\n",
            encoding="utf-8",
            newline="\n",
        )
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"] = {
            "status": "reviewed",
            "depth": "focused",
            "overall_assessment": "no_defect_found",
            "in_scope_units": ["lem:main"],
            "target_units": ["lem:main"],
            "critical_units": ["lem:main"],
            "in_scope_interfaces": [],
            "excluded_units": [],
            "inventory_overrides": [],
            "source_or_parser_limits": [],
        }
        manifest["completion"] = {
            "inventory_reviewed": True,
            "parser_warnings_reviewed": True,
            "dependency_registry_reviewed": True,
            "method_interface_registry_reviewed": True,
            "global_consistency_pass": {
                "status": "completed",
                "evidence": ["Focused global consistency pass completed."],
                "checks": make_global_consistency_checks(),
            },
            "adversarial_pass": {
                "status": "completed",
                "evidence": ["Boundary and weakened-assumption checks completed."],
            },
            "final_report_ready": True,
        }
        write_json(manifest_path, manifest)

        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        dependency_registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        dependency_registry = read_json(dependency_registry_path)
        dependency_registry["closure_contract_version"] = (
            proofcheck.CLOSURE_CONTRACT_VERSION
        )
        dependency_registry["review"] = {
            "status": "reviewed",
            "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
            "inventory_sha256": proofcheck.sha256_file(inventory_path),
            "in_scope_units": ["lem:main"],
            "evidence": [
                "The dependency registry was reconciled against the locked "
                "source, reviewed inventory, and focused audit scope."
            ],
        }
        dependency_registry["internal_uses"] = []
        write_json(dependency_registry_path, dependency_registry)

        interface_registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "METHOD_INTERFACE_REGISTRY.json"
        )
        interface_registry = read_json(interface_registry_path)
        interface_registry["scope"] = {
            "status": "reviewed",
            "trigger": "not_required",
            "reason": "The focused reflexivity proof has no estimated method interface.",
        }
        write_json(interface_registry_path, interface_registry)

        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        challenge_record = read_json(ledger_path)["independent_check"]
        final_report = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        final_report.write_text(
            "# Final Proof-Check Report\n\n"
            "- Overall assessment code: no_defect_found\n"
            "- Overall judgment: No defect found under the stated non-formal protocol.\n"
            "- Checked scope: lem:main\n"
            "- Source revision: scaffolded source snapshot.\n"
            "- Skill version: 1.0\n"
            f"- Artifact schema version: {proofcheck.SCHEMA_VERSION}\n"
            f"- Evidence contract version: {proofcheck.EVIDENCE_CONTRACT_VERSION}\n"
            "- Method-interface schema version: 1\n"
            f"- Closure contract version: {proofcheck.CLOSURE_CONTRACT_VERSION}\n"
            f"- Source snapshot ID: {manifest['source_snapshot']['sha256']}\n"
            "- Finalization record: audit/06_reports/FINALIZATION.json\n"
            "- Highest-consequence issue: none\n"
            "- Final confidence: high within the declared non-formal scope.\n\n"
            "## Audit boundary and limitations\n\n"
            "- Files and results checked: paper.tex and lem:main.\n"
            "- Target results: lem:main\n"
            "- Results not checked: none\n"
            "- External results checked: none\n"
            "- External results not checked: none\n"
            "- Tooling, extraction, or rendering limitations: none\n"
            "- Declared external deliverables: none\n"
            "- Independence level of the critical-path challenge: fresh_context_same_model\n\n"
            "## Main theorem chain\n\n"
            "| Result | Unit status | Contract fidelity | Argument status | Statement status | Dependency closure | Use-site sufficiency | Evidence |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| lem:main | verified | verified | valid | established | verified | not_applicable | Exact source ledger and direct reconstruction. |\n\n"
            "## Conclusion judgments\n\n"
            "| Result | Conclusion | Contract fidelity | Argument status | Statement status | Dependency closure | Use-site sufficiency | Support | Dependency use IDs | Issue IDs |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            "| lem:main | C001 | verified | valid | established | verified | not_applicable | S003/M001 | none | none |\n\n"
            "## Dependency closure\n\n"
            "| Dependent | Use ID | Dependency | Dependency conclusion | Kind | Source status | Applicability status | Effective status | Issue IDs |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "None.\n\n"
            "## Issue index\n\nNo issues.\n\n"
            "## Detailed findings\n\nNo issues.\n\n"
            "## Independent critical-path challenges\n\n"
            "| Result | Challenge status | Independence | Covered issue IDs | Challenger verdict | Reconciled verdict | Disagreements | Artifact | Source snapshot SHA256 | Challenged ledger SHA256 | Artifact SHA256 | Generated UTC | Resolution |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
            f"| lem:main | agreed | fresh_context_same_model | none | verified | verified | [] | {challenge_record['artifact']} | {challenge_record['source_snapshot_sha256']} | {challenge_record['challenged_ledger_sha256']} | {challenge_record['challenge_artifact_sha256']} | {challenge_record['generated_utc']} | none |\n\n"
            "## Method-interface findings\n\nNone.\n\n"
            "## Computational evidence\n\nNone.\n\n"
            "## Unchecked scope\n\nNone.\n\n"
            "## Assurance boundary\n\n"
            "This is a non-formal audit. This is not a kernel-checked proof certificate.\n",
            encoding="utf-8",
            newline="\n",
        )

        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["status"] = "complete"
        progress["current_pass"] = 8
        progress["source_snapshot_sha256"] = manifest["source_snapshot"]["sha256"]
        progress["active_unit"] = None
        progress["completed_units"] = ["lem:main"]
        progress["conditional_units"] = []
        progress["blocked_units"] = {}
        progress["not_started_units"] = []
        progress["open_high_priority_issues"] = []
        progress["source_or_parser_limits"] = []
        progress["next_action"] = (
            "Audit complete; rerun finalization after any source or artifact change."
        )
        write_json(progress_path, progress)
        return ledger_path

    def refresh_dependency_review(self) -> dict:
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
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
        registry["closure_contract_version"] = (
            proofcheck.CLOSURE_CONTRACT_VERSION
        )
        registry["review"] = {
            "status": "reviewed",
            "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
            "inventory_sha256": proofcheck.sha256_file(inventory_path),
            "in_scope_units": list(manifest["audit_scope"]["in_scope_units"]),
            "evidence": [
                "The dependency registry was reconciled against the locked "
                "source, reviewed inventory, and declared audit scope."
            ],
        }
        registry.setdefault("internal_uses", [])
        write_json(registry_path, registry)
        return registry

    def attach_result_dependency(self, ledger_path: Path, dependency: dict) -> None:
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        step["dependencies"] = [dict(dependency)]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": dependency["needed_form"],
                "origin": {
                    "kind": dependency["kind"],
                    "reference": dependency["use_id"],
                },
                "evidence": (
                    "The dependency supplies exactly the recorded needed form."
                ),
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        ledger["review"]["direct_dependencies"] = [dict(dependency)]
        ledger["review"]["conclusion_results"][0]["dependency_use_ids"] = [
            dependency["use_id"]
        ]
        write_json(ledger_path, ledger)

    def install_internal_dependency(self, ledger_path: Path) -> tuple[Path, dict]:
        prior_path = ledger_path.with_name("lem-prior.ledger.json")
        prior = read_json(ledger_path)
        prior["unit_id"] = "lem:prior"
        definition_text = self.definitions.read_text(encoding="utf-8").splitlines()[0]
        prior_span = proofcheck.locked_span(
            self.definitions, 1, 1, prior_path.parent
        )
        prior["source"] = {
            "file": proofcheck.relative_or_absolute(
                self.definitions, prior_path.parent
            ),
            "start_line": 1,
            "end_line": 1,
            "unit_sha256": proofcheck.sha256_text(definition_text),
            "coverage_mode": "statement_and_proof",
            "separate_statement_reason": "",
        }
        prior["source_lines"] = [
            {
                "line": 1,
                "text": definition_text,
                "sha256": proofcheck.sha256_text(definition_text),
            }
        ]
        prior["obligation"]["statement_spans"] = [prior_span]
        prior["obligation"]["conclusion"] = (
            "Equality is reflexive on the real numbers"
        )
        prior["obligation"]["conclusions"][0]["claim"] = (
            "Equality is reflexive on the real numbers"
        )
        prior["obligation"]["conclusions"][0]["source_spans"] = [
            dict(prior_span)
        ]
        prior_step = json.loads(json.dumps(prior["steps"][2]))
        prior_step["id"] = "S001"
        prior_step["source_unit_id"] = "U001"
        prior_step["goal"] = "Establish reflexivity of real-number equality."
        prior_step["restatement"] = (
            "Equality is reflexive on the real numbers"
        )
        prior_step["inference"]["moves"][0]["claim"] = prior_step[
            "restatement"
        ]
        prior["steps"] = [prior_step]
        prior["source_units"] = [
            {
                "id": "U001",
                "lines": [1, 1],
                "kind": "one_line",
                "source_sha256": proofcheck.source_span_sha256(
                    self.definitions, 1, 1
                ),
                "partition_evidence": (
                    "Line 1 is the complete locked source unit for lem:prior."
                ),
            }
        ]
        prior["review"]["conclusion_step_id"] = "S001"
        prior["review"]["conclusion_results"][0]["support"]["step_id"] = "S001"
        prior["review"]["source_reference_dispositions"] = []
        prior["review"]["citation_dispositions"] = []
        write_json(prior_path, prior)

        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        prior_unit = json.loads(json.dumps(inventory["units"][0]))
        prior_unit["id"] = "lem:prior"
        prior_unit["label"] = "lem:prior"
        prior_unit["environment"] = "definition"
        prior_unit["proof_required"] = False
        prior_unit["statement"] = {
            "file": proofcheck.relative_or_absolute(
                self.definitions, self.paper.parent
            ),
            "start_line": 1,
            "end_line": 1,
        }
        prior_unit["statement_excerpt"] = definition_text
        prior_unit["proof"] = None
        prior_unit["proof_redirects"] = []
        prior_unit["proof_association"] = {
            "status": "not_required",
            "method": "manual_nonproof",
            "target": "lem:prior",
            "evidence_occurrence_ids": [],
        }
        prior_unit["reference_occurrences"] = []
        prior_unit["dependencies"] = []
        prior_unit["candidate_internal_dependencies"] = []
        prior_unit["citations"] = []
        inventory["units"].append(prior_unit)
        write_json(inventory_path, inventory)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["in_scope_units"] = ["lem:main", "lem:prior"]
        manifest["audit_scope"]["inventory_overrides"] = [
            {
                "unit_id": "lem:prior",
                "kind": "manual_unit",
                "reason": "The companion result is manually included for dependency tests.",
                "evidence": "Rendered-source review identifies its exact nonproof statement.",
                "reviewed_unit_sha256": proofcheck.canonical_sha256(prior_unit),
            }
        ]
        write_json(manifest_path, manifest)

        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["completed_units"] = ["lem:main", "lem:prior"]
        write_json(progress_path, progress)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report = report.replace(
            "- Checked scope: lem:main",
            "- Checked scope: lem:main, lem:prior",
        )
        report = report.replace(
            "- Files and results checked: paper.tex and lem:main.",
            "- Files and results checked: paper.tex, lem:main, and lem:prior.",
        )
        main_row = (
            "| lem:main | verified | verified | valid | established | verified | "
            "not_applicable | Exact source ledger and direct reconstruction. |"
        )
        prior_row = (
            "| lem:prior | verified | verified | valid | established | verified | "
            "not_applicable | Exact source ledger and direct reconstruction. |"
        )
        report = report.replace(main_row, main_row + "\n" + prior_row)
        main_conclusion = (
            "| lem:main | C001 | verified | valid | established | verified | "
            "not_applicable | S003/M001 | none | none |"
        )
        dependent_conclusion = (
            "| lem:main | C001 | verified | valid | established | verified | "
            "not_applicable | S003/M001 | D001 | none |"
        )
        prior_conclusion = (
            "| lem:prior | C001 | verified | valid | established | verified | "
            "not_applicable | S001/M001 | none | none |"
        )
        report = report.replace(
            main_conclusion,
            dependent_conclusion + "\n" + prior_conclusion,
        )
        empty_closure = (
            "| Dependent | Use ID | Dependency | Dependency conclusion | Kind | "
            "Source status | Applicability status | Effective status | Issue IDs |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "None."
        )
        internal_closure = (
            "| Dependent | Use ID | Dependency | Dependency conclusion | Kind | "
            "Source status | Applicability status | Effective status | Issue IDs |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "| lem:main | D001 | lem:prior | C001 | internal_result | verified | "
            "passed | verified | none |"
        )
        report = report.replace(empty_closure, internal_closure)
        report_path.write_text(report, encoding="utf-8", newline="\n")

        dependency = {
            "id": "lem:prior",
            "use_id": "D001",
            "kind": "internal_result",
            "conclusion_id": "C001",
            "status": "verified",
            "needed_form": prior["obligation"]["conclusion"],
            "compatibility_check": (
                "The required result has the same quantifiers, domain, and conclusion."
            ),
        }
        self.attach_result_dependency(ledger_path, dependency)
        use = {
            "dependent_unit": "lem:main",
            "use_id": dependency["use_id"],
            "dependency_id": "lem:prior",
            "dependency_conclusion_id": dependency["conclusion_id"],
            "step_ids": ["S003"],
            "needed_form": dependency["needed_form"],
            "dependency_conclusion": prior["obligation"]["conclusion"],
            "dependency_contract_sha256": proofcheck.canonical_sha256(
                proofcheck.conclusion_contract_payload(
                    prior["obligation"], dependency["conclusion_id"]
                )
            ),
            "compatibility_check": dependency["compatibility_check"],
            "compatibility_checks": make_compatibility_checks(),
            "status": "verified",
            "issue_ids": [],
        }
        registry = self.refresh_dependency_review()
        registry["internal_uses"] = [use]
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        write_json(registry_path, registry)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        self.seal_schema5_challenge(prior_path, read_json(prior_path))
        return prior_path, use

    def install_external_dependency(self, ledger_path: Path) -> tuple[Path, dict]:
        source_path = self.base / "external-reflexivity.txt"
        source_path.write_text(
            "External Result 1\nEquality is reflexive on the real numbers.\n",
            encoding="utf-8",
            newline="\n",
        )
        exact_statement = "Equality is reflexive on the real numbers."
        source_evidence = [
            {
                "file": proofcheck.relative_or_absolute(source_path, self.audit),
                "sha256": proofcheck.sha256_file(source_path),
                "locator": "External Result 1, line 2",
                "role": "authoritative_theorem_source",
            }
        ]
        dependency = {
            "id": "ext:reflexivity",
            "use_id": "D001",
            "kind": "external_result",
            "status": "verified",
            "needed_form": "Equality is reflexive on the real numbers",
            "compatibility_check": (
                "The external conclusion has the same domain and exact needed form."
            ),
        }
        self.attach_result_dependency(ledger_path, dependency)
        ledger = read_json(ledger_path)
        ledger["review"]["citation_dispositions"][0] = {
            "key": "smith",
            "disposition": "external_result",
            "dependency_id": dependency["id"],
            "dependency_use_id": dependency["use_id"],
            "evidence": (
                "The citation supplies the exact external reflexivity result used in S003."
            ),
        }
        write_json(ledger_path, ledger)

        contract_payload = {
            "source_identity": "doi:10.0000/reflexivity",
            "version": "version 1",
            "theorem_location": "External Result 1",
            "exact_statement": exact_statement,
            "source_evidence": source_evidence,
        }
        use = {
            "dependent_unit": "lem:main",
            "use_id": dependency["use_id"],
            "dependency_id": dependency["id"],
            "step_ids": ["S003"],
            "needed_form": dependency["needed_form"],
            "dependency_conclusion": exact_statement,
            "dependency_contract_sha256": proofcheck.canonical_sha256(
                contract_payload
            ),
            "compatibility_check": dependency["compatibility_check"],
            "compatibility_checks": make_compatibility_checks(),
            "status": "verified",
            "issue_ids": [],
            "citation_keys": ["smith"],
            "prerequisite_map": [
                {
                    "prerequisite": "The manuscript variable x is real.",
                    "manuscript_evidence": (
                        "The locked theorem statement quantifies x over the real numbers."
                    ),
                    "status": "satisfied",
                    "evidence_spans": [
                        proofcheck.locked_span(
                            self.paper,
                            2,
                            4,
                            self.audit,
                            role="manuscript_prerequisite",
                        )
                    ],
                    "issue_ids": [],
                }
            ],
        }
        external = {
            "id": dependency["id"],
            "status": "verified",
            **contract_payload,
            "issue_ids": [],
            "uses": [use],
        }
        registry = self.refresh_dependency_review()
        registry["external_results"] = [external]
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        write_json(registry_path, registry)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "- External results checked: none",
            "- External results checked: ext:reflexivity",
        )
        report = report.replace(
            "| lem:main | C001 | verified | valid | established | verified | "
            "not_applicable | S003/M001 | none | none |",
            "| lem:main | C001 | verified | valid | established | verified | "
            "not_applicable | S003/M001 | D001 | none |",
        )
        empty_closure = (
            "| Dependent | Use ID | Dependency | Dependency conclusion | Kind | "
            "Source status | Applicability status | Effective status | Issue IDs |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "None."
        )
        external_closure = (
            "| Dependent | Use ID | Dependency | Dependency conclusion | Kind | "
            "Source status | Applicability status | Effective status | Issue IDs |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "| lem:main | D001 | ext:reflexivity | none | external_result | "
            "verified | passed | verified | none |"
        )
        report = report.replace(empty_closure, external_closure)
        report_path.write_text(report, encoding="utf-8", newline="\n")
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        return source_path, use

    def migrate_issue_fixture_to_schema5(
        self,
        issue: dict,
        *,
        ledger_path: Path | None = None,
        step_index: int | None = None,
    ) -> tuple[dict, int | None]:
        if (
            "origin_ref" in issue
            and "contract_refs" in issue
            and "invalidation_kind" in issue
            and "suggested_changes" in issue
        ):
            return issue, step_index

        affected_result = issue.get("affected_result")
        if ledger_path is not None:
            ledger = read_json(ledger_path)
            if step_index is None:
                conclusion_step_id = ledger.get("review", {}).get(
                    "conclusion_step_id"
                )
                step_index = next(
                    (
                        index
                        for index, step in enumerate(ledger.get("steps", []))
                        if step.get("id") == conclusion_step_id
                    ),
                    0,
                )
            step = ledger["steps"][step_index]
            moves = step.get("inference", {}).get("moves", [])
            move_id = (
                moves[-1].get("id")
                if isinstance(moves, list)
                and moves
                and isinstance(moves[-1], dict)
                else None
            )
            issue["origin_ref"] = (
                {
                    "kind": "ledger_move",
                    "unit_id": ledger["unit_id"],
                    "step_id": step["id"],
                    "move_id": move_id,
                }
                if move_id is not None
                else {
                    "kind": "obligation_pointer",
                    "unit_id": ledger["unit_id"],
                    "pointer": "/conclusions/0",
                }
            )
        elif isinstance(issue.get("interface_id"), str):
            issue["origin_ref"] = {
                "kind": "interface_record",
                "interface_id": issue["interface_id"],
                "evidence_spans": [
                    proofcheck.locked_span(
                        self.paper,
                        2,
                        4,
                        self.audit,
                        role="authoritative_definition",
                    )
                ],
            }
        else:
            issue["origin_ref"] = {
                "kind": "obligation_pointer",
                "unit_id": affected_result,
                "pointer": "/conclusions/0",
            }

        issue["contract_refs"] = []
        if issue["origin_ref"]["kind"] == "obligation_pointer":
            issue["contract_refs"].append(
                {
                    "kind": "obligation_pointer",
                    "unit_id": affected_result,
                    "pointer": issue["origin_ref"]["pointer"],
                }
            )
        issue["contract_refs"].append(
            {
                "kind": "conclusion",
                "unit_id": affected_result,
                "conclusion_id": "C001",
            }
        )
        finding_status = issue.get("finding_status")
        issue["invalidation_kind"] = (
            "scope_inconclusive"
            if finding_status == "inconclusive"
            else (
                "proof_invalid"
                if issue.get("load_bearing") is True
                else "presentation_only"
            )
        )
        proposal = issue.get("possible_repair")
        if not isinstance(proposal, str):
            proposal = "Resolve the finding and rerun every required check."
        affected_results = issue.get("affected_results")
        required_rechecks = (
            sorted(
                result
                for result in affected_results
                if isinstance(result, str)
            )
            if isinstance(affected_results, list)
            else []
        )
        issue["suggested_changes"] = [
            {
                "target_ref": {
                    "kind": "source_span",
                    "file": proofcheck.relative_or_absolute(
                        self.paper, self.audit
                    ),
                    "start_line": 2,
                    "end_line": 4,
                    "sha256": proofcheck.source_span_sha256(
                        self.paper, 2, 4
                    ),
                },
                "action": "repair_step",
                "proposal": proposal,
                "verification_status": "candidate",
                "required_rechecks": required_rechecks,
            }
        ]
        for field in (
            "location",
            "evidence",
            "downstream_consequences",
            "possible_repair",
        ):
            issue.pop(field, None)
        return issue, step_index

    def install_canonical_issue(
        self,
        issue: dict,
        *,
        ledger_path: Path | None = None,
        step_index: int | None = None,
        migrate: bool = True,
    ) -> None:
        if migrate:
            issue, step_index = self.migrate_issue_fixture_to_schema5(
                issue,
                ledger_path=ledger_path,
                step_index=step_index,
            )
        if ledger_path is not None:
            ledger = read_json(ledger_path)
            if step_index is None:
                step_index = 0
            linked_step = ledger["steps"][step_index]
            linked_step["issue_ids"] = sorted(
                set([*linked_step["issue_ids"], issue["id"]])
            )
            for result in ledger.get("review", {}).get(
                "conclusion_results", []
            ):
                support = result.get("support")
                if (
                    isinstance(support, dict)
                    and support.get("step_id") == linked_step.get("id")
                ):
                    result["issue_ids"] = sorted(
                        set([*result.get("issue_ids", []), issue["id"]])
                    )
            write_json(ledger_path, ledger)
            self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        write_json(
            issue_path,
            {"schema_version": proofcheck.SCHEMA_VERSION, "issues": [issue]},
        )
        summary_path = self.audit / "audit" / "06_reports" / "ISSUE_SUMMARY.md"
        summary_path.write_text(
            proofcheck.render_issue_summary([issue]),
            encoding="utf-8",
            newline="\n",
        )

        _, summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        summaries_by_id = {
            summary["unit_id"]: summary
            for summary in summaries
            if isinstance(summary.get("unit_id"), str)
        }
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
        registry_path = self.audit / "audit" / "03_dependencies" / "DEPENDENCY_REGISTRY.json"
        registry = read_json(registry_path)
        dependency_edges = list(registry.get("internal_uses", []))
        for external in registry.get("external_results", []):
            if isinstance(external, dict):
                dependency_edges.extend(external.get("uses", []))
        scope = manifest["audit_scope"]
        critical, _ = proofcheck.effective_critical_requirements(
            manifest,
            [issue],
        )
        interface_registry = read_json(
            self.audit
            / "audit"
            / "03_dependencies"
            / "METHOD_INTERFACE_REGISTRY.json"
        )
        interfaces = {
            row["id"]: row
            for row in interface_registry.get("interfaces", [])
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        global_pass = manifest.get("completion", {}).get(
            "global_consistency_pass", {}
        )
        global_checks = {
            row["aspect"]: row
            for row in global_pass.get("checks", [])
            if isinstance(row, dict) and isinstance(row.get("aspect"), str)
        }
        issue_index, detail = proofcheck.render_issue_report_views(
            [issue],
            summaries_by_id,
            dependency_edges,
            critical,
            manifest.get("report_deliverables", []),
            scope.get("overall_assessment"),
            interfaces=interfaces,
            global_checks=global_checks,
        )
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        if issue.get("status") in {"open", "deferred"}:
            report = report.replace(
                "- Highest-consequence issue: none",
                f"- Highest-consequence issue: {issue['id']}",
            )
        report = proofcheck.replace_report_section_text(
            report, "## Issue index", issue_index
        )
        report = proofcheck.replace_report_section_text(
            report, "## Detailed findings", detail
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

    def make_global_issue(
        self,
        *,
        finding_status: str = "inconclusive",
        load_bearing: bool = False,
        affected_result: str = "lem:main",
        affected_results: list[str] | None = None,
        issue_id: str = "I-001",
        severity: str = "S2",
        summary: str = "A proof-audit finding requires explicit resolution.",
    ) -> dict:
        issue = {
            "id": issue_id,
            "severity": severity,
            "confidence": "high",
            "status": "open",
            "finding_status": finding_status,
            "scope": "global",
            "load_bearing": load_bearing,
            "affected_result": affected_result,
            "affected_results": (
                [affected_result]
                if affected_results is None
                else list(affected_results)
            ),
            "summary": summary,
        }
        issue, _ = self.migrate_issue_fixture_to_schema5(issue)
        return issue

    def set_expected_assessment(self, assessment: str) -> None:
        judgments = {
            "no_defect_found": (
                "No defect found under the stated non-formal protocol."
            ),
            "inconclusive": "Inconclusive under the stated non-formal protocol.",
            "defects_found": (
                "Defects found under the stated non-formal protocol."
            ),
        }
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        previous = manifest["audit_scope"]["overall_assessment"]
        manifest["audit_scope"]["overall_assessment"] = assessment
        write_json(manifest_path, manifest)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report = report.replace(
            f"- Overall assessment code: {previous}",
            f"- Overall assessment code: {assessment}",
        )
        for judgment in judgments.values():
            report = report.replace(
                f"- Overall judgment: {judgment}",
                f"- Overall judgment: {judgments[assessment]}",
            )
        report_path.write_text(report, encoding="utf-8", newline="\n")

    def sync_incorrect_main_report(
        self,
        ledger_path: Path,
        *,
        dependency_issue: bool = False,
    ) -> None:
        ledger = read_json(ledger_path)
        review = ledger["review"]
        conclusion = review["conclusion_results"][0]
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        clean_main = (
            "| lem:main | verified | verified | valid | established | verified | "
            "not_applicable | Exact source ledger and direct reconstruction. |"
        )
        current_main = (
            f"| lem:main | {review['unit_status']} | "
            f"{review['contract_fidelity']} | {review['argument_status']} | "
            f"{review['statement_status']} | {review['dependency_closure']} | "
            f"{review['use_site_sufficiency']} | Exact source ledger and direct "
            "reconstruction. |"
        )
        report = report.replace(clean_main, current_main, 1)

        dependency_ids = proofcheck.canonical_id_field(
            conclusion.get("dependency_use_ids", [])
        )
        clean_conclusion = (
            "| lem:main | C001 | verified | valid | established | verified | "
            f"not_applicable | S003/M001 | {dependency_ids} | none |"
        )
        current_conclusion = (
            f"| lem:main | C001 | {conclusion['contract_fidelity']} | "
            f"{conclusion['argument_status']} | {conclusion['statement_status']} | "
            f"{conclusion['dependency_closure']} | "
            f"{conclusion['use_site_sufficiency']} | S003/M001 | "
            f"{dependency_ids} | "
            f"{proofcheck.canonical_id_field(conclusion.get('issue_ids', []))} |"
        )
        report = report.replace(clean_conclusion, current_conclusion, 1)

        if dependency_issue:
            clean_dependency = (
                "| lem:main | D001 | lem:prior | C001 | internal_result | "
                "verified | passed | verified | none |"
            )
            current_dependency = (
                "| lem:main | D001 | lem:prior | C001 | internal_result | "
                "verified | incorrect | incorrect | I-001 |"
            )
            report = report.replace(clean_dependency, current_dependency, 1)

        check = ledger["independent_check"]
        challenge = proofcheck.render_markdown_table(
            [
                "Result",
                "Challenge status",
                "Independence",
                "Covered issue IDs",
                "Challenger verdict",
                "Reconciled verdict",
                "Disagreements",
                "Artifact",
                "Source snapshot SHA256",
                "Challenged ledger SHA256",
                "Artifact SHA256",
                "Generated UTC",
                "Resolution",
            ],
            [
                [
                    "lem:main",
                    check["status"],
                    check["independence_level"],
                    proofcheck.canonical_id_field(
                        check.get("covered_issue_ids", [])
                    ),
                    check["challenger_verdict"],
                    check["reconciled_verdict"],
                    json.dumps(
                        check.get("disagreements", []),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                    check["artifact"],
                    check["source_snapshot_sha256"],
                    check["challenged_ledger_sha256"],
                    check["challenge_artifact_sha256"],
                    check["generated_utc"],
                    check.get("resolution") or "none",
                ]
            ],
        )
        report = proofcheck.replace_report_section_text(
            report,
            "## Independent critical-path challenges",
            challenge,
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

    def make_ledger_move_defect_audit(self) -> tuple[Path, dict, str]:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        failure_evidence = (
            "The cited reflexivity rule does not establish the altered "
            "conclusion under the recorded premise."
        )
        step["status"] = "incorrect"
        step["issue_ids"] = ["I-001"]
        step["inference"]["moves"][0]["failure"] = {
            "kind": "invalid_rule",
            "issue_id": "I-001",
            "evidence": failure_evidence,
        }
        conclusion = ledger["review"]["conclusion_results"][0]
        conclusion["argument_status"] = "invalid"
        conclusion["statement_status"] = "not_established"
        conclusion["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "incorrect"
        ledger["review"]["argument_status"] = "invalid"
        ledger["review"]["statement_status"] = "not_established"
        ledger["independent_check"]["covered_issue_ids"] = ["I-001"]
        ledger["independent_check"]["challenger_verdict"] = "incorrect"
        ledger["independent_check"]["reconciled_verdict"] = "incorrect"
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))

        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=True,
            severity="S2",
            summary=(
                "The recorded inference rule does not establish the claimed "
                "conclusion."
            ),
        )
        issue.update(
            {
                "origin_ref": {
                    "kind": "ledger_move",
                    "unit_id": "lem:main",
                    "step_id": "S003",
                    "move_id": "M001",
                },
                "contract_refs": [
                    {
                        "kind": "conclusion",
                        "unit_id": "lem:main",
                        "conclusion_id": "C001",
                    }
                ],
                "invalidation_kind": "proof_invalid",
            }
        )
        self.set_expected_assessment("defects_found")
        self.install_canonical_issue(
            issue,
            ledger_path=ledger_path,
            step_index=2,
            migrate=False,
        )
        self.sync_incorrect_main_report(ledger_path)
        return ledger_path, issue, failure_evidence

    def make_dependency_mismatch_audit(self) -> tuple[Path, dict]:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        for dependency in (
            step["dependencies"][0],
            ledger["review"]["direct_dependencies"][0],
        ):
            dependency["status"] = "incorrect"
            dependency["issue_ids"] = ["I-001"]
        step["status"] = "incorrect"
        step["issue_ids"] = ["I-001"]
        step["inference"]["moves"][0]["failure"] = {
            "kind": "invalid_rule",
            "issue_id": "I-001",
            "evidence": (
                "The dependency compatibility check is incorrect, so this "
                "move cannot use D001 as recorded."
            ),
        }
        conclusion = ledger["review"]["conclusion_results"][0]
        conclusion["argument_status"] = "invalid"
        conclusion["statement_status"] = "not_established"
        conclusion["dependency_closure"] = "incorrect"
        conclusion["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "incorrect"
        ledger["review"]["argument_status"] = "invalid"
        ledger["review"]["statement_status"] = "not_established"
        ledger["review"]["dependency_closure"] = "incorrect"
        ledger["independent_check"]["covered_issue_ids"] = ["I-001"]
        ledger["independent_check"]["challenger_verdict"] = "incorrect"
        ledger["independent_check"]["reconciled_verdict"] = "incorrect"
        write_json(ledger_path, ledger)

        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        use = registry["internal_uses"][0]
        use["compatibility_checks"][0].update(
            {
                "status": "incorrect",
                "evidence": (
                    "The dependency conclusion has the wrong quantified domain "
                    "at this use site."
                ),
                "issue_ids": ["I-001"],
            }
        )
        use["status"] = "incorrect"
        use["issue_ids"] = ["I-001"]
        write_json(registry_path, registry)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))

        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=True,
            severity="S2",
            summary=(
                "The D001 dependency use fails its quantified-domain "
                "compatibility check."
            ),
        )
        issue.update(
            {
                "origin_ref": {
                    "kind": "dependency_use",
                    "unit_id": "lem:main",
                    "use_id": "D001",
                },
                "contract_refs": [
                    {
                        "kind": "dependency_use",
                        "unit_id": "lem:main",
                        "use_id": "D001",
                    },
                    {
                        "kind": "conclusion",
                        "unit_id": "lem:main",
                        "conclusion_id": "C001",
                    },
                ],
                "invalidation_kind": "dependency_mismatch",
            }
        )
        issue["suggested_changes"][0]["action"] = "repair_dependency"
        self.set_expected_assessment("defects_found")
        self.install_canonical_issue(
            issue,
            ledger_path=ledger_path,
            step_index=2,
            migrate=False,
        )
        self.sync_incorrect_main_report(
            ledger_path,
            dependency_issue=True,
        )
        return ledger_path, issue

    def make_interface_record(
        self,
        *,
        specification: str = "clear",
        target_verdict: str = "match",
        implementation_inspection: str = "inspected",
        code_to_documented: str = "consistent",
        code_to_target: str = "consistent",
        execution_provenance: str = "not_checked",
        load_bearing: bool = False,
        implementation_required: bool = False,
        execution_required: bool = False,
    ) -> dict:
        code = self.base / "estimator.py"
        code.write_text(
            "def fit_ratio(states, beta_actions, pi_actions):\n"
            "    return states, beta_actions, pi_actions\n",
            encoding="utf-8",
            newline="\n",
        )
        manuscript_span = proofcheck.locked_span(
            self.paper, 2, 4, self.audit, role="authoritative_definition"
        )
        inspected = implementation_inspection == "inspected"
        implementation_spans = (
            [
                proofcheck.locked_span(
                    code,
                    1,
                    2,
                    self.audit,
                    role="implementation_snapshot",
                )
            ]
            if inspected
            else []
        )
        run_record = self.base / "run-record.txt"
        run_record.write_text(
            "reported_revision=other-snapshot\n",
            encoding="utf-8",
            newline="\n",
        )
        provenance_spans = (
            [
                proofcheck.locked_span(
                    run_record,
                    1,
                    1,
                    self.audit,
                    role="execution_provenance",
                )
            ]
            if execution_provenance in {"matched", "not_matched"}
            else []
        )
        alternatives = []
        if specification in {"ambiguous", "incomplete"}:
            alternatives = [
                {
                    "interpretation": "The two laws share the same state reference law.",
                    "consequence": "The state marginal cancels.",
                    "evidence": ["paper.tex:2-4"],
                },
                {
                    "interpretation": "The two laws use policy-specific state marginals.",
                    "consequence": "An additional state-density ratio remains.",
                    "evidence": ["paper.tex:2-4"],
                },
            ]
        unresolved = (
            specification in {"ambiguous", "incomplete", "not_checked"}
            or target_verdict
            in {"conditional_match", "not_assessable", "not_checked"}
            or (
                implementation_required
                and (
                    implementation_inspection
                    in {"available_not_checked", "unavailable", "out_of_scope"}
                    or code_to_documented != "consistent"
                    or code_to_target != "consistent"
                )
            )
            or (execution_required and execution_provenance != "matched")
        )
        return {
            "id": "MI-001",
            "kind": "density_ratio",
            "load_bearing": load_bearing,
            "implementation_required_for_claim": implementation_required,
            "execution_provenance_required_for_claim": execution_required,
            "affected_results": ["lem:main"],
            "population_target": {
                "formula": "pi(a|s) / beta(a|s)",
                "measure_and_support": "The conditional action laws on their common support.",
                "equality_notion": "Equality almost everywhere under the behavior law.",
            },
            "identification_identity": "d(P_ref pi) / d(P_ref beta) = pi / beta.",
            "fitting_sample_laws": [
                {
                    "role": "numerator",
                    "law": "P_ref(ds) pi(da|s)",
                    "reference_law": "P_ref",
                    "evidence_spans": [dict(manuscript_span)],
                },
                {
                    "role": "denominator",
                    "law": "P_ref(ds) beta(da|s)",
                    "reference_law": "P_ref",
                    "evidence_spans": [dict(manuscript_span)],
                },
            ],
            "marginal_relationships": [
                "The state reference law is equal; the conditional action law changes."
            ],
            "evaluation_sites": ["Logged successor state-action inputs."],
            "downstream_uses": ["The weight in lem:main."],
            "interface_specification_status": specification,
            "derivation_status": "valid",
            "target_relation": {
                "verdict": target_verdict,
                "assumptions": [],
                "reason": "The relation follows from, or is limited by, the locked specification.",
                "evidence_spans": [dict(manuscript_span)],
            },
            "implementation_relation": {
                "inspection_status": implementation_inspection,
                "inspection_mode": "static" if inspected else "not_applicable",
                "revision": "test-snapshot" if inspected else "",
                "evidence_spans": implementation_spans,
                "reason": (
                    "The locked implementation snapshot was inspected."
                    if inspected
                    else "Implementation evidence was unavailable or outside inspection scope."
                ),
                "comparisons": [
                    {
                        "to": "documented_estimator",
                        "verdict": code_to_documented,
                        "reason": "The code was compared with the documented estimator.",
                        "evidence_spans": (
                            implementation_spans
                            if code_to_documented in {"consistent", "inconsistent"}
                            else []
                        ),
                    },
                    {
                        "to": "required_target",
                        "verdict": code_to_target,
                        "reason": "The code was compared with the required target.",
                        "evidence_spans": (
                            implementation_spans
                            if code_to_target in {"consistent", "inconsistent"}
                            else []
                        ),
                    },
                ],
                "execution_provenance": {
                    "status": execution_provenance,
                    "reason": (
                        "The locked run record identifies a different revision."
                        if execution_provenance == "not_matched"
                        else "No run-to-snapshot linkage was supplied."
                    ),
                    "evidence_spans": provenance_spans,
                },
            },
            "alternative_interpretations": alternatives,
            "resolution_evidence_needed": (
                ["Authoritative fitting laws or implementation evidence are needed."]
                if unresolved
                else []
            ),
            "issue_ids": [],
        }

    def install_interface_record(self, record: dict) -> None:
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "METHOD_INTERFACE_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["scope"] = {
            "status": "reviewed",
            "trigger": "required",
            "reason": "A load-bearing density-ratio interface was reviewed.",
        }
        registry["interfaces"] = [record]
        write_json(registry_path, registry)
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["in_scope_interfaces"] = [record["id"]]
        write_json(manifest_path, manifest)

    def install_interface_issue(self, record: dict, issue: dict) -> None:
        record["issue_ids"] = [issue["id"]]
        self.install_interface_record(record)
        self.install_canonical_issue(issue)
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        row = "| " + " | ".join(
            proofcheck.escape_markdown(value)
            for value in proofcheck.canonical_interface_issue_row(
                issue,
                {record["id"]: record},
            )
        ) + " |"
        report = report.replace(
            "## Method-interface findings\n\nNone.",
            "## Method-interface findings\n\n"
            "| Issue | Finding class | Interface ID | Estimator-target status | Implementation inspection | Inspection mode | Code to documented estimator | Code to required target | Execution provenance | Affected layer |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            + row,
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

    def test_complete_minimal_audit_passes(self) -> None:
        self.make_complete_audit()
        errors, result = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)
        self.assertEqual(0, result["errors"])

    def test_empty_audit_fails_finalization(self) -> None:
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("at least one proof-unit ledger" in error for error in errors),
            errors,
        )

    def test_unknown_verified_dependency_fails(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        dependency = {
            "id": "lem:missing",
            "use_id": "D001",
            "kind": "internal_result",
            "conclusion_id": "C001",
            "status": "verified",
            "needed_form": "A missing conclusion.",
            "compatibility_check": "The record claims compatibility.",
        }
        ledger["steps"][0]["dependencies"] = [dependency]
        ledger["review"]["direct_dependencies"] = [dependency]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("unknown internal dependency lem:missing" in error for error in errors),
            errors,
        )

    def test_step_dependency_cycle_fails(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][0]["dependencies"] = [
            {
                "id": "S001",
                "kind": "step",
                "status": "verified",
            }
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(any("Step dependency cycle" in error for error in errors), errors)

    def test_step_cannot_depend_on_a_later_step(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][0]["dependencies"] = [
            {
                "id": "S003",
                "kind": "step",
                "status": "verified",
            }
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("not established before use" in error for error in errors), errors
        )

    def test_conditional_status_cannot_hide_failed_dependency(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        dependency = {
            "id": "ext:failed",
            "use_id": "D001",
            "kind": "external_result",
            "status": "gap",
            "needed_form": "A required external conclusion.",
            "compatibility_check": "The external prerequisite is absent.",
        }
        ledger["steps"][0]["dependencies"] = [dependency]
        ledger["steps"][0]["status"] = "conditionally_verified"
        ledger["steps"][0]["conditions"] = ["Assume the missing premise."]
        ledger["review"]["unit_status"] = "conditionally_verified"
        ledger["review"]["argument_status"] = "conditional"
        ledger["review"]["statement_status"] = "conditional"
        ledger["review"]["dependency_closure"] = "conditionally_verified"
        ledger["review"]["direct_dependencies"] = [dependency]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("cannot hide failed dependencies" in error for error in errors),
            errors,
        )

    def mark_s003_conditional(self, ledger: dict) -> dict:
        step = ledger["steps"][2]
        step["status"] = "conditionally_verified"
        ledger["review"]["unit_status"] = "conditionally_verified"
        ledger["review"]["argument_status"] = "conditional"
        ledger["review"]["statement_status"] = "conditional"
        result = ledger["review"]["conclusion_results"][0]
        result["argument_status"] = "conditional"
        result["statement_status"] = "conditional"
        ledger["independent_check"]["challenger_verdict"] = (
            "conditionally_verified"
        )
        ledger["independent_check"]["reconciled_verdict"] = (
            "conditionally_verified"
        )
        return step

    def test_legacy_ledger_is_inspection_only(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = self.downgrade_ledger_fixture_to_schema4(
            read_json(ledger_path)
        )
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "schema 4 is inspection-only" in error
                or "evidence contract 3 is inspection-only" in error
                for error in errors
            ),
            errors,
        )

    def test_legacy_ledger_remains_readable_in_nonfinal_mode(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = self.downgrade_ledger_fixture_to_schema4(
            read_json(ledger_path)
        )
        del ledger["obligation"]["normalization_checks"]
        del ledger["obligation"]["quantified_variables"][0]["quantifier"]
        ledger["review"]["conclusion_results"] = []
        for step in (ledger["steps"][0], ledger["steps"][2]):
            step.pop("premise_uses", None)
            step.pop("inference", None)
            step.pop("risk_checks", None)
            step["required_facts"] = ["Legacy free-text fact."]
            step["assumptions"] = ["Legacy free-text assumption."]
            step["checks"]["inferential"] = "Legacy free-text inference."
            step["checks"]["atomicity"] = "Legacy free-text atomicity."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, False)
        self.assertEqual([], errors)

    def test_evidence_contract_rejects_legacy_step_fields(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["required_facts"] = ["Reflexivity"]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("legacy free-text fields are not allowed" in error for error in errors),
            errors,
        )

    def test_obligation_premise_origin_must_resolve(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["premise_uses"][0]["origin"]["reference"] = (
            "/quantified_variables/99"
        )
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("unresolved obligation premise" in error for error in errors),
            errors,
        )

    def test_theorem_statement_cannot_be_used_as_its_own_premise(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["premise_uses"][0]["origin"]["reference"] = (
            "/statement_spans/0"
        )
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("unresolved obligation premise /statement_spans/0" in error for error in errors),
            errors,
        )

    def test_obligation_premise_needs_a_locked_anchor(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["premise_uses"][0]["origin"]["anchor"]["index"] = 2
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("origin.anchor is out of range" in error for error in errors),
            errors,
        )

    def test_inference_must_consume_every_premise(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["inference"]["moves"][0]["premise_ids"] = []
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("premise uses not consumed" in error for error in errors),
            errors,
        )

    def test_inference_cannot_use_an_unknown_premise(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["inference"]["moves"][0]["premise_ids"] = ["P999"]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("uses unknown premise P999" in error for error in errors),
            errors,
        )

    def test_final_inference_claim_must_match_restatement(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["inference"]["moves"][0]["claim"] = "x equals x."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("final inference claim must exactly match restatement" in error for error in errors),
            errors,
        )

    def test_source_indivisible_chain_records_each_atomic_move(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = self.downgrade_ledger_fixture_to_schema4(
            read_json(ledger_path)
        )
        step = ledger["steps"][2]
        step["checks"]["atomicity"] = {
            "status": "source_indivisible_chain",
            "source_unit_kind": "one_line",
            "partition_evidence": (
                "The single source line contains two successive logical moves."
            ),
            "evidence": "One physical source line contains two linked transitions.",
        }
        step["inference"] = {
            "moves": [
                {
                    "id": "M001",
                    "claim": "Reflexivity applies to x.",
                    "rule": "Reflexivity of equality",
                    "premise_ids": ["P001"],
                    "prior_move_ids": [],
                    "justification": "The rule applies to the arbitrary real x.",
                },
                {
                    "id": "M002",
                    "claim": step["restatement"],
                    "rule": "Goal closure",
                    "premise_ids": [],
                    "prior_move_ids": ["M001"],
                    "justification": "The reflexive equality is exactly the goal.",
                },
            ],
            "conclusion_move": "M002",
        }
        ledger["review"]["conclusion_results"][0]["support"]["move_id"] = "M002"
        write_json(ledger_path, ledger)
        errors, summary = proofcheck.check_ledger_data(ledger_path, False)
        self.assertEqual([], errors)
        self.assertEqual("legacy_inspection_only", summary["validation_scope"][
            "local_record_integrity"
        ])

    def test_legacy_multiline_chain_remains_inspection_only(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = self.downgrade_ledger_fixture_to_schema4(
            read_json(ledger_path)
        )
        step = ledger["steps"][2]
        del ledger["steps"][1]
        step["lines"] = [5, 6]
        step["checks"]["atomicity"] = {
            "status": "source_indivisible_chain",
            "evidence": "This negative control improperly groups two source lines.",
        }
        step["inference"] = {
            "moves": [
                {
                    "id": "M001",
                    "claim": "Reflexivity applies to x.",
                    "rule": "Reflexivity of equality",
                    "premise_ids": ["P001"],
                    "prior_move_ids": [],
                    "justification": "The rule applies to the arbitrary real x.",
                },
                {
                    "id": "M002",
                    "claim": step["restatement"],
                    "rule": "Goal closure",
                    "premise_ids": [],
                    "prior_move_ids": ["M001"],
                    "justification": "The reflexive equality is exactly the goal.",
                },
            ],
            "conclusion_move": "M002",
        }
        ledger["review"]["conclusion_results"][0]["support"]["move_id"] = "M002"
        write_json(ledger_path, ledger)
        errors, summary = proofcheck.check_ledger_data(ledger_path, False)
        self.assertEqual([], errors)
        self.assertEqual(
            "legacy_inspection_only",
            summary["validation_scope"]["local_record_integrity"],
        )

    def test_single_move_atomicity_rejects_a_chain(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        step["inference"]["moves"].append(
            {
                "id": "M002",
                "claim": step["restatement"],
                "rule": "Repeated closure",
                "premise_ids": [],
                "prior_move_ids": ["M001"],
                "justification": "A second move was inserted for the negative control.",
            }
        )
        step["inference"]["conclusion_move"] = "M002"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "schema-5 inferential step must contain exactly one move"
                in error
                for error in errors
            ),
            errors,
        )

    def test_risk_matrix_requires_exact_aspect_coverage(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["risk_checks"] = [
            row
            for row in ledger["steps"][2]["risk_checks"]
            if row["aspect"] != "rate"
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("risk_checks must contain each required aspect exactly once" in error for error in errors),
            errors,
        )

    def test_verified_step_rejects_an_open_risk(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        domain = next(
            row for row in ledger["steps"][2]["risk_checks"]
            if row["aspect"] == "domain"
        )
        domain["status"] = "open"
        domain["evidence"] = "The domain compatibility has not been established."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("verified step has unresolved risk checks: domain" in error for error in errors),
            errors,
        )

    def test_side_conditions_field_cannot_be_omitted(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        del ledger["steps"][2]["side_conditions"]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("S003.side_conditions must be a list" in error for error in errors),
            errors,
        )

    def test_discharged_side_condition_needs_resolvable_evidence(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["side_conditions"] = [
            {
                "id": "SC001",
                "generated_by": "M001",
                "condition": "x belongs to the domain of equality.",
                "status": "discharged",
                "discharge": {
                    "sources": [
                        {
                            "kind": "premise",
                            "reference": "P999",
                            "contribution": (
                                "This intentionally unresolved premise would "
                                "supply the domain fact."
                            ),
                        }
                    ],
                    "rule": "Domain membership discharges the side condition.",
                    "evidence": "",
                },
            }
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("SC001 has unknown discharge premise P999" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("SC001 discharge evidence must be nonempty" in error for error in errors),
            errors,
        )

    def test_resolved_side_condition_passes(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["side_conditions"] = [
            {
                "id": "SC001",
                "generated_by": "M001",
                "condition": "x belongs to the domain of equality.",
                "status": "discharged",
                "discharge": {
                    "sources": [
                        {
                            "kind": "premise",
                            "reference": "P001",
                            "contribution": "P001 supplies the real-number domain.",
                        }
                    ],
                    "rule": "A real number lies in the domain of real equality.",
                    "evidence": "P001 records x as a real number.",
                },
            }
        ]
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

        cases = (
            ("condition", "S003.side_conditions[1].condition"),
            ("discharge_evidence", "SC001 discharge evidence"),
        )
        for case, expected in cases:
            with self.subTest(case=case):
                invalid_ledger = json.loads(json.dumps(ledger))
                side_condition = invalid_ledger["steps"][2]["side_conditions"][0]
                if case == "condition":
                    side_condition["condition"] = "N/A"
                else:
                    side_condition["discharge"]["evidence"] = "N/A"
                write_json(ledger_path, invalid_ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(
                    any(
                        expected in error
                        and (
                            "substantive" in error or "reserved placeholder" in error
                        )
                        for error in errors
                    ),
                    errors,
                )

    def test_side_condition_discharge_cannot_be_circular(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["side_conditions"] = [
            {
                "id": "SC001",
                "generated_by": "M001",
                "condition": "The move's own domain condition holds.",
                "status": "discharged",
                "discharge": {
                    "sources": [
                        {
                            "kind": "inference_move",
                            "reference": "M001",
                            "contribution": (
                                "This intentionally circular source repeats the "
                                "generating move."
                            ),
                        }
                    ],
                    "rule": "The generating move cannot discharge itself.",
                    "evidence": "This intentionally circular record is invalid.",
                },
            }
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("is not established before generating move M001" in error for error in errors),
            errors,
        )

    def test_conditional_step_requires_exact_cause_mapping(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = self.mark_s003_conditional(ledger)
        step["side_conditions"] = [
            {
                "id": "SC001",
                "generated_by": "M001",
                "condition": "Assume x lies in the required support.",
                "status": "open",
            }
        ]
        step["conditions"] = []
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("conditions must match every unresolved conditional cause" in error for error in errors),
            errors,
        )

    def test_conditional_step_with_exact_cause_mapping_passes(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = self.mark_s003_conditional(ledger)
        step["side_conditions"] = [
            {
                "id": "SC001",
                "generated_by": "M001",
                "condition": "Assume x lies in the required support.",
                "status": "open",
            }
        ]
        step["conditions"] = [
            {
                "kind": "side_condition",
                "reference": "SC001",
                "condition": "Validity is conditional on the stated support condition.",
            }
        ]
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_checkpoint_derives_partitions_and_preserves_resume_fields(self) -> None:
        complete_path = self.make_complete_audit()
        complete = read_json(complete_path)
        ledger_dir = complete_path.parent

        conditional = json.loads(json.dumps(complete))
        conditional["unit_id"] = "lem:conditional"
        conditional_step = self.mark_s003_conditional(conditional)
        conditional_step["side_conditions"] = [
            {
                "id": "SC001",
                "generated_by": "M001",
                "condition": "Assume x lies in the required support.",
                "status": "open",
            }
        ]
        conditional_step["conditions"] = [
            {
                "kind": "side_condition",
                "reference": "SC001",
                "condition": "Validity is conditional on the stated support condition.",
            }
        ]
        conditional_path = ledger_dir / "lem-conditional.ledger.json"
        write_json(conditional_path, conditional)
        self.seal_schema5_challenge(
            conditional_path, read_json(conditional_path)
        )

        for unit_id, filename in (
            ("lem:active", "lem-active.ledger.json"),
            ("lem:not-started", "lem-not-started.ledger.json"),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                proofcheck.cmd_extract(
                    argparse.Namespace(
                        file=self.paper,
                        start=2,
                        end=7,
                        statement_file=self.paper,
                        statement_start=2,
                        statement_end=4,
                        separate_statement_reason=None,
                        unit_id=unit_id,
                        output=ledger_dir / filename,
                        force=False,
                    )
                )
        active_path = ledger_dir / "lem-active.ledger.json"
        active = read_json(active_path)
        active["obligation"] = json.loads(json.dumps(complete["obligation"]))
        active["steps"] = [
            {
                "id": "S001",
                "lines": [2, 2],
                "kind": "other",
                "status": "non_substantive",
                "issue_ids": [],
            }
        ]
        write_json(active_path, active)
        not_started_path = ledger_dir / "lem-not-started.ledger.json"
        not_started = read_json(not_started_path)
        not_started["obligation"] = json.loads(
            json.dumps(complete["obligation"])
        )
        write_json(not_started_path, not_started)

        unit_ids = [
            "lem:main",
            "lem:conditional",
            "lem:active",
            "lem:not-started",
        ]
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        discovered = inventory["units"][0]
        for unit_id in unit_ids[1:]:
            added = json.loads(json.dumps(discovered))
            added["id"] = unit_id
            added["label"] = unit_id
            added["proof_association"]["target"] = unit_id
            inventory["units"].append(added)
        write_json(inventory_path, inventory)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["in_scope_units"] = unit_ids
        write_json(manifest_path, manifest)

        next_action = "Continue the atomic ledger for lem:active from source line 3."
        checkpoint_output = io.StringIO()
        with contextlib.redirect_stdout(checkpoint_output):
            status = proofcheck.cmd_checkpoint(
                argparse.Namespace(
                    root=self.audit,
                    active_unit="lem:active",
                    clear_active_unit=False,
                    next_action=next_action,
                )
            )

        progress = read_json(self.audit / "PROGRESS.json")
        self.assertEqual(0, status)
        self.assertEqual("lem:active", progress["active_unit"])
        self.assertEqual(next_action, progress["next_action"])
        self.assertEqual(4, progress["current_pass"])
        self.assertCountEqual(
            ["lem:main", "lem:conditional"], progress["completed_units"]
        )
        self.assertCountEqual(
            ["lem:conditional"], progress["conditional_units"]
        )
        self.assertCountEqual(["lem:active"], progress["in_progress_units"])
        self.assertCountEqual(
            ["lem:not-started"], progress["not_started_units"]
        )

    def test_checkpoint_status_and_issue_views_are_registered_in_cli(
        self,
    ) -> None:
        parser = proofcheck.build_parser()
        checkpoint = parser.parse_args(
            [
                "checkpoint",
                "--root",
                str(self.audit),
                "--active-unit",
                "lem:main",
                "--next-action",
                "Continue lem:main.",
            ]
        )
        status = parser.parse_args(
            ["status", "--root", str(self.audit), "--verbose"]
        )
        issues = parser.parse_args(
            [
                "issues",
                "--root",
                str(self.audit),
                "--write-summary",
                "--write-report-views",
                "--final",
            ]
        )
        revalidate = parser.parse_args(
            ["revalidate-protocol", "--root", str(self.audit)]
        )

        self.assertIs(proofcheck.cmd_checkpoint, checkpoint.func)
        self.assertEqual("lem:main", checkpoint.active_unit)
        self.assertFalse(checkpoint.clear_active_unit)
        self.assertTrue(status.verbose)
        self.assertIs(proofcheck.cmd_issues, issues.func)
        self.assertTrue(issues.write_summary)
        self.assertTrue(issues.write_report_views)
        self.assertTrue(issues.final)
        self.assertIs(proofcheck.cmd_revalidate_protocol, revalidate.func)

    def test_early_checkpoints_derive_passes_one_two_and_three(self) -> None:
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        observed_passes = []
        for expected_pass, transition in (
            (1, "scaffolded"),
            (2, "scope_reviewed"),
            (3, "map_reviewed"),
        ):
            if transition == "scope_reviewed":
                manifest = read_json(manifest_path)
                manifest["audit_scope"].update(
                    {
                        "status": "reviewed",
                        "depth": "focused",
                        "in_scope_units": ["lem:main"],
                        "target_units": ["lem:main"],
                        "critical_units": ["lem:main"],
                    }
                )
                write_json(manifest_path, manifest)
            elif transition == "map_reviewed":
                manifest = read_json(manifest_path)
                manifest["completion"]["inventory_reviewed"] = True
                manifest["completion"]["parser_warnings_reviewed"] = True
                write_json(manifest_path, manifest)
            with contextlib.redirect_stdout(io.StringIO()):
                proofcheck.cmd_checkpoint(
                    argparse.Namespace(
                        root=self.audit,
                        active_unit="lem:main",
                        clear_active_unit=False,
                        next_action=(
                            f"Continue the canonical work required for pass {expected_pass}."
                        ),
                    )
                )
            observed_passes.append(
                read_json(self.audit / "PROGRESS.json")["current_pass"]
            )

        self.assertEqual([1, 2, 3], observed_passes)

    def test_partially_normalized_ledger_cannot_advance_past_pass_three(
        self,
    ) -> None:
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"].update(
            {
                "status": "reviewed",
                "depth": "focused",
                "in_scope_units": ["lem:main"],
                "target_units": ["lem:main"],
                "critical_units": ["lem:main"],
            }
        )
        manifest["completion"]["inventory_reviewed"] = True
        manifest["completion"]["parser_warnings_reviewed"] = True
        write_json(manifest_path, manifest)

        ledger_path = (
            self.audit / "audit" / "04_local_checks" / "lem-main.ledger.json"
        )
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=self.paper,
                    start=2,
                    end=7,
                    statement_file=self.paper,
                    statement_start=2,
                    statement_end=4,
                    separate_statement_reason=None,
                    unit_id="lem:main",
                    output=ledger_path,
                    force=False,
                )
            )
        ledger = read_json(ledger_path)
        ledger["obligation"]["quantifier_scope"] = "For every real x."
        ledger["obligation"]["conclusion"] = "x equals x"
        ledger["steps"] = [
            {
                "id": "S001",
                "lines": [2, 2],
                "kind": "other",
                "status": "non_substantive",
                "issue_ids": [],
            }
        ]
        write_json(ledger_path, ledger)

        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_checkpoint(
                argparse.Namespace(
                    root=self.audit,
                    active_unit="lem:main",
                    clear_active_unit=False,
                    next_action="Finish normalizing every field of the locked obligation.",
                )
            )

        progress = read_json(self.audit / "PROGRESS.json")
        self.assertEqual(3, progress["current_pass"])
        self.assertCountEqual(["lem:main"], progress["in_progress_units"])

    def test_duplicate_step_dependency_fails(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        dependency = {
            "id": "S001",
            "kind": "step",
            "status": "verified",
            "needed_form": "The source-locked theorem obligation.",
            "compatibility_check": "S001 records exactly the obligation used here.",
        }
        step = ledger["steps"][2]
        step["dependencies"] = [dependency, dict(dependency)]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": "The theorem obligation is x equals x.",
                "origin": {"kind": "prior_step", "reference": "S001"},
                "evidence": "S001 is the prior source-locked statement row.",
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("duplicate dependency use S001" in error for error in errors),
            errors,
        )

    def test_dependency_must_be_used_by_a_premise(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["dependencies"] = [
            {
                "id": "S001",
                "kind": "step",
                "status": "verified",
                "needed_form": "The source-locked theorem obligation.",
                "compatibility_check": "The dependency is available but unused.",
            }
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("dependencies not used by premise_uses: S001" in error for error in errors),
            errors,
        )

    def test_review_cannot_list_an_unused_direct_dependency(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["review"]["direct_dependencies"] = [
            {
                "id": "lem:unused",
                "use_id": "D001",
                "kind": "internal_result",
                "conclusion_id": "C001",
                "status": "verified",
                "needed_form": "An unused result.",
                "compatibility_check": "No proof step actually invokes it.",
            }
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("direct_dependencies contains unused results" in error for error in errors),
            errors,
        )

    def test_normalization_matrix_requires_exact_aspect_coverage(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["normalization_checks"] = [
            row
            for row in ledger["obligation"]["normalization_checks"]
            if row["aspect"] != "regime"
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("normalization_checks must contain each required aspect exactly once" in error for error in errors),
            errors,
        )

    def test_verified_contract_rejects_unclear_normalization(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["uniformity"] = "unclear"
        uniformity = next(
            row for row in ledger["obligation"]["normalization_checks"]
            if row["aspect"] == "uniformity"
        )
        uniformity["status"] = "unclear"
        uniformity["evidence"] = "The statement does not determine uniformity."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("verified contract fidelity has unresolved normalization checks" in error for error in errors),
            errors,
        )

    def test_not_applicable_normalization_requires_explicit_absence(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["probability_model"] = (
            "Independent observations follow a common distribution P."
        )
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "normalization_checks[probability_model] is not_applicable "
                "but obligation.probability_model is substantive" in error
                for error in errors
            ),
            errors,
        )


    def test_explicit_absence_requires_not_applicable_normalization(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        cases = (
            ("probability_model", "N/A."),
            ("hypotheses", ["N/A"]),
            ("definitions", ["none"]),
            ("uniformity", "not_applicable"),
            ("regime", "not applicable"),
            ("constant_dependencies", ["not-applicable"]),
        )
        for aspect, marker in cases:
            with self.subTest(aspect=aspect):
                ledger = json.loads(json.dumps(base_ledger))
                ledger["obligation"][aspect] = marker
                normalization = next(
                    item
                    for item in ledger["obligation"]["normalization_checks"]
                    if item["aspect"] == aspect
                )
                normalization["status"] = "checked"
                normalization["evidence"] = (
                    "This intentionally inconsistent record is rejected."
                )
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                expected = (
                    f"obligation.normalization_checks[{aspect}] is 'checked' "
                    f"but obligation.{aspect} records only absence"
                )
                self.assertTrue(
                    any(expected in error for error in errors),
                    errors,
                )

    def test_checked_normalization_rejects_embedded_absence_marker(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["definitions"].append("N/A")
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "obligation.definitions[2] cannot use an absence marker "
                "unless the field is not_applicable" in error
                for error in errors
            ),
            errors,
        )

    def test_conditional_contract_rejects_unclear_normalization(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        self.mark_s003_conditional(ledger)
        ledger["review"]["contract_fidelity"] = "conditionally_verified"
        ledger["obligation"]["uniformity"] = "unclear"
        uniformity = next(
            row for row in ledger["obligation"]["normalization_checks"]
            if row["aspect"] == "uniformity"
        )
        uniformity["status"] = "unclear"
        uniformity["evidence"] = "The source does not determine uniformity."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "conditionally_verified contract fidelity has unresolved "
                "normalization checks" in error
                for error in errors
            ),
            errors,
        )

    def test_failed_zero_input_move_requires_structured_failure(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        step["premise_uses"] = []
        step["inference"]["moves"][0]["premise_ids"] = []
        step["status"] = "gap"
        step["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "gap"
        ledger["review"]["argument_status"] = "gap"
        ledger["review"]["statement_status"] = "not_established"
        ledger["independent_check"]["challenger_verdict"] = "gap"
        ledger["independent_check"]["reconciled_verdict"] = "gap"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("zero-input failed move requires" in error for error in errors),
            errors,
        )

    def test_failed_zero_input_move_with_issue_link_passes(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        step["premise_uses"] = []
        move = step["inference"]["moves"][0]
        move["premise_ids"] = []
        move["rule"] = "Unsupported source assertion"
        move["justification"] = (
            "The source supplies no premise from which the conclusion follows."
        )
        move["failure"] = {
            "kind": "unsupported_assertion",
            "issue_id": "I-001",
            "evidence": (
                "The conclusion is asserted without a load-bearing premise."
            ),
        }
        step["status"] = "gap"
        step["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "gap"
        ledger["review"]["argument_status"] = "gap"
        ledger["review"]["statement_status"] = "not_established"
        result = ledger["review"]["conclusion_results"][0]
        result["argument_status"] = "gap"
        result["statement_status"] = "not_established"
        result["issue_ids"] = ["I-001"]
        ledger["independent_check"]["challenger_verdict"] = "gap"
        ledger["independent_check"]["reconciled_verdict"] = "gap"
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

        move["failure"]["evidence"] = "N/A"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "failure.evidence must be nonempty and substantive" in error
                for error in errors
            ),
            errors,
        )

    def test_direct_dependency_must_exactly_mirror_step_record(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        dependency = {
            "id": "lem:prior",
            "use_id": "D001",
            "kind": "internal_result",
            "conclusion_id": "C001",
            "status": "verified",
            "needed_form": "The imported result gives x equals x.",
            "compatibility_check": "The result has the same domain and conclusion.",
        }
        step = ledger["steps"][2]
        step["dependencies"] = [dependency]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": dependency["needed_form"],
                "origin": {
                    "kind": "internal_result",
                    "reference": "D001",
                },
                "evidence": "The dependency supplies exactly the recorded form.",
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        direct_dependency = dict(dependency)
        direct_dependency["needed_form"] = "A different imported conclusion."
        ledger["review"]["direct_dependencies"] = [direct_dependency]
        ledger["review"]["conclusion_results"][0]["dependency_use_ids"] = [
            "D001"
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "needed_form differs from review.direct_dependencies" in error
                for error in errors
            ),
            errors,
        )

    def test_source_reference_anchor_must_contain_exact_label(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["context_spans"].append(
            proofcheck.locked_span(
                self.definitions,
                1,
                1,
                ledger_path.parent,
                role="unrelated definition",
            )
        )
        premise = ledger["steps"][2]["premise_uses"][0]
        premise["origin"]["anchor"] = {
            "kind": "context_span",
            "index": 1,
        }
        premise["source_reference_id"] = "eq:reflexive"
        disposition = ledger["review"]["source_reference_dispositions"][0]
        premise["source_reference_occurrence_id"] = disposition["occurrence_id"]
        disposition["disposition"] = "obligation_context"
        disposition["premise_links"] = [
            {
                "step_id": "S003",
                "premise_id": "P001",
            }
        ]
        disposition["evidence"] = (
            "This link intentionally points to an unrelated locked span."
        )
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("is not contained in its locked anchor" in error for error in errors),
            errors,
        )

    def test_missing_premise_cannot_support_refuted_status(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        step["premise_uses"] = []
        move = step["inference"]["moves"][0]
        move["premise_ids"] = []
        move["failure"] = {
            "kind": "missing_premise",
            "issue_id": "I-001",
            "evidence": "A required load-bearing premise is absent.",
        }
        step["status"] = "incorrect"
        step["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "incorrect"
        ledger["review"]["argument_status"] = "invalid"
        ledger["review"]["statement_status"] = "refuted"
        result = ledger["review"]["conclusion_results"][0]
        result["argument_status"] = "invalid"
        result["statement_status"] = "refuted"
        result["issue_ids"] = ["I-001"]
        ledger["independent_check"]["challenger_verdict"] = "incorrect"
        ledger["independent_check"]["reconciled_verdict"] = "incorrect"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("missing_premise requires step status gap" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("counterexample or contradiction" in error for error in errors),
            errors,
        )

    def test_counterexample_failure_can_support_refuted_status(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        step["premise_uses"] = []
        step["restatement"] = "The recorded witness violates the conclusion."
        move = step["inference"]["moves"][0]
        move["claim"] = step["restatement"]
        move["premise_ids"] = []
        move["rule"] = "Counterexample"
        move["justification"] = "The recorded witness directly violates the claim."
        move["failure"] = {
            "kind": "counterexample",
            "issue_id": "I-001",
            "evidence": "Record the exact witness and evaluate both sides.",
            "target": ledger["obligation"]["conclusion"],
        }
        step["status"] = "incorrect"
        step["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "incorrect"
        ledger["review"]["argument_status"] = "invalid"
        ledger["review"]["statement_status"] = "refuted"
        result = ledger["review"]["conclusion_results"][0]
        result["argument_status"] = "invalid"
        result["statement_status"] = "refuted"
        result["issue_ids"] = ["I-001"]
        ledger["independent_check"]["challenger_verdict"] = "incorrect"
        ledger["independent_check"]["reconciled_verdict"] = "incorrect"
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_malformed_failure_kind_is_rejected_without_crashing(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        step["premise_uses"] = []
        move = step["inference"]["moves"][0]
        move["premise_ids"] = []
        move["failure"] = {
            "kind": [],
            "issue_id": "I-001",
            "evidence": "This malformed record must be rejected safely.",
        }
        step["status"] = "incorrect"
        step["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "incorrect"
        ledger["review"]["argument_status"] = "invalid"
        ledger["review"]["statement_status"] = "refuted"
        ledger["independent_check"]["challenger_verdict"] = "incorrect"
        ledger["independent_check"]["reconciled_verdict"] = "incorrect"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("failure.kind is invalid" in error for error in errors),
            errors,
        )

    def test_mandatory_obligation_fields_reject_absence_markers(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        cases = (
            ("quantifier_scope", "obligation.quantifier_scope"),
            ("conclusion", "obligation.conclusion"),
            ("quantified_variable_domain", "quantified_variables[1].domain"),
        )
        for case, expected_field in cases:
            with self.subTest(case=case):
                ledger = json.loads(json.dumps(base_ledger))
                if case == "quantified_variable_domain":
                    ledger["obligation"]["quantified_variables"][0]["domain"] = (
                        "not applicable"
                    )
                else:
                    ledger["obligation"][case] = "not applicable"
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(
                    any(
                        f"{expected_field} cannot use an absence marker" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_normalized_obligation_rejects_unresolved_placeholders(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        cases = (
            (("quantifier_scope",), "TODO: fill this in", "obligation.quantifier_scope"),
            (("probability_model",), "**unknown**", "obligation.probability_model"),
            (("conclusion",), "`TBD`", "obligation.conclusion"),
            (("hypotheses", 0), r"\texttt{TODO}", "obligation.hypotheses[1]"),
            (("definitions", 0), r"\texttt{TODO}", "obligation.definitions[1]"),
            (
                ("constant_dependencies", 0),
                "TBD?",
                "obligation.constant_dependencies[1]",
            ),
            (
                ("quantified_variables", 0, "symbol"),
                r"\texttt{TODO}",
                "obligation.quantified_variables[1].symbol",
            ),
            (
                ("quantified_variables", 0, "type"),
                "TODO: fill this in",
                "obligation.quantified_variables[1].type",
            ),
            (
                ("quantified_variables", 0, "domain"),
                r"\texttt{TODO}",
                "obligation.quantified_variables[1].domain",
            ),
            (
                ("quantifier_scope",),
                "unknown: fill this in",
                "obligation.quantifier_scope",
            ),
            (
                ("conclusion",),
                "unresolved: verify later",
                "obligation.conclusion",
            ),
            (
                ("definitions", 0),
                "pending: author response",
                "obligation.definitions[1]",
            ),
            (
                ("quantified_variables", 0, "symbol"),
                "not checked: run audit",
                "obligation.quantified_variables[1].symbol",
            ),
            (
                ("quantifier_scope",),
                "unknown\uFF1Afill this in",
                "obligation.quantifier_scope",
            ),
            (
                ("quantified_variables", 0, "symbol"),
                "not  checked: run audit",
                "obligation.quantified_variables[1].symbol",
            ),
            (
                ("quantifier_scope",),
                "unknown\u2236fill this in",
                "obligation.quantifier_scope",
            ),
            (
                ("conclusion",),
                "unknown\uFE13fill this in",
                "obligation.conclusion",
            ),
            (
                ("definitions", 0),
                "unknown\u02D0fill this in",
                "obligation.definitions[1]",
            ),
            (
                ("quantified_variables", 0, "symbol"),
                "not\u200Bchecked: run audit",
                "obligation.quantified_variables[1].symbol",
            ),
            (
                ("quantified_variables", 0, "type"),
                "not\u2060checked: run audit",
                "obligation.quantified_variables[1].type",
            ),
            (
                ("quantifier_scope",),
                "unknown\uFE0F: fill this in",
                "obligation.quantifier_scope",
            ),
            (
                ("conclusion",),
                "unk\u034Fnown: fill this in",
                "obligation.conclusion",
            ),
        )
        for path, marker, expected_field in cases:
            with self.subTest(path=path, marker=marker):
                ledger = json.loads(json.dumps(base_ledger))
                target = ledger["obligation"]
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = marker
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(
                    any(
                        f"{expected_field} cannot use an unresolved placeholder"
                        in error
                        for error in errors
                    ),
                    errors,
                )

    def test_statistical_unknown_phrases_are_not_placeholders(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        phrases = (
            "Unknown (but fixed) parameter theta lies in Theta.",
            "Unknown-variance Gaussian errors have finite fourth moment.",
        )
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                ledger = json.loads(json.dumps(base_ledger))
                ledger["obligation"]["hypotheses"] = [phrase]
                normalization = next(
                    item
                    for item in ledger["obligation"]["normalization_checks"]
                    if item["aspect"] == "hypotheses"
                )
                normalization["status"] = "checked"
                normalization["evidence"] = (
                    "The statistical hypothesis is stated explicitly."
                )
                write_json(ledger_path, ledger)
                self.seal_schema5_challenge(
                    ledger_path, read_json(ledger_path)
                )
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertEqual([], errors)

    def test_commented_label_cannot_satisfy_source_anchor(self) -> None:
        ledger_path = self.make_complete_audit()
        self.definitions.write_text(
            "% \\label{eq:reflexive}\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger = read_json(ledger_path)
        ledger["obligation"]["context_spans"].append(
            proofcheck.locked_span(
                self.definitions,
                1,
                1,
                ledger_path.parent,
                role="commented label",
            )
        )
        premise = ledger["steps"][2]["premise_uses"][0]
        premise["origin"]["anchor"] = {
            "kind": "context_span",
            "index": 1,
        }
        premise["source_reference_id"] = "eq:reflexive"
        disposition = ledger["review"]["source_reference_dispositions"][0]
        premise["source_reference_occurrence_id"] = disposition["occurrence_id"]
        disposition["disposition"] = "obligation_context"
        disposition["premise_links"] = [
            {
                "step_id": "S003",
                "premise_id": "P001",
            }
        ]
        disposition["evidence"] = "The only apparent label is commented out."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("is not contained in its locked anchor" in error for error in errors),
            errors,
        )

    def test_direct_dependency_compatibility_check_must_match(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        dependency = {
            "id": "lem:prior",
            "use_id": "D001",
            "kind": "internal_result",
            "conclusion_id": "C001",
            "status": "verified",
            "needed_form": "The imported result gives x equals x.",
            "compatibility_check": "The result has the same domain and conclusion.",
        }
        step = ledger["steps"][2]
        step["dependencies"] = [dependency]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": dependency["needed_form"],
                "origin": {
                    "kind": "internal_result",
                    "reference": "D001",
                },
                "evidence": "The dependency supplies exactly the recorded form.",
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        direct_dependency = dict(dependency)
        direct_dependency["compatibility_check"] = (
            "A different compatibility assessment."
        )
        ledger["review"]["direct_dependencies"] = [direct_dependency]
        ledger["review"]["conclusion_results"][0]["dependency_use_ids"] = [
            "D001"
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "compatibility_check differs from review.direct_dependencies"
                in error
                for error in errors
            ),
            errors,
        )

    def test_local_enum_fields_reject_unhashable_values(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        paths = (
            ("source.coverage_mode", ("source", "coverage_mode")),
            (
                "obligation.quantifier",
                ("obligation", "quantified_variables", 0, "quantifier"),
            ),
            (
                "obligation.normalization.status",
                ("obligation", "normalization_checks", 0, "status"),
            ),
            ("obligation.uniformity", ("obligation", "uniformity")),
            ("obligation.regime", ("obligation", "regime")),
            ("independent.status", ("independent_check", "status")),
            (
                "independent.level",
                ("independent_check", "independence_level"),
            ),
            (
                "independent.challenger",
                ("independent_check", "challenger_verdict"),
            ),
            (
                "independent.reconciled",
                ("independent_check", "reconciled_verdict"),
            ),
            ("premise.role", ("steps", 2, "premise_uses", 0, "role")),
            (
                "premise.origin.kind",
                ("steps", 2, "premise_uses", 0, "origin", "kind"),
            ),
            (
                "premise.anchor.kind",
                (
                    "steps",
                    2,
                    "premise_uses",
                    0,
                    "origin",
                    "anchor",
                    "kind",
                ),
            ),
            ("step.kind", ("steps", 2, "kind")),
            ("step.status", ("steps", 2, "status")),
            (
                "step.atomicity",
                ("steps", 2, "checks", "atomicity", "status"),
            ),
            ("review.unit", ("review", "unit_status")),
            ("review.contract", ("review", "contract_fidelity")),
            ("review.dependency", ("review", "dependency_closure")),
            ("review.argument", ("review", "argument_status")),
            ("review.statement", ("review", "statement_status")),
            ("review.use", ("review", "use_site_sufficiency")),
            (
                "review.source_disposition",
                ("review", "source_reference_dispositions", 0, "disposition"),
            ),
            (
                "review.citation_disposition",
                ("review", "citation_dispositions", 0, "disposition"),
            ),
            ("risk.status", ("steps", 2, "risk_checks", 0, "status")),
        )
        for name, path in paths:
            with self.subTest(field=name):
                ledger = json.loads(json.dumps(base_ledger))
                cursor = ledger
                for token in path[:-1]:
                    cursor = cursor[token]
                cursor[path[-1]] = []
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(errors)

    def test_nested_enum_fields_reject_unhashable_values(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        dependency = {
            "id": "lem:prior",
            "use_id": "D001",
            "kind": "internal_result",
            "conclusion_id": "C001",
            "status": "verified",
            "needed_form": "The imported result gives x equals x.",
            "compatibility_check": "The domains and conclusion agree.",
        }
        cases = (
            "step_dependency_kind",
            "step_dependency_status",
            "direct_dependency_kind",
            "direct_dependency_status",
            "side_condition_status",
            "discharge_kind",
            "condition_kind",
        )
        for case in cases:
            with self.subTest(case=case):
                ledger = json.loads(json.dumps(base_ledger))
                step = ledger["steps"][2]
                if case.startswith("step_dependency"):
                    record = dict(dependency)
                    record[case.rsplit("_", 1)[1]] = []
                    step["dependencies"] = [record]
                elif case.startswith("direct_dependency"):
                    record = dict(dependency)
                    record[case.rsplit("_", 1)[1]] = []
                    ledger["review"]["direct_dependencies"] = [record]
                elif case == "side_condition_status":
                    step["side_conditions"] = [
                        {
                            "id": "SC001",
                            "generated_by": "M001",
                            "condition": "A test condition.",
                            "status": [],
                        }
                    ]
                elif case == "discharge_kind":
                    step["side_conditions"] = [
                        {
                            "id": "SC001",
                            "generated_by": "M001",
                            "condition": "A test condition.",
                            "status": "discharged",
                            "discharge": {
                                "sources": [
                                    {
                                        "kind": [],
                                        "reference": "P001",
                                        "contribution": (
                                            "The malformed source would supply "
                                            "the domain premise."
                                        ),
                                    }
                                ],
                                "rule": "The domain premise discharges the condition.",
                                "evidence": "A malformed discharge kind.",
                            },
                        }
                    ]
                else:
                    step["conditions"] = [
                        {
                            "kind": [],
                            "reference": "domain",
                            "condition": "A malformed cause kind.",
                        }
                    ]
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(errors)

    def test_malformed_move_links_return_errors_without_crashing(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        for case in ("conclusion_move", "generated_by", "discharge_reference"):
            with self.subTest(case=case):
                ledger = json.loads(json.dumps(base_ledger))
                step = ledger["steps"][2]
                if case == "conclusion_move":
                    step["inference"]["conclusion_move"] = []
                else:
                    step["side_conditions"] = [
                        {
                            "id": "SC001",
                            "generated_by": [] if case == "generated_by" else "M001",
                            "condition": "A malformed link.",
                            "status": "discharged",
                            "discharge": {
                                "sources": [
                                    {
                                        "kind": "inference_move",
                                        "reference": (
                                            []
                                            if case == "discharge_reference"
                                            else "M001"
                                        ),
                                        "contribution": (
                                            "The source is intentionally malformed "
                                            "for this negative control."
                                        ),
                                    }
                                ],
                                "rule": "Only an earlier move may discharge the condition.",
                                "evidence": "This malformed link must be rejected.",
                            },
                        }
                    ]
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(errors)

    def test_malformed_obligation_span_lists_do_not_crash(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        for field in ("statement_spans", "context_spans"):
            for bad_value in (None, 1, True):
                with self.subTest(field=field, value=bad_value):
                    ledger = json.loads(json.dumps(base_ledger))
                    ledger["obligation"][field] = bad_value
                    write_json(ledger_path, ledger)
                    errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                    self.assertTrue(errors)

    def test_n_a_marker_is_rejected_in_mandatory_obligation_fields(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        cases = (
            ("quantifier_scope", "obligation.quantifier_scope"),
            ("conclusion", "obligation.conclusion"),
            ("quantified_variable_domain", "quantified_variables[1].domain"),
        )
        for case, expected_field in cases:
            with self.subTest(case=case):
                ledger = json.loads(json.dumps(base_ledger))
                if case == "quantified_variable_domain":
                    ledger["obligation"]["quantified_variables"][0]["domain"] = "N/A"
                else:
                    ledger["obligation"][case] = "N/A"
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(
                    any(
                        f"{expected_field} cannot use an absence marker" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_reserved_bare_markers_are_not_substantive(self) -> None:
        markers = (
            "none",
            "N/A",
            "N/A.",
            "*N/A*",
            "**N/A**",
            "---N/A---",
            "not applicable",
            "not-applicable",
            "not_applicable",
            "unclear",
            "unknown",
            "***unknown***",
            "unresolved",
            "TBD",
            "TBD?",
            "TODO: fill this in",
            "TODO",
            "`TODO`",
            "_TODO_",
            "\\text{TODO}",
            "**\\text{TODO}**",
            "pending",
            "(pending)",
            "not checked",
            "not_checked",
        )
        for marker in markers:
            with self.subTest(marker=marker):
                self.assertFalse(proofcheck.is_substantive_string(marker))

    def test_marker_normalization_removes_visual_blank_characters(self) -> None:
        codepoints = (
            0x115F,
            0x1160,
            0x17B4,
            0x17B5,
            0x2800,
            0x3164,
            0xFFA0,
        )
        for codepoint in codepoints:
            with self.subTest(codepoint=hex(codepoint)):
                marker = f"unk{chr(codepoint)}nown: fill this in"
                self.assertEqual(
                    "unknown: fill this in",
                    proofcheck.normalized_marker(marker),
                )
                self.assertTrue(
                    proofcheck.is_forbidden_contract_placeholder(marker)
                )

    def test_structured_obligation_pointer_cannot_supply_arbitrary_claim(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        premise = ledger["steps"][2]["premise_uses"][0]
        premise["claim"] = "The Moon is made of green cheese."
        premise["origin"]["reference"] = "/quantified_variables/0"
        premise["evidence"] = "This arbitrary claim is intentionally invalid."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "obligation premise must resolve to one concrete item" in error
                for error in errors
            ),
            errors,
        )

    def test_inactive_conditional_label_cannot_satisfy_source_anchor(self) -> None:
        ledger_path = self.make_complete_audit()
        self.definitions.write_text(
            "\\iffalse\n"
            "\\label{eq:reflexive}\n"
            "\\fi\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger = read_json(ledger_path)
        ledger["obligation"]["context_spans"].append(
            proofcheck.locked_span(
                self.definitions,
                1,
                3,
                ledger_path.parent,
                role="inactive label",
            )
        )
        premise = ledger["steps"][2]["premise_uses"][0]
        premise["origin"]["anchor"] = {
            "kind": "context_span",
            "index": 1,
        }
        premise["source_reference_id"] = "eq:reflexive"
        disposition = ledger["review"]["source_reference_dispositions"][0]
        premise["source_reference_occurrence_id"] = disposition["occurrence_id"]
        disposition["disposition"] = "obligation_context"
        disposition["premise_links"] = [
            {
                "step_id": "S003",
                "premise_id": "P001",
            }
        ]
        disposition["evidence"] = "The only matching label is inactive."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("is not contained in its locked anchor" in error for error in errors),
            errors,
        )

    def test_unknown_and_unless_conditional_labels_are_not_treated_as_active(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        for conditional in ("\\ifcustom", "\\unless\\iftrue"):
            with self.subTest(conditional=conditional):
                self.definitions.write_text(
                    f"{conditional}\n"
                    "\\label{eq:reflexive}\n"
                    "\\fi\n",
                    encoding="utf-8",
                    newline="\n",
                )
                ledger = json.loads(json.dumps(base_ledger))
                ledger["obligation"]["context_spans"].append(
                    proofcheck.locked_span(
                        self.definitions,
                        1,
                        3,
                        ledger_path.parent,
                        role="unresolved conditional label",
                    )
                )
                premise = ledger["steps"][2]["premise_uses"][0]
                premise["origin"]["anchor"] = {
                    "kind": "context_span",
                    "index": 1,
                }
                premise["source_reference_id"] = "eq:reflexive"
                disposition = ledger["review"]["source_reference_dispositions"][0]
                premise["source_reference_occurrence_id"] = disposition[
                    "occurrence_id"
                ]
                disposition["disposition"] = "obligation_context"
                disposition["premise_links"] = [
                    {
                        "step_id": "S003",
                        "premise_id": "P001",
                    }
                ]
                disposition["evidence"] = "The matching label is not statically active."
                write_json(ledger_path, ledger)
                self.seal_schema5_challenge(
                    ledger_path, read_json(ledger_path)
                )
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(
                    any(
                        "is not contained in its locked anchor" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_nonexecuting_label_tokens_cannot_satisfy_source_anchor(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        cases = (
            (
                "newcommand",
                "\\newcommand{\\ghost}{\\label{eq:reflexive}}\n",
            ),
            (
                "conditional newcommand",
                "\\newcommand{\\ghost}{\\iftrue\\label{eq:reflexive}\\fi}\n",
            ),
            (
                "multiline newcommand",
                "\\newcommand{\\ghost}{%\n"
                "  \\label{eq:reflexive}\n"
                "}\n",
            ),
            (
                "primitive definition",
                "\\def\\ghost{\\label{eq:reflexive}}\n",
            ),
            (
                "document command",
                "\\NewDocumentCommand{\\ghost}{m}{\\label{eq:reflexive}}\n",
            ),
            (
                "latex3 command definition",
                "\\cs_new:Npn \\ghost:n #1 {\\label{eq:reflexive}}\n",
            ),
            (
                "latex3 protected command definition",
                "\\cs_new_protected:Npn \\ghost:n #1 "
                "{\\label{eq:reflexive}}\n",
            ),
            (
                "new document environment",
                "\\NewDocumentEnvironment{ghost}{}"
                "{\\label{eq:reflexive}}{}\n",
            ),
            (
                "renewed document environment",
                "\\RenewDocumentEnvironment{ghost}{}"
                "{\\label{eq:reflexive}}{}\n",
            ),
            (
                "paired delimiter definition",
                "\\DeclarePairedDelimiter{\\ghost}"
                "{\\label{eq:reflexive}}{\\rvert}\n",
            ),
            (
                "theorem definition",
                "\\newtheorem{ghost}{Title \\label{eq:reflexive}}\n",
            ),
            (
                "inline verb",
                "\\verb|\\label{eq:reflexive}|\n",
            ),
            (
                "verbatim environment",
                "\\begin{verbatim}\n"
                "\\label{eq:reflexive}\n"
                "\\end{verbatim}\n",
            ),
        )
        for case, source_text in cases:
            with self.subTest(case=case):
                self.definitions.write_text(
                    source_text,
                    encoding="utf-8",
                    newline="\n",
                )
                ledger = json.loads(json.dumps(base_ledger))
                end_line = len(source_text.splitlines())
                ledger["obligation"]["context_spans"].append(
                    proofcheck.locked_span(
                        self.definitions,
                        1,
                        end_line,
                        ledger_path.parent,
                        role="nonexecuting label token",
                    )
                )
                premise = ledger["steps"][2]["premise_uses"][0]
                premise["origin"]["anchor"] = {
                    "kind": "context_span",
                    "index": 1,
                }
                premise["source_reference_id"] = "eq:reflexive"
                disposition = ledger["review"]["source_reference_dispositions"][0]
                premise["source_reference_occurrence_id"] = disposition[
                    "occurrence_id"
                ]
                disposition["disposition"] = "obligation_context"
                disposition["premise_links"] = [
                    {
                        "step_id": "S003",
                        "premise_id": "P001",
                    }
                ]
                disposition["evidence"] = (
                    "The matching token occurs only in nonexecuting TeX."
                )
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(
                    any(
                        "is not contained in its locked anchor" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_label_after_command_definition_remains_active(self) -> None:
        ledger_path = self.make_complete_audit()
        self.definitions.write_text(
            "\\newcommand{\\ghost}{\\label{eq:inactive}}\n"
            "\\label{eq:reflexive}\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger = read_json(ledger_path)
        ledger["obligation"]["context_spans"].append(
            proofcheck.locked_span(
                self.definitions,
                1,
                2,
                ledger_path.parent,
                role="active label after a definition",
            )
        )
        premise = ledger["steps"][2]["premise_uses"][0]
        premise["origin"]["anchor"] = {
            "kind": "context_span",
            "index": 1,
        }
        premise["source_reference_id"] = "eq:reflexive"
        disposition = ledger["review"]["source_reference_dispositions"][0]
        premise["source_reference_occurrence_id"] = disposition["occurrence_id"]
        disposition["disposition"] = "obligation_context"
        disposition["premise_links"] = [
            {
                "step_id": "S003",
                "premise_id": "P001",
            }
        ]
        disposition["evidence"] = "The label after the definition is active."
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_label_after_extended_definition_families_remains_active(self) -> None:
        definitions = (
            (
                "latex3 command",
                "\\cs_new:Npn \\ghost:n #1 {\\label{eq:inactive}}\n",
            ),
            (
                "latex3 protected command",
                "\\cs_new_protected:Npn \\ghost:n #1 "
                "{\\label{eq:inactive}}\n",
            ),
            (
                "new document environment",
                "\\NewDocumentEnvironment{ghost}{}"
                "{\\label{eq:inactive}}{}\n",
            ),
            (
                "renewed document environment",
                "\\RenewDocumentEnvironment{ghost}{}"
                "{\\label{eq:inactive}}{}\n",
            ),
            (
                "paired delimiter",
                "\\DeclarePairedDelimiter{\\ghost}"
                "{\\label{eq:inactive}}{\\rvert}\n",
            ),
            (
                "theorem definition",
                "\\newtheorem{ghost}{Title \\label{eq:inactive}}\n",
            ),
        )
        for case, definition in definitions:
            with self.subTest(case=case):
                source_text = definition + "\\label{eq:reflexive}\n"
                self.definitions.write_text(
                    source_text, encoding="utf-8", newline="\n"
                )
                span = proofcheck.locked_span(
                    self.definitions,
                    1,
                    len(source_text.splitlines()),
                    self.base,
                )
                self.assertTrue(
                    proofcheck.locked_span_contains_label(
                        span, self.base, "eq:reflexive"
                    )
                )

    def test_refutation_requires_exact_target_and_verified_contract(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        step = base_ledger["steps"][2]
        step["premise_uses"] = []
        step["restatement"] = "The recorded witness violates the conclusion."
        move = step["inference"]["moves"][0]
        move["claim"] = step["restatement"]
        move["premise_ids"] = []
        move["rule"] = "Counterexample"
        move["justification"] = "The recorded witness directly violates the claim."
        move["failure"] = {
            "kind": "counterexample",
            "issue_id": "I-001",
            "target": base_ledger["obligation"]["conclusion"],
            "evidence": "Record the exact witness and evaluate both sides.",
        }
        step["status"] = "incorrect"
        step["issue_ids"] = ["I-001"]
        base_ledger["review"]["unit_status"] = "incorrect"
        base_ledger["review"]["argument_status"] = "invalid"
        base_ledger["review"]["statement_status"] = "refuted"
        result = base_ledger["review"]["conclusion_results"][0]
        result["argument_status"] = "invalid"
        result["statement_status"] = "refuted"
        result["issue_ids"] = ["I-001"]
        base_ledger["independent_check"]["challenger_verdict"] = "incorrect"
        base_ledger["independent_check"]["reconciled_verdict"] = "incorrect"

        cases = ("missing_target", "wrong_target", "unclear_contract")
        for case in cases:
            with self.subTest(case=case):
                ledger = json.loads(json.dumps(base_ledger))
                failure = ledger["steps"][2]["inference"]["moves"][0]["failure"]
                if case == "missing_target":
                    del failure["target"]
                elif case == "wrong_target":
                    failure["target"] = "An unrelated theorem."
                else:
                    ledger["review"]["contract_fidelity"] = "unclear"
                    ledger["review"]["conclusion_results"][0][
                        "contract_fidelity"
                    ] = "unclear"
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                if case == "unclear_contract":
                    expected = "requires verified contract fidelity"
                else:
                    expected = "refutation target must exactly match"
                self.assertTrue(
                    any(expected in error for error in errors),
                    errors,
                )

    def test_prior_step_dependency_is_bound_to_prior_restatement(self) -> None:
        ledger_path = self.make_complete_audit()
        valid_ledger = read_json(ledger_path)
        prior = valid_ledger["steps"][0]
        prior["kind"] = "setup"
        prior["restatement"] = "x is fixed as a real number."
        dependency = {
            "id": "S001",
            "kind": "step",
            "status": "verified",
            "needed_form": prior["restatement"],
            "compatibility_check": "The same x is used in the conclusion step.",
        }
        step = valid_ledger["steps"][2]
        step["dependencies"] = [dependency]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": dependency["needed_form"],
                "origin": {
                    "kind": "prior_step",
                    "reference": "S001",
                },
                "evidence": "S001 supplies this exact setup claim.",
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        write_json(ledger_path, valid_ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

        invalid_ledger = json.loads(json.dumps(valid_ledger))
        invalid_dependency = invalid_ledger["steps"][2]["dependencies"][0]
        invalid_dependency["needed_form"] = "The Moon is made of green cheese."
        invalid_premise = invalid_ledger["steps"][2]["premise_uses"][1]
        invalid_premise["claim"] = invalid_dependency["needed_form"]
        write_json(ledger_path, invalid_ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "needed_form must exactly match the prior step restatement" in error
                for error in errors
            ),
            errors,
        )

    def test_reserved_placeholders_cannot_form_a_prior_step_chain(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        prior = ledger["steps"][0]
        prior["kind"] = "setup"
        prior["restatement"] = "N/A"
        dependency = {
            "id": "S001",
            "kind": "step",
            "status": "verified",
            "needed_form": "N/A",
            "compatibility_check": "N/A",
        }
        step = ledger["steps"][2]
        step["dependencies"] = [dependency]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": "N/A",
                "origin": {
                    "kind": "prior_step",
                    "reference": "S001",
                },
                "evidence": "N/A",
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        expected_fragments = (
            "S001: substantive step needs a restatement",
            ".needed_form must state the exact form used",
            ".compatibility_check must map the result to this use",
            ".claim must be a nonempty string",
            ".evidence must be a nonempty string",
        )
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertTrue(
                    any(
                        fragment in error and "reserved placeholder" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_reserved_placeholders_are_rejected_across_evidence_fields(self) -> None:
        ledger_path = self.make_complete_audit()
        base_ledger = read_json(ledger_path)
        cases = (
            (
                "normalization evidence",
                lambda value: value["obligation"]["normalization_checks"][0].__setitem__(
                    "evidence", "N/A"
                ),
                "obligation.normalization_checks[1].evidence",
            ),
            (
                "risk evidence",
                lambda value: value["steps"][2]["risk_checks"][0].__setitem__("evidence", "N/A"),
                "S003.risk_checks[1].evidence",
            ),
            (
                "premise evidence",
                lambda value: value["steps"][2]["premise_uses"][0].__setitem__("evidence", "N/A"),
                "S003.premise_uses[1].evidence",
            ),
            (
                "source-reference evidence",
                lambda value: value["review"]["source_reference_dispositions"][0].__setitem__(
                    "evidence", "N/A"
                ),
                "review.source_reference_dispositions[1].evidence",
            ),
            (
                "citation evidence",
                lambda value: value["review"]["citation_dispositions"][0].__setitem__(
                    "evidence", "N/A"
                ),
                "review.citation_dispositions[1].evidence",
            ),
            (
                "move rule",
                lambda value: value["steps"][2]["inference"]["moves"][0].__setitem__("rule", "N/A"),
                "S003.inference.moves[1].rule",
            ),
            (
                "literal check",
                lambda value: value["steps"][2]["checks"].__setitem__("literal", "N/A"),
                "S003.checks.literal",
            ),
            (
                "adversarial check",
                lambda value: value["steps"][2]["checks"].__setitem__("adversarial", ["N/A"]),
                "S003.checks.adversarial",
            ),
            (
                "atomicity evidence",
                lambda value: value["steps"][2]["checks"]["atomicity"].__setitem__(
                    "evidence", "N/A"
                ),
                "S003.checks.atomicity.evidence",
            ),
            (
                "verification basis",
                lambda value: value["review"].__setitem__("verification_basis", ["N/A"]),
                "review.verification_basis",
            ),
            (
                "reviewer note",
                lambda value: value["review"].__setitem__("reviewer_notes", ["N/A"]),
                "review.reviewer_notes",
            ),
        )
        for case, mutate, field in cases:
            with self.subTest(case=case):
                ledger = json.loads(json.dumps(base_ledger))
                mutate(ledger)
                write_json(ledger_path, ledger)
                errors, _ = proofcheck.check_ledger_data(ledger_path, True)
                self.assertTrue(
                    any(
                        field in error
                        and ("substantive" in error or "reserved placeholder" in error)
                        for error in errors
                    ),
                    errors,
                )

    def test_duplicate_quantified_variable_symbol_fails(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["quantified_variables"].append(
            {
                "symbol": "x",
                "type": "real number",
                "domain": "R",
                "quantifier": "forall",
            }
        )
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("duplicate quantified variable symbol x" in error for error in errors),
            errors,
        )

    def test_final_ledger_requires_designated_conclusion_step(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        del ledger["review"]["conclusion_step_id"]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("conclusion_step_id must equal its support step" in error for error in errors),
            errors,
        )

    def test_designated_conclusion_step_must_exist(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["review"]["conclusion_step_id"] = "S999"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("conclusion_step_id must equal its support step" in error for error in errors),
            errors,
        )

    def test_designated_conclusion_must_match_obligation(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["conclusion"] = "y equals y"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "obligation.conclusion must exactly match" in error
                for error in errors
            ),
            errors,
        )

    def test_designated_conclusion_step_must_be_inferential(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["review"]["conclusion_step_id"] = "S001"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("conclusion_step_id must equal its support step" in error for error in errors),
            errors,
        )

    def test_conclusion_step_status_matches_statement_status(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        self.mark_s003_conditional(ledger)
        ledger["review"]["statement_status"] = "established"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "review.statement_status must be the weakest conclusion judgment"
                in error
                for error in errors
            ),
            errors,
        )

    def test_inference_move_cannot_have_zero_inputs(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        step["premise_uses"] = []
        step["inference"]["moves"][0]["premise_ids"] = []
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "must use at least one premise or earlier move" in error
                for error in errors
            ),
            errors,
        )

    def test_orphan_inference_move_is_rejected(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        second_premise = json.loads(json.dumps(step["premise_uses"][0]))
        second_premise["id"] = "P002"
        step["premise_uses"].append(second_premise)
        step["checks"]["atomicity"] = {
            "status": "source_indivisible_chain",
            "source_unit_kind": "one_line",
            "partition_evidence": (
                "The one line has two independent candidate moves for this test."
            ),
            "evidence": "The negative control records two moves on one source line.",
        }
        step["inference"] = {
            "moves": [
                {
                    "id": "M001",
                    "claim": "A detached domain observation.",
                    "rule": "Domain inspection",
                    "premise_ids": ["P001"],
                    "prior_move_ids": [],
                    "justification": "P001 gives the stated domain observation.",
                },
                {
                    "id": "M002",
                    "claim": step["restatement"],
                    "rule": "Reflexivity of equality",
                    "premise_ids": ["P002"],
                    "prior_move_ids": [],
                    "justification": "P002 supplies the arbitrary real variable.",
                },
            ],
            "conclusion_move": "M002",
        }
        ledger["review"]["conclusion_results"][0]["support"]["move_id"] = "M002"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "inference moves are not load-bearing for the conclusion: M001"
                in error
                for error in errors
            ),
            errors,
        )

    def test_dependency_premise_claim_must_match_needed_form(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        dependency = {
            "id": "lem:prior",
            "use_id": "D001",
            "kind": "internal_result",
            "conclusion_id": "C001",
            "status": "verified",
            "needed_form": "The imported result gives x equals x.",
            "compatibility_check": "The result has the same domain and conclusion.",
        }
        step = ledger["steps"][2]
        step["dependencies"] = [dependency]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": "A stronger claim not supplied by the result.",
                "origin": {
                    "kind": "internal_result",
                    "reference": "D001",
                },
                "evidence": "This is an intentional mismatch.",
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        ledger["review"]["direct_dependencies"] = [dependency]
        ledger["review"]["conclusion_results"][0]["dependency_use_ids"] = [
            "D001"
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "claim must exactly match dependency D001 needed_form" in error
                for error in errors
            ),
            errors,
        )

    def test_prior_step_premise_claim_must_match_needed_form(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][0]["kind"] = "setup"
        dependency = {
            "id": "S001",
            "kind": "step",
            "status": "verified",
            "needed_form": "x is fixed as a real number.",
            "compatibility_check": "The setup introduces the same x used below.",
        }
        step = ledger["steps"][2]
        step["dependencies"] = [dependency]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": "x is a positive real number.",
                "origin": {"kind": "prior_step", "reference": "S001"},
                "evidence": "This intentionally strengthens the needed form.",
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "claim must exactly match dependency S001 needed_form" in error
                for error in errors
            ),
            errors,
        )

    def test_theorem_statement_step_cannot_be_a_prior_premise(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        dependency = {
            "id": "S001",
            "kind": "step",
            "status": "verified",
            "needed_form": "For every real x, x equals x.",
            "compatibility_check": "This intentionally cites the target statement.",
        }
        step = ledger["steps"][2]
        step["dependencies"] = [dependency]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": dependency["needed_form"],
                "origin": {"kind": "prior_step", "reference": "S001"},
                "evidence": "This is the circular target statement.",
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("cannot use the theorem statement step S001" in error for error in errors),
            errors,
        )

    def test_non_substantive_step_cannot_be_a_prior_premise(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        dependency = {
            "id": "S002",
            "kind": "step",
            "status": "not_applicable",
            "needed_form": "The proof environment is open.",
            "compatibility_check": "This intentionally cites a delimiter row.",
        }
        step = ledger["steps"][2]
        step["dependencies"] = [dependency]
        step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": dependency["needed_form"],
                "origin": {"kind": "prior_step", "reference": "S002"},
                "evidence": "This is an intentional non-substantive premise.",
            }
        )
        step["inference"]["moves"][0]["premise_ids"].append("P002")
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("cannot use non_substantive step S002" in error for error in errors),
            errors,
        )

    def test_duplicate_premise_id_is_rejected(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        duplicate = json.loads(json.dumps(ledger["steps"][2]["premise_uses"][0]))
        ledger["steps"][2]["premise_uses"].append(duplicate)
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("duplicate premise id P001" in error for error in errors),
            errors,
        )

    def test_string_obligation_premise_claim_must_match_origin(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        premise = ledger["steps"][2]["premise_uses"][0]
        premise["origin"]["reference"] = "/quantifier_scope"
        premise["claim"] = "A different quantifier scope."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "claim must exactly match its string-valued obligation premise"
                in error
                for error in errors
            ),
            errors,
        )

    def test_risk_check_evidence_cannot_be_blank(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["risk_checks"][0]["evidence"] = " "
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "S003.risk_checks[1].evidence must be a nonempty string"
                in error
                for error in errors
            ),
            errors,
        )

    def test_conditional_step_cannot_hide_failed_risk(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = self.mark_s003_conditional(ledger)
        domain = next(
            row for row in step["risk_checks"] if row["aspect"] == "domain"
        )
        domain["status"] = "failed"
        domain["evidence"] = "The required domain relation is false."
        step["conditions"] = []
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "cannot hide failed or unclear risk checks: domain" in error
                for error in errors
            ),
            errors,
        )

    def test_conditional_open_risk_with_exact_mapping_passes(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = self.mark_s003_conditional(ledger)
        domain = next(
            row for row in step["risk_checks"] if row["aspect"] == "domain"
        )
        domain["status"] = "open"
        domain["evidence"] = "Domain compatibility remains an explicit condition."
        step["conditions"] = [
            {
                "kind": "risk_check",
                "reference": "domain",
                "condition": "Validity is conditional on domain compatibility.",
            }
        ]
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_conclusion_normalization_cannot_be_not_applicable(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        conclusion = next(
            row
            for row in ledger["obligation"]["normalization_checks"]
            if row["aspect"] == "conclusion"
        )
        conclusion["status"] = "not_applicable"
        conclusion["evidence"] = "This disposition is intentionally invalid."
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "normalization_checks[conclusion] cannot be not_applicable" in error
                for error in errors
            ),
            errors,
        )

    def test_unclear_model_requires_unclear_normalization(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["probability_model"] = "unclear"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "probability_model is unclear but its normalization check is not"
                in error
                for error in errors
            ),
            errors,
        )
        self.assertFalse(
            any(
                "cannot use an unresolved placeholder" in error
                for error in errors
            ),
            errors,
        )

    def test_braces_are_substantive_source_lines(self) -> None:
        self.assertFalse(proofcheck.is_non_substantive("{"))
        self.assertFalse(proofcheck.is_non_substantive("}"))

    def test_nonfinal_validation_is_inspection_only(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = self.downgrade_ledger_fixture_to_schema4(
            read_json(ledger_path)
        )
        write_json(ledger_path, ledger)
        errors, summary = proofcheck.check_ledger_data(ledger_path, False)
        self.assertEqual([], errors)
        self.assertEqual("draft", summary["validation_mode"])
        self.assertEqual(
            "legacy_inspection_only",
            summary["validation_scope"]["local_record_integrity"],
        )

    def test_legacy_challenge_without_schema5_freshness_is_inspection_only(
        self,
    ) -> None:
        ledger_path = self.make_complete_audit()
        ledger = self.downgrade_ledger_fixture_to_schema4(
            read_json(ledger_path)
        )
        for field in (
            "covered_issue_ids",
            "source_snapshot_sha256",
            "challenged_ledger_sha256",
            "challenge_artifact_sha256",
            "generated_utc",
        ):
            ledger["independent_check"].pop(field, None)
        write_json(ledger_path, ledger)

        draft_errors, summary = proofcheck.check_ledger_data(
            ledger_path, False
        )
        final_errors, _ = proofcheck.check_ledger_data(ledger_path, True)

        self.assertEqual([], draft_errors)
        self.assertEqual(
            "legacy_inspection_only",
            summary["validation_scope"]["local_record_integrity"],
        )
        self.assertTrue(
            any("upgrade_required" in error for error in final_errors),
            final_errors,
        )
        for field in (
            "covered_issue_ids",
            "source_snapshot_sha256",
            "challenged_ledger_sha256",
            "challenge_artifact_sha256",
            "generated_utc",
        ):
            self.assertFalse(
                any(field in error for error in final_errors),
                (field, final_errors),
            )

    def test_schema4_issue_log_is_inspection_only_and_blocks_final_mode(
        self,
    ) -> None:
        self.make_complete_audit()
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        issue_log = read_json(issue_path)
        issue_log["schema_version"] = 4
        write_json(issue_path, issue_log)

        final_errors, _ = proofcheck.check_audit_finalization(self.audit)
        output = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(
            stderr
        ):
            status = proofcheck.cmd_issues(
                argparse.Namespace(
                    root=self.audit,
                    write_summary=False,
                    write_report_views=False,
                    final=True,
                )
            )

        self.assertEqual(1, status)
        self.assertTrue(
            any(
                "ISSUE_LOG" in error
                and "upgrade_required" in error
                and "schema" in error.lower()
                for error in final_errors
            ),
            final_errors,
        )
        self.assertIn("upgrade_required", stderr.getvalue())

    def test_obligation_context_reference_requires_a_premise_link(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        disposition = ledger["review"]["source_reference_dispositions"][0]
        disposition["disposition"] = "obligation_context"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "obligation_context requires nonempty premise_links" in error
                for error in errors
            ),
            errors,
        )

    def test_obligation_context_reference_with_exact_premise_link_passes(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        premise = ledger["steps"][2]["premise_uses"][0]
        premise["source_reference_id"] = "eq:reflexive"
        disposition = ledger["review"]["source_reference_dispositions"][0]
        premise["source_reference_occurrence_id"] = disposition["occurrence_id"]
        disposition["disposition"] = "obligation_context"
        disposition["premise_links"] = [
            {
                "step_id": "S003",
                "premise_id": "P001",
            }
        ]
        disposition["evidence"] = (
            "The referenced statement supplies the exact domain premise P001."
        )
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_source_reference_premise_requires_reverse_disposition_link(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["steps"][2]["premise_uses"][0]["source_reference_id"] = (
            "eq:reflexive"
        )
        ledger["steps"][2]["premise_uses"][0][
            "source_reference_occurrence_id"
        ] = ledger["review"]["source_reference_dispositions"][0]["occurrence_id"]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "Premises with source reference anchors lack an exact "
                "occurrence link" in error
                for error in errors
            ),
            errors,
        )

    def test_completed_gap_can_preserve_target_mismatch(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["conclusion"] = "A stronger conclusion."
        ledger["obligation"]["conclusions"][0]["claim"] = "A stronger conclusion."
        step = ledger["steps"][2]
        step["status"] = "gap"
        step["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "gap"
        ledger["review"]["argument_status"] = "gap"
        ledger["review"]["statement_status"] = "not_established"
        result = ledger["review"]["conclusion_results"][0]
        result["argument_status"] = "gap"
        result["statement_status"] = "not_established"
        result["issue_ids"] = ["I-001"]
        ledger["independent_check"]["challenger_verdict"] = "gap"
        ledger["independent_check"]["reconciled_verdict"] = "gap"
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_locked_source_records_must_be_an_ordered_bijection(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["source_lines"][1]["line"] = ledger["source_lines"][0]["line"]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("source_lines[2].line must be" in error for error in errors),
            errors,
        )

    def test_contract_must_anchor_the_inventoried_statement(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["obligation"]["statement_spans"] = [
            proofcheck.locked_span(self.paper, 3, 3, ledger_path.parent)
        ]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("does not exactly match the inventory" in error for error in errors),
            errors,
        )

    def test_source_reference_needs_a_reviewed_disposition(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["review"]["source_reference_dispositions"] = []
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "source occurrences lack reviewed dispositions" in error
                for error in errors
            ),
            errors,
        )

    def test_reviewed_inventory_cannot_drop_a_discovered_unit(self) -> None:
        self.make_complete_audit()
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        inventory["units"] = []
        write_json(inventory_path, inventory)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("omits parser-discovered units" in error for error in errors), errors
        )

    def test_agreed_challenger_must_match_primary_verdict(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["independent_check"]["challenger_verdict"] = "incorrect"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("challenger_verdict differs" in error for error in errors), errors
        )

    def test_agreed_challenge_requires_matching_recorded_verdicts(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["independent_check"]["challenger_verdict"] = "verified"
        ledger["independent_check"]["reconciled_verdict"] = "incorrect"
        ledger["independent_check"]["disagreements"] = []
        self.seal_schema5_challenge(ledger_path, ledger)

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)

        self.assertTrue(
            any(
                "agreed" in error
                and "challenger" in error
                and "reconciled" in error
                for error in errors
            ),
            errors,
        )

    def test_resolved_challenge_requires_a_recorded_disagreement(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["independent_check"].update(
            {
                "status": "resolved",
                "challenger_verdict": "incorrect",
                "reconciled_verdict": "verified",
                "disagreements": [],
                "resolution": (
                    "The primary audit rechecked the disputed transition and "
                    "documented why the verified verdict is retained."
                ),
            }
        )
        self.seal_schema5_challenge(ledger_path, ledger)

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)

        self.assertTrue(
            any(
                "resolved" in error
                and "disagreement" in error
                for error in errors
            ),
            errors,
        )

    def test_required_challenger_cannot_be_not_checked(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["independent_check"]["challenger_verdict"] = "not_checked"
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("needs a checked challenger verdict" in error for error in errors),
            errors,
        )

    def test_parser_warning_record_cannot_be_rewritten(self) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["parser_warnings"] = ["invented warning"]
        manifest["audit_scope"]["source_or_parser_limits"] = [
            "An invented warning was reviewed."
        ]
        write_json(manifest_path, manifest)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("does not match the current parser warning set" in error for error in errors),
            errors,
        )

    def test_extract_supports_statement_and_proof_in_different_files(self) -> None:
        statement_file = self.base / "statement.tex"
        proof_file = self.base / "proof.tex"
        statement_file.write_text(
            "\\begin{lemma}\nA statement.\n\\end{lemma}\n",
            encoding="utf-8",
            newline="\n",
        )
        proof_file.write_text(
            "\\begin{proof}\nA proof.\n\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger_path = self.base / "split.ledger.json"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=proof_file,
                    start=1,
                    end=3,
                    statement_file=statement_file,
                    statement_start=1,
                    statement_end=3,
                    separate_statement_reason="Statement and proof are in different files.",
                    unit_id="lem:split",
                    output=ledger_path,
                    force=False,
                )
            )
        ledger = read_json(ledger_path)
        span = ledger["obligation"]["statement_spans"][0]
        self.assertEqual(
            statement_file.resolve(),
            proofcheck.resolve_stored_path(span["file"], ledger_path.parent),
        )

    def test_extract_reports_skeleton_state_and_next_action(self) -> None:
        ledger_path = self.base / "skeleton.ledger.json"
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = proofcheck.cmd_extract(
                argparse.Namespace(
                    file=self.paper,
                    start=2,
                    end=7,
                    statement_file=self.paper,
                    statement_start=2,
                    statement_end=4,
                    separate_statement_reason=None,
                    unit_id="lem:skeleton",
                    output=ledger_path,
                    force=False,
                )
            )
        payload = json.loads(output.getvalue())

        self.assertEqual(0, status)
        self.assertEqual("source_locked_skeleton", payload["artifact_state"])
        self.assertIn("next_action", payload)
        self.assertTrue(payload["next_action"].strip())
        self.assertIn("obligation", payload["next_action"].lower())
        self.assertIn("step", payload["next_action"].lower())

    def make_legacy_migration_fixture(self) -> tuple[Path, Path, dict]:
        current_path = self.make_complete_audit()
        current = read_json(current_path)
        legacy_path = current_path.with_name("lem-main-v4.ledger.json")
        legacy = self.downgrade_ledger_fixture_to_schema4(
            json.loads(json.dumps(current))
        )
        write_json(legacy_path, legacy)
        return legacy_path, current_path.with_name(
            "lem-main-migrated.ledger.json"
        ), current

    def test_migrate_ledger_never_overwrites_the_legacy_record(self) -> None:
        legacy_path, migrated_path, _ = self.make_legacy_migration_fixture()
        legacy_bytes = legacy_path.read_bytes()

        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_migrate_ledger(
                argparse.Namespace(
                    ledger=legacy_path,
                    output=migrated_path,
                    force=False,
                )
            )

        self.assertEqual(0, status)
        self.assertEqual(legacy_bytes, legacy_path.read_bytes())
        with self.assertRaises(ValueError):
            proofcheck.cmd_migrate_ledger(
                argparse.Namespace(
                    ledger=legacy_path,
                    output=legacy_path,
                    force=False,
                )
            )
        with self.assertRaises(FileExistsError):
            proofcheck.cmd_migrate_ledger(
                argparse.Namespace(
                    ledger=legacy_path,
                    output=migrated_path,
                    force=False,
                )
            )

    def test_migrate_ledger_creates_a_schema5_recheck_skeleton(self) -> None:
        legacy_path, migrated_path, _ = self.make_legacy_migration_fixture()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = proofcheck.cmd_migrate_ledger(
                argparse.Namespace(
                    ledger=legacy_path,
                    output=migrated_path,
                    force=False,
                )
            )

        payload = json.loads(output.getvalue())
        migrated = read_json(migrated_path)
        legacy = read_json(legacy_path)
        self.assertEqual(0, status)
        self.assertEqual("requires_manual_recheck", payload["artifact_state"])
        self.assertTrue(payload["next_action"].strip())
        self.assertEqual(5, migrated["schema_version"])
        self.assertEqual(4, migrated["evidence_contract_version"])
        self.assertEqual([], migrated["steps"])
        self.assertEqual("not_checked", migrated["review"]["unit_status"])
        self.assertFalse(migrated["independent_check"]["required"])
        self.assertEqual(
            len(migrated["source_lines"]), len(migrated["source_units"])
        )
        self.assertEqual(
            proofcheck.sha256_file(legacy_path),
            migrated["migration"]["legacy_ledger_sha256"],
        )
        self.assertEqual(
            len(legacy["steps"]), migrated["migration"]["legacy_step_count"]
        )
        self.assertEqual(
            "requires_manual_recheck", migrated["migration"]["status"]
        )

    def test_migrated_ledger_needs_an_explicit_full_recheck(self) -> None:
        legacy_path, migrated_path, current = (
            self.make_legacy_migration_fixture()
        )
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_migrate_ledger(
                argparse.Namespace(
                    ledger=legacy_path,
                    output=migrated_path,
                    force=False,
                )
            )
        migrated = read_json(migrated_path)
        for field in (
            "source_units",
            "obligation",
            "review",
            "independent_check",
            "steps",
        ):
            migrated[field] = json.loads(json.dumps(current[field]))
        write_json(migrated_path, migrated)
        self.seal_schema5_challenge(
            migrated_path, read_json(migrated_path)
        )

        errors, _ = proofcheck.check_ledger_data(migrated_path, True)

        self.assertTrue(
            any(
                "requires a full manual atomic recheck" in error
                for error in errors
            ),
            errors,
        )

        migrated = read_json(migrated_path)
        migrated["migration"].update(
            {
                "status": "rechecked",
                "recheck_evidence": (
                    "Every atomic step was rechecked against the locked source."
                ),
                "rechecked_utc": "2026-08-09T00:00:00+00:00",
            }
        )
        write_json(migrated_path, migrated)
        self.seal_schema5_challenge(
            migrated_path, read_json(migrated_path)
        )

        errors, _ = proofcheck.check_ledger_data(migrated_path, True)

        self.assertEqual([], errors)

    def test_skeleton_coverage_diagnostics_are_grouped_and_bounded(self) -> None:
        source = self.base / "long-proof.tex"
        source.write_text(
            "\n".join(f"Proof source line {line}." for line in range(1, 161))
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger_path = self.base / "long-proof.ledger.json"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=source,
                    start=1,
                    end=160,
                    statement_file=None,
                    statement_start=None,
                    statement_end=None,
                    separate_statement_reason="Statement location is not yet recorded.",
                    unit_id="lem:long-skeleton",
                    output=ledger_path,
                    force=False,
                )
            )

        ledger = read_json(ledger_path)
        ledger["source_units"] = []
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, False)
        uncovered = [
            error for error in errors if "Uncovered source line" in error
        ]

        self.assertEqual(1, len(uncovered), errors)
        self.assertIn("1-160", uncovered[0])
        self.assertLess(len(errors), 50, errors)

    def test_locked_source_mismatch_reports_expected_actual_and_first_difference(
        self,
    ) -> None:
        source = self.base / "exact-source.tex"
        source.write_text(
            "Alpha.\nBeta.\nGamma.\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger_path = self.base / "exact-source.ledger.json"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=source,
                    start=1,
                    end=3,
                    statement_file=None,
                    statement_start=None,
                    statement_end=None,
                    separate_statement_reason="Statement location is not yet recorded.",
                    unit_id="lem:exact-source",
                    output=ledger_path,
                    force=False,
                )
            )
        source.write_text(
            "Alpha.\nChanged beta.\nGamma.\n",
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_ledger_data(ledger_path, False)
        mismatches = [
            error for error in errors if "Locked source mismatch" in error
        ]

        self.assertEqual(1, len(mismatches), errors)
        message = mismatches[0]
        self.assertIn("source_lines", message)
        self.assertIn("expected=", message)
        self.assertIn("actual=", message)
        self.assertIn("first difference", message.replace("_", " ").lower())
        self.assertIn("Beta.", message)
        self.assertIn("Changed beta.", message)

    def test_late_exact_mismatch_reports_bounded_context_around_difference(
        self,
    ) -> None:
        prefix = "shared-prefix-" + "a" * 220
        expected_tail = "EXPECTED_DIFFERING_SUBSTRING"
        actual_tail = "ACTUAL_DIFFERING_SUBSTRING"
        suffix = "-shared-suffix-" + "z" * 220
        source = self.base / "late-exact-source.tex"
        source.write_text(
            prefix + expected_tail + suffix + "\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger_path = self.base / "late-exact-source.ledger.json"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=source,
                    start=1,
                    end=1,
                    statement_file=None,
                    statement_start=None,
                    statement_end=None,
                    separate_statement_reason="Statement location is not yet recorded.",
                    unit_id="lem:late-exact-source",
                    output=ledger_path,
                    force=False,
                )
            )
        source.write_text(
            prefix + actual_tail + suffix + "\n",
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_ledger_data(ledger_path, False)
        message = next(
            error for error in errors if "Locked source mismatch" in error
        )

        self.assertIn(expected_tail, message)
        self.assertIn(actual_tail, message)
        self.assertIn("first difference at character", message)
        self.assertLess(len(message), 500)
        self.assertNotIn("a" * 180, message)

    def test_unbraced_input_is_included_in_source_closure(self) -> None:
        root = self.base / "unbraced.tex"
        child = self.base / "child.tex"
        child.write_text("Child content.\n", encoding="utf-8", newline="\n")
        root.write_text("\\input child\n", encoding="utf-8", newline="\n")
        files, warnings = proofcheck.collect_tex_files(root)
        self.assertIn(child.resolve(), files)
        self.assertEqual([], warnings)

    def test_dynamic_subfile_emits_parser_warning(self) -> None:
        root = self.base / "dynamic.tex"
        root.write_text("\\subfile{\\whichfile}\n", encoding="utf-8", newline="\n")
        _, warnings = proofcheck.collect_tex_files(root)
        self.assertTrue(any("Dynamic include" in item for item in warnings), warnings)

    def test_verified_external_result_needs_explicit_prerequisite_map(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_external_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["external_results"][0]["uses"][0]["prerequisite_map"] = []
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("prerequisite_map must not be empty" in error for error in errors),
            errors,
        )

    def test_final_report_assessment_must_match_manifest(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report = report.replace(
            "Overall assessment code: no_defect_found",
            "Overall assessment code: defects_found",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("Final report assessment disagrees" in error for error in errors),
            errors,
        )

    def test_same_file_separate_statement_requires_a_reason(self) -> None:
        ledger_path = self.make_complete_audit()
        original = read_json(ledger_path)
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=self.paper,
                    start=5,
                    end=7,
                    statement_file=self.paper,
                    statement_start=2,
                    statement_end=4,
                    unit_id="lem:main",
                    output=ledger_path,
                    force=True,
                )
            )
        proof_only = read_json(ledger_path)
        proof_only["obligation"] = original["obligation"]
        proof_only["review"] = original["review"]
        proof_only["independent_check"] = original["independent_check"]
        proof_only["steps"] = original["steps"][1:]
        for index, step in enumerate(proof_only["steps"], 1):
            step["source_unit_id"] = f"U{index:03d}"
        write_json(ledger_path, proof_only)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("separate_statement_reason" in error for error in errors),
            errors,
        )
        proof_only["source"]["separate_statement_reason"] = (
            "The theorem statement and its distant proof are intentionally audited as "
            "separate locked spans."
        )
        write_json(ledger_path, proof_only)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)

    def test_citation_needs_a_reviewed_disposition(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["review"]["citation_dispositions"] = []
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("citations lack reviewed dispositions" in error for error in errors),
            errors,
        )

    def test_proof_required_result_cannot_be_verified_without_a_proof(self) -> None:
        proofless_paper = self.base / "proofless.tex"
        proofless_paper.write_text(
            "\\input{definitions}\n"
            "\\begin{lemma}\\label{lem:main}\n"
            "$x=x$ for every real $x$.\\label{eq:reflexive}\n"
            "\\end{lemma}\n"
            "% no proof is supplied\n"
            "\n"
            "\n",
            encoding="utf-8",
            newline="\n",
        )
        proofless_audit = self.base / "proofless-audit"
        original_paper, original_audit = self.paper, self.audit
        try:
            self.paper, self.audit = proofless_paper, proofless_audit
            with contextlib.redirect_stdout(io.StringIO()):
                proofcheck.cmd_scaffold(
                    argparse.Namespace(paper=self.paper, output=self.audit)
                )
            self.make_complete_audit()
            errors, _ = proofcheck.check_audit_finalization(self.audit)
        finally:
            self.paper, self.audit = original_paper, original_audit
        self.assertTrue(
            any("proof-required result has no inventoried proof range" in error for error in errors),
            errors,
        )

    def test_custom_theorem_environment_requires_a_proof(self) -> None:
        custom = self.base / "custom.tex"
        custom.write_text(
            "\\newtheorem{thm}{Theorem}\n"
            "\\begin{thm}\\label{thm:custom}\nA claim.\n\\end{thm}\n",
            encoding="utf-8",
            newline="\n",
        )
        inventory = proofcheck.scan_formal_units(custom)
        unit = next(item for item in inventory["units"] if item["id"] == "thm:custom")
        self.assertTrue(unit["proof_required"])
        self.assertTrue(
            any("no associated proof" in warning for warning in inventory["warnings"]),
            inventory["warnings"],
        )

    def test_common_and_unsupported_citation_commands_are_not_silent(self) -> None:
        source = self.base / "citations.tex"
        source.write_text(
            "\\newtheorem{lemma}{Lemma}\n"
            "\\begin{lemma}\\label{lem:cite}\nA claim.\n\\end{lemma}\n"
            "\\begin{proof}\n"
            "Use \\footcite{known} and \\mycite{unknown}.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        inventory = proofcheck.scan_formal_units(source)
        unit = next(item for item in inventory["units"] if item["id"] == "lem:cite")
        self.assertIn("known", unit["citations"])
        self.assertTrue(
            any("Unsupported citation command" in warning for warning in inventory["warnings"]),
            inventory["warnings"],
        )

    def test_s0_issue_cannot_be_declared_non_load_bearing(self) -> None:
        issues = [
            {
                "id": "I-001",
                "severity": "S0",
                "confidence": "high",
                "status": "open",
                "finding_status": "defect",
                "scope": "unit",
                "load_bearing": False,
                "location": "paper.tex:6",
                "affected_result": "lem:main",
                "affected_results": ["lem:main"],
                "summary": "A fatal proof defect.",
                "evidence": ["paper.tex:6"],
                "downstream_consequences": ["The central claim is not established."],
                "possible_repair": "none proposed",
            }
        ]
        errors, _ = proofcheck.validate_issues(issues, {"I-001"}, True)
        self.assertTrue(
            any("S0 and S1 issues must be load-bearing" in error for error in errors),
            errors,
        )

    def test_included_source_drift_fails(self) -> None:
        self.make_complete_audit()
        self.definitions.write_text(
            "\\newtheorem{lemma}{Lemma}\n% changed context\n",
            encoding="utf-8",
            newline="\n",
        )
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("Source drift in included file" in error for error in errors),
            errors,
        )

    def test_resolved_issue_without_recheck_fails(self) -> None:
        ledger_path = self.make_complete_audit()
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
        issue = {
            "id": "I-001",
            "severity": "S3",
            "confidence": "high",
            "status": "resolved",
            "finding_status": "resolved",
            "scope": "unit",
            "load_bearing": False,
            "location": "paper.tex:6",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "A resolved exposition issue.",
            "evidence": ["paper.tex:6"],
            "downstream_consequences": ["none identified"],
            "possible_repair": "Text was clarified.",
            "resolution": "Text was clarified.",
            "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
            "rechecked_units": ["lem:main"],
        }
        self.install_canonical_issue(issue, ledger_path=ledger_path)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("source_revision" in error for error in errors), errors
        )
        self.assertTrue(
            any("recheck_evidence" in error for error in errors), errors
        )

    def test_open_load_bearing_issue_blocks_no_defect_claim(self) -> None:
        ledger_path = self.make_complete_audit()
        issue = {
            "id": "I-001",
            "severity": "S2",
            "confidence": "high",
            "status": "open",
            "finding_status": "defect",
            "scope": "unit",
            "load_bearing": True,
            "location": "paper.tex:6",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "A load-bearing premise is missing.",
            "evidence": ["paper.tex:6"],
            "downstream_consequences": ["lem:main is not established"],
            "possible_repair": "none proposed",
        }
        self.install_canonical_issue(issue, ledger_path=ledger_path)
        errors, result = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual("defects_found", result["derived_assessment"])
        self.assertTrue(
            any(
                "load-bearing defect finding" in error
                or "expected defects_found" in error
                for error in errors
            ),
            errors,
        )

    def test_density_ratio_interface_requires_complete_trace(self) -> None:
        record = self.make_interface_record()
        registry = {
            "schema_version": proofcheck.METHOD_INTERFACE_SCHEMA_VERSION,
            "scope": {
                "status": "reviewed",
                "trigger": "required",
                "reason": "Density-ratio target is load-bearing.",
            },
            "interfaces": [record],
        }
        mutations = {
            "population target": lambda item: item.pop("population_target"),
            "identification identity": lambda item: item.pop("identification_identity"),
            "numerator law": lambda item: item["fitting_sample_laws"].pop(0),
            "marginal relationships": lambda item: item.pop("marginal_relationships"),
            "evaluation site": lambda item: item.pop("evaluation_sites"),
            "downstream use": lambda item: item.pop("downstream_uses"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                changed = json.loads(json.dumps(registry))
                mutate(changed["interfaces"][0])
                errors: list[str] = []
                proofcheck.validate_method_interface_registry(changed, self.audit, errors)
                self.assertTrue(errors, label)

    def test_ambiguous_interface_cannot_be_declared_a_target_mismatch(self) -> None:
        record = self.make_interface_record(
            specification="ambiguous", target_verdict="mismatch"
        )
        record["issue_ids"] = ["I-001"]
        registry = {
            "schema_version": proofcheck.METHOD_INTERFACE_SCHEMA_VERSION,
            "scope": {
                "status": "reviewed",
                "trigger": "required",
                "reason": "The fitting laws permit distinct interpretations.",
            },
            "interfaces": [record],
        }
        errors: list[str] = []
        proofcheck.validate_method_interface_registry(registry, self.audit, errors)
        self.assertTrue(
            any("cannot establish target_relation" in error for error in errors), errors
        )

    def test_unavailable_implementation_cannot_support_mismatch_finding(self) -> None:
        record = self.make_interface_record(
            implementation_inspection="unavailable",
            code_to_documented="not_checked",
            code_to_target="not_checked",
        )
        record["issue_ids"] = ["I-001"]
        issue = {
            "id": "I-001",
            "severity": "S2",
            "confidence": "medium",
            "status": "open",
            "finding_status": "defect",
            "scope": "global",
            "load_bearing": False,
            "interface_id": "MI-001",
            "finding_class": "implementation_mismatch",
            "affected_layer": "implementation",
            "evidence_class": "not_established",
            "estimator_target_status": "match",
            "implementation_inspection_status": "unavailable",
            "code_to_documented_estimator": "not_checked",
            "code_to_required_target": "not_checked",
            "execution_provenance_status": "not_checked",
            "location": "paper.tex:2-4",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "The implementation is unavailable.",
            "evidence": ["No code snapshot was supplied."],
            "resolution_evidence_needed": ["Supply and inspect the implementation."],
            "downstream_consequences": ["Implementation correspondence is unknown."],
            "possible_repair": "Inspect an exact implementation revision.",
        }
        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            evidence_base=self.audit,
            interfaces={"MI-001": record},
        )
        self.assertTrue(
            any("requires code-to-documentation inconsistency" in error for error in errors),
            errors,
        )

    def test_ambiguity_with_consistent_code_preserves_calibrated_finding(self) -> None:
        self.make_complete_audit()
        record = self.make_interface_record(
            specification="ambiguous",
            target_verdict="not_assessable",
            code_to_documented="not_assessable",
        )
        issue = {
            "id": "I-001",
            "severity": "S3",
            "confidence": "high",
            "status": "open",
            "finding_status": "inconclusive",
            "scope": "global",
            "load_bearing": False,
            "interface_id": "MI-001",
            "finding_class": "exposition_ambiguity",
            "affected_layer": "specification",
            "evidence_class": "observed",
            "estimator_target_status": "not_assessable",
            "implementation_inspection_status": "inspected",
            "code_to_documented_estimator": "not_assessable",
            "code_to_required_target": "consistent",
            "execution_provenance_status": "not_checked",
            "location": "paper.tex:2-4",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "Generic notation leaves two population readings open.",
            "evidence": ["paper.tex:2-4", "estimator.py:1-2"],
            "resolution_evidence_needed": [
                "State the numerator and denominator laws in the manuscript."
            ],
            "downstream_consequences": ["The prose is not self-contained."],
            "possible_repair": "Add the two fitting laws explicitly.",
        }
        self.install_interface_issue(record, issue)
        errors, result = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)
        self.assertEqual("no_defect_found", result["derived_assessment"])
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        method_rows = proofcheck.markdown_table_rows(
            proofcheck.report_section(
                report,
                "## Method-interface findings",
            )
            or ""
        )
        self.assertEqual("static", method_rows[2][5])
        drifted_row = list(method_rows[2])
        drifted_row[5] = "executed"
        report_path.write_text(
            proofcheck.replace_report_section_text(
                report,
                "## Method-interface findings",
                proofcheck.render_markdown_table(
                    method_rows[0],
                    [drifted_row],
                ),
            ),
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "Method-interface findings rows disagree" in error
                for error in errors
            ),
            errors,
        )

    def test_interface_issue_origin_requires_member_evidence_span(self) -> None:
        self.make_complete_audit()
        record = self.make_interface_record(
            specification="ambiguous",
            target_verdict="not_assessable",
            code_to_documented="not_assessable",
        )
        issue = self.make_global_issue(
            finding_status="inconclusive",
            load_bearing=False,
            severity="S3",
            summary="The method interface has two unresolved population readings.",
        )
        issue.update(
            {
                "interface_id": "MI-001",
                "finding_class": "exposition_ambiguity",
                "affected_layer": "specification",
                "evidence_class": "observed",
                "estimator_target_status": "not_assessable",
                "implementation_inspection_status": "inspected",
                "code_to_documented_estimator": "not_assessable",
                "code_to_required_target": "consistent",
                "execution_provenance_status": "not_checked",
                "resolution_evidence_needed": [
                    "State the numerator and denominator laws explicitly."
                ],
                "origin_ref": {
                    "kind": "interface_record",
                    "interface_id": "MI-001",
                    "evidence_spans": [
                        dict(record["fitting_sample_laws"][0][
                            "evidence_spans"
                        ][0])
                    ],
                },
                "invalidation_kind": "scope_inconclusive",
            }
        )
        self.install_interface_issue(record, issue)

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)
        detail_section = proofcheck.report_section(
            (
                self.audit
                / "audit"
                / "06_reports"
                / "FINAL_REPORT.md"
            ).read_text(encoding="utf-8"),
            "## Detailed findings",
        )
        failure_row = proofcheck.markdown_tables(
            detail_section or ""
        )[0][2]
        self.assertNotEqual("none", failure_row[1])
        self.assertNotEqual("none", failure_row[2])

        issue_without_evidence = json.loads(json.dumps(issue))
        issue_without_evidence["origin_ref"].pop("evidence_spans")
        self.install_canonical_issue(
            issue_without_evidence,
            migrate=False,
        )
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "I-001.origin_ref.evidence_spans" in error
                and "nonempty" in error.lower()
                for error in errors
            ),
            errors,
        )

    def test_issue_origin_contract_and_invalidation_must_be_coherent(
        self,
    ) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        record = self.make_interface_record(
            specification="ambiguous",
            target_verdict="not_assessable",
            code_to_documented="not_assessable",
        )
        record["issue_ids"] = ["I-001"]
        self.install_interface_record(record)
        issue = self.make_global_issue(
            finding_status="inconclusive",
            load_bearing=False,
            severity="S3",
            summary="The method interface remains ambiguous.",
        )
        issue.update(
            {
                "interface_id": "MI-001",
                "finding_class": "exposition_ambiguity",
                "affected_layer": "specification",
                "evidence_class": "observed",
                "estimator_target_status": "not_assessable",
                "implementation_inspection_status": "inspected",
                "code_to_documented_estimator": "not_assessable",
                "code_to_required_target": "consistent",
                "execution_provenance_status": "not_checked",
                "resolution_evidence_needed": [
                    "State the two fitting laws explicitly."
                ],
                "origin_ref": {
                    "kind": "interface_record",
                    "interface_id": "MI-001",
                    "evidence_spans": [
                        dict(record["fitting_sample_laws"][0][
                            "evidence_spans"
                        ][0])
                    ],
                },
                "invalidation_kind": "scope_inconclusive",
            }
        )
        _, summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")

        def issue_errors(candidate: dict) -> list[str]:
            errors, _ = proofcheck.validate_issues(
                [candidate],
                set(),
                True,
                evidence_base=self.audit,
                interfaces={"MI-001": record},
                source_snapshot_id=manifest["source_snapshot"]["sha256"],
                in_scope=["lem:main", "lem:prior"],
                ledger_summaries=summaries,
            )
            return errors

        self.assertEqual([], issue_errors(issue))

        unrelated_contract = json.loads(json.dumps(issue))
        unrelated_contract["contract_refs"] = [
            {
                "kind": "conclusion",
                "unit_id": "lem:prior",
                "conclusion_id": "C001",
            }
        ]
        errors = issue_errors(unrelated_contract)
        self.assertTrue(
            any(
                "contract_refs" in error
                and "affected_result" in error
                for error in errors
            ),
            errors,
        )

        wrong_finding = json.loads(json.dumps(issue))
        wrong_finding["finding_status"] = "defect"
        errors = issue_errors(wrong_finding)
        self.assertTrue(
            any(
                "scope_inconclusive" in error
                and "finding_status" in error
                for error in errors
            ),
            errors,
        )

        wrong_dependency_origin = json.loads(json.dumps(issue))
        wrong_dependency_origin["finding_status"] = "defect"
        wrong_dependency_origin["invalidation_kind"] = "dependency_mismatch"
        errors = issue_errors(wrong_dependency_origin)
        self.assertTrue(
            any(
                "dependency_mismatch" in error
                and "origin_ref" in error
                for error in errors
            ),
            errors,
        )

        wrong_refutation_origin = json.loads(json.dumps(issue))
        wrong_refutation_origin["finding_status"] = "defect"
        wrong_refutation_origin["invalidation_kind"] = "statement_refuted"
        errors = issue_errors(wrong_refutation_origin)
        self.assertTrue(
            any(
                "statement_refuted" in error
                and "origin_ref" in error
                for error in errors
            ),
            errors,
        )

    def test_ledger_move_issue_rejects_unlinked_clean_conclusion_contract_ref(
        self,
    ) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        second_conclusion = json.loads(
            json.dumps(ledger["obligation"]["conclusions"][0])
        )
        second_conclusion["id"] = "C002"
        second_conclusion["claim"] = "Every real x is identical to itself"
        ledger["obligation"]["conclusions"].append(second_conclusion)

        failed_step = ledger["steps"][2]
        clean_step = json.loads(json.dumps(failed_step))
        clean_step["id"] = "S004"
        clean_step["goal"] = "Establish the independent verbal conclusion."
        clean_step["restatement"] = second_conclusion["claim"]
        clean_move = clean_step["inference"]["moves"][0]
        clean_move["claim"] = second_conclusion["claim"]
        clean_move["rule"] = "Reflexivity in verbal form"
        clean_move["justification"] = (
            "Reflexivity establishes identity with itself for the arbitrary "
            "real x."
        )
        clean_step["issue_ids"] = []
        ledger["steps"][3]["id"] = "S005"
        ledger["steps"].insert(3, clean_step)

        second_result = json.loads(
            json.dumps(ledger["review"]["conclusion_results"][0])
        )
        second_result["conclusion_id"] = "C002"
        second_result["support"] = {"step_id": "S004", "move_id": "M001"}
        ledger["review"]["conclusion_results"].append(second_result)
        ledger["review"]["conclusion_step_id"] = ""

        failed_step["status"] = "gap"
        failed_step["issue_ids"] = ["I-001"]
        failed_step["inference"]["moves"][0]["failure"] = {
            "kind": "unsupported_assertion",
            "issue_id": "I-001",
            "evidence": "The recorded premise does not establish this conclusion.",
        }
        first_result = ledger["review"]["conclusion_results"][0]
        first_result["argument_status"] = "gap"
        first_result["statement_status"] = "not_established"
        first_result["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "gap"
        ledger["review"]["argument_status"] = "gap"
        ledger["review"]["statement_status"] = "not_established"
        ledger["independent_check"]["covered_issue_ids"] = ["I-001"]
        ledger["independent_check"]["challenger_verdict"] = "gap"
        ledger["independent_check"]["reconciled_verdict"] = "gap"
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))

        ledger_errors, summary = proofcheck.check_ledger_data(
            ledger_path, True
        )
        self.assertEqual([], ledger_errors)
        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=True,
            severity="S1",
            summary="The first conclusion has an unsupported proof move.",
        )
        issue.update(
            {
                "origin_ref": {
                    "kind": "ledger_move",
                    "unit_id": "lem:main",
                    "step_id": "S003",
                    "move_id": "M001",
                },
                "contract_refs": [
                    {
                        "kind": "conclusion",
                        "unit_id": "lem:main",
                        "conclusion_id": "C001",
                    },
                    {
                        "kind": "conclusion",
                        "unit_id": "lem:main",
                        "conclusion_id": "C002",
                    },
                ],
                "invalidation_kind": "proof_gap",
            }
        )
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")

        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            evidence_base=self.audit,
            source_snapshot_id=manifest["source_snapshot"]["sha256"],
            in_scope=["lem:main"],
            ledger_summaries=[summary],
            dependency_edges=[],
        )

        self.assertTrue(
            any(
                "I-001.contract_refs[2]" in error
                and "C002" in error
                and "not linked back" in error
                for error in errors
            ),
            errors,
        )

    def test_dependency_mismatch_origin_must_itself_establish_the_defect(
        self,
    ) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        first_dependency = step["dependencies"][0]
        first_dependency["status"] = "unchecked"
        first_dependency["issue_ids"] = ["I-001"]
        second_dependency = json.loads(json.dumps(first_dependency))
        second_dependency.update(
            {
                "use_id": "D002",
                "status": "incorrect",
                "needed_form": "Equality is symmetric on the real numbers",
            }
        )
        step["dependencies"].append(second_dependency)
        second_premise = json.loads(json.dumps(step["premise_uses"][1]))
        second_premise.update(
            {
                "id": "P003",
                "claim": second_dependency["needed_form"],
                "evidence": (
                    "D002 supplies exactly its separately recorded needed form."
                ),
            }
        )
        second_premise["origin"]["reference"] = "D002"
        step["premise_uses"].append(second_premise)
        step["inference"]["moves"][0]["premise_ids"].append("P003")
        step["inference"]["moves"][0]["failure"] = {
            "kind": "invalid_rule",
            "issue_id": "I-001",
            "evidence": (
                "The incorrect D002 compatibility record prevents this "
                "inference move."
            ),
        }
        step["status"] = "incorrect"
        step["issue_ids"] = ["I-001"]

        first_review_dependency = ledger["review"]["direct_dependencies"][0]
        first_review_dependency["status"] = "unchecked"
        first_review_dependency["issue_ids"] = ["I-001"]
        second_review_dependency = json.loads(
            json.dumps(first_review_dependency)
        )
        second_review_dependency.update(
            {
                "use_id": "D002",
                "status": "incorrect",
                "needed_form": second_dependency["needed_form"],
            }
        )
        ledger["review"]["direct_dependencies"].append(
            second_review_dependency
        )
        conclusion = ledger["review"]["conclusion_results"][0]
        conclusion["argument_status"] = "invalid"
        conclusion["statement_status"] = "not_established"
        conclusion["dependency_closure"] = "incorrect"
        conclusion["dependency_use_ids"] = ["D001", "D002"]
        conclusion["issue_ids"] = ["I-001"]
        ledger["review"]["unit_status"] = "incorrect"
        ledger["review"]["argument_status"] = "invalid"
        ledger["review"]["statement_status"] = "not_established"
        ledger["review"]["dependency_closure"] = "incorrect"
        ledger["independent_check"]["covered_issue_ids"] = ["I-001"]
        ledger["independent_check"]["challenger_verdict"] = "incorrect"
        ledger["independent_check"]["reconciled_verdict"] = "incorrect"
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))

        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        first_use = registry["internal_uses"][0]
        first_use["compatibility_checks"][0].update(
            {
                "status": "unchecked",
                "evidence": (
                    "The D001 quantified-domain comparison was not checked."
                ),
                "issue_ids": ["I-001"],
            }
        )
        first_use["status"] = "unchecked"
        first_use["issue_ids"] = ["I-001"]
        second_use = json.loads(json.dumps(first_use))
        second_use["use_id"] = "D002"
        second_use["needed_form"] = second_dependency["needed_form"]
        second_use["compatibility_checks"][0].update(
            {
                "status": "incorrect",
                "evidence": (
                    "The D002 quantified-domain comparison is incorrect."
                ),
                "issue_ids": ["I-001"],
            }
        )
        second_use["status"] = "incorrect"
        registry["internal_uses"].append(second_use)
        write_json(registry_path, registry)

        ledger_errors, summaries, _ = proofcheck.audit_ledgers(
            self.audit, True
        )
        self.assertEqual([], ledger_errors)
        summaries_by_id = {
            summary["unit_id"]: summary for summary in summaries
        }
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        closure_errors: list[str] = []
        closure = proofcheck.validate_dependency_closure(
            registry,
            self.audit,
            summaries_by_id,
            source_snapshot_sha256=manifest["source_snapshot"]["sha256"],
            inventory_sha256=proofcheck.sha256_file(inventory_path),
            in_scope=manifest["audit_scope"]["in_scope_units"],
            errors=closure_errors,
        )
        self.assertEqual([], closure_errors)
        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=True,
            severity="S2",
            summary=(
                "The dependency closure contains one unchecked use and one "
                "incorrect use."
            ),
        )
        issue.update(
            {
                "origin_ref": {
                    "kind": "dependency_use",
                    "unit_id": "lem:main",
                    "use_id": "D001",
                },
                "contract_refs": [
                    {
                        "kind": "dependency_use",
                        "unit_id": "lem:main",
                        "use_id": "D001",
                    },
                    {
                        "kind": "dependency_use",
                        "unit_id": "lem:main",
                        "use_id": "D002",
                    },
                    {
                        "kind": "conclusion",
                        "unit_id": "lem:main",
                        "conclusion_id": "C001",
                    },
                ],
                "invalidation_kind": "dependency_mismatch",
            }
        )
        issue["suggested_changes"][0]["action"] = "repair_dependency"

        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            evidence_base=self.audit,
            source_snapshot_id=manifest["source_snapshot"]["sha256"],
            in_scope=manifest["audit_scope"]["in_scope_units"],
            ledger_summaries=summaries,
            dependency_edges=closure["edges"],
        )

        self.assertTrue(
            any(
                "I-001.origin_ref" in error
                and "dependency use" in error
                and "unchecked" in error
                and "cannot establish dependency_mismatch" in error
                for error in errors
            ),
            errors,
        )

    def test_established_target_mismatch_forces_defects_found(self) -> None:
        self.make_complete_audit()
        record = self.make_interface_record(
            target_verdict="mismatch",
            code_to_documented="consistent",
            code_to_target="inconsistent",
        )
        issue = {
            "id": "I-001",
            "severity": "S2",
            "confidence": "high",
            "status": "open",
            "finding_status": "defect",
            "scope": "global",
            "load_bearing": False,
            "interface_id": "MI-001",
            "finding_class": "estimator_target_mismatch",
            "affected_layer": "estimator_target",
            "evidence_class": "observed",
            "estimator_target_status": "mismatch",
            "implementation_inspection_status": "inspected",
            "code_to_documented_estimator": "consistent",
            "code_to_required_target": "inconsistent",
            "execution_provenance_status": "not_checked",
            "location": "paper.tex:2-4",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "The fixed fitting laws target a different population ratio.",
            "evidence": ["paper.tex:2-4"],
            "resolution_evidence_needed": ["Change the estimator or the claimed target."],
            "downstream_consequences": ["The documented feasible method is mismatched."],
            "possible_repair": "Use equal state reference laws.",
        }
        self.install_interface_issue(record, issue)
        errors, result = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual("defects_found", result["derived_assessment"])
        self.assertTrue(
            any("expected defects_found" in error for error in errors), errors
        )

    def test_locked_code_evidence_detects_drift(self) -> None:
        record = self.make_interface_record()
        registry = {
            "schema_version": proofcheck.METHOD_INTERFACE_SCHEMA_VERSION,
            "scope": {
                "status": "reviewed",
                "trigger": "required",
                "reason": "The implementation relation was inspected.",
            },
            "interfaces": [record],
        }
        errors: list[str] = []
        proofcheck.validate_method_interface_registry(registry, self.audit, errors)
        self.assertEqual([], errors)
        (self.base / "estimator.py").write_text(
            "def fit_ratio(states, beta_actions, pi_actions):\n"
            "    return states, pi_actions, beta_actions\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = []
        proofcheck.validate_method_interface_registry(registry, self.audit, errors)
        self.assertTrue(any("source drift" in error for error in errors), errors)

    def test_unlinked_code_does_not_block_an_oracle_theorem_scope(self) -> None:
        self.make_complete_audit()
        record = self.make_interface_record(
            load_bearing=True,
            implementation_required=False,
            execution_required=False,
            execution_provenance="not_checked",
        )
        self.install_interface_record(record)
        errors, result = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)
        self.assertEqual("no_defect_found", result["derived_assessment"])

    def test_required_execution_provenance_forces_inconclusive(self) -> None:
        self.make_complete_audit()
        record = self.make_interface_record(
            load_bearing=True,
            execution_required=True,
            execution_provenance="not_checked",
        )
        issue = {
            "id": "I-001",
            "severity": "S2",
            "confidence": "high",
            "status": "open",
            "finding_status": "inconclusive",
            "scope": "global",
            "load_bearing": True,
            "interface_id": "MI-001",
            "finding_class": "reproducibility_gap",
            "affected_layer": "execution_provenance",
            "evidence_class": "not_established",
            "estimator_target_status": "match",
            "implementation_inspection_status": "inspected",
            "code_to_documented_estimator": "consistent",
            "code_to_required_target": "consistent",
            "execution_provenance_status": "not_checked",
            "location": "reported experiments",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "The inspected revision is not linked to reported runs.",
            "evidence": ["No run-to-revision record was supplied."],
            "resolution_evidence_needed": [
                "Supply revision, semantic configuration, inputs, and output linkage."
            ],
            "downstream_consequences": [
                "The declared end-to-end empirical claim remains unverified."
            ],
            "possible_repair": "Provide source-locked execution provenance.",
        }
        self.install_interface_issue(record, issue)
        errors, result = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual("inconclusive", result["derived_assessment"])
        self.assertTrue(any("expected inconclusive" in error for error in errors), errors)

    def test_nonrequired_provenance_nonmatch_does_not_block_oracle_scope(self) -> None:
        self.make_complete_audit()
        record = self.make_interface_record(
            load_bearing=True,
            execution_required=False,
            execution_provenance="not_matched",
        )
        issue = {
            "id": "I-001",
            "severity": "S3",
            "confidence": "high",
            "status": "open",
            "finding_status": "defect",
            "scope": "global",
            "load_bearing": False,
            "interface_id": "MI-001",
            "finding_class": "reproducibility_gap",
            "affected_layer": "execution_provenance",
            "evidence_class": "observed",
            "estimator_target_status": "match",
            "implementation_inspection_status": "inspected",
            "code_to_documented_estimator": "consistent",
            "code_to_required_target": "consistent",
            "execution_provenance_status": "not_matched",
            "location": "reported experiments",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "The archived revision differs from the recorded run revision.",
            "evidence": ["run-record.txt:1"],
            "resolution_evidence_needed": ["Locate the executed revision."],
            "downstream_consequences": [
                "The archive cannot reproduce the run, but the oracle proof is unaffected."
            ],
            "possible_repair": "Archive the executed revision and configuration.",
        }
        self.install_interface_issue(record, issue)
        errors, result = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)
        self.assertEqual("no_defect_found", result["derived_assessment"])

    def test_load_bearing_interface_issue_requires_load_bearing_interface(self) -> None:
        record = self.make_interface_record(
            specification="ambiguous",
            target_verdict="not_assessable",
            code_to_documented="not_assessable",
            load_bearing=False,
        )
        record["issue_ids"] = ["I-001"]
        issue = {
            "id": "I-001",
            "severity": "S1",
            "confidence": "medium",
            "status": "open",
            "finding_status": "inconclusive",
            "scope": "global",
            "load_bearing": True,
            "interface_id": "MI-001",
            "finding_class": "exposition_ambiguity",
            "affected_layer": "specification",
            "evidence_class": "observed",
            "estimator_target_status": "not_assessable",
            "implementation_inspection_status": "inspected",
            "code_to_documented_estimator": "not_assessable",
            "code_to_required_target": "consistent",
            "execution_provenance_status": "not_checked",
            "location": "paper.tex:2-4",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "A central estimator description is ambiguous.",
            "evidence": ["paper.tex:2-4"],
            "resolution_evidence_needed": ["Clarify both fitting laws."],
            "downstream_consequences": ["The central feasible method is not assessable."],
            "possible_repair": "State both laws explicitly.",
        }
        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            evidence_base=self.audit,
            interfaces={"MI-001": record},
        )
        self.assertTrue(
            any("requires a load-bearing interface" in error for error in errors),
            errors,
        )

    def test_open_interface_contract_detects_semantic_span_drift(self) -> None:
        self.make_complete_audit()
        record = self.make_interface_record(
            specification="ambiguous",
            target_verdict="not_assessable",
            code_to_documented="not_assessable",
        )
        record["issue_ids"] = ["I-001"]
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
        issue = {
            "id": "I-001",
            "severity": "S3",
            "confidence": "high",
            "status": "open",
            "finding_status": "inconclusive",
            "scope": "global",
            "load_bearing": False,
            "interface_id": "MI-001",
            "finding_class": "exposition_ambiguity",
            "affected_layer": "specification",
            "evidence_class": "observed",
            "estimator_target_status": "not_assessable",
            "implementation_inspection_status": "inspected",
            "code_to_documented_estimator": "not_assessable",
            "code_to_required_target": "consistent",
            "execution_provenance_status": "not_checked",
            "location": "paper.tex:2-4",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "The interface wording remains ambiguous.",
            "evidence": ["paper.tex:2-4"],
            "resolution_evidence_needed": ["State both fitting laws."],
            "downstream_consequences": ["none identified"],
            "possible_repair": "State both fitting laws explicitly.",
            "rechecked_units": [],
            "rechecked_dependency_uses": [],
            "reconciled_deliverables": [],
            "semantic_contract": {
                "protected_meaning": "Both laws use the same state reference measure.",
                "supporting_spans": [
                    proofcheck.locked_span(
                        self.paper,
                        2,
                        4,
                        self.audit,
                        role="authoritative_definition",
                    )
                ],
                "dependent_claims": ["lem:main"],
                "reopen_if": ["The common reference law becomes unspecified."],
                "regression_check": "Reconstruct both fitting laws after edits.",
                "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
            },
        }
        issue, _ = self.migrate_issue_fixture_to_schema5(issue)
        _, summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            evidence_base=self.audit,
            interfaces={"MI-001": record},
            source_snapshot_id=manifest["source_snapshot"]["sha256"],
            ledger_summaries=summaries,
        )
        self.assertEqual([], errors)
        self.paper.write_text(
            self.paper.read_text(encoding="utf-8").replace("$x=x$", "$x\\le x$"),
            encoding="utf-8",
            newline="\n",
        )
        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            evidence_base=self.audit,
            interfaces={"MI-001": record},
            source_snapshot_id=manifest["source_snapshot"]["sha256"],
            ledger_summaries=summaries,
        )
        self.assertTrue(any("source drift" in error for error in errors), errors)

    def test_finalize_writes_protocol_seal(self) -> None:
        self.make_complete_audit()
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_finalize(argparse.Namespace(root=self.audit))
        self.assertEqual(0, status)
        record = read_json(
            self.audit / "audit" / "06_reports" / "FINALIZATION.json"
        )
        self.assertEqual("passed", record["status"])
        self.assertEqual("1.0", record["protocol"]["skill_version"])
        self.assertTrue(record["audit_state_sha256"])

    def test_portable_finalization_stays_fresh_after_relocation_with_warning(
        self,
    ) -> None:
        self.definitions.write_text(
            self.definitions.read_text(encoding="utf-8")
            + "\\input{missing-portable-source}\n",
            encoding="utf-8",
            newline="\n",
        )
        original_paper = self.paper
        original_definitions = self.definitions
        self.audit = self.base / "portable-final-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_scaffold(
                argparse.Namespace(
                    paper=self.paper,
                    output=self.audit,
                    input_kind="latex",
                    publisher_pdf=None,
                    portable_sources=True,
                    visual_review_status="not_started",
                    visual_review_notes=None,
                    additional_source=None,
                    fls=None,
                    project_root=self.base,
                )
            )
        self.assertEqual(0, status)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        inventory = read_json(
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        cross_references = read_json(
            self.audit / "audit" / "01_index" / "cross_reference_audit.json"
        )
        self.assertEqual("paper.tex", inventory["root_file"])
        self.assertEqual("paper.tex", cross_references["root_file"])
        self.assertTrue(manifest["parser_warnings"])
        self.assertTrue(
            any(
                "Included file not found: definitions.tex:2: "
                "missing-portable-source" in warning
                for warning in manifest["parser_warnings"]
            ),
            manifest["parser_warnings"],
        )
        persisted_text = json.dumps(
            [manifest, inventory, cross_references], ensure_ascii=False
        )
        self.assertNotIn(".proofcheck.stage", persisted_text)

        self.paper = proofcheck.resolve_stored_path(
            manifest["paper_file"], self.audit
        )
        self.definitions = self.paper.parent / "definitions.tex"
        self.make_complete_audit()
        manifest = read_json(manifest_path)
        for review in manifest["parser_warning_reviews"]:
            review.update(
                {
                    "disposition": "confirmed_non_load_bearing",
                    "affected_units": [],
                    "evidence": (
                        "The missing optional input contains no audited proof content."
                    ),
                }
            )
        write_json(manifest_path, manifest)

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            finalize_status = proofcheck.cmd_finalize(
                argparse.Namespace(root=self.audit)
            )
        self.assertEqual(0, finalize_status)

        original_paper.unlink()
        original_definitions.unlink()
        moved = self.base / "relocated portable final audit"
        self.audit.rename(moved)
        self.audit = moved
        freshness = proofcheck.check_finalization_freshness(self.audit)

        self.assertEqual("current", freshness["freshness"])
        self.assertTrue(freshness["usable_finalization"])
        self.assertEqual([], freshness["current_gate_errors"])
        self.assertEqual([], freshness["stale_reasons"])

    def test_source_closure_follows_local_classes_and_packages(self) -> None:
        root = self.base / "local-dependencies.tex"
        local_class = self.base / "localjournal.cls"
        local_package = self.base / "localmath.sty"
        class_helper = self.base / "classhelper.sty"
        package_helper = self.base / "package-helper.tex"
        root.write_text(
            "\\documentclass{localjournal}\n"
            "\\usepackage{localmath}\n"
            "Document body.\n",
            encoding="utf-8",
            newline="\n",
        )
        local_class.write_text(
            "\\LoadClass{article}\n\\RequirePackage{classhelper}\n",
            encoding="utf-8",
            newline="\n",
        )
        local_package.write_text(
            "\\input{package-helper}\n",
            encoding="utf-8",
            newline="\n",
        )
        class_helper.write_text(
            "\\ProvidesPackage{classhelper}\n",
            encoding="utf-8",
            newline="\n",
        )
        package_helper.write_text(
            "\\newcommand{\\helper}{helper}\n",
            encoding="utf-8",
            newline="\n",
        )

        closure = proofcheck.discover_source_closure(root)

        self.assertEqual(
            {
                root.resolve(),
                local_class.resolve(),
                local_package.resolve(),
                class_helper.resolve(),
                package_helper.resolve(),
            },
            set(closure["files"]),
        )
        self.assertEqual([], closure["warnings"])

    def test_scaffold_locks_additional_sources_and_their_dependencies(self) -> None:
        additional = self.base / "supplement.tex"
        helper = self.base / "supplement-helper.tex"
        additional.write_text(
            "\\input{supplement-helper}\nSupplement.\n",
            encoding="utf-8",
            newline="\n",
        )
        helper.write_text("Helper.\n", encoding="utf-8", newline="\n")
        audit = self.base / "additional-source-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(
                    paper=self.paper,
                    output=audit,
                    additional_source=[
                        (
                            str(additional),
                            "The supplement contains proof context.",
                            "The author identified this file as part of the audit scope.",
                        )
                    ],
                    fls=None,
                )
            )

        manifest = read_json(audit / "AUDIT_MANIFEST.json")
        locked_files = {
            proofcheck.resolve_stored_path(row["file"], audit)
            for row in manifest["source_snapshot"]["files"]
        }
        self.assertIn(additional.resolve(), locked_files)
        self.assertIn(helper.resolve(), locked_files)
        self.assertEqual(
            "The supplement contains proof context.",
            manifest["source_discovery"]["additional_files"][0]["reason"],
        )

        helper.write_text("Changed helper.\n", encoding="utf-8", newline="\n")
        errors, _ = proofcheck.check_audit_finalization(audit)
        self.assertTrue(
            any("Source drift in included file" in error for error in errors),
            errors,
        )

    def test_fls_adds_project_sources_and_is_itself_source_locked(self) -> None:
        recorder_source = self.base / "generated-definitions.sty"
        recorder_source.write_text(
            "\\ProvidesPackage{generated-definitions}\n",
            encoding="utf-8",
            newline="\n",
        )
        outside_input = self.base.parent / "external-system-package.sty"
        fls = self.base / "paper.fls"
        fls.write_text(
            f"PWD {self.base}\n"
            f"INPUT {recorder_source}\n"
            f"INPUT {outside_input}\n",
            encoding="utf-8",
            newline="\n",
        )
        audit = self.base / "fls-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(
                    paper=self.paper,
                    output=audit,
                    additional_source=None,
                    fls=fls,
                )
            )

        manifest = read_json(audit / "AUDIT_MANIFEST.json")
        locked_files = {
            proofcheck.resolve_stored_path(row["file"], audit)
            for row in manifest["source_snapshot"]["files"]
        }
        fls_record = manifest["source_discovery"]["fls"]
        self.assertIn(recorder_source.resolve(), locked_files)
        self.assertEqual(
            [str(outside_input.resolve())],
            fls_record["outside_project_inputs"],
        )

        fls.write_text(
            fls.read_text(encoding="utf-8") + "OUTPUT paper.pdf\n",
            encoding="utf-8",
            newline="\n",
        )
        errors, _ = proofcheck.check_audit_finalization(audit)
        self.assertTrue(any("Recorder file drift" in error for error in errors), errors)

    def rebuild_with_parser_warning(self) -> Path:
        self.paper.write_text(
            self.paper.read_text(encoding="utf-8") + "\\subfile{\\whichfile}\n",
            encoding="utf-8",
            newline="\n",
        )
        self.audit = self.base / "warning-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(paper=self.paper, output=self.audit)
            )
        self.make_complete_audit()
        return self.audit / "AUDIT_MANIFEST.json"

    def test_parser_warning_reviews_are_an_exact_bijection(self) -> None:
        manifest_path = self.rebuild_with_parser_warning()
        manifest = read_json(manifest_path)
        self.assertTrue(manifest["parser_warnings"])
        manifest["parser_warning_reviews"] = []
        write_json(manifest_path, manifest)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("must be a one-to-one review" in error for error in errors),
            errors,
        )

    def test_parser_warning_disposition_controls_no_defect_claim(self) -> None:
        manifest_path = self.rebuild_with_parser_warning()
        manifest = read_json(manifest_path)
        review = manifest["parser_warning_reviews"][0]
        review.update(
            {
                "disposition": "confirmed_non_load_bearing",
                "affected_units": [],
                "evidence": "The dynamic include occurs after the only proof unit.",
            }
        )
        write_json(manifest_path, manifest)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)

        manifest = read_json(manifest_path)
        manifest["parser_warning_reviews"][0]["disposition"] = "unresolved"
        write_json(manifest_path, manifest)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "unresolved parser warning blocks no_defect_found" in error
                for error in errors
            ),
            errors,
        )

    def test_parser_scope_limitation_requires_a_recorded_limit(self) -> None:
        manifest_path = self.rebuild_with_parser_warning()
        manifest = read_json(manifest_path)
        manifest["parser_warning_reviews"][0].update(
            {
                "disposition": "scope_limitation",
                "affected_units": [],
                "evidence": "The dynamically selected file could not be resolved.",
            }
        )
        write_json(manifest_path, manifest)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("scope_limitation requires" in error for error in errors),
            errors,
        )

    def test_parser_limitation_outside_scope_is_assessment_neutral(self) -> None:
        manifest_path = self.rebuild_with_parser_warning()
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        excluded = json.loads(json.dumps(inventory["units"][0]))
        excluded["id"] = "lem:excluded"
        excluded["label"] = "lem:excluded"
        inventory["units"].append(excluded)
        write_json(inventory_path, inventory)

        limitation = "Dynamic source selection outside the audited proof scope."
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["excluded_units"] = [
            {
                "id": "lem:excluded",
                "reason": "The companion proof unit is outside the focused audit.",
            }
        ]
        manifest["audit_scope"]["inventory_overrides"] = [
            {
                "unit_id": "lem:excluded",
                "kind": "manual_unit",
                "reason": "Rendered-source review identified a companion proof unit.",
                "evidence": "Its statement and proof are visible in rendered source.",
            }
        ]
        manifest["audit_scope"]["source_or_parser_limits"] = [limitation]
        manifest["parser_warning_reviews"][0].update(
            {
                "disposition": "scope_limitation",
                "affected_units": ["lem:excluded"],
                "evidence": "The unresolved include can affect only the excluded unit.",
            }
        )
        write_json(manifest_path, manifest)
        self.refresh_dependency_review()

        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["source_or_parser_limits"] = [limitation]
        write_json(progress_path, progress)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report = report.replace("- Results not checked: none", "- Results not checked: lem:excluded")
        report = report.replace(
            "- Tooling, extraction, or rendering limitations: none",
            f"- Tooling, extraction, or rendering limitations: {limitation}",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        errors, result = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual("no_defect_found", result["derived_assessment"])
        self.assertFalse(
            any("parser limitation blocks no_defect_found" in error for error in errors),
            errors,
        )

        canonical_manifest = read_json(manifest_path)
        cases = {
            "unresolved": lambda review: review.update(
                {"disposition": "unresolved", "affected_units": ["lem:excluded"]}
            ),
            "empty scope": lambda review: review.__setitem__("affected_units", []),
            "in-scope unit": lambda review: review.__setitem__(
                "affected_units", ["lem:main"]
            ),
        }
        for label, mutate in cases.items():
            with self.subTest(case=label):
                changed = json.loads(json.dumps(canonical_manifest))
                mutate(changed["parser_warning_reviews"][0])
                write_json(manifest_path, changed)
                errors, result = proofcheck.check_audit_finalization(self.audit)
                self.assertEqual("inconclusive", result["derived_assessment"])
                self.assertTrue(
                    any("blocks no_defect_found" in error for error in errors),
                    errors,
                )

    def test_status_reports_a_current_usable_finalization(self) -> None:
        self.make_complete_audit()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(
                0,
                proofcheck.cmd_finalize(argparse.Namespace(root=self.audit)),
            )
        status_output = io.StringIO()
        with contextlib.redirect_stdout(status_output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                )
            )
        payload = json.loads(status_output.getvalue())

        self.assertEqual(0, status)
        self.assertEqual("passed", payload["finalization"]["record_status"])
        self.assertEqual("current", payload["finalization"]["freshness"])
        self.assertTrue(payload["finalization"]["usable_finalization"])

    def test_status_marks_changed_audit_artifact_as_stale(self) -> None:
        self.make_complete_audit()
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_finalize(argparse.Namespace(root=self.audit))
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report_path.write_text(
            report_path.read_text(encoding="utf-8") + "\nEditorial note.\n",
            encoding="utf-8",
            newline="\n",
        )

        freshness = proofcheck.check_finalization_freshness(self.audit)
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                )
            )

        self.assertEqual(1, status)
        self.assertEqual("stale", freshness["freshness"])
        self.assertFalse(freshness["usable_finalization"])
        self.assertIn(
            "audit/06_reports/FINAL_REPORT.md",
            freshness["artifact_changes"]["changed"],
        )

    def test_external_source_drift_invalidates_finalization(self) -> None:
        self.make_complete_audit()
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_finalize(argparse.Namespace(root=self.audit))
        self.definitions.write_text(
            "\\newtheorem{lemma}{Lemma}\n% changed after finalization\n",
            encoding="utf-8",
            newline="\n",
        )

        freshness = proofcheck.check_finalization_freshness(self.audit)

        self.assertEqual("stale", freshness["freshness"])
        self.assertFalse(freshness["usable_finalization"])
        self.assertTrue(
            any(
                "Source drift in included file" in error
                for error in freshness["current_gate_errors"]
            ),
            freshness,
        )

    def test_status_without_finalization_record_remains_nonfailing(self) -> None:
        self.make_complete_audit()
        status_output = io.StringIO()
        with contextlib.redirect_stdout(status_output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                )
            )
        payload = json.loads(status_output.getvalue())

        self.assertEqual(0, status)
        self.assertEqual("missing", payload["finalization"]["record_status"])
        self.assertEqual("not_applicable", payload["finalization"]["freshness"])
        self.assertFalse(payload["finalization"]["usable_finalization"])

    def test_status_exposes_a_healthy_checkpointed_work_in_progress(self) -> None:
        ledger_path = (
            self.audit / "audit" / "04_local_checks" / "lem-main.ledger.json"
        )
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=self.paper,
                    start=2,
                    end=7,
                    statement_file=self.paper,
                    statement_start=2,
                    statement_end=4,
                    separate_statement_reason=None,
                    unit_id="lem:main",
                    output=ledger_path,
                    force=False,
                )
            )
        next_action = "Populate the obligation and first atomic step for lem:main."
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_checkpoint(
                argparse.Namespace(
                    root=self.audit,
                    active_unit="lem:main",
                    clear_active_unit=False,
                    next_action=next_action,
                )
            )

        status_output = io.StringIO()
        with contextlib.redirect_stdout(status_output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                    verbose=False,
                )
            )
        payload = json.loads(status_output.getvalue())

        self.assertEqual(0, status)
        self.assertEqual("healthy_wip", payload["workflow_state"])
        self.assertEqual("lem:main", payload["progress"]["active_unit"])
        self.assertEqual(next_action, payload["progress"]["next_action"])
        self.assertEqual([], payload["progress"]["drift"])
        self.assertCountEqual(
            ["lem:main"], payload["progress"]["not_started_units"]
        )

    def test_status_marks_stale_checkpoint_as_malformed_or_stale(self) -> None:
        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["source_snapshot_sha256"] = "0" * 64
        write_json(progress_path, progress)

        status_output = io.StringIO()
        with contextlib.redirect_stdout(status_output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                    verbose=False,
                )
            )
        payload = json.loads(status_output.getvalue())

        self.assertEqual(1, status)
        self.assertEqual("malformed_or_stale", payload["workflow_state"])
        self.assertTrue(payload["progress"]["drift"])
        self.assertIn(
            "source_snapshot_sha256",
            json.dumps(payload["progress"]["drift"]),
        )

    def test_status_reports_coherent_legacy_audit_as_upgrade_required(
        self,
    ) -> None:
        ledger_path = self.downgrade_complete_audit_to_schema4()

        def status_payload(verbose: bool) -> tuple[int, dict]:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = proofcheck.cmd_status(
                    argparse.Namespace(
                        root=self.audit,
                        format="json",
                        output=None,
                        force=False,
                        verbose=verbose,
                    )
                )
            return status, json.loads(output.getvalue())

        concise_status, concise = status_payload(False)
        verbose_status, verbose = status_payload(True)
        expected_recorded = {
            "artifact_schema_version": 4,
            "evidence_contract_version": 3,
            "closure_contract_version": 2,
        }
        expected_current = {
            "artifact_schema_version": proofcheck.SCHEMA_VERSION,
            "evidence_contract_version": (
                proofcheck.EVIDENCE_CONTRACT_VERSION
            ),
            "closure_contract_version": (
                proofcheck.CLOSURE_CONTRACT_VERSION
            ),
        }

        self.assertEqual(1, concise_status)
        self.assertEqual(1, verbose_status)
        self.assertEqual("upgrade_required", concise["workflow_state"])
        self.assertEqual("upgrade_required", verbose["workflow_state"])
        self.assertEqual("upgrade_required", concise["protocol"]["status"])
        self.assertEqual(
            expected_recorded, concise["protocol"]["recorded"]
        )
        self.assertEqual(expected_current, concise["protocol"]["current"])
        self.assertTrue(
            any(
                str(path).endswith(ledger_path.name)
                for path in concise["protocol"]["legacy_ledgers"]
            ),
            concise["protocol"],
        )
        next_action = concise["protocol"]["next_action"].lower()
        self.assertIn("migrate-ledger", next_action)
        self.assertIn("recheck", next_action)
        self.assertEqual([], concise["structural_errors"])
        self.assertEqual([], concise["invalid_ledgers"])
        self.assertLessEqual(
            len(concise["finalization"]["current_gate_errors"]), 4
        )
        self.assertTrue(
            any(
                "upgrade" in error.lower()
                or "protocol" in error.lower()
                for error in concise["finalization"]["current_gate_errors"]
            ),
            concise["finalization"],
        )
        self.assertGreater(
            concise["finalization"]["current_gate_errors_omitted"], 0
        )
        self.assertEqual(
            0, verbose["finalization"]["current_gate_errors_omitted"]
        )
        self.assertEqual(
            verbose["finalization"]["current_gate_error_count"],
            len(verbose["finalization"]["current_gate_errors"]),
        )
        self.assertEqual(
            concise["finalization"]["current_gate_error_count"],
            verbose["finalization"]["current_gate_error_count"],
        )
        self.assertGreater(
            len(verbose["finalization"]["current_gate_errors"]),
            len(concise["finalization"]["current_gate_errors"]),
        )

    def test_status_requires_explicit_same_schema_validator_revalidation(
        self,
    ) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["protocol"]["validator_sha256"] = "0" * 64
        write_json(manifest_path, manifest)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                    verbose=False,
                )
            )
        payload = json.loads(output.getvalue())

        self.assertEqual(1, status)
        self.assertEqual(
            "validator_revalidation_required", payload["workflow_state"]
        )
        self.assertEqual(
            "validator_revalidation_required", payload["protocol"]["status"]
        )
        self.assertIn(
            "revalidate-protocol", payload["protocol"]["next_action"]
        )

        revalidation_output = io.StringIO()
        with contextlib.redirect_stdout(revalidation_output):
            revalidation_status = proofcheck.cmd_revalidate_protocol(
                argparse.Namespace(root=self.audit)
            )
        revalidation = json.loads(revalidation_output.getvalue())

        self.assertEqual(0, revalidation_status)
        self.assertEqual("revalidated", revalidation["status"])
        self.assertTrue(revalidation["updated"])
        self.assertEqual(
            proofcheck.protocol_identity(),
            read_json(manifest_path)["protocol"],
        )
        self.assertEqual([], proofcheck.check_audit_finalization(self.audit)[0])

    def test_protocol_revalidation_accepts_a_valid_scaffold_wip(self) -> None:
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["protocol"]["validator_sha256"] = "0" * 64
        write_json(manifest_path, manifest)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = proofcheck.cmd_revalidate_protocol(
                argparse.Namespace(root=self.audit)
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(0, status)
        self.assertEqual("revalidated", payload["status"])
        self.assertEqual(
            proofcheck.protocol_identity(),
            read_json(manifest_path)["protocol"],
        )

    def test_protocol_revalidation_refuses_source_drift(self) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["protocol"]["validator_sha256"] = "0" * 64
        write_json(manifest_path, manifest)
        self.paper.write_text(
            self.paper.read_text(encoding="utf-8") + "% changed source\n",
            encoding="utf-8",
            newline="\n",
        )

        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = proofcheck.cmd_revalidate_protocol(
                argparse.Namespace(root=self.audit)
            )

        self.assertEqual(1, status)
        self.assertEqual("failed", json.loads(output.getvalue())["status"])
        self.assertEqual("0" * 64, read_json(manifest_path)["protocol"]["validator_sha256"])
        self.assertIn("drift", errors.getvalue().lower())

    def test_protocol_revalidation_refuses_unreadable_canonical_records(
        self,
    ) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["protocol"]["validator_sha256"] = "0" * 64
        write_json(manifest_path, manifest)
        canonical_records = {
            "inventory": (
                self.audit
                / "audit"
                / "01_index"
                / "theorem_inventory.json"
            ),
            "dependency registry": (
                self.audit
                / "audit"
                / "03_dependencies"
                / "DEPENDENCY_REGISTRY.json"
            ),
            "method-interface registry": (
                self.audit
                / "audit"
                / "03_dependencies"
                / "METHOD_INTERFACE_REGISTRY.json"
            ),
            "final report": (
                self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
            ),
        }
        original_bytes = {
            label: path.read_bytes()
            for label, path in canonical_records.items()
        }

        for label, path in canonical_records.items():
            with self.subTest(record=label):
                for original_label, original_path in canonical_records.items():
                    original_path.write_bytes(original_bytes[original_label])
                path.write_bytes(
                    b"\xff" if label == "final report" else b"{malformed json"
                )

                output = io.StringIO()
                errors = io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(
                    errors
                ):
                    status = proofcheck.cmd_revalidate_protocol(
                        argparse.Namespace(root=self.audit)
                    )

                self.assertEqual(1, status)
                self.assertEqual("failed", json.loads(output.getvalue())["status"])
                self.assertEqual(
                    "0" * 64,
                    read_json(manifest_path)["protocol"]["validator_sha256"],
                )
                self.assertTrue(errors.getvalue(), label)

    def test_protocol_revalidation_validates_dependency_registry_shape(
        self,
    ) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["protocol"]["validator_sha256"] = "0" * 64
        write_json(manifest_path, manifest)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["internal_uses"] = {}
        write_json(registry_path, registry)

        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = proofcheck.cmd_revalidate_protocol(
                argparse.Namespace(root=self.audit)
            )

        self.assertEqual(1, status)
        self.assertEqual("failed", json.loads(output.getvalue())["status"])
        self.assertEqual(
            "0" * 64,
            read_json(manifest_path)["protocol"]["validator_sha256"],
        )
        self.assertIn("internal_uses must be a list", errors.getvalue())

    def test_protocol_revalidation_refuses_foreign_finalization_pointer(
        self,
    ) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["protocol"]["validator_sha256"] = "0" * 64
        manifest["finalization_record"] = (
            "Z:\\foreign-audit\\FINALIZATION.json"
        )
        write_json(manifest_path, manifest)

        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = proofcheck.cmd_revalidate_protocol(
                argparse.Namespace(root=self.audit)
            )

        self.assertEqual(1, status)
        self.assertEqual("failed", json.loads(output.getvalue())["status"])
        self.assertEqual(
            "0" * 64,
            read_json(manifest_path)["protocol"]["validator_sha256"],
        )
        self.assertIn("manifest.finalization_record", errors.getvalue())

    def test_protocol_revalidation_refuses_malformed_finalization_record(
        self,
    ) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["protocol"]["validator_sha256"] = "0" * 64
        write_json(manifest_path, manifest)
        (
            self.audit / "audit" / "06_reports" / "FINALIZATION.json"
        ).write_bytes(b"{malformed json")

        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = proofcheck.cmd_revalidate_protocol(
                argparse.Namespace(root=self.audit)
            )

        self.assertEqual(1, status)
        self.assertEqual("failed", json.loads(output.getvalue())["status"])
        self.assertEqual(
            "0" * 64,
            read_json(manifest_path)["protocol"]["validator_sha256"],
        )
        self.assertIn("Cannot read finalization record", errors.getvalue())

    def test_status_rejects_incompatible_current_manifest_protocol(self) -> None:
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["protocol"]["closure_contract_version"] = 999
        write_json(manifest_path, manifest)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                    verbose=False,
                )
            )
        payload = json.loads(output.getvalue())

        self.assertEqual(1, status)
        self.assertEqual("mismatch", payload["protocol"]["status"])
        self.assertEqual("malformed_or_stale", payload["workflow_state"])
        self.assertIn("Re-scaffold", payload["progress"]["next_action"])

    def test_upgrade_required_does_not_mask_malformed_legacy_state(
        self,
    ) -> None:
        ledger_path = self.downgrade_complete_audit_to_schema4()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        paper_bytes = self.paper.read_bytes()
        ledger_bytes = ledger_path.read_bytes()
        manifest_bytes = manifest_path.read_bytes()

        for case in (
            "source_drift",
            "ledger_integrity",
            "structural_read",
        ):
            with self.subTest(case=case):
                self.paper.write_bytes(paper_bytes)
                ledger_path.write_bytes(ledger_bytes)
                manifest_path.write_bytes(manifest_bytes)
                if case == "source_drift":
                    self.paper.write_text(
                        self.paper.read_text(encoding="utf-8")
                        + "% changed after legacy audit\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                elif case == "ledger_integrity":
                    ledger = read_json(ledger_path)
                    ledger["source_lines"][0]["sha256"] = "0" * 64
                    write_json(ledger_path, ledger)
                else:
                    manifest_path.write_text(
                        "{malformed json",
                        encoding="utf-8",
                        newline="\n",
                    )

                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    status = proofcheck.cmd_status(
                        argparse.Namespace(
                            root=self.audit,
                            format="json",
                            output=None,
                            force=False,
                            verbose=False,
                        )
                    )
                payload = json.loads(output.getvalue())

                self.assertEqual(1, status)
                self.assertEqual(
                    "malformed_or_stale", payload["workflow_state"]
                )

    def test_status_reconciles_stale_partition_and_completed_active_unit(
        self,
    ) -> None:
        complete_path = self.make_complete_audit()
        pending_path = complete_path.with_name("lem-pending.ledger.json")
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=self.paper,
                    start=2,
                    end=7,
                    statement_file=self.paper,
                    statement_start=2,
                    statement_end=4,
                    separate_statement_reason=None,
                    unit_id="lem:pending",
                    output=pending_path,
                    force=False,
                )
            )

        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        pending_unit = json.loads(json.dumps(inventory["units"][0]))
        pending_unit["id"] = "lem:pending"
        pending_unit["label"] = "lem:pending"
        pending_unit["proof_association"]["target"] = "lem:pending"
        inventory["units"].append(pending_unit)
        write_json(inventory_path, inventory)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["in_scope_units"] = [
            "lem:main",
            "lem:pending",
        ]
        write_json(manifest_path, manifest)

        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["completed_units"] = []
        progress["active_unit"] = "lem:main"
        write_json(progress_path, progress)

        status_output = io.StringIO()
        with contextlib.redirect_stdout(status_output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                    verbose=False,
                )
            )
        payload = json.loads(status_output.getvalue())
        drift = "\n".join(payload["progress"]["drift"])

        self.assertEqual(1, status)
        self.assertEqual("malformed_or_stale", payload["workflow_state"])
        self.assertIn("completed_units:", drift)
        self.assertIn("active_unit is already completed", drift)
        self.assertCountEqual(
            ["lem:main"], payload["progress"]["completed_units"]
        )
        self.assertCountEqual(
            ["lem:pending"], payload["progress"]["not_started_units"]
        )

    def test_source_drift_blocks_checkpoint_and_marks_status_malformed(self) -> None:
        progress_path = self.audit / "PROGRESS.json"
        original_progress = read_json(progress_path)
        self.paper.write_text(
            self.paper.read_text(encoding="utf-8") + "% changed after scaffold\n",
            encoding="utf-8",
            newline="\n",
        )

        with self.assertRaisesRegex(ValueError, "Source drift"):
            proofcheck.cmd_checkpoint(
                argparse.Namespace(
                    root=self.audit,
                    active_unit="lem:main",
                    clear_active_unit=False,
                    next_action="Reconcile the changed source before continuing.",
                )
            )

        self.assertEqual(original_progress, read_json(progress_path))
        status_output = io.StringIO()
        with contextlib.redirect_stdout(status_output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                    verbose=False,
                )
            )
        payload = json.loads(status_output.getvalue())

        self.assertEqual(1, status)
        self.assertEqual("malformed_or_stale", payload["workflow_state"])
        self.assertIn("Source drift", json.dumps(payload))

    def test_status_marks_a_complete_preflight_as_finalizable(self) -> None:
        self.make_complete_audit()
        status_output = io.StringIO()
        with contextlib.redirect_stdout(status_output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                    verbose=False,
                )
            )
        payload = json.loads(status_output.getvalue())

        self.assertEqual(0, status)
        self.assertEqual("finalizable", payload["workflow_state"])
        self.assertEqual([], payload["progress"]["drift"])
        self.assertCountEqual(
            ["lem:main"], payload["progress"]["completed_units"]
        )

    def test_checkpoint_migrates_legacy_progress_without_in_progress_units(
        self,
    ) -> None:
        self.make_complete_audit()
        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress.pop("in_progress_units")
        write_json(progress_path, progress)

        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_checkpoint(
                argparse.Namespace(
                    root=self.audit,
                    active_unit=None,
                    clear_active_unit=True,
                    next_action=(
                        "Audit complete; rerun finalization after any artifact change."
                    ),
                )
            )

        migrated = read_json(progress_path)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual(0, status)
        self.assertEqual([], migrated["in_progress_units"])
        self.assertEqual("complete", migrated["status"])
        self.assertEqual([], errors)

    def test_checkpoint_stages_new_next_action_before_completion_gate(self) -> None:
        self.make_complete_audit()
        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["next_action"] = "TBD"
        write_json(progress_path, progress)
        replacement = (
            "Audit complete; rerun finalization after any source or artifact change."
        )

        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_checkpoint(
                argparse.Namespace(
                    root=self.audit,
                    active_unit=None,
                    clear_active_unit=True,
                    next_action=replacement,
                )
            )

        updated = read_json(progress_path)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual(0, status)
        self.assertEqual(replacement, updated["next_action"])
        self.assertEqual(8, updated["current_pass"])
        self.assertEqual("complete", updated["status"])
        self.assertEqual([], errors)

    def test_checkpoint_rejects_an_already_completed_active_unit(self) -> None:
        self.make_complete_audit()
        progress_path = self.audit / "PROGRESS.json"
        original = read_json(progress_path)

        with self.assertRaisesRegex(ValueError, "active unit is already completed"):
            proofcheck.cmd_checkpoint(
                argparse.Namespace(
                    root=self.audit,
                    active_unit="lem:main",
                    clear_active_unit=False,
                    next_action="Continue work on a unit that is already complete.",
                )
            )

        self.assertEqual(original, read_json(progress_path))

    def test_checkpoint_derives_passes_five_through_eight(self) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        progress_path = self.audit / "PROGRESS.json"

        def checkpoint(next_action: str) -> tuple[int, str]:
            with contextlib.redirect_stdout(io.StringIO()):
                proofcheck.cmd_checkpoint(
                    argparse.Namespace(
                        root=self.audit,
                        active_unit=None,
                        clear_active_unit=True,
                        next_action=next_action,
                    )
                )
            progress = read_json(progress_path)
            return progress["current_pass"], progress["status"]

        manifest = read_json(manifest_path)
        manifest["completion"]["dependency_registry_reviewed"] = False
        write_json(manifest_path, manifest)
        pass_five = checkpoint("Complete the remaining system-level reviews.")

        manifest = read_json(manifest_path)
        manifest["completion"]["dependency_registry_reviewed"] = True
        manifest["audit_scope"]["critical_units"] = []
        write_json(manifest_path, manifest)
        pass_six = checkpoint("Complete the independent critical-path challenge.")

        manifest = read_json(manifest_path)
        manifest["audit_scope"]["critical_units"] = ["lem:main"]
        manifest["completion"]["final_report_ready"] = False
        write_json(manifest_path, manifest)
        pass_seven = checkpoint("Finish and reconcile the final report.")

        manifest = read_json(manifest_path)
        manifest["completion"]["final_report_ready"] = True
        write_json(manifest_path, manifest)
        pass_eight = checkpoint(
            "Audit complete; rerun finalization after any source or artifact change."
        )

        self.assertEqual([5, 6, 7, 8], [
            pass_five[0],
            pass_six[0],
            pass_seven[0],
            pass_eight[0],
        ])
        self.assertEqual(
            ["in_progress", "in_progress", "in_progress", "complete"],
            [pass_five[1], pass_six[1], pass_seven[1], pass_eight[1]],
        )

    def test_checkpoint_does_not_claim_completion_when_strict_gates_fail(
        self,
    ) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "Overall assessment code: no_defect_found",
            "Overall assessment code: defects_found",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")
        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["status"] = "in_progress"
        progress["current_pass"] = 7
        write_json(progress_path, progress)

        with contextlib.redirect_stdout(io.StringIO()):
            checkpoint_status = proofcheck.cmd_checkpoint(
                argparse.Namespace(
                    root=self.audit,
                    active_unit=None,
                    clear_active_unit=True,
                    next_action="Correct the final report assessment before finalization.",
                )
            )
        checkpoint = read_json(progress_path)

        status_output = io.StringIO()
        with contextlib.redirect_stdout(status_output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                    verbose=False,
                )
            )
        payload = json.loads(status_output.getvalue())

        self.assertEqual(0, checkpoint_status)
        self.assertNotEqual("complete", checkpoint["status"])
        self.assertEqual(1, status)
        self.assertEqual("malformed_or_stale", payload["workflow_state"])
        self.assertIn("Final report assessment disagrees", json.dumps(payload))

    def test_failed_finalization_record_makes_status_nonzero(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            self.assertEqual(
                1,
                proofcheck.cmd_finalize(argparse.Namespace(root=self.audit)),
            )
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                )
            )
        freshness = proofcheck.check_finalization_freshness(self.audit)

        self.assertEqual(1, status)
        self.assertEqual("failed", freshness["record_status"])
        self.assertEqual("current", freshness["freshness"])
        self.assertFalse(freshness["usable_finalization"])

    def test_legacy_finalization_record_can_still_be_verified(self) -> None:
        self.make_complete_audit()
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_finalize(argparse.Namespace(root=self.audit))
        record_path = self.audit / "audit" / "06_reports" / "FINALIZATION.json"
        record = read_json(record_path)
        record.pop("finalization_schema_version")
        record.pop("artifact_manifest")
        record.pop("record_payload_sha256")
        write_json(record_path, record)

        freshness = proofcheck.check_finalization_freshness(self.audit)

        self.assertEqual("current", freshness["freshness"])
        self.assertTrue(freshness["usable_finalization"])

    def test_status_refuses_to_mutate_a_finalized_audit_root(self) -> None:
        self.make_complete_audit()
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_finalize(argparse.Namespace(root=self.audit))

        with self.assertRaisesRegex(ValueError, "inside an audit root"):
            proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=self.audit / "STATUS.json",
                    force=False,
                )
            )

    def test_malformed_finalization_record_path_is_invalid(self) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["finalization_record"] = {"file": "not-a-string"}
        write_json(manifest_path, manifest)

        freshness = proofcheck.check_finalization_freshness(self.audit)
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                )
            )

        self.assertEqual(1, status)
        self.assertEqual("invalid", freshness["record_status"])
        self.assertEqual("unknown", freshness["freshness"])
        self.assertTrue(
            any(
                "finalization_record" in reason
                for reason in freshness["stale_reasons"]
            ),
            freshness,
        )

    def test_markdown_status_keeps_key_gate_error_when_bounded(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            self.assertEqual(
                1,
                proofcheck.cmd_finalize(argparse.Namespace(root=self.audit)),
            )
        status_output = io.StringIO()
        with contextlib.redirect_stdout(status_output):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="markdown",
                    output=None,
                    force=False,
                    verbose=False,
                )
            )

        markdown = status_output.getvalue()
        self.assertEqual(1, status)
        self.assertIn("at least one proof-unit ledger", markdown)
        self.assertIn("additional errors omitted; rerun status --verbose", markdown)
        self.assertLessEqual(len(markdown.splitlines()), 80)

    def test_explicit_missing_local_package_emits_warning(self) -> None:
        root = self.base / "missing-package.tex"
        root.write_text(
            "\\usepackage{./missing}\n",
            encoding="utf-8",
            newline="\n",
        )

        closure = proofcheck.discover_source_closure(root)

        self.assertTrue(
            any(
                "Explicit local class or package not found" in warning
                for warning in closure["warnings"]
            ),
            closure,
        )

    def test_fls_missing_main_paper_emits_warning(self) -> None:
        recorder_source = self.base / "only-dependency.sty"
        recorder_source.write_text(
            "\\ProvidesPackage{only-dependency}\n",
            encoding="utf-8",
            newline="\n",
        )
        fls = self.base / "incomplete.fls"
        fls.write_text(
            f"PWD {self.base}\nINPUT {recorder_source}\n",
            encoding="utf-8",
            newline="\n",
        )

        closure = proofcheck.discover_source_closure(
            self.paper,
            fls_file=fls,
            project_root=self.base,
        )

        self.assertTrue(
            any(
                "does not include the main paper" in warning.lower()
                for warning in closure["warnings"]
            ),
            closure,
        )

    def test_finalization_result_counts_the_full_parser_warning_set(self) -> None:
        self.paper.write_text(
            self.paper.read_text(encoding="utf-8").replace(
                "\\cite{smith}.",
                "\\cite{smith} and \\mycite{unknown}.",
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.audit = self.base / "inventory-warning-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(paper=self.paper, output=self.audit)
            )
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        self.assertTrue(manifest["parser_warnings"])
        for review in manifest["parser_warning_reviews"]:
            review.update(
                {
                    "disposition": "confirmed_non_load_bearing",
                    "affected_units": ["lem:main"],
                    "evidence": "The unsupported citation macro affects attribution only.",
                }
            )
        write_json(manifest_path, manifest)

        errors, result = proofcheck.check_audit_finalization(self.audit)

        self.assertEqual([], errors)
        self.assertEqual(
            len(manifest["parser_warnings"]),
            result["parser_warnings"],
        )

    def test_unreadable_local_style_is_locked_and_reported(self) -> None:
        unreadable_style = self.base / "unreadable.sty"
        unreadable_style.write_bytes(b"\\ProvidesPackage{unreadable}\n\xff\xfe\n")
        self.paper.write_text(
            self.paper.read_text(encoding="utf-8")
            + "\\usepackage{./unreadable}\n",
            encoding="utf-8",
            newline="\n",
        )
        self.audit = self.base / "unreadable-style-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(paper=self.paper, output=self.audit)
            )

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        locked_files = {
            proofcheck.resolve_stored_path(row["file"], self.audit)
            for row in manifest["source_snapshot"]["files"]
        }
        self.assertIn(unreadable_style.resolve(), locked_files)
        self.assertTrue(
            any("Cannot decode" in warning for warning in manifest["parser_warnings"]),
            manifest,
        )

        self.make_complete_audit()
        manifest = read_json(manifest_path)
        for review in manifest["parser_warning_reviews"]:
            review.update(
                {
                    "disposition": "confirmed_non_load_bearing",
                    "affected_units": [],
                    "evidence": "The unreadable style defines no audited proof content.",
                }
            )
        write_json(manifest_path, manifest)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            status = proofcheck.cmd_finalize(argparse.Namespace(root=self.audit))

        self.assertEqual(0, status)
        record = read_json(
            self.audit / "audit" / "06_reports" / "FINALIZATION.json"
        )
        self.assertEqual("passed", record["status"])

    def test_invalid_utf8_manifest_returns_errors(self) -> None:
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest_path.write_bytes(b"{\xff}")

        errors, result = proofcheck.check_audit_finalization(self.audit)
        freshness = proofcheck.check_finalization_freshness(self.audit)

        self.assertTrue(any("Cannot read audit manifest" in error for error in errors))
        self.assertEqual(len(errors), result["errors"])
        self.assertEqual("invalid", freshness["record_status"])
        self.assertEqual("unknown", freshness["freshness"])

    def test_invalid_utf8_finalization_record_returns_errors(self) -> None:
        self.make_complete_audit()
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_finalize(argparse.Namespace(root=self.audit))
        record_path = self.audit / "audit" / "06_reports" / "FINALIZATION.json"
        record_path.write_bytes(b"{\xff}")

        freshness = proofcheck.check_finalization_freshness(self.audit)
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                )
            )

        self.assertEqual(1, status)
        self.assertEqual("invalid", freshness["record_status"])
        self.assertEqual("unknown", freshness["freshness"])
        self.assertTrue(
            any(
                "Cannot read finalization record" in reason
                for reason in freshness["stale_reasons"]
            ),
            freshness,
        )

    def test_invalid_utf8_ledger_returns_errors(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger_path.write_bytes(b"{\xff}")

        errors, result = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(any("Cannot read ledger" in error for error in errors), errors)
        self.assertGreater(result["errors"], 0)

    def test_invalid_utf8_issue_log_returns_errors(self) -> None:
        self.make_complete_audit()
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        issue_path.write_bytes(b"{\xff}")

        errors, result = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(any("Cannot read issue log" in error for error in errors), errors)
        self.assertGreater(result["errors"], 0)

    def test_invalid_utf8_canonical_text_artifacts_return_controlled_errors(
        self,
    ) -> None:
        self.make_complete_audit()
        paths = (
            self.audit / "audit" / "06_reports" / "FINAL_REPORT.md",
            self.audit / "audit" / "06_reports" / "ISSUE_SUMMARY.md",
            self.audit / "audit" / "01_index" / "cross_reference_audit.md",
        )
        baselines = {path: path.read_bytes() for path in paths}
        for path in paths:
            with self.subTest(path=path.name):
                path.write_bytes(b"\xff\xfe")

                errors, result = proofcheck.check_audit_finalization(
                    self.audit
                )

                self.assertTrue(
                    any(
                        "Unreadable UTF-8 text artifact" in error
                        and path.name in error
                        for error in errors
                    ),
                    errors,
                )
                self.assertGreater(result["errors"], 0)
                path.write_bytes(baselines[path])

    def test_invalid_utf8_declared_report_returns_controlled_error(self) -> None:
        canonical_report, user_report = (
            self.install_declared_user_report_with_orientation(
                "This reader-facing orientation remains within audit scope."
            )
        )
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        old_digest = manifest["report_deliverables"][0]["sha256"]
        user_report.write_bytes(b"\xff\xfe")
        new_digest = proofcheck.sha256_file(user_report)
        manifest["report_deliverables"][0]["sha256"] = new_digest
        write_json(manifest_path, manifest)
        canonical_report.write_text(
            canonical_report.read_text(encoding="utf-8").replace(
                old_digest,
                new_digest,
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )

        errors, result = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "report_deliverables[1]" in error
                and "Unreadable UTF-8 text artifact" in error
                and "USER_REPORT.md" in error
                for error in errors
            ),
            errors,
        )
        self.assertGreater(result["errors"], 0)

    def test_invalid_utf8_source_file_returns_controlled_error(self) -> None:
        self.make_complete_audit()
        self.paper.write_bytes(b"\xff\xfe")

        errors, result = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "Unreadable UTF-8 text artifact" in error
                and self.paper.name in error
                for error in errors
            ),
            errors,
        )
        self.assertGreater(result["errors"], 0)

    def test_nested_input_resolution_locks_both_ambiguous_candidates(self) -> None:
        sections = self.base / "sections"
        sections.mkdir()
        root = self.base / "nested-main.tex"
        nested = sections / "part.tex"
        containing_candidate = sections / "shared.tex"
        project_candidate = self.base / "shared.tex"
        root.write_text(
            "\\input{sections/part}\n",
            encoding="utf-8",
            newline="\n",
        )
        nested.write_text(
            "\\input{shared}\n",
            encoding="utf-8",
            newline="\n",
        )
        containing_candidate.write_text(
            "Containing-file candidate.\n",
            encoding="utf-8",
            newline="\n",
        )
        project_candidate.write_text(
            "Project-root candidate.\n",
            encoding="utf-8",
            newline="\n",
        )

        closure = proofcheck.discover_source_closure(
            root,
            project_root=self.base,
        )

        self.assertIn(containing_candidate.resolve(), closure["files"])
        self.assertIn(project_candidate.resolve(), closure["files"])
        self.assertTrue(
            any(
                "Ambiguous include resolution" in warning
                for warning in closure["warnings"]
            ),
            closure,
        )

    def assert_scaffold_rejected_before_output(
        self,
        output: Path,
        expected_exception: type[Exception],
        *,
        additional_source: list[tuple[str, str, str]] | None = None,
        fls: Path | None = None,
    ) -> None:
        self.assertFalse(output.exists())
        with self.assertRaises(expected_exception):
            proofcheck.cmd_scaffold(
                argparse.Namespace(
                    paper=self.paper,
                    output=output,
                    additional_source=additional_source,
                    fls=fls,
                )
            )
        self.assertFalse(output.exists())

    def test_scaffold_rejects_missing_additional_source_before_writing(self) -> None:
        self.assert_scaffold_rejected_before_output(
            self.base / "missing-additional-audit",
            FileNotFoundError,
            additional_source=[
                (
                    str(self.base / "missing-supplement.tex"),
                    "The file was declared as proof context.",
                    "The declaration came from the audit plan.",
                )
            ],
        )

    def test_scaffold_rejects_duplicate_additional_source_before_writing(self) -> None:
        additional = self.base / "duplicate-supplement.tex"
        additional.write_text("Supplement.\n", encoding="utf-8", newline="\n")
        self.assert_scaffold_rejected_before_output(
            self.base / "duplicate-additional-audit",
            ValueError,
            additional_source=[
                (
                    str(additional),
                    "First declaration.",
                    "First evidence record.",
                ),
                (
                    str(additional.resolve()),
                    "Second declaration.",
                    "Second evidence record.",
                ),
            ],
        )

    def test_scaffold_rejects_blank_additional_metadata_before_writing(self) -> None:
        additional = self.base / "metadata-supplement.tex"
        additional.write_text("Supplement.\n", encoding="utf-8", newline="\n")
        cases = {
            "reason": ("   ", "Evidence is present."),
            "evidence": ("Reason is present.", "   "),
        }
        for label, (reason, evidence) in cases.items():
            with self.subTest(field=label):
                self.assert_scaffold_rejected_before_output(
                    self.base / f"blank-{label}-audit",
                    ValueError,
                    additional_source=[
                        (str(additional), reason, evidence)
                    ],
                )

    def test_scaffold_rejects_missing_fls_before_writing(self) -> None:
        self.assert_scaffold_rejected_before_output(
            self.base / "missing-fls-audit",
            FileNotFoundError,
            fls=self.base / "missing-paper.fls",
        )

    def test_external_finalization_target_is_not_overwritten(self) -> None:
        self.make_complete_audit()
        outside_record = self.base / "outside-finalization.json"
        outside_record.write_text(
            "outside sentinel\n",
            encoding="utf-8",
            newline="\n",
        )
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["finalization_record"] = proofcheck.relative_or_absolute(
            outside_record,
            self.audit,
        )
        write_json(manifest_path, manifest)

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            finalize_status = proofcheck.cmd_finalize(
                argparse.Namespace(root=self.audit)
            )
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                )
            )
        freshness = proofcheck.check_finalization_freshness(self.audit)

        self.assertEqual(1, finalize_status)
        self.assertEqual(1, status)
        self.assertEqual("outside sentinel\n", outside_record.read_text(encoding="utf-8"))
        self.assertEqual("invalid", freshness["record_status"])
        self.assertEqual("unknown", freshness["freshness"])
        self.assertTrue(
            any("must resolve to" in reason for reason in freshness["stale_reasons"]),
            freshness,
        )

    def test_external_dependency_registry_cannot_be_finalized_or_stay_current(
        self,
    ) -> None:
        self.make_complete_audit()
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        outside_registry = self.base / "outside-dependency-registry.json"
        outside_registry.write_bytes(registry_path.read_bytes())
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["dependency_registry"] = "../outside-dependency-registry.json"
        write_json(manifest_path, manifest)

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            finalize_status = proofcheck.cmd_finalize(
                argparse.Namespace(root=self.audit)
            )
        changed = read_json(outside_registry)
        changed["review"]["evidence"] = [
            "This external evidence changed after finalization."
        ]
        write_json(outside_registry, changed)
        freshness = proofcheck.check_finalization_freshness(self.audit)

        self.assertEqual(1, finalize_status)
        self.assertFalse(freshness["usable_finalization"], freshness)
        self.assertTrue(
            any(
                "manifest.dependency_registry must resolve to" in error
                for error in freshness["current_gate_errors"]
            ),
            freshness,
        )

    def test_manifest_artifact_paths_require_exact_canonical_locations(self) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        original = read_json(manifest_path)
        cases = {
            "inventory_file": "../outside-inventory.json",
            "dependency_registry": "../outside-dependencies.json",
            "method_interface_registry": "../outside-interfaces.json",
            "finalization_record": "../outside-finalization.json",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                changed = json.loads(json.dumps(original))
                changed[field] = value
                write_json(manifest_path, changed)
                errors, _ = proofcheck.check_audit_finalization(self.audit)
                self.assertTrue(
                    any(
                        f"manifest.{field} must resolve to" in error
                        for error in errors
                    ),
                    errors,
                )

        changed = json.loads(json.dumps(original))
        changed["dependency_registry"] = (
            "audit/03_dependencies/../dependencies/DEPENDENCY_REGISTRY.json"
        )
        write_json(manifest_path, changed)
        traversal_errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "manifest.dependency_registry must resolve to" in error
                for error in traversal_errors
            ),
            traversal_errors,
        )

        changed = json.loads(json.dumps(original))
        changed["inventory_file"] = original["inventory_file"].replace("/", "\\")
        write_json(manifest_path, changed)
        legacy_separator_errors, _ = proofcheck.check_audit_finalization(
            self.audit
        )
        self.assertFalse(
            any(
                "manifest.inventory_file" in error
                for error in legacy_separator_errors
            ),
            legacy_separator_errors,
        )

    def test_status_reports_foreign_and_malformed_artifact_paths_structurally(
        self,
    ) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        original = read_json(manifest_path)
        cases = (
            "Z:\\foreign-audit\\theorem_inventory.json",
            {"file": "audit/01_index/theorem_inventory.json"},
        )
        for value in cases:
            with self.subTest(value=repr(value)):
                changed = json.loads(json.dumps(original))
                changed["inventory_file"] = value
                write_json(manifest_path, changed)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    status = proofcheck.cmd_status(
                        argparse.Namespace(
                            root=self.audit,
                            format="json",
                            output=None,
                            force=False,
                            verbose=True,
                        )
                    )
                payload = json.loads(output.getvalue())
                self.assertEqual(1, status)
                self.assertEqual("malformed_or_stale", payload["workflow_state"])
                self.assertTrue(
                    any(
                        "manifest.inventory_file" in error
                        for error in payload["structural_errors"]
                    ),
                    payload,
                )

    def test_fixed_canonical_artifacts_reject_redirecting_components(self) -> None:
        self.make_complete_audit()
        targets = {
            "audit manifest": self.audit / "AUDIT_MANIFEST.json",
            "proof-unit inventory": (
                self.audit / "audit" / "01_index" / "theorem_inventory.json"
            ),
            "cross-reference audit JSON": (
                self.audit
                / "audit"
                / "01_index"
                / "cross_reference_audit.json"
            ),
            "cross-reference audit Markdown": (
                self.audit
                / "audit"
                / "01_index"
                / "cross_reference_audit.md"
            ),
            "dependency registry": (
                self.audit
                / "audit"
                / "03_dependencies"
                / "DEPENDENCY_REGISTRY.json"
            ),
            "method-interface registry": (
                self.audit
                / "audit"
                / "03_dependencies"
                / "METHOD_INTERFACE_REGISTRY.json"
            ),
            "issue log": (
                self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
            ),
            "issue summary": (
                self.audit / "audit" / "06_reports" / "ISSUE_SUMMARY.md"
            ),
            "progress record": self.audit / "PROGRESS.json",
            "final report": (
                self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
            ),
            "finalization record": (
                self.audit / "audit" / "06_reports" / "FINALIZATION.json"
            ),
        }
        original_redirect_kind = proofcheck.path_redirect_kind
        for label, target in targets.items():
            with self.subTest(label=label):
                def simulated_redirect_kind(path: Path) -> str | None:
                    if path == target:
                        return "junction"
                    return original_redirect_kind(path)

                with mock.patch.object(
                    proofcheck,
                    "path_redirect_kind",
                    side_effect=simulated_redirect_kind,
                ):
                    errors, _ = proofcheck.check_audit_finalization(self.audit)
                self.assertTrue(
                    any(
                        f"Canonical {label} location traverses a junction"
                        in error
                        for error in errors
                    ),
                    errors,
                )

    def test_canonical_artifacts_reject_redirecting_ancestor(self) -> None:
        self.make_complete_audit()
        redirected_ancestor = self.audit / "audit" / "03_dependencies"
        original_redirect_kind = proofcheck.path_redirect_kind

        def simulated_redirect_kind(path: Path) -> str | None:
            if path == redirected_ancestor:
                return "junction"
            return original_redirect_kind(path)

        with mock.patch.object(
            proofcheck,
            "path_redirect_kind",
            side_effect=simulated_redirect_kind,
        ):
            errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "Canonical dependency registry location traverses a junction"
                in error
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any(
                "Canonical method-interface registry location traverses a junction"
                in error
                for error in errors
            ),
            errors,
        )

    def test_manifest_cannot_be_used_as_finalization_target(self) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["finalization_record"] = "AUDIT_MANIFEST.json"
        write_json(manifest_path, manifest)
        sentinel = manifest_path.read_bytes()

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            finalize_status = proofcheck.cmd_finalize(
                argparse.Namespace(root=self.audit)
            )

        self.assertEqual(1, finalize_status)
        self.assertEqual(sentinel, manifest_path.read_bytes())
        self.assertTrue(
            (self.audit / "audit" / "06_reports" / "FINALIZATION.json").is_file()
        )

    def test_finalization_schema_rejects_bool_and_float_one(self) -> None:
        self.make_complete_audit()
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_finalize(argparse.Namespace(root=self.audit))
        record_path = self.audit / "audit" / "06_reports" / "FINALIZATION.json"
        original = read_json(record_path)

        for schema_value in (True, 1.0):
            with self.subTest(schema_value=repr(schema_value)):
                changed = json.loads(json.dumps(original))
                changed["finalization_schema_version"] = schema_value
                write_json(record_path, changed)

                freshness = proofcheck.check_finalization_freshness(self.audit)

                self.assertEqual("invalid", freshness["record_status"])
                self.assertEqual("unknown", freshness["freshness"])
                self.assertTrue(
                    any(
                        "unsupported finalization_schema_version" in reason
                        for reason in freshness["stale_reasons"]
                    ),
                    freshness,
                )

    def test_schema_one_finalization_requires_generated_utc(self) -> None:
        self.make_complete_audit()
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_finalize(argparse.Namespace(root=self.audit))
        record_path = self.audit / "audit" / "06_reports" / "FINALIZATION.json"
        record = read_json(record_path)
        record.pop("generated_utc")
        write_json(record_path, record)

        freshness = proofcheck.check_finalization_freshness(self.audit)

        self.assertEqual("invalid", freshness["record_status"])
        self.assertEqual("unknown", freshness["freshness"])
        self.assertTrue(
            any("requires generated_utc" in reason for reason in freshness["stale_reasons"]),
            freshness,
        )

    def test_parser_warning_affected_units_reject_duplicates(self) -> None:
        manifest_path = self.rebuild_with_parser_warning()
        manifest = read_json(manifest_path)
        manifest["parser_warning_reviews"][0].update(
            {
                "disposition": "confirmed_non_load_bearing",
                "affected_units": ["lem:main", "lem:main"],
                "evidence": "The warning was reviewed against the only proof unit.",
            }
        )
        write_json(manifest_path, manifest)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("affected_units contains duplicates" in error for error in errors),
            errors,
        )

    def test_parser_warning_malformed_affected_units_returns_errors(self) -> None:
        manifest_path = self.rebuild_with_parser_warning()
        original = read_json(manifest_path)
        malformed_values = (None, {"lem:main": True}, [{}])
        for value in malformed_values:
            with self.subTest(value=repr(value)):
                manifest = json.loads(json.dumps(original))
                manifest["parser_warning_reviews"][0].update(
                    {
                        "disposition": "confirmed_non_load_bearing",
                        "affected_units": value,
                        "evidence": (
                            "The warning was reviewed against the focused proof unit."
                        ),
                    }
                )
                write_json(manifest_path, manifest)
                try:
                    errors, _ = proofcheck.check_audit_finalization(self.audit)
                except (TypeError, ValueError) as exc:
                    self.fail(f"Malformed affected_units raised {type(exc).__name__}: {exc}")
                self.assertTrue(
                    any("affected_units" in error for error in errors),
                    errors,
                )

    def test_global_consistency_placeholder_evidence_fails(self) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["completion"]["global_consistency_pass"]["checks"][0][
            "evidence"
        ] = "TBD"
        write_json(manifest_path, manifest)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "global_consistency_pass" in error and "evidence" in error
                for error in errors
            ),
            errors,
        )

    def test_adversarial_pass_placeholder_evidence_fails(self) -> None:
        self.make_complete_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["completion"]["adversarial_pass"]["evidence"] = ["TBD"]
        write_json(manifest_path, manifest)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "adversarial_pass.evidence" in error
                and "substantive" in error.lower()
                for error in errors
            ),
            errors,
        )

    def test_dependency_registry_review_binding_is_exact(self) -> None:
        self.make_complete_audit()
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        original = read_json(registry_path)
        cases = {
            "status": lambda item: item["review"].__setitem__(
                "status", "not_reviewed"
            ),
            "source_snapshot_sha256": lambda item: item["review"].__setitem__(
                "source_snapshot_sha256", "0" * 64
            ),
            "inventory_sha256": lambda item: item["review"].__setitem__(
                "inventory_sha256", "0" * 64
            ),
            "in_scope_units": lambda item: item["review"].__setitem__(
                "in_scope_units", []
            ),
            "evidence": lambda item: item["review"].__setitem__(
                "evidence", ["TBD"]
            ),
            "closure_contract_version": lambda item: item.__setitem__(
                "closure_contract_version", 999
            ),
        }
        for field, mutate in cases.items():
            with self.subTest(field=field):
                registry = json.loads(json.dumps(original))
                mutate(registry)
                write_json(registry_path, registry)
                errors, _ = proofcheck.check_audit_finalization(self.audit)
                self.assertTrue(
                    any(field in error for error in errors),
                    errors,
                )

    def test_progress_state_must_be_an_exact_partition(self) -> None:
        self.make_complete_audit()
        progress_path = self.audit / "PROGRESS.json"
        original = read_json(progress_path)
        cases = {
            "unknown completed unit": lambda item: item["completed_units"].append(
                "lem:ghost"
            ),
            "conditional and completed": lambda item: item[
                "conditional_units"
            ].append("lem:main"),
            "not started and completed": lambda item: item[
                "not_started_units"
            ].append("lem:main"),
            "stale source snapshot": lambda item: item.__setitem__(
                "source_snapshot_sha256", "0" * 64
            ),
        }
        for label, mutate in cases.items():
            with self.subTest(case=label):
                progress = json.loads(json.dumps(original))
                mutate(progress)
                write_json(progress_path, progress)
                errors, _ = proofcheck.check_audit_finalization(self.audit)
                self.assertTrue(
                    any("PROGRESS.json" in error for error in errors),
                    errors,
                )

    def test_progress_scaffold_pass_zero_blocks_finalization(self) -> None:
        self.make_complete_audit()
        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["current_pass"] = 0
        write_json(progress_path, progress)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("current_pass" in error and "8" in error for error in errors),
            errors,
        )

    def test_full_audit_cannot_exclude_a_proof_unit(self) -> None:
        self.make_complete_audit()
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        excluded = json.loads(json.dumps(inventory["units"][0]))
        excluded["id"] = "lem:excluded"
        excluded["label"] = "lem:excluded"
        inventory["units"].append(excluded)
        write_json(inventory_path, inventory)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["depth"] = "full"
        manifest["audit_scope"]["excluded_units"] = [
            {
                "id": "lem:excluded",
                "reason": "The proof unit was intentionally excluded for this test.",
            }
        ]
        manifest["audit_scope"]["inventory_overrides"] = [
            {
                "unit_id": "lem:excluded",
                "kind": "manual_unit",
                "reason": "Rendered-source review identified a companion proof unit.",
                "evidence": "The statement and proof are visible in the rendered source.",
            }
        ]
        write_json(manifest_path, manifest)
        self.refresh_dependency_review()

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("full" in error.lower() and "exclud" in error.lower() for error in errors),
            errors,
        )

    def test_final_report_rejects_duplicate_singleton_fields(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "- Overall judgment:",
            "- Overall assessment code: defects_found\n- Overall judgment:",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("duplicate" in error.lower() and "Overall assessment code" in error for error in errors),
            errors,
        )

    def test_hidden_report_contract_cannot_satisfy_required_content(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        baseline = report_path.read_text(encoding="utf-8")
        wrappers = {
            "html-comment": f"<!--\n{baseline}\n-->\n",
            "fenced-code": f"```markdown\n{baseline}\n```\n",
            "hidden-div": f"<div hidden>\n{baseline}\n</div>\n",
            "pre-block": f"<pre>\n{baseline}\n</pre>\n",
        }
        for case, hidden_report in wrappers.items():
            with self.subTest(case=case):
                report_path.write_text(
                    hidden_report,
                    encoding="utf-8",
                    newline="\n",
                )

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                if case in {"hidden-div", "pre-block"}:
                    self.assertTrue(
                        any(
                            "active raw HTML" in error
                            for error in errors
                        ),
                        errors,
                    )
                    continue
                self.assertTrue(
                    any(
                        "missing the Overall assessment code field" in error
                        for error in errors
                    ),
                    errors,
                )
                self.assertTrue(
                    any("missing required heading" in error for error in errors),
                    errors,
                )
        report_path.write_text(baseline, encoding="utf-8", newline="\n")

    def test_markdown_visibility_lexer_distinguishes_literals_from_raw_blocks(
        self,
    ) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        baseline = report_path.read_text(encoding="utf-8")
        safe_literals = {
            "fenced-unmatched-comment": "\n```markdown\n<!--\n```\n",
            "inline-details": "\nThe literal `<details>` tag is discussed.\n",
            "fenced-details": "\n```html\n<details>\n```\n",
            "math-less-than-a": "\nThe admissible range is $x<a>0$.\n",
        }
        for case, addition in safe_literals.items():
            with self.subTest(case=case):
                report_path.write_text(
                    baseline + addition,
                    encoding="utf-8",
                    newline="\n",
                )

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                self.assertEqual([], errors)

        active_raw_blocks = {
            "nested-hidden-div": (
                "\n<div>\n<div hidden>Hidden canonical content.</div>\n"
                "</div>\n"
            ),
            "visible-div": "\n<div>Visible block content.</div>\n",
            "pre": "\n<pre>Hidden canonical content.</pre>\n",
            "textarea": "\n<textarea>Hidden canonical content.</textarea>\n",
            "visibility-hidden": (
                "\n<span style=\"visibility:hidden\">"
                "Hidden canonical content.</span>\n"
            ),
        }
        for case, addition in active_raw_blocks.items():
            with self.subTest(case=case):
                report_path.write_text(
                    baseline + addition,
                    encoding="utf-8",
                    newline="\n",
                )

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                self.assertTrue(
                    any("active raw HTML" in error for error in errors),
                    errors,
                )
        report_path.write_text(baseline, encoding="utf-8", newline="\n")

    def test_indented_canonical_tables_cannot_satisfy_report_contract(
        self,
    ) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        indented = "\n".join(
            f"    {line}" if line.startswith("|") else line
            for line in report.splitlines()
        ) + "\n"
        report_path.write_text(
            indented,
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("invalid table header" in error for error in errors),
            errors,
        )

    def test_visible_report_contract_ignores_hidden_duplicates(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        baseline = report_path.read_text(encoding="utf-8")
        hidden_duplicates = (
            "\n<!--\n"
            "- Overall assessment code: defects_found\n"
            "## Main theorem chain\n"
            "-->\n"
            "```markdown\n"
            "- Overall assessment code: inconclusive\n"
            "## Main theorem chain\n"
            "```\n"
        )
        report_path.write_text(
            baseline + hidden_duplicates,
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertEqual([], errors)

    def test_final_report_rejects_unqualified_correctness_overclaim(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "No defect found under the stated non-formal protocol.",
            "Every theorem and proof in the paper is mathematically correct.",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("overclaim" in error.lower() or "unsupported" in error.lower() for error in errors),
            errors,
        )

    def test_final_report_rejects_active_correctness_overclaim(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report_path.write_text(
            report_path.read_text(encoding="utf-8")
            + "\nThe theorem and its proof are correct.\n",
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("correctness overclaim" in error for error in errors),
            errors,
        )

    def test_final_report_allows_quoted_disclaimed_and_exact_evidence_phrases(
        self,
    ) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        baseline = report_path.read_text(encoding="utf-8")
        additions = {
            "quoted": (
                "\n> Exact manuscript quotation: The theorem and its proof "
                "are correct.\n"
            ),
            "disclaimed": (
                "\nThis audit does not claim that the theorem and its proof "
                "are correct.\n"
            ),
            "exact-evidence": (
                "\n| Failure evidence |\n"
                "|---|\n"
                "| The theorem and its proof are correct. |\n"
            ),
            "unclear-whether": (
                "\nIt remains unclear whether the theorem and its proof "
                "are correct.\n"
            ),
            "unresolved-whether": (
                "\nWhether the lemma and its argument are valid remains "
                "unresolved.\n"
            ),
            "no-evidence": (
                "\nThere is no evidence that the proposition and its "
                "derivation are correct.\n"
            ),
        }
        for case, addition in additions.items():
            with self.subTest(case=case):
                report_path.write_text(
                    baseline + addition,
                    encoding="utf-8",
                    newline="\n",
                )

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                self.assertEqual([], errors)
        report_path.write_text(baseline, encoding="utf-8", newline="\n")

    def test_final_report_rejects_direct_correctness_claims_for_proof_objects(
        self,
    ) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        baseline = report_path.read_text(encoding="utf-8")
        claims = {
            "lemma": "The lemma is correct.",
            "proposition": "This proposition is valid.",
            "corollary": "The corollary is mathematically correct.",
            "result": "This result is valid.",
            "argument": "The argument is correct.",
            "derivation": "This derivation is valid.",
        }
        for case, claim in claims.items():
            with self.subTest(case=case):
                report_path.write_text(
                    baseline + f"\n{claim}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                self.assertTrue(
                    any(
                        "unsupported correctness overclaim" in error
                        for error in errors
                    ),
                    errors,
                )
        report_path.write_text(baseline, encoding="utf-8", newline="\n")

    def test_final_report_checked_scope_must_match_manifest(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "- Checked scope: lem:main",
            "- Checked scope: none",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("Checked scope" in error for error in errors),
            errors,
        )

    def test_final_report_independence_must_match_critical_ledger(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "fresh_context_same_model",
            "none",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("Independence level" in error for error in errors),
            errors,
        )

    def test_independent_challenge_report_row_must_match_ledger(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "| lem:main | agreed | fresh_context_same_model | none | verified | verified |",
            "| lem:main | agreed | fresh_context_same_model | none | incorrect | verified |",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "challenge" in error.lower()
                and ("row" in error.lower() or "ledger" in error.lower())
                for error in errors
            ),
            errors,
        )

    def test_final_report_rejects_fabricated_table_delimiter_row(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        heading = "## Independent critical-path challenges"
        section = proofcheck.report_section(report, heading) or ""
        lines = section.splitlines()
        header_index = next(
            index
            for index, line in enumerate(lines)
            if line.strip().startswith("| Result | Challenge status |")
        )
        width = lines[header_index].count("|") - 1
        lines[header_index + 1] = (
            "| " + " | ".join(["fabricated data"] * width) + " |"
        )
        report_path.write_text(
            proofcheck.replace_report_section_text(
                report,
                heading,
                "\n".join(lines),
            ),
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "Independent critical-path challenges" in error
                for error in errors
            ),
            errors,
        )

    def test_independent_challenge_report_reconciles_disagreements_and_artifact(
        self,
    ) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        original_report = report_path.read_text(encoding="utf-8")
        section_rows = proofcheck.markdown_table_rows(
            proofcheck.report_section(
                original_report,
                "## Independent critical-path challenges",
            )
            or ""
        )
        self.assertEqual("[]", section_rows[2][6])
        self.assertEqual(
            ledger["independent_check"]["artifact"],
            section_rows[2][7],
        )

        for field, column, changed_value in (
            ("disagreements", 6, "[\"fabricated disagreement\"]"),
            ("artifact", 7, "audit/05_adversarial/wrong-artifact.md"),
        ):
            with self.subTest(field=field):
                changed_row = list(section_rows[2])
                changed_row[column] = changed_value
                report_path.write_text(
                    proofcheck.replace_report_section_text(
                        original_report,
                        "## Independent critical-path challenges",
                        proofcheck.render_markdown_table(
                            section_rows[0],
                            [changed_row],
                        ),
                    ),
                    encoding="utf-8",
                    newline="\n",
                )

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                self.assertTrue(
                    any(
                        "Independent critical-path challenges rows disagree"
                        in error
                        for error in errors
                    ),
                    errors,
                )

    def test_final_report_declared_deliverables_scalar_must_match_manifest(
        self,
    ) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report_path.write_text(
            report_path.read_text(encoding="utf-8").replace(
                "- Declared external deliverables: none",
                "- Declared external deliverables: R001",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "Declared external deliverables field disagrees" in error
                for error in errors
            ),
            errors,
        )

    def test_main_chain_row_must_match_ledger_components(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "| lem:main | verified | verified | valid | established | verified |",
            "| lem:main | gap | verified | valid | established | verified |",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("main-chain" in error.lower() or "Main theorem chain" in error for error in errors),
            errors,
        )

    def test_complete_internal_dependency_closure_passes(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertEqual([], errors)

    def test_missing_internal_use_fails_closure(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["internal_uses"] = []
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("internal use" in error.lower() and "missing" in error.lower() for error in errors),
            errors,
        )

    def test_duplicate_internal_use_fails_closure(self) -> None:
        ledger_path = self.make_complete_audit()
        _, use = self.install_internal_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["internal_uses"].append(json.loads(json.dumps(use)))
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("duplicate" in error.lower() and "internal" in error.lower() for error in errors),
            errors,
        )

    def test_dependency_use_ids_are_unique_across_the_whole_audit(
        self,
    ) -> None:
        ledger_path = self.make_complete_audit()
        _, use = self.install_internal_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        cross_unit_duplicate = json.loads(json.dumps(use))
        cross_unit_duplicate["dependent_unit"] = "lem:prior"
        cross_unit_duplicate["dependency_id"] = "lem:main"
        cross_unit_duplicate["step_ids"] = ["S001"]
        registry["internal_uses"].append(cross_unit_duplicate)
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "Dependency use ID D001 is not audit-globally unique"
                in error
                for error in errors
            ),
            errors,
        )

    def test_stale_internal_use_fails_closure(self) -> None:
        ledger_path = self.make_complete_audit()
        _, use = self.install_internal_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        stale = json.loads(json.dumps(use))
        stale["dependent_unit"] = "lem:prior"
        registry["internal_uses"].append(stale)
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "internal use" in error.lower()
                and ("stale" in error.lower() or "unused" in error.lower())
                for error in errors
            ),
            errors,
        )

    def test_internal_use_contract_hash_and_needed_form_are_exact(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        original = read_json(registry_path)
        cases = {
            "dependency_contract_sha256": lambda use: use.__setitem__(
                "dependency_contract_sha256", "0" * 64
            ),
            "needed_form": lambda use: use.__setitem__(
                "needed_form", "A stronger conclusion not used by the proof."
            ),
        }
        for field, mutate in cases.items():
            with self.subTest(field=field):
                registry = json.loads(json.dumps(original))
                mutate(registry["internal_uses"][0])
                write_json(registry_path, registry)
                errors, _ = proofcheck.check_audit_finalization(self.audit)
                self.assertTrue(
                    any(field in error for error in errors),
                    errors,
                )

    def test_internal_source_status_is_conclusion_aware(self) -> None:
        cases = (
            ("verified", "valid", "verified", "established", "verified"),
            (
                "conditionally_verified",
                "valid",
                "verified",
                "established",
                "conditional",
            ),
            ("verified", "invalid", "verified", "established", "gap"),
            ("verified", "invalid", "verified", "refuted", "incorrect"),
            ("verified", "gap", "verified", "not_established", "gap"),
            ("unclear", "unclear", "unclear", "unclear", "unclear"),
            (
                "not_checked",
                "not_checked",
                "not_checked",
                "not_assessed",
                "unchecked",
            ),
        )
        for contract, argument, closure, statement_status, expected in cases:
            with self.subTest(
                contract=contract,
                statement_status=statement_status,
            ):
                summary = {
                    "conclusion_results": [
                        {
                            "conclusion_id": "C001",
                            "contract_fidelity": contract,
                            "argument_status": argument,
                            "dependency_closure": closure,
                            "statement_status": statement_status,
                        }
                    ],
                }
                self.assertEqual(
                    expected,
                    proofcheck.internal_dependency_status(summary, "C001"),
                )

    def test_compatibility_status_must_propagate_to_internal_use(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["internal_uses"][0]["compatibility_checks"][0][
            "status"
        ] = "conditional"
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("compatibility" in error.lower() and "status" in error.lower() for error in errors),
            errors,
        )

    def test_dependency_closure_is_derived_from_effective_uses(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        use = registry["internal_uses"][0]
        use["compatibility_checks"][0]["status"] = "conditional"
        use["status"] = "conditional"
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("dependency_closure" in error for error in errors),
            errors,
        )

    def test_complete_external_dependency_closure_passes(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_external_dependency(ledger_path)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertEqual([], errors)

    def test_external_result_requires_substantive_source_evidence(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_external_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        external = registry["external_results"][0]
        external["source_evidence"][0]["locator"] = "TBD"
        contract_payload = {
            field: external[field]
            for field in (
                "source_identity",
                "version",
                "theorem_location",
                "exact_statement",
                "source_evidence",
            )
        }
        external["uses"][0]["dependency_contract_sha256"] = (
            proofcheck.canonical_sha256(contract_payload)
        )
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("source_evidence" in error and "locator" in error for error in errors),
            errors,
        )

    def test_external_result_requires_locked_source_evidence(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_external_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["external_results"][0]["source_evidence"] = []
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("source_evidence" in error for error in errors),
            errors,
        )

    def test_external_source_evidence_drift_fails(self) -> None:
        ledger_path = self.make_complete_audit()
        source_path, _ = self.install_external_dependency(ledger_path)
        source_path.write_text(
            "External Result 1\nFor every real x, x is nonnegative.\n",
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("source drift" in error.lower() for error in errors),
            errors,
        )

    def test_external_result_requires_one_closure_record_per_use(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_external_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["external_results"][0]["uses"] = []
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("external use" in error.lower() and "missing" in error.lower() for error in errors),
            errors,
        )

    def test_fully_valid_but_unused_external_catalog_record_fails(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_external_dependency(ledger_path)

        ledger = read_json(ledger_path)
        step = ledger["steps"][2]
        step["dependencies"] = []
        step["premise_uses"] = [
            premise
            for premise in step["premise_uses"]
            if premise.get("id") != "P002"
        ]
        step["inference"]["moves"][0]["premise_ids"] = ["P001"]
        ledger["review"]["direct_dependencies"] = []
        ledger["review"]["citation_dispositions"][0] = {
            "key": "smith",
            "disposition": "bibliographic_only",
            "evidence": "The citation supplies attribution and no proof premise.",
        }
        write_json(ledger_path, ledger)

        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["external_results"][0]["uses"] = []
        write_json(registry_path, registry)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        external_row = (
            "| lem:main | ext:reflexivity | external_result | verified | passed | "
            "verified | none |"
        )
        report = report.replace(external_row, "None.")
        report_path.write_text(report, encoding="utf-8", newline="\n")

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "ext:reflexivity" in error
                and "unused" in error.lower()
                for error in errors
            ),
            errors,
        )

    def test_resolved_issue_rejects_placeholder_evidence(self) -> None:
        ledger_path = self.make_complete_audit()
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
        issue = {
            "id": "I-001",
            "severity": "S3",
            "confidence": "high",
            "status": "resolved",
            "finding_status": "resolved",
            "scope": "unit",
            "load_bearing": False,
            "location": "TBD",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "TBD",
            "evidence": ["TBD"],
            "downstream_consequences": ["TBD"],
            "possible_repair": "TBD",
            "resolution": "TBD",
            "source_revision": "TBD",
            "recheck_evidence": ["TBD"],
            "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
            "rechecked_units": ["lem:main"],
        }
        self.install_canonical_issue(issue, ledger_path=ledger_path)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "I-001" in error
                and ("substantive" in error.lower() or "placeholder" in error.lower())
                for error in errors
            ),
            errors,
        )

    def test_unit_issue_affected_result_must_match_ledger(self) -> None:
        ledger_path = self.make_complete_audit()
        issue = {
            "id": "I-001",
            "severity": "S3",
            "confidence": "high",
            "status": "open",
            "finding_status": "inconclusive",
            "scope": "unit",
            "load_bearing": False,
            "location": "paper.tex:2-4",
            "affected_result": "lem:ghost",
            "affected_results": ["lem:ghost"],
            "summary": "The issue is intentionally linked to the wrong unit.",
            "evidence": ["The ledger link and affected result disagree."],
            "downstream_consequences": ["The recorded scope is unreliable."],
            "possible_repair": "Link the issue to the affected proof unit.",
        }
        self.install_canonical_issue(issue, ledger_path=ledger_path)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("affected_result" in error for error in errors),
            errors,
        )

    def test_issue_affected_results_follow_reverse_dependency_closure(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        issue = {
            "id": "I-001",
            "severity": "S3",
            "confidence": "high",
            "status": "open",
            "finding_status": "inconclusive",
            "scope": "global",
            "load_bearing": True,
            "location": "lem:prior",
            "affected_result": "lem:prior",
            "affected_results": ["lem:prior"],
            "summary": "A prerequisite concern can propagate to its dependent result.",
            "evidence": ["lem:main directly depends on lem:prior."],
            "downstream_consequences": ["lem:main may inherit the concern."],
            "possible_repair": "Resolve the prerequisite and recheck its dependents.",
        }
        self.install_canonical_issue(issue)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("affected_results" in error and "lem:main" in error for error in errors),
            errors,
        )

    def test_issue_summary_preserves_finding_status_and_affected_results(self) -> None:
        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=True,
            affected_result="lem:prior",
            affected_results=["lem:main", "lem:prior"],
        )

        summary = proofcheck.render_issue_summary([issue])

        self.assertIn("Finding", summary)
        self.assertIn("Affected results", summary)
        self.assertIn("defect", summary)
        self.assertIn("lem:main, lem:prior", summary)

    def test_non_load_bearing_issue_remains_root_only(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        _, summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        issue = self.make_global_issue(
            finding_status="inconclusive",
            load_bearing=False,
            affected_result="lem:prior",
            affected_results=["lem:prior"],
            severity="S3",
        )
        reverse_graph = {
            "lem:main": set(),
            "lem:prior": {"lem:main"},
        }

        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            evidence_base=self.audit,
            in_scope=["lem:main", "lem:prior"],
            reverse_graph=reverse_graph,
            ledger_summaries=summaries,
        )
        self.assertEqual([], errors)

        issue["affected_results"] = ["lem:main", "lem:prior"]
        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            evidence_base=self.audit,
            in_scope=["lem:main", "lem:prior"],
            reverse_graph=reverse_graph,
            ledger_summaries=summaries,
        )
        self.assertTrue(
            any("reverse dependency closure" in error for error in errors),
            errors,
        )

    def test_load_bearing_issue_weakens_every_reached_unit(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        clean_manifest = read_json(manifest_path)
        clean_report = report_path.read_text(encoding="utf-8")
        cases = {
            "inconclusive": "inconclusive",
            "defect": "defects_found",
        }
        for finding_status, assessment in cases.items():
            with self.subTest(finding_status=finding_status):
                write_json(manifest_path, clean_manifest)
                report_path.write_text(clean_report, encoding="utf-8", newline="\n")
                self.set_expected_assessment(assessment)
                issue = self.make_global_issue(
                    finding_status=finding_status,
                    load_bearing=True,
                    affected_result="lem:prior",
                    affected_results=["lem:main", "lem:prior"],
                )
                self.install_canonical_issue(issue)

                errors, result = proofcheck.check_audit_finalization(self.audit)

                self.assertEqual(assessment, result["derived_assessment"])
                for unit_id in ("lem:main", "lem:prior"):
                    self.assertTrue(
                        any(
                            "load-bearing" in error
                            and unit_id in error
                            for error in errors
                        ),
                        errors,
                    )

    def test_finding_status_controls_conditional_propagation_strength(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        step = self.mark_s003_conditional(ledger)
        step["side_conditions"] = [
            {
                "id": "SC001",
                "generated_by": "M001",
                "condition": "Assume x lies in the required support.",
                "status": "open",
            }
        ]
        step["conditions"] = [
            {
                "kind": "side_condition",
                "reference": "SC001",
                "condition": (
                    "Validity is conditional on the stated support condition."
                ),
            }
        ]
        write_json(ledger_path, ledger)

        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["conditional_units"] = ["lem:main"]
        write_json(progress_path, progress)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report = report.replace(
            "| lem:main | verified | verified | valid | established | verified |",
            "| lem:main | conditionally_verified | verified | conditional | conditional | verified |",
        )
        report = report.replace(
            "| lem:main | agreed | fresh_context_same_model | verified | verified |",
            "| lem:main | agreed | fresh_context_same_model | conditionally_verified | conditionally_verified |",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        clean_manifest = read_json(manifest_path)
        clean_report = report_path.read_text(encoding="utf-8")
        cases = {
            "inconclusive": "inconclusive",
            "defect": "defects_found",
        }
        for finding_status, assessment in cases.items():
            with self.subTest(finding_status=finding_status):
                write_json(manifest_path, clean_manifest)
                report_path.write_text(clean_report, encoding="utf-8", newline="\n")
                self.set_expected_assessment(assessment)
                issue = self.make_global_issue(
                    finding_status=finding_status,
                    load_bearing=True,
                )
                self.install_canonical_issue(issue)

                errors, result = proofcheck.check_audit_finalization(self.audit)

                self.assertEqual(assessment, result["derived_assessment"])
                propagation_errors = [
                    error
                    for error in errors
                    if "load-bearing" in error and "lem:main" in error
                ]
                if finding_status == "inconclusive":
                    self.assertEqual([], propagation_errors, errors)
                else:
                    self.assertTrue(propagation_errors, errors)

    def test_malformed_issue_affected_results_fails_closed(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        clean_report = report_path.read_text(encoding="utf-8")
        malformed_values = (None, [{}])
        for value in malformed_values:
            with self.subTest(value=repr(value)):
                report_path.write_text(clean_report, encoding="utf-8", newline="\n")
                issue = self.make_global_issue(load_bearing=False, severity="S3")
                issue["affected_results"] = value
                self.install_canonical_issue(issue)
                try:
                    errors, _ = proofcheck.check_audit_finalization(self.audit)
                except (TypeError, ValueError) as exc:
                    self.fail(
                        "Malformed affected_results raised "
                        f"{type(exc).__name__}: {exc}"
                    )
                self.assertTrue(errors)
                self.assertTrue(
                    any("affected_results" in error for error in errors),
                    errors,
                )

    def test_new_pass3_enum_fields_fail_closed_on_object_values(self) -> None:
        source_path = self.base / "enum-source.txt"
        source_path.write_text(
            "External theorem statement.\n",
            encoding="utf-8",
            newline="\n",
        )

        def external_case(errors: list[str]) -> None:
            proofcheck.validate_external_result_catalog(
                {
                    "external_results": [
                        {
                            "id": "ext:enum",
                            "status": {},
                            "source_identity": "doi:10.0000/enum",
                            "version": "version 1",
                            "theorem_location": "Theorem 1",
                            "exact_statement": "External theorem statement.",
                            "source_evidence": [
                                {
                                    "file": str(source_path),
                                    "sha256": proofcheck.sha256_file(source_path),
                                    "locator": "line 1",
                                    "role": "authoritative_theorem_source",
                                }
                            ],
                            "issue_ids": [],
                            "uses": [],
                        }
                    ]
                },
                self.audit,
                errors,
            )

        def global_case(errors: list[str]) -> None:
            checks = make_global_consistency_checks()
            checks[0]["status"] = {}
            proofcheck.validate_global_consistency_pass(
                {"status": "completed", "checks": checks},
                ["lem:main"],
                errors,
            )

        def cross_reference_case(errors: list[str]) -> None:
            locations = [{"file": "paper.tex", "line": 6}]
            proofcheck.validate_cross_reference_reviews(
                [
                    {
                        "kind": "broken_reference",
                        "key": "lem:missing",
                        "locations": locations,
                        "status": {},
                        "evidence": "The anomaly was reviewed for this negative control.",
                        "affected_units": [],
                        "issue_ids": [],
                    }
                ],
                {"broken_references": {"lem:missing": locations}},
                ["lem:main"],
                errors,
            )

        def issue_case(errors: list[str]) -> None:
            issue = self.make_global_issue(load_bearing=False, severity="S3")
            issue["finding_status"] = {}
            found, _ = proofcheck.validate_issues([issue], set(), True)
            errors.extend(found)

        cases = {
            "external result status": external_case,
            "global row status": global_case,
            "cross-reference status": cross_reference_case,
            "issue finding_status": issue_case,
        }
        for label, invoke in cases.items():
            with self.subTest(field=label):
                errors: list[str] = []
                try:
                    invoke(errors)
                except (TypeError, ValueError) as exc:
                    self.fail(f"{label} raised {type(exc).__name__}: {exc}")
                self.assertTrue(errors, label)

    def test_cross_reference_findings_reconcile_with_source_resolution(self) -> None:
        self.paper.write_text(
            self.paper.read_text(encoding="utf-8").replace(
                "and \\cite{smith}.",
                "and \\cite{smith}; compare \\ref{lem:missing}.",
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.audit = self.base / "cross-reference-finding-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(paper=self.paper, output=self.audit)
            )
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["review"]["source_reference_dispositions"].append(
            {
                "id": "lem:missing",
                "disposition": "non_load_bearing",
                "evidence": (
                    "The broken display reference supplies no premise to the proof."
                ),
            }
        )
        write_json(ledger_path, ledger)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        self.assertEqual(1, len(manifest["cross_reference_reviews"]))
        manifest["cross_reference_reviews"][0].update(
            {
                "status": "defect",
                "evidence": "The source contains a broken reference.",
                "affected_units": ["lem:main"],
                "issue_ids": ["I-001"],
            }
        )
        source_resolution = next(
            row
            for row in manifest["completion"]["global_consistency_pass"]["checks"]
            if row["aspect"] == "source_resolution"
        )
        source_resolution.update(
            {
                "status": "defect",
                "evidence": "The broken reference is recorded as a source defect.",
                "affected_units": ["lem:main"],
                "issue_ids": ["I-001"],
            }
        )
        manifest["completion"]["global_consistency_pass"]["status"] = (
            "completed_with_findings"
        )
        write_json(manifest_path, manifest)
        self.set_expected_assessment("defects_found")
        self.install_canonical_issue(
            self.make_global_issue(
                finding_status="defect",
                load_bearing=False,
                severity="S3",
                summary="The manuscript contains a broken result reference.",
            )
        )

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        canonical_manifest = read_json(manifest_path)
        canonical_report = report_path.read_text(encoding="utf-8")
        cases = {
            "status": lambda row: row.__setitem__("status", "inconclusive"),
            "affected_units": lambda row: row.__setitem__("affected_units", []),
            "issue_ids": lambda row: row.__setitem__("issue_ids", []),
        }
        for field, mutate in cases.items():
            with self.subTest(field=field):
                changed = json.loads(json.dumps(canonical_manifest))
                row = next(
                    item
                    for item in changed["completion"]["global_consistency_pass"]["checks"]
                    if item["aspect"] == "source_resolution"
                )
                mutate(row)
                write_json(manifest_path, changed)
                report_path.write_text(
                    canonical_report,
                    encoding="utf-8",
                    newline="\n",
                )

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                self.assertTrue(
                    any(
                        "source_resolution" in error
                        and field in error
                        and "cross-reference" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_issue_summary_newline_is_rejected_for_canonical_heading(
        self,
    ) -> None:
        self.make_complete_audit()
        issue = self.make_global_issue(
            load_bearing=False,
            severity="S3",
            summary="The first line\nand the second | clause form one summary.",
        )
        self.install_canonical_issue(issue)

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "summary must be one line for the canonical finding heading"
                in error
                for error in errors
            ),
            errors,
        )

    def test_issue_summary_with_angle_comparison_is_safely_rendered(self) -> None:
        self.make_complete_audit()
        issue = self.make_global_issue(
            load_bearing=False,
            severity="S3",
            summary="The claimed bound fails in the n<p regime.",
        )
        self.install_canonical_issue(issue)

        report = (
            self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        ).read_text(encoding="utf-8")
        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertIn("n&lt;p", report)
        self.assertFalse(
            any("active raw HTML" in error for error in errors), errors
        )
        self.assertFalse(
            any("heading is stale" in error for error in errors), errors
        )

    def test_fresh_report_template_has_no_active_raw_html_placeholder(self) -> None:
        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertFalse(
            any("active raw HTML" in error for error in errors), errors
        )

    def test_issue_report_views_order_by_severity_then_issue_id(self) -> None:
        issues = [
            {
                "id": "I-001",
                "severity": "S3",
                "summary": "Lower-severity finding with the first ID.",
                "affected_result": "lem:main",
                "affected_results": ["lem:main"],
            },
            {
                "id": "I-003",
                "severity": "S1",
                "summary": "Higher-severity finding with the later ID.",
                "affected_result": "lem:main",
                "affected_results": ["lem:main"],
            },
            {
                "id": "I-002",
                "severity": "S1",
                "summary": "Higher-severity finding with the earlier ID.",
                "affected_result": "lem:main",
                "affected_results": ["lem:main"],
            },
        ]

        _, details = proofcheck.render_issue_report_views(
            issues,
            {},
            [],
            [],
            [],
            "defects_found",
        )
        headings = [
            line.split()[1]
            for line in details.splitlines()
            if line.startswith("### I-")
        ]

        self.assertEqual(["I-002", "I-003", "I-001"], headings)

    def test_issue_report_views_require_final_mode(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        before = report_path.read_text(encoding="utf-8")
        output = io.StringIO()
        errors = io.StringIO()

        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = proofcheck.cmd_issues(
                argparse.Namespace(
                    root=self.audit,
                    write_summary=False,
                    write_report_views=True,
                    final=False,
                )
            )
        payload = json.loads(output.getvalue())

        self.assertEqual(1, status)
        self.assertFalse(payload["report_views_written"])
        self.assertIn("--write-report-views requires --final", errors.getvalue())
        self.assertEqual(before, report_path.read_text(encoding="utf-8"))

    def test_failed_final_issue_reconciliation_preserves_all_views(self) -> None:
        self.make_complete_audit()
        summary_path = self.audit / "audit" / "06_reports" / "ISSUE_SUMMARY.md"
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        summary_before = summary_path.read_bytes()
        report_before = report_path.read_bytes()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["status"] = "draft"
        write_json(manifest_path, manifest)

        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = proofcheck.cmd_issues(
                argparse.Namespace(
                    root=self.audit,
                    write_summary=True,
                    write_report_views=True,
                    final=True,
                )
            )

        self.assertEqual(1, status)
        self.assertFalse(json.loads(output.getvalue())["report_views_written"])
        self.assertTrue(errors.getvalue())
        self.assertEqual(summary_before, summary_path.read_bytes())
        self.assertEqual(report_before, report_path.read_bytes())

    def test_issue_view_transaction_rolls_back_each_failed_commit(self) -> None:
        self.make_complete_audit()
        summary_path = self.audit / "audit" / "06_reports" / "ISSUE_SUMMARY.md"
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report = proofcheck.replace_report_section_text(
            report, "## Issue index", "stale issue index"
        )
        report = proofcheck.replace_report_section_text(
            report, "## Detailed findings", "stale detailed findings"
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")
        summary_path.write_text(
            "stale issue summary\n", encoding="utf-8", newline="\n"
        )
        summary_before = summary_path.read_bytes()
        report_before = report_path.read_bytes()
        original_replace = proofcheck.os.replace

        for failed_path in (report_path, summary_path):
            with self.subTest(failed_destination=failed_path.name):
                events: list[tuple[str, Path]] = []

                def fail_commit(source: Path, destination: Path) -> None:
                    destination_path = Path(destination).resolve()
                    if destination_path == failed_path.resolve():
                        events.append(("failed", destination_path))
                        raise OSError(
                            f"simulated {failed_path.name} commit failure"
                        )
                    original_replace(source, destination)
                    events.append(("replaced", destination_path))

                with mock.patch.object(
                    proofcheck.os, "replace", side_effect=fail_commit
                ):
                    with self.assertRaisesRegex(
                        OSError, f"simulated {re.escape(failed_path.name)}"
                    ):
                        proofcheck.cmd_issues(
                            argparse.Namespace(
                                root=self.audit,
                                write_summary=True,
                                write_report_views=True,
                                final=True,
                            )
                        )

                self.assertEqual(summary_before, summary_path.read_bytes())
                self.assertEqual(report_before, report_path.read_bytes())
                self.assertEqual(
                    [],
                    list(report_path.parent.glob(".*.proofcheck.tmp")),
                )
                if failed_path == summary_path:
                    self.assertEqual(
                        [
                            ("replaced", report_path.resolve()),
                            ("failed", summary_path.resolve()),
                            ("replaced", report_path.resolve()),
                        ],
                        events,
                    )
                else:
                    self.assertEqual(
                        [("failed", report_path.resolve())], events
                    )

    def test_issue_report_views_generate_exact_empty_sections_only(
        self,
    ) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        before = report_path.read_text(encoding="utf-8")
        before = proofcheck.replace_report_section_text(
            before, "## Issue index", "stale issue index"
        )
        before = proofcheck.replace_report_section_text(
            before, "## Detailed findings", "stale detailed findings"
        )
        report_path.write_text(before, encoding="utf-8", newline="\n")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = proofcheck.cmd_issues(
                argparse.Namespace(
                    root=self.audit,
                    write_summary=True,
                    write_report_views=True,
                    final=True,
                )
            )
        payload = json.loads(output.getvalue())
        after = report_path.read_text(encoding="utf-8")

        self.assertEqual(0, status)
        self.assertTrue(payload["report_views_written"])
        self.assertEqual(
            "No issues.",
            (proofcheck.report_section(after, "## Issue index") or "").strip(),
        )
        self.assertEqual(
            "No issues.",
            (
                proofcheck.report_section(after, "## Detailed findings") or ""
            ).strip(),
        )
        for heading in ("## Issue index", "## Detailed findings"):
            before = proofcheck.replace_report_section_text(
                before, heading, "<generated>"
            )
            after = proofcheck.replace_report_section_text(
                after, heading, "<generated>"
            )
        self.assertEqual(before, after)

    def test_issue_report_views_generate_schema5_tables_accepted_by_finalization(
        self,
    ) -> None:
        self.make_complete_audit()
        issue = self.make_global_issue(
            load_bearing=False,
            severity="S3",
            summary="A canonical schema-five finding.",
        )
        self.install_canonical_issue(issue)
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        before = report_path.read_text(encoding="utf-8")
        before = proofcheck.replace_report_section_text(
            before, "## Issue index", "stale issue index"
        )
        before = proofcheck.replace_report_section_text(
            before, "## Detailed findings", "stale detailed findings"
        )
        report_path.write_text(before, encoding="utf-8", newline="\n")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = proofcheck.cmd_issues(
                argparse.Namespace(
                    root=self.audit,
                    write_summary=True,
                    write_report_views=True,
                    final=True,
                )
            )
        payload = json.loads(output.getvalue())
        after = report_path.read_text(encoding="utf-8")
        _, summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        summaries_by_id = {
            summary["unit_id"]: summary for summary in summaries
        }
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
        critical, _ = proofcheck.effective_critical_requirements(
            manifest, [issue]
        )
        expected_index, expected_details = (
            proofcheck.render_issue_report_views(
                [issue],
                summaries_by_id,
                [],
                critical,
                manifest.get("report_deliverables", []),
                manifest["audit_scope"]["overall_assessment"],
            )
        )

        self.assertEqual(0, status)
        self.assertTrue(payload["report_views_written"])
        self.assertEqual(
            expected_index,
            (proofcheck.report_section(after, "## Issue index") or "").strip(),
        )
        self.assertEqual(
            expected_details,
            (
                proofcheck.report_section(after, "## Detailed findings") or ""
            ).strip(),
        )
        for heading in ("## Issue index", "## Detailed findings"):
            before = proofcheck.replace_report_section_text(
                before, heading, "<generated>"
            )
            after = proofcheck.replace_report_section_text(
                after, heading, "<generated>"
            )
        self.assertEqual(before, after)
        final_errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], final_errors)

    def test_ledger_move_report_preserves_exact_premises_and_failure_evidence(
        self,
    ) -> None:
        _, _, failure_evidence = self.make_ledger_move_defect_audit()
        final_errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], final_errors)
        report = (
            self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        ).read_text(encoding="utf-8")
        details = proofcheck.report_section(report, "## Detailed findings") or ""
        failure_table = proofcheck.markdown_tables(details)[0]
        failure_row = failure_table[2]
        expected_premises = json.dumps(
            {
                "premises": [
                    {
                        "id": "P001",
                        "claim": "For every real x.",
                        "origin": {
                            "kind": "obligation",
                            "reference": "/quantifier_scope",
                            "anchor": {
                                "kind": "statement_span",
                                "index": 1,
                            },
                        },
                    }
                ],
                "prior_moves": [],
            },
            ensure_ascii=False,
        )

        self.assertEqual("Premises", failure_table[0][7])
        self.assertEqual("Failure evidence", failure_table[0][8])
        self.assertEqual(expected_premises, failure_row[7])
        self.assertEqual(failure_evidence, failure_row[8])
        self.assertEqual("invalid_rule", failure_row[9])

    def test_ledger_move_report_rejects_stale_premises_or_failure_evidence(
        self,
    ) -> None:
        self.make_ledger_move_defect_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        baseline = report_path.read_text(encoding="utf-8")
        details = proofcheck.report_section(
            baseline, "## Detailed findings"
        ) or ""
        failure_row = proofcheck.markdown_tables(details)[0][2]
        self.assertEqual([], proofcheck.check_audit_finalization(self.audit)[0])

        for field, value, stale in (
            ("Premises", failure_row[7], "stale premise projection"),
            (
                "Failure evidence",
                failure_row[8],
                "stale failure evidence",
            ),
        ):
            with self.subTest(field=field):
                self.assertIn(value, baseline)
                report_path.write_text(
                    baseline.replace(value, stale, 1),
                    encoding="utf-8",
                    newline="\n",
                )
                errors, _ = proofcheck.check_audit_finalization(self.audit)
                self.assertTrue(
                    any(
                        "I-001" in error
                        and "Exact failure site and contract" in error
                        and "disagrees with canonical evidence" in error
                        for error in errors
                    ),
                    errors,
                )
                report_path.write_text(
                    baseline,
                    encoding="utf-8",
                    newline="\n",
                )

    def test_dependency_issue_report_views_use_derived_final_closure(
        self,
    ) -> None:
        self.make_dependency_mismatch_audit()
        output = io.StringIO()
        errors = io.StringIO()

        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = proofcheck.cmd_issues(
                argparse.Namespace(
                    root=self.audit,
                    write_summary=True,
                    write_report_views=True,
                    final=True,
                )
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(0, status, errors.getvalue())
        self.assertEqual("", errors.getvalue())
        self.assertTrue(payload["report_views_written"])

        report = (
            self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        ).read_text(encoding="utf-8")
        details = proofcheck.report_section(report, "## Detailed findings") or ""
        tables = proofcheck.markdown_tables(details)
        failure_row = tables[0][2]
        self.assertEqual(
            json.dumps(
                {
                    "source_status": "verified",
                    "applicability_status": "incorrect",
                    "effective_status": "incorrect",
                    "issue_ids": ["I-001"],
                    "nonpassing_compatibility_checks": [
                        {
                            "aspect": "quantifiers_and_domains",
                            "status": "incorrect",
                            "evidence": (
                                "The dependency conclusion has the wrong "
                                "quantified domain at this use site."
                            ),
                            "issue_ids": ["I-001"],
                        }
                    ],
                    "nonpassing_prerequisites": [],
                    "source_evidence": [],
                },
                ensure_ascii=False,
            ),
            failure_row[8],
        )
        propagation = next(
            row for row in tables[2][2:] if row[2] == "D001"
        )
        self.assertEqual("lem:main", propagation[0])
        self.assertEqual("uses lem:prior", propagation[1])
        self.assertEqual("C001", propagation[3])
        self.assertNotEqual("none", propagation[4])
        self.assertNotEqual("none", propagation[5])
        self.assertNotEqual("none", propagation[6])
        closure = tables[-1][2]
        self.assertEqual("D001", closure[2])
        self.assertEqual("none", closure[3])
        self.assertEqual("open", closure[-1])

        final_errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], final_errors)

    def test_external_dependency_finding_preserves_exact_failure_evidence(
        self,
    ) -> None:
        compatibility_failure = {
            "aspect": "quantifiers_and_domains",
            "status": "incorrect",
            "evidence": "The cited result quantifies only over bounded x.",
            "issue_ids": ["I-001"],
        }
        prerequisite_failure = {
            "prerequisite": "The manuscript variable x is bounded.",
            "status": "incorrect",
            "manuscript_evidence": (
                "The theorem statement instead permits every real x."
            ),
            "evidence_spans": [
                {
                    "file": "paper.tex",
                    "start_line": 2,
                    "end_line": 4,
                    "sha256": "1" * 64,
                    "role": "manuscript_prerequisite",
                }
            ],
            "issue_ids": ["I-001"],
        }
        source_evidence = [
            {
                "file": "external-result.txt",
                "sha256": "2" * 64,
                "locator": "Theorem 2, page 7",
                "role": "authoritative_theorem_source",
            }
        ]
        issue = {
            "id": "I-001",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "status": "open",
            "severity": "S1",
            "confidence": "high",
            "load_bearing": True,
            "invalidation_kind": "dependency_mismatch",
            "origin_ref": {
                "kind": "dependency_use",
                "unit_id": "lem:main",
                "use_id": "D001",
            },
            "contract_refs": [],
            "suggested_changes": [],
        }
        summaries = {
            "lem:main": {
                "result_dependency_claims": [{"use_id": "D001"}],
                "direct_dependencies": [
                    {
                        "id": "ext:bounded",
                        "use_id": "D001",
                        "needed_form": "The claim holds for every real x.",
                        "compatibility_check": (
                            "The cited and needed domains must agree."
                        ),
                        "status": "incorrect",
                    }
                ],
                "review_components": {},
                "conclusion_results": [],
            }
        }
        dependency_edges = [
            {
                "dependent_unit": "lem:main",
                "use_id": "D001",
                "dependency_id": "ext:bounded",
                "dependency_conclusion_id": None,
                "kind": "external_result",
                "source_status": "incorrect",
                "applicability_status": "incorrect",
                "effective_status": "incorrect",
                "issue_ids": ["I-001"],
                "compatibility_checks": [
                    {
                        "aspect": "object_identity",
                        "status": "passed",
                        "evidence": "The same variable x is used.",
                        "issue_ids": [],
                    },
                    compatibility_failure,
                ],
                "prerequisite_map": [
                    {
                        "prerequisite": "The object is real-valued.",
                        "status": "satisfied",
                        "manuscript_evidence": "The statement declares x real.",
                        "evidence_spans": [],
                        "issue_ids": [],
                    },
                    prerequisite_failure,
                ],
                "source_evidence": source_evidence,
            }
        ]

        projection = proofcheck.canonical_issue_detail_projection(
            issue,
            summaries,
            dependency_edges,
            [],
            [],
            "defects_found",
        )

        self.assertEqual(
            json.dumps(
                {
                    "source_status": "incorrect",
                    "applicability_status": "incorrect",
                    "effective_status": "incorrect",
                    "issue_ids": ["I-001"],
                    "nonpassing_compatibility_checks": [
                        compatibility_failure
                    ],
                    "nonpassing_prerequisites": [prerequisite_failure],
                    "source_evidence": source_evidence,
                },
                ensure_ascii=False,
            ),
            projection["failure"][0][8],
        )

    def test_detailed_finding_heading_preserves_vertical_bar(self) -> None:
        self.make_complete_audit()
        summary = "The first and second | clauses form one summary."
        issue = self.make_global_issue(
            load_bearing=False,
            severity="S3",
            summary=summary,
        )
        self.install_canonical_issue(issue)

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        section = proofcheck.report_section(
            report_path.read_text(encoding="utf-8"),
            "## Detailed findings",
        )

        self.assertEqual([], errors)
        self.assertIn(f"### I-001 [S3] {summary}", section or "")

    def test_global_check_finding_projects_exact_canonical_status_evidence(
        self,
    ) -> None:
        self.make_complete_audit()
        _, summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        summaries_by_id = {
            summary["unit_id"]: summary for summary in summaries
        }
        aspect = "constants_and_rates"
        check = {
            "aspect": aspect,
            "status": "defect",
            "evidence": (
                "Distinctive global evidence: the n^-1 rate was substituted "
                "for the required n^-1/2 rate."
            ),
            "affected_units": ["lem:main"],
            "issue_ids": ["I-001"],
        }
        issue = self.make_global_issue(
            finding_status="defect",
            summary="The global rate check records a canonical mismatch.",
        )
        issue["origin_ref"] = {
            "kind": "global_check",
            "aspect": aspect,
            "evidence_spans": [
                proofcheck.locked_span(
                    self.paper,
                    3,
                    3,
                    self.audit,
                    role="global_consistency_evidence",
                )
            ],
        }

        _, details = proofcheck.render_issue_report_views(
            [issue],
            summaries_by_id,
            [],
            ["lem:main"],
            [],
            "defects_found",
            global_checks={aspect: check},
        )
        failure_row = proofcheck.markdown_tables(details)[0][2]

        self.assertEqual(
            {
                "affected_units": ["lem:main"],
                "aspect": aspect,
                "evidence": check["evidence"],
                "issue_ids": ["I-001"],
                "status": "defect",
            },
            json.loads(failure_row[8]),
        )
        self.assertEqual("defect", failure_row[9])
        self.assertEqual(
            {"affected_units": ["lem:main"]},
            json.loads(failure_row[7]),
        )

    def test_interface_finding_projects_exact_mismatch_statuses(self) -> None:
        self.make_complete_audit()
        _, summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        summaries_by_id = {
            summary["unit_id"]: summary for summary in summaries
        }
        interface = self.make_interface_record(
            target_verdict="mismatch",
            code_to_documented="inconsistent",
            code_to_target="inconsistent",
            execution_provenance="not_matched",
            load_bearing=True,
            implementation_required=True,
            execution_required=True,
        )
        interface["issue_ids"] = ["I-001"]
        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=True,
            severity="S1",
            summary="The estimator implementation targets the wrong object.",
        )
        issue.update(
            {
                "interface_id": interface["id"],
                "finding_class": "implementation_mismatch",
                "affected_layer": "implementation_to_target",
                "origin_ref": {
                    "kind": "interface_record",
                    "interface_id": interface["id"],
                    "evidence_spans": interface[
                        "implementation_relation"
                    ]["evidence_spans"],
                },
            }
        )

        _, details = proofcheck.render_issue_report_views(
            [issue],
            summaries_by_id,
            [],
            ["lem:main"],
            [],
            "defects_found",
            interfaces={interface["id"]: interface},
        )
        failure_row = proofcheck.markdown_tables(details)[0][2]
        evidence = json.loads(failure_row[8])

        self.assertEqual(
            interface["target_relation"], evidence["target_relation"]
        )
        self.assertEqual(
            interface["implementation_relation"],
            evidence["implementation_relation"],
        )
        self.assertEqual(["I-001"], evidence["issue_ids"])
        self.assertEqual(
            "mismatch", evidence["target_relation"]["verdict"]
        )
        comparisons = {
            row["to"]: row["verdict"]
            for row in evidence["implementation_relation"]["comparisons"]
        }
        self.assertEqual("inconsistent", comparisons["documented_estimator"])
        self.assertEqual("inconsistent", comparisons["required_target"])
        self.assertEqual(
            "not_matched",
            evidence["implementation_relation"]["execution_provenance"][
                "status"
            ],
        )
        self.assertEqual("implementation_mismatch", failure_row[9])

    def test_stored_cross_reference_json_must_match_fresh_scan(self) -> None:
        self.make_complete_audit()
        crossref_path = (
            self.audit / "audit" / "01_index" / "cross_reference_audit.json"
        )
        crossref = read_json(crossref_path)
        crossref["references"] = {}
        write_json(crossref_path, crossref)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("cross_reference_audit.json" in error for error in errors),
            errors,
        )

    def test_stored_cross_reference_markdown_must_match_json(self) -> None:
        self.make_complete_audit()
        crossref_path = (
            self.audit / "audit" / "01_index" / "cross_reference_audit.md"
        )
        crossref_path.write_text(
            "# Invented Cross-Reference Audit\n\nNo references.\n",
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any("cross_reference_audit.md" in error for error in errors),
            errors,
        )

    def test_final_report_rejects_certification_overclaim(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report += "\nThis certifies the proof as correct.\n"
        report_path.write_text(report, encoding="utf-8", newline="\n")
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("unsupported proof-certification language" in error for error in errors),
            errors,
        )

    def test_final_report_rejects_formal_verification_overclaim(self) -> None:
        self.make_complete_audit()
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report += "\nThis is a formally verified proof.\n"
        report_path.write_text(report, encoding="utf-8", newline="\n")
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("unsupported formal-verification language" in error for error in errors),
            errors,
        )

    def test_multi_conclusion_support_is_ordered_and_complete(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        second = json.loads(
            json.dumps(ledger["obligation"]["conclusions"][0])
        )
        second["id"] = "C002"
        second["claim"] = "Every real x is identical to itself"
        ledger["obligation"]["conclusions"].append(second)

        first_step = ledger["steps"][2]
        second_step = json.loads(json.dumps(first_step))
        second_step["id"] = "S004"
        second_step["restatement"] = second["claim"]
        second_step["goal"] = "Record the equivalent verbal conclusion."
        second_step["dependencies"] = [
            {
                "id": "S003",
                "kind": "step",
                "status": "verified",
                "needed_form": first_step["restatement"],
                "compatibility_check": (
                    "The verbal conclusion restates the same reflexive equality."
                ),
            }
        ]
        second_step["premise_uses"] = [
            {
                "id": "P001",
                "role": "fact",
                "claim": first_step["restatement"],
                "origin": {"kind": "prior_step", "reference": "S003"},
                "evidence": (
                    "S003 establishes the symbolic reflexive equality first."
                ),
            }
        ]
        second_step["inference"] = {
            "moves": [
                {
                    "id": "M001",
                    "claim": second["claim"],
                    "rule": "Equivalent verbal restatement",
                    "premise_ids": ["P001"],
                    "prior_move_ids": [],
                    "justification": (
                        "Identity with itself is the verbal form of reflexivity."
                    ),
                }
            ],
            "conclusion_move": "M001",
        }
        second_step["checks"]["literal"] = (
            "The shared source line states the same reflexive equality."
        )
        ledger["steps"][3]["id"] = "S005"
        ledger["steps"].insert(3, second_step)
        second_result = json.loads(
            json.dumps(ledger["review"]["conclusion_results"][0])
        )
        second_result["conclusion_id"] = "C002"
        second_result["support"] = {"step_id": "S004", "move_id": "M001"}
        ledger["review"]["conclusion_results"].append(second_result)
        ledger["review"]["conclusion_step_id"] = ""
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

        ledger["review"]["conclusion_results"].pop()
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("omits conclusions: C002" in error for error in errors),
            errors,
        )

    def test_joint_side_condition_discharge_uses_all_sources(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        conclusion_step = ledger["steps"][2]
        domain_step = json.loads(json.dumps(conclusion_step))
        domain_step["restatement"] = (
            "x lies in the real-number equality domain"
        )
        domain_step["goal"] = "Establish the domain fact used by reflexivity."
        domain_step["inference"] = {
            "moves": [
                {
                    "id": "M001",
                    "claim": "x lies in the real-number equality domain",
                    "rule": "Domain extraction",
                    "premise_ids": ["P001"],
                    "prior_move_ids": [],
                    "justification": "P001 quantifies x over the real numbers.",
                }
            ],
            "conclusion_move": "M001",
        }
        domain_step["side_conditions"] = []

        conclusion_step = json.loads(json.dumps(conclusion_step))
        conclusion_step["id"] = "S004"
        conclusion_step["dependencies"] = [
            {
                "id": "S003",
                "kind": "step",
                "status": "verified",
                "needed_form": domain_step["restatement"],
                "compatibility_check": (
                    "The established domain is exactly the domain of equality."
                ),
            }
        ]
        conclusion_step["premise_uses"].append(
            {
                "id": "P002",
                "role": "fact",
                "claim": domain_step["restatement"],
                "origin": {"kind": "prior_step", "reference": "S003"},
                "evidence": "S003 supplies the exact real-domain fact.",
            }
        )
        conclusion_step["inference"] = {
            "moves": [
                {
                    "id": "M001",
                    "claim": conclusion_step["restatement"],
                    "rule": "Reflexivity of equality",
                    "premise_ids": ["P001", "P002"],
                    "prior_move_ids": [],
                    "justification": (
                        "The quantified real variable and established domain "
                        "jointly permit reflexivity."
                    ),
                },
            ],
            "conclusion_move": "M001",
        }
        conclusion_step["side_conditions"] = [
            {
                "id": "SC001",
                "generated_by": "M001",
                "condition": "The equality operation is defined for x.",
                "status": "discharged",
                "discharge": {
                    "sources": [
                        {
                            "kind": "premise",
                            "reference": "P001",
                            "contribution": "P001 supplies the real-number domain.",
                        },
                        {
                            "kind": "premise",
                            "reference": "P002",
                            "contribution": (
                                "P002 supplies the specialized domain fact."
                            ),
                        },
                    ],
                    "rule": (
                        "The quantified domain and its specialization jointly "
                        "establish definedness."
                    ),
                    "evidence": (
                        "Both recorded sources are needed for the explicit "
                        "domain discharge."
                    ),
                },
            }
        ]
        ledger["steps"][2] = domain_step
        ledger["steps"][3]["id"] = "S005"
        ledger["steps"].insert(3, conclusion_step)
        ledger["review"]["conclusion_step_id"] = "S004"
        ledger["review"]["conclusion_results"][0]["support"] = {
            "step_id": "S004",
            "move_id": "M001",
        }
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_controlled_multiline_atomicity_requires_full_source_partition(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = self.downgrade_ledger_fixture_to_schema4(
            read_json(ledger_path)
        )
        del ledger["steps"][1]
        step = ledger["steps"][1]
        step["lines"] = [5, 6]
        step["checks"]["atomicity"] = {
            "status": "source_indivisible_chain",
            "source_unit_kind": "continued_sentence",
            "partition_evidence": (
                "The two adjacent source lines are treated as one continued unit."
            ),
            "evidence": "Each physical line is assigned to an atomic move.",
        }
        step["inference"] = {
            "moves": [
                {
                    "id": "M001",
                    "claim": "The proof environment opens the argument.",
                    "rule": "Proof setup",
                    "premise_ids": ["P001"],
                    "prior_move_ids": [],
                    "source_line_range": [5, 5],
                    "justification": "The first line establishes the proof context.",
                },
                {
                    "id": "M002",
                    "claim": step["restatement"],
                    "rule": "Reflexivity of equality",
                    "premise_ids": [],
                    "prior_move_ids": ["M001"],
                    "source_line_range": [6, 6],
                    "justification": "The second line states the reflexive conclusion.",
                },
            ],
            "conclusion_move": "M002",
        }
        ledger["review"]["conclusion_results"][0]["support"]["move_id"] = "M002"
        write_json(ledger_path, ledger)

        errors, _ = proofcheck.check_ledger_data(ledger_path, False)
        self.assertEqual([], errors)

        step["inference"]["moves"][1]["source_line_range"] = [5, 5]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any(
                "do not represent every covered source line" in error
                for error in errors
            ),
            errors,
        )

    def test_prior_step_source_anchor_binds_exact_occurrence(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        prior = ledger["steps"][0]
        prior["kind"] = "setup"
        dependency = {
            "id": "S001",
            "kind": "step",
            "status": "verified",
            "needed_form": prior["restatement"],
            "compatibility_check": (
                "The prior setup is used in exactly its recorded form."
            ),
        }
        step = ledger["steps"][2]
        step["dependencies"] = [dependency]
        premise = step["premise_uses"][0]
        premise["claim"] = prior["restatement"]
        premise["origin"] = {"kind": "prior_step", "reference": "S001"}
        disposition = ledger["review"]["source_reference_dispositions"][0]
        premise["source_reference_id"] = disposition["target"]
        premise["source_reference_occurrence_id"] = disposition["occurrence_id"]
        disposition["disposition"] = "local_step"
        disposition["premise_links"] = [
            {"step_id": "S003", "premise_id": "P001"}
        ]
        disposition["evidence"] = (
            "The exact proof occurrence names the label inside the earlier setup."
        )
        write_json(ledger_path, ledger)
        self.seal_schema5_challenge(ledger_path, read_json(ledger_path))

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_occurrence_disposition_cannot_be_reused_for_another_occurrence(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        ledger["review"]["source_reference_dispositions"][0][
            "occurrence_id"
        ] = "R-deadbeefdeadbeef"
        write_json(ledger_path, ledger)

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "source occurrences lack reviewed dispositions" in error
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any(
                "source-reference dispositions are not present" in error
                for error in errors
            ),
            errors,
        )

    def test_reviewed_proof_evidence_must_match_canonical_rescan(self) -> None:
        self.make_complete_audit()
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        inventory["units"][0]["reference_occurrences"] = []
        write_json(inventory_path, inventory)
        self.refresh_dependency_review()

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "reference_occurrences disagrees with the canonical rescan"
                in error
                for error in errors
            ),
            errors,
        )

    def test_explicit_proof_rejection_requires_exact_overrides(self) -> None:
        ledger_path = self.make_complete_audit()
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        unit = inventory["units"][0]
        parser_proof = proofcheck.canonical_location(unit["proof"])
        parser_association = json.loads(
            json.dumps(unit["proof_association"])
        )
        reviewed_association = {
            "status": "rejected",
            "method": "reviewed_rejection",
            "target": "lem:main",
            "evidence_occurrence_ids": [],
        }
        unit["proof"] = None
        unit["proof_redirects"] = []
        unit["proof_association"] = reviewed_association
        unit["reference_occurrences"] = []
        unit["dependencies"] = []
        unit["candidate_internal_dependencies"] = []
        unit["citations"] = []
        write_json(inventory_path, inventory)

        ledger = read_json(ledger_path)
        ledger["review"]["source_reference_dispositions"] = []
        ledger["review"]["citation_dispositions"] = []
        write_json(ledger_path, ledger)
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["inventory_overrides"] = [
            {
                "unit_id": "lem:main",
                "kind": "proof_location",
                "parser_proof": parser_proof,
                "reviewed_proof": None,
                "reviewed_proof_sha256": None,
                "association_method": "reviewed_rejection",
                "reason": "Rendered review rejects the parser-associated proof.",
                "evidence": "The reviewed unit intentionally has no accepted proof.",
            },
            {
                "unit_id": "lem:main",
                "kind": "proof_association",
                "parser_association": parser_association,
                "reviewed_association": reviewed_association,
                "rendered_source_evidence": (
                    "Rendered source confirms that the associated span is rejected."
                ),
                "reason": "The parser candidate is not accepted as this proof.",
                "evidence": "The rejection is explicit and source reviewed.",
            },
        ]
        write_json(manifest_path, manifest)
        self.refresh_dependency_review()

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "proof-required result has no inventoried proof range" in error
                for error in errors
            ),
            errors,
        )
        self.assertFalse(
            any("lack explicit overrides" in error for error in errors),
            errors,
        )

    def test_manual_unit_override_hash_is_fail_closed(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["inventory_overrides"][0][
            "reviewed_unit_sha256"
        ] = "0" * 64
        write_json(manifest_path, manifest)

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("reviewed_unit_sha256 is stale" in error for error in errors),
            errors,
        )

    def test_internal_use_must_name_the_exact_dependency_conclusion(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["internal_uses"][0]["dependency_conclusion_id"] = "C002"
        write_json(registry_path, registry)

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "dependency_conclusion_id disagrees with the invoking ledger"
                in error
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any("unknown dependency conclusion C002" in error for error in errors),
            errors,
        )

    def test_focused_scope_must_equal_exact_target_closure(self) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["target_units"] = ["lem:prior"]
        manifest["audit_scope"]["critical_units"] = ["lem:prior"]
        write_json(manifest_path, manifest)
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "- Target results: lem:main",
            "- Target results: lem:prior",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "includes units outside the exact target closure" in error
                for error in errors
            ),
            errors,
        )

    def test_status_preflight_is_populated_without_a_finalization_record(self) -> None:
        complete_output = io.StringIO()
        self.make_complete_audit()
        with contextlib.redirect_stdout(complete_output):
            complete_status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=self.audit,
                    format="json",
                    output=None,
                    force=False,
                )
            )
        complete = json.loads(complete_output.getvalue())["finalization"]
        self.assertEqual(0, complete_status)
        self.assertEqual("passed", complete["preflight_status"])
        self.assertTrue(complete["finalizable_now"])
        self.assertEqual([], complete["current_gate_errors"])

        incomplete_output = io.StringIO()
        incomplete_root = self.base / "incomplete-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(paper=self.paper, output=incomplete_root)
            )
        with contextlib.redirect_stdout(incomplete_output):
            incomplete_status = proofcheck.cmd_status(
                argparse.Namespace(
                    root=incomplete_root,
                    format="json",
                    output=None,
                    force=False,
                )
            )
        incomplete = json.loads(incomplete_output.getvalue())["finalization"]
        self.assertEqual(0, incomplete_status)
        self.assertEqual("failed", incomplete["preflight_status"])
        self.assertFalse(incomplete["finalizable_now"])
        self.assertTrue(incomplete["current_gate_errors"])

    def test_unresolved_named_proof_does_not_fall_through_to_adjacency(self) -> None:
        cases = {
            "ambiguous": (
                "Proof of \\ref{thm:first} and \\ref{thm:second}"
            ),
            "unresolved": "Proof of \\ref{thm:missing}",
        }
        for case, title in cases.items():
            with self.subTest(case=case):
                source = self.base / f"named-{case}.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    "\\begin{theorem}\\label{thm:first}\nFirst.\n"
                    "\\end{theorem}\n"
                    "\\begin{theorem}\\label{thm:second}\nSecond.\n"
                    "\\end{theorem}\n"
                    f"\\begin{{proof}}[{title}]\n"
                    "A proof body.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)
                units = {unit["id"]: unit for unit in inventory["units"]}

                self.assertIsNone(units["thm:first"]["proof"])
                self.assertIsNone(units["thm:second"]["proof"])
                self.assertTrue(
                    any(
                        "Named proof header does not resolve to exactly one"
                        in warning
                        for warning in inventory["warnings"]
                    ),
                    inventory,
                )
                self.assertFalse(
                    any(
                        unit["proof_association"]["method"]
                        == "adjacent_environment"
                        for unit in units.values()
                    ),
                    inventory,
                )

    def test_multiline_proof_title_uses_exact_header_location(self) -> None:
        source = self.base / "multiline-proof-title.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\begin{theorem}\\label{thm:first}\nFirst.\n"
            "\\end{theorem}\n"
            "\\begin{theorem}\\label{thm:second}\nSecond.\n"
            "\\end{theorem}\n"
            "\\begin{proof}[\n"
            "Proof of \\ref{thm:first}] Body uses \\ref{thm:second}.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)
        first = next(
            unit for unit in inventory["units"] if unit["id"] == "thm:first"
        )
        occurrences = {
            occurrence["target"]: occurrence
            for occurrence in first["reference_occurrences"]
        }

        self.assertEqual("named_environment", first["proof_association"]["method"])
        self.assertEqual("proof_header", occurrences["thm:first"]["structural_context"])
        self.assertEqual("proof_body", occurrences["thm:second"]["structural_context"])
        self.assertEqual(["thm:second"], first["candidate_internal_dependencies"])

    def test_named_proof_heading_resolves_balanced_hyperref_target(self) -> None:
        source = self.base / "named-proof-hyperref.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\begin{theorem}\\label{thm:x}\n"
            "Claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}[Proof of \\hyperref[thm:x]{Theorem 1}]\n"
            "Proof body.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)
        unit = inventory["units"][0]

        self.assertEqual("thm:x", unit["id"])
        self.assertEqual(
            {
                "file": source.name,
                "start_line": 5,
                "end_line": 7,
            },
            unit["proof"],
        )
        self.assertEqual("associated", unit["proof_association"]["status"])
        self.assertEqual(
            "named_environment", unit["proof_association"]["method"]
        )
        self.assertEqual("thm:x", unit["proof_association"]["target"])
        occurrence = next(
            row
            for row in unit["reference_occurrences"]
            if row["command"] == "hyperref"
        )
        self.assertEqual("proof_header", occurrence["structural_context"])
        self.assertEqual([], inventory["warnings"], inventory)

    def test_bracket_hyperref_is_recognized_as_an_exact_occurrence(self) -> None:
        source = self.base / "hyperref-occurrence.tex"
        text = "\\hyperref[thm:target]{the target theorem}"
        occurrences, warnings = proofcheck.scan_reference_occurrences(
            text,
            source,
            self.base,
        )

        self.assertEqual([], warnings)
        self.assertEqual(1, len(occurrences))
        self.assertEqual("hyperref", occurrences[0]["command"])
        self.assertEqual("thm:target", occurrences[0]["target"])
        self.assertEqual(1, occurrences[0]["line"])
        self.assertEqual(1, occurrences[0]["column"])

    def test_common_single_target_reference_commands_are_exact(self) -> None:
        source = self.base / "single-target-references.tex"
        commands = (
            "nameref",
            "vref",
            "Vref",
            "cpageref",
            "Cpageref",
            "labelcref",
            "labelcpageref",
        )
        expected = [
            (command, f"target:{index}")
            for index, command in enumerate(commands, 1)
        ]
        text = "\n".join(
            f"\\{command}{{{target}}}"
            for command, target in expected
        )

        occurrences, warnings = proofcheck.scan_reference_occurrences(
            text,
            source,
            self.base,
        )

        self.assertEqual([], warnings)
        self.assertEqual(
            expected,
            [
                (occurrence["command"], occurrence["target"])
                for occurrence in occurrences
            ],
        )
        self.assertEqual(
            list(range(1, len(commands) + 1)),
            [occurrence["line"] for occurrence in occurrences],
        )
        self.assertTrue(
            all(occurrence["column"] == 1 for occurrence in occurrences)
        )

    def test_reference_range_commands_emit_both_exact_targets(self) -> None:
        source = self.base / "range-references.tex"
        commands = (
            "crefrange",
            "Crefrange",
            "cpagerefrange",
            "Cpagerefrange",
            "vrefrange",
            "Vrefrange",
        )
        text = "\n".join(
            f"\\{command}{{range:{index}:first}}{{range:{index}:last}}"
            for index, command in enumerate(commands, 1)
        )
        expected = [
            (command, target)
            for index, command in enumerate(commands, 1)
            for target in (
                f"range:{index}:first",
                f"range:{index}:last",
            )
        ]

        occurrences, warnings = proofcheck.scan_reference_occurrences(
            text,
            source,
            self.base,
        )

        self.assertEqual([], warnings)
        self.assertEqual(
            expected,
            [
                (occurrence["command"], occurrence["target"])
                for occurrence in occurrences
            ],
        )
        self.assertEqual(
            [
                line
                for line in range(1, len(commands) + 1)
                for _ in range(2)
            ],
            [occurrence["line"] for occurrence in occurrences],
        )
        self.assertFalse(
            any(
                occurrence["command"] == "cref"
                for occurrence in occurrences
            ),
            occurrences,
        )

    def test_unsupported_ref_like_command_warns_once_without_config_noise(
        self,
    ) -> None:
        source = self.base / "unsupported-reference-command.tex"
        text = (
            "\\refstepcounter{theorem}\n"
            "\\crefname{theorem}{theorem}{theorems}\n"
            "\\Crefname{theorem}{Theorem}{Theorems}\n"
            "\\crefalias{lemma}{theorem}\n"
            "\\creflabelformat{equation}{(#2#1#3)}\n"
            "\\crefrangeconjunction{to}\n"
            "\\mysteryref{thm:target}\n"
        )

        occurrences, warnings = proofcheck.scan_reference_occurrences(
            text,
            source,
            self.base,
        )

        self.assertEqual([], occurrences)
        self.assertEqual(1, len(warnings), warnings)
        self.assertIn("\\mysteryref", warnings[0])
        self.assertIn("manual review", warnings[0].lower())
        self.assertIn(f"{source.name}:7:1", warnings[0])

    def test_equation_label_owner_promotes_the_formal_result_dependency(self) -> None:
        source = self.base / "equation-owner.tex"
        source.write_text(
            "\\newtheorem{lemma}{Lemma}\n"
            "\\begin{lemma}\\label{lem:prior}\n"
            "\\begin{equation}x=x\\label{eq:prior}\\end{equation}\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nBy reflexivity.\n\\end{proof}\n"
            "\\begin{lemma}\\label{lem:main}\nMain claim.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nUse \\eqref{eq:prior}.\n\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)
        main = next(
            unit for unit in inventory["units"] if unit["id"] == "lem:main"
        )
        occurrence = next(
            row
            for row in main["reference_occurrences"]
            if row["target"] == "eq:prior"
        )

        self.assertEqual("unique", occurrence["resolution_status"])
        self.assertEqual("lem:prior", occurrence["owner_unit_id"])
        self.assertEqual("statement", occurrence["owner_region"])
        self.assertEqual(["lem:prior"], main["candidate_internal_dependencies"])

    def test_formal_statement_reference_promotes_internal_candidate(self) -> None:
        source = self.base / "statement-dependency.tex"
        source.write_text(
            "\\newtheorem{lemma}{Lemma}\n"
            "\\begin{lemma}\\label{lem:prior}\nPrior claim.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nPrior proof.\n\\end{proof}\n"
            "\\begin{lemma}\\label{lem:main}\n"
            "Under Lemma~\\ref{lem:prior}, the main claim holds.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nThe proof repeats no source reference.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)
        unit_inventory = {
            unit["id"]: unit for unit in inventory["units"]
        }
        main = unit_inventory["lem:main"]

        self.assertEqual([], main["reference_occurrences"])
        self.assertEqual([], main["dependencies"])
        self.assertEqual(
            ["lem:prior"], main["candidate_internal_dependencies"]
        )

        cross_references = proofcheck.scan_cross_references(source)
        label_owners = proofcheck.reviewed_label_owners(
            cross_references, unit_inventory, self.base
        )
        source_lines = {source.resolve(): proofcheck.read_lines(source)}
        support_index = proofcheck.build_unowned_label_support_index(
            source_lines,
            unit_inventory.values(),
            label_owners,
            self.base,
        )
        rescanned = proofcheck.reviewed_span_evidence(
            "lem:main",
            main,
            self.base,
            label_owners,
            support_index,
        )
        self.assertEqual(
            main["candidate_internal_dependencies"],
            rescanned["candidate_internal_dependencies"],
        )

    def test_bounded_unowned_equation_promotes_supporting_result(self) -> None:
        source = self.base / "bounded-unowned-equation.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\newtheorem{lemma}{Lemma}\n"
            "\\begin{theorem}\\label{thm:support}\nSupport result.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\nSupport proof.\n\\end{proof}\n"
            "\\begin{theorem}\\label{thm:outside}\nOutside result.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\nOutside proof.\n\\end{proof}\n"
            "Before the proof heading, see \\ref{thm:outside}.\n"
            "\\section*{Proof of a calibration result}\n"
            "Using Theorem~\\ref{thm:support}, derive\n"
            "\\begin{equation}\n"
            "x=x.\n"
            "\\label{eq:bridge}\n"
            "\\end{equation}\n"
            "After the display, see \\ref{thm:outside}.\n"
            "\\begin{lemma}\\label{lem:main}\nMain claim.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nUse \\eqref{eq:bridge}.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)
        unit_inventory = {
            unit["id"]: unit for unit in inventory["units"]
        }
        main = unit_inventory["lem:main"]
        occurrence = next(
            row
            for row in main["reference_occurrences"]
            if row["target"] == "eq:bridge"
        )

        self.assertEqual("unowned", occurrence["resolution_status"])
        self.assertIsNone(occurrence["owner_unit_id"])
        self.assertEqual(["eq:bridge"], main["dependencies"])
        self.assertEqual(
            ["thm:support"], main["candidate_internal_dependencies"]
        )

        cross_references = proofcheck.scan_cross_references(source)
        label_owners = proofcheck.reviewed_label_owners(
            cross_references, unit_inventory, self.base
        )
        source_lines = {source.resolve(): proofcheck.read_lines(source)}
        support_index = proofcheck.build_unowned_label_support_index(
            source_lines,
            unit_inventory.values(),
            label_owners,
            self.base,
        )
        rescanned = proofcheck.reviewed_span_evidence(
            "lem:main",
            main,
            self.base,
            label_owners,
            support_index,
        )
        self.assertEqual(
            main["candidate_internal_dependencies"],
            rescanned["candidate_internal_dependencies"],
        )

    def test_bounded_unowned_dependency_uses_source_closure(self) -> None:
        included = self.base / "included-derivation.tex"
        included.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\begin{theorem}\\label{thm:support}\nSupport result.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\nSupport proof.\n\\end{proof}\n"
            "\\section*{Proof of the bridge identity}\n"
            "By Theorem~\\ref{thm:support},\n"
            "\\begin{align}\n"
            "x &= x.\\label{eq:bridge}\n"
            "\\end{align}\n",
            encoding="utf-8",
            newline="\n",
        )
        source = self.base / "cross-file-dependency.tex"
        source.write_text(
            "\\newtheorem{lemma}{Lemma}\n"
            "\\input{included-derivation}\n"
            "\\begin{lemma}\\label{lem:main}\nMain claim.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nUse \\eqref{eq:bridge}.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        closure = proofcheck.discover_source_closure(source)
        inventory = proofcheck.scan_formal_units(
            source,
            source_files=closure["files"],
            source_warnings=closure["warnings"],
        )
        main = next(
            unit for unit in inventory["units"] if unit["id"] == "lem:main"
        )

        self.assertEqual(
            ["thm:support"], main["candidate_internal_dependencies"]
        )

    def test_candidate_traversal_is_cycle_safe_and_suppresses_self(self) -> None:
        label_owners = {
            "eq:a": {"status": "unowned", "owner_unit_id": None},
            "eq:b": {"status": "unowned", "owner_unit_id": None},
            "eq:unsafe": {"status": "unowned", "owner_unit_id": None},
            "lem:main": {
                "status": "unique",
                "owner_unit_id": "lem:main",
            },
            "thm:prior": {
                "status": "unique",
                "owner_unit_id": "thm:prior",
            },
        }
        support_index = {
            "eq:a": {"reference_occurrences": [{"target": "eq:b"}]},
            "eq:b": {
                "reference_occurrences": [
                    {"target": "eq:a"},
                    {"target": "lem:main"},
                    {"target": "thm:prior"},
                ],
            },
        }

        candidates = proofcheck.resolve_candidate_internal_dependencies(
            "lem:main",
            [{"target": "eq:a"}, {"target": "eq:unsafe"}],
            label_owners,
            support_index,
        )

        self.assertEqual(["thm:prior"], candidates)

    def test_partial_and_stale_hash_proof_location_overrides_fail(self) -> None:
        self.paper.write_text(
            self.paper.read_text(encoding="utf-8")
            + "\\begin{proof}\nAgain by reflexivity.\n\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        self.audit = self.base / "proof-location-override-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                argparse.Namespace(paper=self.paper, output=self.audit)
            )
        ledger_path = self.make_complete_audit()
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        unit = inventory["units"][0]
        parser_proof = proofcheck.canonical_location(unit["proof"])
        parser_association = json.loads(
            json.dumps(unit["proof_association"])
        )
        reviewed_proof = {
            "file": "paper.tex",
            "start_line": 8,
            "end_line": 10,
        }
        reviewed_association = {
            "status": "associated",
            "method": "reviewed_manual",
            "target": "lem:main",
            "evidence_occurrence_ids": [],
        }
        unit["proof"] = reviewed_proof
        unit["proof_redirects"] = []
        unit["proof_association"] = reviewed_association
        unit["reference_occurrences"] = []
        unit["dependencies"] = []
        unit["candidate_internal_dependencies"] = []
        unit["citations"] = []
        write_json(inventory_path, inventory)
        ledger = read_json(ledger_path)
        ledger["review"]["source_reference_dispositions"] = []
        ledger["review"]["citation_dispositions"] = []
        write_json(ledger_path, ledger)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        proof_location_override = {
            "unit_id": "lem:main",
            "kind": "proof_location",
            "parser_proof": parser_proof,
            "reviewed_proof": reviewed_proof,
            "reviewed_proof_sha256": "0" * 64,
            "association_method": "reviewed_manual",
            "reason": "Rendered review selects the alternate complete proof.",
            "evidence": "The alternate proof span is inspected directly.",
        }
        association_override = {
            "unit_id": "lem:main",
            "kind": "proof_association",
            "parser_association": parser_association,
            "reviewed_association": reviewed_association,
            "rendered_source_evidence": (
                "Rendered source shows the complete alternate proof span."
            ),
            "reason": "The alternate proof is associated manually.",
            "evidence": "The association is recorded with exact source bounds.",
        }
        manifest["audit_scope"]["inventory_overrides"] = [
            proof_location_override,
            association_override,
        ]
        for review in manifest["parser_warning_reviews"]:
            review.update(
                {
                    "disposition": "confirmed_non_load_bearing",
                    "affected_units": [],
                    "evidence": (
                        "The additional orphan proof is a controlled test fixture."
                    ),
                }
            )
        write_json(manifest_path, manifest)
        self.refresh_dependency_review()

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("reviewed_proof_sha256 is stale" in error for error in errors),
            errors,
        )

        partial_manifest = read_json(manifest_path)
        del partial_manifest["audit_scope"]["inventory_overrides"][0][
            "parser_proof"
        ]
        partial_manifest["audit_scope"]["inventory_overrides"][0][
            "reviewed_proof_sha256"
        ] = proofcheck.source_span_sha256(self.paper, 8, 10)
        write_json(manifest_path, partial_manifest)
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("parser_proof is stale" in error for error in errors),
            errors,
        )

    def schema5_risk_checks(self, step_id: str) -> list[dict[str, str]]:
        rows = json.loads(json.dumps(make_risk_checks()))
        for row in rows:
            row["evidence"] = f"{row['evidence']} This disposition is specific to {step_id}."
        return rows

    def seal_schema5_challenge(
        self,
        ledger_path: Path,
        ledger: dict,
        *,
        covered_issue_ids: list[str] | None = None,
        artifact_text: str | None = None,
    ) -> None:
        independent = ledger["independent_check"]
        if independent.get("required") is not True:
            independent.update(
                {
                    "covered_issue_ids": [],
                    "source_snapshot_sha256": "",
                    "challenged_ledger_sha256": "",
                    "challenge_artifact_sha256": "",
                    "generated_utc": "",
                }
            )
            write_json(ledger_path, ledger)
            return

        artifact = self.audit / independent["artifact"]
        if artifact_text is not None:
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(artifact_text, encoding="utf-8", newline="\n")
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
        independent.update(
            {
                "covered_issue_ids": sorted(covered_issue_ids or []),
                "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
                "challenged_ledger_sha256": (
                    proofcheck.canonical_primary_ledger_sha256(ledger)
                ),
                "challenge_artifact_sha256": proofcheck.sha256_file(artifact),
                "generated_utc": "2026-08-09T00:00:00+00:00",
            }
        )
        write_json(ledger_path, ledger)
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        if report_path.is_file():
            report = report_path.read_text(encoding="utf-8")
            heading = "## Independent critical-path challenges"
            section_start = report.find(heading)
            if section_start >= 0:
                next_heading = report.find("\n## ", section_start + len(heading))
                section_end = len(report) if next_heading < 0 else next_heading
                section = report[section_start:section_end]
                unit_id = ledger["unit_id"]
                row = (
                    f"| {unit_id} | {independent['status']} | "
                    f"{independent['independence_level']} | "
                    f"{proofcheck.canonical_id_field(independent['covered_issue_ids'])} | "
                    f"{independent['challenger_verdict']} | "
                    f"{independent['reconciled_verdict']} | "
                    f"{json.dumps(independent.get('disagreements', []), ensure_ascii=False, separators=(',', ':'))} | "
                    f"{independent['artifact']} | "
                    f"{independent['source_snapshot_sha256']} | "
                    f"{independent['challenged_ledger_sha256']} | "
                    f"{independent['challenge_artifact_sha256']} | "
                    f"{independent['generated_utc']} | "
                    f"{independent.get('resolution') or 'none'} |"
                )
                section = re.sub(
                    rf"^\| {re.escape(unit_id)} \|.*$",
                    lambda _: row,
                    section,
                    count=1,
                    flags=re.MULTILINE,
                )
                report_path.write_text(
                    report[:section_start] + section + report[section_end:],
                    encoding="utf-8",
                    newline="\n",
                )

    def downgrade_ledger_fixture_to_schema4(self, ledger: dict) -> dict:
        source_units = {
            unit["id"]: unit
            for unit in ledger.get("source_units", [])
            if isinstance(unit, dict) and isinstance(unit.get("id"), str)
        }
        for step in ledger.get("steps", []):
            source_unit = source_units.get(step.pop("source_unit_id", None))
            if source_unit is not None:
                step["lines"] = list(source_unit["lines"])
            step.pop("support_role", None)
        ledger["schema_version"] = 4
        ledger["evidence_contract_version"] = 3
        ledger.pop("source_units", None)
        return ledger

    def downgrade_complete_audit_to_schema4(self) -> Path:
        ledger_path = self.make_complete_audit()
        ledger = self.downgrade_ledger_fixture_to_schema4(
            read_json(ledger_path)
        )
        for field in (
            "covered_issue_ids",
            "source_snapshot_sha256",
            "challenged_ledger_sha256",
            "challenge_artifact_sha256",
            "generated_utc",
        ):
            ledger["independent_check"].pop(field, None)
        write_json(ledger_path, ledger)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["schema_version"] = 4
        manifest["protocol"].update(
            {
                "artifact_schema_version": 4,
                "evidence_contract_version": 3,
                "closure_contract_version": 2,
                "validator_sha256": proofcheck.sha256_text(
                    "legacy validator fixture"
                ),
            }
        )
        write_json(manifest_path, manifest)

        versioned_paths = (
            self.audit / "PROGRESS.json",
            self.audit / "audit" / "01_index" / "theorem_inventory.json",
            self.audit
            / "audit"
            / "01_index"
            / "cross_reference_audit.json",
            self.audit / "audit" / "06_reports" / "ISSUE_LOG.json",
        )
        for path in versioned_paths:
            record = read_json(path)
            record["schema_version"] = 4
            write_json(path, record)

        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["schema_version"] = 4
        registry["closure_contract_version"] = 2
        registry["review"]["inventory_sha256"] = proofcheck.sha256_file(
            self.audit
            / "audit"
            / "01_index"
            / "theorem_inventory.json"
        )
        write_json(registry_path, registry)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report = report.replace(
            "- Artifact schema version: 5",
            "- Artifact schema version: 4",
        )
        report = report.replace(
            "- Evidence contract version: 4",
            "- Evidence contract version: 3",
        )
        report = report.replace(
            "- Closure contract version: 3",
            "- Closure contract version: 2",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")
        return ledger_path

    def upgrade_ledger_to_schema5(self, ledger_path: Path) -> dict:
        ledger = read_json(ledger_path)
        source_path = proofcheck.resolve_stored_path(
            ledger["source"]["file"], ledger_path.parent
        )
        source_units = []
        for index, step in enumerate(ledger["steps"], 1):
            unit_id = f"U{index:03d}"
            lines = step.pop("lines", None)
            if not (
                isinstance(lines, list)
                and len(lines) == 2
                and all(isinstance(value, int) for value in lines)
            ):
                existing = next(
                    (
                        row
                        for row in ledger.get("source_units", [])
                        if row.get("id") == step.get("source_unit_id")
                    ),
                    None,
                )
                if existing is None:
                    raise AssertionError(f"Cannot recover source unit for {step['id']}")
                lines = list(existing["lines"])
            if step.get("status") == "non_substantive":
                kind = "non_substantive"
            elif lines[0] == lines[1]:
                kind = "one_line"
            else:
                kind = "continued_sentence"
            source_units.append(
                {
                    "id": unit_id,
                    "lines": lines,
                    "kind": kind,
                    "source_sha256": proofcheck.source_span_sha256(
                        source_path, lines[0], lines[1]
                    ),
                    "partition_evidence": (
                        f"{unit_id} is the exact physical source unit assigned to "
                        f"{step['id']}."
                    ),
                }
            )
            step["source_unit_id"] = unit_id
            if step.get("inference", {}).get("moves"):
                step["support_role"] = "derivation"
        ledger["schema_version"] = 5
        ledger["evidence_contract_version"] = 4
        ledger["source_units"] = source_units
        self.seal_schema5_challenge(ledger_path, ledger)
        return read_json(ledger_path)

    def upgrade_complete_audit_to_schema5(self) -> list[Path]:
        ledger_paths = sorted(
            (self.audit / "audit" / "04_local_checks").glob("*.ledger.json")
        )
        for ledger_path in ledger_paths:
            self.upgrade_ledger_to_schema5(ledger_path)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["schema_version"] = 5
        manifest["protocol"].update(
            {
                "skill_name": "stat-paper-proofcheck",
                "skill_version": "1.0",
                "artifact_schema_version": 5,
                "evidence_contract_version": 4,
                "method_interface_schema_version": 1,
                "closure_contract_version": 3,
                "validator_sha256": proofcheck.sha256_file(SCRIPT),
            }
        )
        write_json(manifest_path, manifest)

        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        inventory["schema_version"] = 5
        write_json(inventory_path, inventory)

        crossref_path = (
            self.audit / "audit" / "01_index" / "cross_reference_audit.json"
        )
        crossref = read_json(crossref_path)
        crossref["schema_version"] = 5
        write_json(crossref_path, crossref)

        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        issue_log = read_json(issue_path)
        issue_log["schema_version"] = 5
        write_json(issue_path, issue_log)

        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["schema_version"] = 5
        write_json(progress_path, progress)

        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["schema_version"] = 5
        registry["closure_contract_version"] = 3
        registry["review"]["inventory_sha256"] = proofcheck.sha256_file(
            inventory_path
        )
        write_json(registry_path, registry)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report_lines = report_path.read_text(encoding="utf-8").splitlines()
        replacements = {
            "Skill version": "1.0",
            "Artifact schema version": "5",
            "Evidence contract version": "4",
            "Closure contract version": "3",
        }
        for index, line in enumerate(report_lines):
            for label, value in replacements.items():
                if line.startswith(f"- {label}:"):
                    report_lines[index] = f"- {label}: {value}"
        report_path.write_text(
            "\n".join(report_lines) + "\n", encoding="utf-8", newline="\n"
        )

        self.assertEqual("1.0", manifest["protocol"]["skill_version"])
        return ledger_paths

    def replace_ledger_source(
        self,
        ledger_path: Path,
        source: Path,
        *,
        statement_start: int,
        statement_end: int,
        source_end: int,
    ) -> tuple[dict, dict]:
        ledger = read_json(ledger_path)
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_extract(
                argparse.Namespace(
                    file=source,
                    start=1,
                    end=source_end,
                    statement_file=source,
                    statement_start=statement_start,
                    statement_end=statement_end,
                    separate_statement_reason=None,
                    unit_id="lem:main",
                    output=ledger_path,
                    force=True,
                )
            )
        extracted = read_json(ledger_path)
        ledger["source"] = extracted["source"]
        ledger["source_lines"] = extracted["source_lines"]
        statement_span = extracted["obligation"]["statement_spans"][0]
        ledger["obligation"]["statement_spans"] = [statement_span]
        ledger["obligation"]["conclusions"][0]["source_spans"] = [
            dict(statement_span)
        ]
        ledger["review"]["source_reference_dispositions"] = []
        ledger["review"]["citation_dispositions"] = []
        return ledger, extracted

    def make_schema5_long_display_ledger(self) -> Path:
        ledger_path = self.make_complete_audit()
        source = self.base / "long-indivisible-display.tex"
        source.write_text(
            "\\begin{lemma}\\label{lem:main}For every real $x$, $x=x$.\\end{lemma}\n"
            "\\begin{proof}\n"
            "\\begin{equation*}\n"
            "\\underbrace{\n"
            "\\left(\n"
            "x\n"
            "\\right)\n"
            "}_{\\text{the arbitrary real number}}\n"
            "=\n"
            "x.\n"
            "\\end{equation*}\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger, _ = self.replace_ledger_source(
            ledger_path,
            source,
            statement_start=1,
            statement_end=1,
            source_end=12,
        )
        statement_step = json.loads(json.dumps(ledger["steps"][0]))
        statement_step.pop("lines", None)
        statement_step["source_unit_id"] = "U001"
        open_step = {
            "id": "S002",
            "source_unit_id": "U002",
            "kind": "other",
            "status": "non_substantive",
            "issue_ids": [],
        }
        conclusion_step = json.loads(json.dumps(ledger["steps"][2]))
        conclusion_step.pop("lines", None)
        conclusion_step["source_unit_id"] = "U003"
        conclusion_step["support_role"] = "derivation"
        conclusion_step["checks"]["literal"] = (
            "Lines 3-11 form one displayed reflexive equality for the fixed x."
        )
        conclusion_step["checks"]["atomicity"] = {
            "status": "single_move",
            "evidence": (
                "The long display is one syntactic equality split only for layout."
            ),
        }
        conclusion_step["checks"]["adversarial"] = [
            "Removing the layout commands leaves the single equality x equals x."
        ]
        conclusion_step["risk_checks"] = self.schema5_risk_checks("S003")
        close_step = {
            "id": "S004",
            "source_unit_id": "U004",
            "kind": "other",
            "status": "non_substantive",
            "issue_ids": [],
        }
        ledger["steps"] = [statement_step, open_step, conclusion_step, close_step]
        ledger["source_units"] = [
            {
                "id": "U001",
                "lines": [1, 1],
                "kind": "one_line",
                "source_sha256": proofcheck.source_span_sha256(source, 1, 1),
                "partition_evidence": "The complete theorem statement is on line 1.",
            },
            {
                "id": "U002",
                "lines": [2, 2],
                "kind": "non_substantive",
                "source_sha256": proofcheck.source_span_sha256(source, 2, 2),
                "partition_evidence": "Line 2 is only the proof delimiter.",
            },
            {
                "id": "U003",
                "lines": [3, 11],
                "kind": "continued_display",
                "source_sha256": proofcheck.source_span_sha256(source, 3, 11),
                "partition_evidence": (
                    "Lines 3-11 are one uninterrupted display of x equals x."
                ),
            },
            {
                "id": "U004",
                "lines": [12, 12],
                "kind": "non_substantive",
                "source_sha256": proofcheck.source_span_sha256(source, 12, 12),
                "partition_evidence": "Line 12 is only the proof delimiter.",
            },
        ]
        ledger["schema_version"] = 5
        ledger["evidence_contract_version"] = 4
        self.seal_schema5_challenge(ledger_path, ledger)
        return ledger_path

    def make_schema5_parallel_steps_ledger(self) -> Path:
        ledger_path = self.make_complete_audit()
        source = self.base / "parallel-atomic-steps.tex"
        source.write_text(
            "\\begin{lemma}\\label{lem:main}For every real $x$, $x=x$.\\end{lemma}\n"
            "\\begin{proof}\n"
            "The element $x$ lies in the real-number domain.\n"
            "Equality is defined on pairs of real numbers.\n"
            "Reflexivity applies to every real number.\n"
            "Both coordinates of the current pair are the same $x$.\n"
            "Therefore $x=x$.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger, _ = self.replace_ledger_source(
            ledger_path,
            source,
            statement_start=1,
            statement_end=1,
            source_end=8,
        )

        def obligation_premise(
            premise_id: str, claim: str, reference: str, evidence: str
        ) -> dict:
            return {
                "id": premise_id,
                "role": "fact",
                "claim": claim,
                "origin": {
                    "kind": "obligation",
                    "reference": reference,
                    "anchor": {"kind": "statement_span", "index": 1},
                },
                "evidence": evidence,
            }

        def derivation_step(
            step_id: str,
            source_unit_id: str,
            claim: str,
            used_premises: list[dict],
            dependencies: list[dict],
            rule: str,
        ) -> dict:
            return {
                "id": step_id,
                "source_unit_id": source_unit_id,
                "support_role": "derivation",
                "kind": "conclusion" if step_id == "S007" else "setup",
                "goal": f"Establish the atomic claim recorded in {step_id}.",
                "restatement": claim,
                "premise_uses": used_premises,
                "dependencies": dependencies,
                "inference": {
                    "moves": [
                        {
                            "id": "M001",
                            "claim": claim,
                            "rule": rule,
                            "premise_ids": [row["id"] for row in used_premises],
                            "prior_move_ids": [],
                            "justification": (
                                f"The recorded premises justify only the {step_id} claim."
                            ),
                        }
                    ],
                    "conclusion_move": "M001",
                },
                "checks": {
                    "literal": f"The source line for {step_id} states this exact claim.",
                    "atomicity": {
                        "status": "single_move",
                        "evidence": f"{step_id} contains one independently checkable move.",
                    },
                    "adversarial": [
                        f"The weakest real-domain case was checked specifically for {step_id}."
                    ],
                },
                "side_conditions": [],
                "risk_checks": self.schema5_risk_checks(step_id),
                "status": "verified",
                "issue_ids": [],
            }

        statement = json.loads(json.dumps(ledger["steps"][0]))
        statement.pop("lines", None)
        statement["source_unit_id"] = "U001"
        proof_open = {
            "id": "S002",
            "source_unit_id": "U002",
            "kind": "other",
            "status": "non_substantive",
            "issue_ids": [],
        }
        parallel_claims = [
            "x lies in the real-number domain.",
            "Equality is defined on pairs of real numbers.",
            "Reflexivity applies to every real number.",
            "Both coordinates of the current pair are the same x.",
        ]
        parallel_steps = []
        for offset, claim in enumerate(parallel_claims, 3):
            reference = "/definitions/0" if offset in {4, 5} else "/quantifier_scope"
            source_claim = (
                ledger["obligation"]["definitions"][0]
                if reference == "/definitions/0"
                else ledger["obligation"]["quantifier_scope"]
            )
            parallel_steps.append(
                derivation_step(
                    f"S{offset:03d}",
                    f"U{offset:03d}",
                    claim,
                    [
                        obligation_premise(
                            "P001",
                            source_claim,
                            reference,
                            f"The locked statement supplies the input for S{offset:03d}.",
                        )
                    ],
                    [],
                    "Direct specialization of the locked theorem contract",
                )
            )
        final_dependencies = []
        final_premises = []
        for offset, claim in enumerate(parallel_claims, 3):
            step_id = f"S{offset:03d}"
            final_dependencies.append(
                {
                    "id": step_id,
                    "kind": "step",
                    "status": "verified",
                    "needed_form": claim,
                    "compatibility_check": (
                        f"{step_id} concerns the same real number x as the conclusion."
                    ),
                }
            )
            final_premises.append(
                {
                    "id": f"P{offset - 2:03d}",
                    "role": "fact",
                    "claim": claim,
                    "origin": {"kind": "prior_step", "reference": step_id},
                    "evidence": f"{step_id} supplies this exact prerequisite.",
                }
            )
        final_step = derivation_step(
            "S007",
            "U007",
            "x equals x",
            final_premises,
            final_dependencies,
            "Definition of equality and reflexivity",
        )
        proof_close = {
            "id": "S008",
            "source_unit_id": "U008",
            "kind": "other",
            "status": "non_substantive",
            "issue_ids": [],
        }
        ledger["steps"] = [
            statement,
            proof_open,
            *parallel_steps,
            final_step,
            proof_close,
        ]
        ledger["review"]["conclusion_step_id"] = "S007"
        ledger["review"]["conclusion_results"][0]["support"] = {
            "step_id": "S007",
            "move_id": "M001",
        }
        ledger["source_units"] = [
            {
                "id": f"U{line:03d}",
                "lines": [line, line],
                "kind": "non_substantive" if line in {2, 8} else "one_line",
                "source_sha256": proofcheck.source_span_sha256(source, line, line),
                "partition_evidence": (
                    f"Line {line} is the complete physical source unit U{line:03d}."
                ),
            }
            for line in range(1, 9)
        ]
        ledger["schema_version"] = 5
        ledger["evidence_contract_version"] = 4
        self.seal_schema5_challenge(ledger_path, ledger)
        return ledger_path

    def test_nonexecuting_tex_cannot_create_formal_units_or_proof_spans(
        self,
    ) -> None:
        cases = {
            "newcommand": (
                "\\newcommand{\\ghost}{"
                "\\newtheorem{ghost}{Ghost}"
                "\\begin{ghost}\\label{thm:ghost}Ghost.\\end{ghost}"
                "\\begin{proof}Ghost.\\end{proof}}\n"
            ),
            "verbatim": (
                "\\begin{verbatim}\n"
                "\\begin{theorem}\\label{thm:ghost}Ghost.\\end{theorem}\n"
                "\\begin{proof}Ghost.\\end{proof}\n"
                "\\end{verbatim}\n"
            ),
            "lstlisting": (
                "\\begin{lstlisting}\n"
                "\\begin{theorem}\\label{thm:ghost}Ghost.\\end{theorem}\n"
                "\\begin{proof}Ghost.\\end{proof}\n"
                "\\end{lstlisting}\n"
            ),
            "minted": (
                "\\begin{minted}{latex}\n"
                "\\begin{theorem}\\label{thm:ghost}Ghost.\\end{theorem}\n"
                "\\begin{proof}Ghost.\\end{proof}\n"
                "\\end{minted}\n"
            ),
            "iffalse": (
                "\\iffalse\n"
                "\\begin{theorem}\\label{thm:ghost}Ghost.\\end{theorem}\n"
                "\\begin{proof}Ghost.\\end{proof}\n"
                "\\fi\n"
            ),
        }

        for case, text in cases.items():
            with self.subTest(case=case):
                source = self.base / f"masked-{case}.tex"
                source.write_text(text, encoding="utf-8", newline="\n")

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual([], inventory["units"], inventory)
                self.assertEqual(
                    set(),
                    proofcheck.proof_environment_spans(source),
                    inventory,
                )
                self.assertEqual([], inventory["warnings"], inventory)
                if case == "newcommand":
                    self.assertNotIn(
                        "ghost",
                        inventory["formal_environments"],
                        inventory,
                    )

    def test_inline_verb_delimiter_inside_multiline_macro_stays_masked(
        self,
    ) -> None:
        source = self.base / "multiline-macro-inline-verb.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\newcommand{\\ghost}{%\n"
            "  \\verb|}|%\n"
            "  \\begin{theorem}\\label{thm:ghost}Ghost.\\end{theorem}\n"
            "  \\begin{proof}Ghost proof.\\end{proof}\n"
            "}\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Real claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Real proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        self.assertEqual(
            {(10, 12)}, proofcheck.proof_environment_spans(source)
        )
        self.assertEqual([], inventory["warnings"], inventory)

    def test_inline_verb_delimiters_inside_multiline_environment_stay_masked(
        self,
    ) -> None:
        source = self.base / "multiline-environment-inline-verb.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\NewDocumentEnvironment{ghost}{}{%\n"
            "  \\verb|}|%\n"
            "  \\begin{theorem}\\label{thm:ghost}Ghost.\\end{theorem}\n"
            "  \\begin{proof}Ghost proof.\\end{proof}\n"
            "}{%\n"
            "  \\verb|{|%\n"
            "}\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Real claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Real proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        self.assertEqual(
            {(12, 14)}, proofcheck.proof_environment_spans(source)
        )
        self.assertEqual([], inventory["warnings"], inventory)

    def test_robust_command_definitions_mask_ghost_proof_structure(self) -> None:
        for command in (
            "newrobustcmd",
            "renewrobustcmd",
            "providerobustcmd",
        ):
            with self.subTest(command=command):
                source = self.base / f"{command}-masked.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    f"\\{command}{{\\ghost}}{{%\n"
                    "\\begin{theorem}\\label{thm:ghost}Ghost."
                    "\\end{theorem}\n"
                    "\\begin{proof}Ghost proof.\\end{proof}\n"
                    "}\n"
                    "\\begin{theorem}\\label{thm:real}\n"
                    "Real claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Real proof.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual(
                    ["thm:real"],
                    [unit["id"] for unit in inventory["units"]],
                    inventory,
                )
                self.assertEqual(
                    {(9, 11)}, proofcheck.proof_environment_spans(source)
                )
                self.assertEqual([], inventory["warnings"], inventory)

    def test_named_and_protected_definitions_mask_ghost_proof_structure(
        self,
    ) -> None:
        definitions = {
            "@namedef": "\\@namedef{ghost}#1",
            "csdef": "\\csdef{ghost}#1",
            "csedef": "\\csedef{ghost}#1",
            "csgdef": "\\csgdef{ghost}#1",
            "csxdef": "\\csxdef{ghost}#1",
            "protected@edef": "\\protected@edef\\ghost#1",
            "protected@xdef": "\\protected@xdef\\ghost#1",
        }
        for command, definition in definitions.items():
            with self.subTest(command=command):
                source = self.base / f"{command.replace('@', '-')}-masked.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    f"{definition}{{%\n"
                    "\\begin{theorem}\\label{thm:ghost}Ghost."
                    "\\end{theorem}\n"
                    "\\begin{proof}Ghost proof.\\end{proof}\n"
                    "}\n"
                    "\\begin{theorem}\\label{thm:real}\n"
                    "Real claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Real proof.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual(
                    ["thm:real"],
                    [unit["id"] for unit in inventory["units"]],
                    inventory,
                )
                self.assertEqual(
                    {(9, 11)},
                    proofcheck.proof_environment_spans(source),
                )
                self.assertEqual([], inventory["warnings"], inventory)

    def test_extended_inline_verbatim_forms_mask_ghost_proof_structure(
        self,
    ) -> None:
        inline_forms = {
            "lstinline": (
                "\\lstinline|\\begin{theorem}\\label{thm:ghost}Ghost."
                "\\end{theorem}\\begin{proof}Ghost.\\end{proof}|"
            ),
            "mintinline": (
                "\\mintinline{latex}|\\begin{theorem}"
                "\\label{thm:ghost}Ghost.\\end{theorem}"
                "\\begin{proof}Ghost.\\end{proof}|"
            ),
            "Verb-options": (
                "\\Verb[formatcom=\\bfseries]|\\begin{theorem}"
                "\\label{thm:ghost}Ghost.\\end{theorem}"
                "\\begin{proof}Ghost.\\end{proof}|"
            ),
        }
        for case, inline_form in inline_forms.items():
            with self.subTest(case=case):
                source = self.base / f"{case}-masked.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    f"{inline_form}\n"
                    "\\begin{theorem}\\label{thm:real}\n"
                    "Real claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Real proof.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual(
                    ["thm:real"],
                    [unit["id"] for unit in inventory["units"]],
                    inventory,
                )
                self.assertEqual(
                    {(6, 8)}, proofcheck.proof_environment_spans(source)
                )
                self.assertEqual([], inventory["warnings"], inventory)

    def test_real_theorem_and_manual_proof_survive_preceding_masked_tex(
        self,
    ) -> None:
        source = self.base / "masked-positive-control.tex"
        source.write_text(
            "\\newcommand{\\ghost}{\\newtheorem{ghost}{Ghost}"
            "\\begin{ghost}\\label{thm:macro}Ghost.\\end{ghost}"
            "\\begin{proof}Ghost.\\end{proof}}\n"
            "\\begin{verbatim}\n"
            "\\begin{theorem}\\label{thm:verbatim}Ghost.\\end{theorem}"
            "\\begin{proof}Ghost.\\end{proof}\n"
            "\\end{verbatim}\n"
            "\\begin{lstlisting}\n"
            "\\begin{theorem}\\label{thm:listing}Ghost.\\end{theorem}"
            "\\begin{proof}Ghost.\\end{proof}\n"
            "\\end{lstlisting}\n"
            "\\begin{minted}{latex}\n"
            "\\begin{theorem}\\label{thm:minted}Ghost.\\end{theorem}"
            "\\begin{proof}Ghost.\\end{proof}\n"
            "\\end{minted}\n"
            "\\iffalse\n"
            "\\begin{theorem}\\label{thm:disabled}Ghost.\\end{theorem}"
            "\\begin{proof}Ghost.\\end{proof}\n"
            "\\fi\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Real claim.\n"
            "\\end{theorem}\n"
            "\\subsection{Proof of Theorem \\ref{thm:real}}\n"
            "Real argument.\n"
            "\\qed\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        self.assertNotIn("ghost", inventory["formal_environments"], inventory)
        self.assertEqual(
            set(),
            proofcheck.proof_environment_spans(source),
            inventory,
        )
        unit = inventory["units"][0]
        self.assertEqual(
            {
                "file": source.name,
                "start_line": 14,
                "end_line": 16,
            },
            unit["statement"],
        )
        self.assertEqual(
            {
                "file": source.name,
                "start_line": 17,
                "end_line": 19,
            },
            unit["proof"],
        )
        self.assertEqual("associated", unit["proof_association"]["status"])
        self.assertEqual(
            "named_heading", unit["proof_association"]["method"]
        )
        self.assertEqual(
            "thm:real", unit["proof_association"]["target"]
        )
        self.assertEqual([], inventory["warnings"], inventory)

    def test_primitive_definition_ignores_comment_brace_before_body(
        self,
    ) -> None:
        source = self.base / "primitive-definition-comment-brace.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\def\\ghost% comment with {decoy}\n"
            "{\\begin{theorem}\\label{thm:ghost}Ghost.\\end{theorem}}\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Real claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Real proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        unit = inventory["units"][0]
        self.assertEqual(
            {
                "file": source.name,
                "start_line": 4,
                "end_line": 6,
            },
            unit["statement"],
        )
        self.assertEqual(
            {
                "file": source.name,
                "start_line": 7,
                "end_line": 9,
            },
            unit["proof"],
        )
        self.assertEqual(
            {(7, 9)}, proofcheck.proof_environment_spans(source)
        )
        self.assertEqual([], inventory["warnings"], inventory)

    def test_newif_declaration_does_not_poison_later_unconditional_unit(
        self,
    ) -> None:
        source = self.base / "newif-unconditional-unit.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\newif\\ifdraft\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Real claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Real proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        unit = inventory["units"][0]
        self.assertEqual("associated", unit["proof_association"]["status"])
        self.assertEqual(
            "adjacent_environment", unit["proof_association"]["method"]
        )
        self.assertTrue(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 3,
                    "end_line": 5,
                },
                self.base,
                "thm:real",
            )
        )
        self.assertEqual([], inventory["warnings"], inventory)

    def test_newif_custom_conditional_is_reviewed_without_losing_candidates(
        self,
    ) -> None:
        source = self.base / "newif-custom-conditional.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\newif\\ifdraft\n"
            "\\ifdraft\n"
            "\\begin{theorem}\\label{thm:conditional}\n"
            "Conditional claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Conditional proof.\n"
            "\\end{proof}\n"
            "\\fi\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Unconditional claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Unconditional proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:conditional", "thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        self.assertTrue(
            all(
                unit["proof_association"]["status"] == "associated"
                for unit in inventory["units"]
            ),
            inventory,
        )
        conditional_warnings = [
            warning
            for warning in inventory["warnings"]
            if "\\ifdraft" in warning
            and "review" in warning.lower()
        ]
        self.assertEqual(1, len(conditional_warnings), inventory)
        self.assertIn(f"{source.name}:3", conditional_warnings[0])
        self.assertFalse(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 4,
                    "end_line": 6,
                },
                self.base,
                "thm:conditional",
            )
        )
        self.assertTrue(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 11,
                    "end_line": 13,
                },
                self.base,
                "thm:real",
            )
        )

    def test_let_assignments_do_not_poison_later_unconditional_labels(
        self,
    ) -> None:
        assignments = {
            "let": "\\let\\ifdraft\\iffalse",
            "global-let": "\\global\\let\\ifdraft\\iftrue",
        }
        for case, assignment in assignments.items():
            with self.subTest(case=case):
                source = self.base / f"{case}-unconditional-label.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    f"{assignment}\n"
                    "\\begin{theorem}\\label{thm:real}\n"
                    "Real claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Real proof.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual(
                    ["thm:real"],
                    [unit["id"] for unit in inventory["units"]],
                    inventory,
                )
                self.assertTrue(
                    proofcheck.locked_span_contains_label(
                        {
                            "file": source.name,
                            "start_line": 3,
                            "end_line": 5,
                        },
                        self.base,
                        "thm:real",
                    )
                )
                self.assertEqual([], inventory["warnings"], inventory)

    def test_expl3_definitions_mask_fake_structure_for_N_and_c_targets(
        self,
    ) -> None:
        definitions = {
            "N-type": "\\cs_new:Npn \\ghost #1",
            "c-type": "\\cs_new:cpn { ghost } #1",
        }
        for case, definition in definitions.items():
            with self.subTest(case=case):
                source = self.base / f"expl3-{case}.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    f"{definition} {{\n"
                    "\\begin{theorem}\\label{thm:ghost}Ghost."
                    "\\end{theorem}\n"
                    "\\begin{proof}Ghost proof.\\end{proof}}\n"
                    "\\begin{theorem}\\label{thm:real}\n"
                    "Real claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Real proof.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual(
                    ["thm:real"],
                    [unit["id"] for unit in inventory["units"]],
                    inventory,
                )
                unit = inventory["units"][0]
                proof = unit["proof"]
                self.assertIsInstance(proof, dict, inventory)
                self.assertEqual(
                    {(proof["start_line"], proof["end_line"])},
                    proofcheck.proof_environment_spans(source),
                )
                self.assertEqual([], inventory["warnings"], inventory)

    def test_named_proof_heading_inside_iffalse_cannot_associate(self) -> None:
        source = self.base / "inactive-named-proof-heading.tex"
        text = (
            "\\newtheorem{theorem}{Theorem}\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Real claim.\n"
            "\\end{theorem}\n"
            "\\iffalse\n"
            "\\subsection{Proof of Theorem \\ref{thm:real}}\n"
            "\\fi\n"
            "Detached text must not acquire proof status.\n"
            "\\qed\n"
        )
        source.write_text(text, encoding="utf-8", newline="\n")

        inventory = proofcheck.scan_formal_units(source)
        unit = next(
            row for row in inventory["units"] if row["id"] == "thm:real"
        )

        self.assertIsNone(unit["proof"], inventory)
        self.assertEqual("unassociated", unit["proof_association"]["status"])
        self.assertEqual("none", unit["proof_association"]["method"])
        self.assertEqual([], unit["reference_occurrences"])
        self.assertTrue(
            any(
                "Proof-required result has no associated proof: thm:real"
                in warning
                for warning in inventory["warnings"]
            ),
            inventory,
        )

    def test_inactive_labels_and_references_are_excluded(self) -> None:
        source = self.base / "inactive-cross-references.tex"
        source.write_text(
            "\\iffalse\n"
            "\\label{eq:ghost}\n"
            "See \\ref{eq:ghost}.\n"
            "\\fi\n"
            "\\label{eq:real}\n"
            "See \\eqref{eq:real}.\n",
            encoding="utf-8",
            newline="\n",
        )

        cross_references = proofcheck.scan_cross_references(source)

        self.assertEqual(["eq:real"], list(cross_references["labels"]))
        self.assertEqual(["eq:real"], list(cross_references["references"]))
        self.assertEqual(
            ["eq:real"],
            [row["target"] for row in cross_references["occurrences"]],
        )
        self.assertEqual(
            {
                "unique_labels": 1,
                "unique_references": 1,
                "broken_references": 0,
                "orphan_labels": 0,
                "duplicate_labels": 0,
            },
            cross_references["counts"],
        )
        self.assertEqual([], cross_references["warnings"])

    def test_inactive_unless_does_not_leak_into_later_theorem_discovery(
        self,
    ) -> None:
        source = self.base / "inactive-unless-structure.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\iffalse\n"
            "\\unless\\iftrue\n"
            "\\begin{theorem}\\label{thm:ghost}\n"
            "Ghost claim.\n"
            "\\end{theorem}\n"
            "\\fi\n"
            "\\fi\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Real claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Real proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        self.assertEqual(
            "associated",
            inventory["units"][0]["proof_association"]["status"],
        )
        self.assertEqual([], inventory["warnings"], inventory)

    def test_inactive_unless_does_not_leak_into_locked_label_recognition(
        self,
    ) -> None:
        source = self.base / "inactive-unless-labels.tex"
        source.write_text(
            "\\iffalse\n"
            "\\unless\\iftrue\n"
            "\\label{eq:ghost}\n"
            "See \\ref{eq:ghost}.\n"
            "\\fi\n"
            "\\fi\n"
            "\\label{eq:real}\n"
            "See \\ref{eq:real}.\n",
            encoding="utf-8",
            newline="\n",
        )
        span = {
            "file": source.name,
            "start_line": 1,
            "end_line": 8,
        }

        cross_references = proofcheck.scan_cross_references(source)

        self.assertFalse(
            proofcheck.locked_span_contains_label(
                span,
                self.base,
                "eq:ghost",
            )
        )
        self.assertTrue(
            proofcheck.locked_span_contains_label(
                span,
                self.base,
                "eq:real",
            )
        )
        self.assertEqual(["eq:real"], list(cross_references["labels"]))
        self.assertEqual(["eq:real"], list(cross_references["references"]))
        self.assertEqual([], cross_references["warnings"])

    def test_unknown_conditional_preserves_candidates_and_warns(self) -> None:
        source = self.base / "unknown-conditional.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\ifdefined\\pdfoutput\n"
            "\\begin{theorem}\\label{thm:conditional}\n"
            "Conditional claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Conditional proof.\n"
            "\\end{proof}\n"
            "\\fi\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)
        self.assertEqual(
            ["thm:conditional"],
            [row["id"] for row in inventory["units"]],
            inventory,
        )
        unit = inventory["units"][0]
        self.assertEqual(
            {
                "file": source.name,
                "start_line": 3,
                "end_line": 5,
            },
            unit["statement"],
        )
        self.assertEqual(
            {
                "file": source.name,
                "start_line": 6,
                "end_line": 8,
            },
            unit["proof"],
        )
        self.assertEqual(
            "adjacent_environment", unit["proof_association"]["method"]
        )
        self.assertEqual(
            "thm:conditional", unit["proof_association"]["target"]
        )
        self.assertEqual(
            {(6, 8)}, proofcheck.proof_environment_spans(source)
        )
        conditional_warnings = [
            warning
            for warning in inventory["warnings"]
            if "\\ifdefined" in warning
            and "conditional" in warning.lower()
            and "review" in warning.lower()
        ]
        self.assertEqual(1, len(conditional_warnings), inventory)
        self.assertIn(f"{source.name}:2", conditional_warnings[0])

    def test_argument_style_conditionals_warn_without_poisoning_later_labels(
        self,
    ) -> None:
        conditionals = {
            "ifthenelse": (
                "\\ifthenelse{\\boolean{draft}}{Draft text.}{Final text.}"
            ),
            "ifdef": "\\ifdef{\\draftmode}{Draft text.}{Final text.}",
        }
        for command, conditional in conditionals.items():
            with self.subTest(command=command):
                source = self.base / f"argument-{command}.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    f"{conditional}\n"
                    "\\begin{theorem}\\label{thm:real}\n"
                    "Real claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Real proof.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual(
                    ["thm:real"],
                    [unit["id"] for unit in inventory["units"]],
                    inventory,
                )
                self.assertEqual(
                    "associated",
                    inventory["units"][0]["proof_association"]["status"],
                )
                self.assertTrue(
                    proofcheck.locked_span_contains_label(
                        {
                            "file": source.name,
                            "start_line": 3,
                            "end_line": 5,
                        },
                        self.base,
                        "thm:real",
                    )
                )
                conditional_warnings = [
                    warning
                    for warning in inventory["warnings"]
                    if f"\\{command}" in warning
                    and "review" in warning.lower()
                ]
                self.assertEqual(1, len(conditional_warnings), inventory)
                self.assertIn(f"{source.name}:2", conditional_warnings[0])

    def test_argument_conditional_inside_iffalse_does_not_steal_outer_fi(
        self,
    ) -> None:
        source = self.base / "argument-conditional-inside-iffalse.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\iffalse\n"
            "\\ifthenelse{\\boolean{draft}}{%\n"
            "\\begin{theorem}\\label{thm:ghost}Ghost.\\end{theorem}\n"
            "}{Final text.}\n"
            "\\fi\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Real claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Real proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        self.assertTrue(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 7,
                    "end_line": 9,
                },
                self.base,
                "thm:real",
            )
        )

    def test_argument_conditional_inside_unknown_primitive_preserves_outer_fi(
        self,
    ) -> None:
        source = self.base / "argument-conditional-inside-ifdraft.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\newif\\ifdraft\n"
            "\\ifdraft\n"
            "\\ifthenelse{\\boolean{nested}}{%\n"
            "\\begin{theorem}\\label{thm:conditional}\n"
            "Conditional claim.\n"
            "\\end{theorem}\n"
            "}{Final text.}\n"
            "\\fi\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Real claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Real proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:conditional", "thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        self.assertFalse(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 5,
                    "end_line": 7,
                },
                self.base,
                "thm:conditional",
            )
        )
        self.assertTrue(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 10,
                    "end_line": 12,
                },
                self.base,
                "thm:real",
            )
        )
        self.assertEqual(
            1,
            sum(
                "\\ifdraft" in warning and "review" in warning.lower()
                for warning in inventory["warnings"]
            ),
            inventory,
        )

    def test_lowercase_argument_conditionals_inside_iffalse_preserve_outer_fi(
        self,
    ) -> None:
        openings = {
            "ifbool": "\\ifbool{draft}{%",
            "ifnumgreater": "\\ifnumgreater{2}{1}{%",
            "ifdimgreater": "\\ifdimgreater{2pt}{1pt}{%",
        }
        for command, opening in openings.items():
            with self.subTest(command=command):
                source = self.base / f"{command}-inside-iffalse.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    "\\iffalse\n"
                    f"{opening}\n"
                    "\\begin{theorem}\\label{thm:ghost}\n"
                    "Ghost claim.\n"
                    "\\end{theorem}\n"
                    "}{Final text.}\n"
                    "\\fi\n"
                    "\\begin{theorem}\\label{thm:real}\n"
                    "Real claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Real proof.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual(
                    ["thm:real"],
                    [unit["id"] for unit in inventory["units"]],
                    inventory,
                )
                self.assertTrue(
                    proofcheck.locked_span_contains_label(
                        {
                            "file": source.name,
                            "start_line": 9,
                            "end_line": 11,
                        },
                        self.base,
                        "thm:real",
                    )
                )

    def test_lowercase_argument_conditionals_inside_unknown_primitive_preserve_fi(
        self,
    ) -> None:
        openings = {
            "ifbool": "\\ifbool{draft}{%",
            "ifnumgreater": "\\ifnumgreater{2}{1}{%",
            "ifdimgreater": "\\ifdimgreater{2pt}{1pt}{%",
        }
        for command, opening in openings.items():
            with self.subTest(command=command):
                source = self.base / f"{command}-inside-ifdraft.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    "\\newif\\ifdraft\n"
                    "\\ifdraft\n"
                    f"{opening}\n"
                    "\\begin{theorem}\\label{thm:conditional}\n"
                    "Conditional claim.\n"
                    "\\end{theorem}\n"
                    "}{Final text.}\n"
                    "\\fi\n"
                    "\\begin{theorem}\\label{thm:real}\n"
                    "Real claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Real proof.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual(
                    ["thm:conditional", "thm:real"],
                    [unit["id"] for unit in inventory["units"]],
                    inventory,
                )
                self.assertFalse(
                    proofcheck.locked_span_contains_label(
                        {
                            "file": source.name,
                            "start_line": 5,
                            "end_line": 7,
                        },
                        self.base,
                        "thm:conditional",
                    )
                )
                self.assertTrue(
                    proofcheck.locked_span_contains_label(
                        {
                            "file": source.name,
                            "start_line": 10,
                            "end_line": 12,
                        },
                        self.base,
                        "thm:real",
                    )
                )

    def test_uppercase_and_expl3_argument_conditionals_are_review_bounded(
        self,
    ) -> None:
        conditionals = {
            "IfFileExists": (
                "\\IfFileExists{draft.tex}{\n",
                "}{Fallback text.}\n",
            ),
            "bool_if:NTF": (
                "\\bool_if:NTF \\l_tmpa_bool {\n",
                "}{Fallback text.}\n",
            ),
        }
        for command, (opening, closing) in conditionals.items():
            with self.subTest(command=command):
                source = self.base / f"argument-{command.replace(':', '-')}.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    f"{opening}"
                    "\\begin{theorem}\\label{thm:conditional}\n"
                    "Conditional claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Conditional proof.\n"
                    "\\end{proof}\n"
                    f"{closing}"
                    "\\begin{theorem}\\label{thm:real}\n"
                    "Unconditional claim.\n"
                    "\\end{theorem}\n"
                    "\\begin{proof}\n"
                    "Unconditional proof.\n"
                    "\\end{proof}\n",
                    encoding="utf-8",
                    newline="\n",
                )

                inventory = proofcheck.scan_formal_units(source)

                self.assertEqual(
                    ["thm:conditional", "thm:real"],
                    [unit["id"] for unit in inventory["units"]],
                    inventory,
                )
                self.assertTrue(
                    all(
                        unit["proof_association"]["status"] == "associated"
                        for unit in inventory["units"]
                    ),
                    inventory,
                )
                conditional_warnings = [
                    warning
                    for warning in inventory["warnings"]
                    if f"\\{command}" in warning
                    and "review" in warning.lower()
                ]
                self.assertEqual(1, len(conditional_warnings), inventory)
                self.assertIn(f"{source.name}:2", conditional_warnings[0])
                self.assertFalse(
                    proofcheck.locked_span_contains_label(
                        {
                            "file": source.name,
                            "start_line": 3,
                            "end_line": 5,
                        },
                        self.base,
                        "thm:conditional",
                    )
                )
                self.assertTrue(
                    proofcheck.locked_span_contains_label(
                        {
                            "file": source.name,
                            "start_line": 10,
                            "end_line": 12,
                        },
                        self.base,
                        "thm:real",
                    )
                )

    def test_multiline_expl3_n_type_conditional_is_review_bounded(
        self,
    ) -> None:
        source = self.base / "argument-bool-if-ntf-multiline.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\bool_if:NTF\n"
            "  \\l_tmpa_bool\n"
            "  {\n"
            "\\begin{theorem}\\label{thm:conditional}\n"
            "Conditional claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Conditional proof.\n"
            "\\end{proof}\n"
            "  }\n"
            "  {Fallback text.}\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Unconditional claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Unconditional proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:conditional", "thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        self.assertTrue(
            all(
                unit["proof_association"]["status"] == "associated"
                for unit in inventory["units"]
            ),
            inventory,
        )
        warnings = [
            warning
            for warning in inventory["warnings"]
            if "\\bool_if:NTF" in warning and "review" in warning.lower()
        ]
        self.assertEqual(1, len(warnings), inventory)
        self.assertIn(f"{source.name}:2", warnings[0])
        self.assertFalse(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 5,
                    "end_line": 7,
                },
                self.base,
                "thm:conditional",
            )
        )
        self.assertTrue(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 13,
                    "end_line": 15,
                },
                self.base,
                "thm:real",
            )
        )

    def test_multiline_expl3_nn_type_conditional_is_review_bounded(
        self,
    ) -> None:
        source = self.base / "argument-cs-if-eq-nntf-multiline.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\cs_if_eq:NNTF\n"
            "  \\l_tmpa_tl\n"
            "  \\l_tmpb_tl\n"
            "  {\n"
            "\\begin{theorem}\\label{thm:conditional}\n"
            "Conditional claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Conditional proof.\n"
            "\\end{proof}\n"
            "  }\n"
            "  {Fallback text.}\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Unconditional claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Unconditional proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:conditional", "thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        warnings = [
            warning
            for warning in inventory["warnings"]
            if "\\cs_if_eq:NNTF" in warning and "review" in warning.lower()
        ]
        self.assertEqual(1, len(warnings), inventory)
        self.assertIn(f"{source.name}:2", warnings[0])
        self.assertFalse(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 6,
                    "end_line": 8,
                },
                self.base,
                "thm:conditional",
            )
        )
        self.assertTrue(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 14,
                    "end_line": 16,
                },
                self.base,
                "thm:real",
            )
        )

    def test_ifnextchar_token_argument_is_review_bounded(self) -> None:
        source = self.base / "argument-ifnextchar-token.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\makeatletter\n"
            "\\@ifnextchar\n"
            "  [\n"
            "  {\n"
            "\\begin{theorem}\\label{thm:conditional}\n"
            "Conditional claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Conditional proof.\n"
            "\\end{proof}\n"
            "  }\n"
            "  {Fallback text.}\n"
            "\\makeatother\n"
            "\\begin{theorem}\\label{thm:real}\n"
            "Unconditional claim.\n"
            "\\end{theorem}\n"
            "\\begin{proof}\n"
            "Unconditional proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertEqual(
            ["thm:conditional", "thm:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        warnings = [
            warning
            for warning in inventory["warnings"]
            if "\\@ifnextchar" in warning and "review" in warning.lower()
        ]
        self.assertEqual(1, len(warnings), inventory)
        self.assertIn(f"{source.name}:3", warnings[0])
        self.assertFalse(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 6,
                    "end_line": 8,
                },
                self.base,
                "thm:conditional",
            )
        )
        self.assertTrue(
            proofcheck.locked_span_contains_label(
                {
                    "file": source.name,
                    "start_line": 15,
                    "end_line": 17,
                },
                self.base,
                "thm:real",
            )
        )

    def test_thmtools_declaretheorem_registers_the_formal_environment(
        self,
    ) -> None:
        source = self.base / "thmtools-declaretheorem.tex"
        source.write_text(
            "\\usepackage{thmtools}\n"
            "\\declaretheorem[name=Proposition]{proposition}\n"
            "\\begin{proposition}\\label{prop:real}\n"
            "The declared proposition holds.\n"
            "\\end{proposition}\n"
            "\\begin{proof}\n"
            "The claim follows directly.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertIn("proposition", inventory["formal_environments"])
        self.assertEqual(
            ["prop:real"],
            [unit["id"] for unit in inventory["units"]],
            inventory,
        )
        self.assertEqual(
            "associated",
            inventory["units"][0]["proof_association"]["status"],
        )
        self.assertEqual([], inventory["warnings"], inventory)

    def test_adversarial_masking_order_preserves_real_structure(self) -> None:
        source = self.base / "adversarial-masking-order.tex"
        source.write_text(
            "\\newtheorem{result}{Result}\n"
            "\\newcommand{\\ghost}{\\begin{verbatim}}\n"
            "\\verb|%| \\begin{result}\\label{res:real}\n"
            "Real claim.\n"
            "\\end{result}\n"
            "\\begin{proof}\n"
            "Real proof.\n"
            "\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

        inventory = proofcheck.scan_formal_units(source)

        self.assertIn("result", inventory["formal_environments"])
        self.assertEqual(
            ["res:real"],
            [row["id"] for row in inventory["units"]],
            inventory,
        )
        unit = inventory["units"][0]
        self.assertEqual(
            {
                "file": source.name,
                "start_line": 3,
                "end_line": 5,
            },
            unit["statement"],
        )
        self.assertEqual(
            {
                "file": source.name,
                "start_line": 6,
                "end_line": 8,
            },
            unit["proof"],
        )
        self.assertEqual(
            {(6, 8)}, proofcheck.proof_environment_spans(source)
        )
        self.assertEqual("associated", unit["proof_association"]["status"])
        self.assertEqual(
            "adjacent_environment", unit["proof_association"]["method"]
        )
        self.assertEqual("res:real", unit["proof_association"]["target"])
        self.assertEqual([], inventory["warnings"], inventory)

    def test_named_proof_accepts_terminal_marker_after_substantive_text(
        self,
    ) -> None:
        cases = {
            "qed-suffix": (
                "Thus the claim follows. \\qed\n",
                6,
                "\\qed",
                "qed_marker",
            ),
            "black-box-suffix": (
                "Thus the claim follows. \\hfill\\BlackBox\n",
                6,
                "\\BlackBox",
                "qed_marker",
            ),
            "display-qedhere-suffix": (
                "\\begin{align*}\n"
                "x_n\n"
                "&=0. \\qedhere\n"
                "\\end{align*}\n",
                8,
                "\\qedhere",
                "qed_here_marker",
            ),
            "display-qedhere-bracket-close": (
                "\\[\n"
                "x_n=0. \\qedhere\n"
                "\\]\n",
                7,
                "\\qedhere",
                "qed_here_marker",
            ),
            "display-qedhere-same-line-align-close": (
                "\\begin{align*}\n"
                "x_n&=0. \\qedhere\\end{align*}\n",
                7,
                "\\qedhere",
                "qed_here_marker",
            ),
            "dollar-square-suffix": (
                "Thus the claim follows. $\\square$\n",
                6,
                "\\square",
                "qed_marker",
            ),
            "dollar-blacksquare-suffix": (
                "Thus the claim follows. $\\blacksquare$\n",
                6,
                "\\blacksquare",
                "qed_marker",
            ),
        }
        for case, (
            body,
            marker_line,
            marker,
            boundary_kind,
        ) in cases.items():
            with self.subTest(case=case):
                source = self.base / f"named-{case}.tex"
                source.write_text(
                    "\\newtheorem{theorem}{Theorem}\n"
                    "\\begin{theorem}\\label{thm:manual}\n"
                    "The claim holds.\n"
                    "\\end{theorem}\n"
                    "\\subsection{Proof of Theorem \\ref{thm:manual}}\n"
                    f"{body}",
                    encoding="utf-8",
                    newline="\n",
                )

                region = proofcheck.analyze_proof_region(
                    source,
                    5,
                    target_unit_id="thm:manual",
                )

                self.assertEqual("accepted", region["status"], region)
                self.assertEqual("named_heading", region["method"], region)
                self.assertEqual(
                    boundary_kind,
                    region["boundary"]["kind"],
                )
                self.assertEqual(
                    region["end_line"],
                    region["boundary"]["line"],
                )
                self.assertEqual(
                    marker_line,
                    region["boundary"]["marker_line"],
                )
                self.assertIn(
                    marker,
                    proofcheck.read_lines(source)[marker_line - 1],
                )
                self.assertTrue(
                    proofcheck.proof_span_has_safe_boundary(
                        source,
                        5,
                        region["end_line"],
                        target_unit_id="thm:manual",
                    )
                )
                inventory = proofcheck.scan_formal_units(source)
                unit = next(
                    row
                    for row in inventory["units"]
                    if row["id"] == "thm:manual"
                )
                self.assertIsNotNone(unit["proof"], inventory)
                self.assertEqual(
                    "named_heading",
                    unit["proof_association"]["method"],
                )

    def test_suffix_terminal_markers_remain_strict_about_proof_tails(
        self,
    ) -> None:
        cases = {
            "substantive-tail": (
                "\\subsection{Proof of Theorem \\ref{thm:manual}}\n"
                "First argument. \\qed\n"
                "A second substantive derivation continues here.\n"
                "\\end{document}\n",
                "terminator_followed_by_substantive_or_ambiguous_tail",
            ),
            "competing-markers": (
                "\\subsection{Proof of Theorem \\ref{thm:manual}}\n"
                "First argument. \\qed\n"
                "Second argument. \\hfill\\BlackBox\n"
                "\\end{document}\n",
                "multiple_terminal_markers",
            ),
        }
        for case, (text, expected_reason) in cases.items():
            with self.subTest(case=case):
                source = self.base / f"named-{case}.tex"
                source.write_text(text, encoding="utf-8", newline="\n")

                region = proofcheck.analyze_proof_region(
                    source,
                    1,
                    target_unit_id="thm:manual",
                )

                self.assertEqual("ambiguous", region["status"], region)
                self.assertEqual(expected_reason, region["reason"], region)
                self.assertIsNone(
                    proofcheck.bounded_proof_region(
                        source,
                        1,
                        target_unit_id="thm:manual",
                    )
                )

    def test_manual_heading_with_nested_ref_and_terminal_marker_is_bounded(
        self,
    ) -> None:
        source = self.base / "manual-terminal-proof.tex"
        source.write_text(
            "\\newtheorem{theorem}{Theorem}\n"
            "\\begin{theorem}\\label{thm:manual}\n"
            "The claim holds.\n"
            "\\end{theorem}\n"
            "\\subsection{Proof of Theorem \\ref{thm:manual}}\n"
            "The proof checks the claim directly.\n"
            "\\hfill\\BlackBox\n"
            "% The remaining lines are document epilogue only.\n"
            "\\vskip 0.15in\n"
            "\\bibliography{refs}\n"
            "\\end{document}\n",
            encoding="utf-8",
            newline="\n",
        )

        region = proofcheck.bounded_proof_region(source, 5)

        self.assertIsNotNone(region)
        self.assertEqual(5, region["start_line"])
        self.assertEqual(7, region["end_line"])
        self.assertEqual(
            "Proof of Theorem \\ref{thm:manual}",
            region["header_span"]["text"],
        )
        self.assertEqual(
            {
                "kind": "qed_marker",
                "line": 7,
                "marker_line": 7,
                "evidence": "\\hfill\\BlackBox",
            },
            region["boundary"],
        )
        self.assertTrue(proofcheck.proof_span_has_safe_boundary(source, 5, 7))

        inventory = proofcheck.scan_formal_units(source)
        unit = next(row for row in inventory["units"] if row["id"] == "thm:manual")
        unit["proof"] = {
            "file": proofcheck.relative_or_absolute(source, self.base),
            "start_line": 5,
            "end_line": 7,
        }
        units = {"thm:manual": unit}
        cross_references = proofcheck.scan_cross_references(source)
        owners = proofcheck.reviewed_label_owners(
            cross_references, units, self.base
        )
        evidence = proofcheck.reviewed_span_evidence(
            "thm:manual", unit, self.base, owners
        )
        heading_occurrence = next(
            row
            for row in evidence["reference_occurrences"]
            if row["target"] == "thm:manual"
        )
        self.assertEqual("proof_header", heading_occurrence["structural_context"])

    def test_terminal_manual_proof_rejects_ambiguous_or_substantive_tail(
        self,
    ) -> None:
        cases = {
            "substantive_tail": (
                "\\subsection{Proof of Theorem \\ref{thm:manual}}\n"
                "First argument.\n"
                "\\hfill\\BlackBox\n"
                "A second substantive derivation continues here.\n"
                "\\end{document}\n",
                [3],
            ),
            "ambiguous_closures": (
                "\\subsection{Proof of Theorem \\ref{thm:manual}}\n"
                "First argument.\n"
                "\\hfill\\BlackBox\n"
                "Second argument.\n"
                "\\hfill\\BlackBox\n"
                "\\end{document}\n",
                [3, 5],
            ),
        }
        for name, (text, candidate_ends) in cases.items():
            with self.subTest(case=name):
                source = self.base / f"manual-{name}.tex"
                source.write_text(text, encoding="utf-8", newline="\n")
                for end_line in candidate_ends:
                    self.assertFalse(
                        proofcheck.proof_span_has_safe_boundary(
                            source, 1, end_line
                        )
                    )

    def test_schema5_accepts_a_long_indivisible_display(self) -> None:
        ledger_path = self.make_schema5_long_display_ledger()

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)

        self.assertEqual([], errors)

    def test_schema5_rejects_a_coarse_multi_transition_step(self) -> None:
        ledger_path = self.make_schema5_long_display_ledger()
        ledger = read_json(ledger_path)
        step = next(row for row in ledger["steps"] if row["id"] == "S003")
        step["inference"]["moves"].append(
            {
                "id": "M002",
                "claim": step["restatement"],
                "rule": "A second transition hidden in the same ledger step",
                "premise_ids": [],
                "prior_move_ids": ["M001"],
                "justification": (
                    "This deliberately records a second logical transition in S003."
                ),
            }
        )
        step["inference"]["conclusion_move"] = "M002"
        ledger["review"]["conclusion_results"][0]["support"]["move_id"] = "M002"
        self.seal_schema5_challenge(ledger_path, ledger)

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)

        self.assertTrue(
            any(
                "schema-5" in error.lower()
                and "exactly one" in error.lower()
                and "move" in error.lower()
                for error in errors
            ),
            errors,
        )

    def test_schema5_derivation_rejects_duplicate_exact_conclusion_premises(
        self,
    ) -> None:
        ledger_path = self.make_complete_audit()
        ledger = self.upgrade_ledger_to_schema5(ledger_path)
        prior = ledger["steps"][0]
        prior["kind"] = "setup"
        prior["restatement"] = "x equals x"
        step = next(row for row in ledger["steps"] if row["id"] == "S003")
        dependency = {
            "id": "S001",
            "kind": "step",
            "status": "verified",
            "needed_form": step["restatement"],
            "compatibility_check": "The imported claim exactly repeats the goal.",
        }
        step["dependencies"] = [dependency]
        for premise_id in ("P002", "P003"):
            step["premise_uses"].append(
                {
                    "id": premise_id,
                    "role": "fact",
                    "claim": step["restatement"],
                    "origin": {"kind": "prior_step", "reference": "S001"},
                    "evidence": (
                        "The prior row is cited verbatim as the conclusion under review."
                    ),
                }
            )
            step["inference"]["moves"][0]["premise_ids"].append(premise_id)
        self.seal_schema5_challenge(ledger_path, ledger)

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)

        self.assertTrue(
            any(
                "derivation" in error.lower()
                and "restatement" in error.lower()
                and ("premise" in error.lower() or "circular" in error.lower())
                for error in errors
            ),
            errors,
        )

    def test_schema5_evidence_specificity_is_conservative_and_bounded(self) -> None:
        ledger_path = self.make_schema5_parallel_steps_ledger()
        baseline = read_json(ledger_path)
        repeated = (
            "The exact same evidence sentence is reused without identifying "
            "the claim checked in this step."
        )

        cross_step = json.loads(json.dumps(baseline))
        for step_id in ("S003", "S004", "S005", "S006"):
            step = next(row for row in cross_step["steps"] if row["id"] == step_id)
            step["checks"]["literal"] = repeated
        self.seal_schema5_challenge(ledger_path, cross_step)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        repetition_errors = [
            error
            for error in errors
            if "evidence" in error.lower()
            and ("repeated" in error.lower() or "specificity" in error.lower())
        ]
        self.assertEqual(1, len(repetition_errors), errors)
        self.assertIn("4", repetition_errors[0])
        self.assertIn("S003", repetition_errors[0])

        cross_aspect = json.loads(json.dumps(baseline))
        step = next(row for row in cross_aspect["steps"] if row["id"] == "S003")
        for aspect in ("domain", "dimension", "sign"):
            row = next(
                item for item in step["risk_checks"] if item["aspect"] == aspect
            )
            row["status"] = "passed"
            row["evidence"] = repeated
        self.seal_schema5_challenge(ledger_path, cross_aspect)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        aspect_errors = [
            error
            for error in errors
            if "risk" in error.lower()
            and "evidence" in error.lower()
            and ("aspect" in error.lower() or "specificity" in error.lower())
        ]
        self.assertEqual(1, len(aspect_errors), errors)
        self.assertIn("3", aspect_errors[0])
        self.assertIn("S003", aspect_errors[0])

    def test_dependency_issue_origin_enters_propagation_and_recheck_closure(
        self,
    ) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        self.seal_schema5_challenge(
            ledger_path,
            read_json(ledger_path),
            covered_issue_ids=["I-001"],
        )
        _, summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        summaries_by_id = {
            summary["unit_id"]: summary for summary in summaries
        }
        registry = read_json(
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        issue = {
            "id": "I-001",
            "severity": "S1",
            "confidence": "high",
            "status": "resolved",
            "finding_status": "resolved",
            "scope": "unit",
            "load_bearing": True,
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "The dependency use required an explicit compatibility repair.",
            "origin_ref": {
                "kind": "dependency_use",
                "unit_id": "lem:main",
                "use_id": "D001",
            },
            "contract_refs": [
                {
                    "kind": "dependency_use",
                    "unit_id": "lem:main",
                    "use_id": "D001",
                },
                {
                    "kind": "conclusion",
                    "unit_id": "lem:main",
                    "conclusion_id": "C001",
                },
            ],
            "invalidation_kind": "dependency_mismatch",
            "suggested_changes": [],
            "rechecked_units": ["lem:main"],
            "rechecked_dependency_uses": ["D001"],
            "reconciled_deliverables": [],
        }

        projection = proofcheck.canonical_issue_detail_projection(
            issue,
            summaries_by_id,
            registry["internal_uses"],
            ["lem:main"],
            [],
            "defects_found",
        )

        self.assertTrue(
            any(row[2] == "D001" for row in projection["propagation"]),
            projection,
        )
        closure = projection["closure"][0]
        self.assertEqual("D001", closure[2])
        self.assertEqual("D001", closure[3])
        self.assertEqual("complete", closure[-1])

        issue["rechecked_dependency_uses"] = []
        projection = proofcheck.canonical_issue_detail_projection(
            issue,
            summaries_by_id,
            registry["internal_uses"],
            ["lem:main"],
            [],
            "defects_found",
        )
        self.assertEqual("open", projection["closure"][0][-1])

    def test_dependency_mismatch_requires_nonclean_backlinked_origin_use(
        self,
    ) -> None:
        ledger_path = self.make_complete_audit()
        self.install_internal_dependency(ledger_path)
        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=True,
            severity="S1",
            summary="The recorded dependency use is incompatible with the needed form.",
        )
        issue.update(
            {
                "origin_ref": {
                    "kind": "dependency_use",
                    "unit_id": "lem:main",
                    "use_id": "D001",
                },
                "contract_refs": [
                    {
                        "kind": "dependency_use",
                        "unit_id": "lem:main",
                        "use_id": "D001",
                    },
                    {
                        "kind": "conclusion",
                        "unit_id": "lem:main",
                        "conclusion_id": "C001",
                    },
                ],
                "invalidation_kind": "dependency_mismatch",
            }
        )
        issue["suggested_changes"][0]["action"] = "repair_dependency"
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
        registry = read_json(
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        dependency_edges = registry["internal_uses"]

        def validate(summaries: list[dict]) -> list[str]:
            errors, _ = proofcheck.validate_issues(
                [issue],
                set(),
                True,
                evidence_base=self.audit,
                source_snapshot_id=manifest["source_snapshot"]["sha256"],
                in_scope=["lem:main", "lem:prior"],
                ledger_summaries=summaries,
                dependency_edges=dependency_edges,
            )
            return errors

        _, clean_summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        clean_errors = validate(clean_summaries)
        self.assertTrue(
            any(
                "dependency_mismatch" in error
                and "origin_ref" in error
                and (
                    "nonclean" in error.lower()
                    or "backlink" in error.lower()
                    or "verified" in error.lower()
                )
                for error in clean_errors
            ),
            clean_errors,
        )

        ledger = read_json(ledger_path)
        step_dependency = ledger["steps"][2]["dependencies"][0]
        review_dependency = ledger["review"]["direct_dependencies"][0]
        for dependency in (step_dependency, review_dependency):
            dependency["status"] = "incorrect"
            dependency["issue_ids"] = ["I-001"]
        write_json(ledger_path, ledger)
        dependency_edges[0]["status"] = "incorrect"
        dependency_edges[0]["issue_ids"] = ["I-001"]
        nonclean_summaries = json.loads(json.dumps(clean_summaries))
        main_summary = next(
            summary
            for summary in nonclean_summaries
            if summary["unit_id"] == "lem:main"
        )
        main_summary["review_components"]["dependency_closure"] = "incorrect"

        self.assertEqual([], validate(nonclean_summaries))

        ledger = read_json(ledger_path)
        for dependency in (
            ledger["steps"][2]["dependencies"][0],
            ledger["review"]["direct_dependencies"][0],
        ):
            dependency["status"] = "unclear"
        write_json(ledger_path, ledger)
        dependency_edges[0]["status"] = "unclear"
        main_summary["review_components"]["dependency_closure"] = "unclear"

        definite_errors = validate(nonclean_summaries)
        self.assertTrue(
            any(
                "status 'unclear'" in error
                and "finding_status 'defect'" in error
                for error in definite_errors
            ),
            definite_errors,
        )
        issue["finding_status"] = "inconclusive"
        self.assertEqual([], validate(nonclean_summaries))

        ledger = read_json(ledger_path)
        for dependency in (
            ledger["steps"][2]["dependencies"][0],
            ledger["review"]["direct_dependencies"][0],
        ):
            dependency["status"] = "incorrect"
        write_json(ledger_path, ledger)
        dependency_edges[0]["status"] = "incorrect"
        main_summary["review_components"]["dependency_closure"] = "incorrect"
        inconclusive_errors = validate(nonclean_summaries)
        self.assertTrue(
            any(
                "status 'incorrect'" in error
                and "finding_status 'inconclusive'" in error
                for error in inconclusive_errors
            ),
            inconclusive_errors,
        )
        issue["finding_status"] = "defect"

        ledger = read_json(ledger_path)
        for dependency in (
            ledger["steps"][2]["dependencies"][0],
            ledger["review"]["direct_dependencies"][0],
        ):
            dependency["issue_ids"] = []
        write_json(ledger_path, ledger)
        dependency_edges[0]["issue_ids"] = []
        backlink_errors = validate(nonclean_summaries)
        self.assertTrue(
            any(
                "origin_ref dependency use" in error
                and (
                    "backlink" in error.lower()
                    or "link back" in error.lower()
                )
                for error in backlink_errors
            ),
            backlink_errors,
        )

    def install_declared_user_report_with_orientation(
        self,
        orientation: str,
    ) -> tuple[Path, Path]:
        self.make_complete_audit()
        self.upgrade_complete_audit_to_schema5()
        canonical_report = (
            self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        )
        user_report = self.audit / "audit" / "06_reports" / "USER_REPORT.md"
        canonical_text = canonical_report.read_text(encoding="utf-8")
        user_text = canonical_text.replace(
            "- Declared external deliverables: none",
            "- Declared external deliverables: R001",
            1,
        ).replace(
            "# Final Proof-Check Report",
            f"# Reader-Facing Proof Audit\n\n{orientation}",
            1,
        )
        user_report.write_text(
            user_text,
            encoding="utf-8",
            newline="\n",
        )
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["report_deliverables"] = [
            {
                "id": "R001",
                "role": "user_facing_report",
                "path": "audit/06_reports/USER_REPORT.md",
                "sha256": proofcheck.sha256_file(user_report),
                "issue_ids": [],
                "overall_verdict": "no_defect_found",
            }
        ]
        write_json(manifest_path, manifest)
        digest = manifest["report_deliverables"][0]["sha256"]
        canonical_report.write_text(
            canonical_text.replace(
                "- Declared external deliverables: none",
                "- Declared external deliverables: R001",
                1,
            ).replace(
                "## Computational evidence",
                (
                    "## Declared external deliverables\n\n"
                    "| Deliverable ID | Role | Path | SHA256 | Issue IDs | "
                    "Overall verdict |\n"
                    "|---|---|---|---|---|---|\n"
                    "| R001 | user_facing_report | "
                    "audit/06_reports/USER_REPORT.md | "
                    f"{digest} | none | no_defect_found |\n\n"
                    "## Computational evidence"
                ),
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        return canonical_report, user_report

    def test_declared_user_report_rejects_active_correctness_overclaim(
        self,
    ) -> None:
        self.install_declared_user_report_with_orientation(
            "The theorem and its proof are correct."
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "report_deliverables[1]" in error
                and "correctness overclaim" in error
                for error in errors
            ),
            errors,
        )

    def test_declared_user_report_requires_exact_metadata_and_core_sections(
        self,
    ) -> None:
        canonical_report, user_report = (
            self.install_declared_user_report_with_orientation(
                "This orientation paragraph is reader-facing only."
            )
        )
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        baseline_canonical = canonical_report.read_text(encoding="utf-8")
        baseline_user = user_report.read_text(encoding="utf-8")
        baseline_manifest = read_json(manifest_path)
        baseline_digest = baseline_manifest["report_deliverables"][0][
            "sha256"
        ]
        source_snapshot = baseline_manifest["source_snapshot"]["sha256"]
        cases = {
            "changed-skill-version": (
                baseline_user.replace(
                    "- Skill version: 1.0",
                    "- Skill version: 9.9",
                    1,
                ),
                "user-facing report field Skill version disagrees",
            ),
            "changed-source-snapshot": (
                baseline_user.replace(
                    f"- Source snapshot ID: {source_snapshot}",
                    f"- Source snapshot ID: {'0' * 64}",
                    1,
                ),
                "user-facing report field Source snapshot ID disagrees",
            ),
            "removed-top-metadata": (
                re.sub(
                    r"(?ms)^- Overall assessment code:.*?"
                    r"^- Final confidence:.*?\n+",
                    "",
                    baseline_user,
                    count=1,
                ),
                "rendered report needs exactly one canonical overall verdict",
            ),
            "missing-computational-evidence": (
                re.sub(
                    r"(?ms)^## Computational evidence\s*$.*?(?=^## |\Z)",
                    "",
                    baseline_user,
                    count=1,
                ),
                "user-facing Computational evidence section is missing",
            ),
        }
        for case, (mutated_user, expected) in cases.items():
            with self.subTest(case=case):
                user_report.write_text(
                    mutated_user,
                    encoding="utf-8",
                    newline="\n",
                )
                changed_manifest = json.loads(json.dumps(baseline_manifest))
                changed_digest = proofcheck.sha256_file(user_report)
                changed_manifest["report_deliverables"][0]["sha256"] = (
                    changed_digest
                )
                write_json(manifest_path, changed_manifest)
                canonical_report.write_text(
                    baseline_canonical.replace(
                        baseline_digest,
                        changed_digest,
                        1,
                    ),
                    encoding="utf-8",
                    newline="\n",
                )

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                self.assertTrue(
                    any(
                        "report_deliverables[1]" in error
                        and expected in error
                        for error in errors
                    ),
                    errors,
                )
        user_report.write_text(
            baseline_user,
            encoding="utf-8",
            newline="\n",
        )
        write_json(manifest_path, baseline_manifest)
        canonical_report.write_text(
            baseline_canonical,
            encoding="utf-8",
            newline="\n",
        )

    def test_declared_user_report_rejects_issue_and_verdict_drift(self) -> None:
        self.make_complete_audit()
        self.upgrade_complete_audit_to_schema5()
        canonical_report = (
            self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        )
        user_report = self.audit / "audit" / "06_reports" / "USER_REPORT.md"
        user_report.write_text(
            canonical_report.read_text(encoding="utf-8").replace(
                "- Declared external deliverables: none",
                "- Declared external deliverables: R001",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["report_deliverables"] = [
            {
                "id": "R001",
                "role": "user_facing_report",
                "path": "audit/06_reports/USER_REPORT.md",
                "sha256": proofcheck.sha256_file(user_report),
                "issue_ids": [],
                "overall_verdict": "no_defect_found",
            }
        ]
        write_json(manifest_path, manifest)
        deliverable_hash = manifest["report_deliverables"][0]["sha256"]
        canonical_with_deliverable = canonical_report.read_text(
            encoding="utf-8"
        ).replace(
            "- Declared external deliverables: none",
            "- Declared external deliverables: R001",
            1,
        ).replace(
            "## Computational evidence",
            (
                "## Declared external deliverables\n\n"
                "| Deliverable ID | Role | Path | SHA256 | Issue IDs | Overall verdict |\n"
                "|---|---|---|---|---|---|\n"
                "| R001 | user_facing_report | "
                "audit/06_reports/USER_REPORT.md | "
                f"{deliverable_hash} | none | no_defect_found |\n\n"
                "## Computational evidence"
            ),
            1,
        )
        canonical_report.write_text(
            canonical_with_deliverable,
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertFalse(
            any("report_deliverables" in error for error in errors), errors
        )

        cases = {
            "issue_ids": ("issue_ids", ["I-999"]),
            "overall_verdict": ("overall_verdict", "defects_found"),
        }
        for name, (field, value) in cases.items():
            with self.subTest(case=name):
                changed = json.loads(json.dumps(manifest))
                changed["report_deliverables"][0][field] = value
                write_json(manifest_path, changed)

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                self.assertTrue(
                    any(
                        "report_deliverables[1]" in error
                        and field in error
                        and (
                            "canonical" in error.lower()
                            or "disagree" in error.lower()
                        )
                        for error in errors
                    ),
                    errors,
                )

    def test_declared_user_report_requires_canonical_semantic_sections(
        self,
    ) -> None:
        self.make_complete_audit()
        self.upgrade_complete_audit_to_schema5()
        canonical_report = (
            self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        )
        user_report = self.audit / "audit" / "06_reports" / "USER_REPORT.md"
        canonical_text = canonical_report.read_text(encoding="utf-8").replace(
            "- Declared external deliverables: none",
            "- Declared external deliverables: R001",
            1,
        )
        user_text = canonical_text.replace(
            "# Final Proof-Check Report",
            (
                "# Reader-Facing Proof Audit\n\n"
                "This extra orientation paragraph is permitted user-facing prose."
            ),
            1,
        )
        user_report.write_text(
            user_text,
            encoding="utf-8",
            newline="\n",
        )
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["report_deliverables"] = [
            {
                "id": "R001",
                "role": "user_facing_report",
                "path": "audit/06_reports/USER_REPORT.md",
                "sha256": proofcheck.sha256_file(user_report),
                "issue_ids": [],
                "overall_verdict": "no_defect_found",
            }
        ]
        write_json(manifest_path, manifest)
        deliverable_hash = manifest["report_deliverables"][0]["sha256"]
        canonical_with_deliverable = canonical_report.read_text(
            encoding="utf-8"
        ).replace(
            "- Declared external deliverables: none",
            "- Declared external deliverables: R001",
            1,
        ).replace(
            "## Computational evidence",
            (
                "## Declared external deliverables\n\n"
                "| Deliverable ID | Role | Path | SHA256 | Issue IDs | Overall verdict |\n"
                "|---|---|---|---|---|---|\n"
                "| R001 | user_facing_report | "
                "audit/06_reports/USER_REPORT.md | "
                f"{deliverable_hash} | none | no_defect_found |\n\n"
                "## Computational evidence"
            ),
            1,
        )
        canonical_report.write_text(
            canonical_with_deliverable,
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertFalse(
            any("report_deliverables[1]" in error for error in errors),
            errors,
        )

        drifted = user_text.replace(
            "Exact source ledger and direct reconstruction.",
            "A generic summary without the canonical evidence.",
            1,
        )
        user_report.write_text(
            drifted,
            encoding="utf-8",
            newline="\n",
        )
        manifest = read_json(manifest_path)
        manifest["report_deliverables"][0]["sha256"] = (
            proofcheck.sha256_file(user_report)
        )
        write_json(manifest_path, manifest)
        canonical_report.write_text(
            canonical_report.read_text(encoding="utf-8").replace(
                deliverable_hash,
                manifest["report_deliverables"][0]["sha256"],
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "report_deliverables[1]" in error
                and "Main theorem chain" in error
                and (
                    "canonical" in error.lower()
                    or "disagree" in error.lower()
                )
                for error in errors
            ),
            errors,
        )

    def prepare_effective_critical_audit(self) -> tuple[Path, Path]:
        main_path = self.make_complete_audit()
        prior_path, _ = self.install_internal_dependency(main_path)

        main = read_json(main_path)
        main_step = next(row for row in main["steps"] if row["id"] == "S003")
        main_step["dependencies"] = []
        main_step["premise_uses"] = [main_step["premise_uses"][0]]
        main_step["inference"]["moves"][0]["premise_ids"] = ["P001"]
        main["review"]["direct_dependencies"] = []
        main["review"]["conclusion_results"][0]["dependency_use_ids"] = []
        main["independent_check"] = {
            "required": False,
            "status": "not_required",
            "independence_level": "none",
            "challenger_verdict": "not_checked",
            "reconciled_verdict": "not_checked",
            "artifact": "",
            "disagreements": [],
            "resolution": "",
        }
        write_json(main_path, main)

        prior = read_json(prior_path)
        prior["independent_check"]["artifact"] = (
            "audit/05_adversarial/lem-prior-challenge.md"
        )
        write_json(prior_path, prior)
        prior_artifact = self.audit / prior["independent_check"]["artifact"]
        prior_artifact.write_text(
            "# Fresh-context challenge for lem:prior\n\nVerdict: verified.\n",
            encoding="utf-8",
            newline="\n",
        )

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["depth"] = "full"
        manifest["audit_scope"]["critical_units"] = ["lem:prior"]
        write_json(manifest_path, manifest)

        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["internal_uses"] = []
        write_json(registry_path, registry)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report = report.replace(
            "| lem:main | C001 | verified | valid | established | verified | "
            "not_applicable | S003/M001 | D001 | none |",
            "| lem:main | C001 | verified | valid | established | verified | "
            "not_applicable | S003/M001 | none | none |",
        )
        report = report.replace(
            "| lem:main | D001 | lem:prior | C001 | internal_result | verified | "
            "passed | verified | none |",
            "None.",
        )
        report = report.replace(
            "| lem:main | agreed | fresh_context_same_model | verified | verified | "
            "none | none | audit/05_adversarial/lem-main-challenge.md |",
            "| lem:prior | agreed | fresh_context_same_model | verified | verified | "
            "none | none | audit/05_adversarial/lem-prior-challenge.md |",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        self.upgrade_complete_audit_to_schema5()
        return main_path, prior_path

    def make_schema5_issue(
        self,
        *,
        severity: str,
        status: str,
        issue_id: str = "I-001",
    ) -> dict:
        issue = {
            "id": issue_id,
            "severity": severity,
            "confidence": "high",
            "status": status,
            "finding_status": "resolved" if status == "resolved" else "inconclusive",
            "scope": "unit",
            "load_bearing": True,
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "A load-bearing proof premise requires explicit resolution.",
            "origin_ref": {
                "kind": "ledger_move",
                "unit_id": "lem:main",
                "step_id": "S003",
                "move_id": "M001",
            },
            "contract_refs": [
                {
                    "kind": "conclusion",
                    "unit_id": "lem:main",
                    "conclusion_id": "C001",
                }
            ],
            "invalidation_kind": "scope_inconclusive",
            "suggested_changes": [
                {
                    "target_ref": {
                        "kind": "source_span",
                        "file": proofcheck.relative_or_absolute(
                            self.paper, self.audit
                        ),
                        "start_line": 6,
                        "end_line": 6,
                        "sha256": proofcheck.source_span_sha256(self.paper, 6, 6),
                    },
                    "action": "repair_step",
                    "proposal": "Supply the missing premise and recheck the conclusion.",
                    "verification_status": "candidate",
                    "required_rechecks": ["lem:main"],
                }
            ],
        }
        if status == "resolved":
            manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
            issue.update(
                {
                    "resolution": "The missing premise was supplied and rechecked.",
                    "source_revision": "The current locked source contains the repair.",
                    "recheck_evidence": [
                        "The repaired move and conclusion were checked again."
                    ],
                    "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
                    "rechecked_units": ["lem:main"],
                }
            )
        return issue

    def install_schema5_issue(self, ledger_path: Path, issue: dict) -> None:
        ledger = read_json(ledger_path)
        step = next(
            step for step in ledger["steps"] if step["id"] == "S003"
        )
        step["issue_ids"] = sorted(set([*step["issue_ids"], issue["id"]]))
        result = ledger["review"]["conclusion_results"][0]
        result["issue_ids"] = sorted(
            set([*result["issue_ids"], issue["id"]])
        )
        unresolved_load_bearing = (
            issue["status"] in {"open", "deferred"}
            and issue["load_bearing"] is True
        )
        if unresolved_load_bearing:
            self.mark_s003_conditional(ledger)
            step["side_conditions"] = [
                {
                    "id": "SC001",
                    "generated_by": "M001",
                    "condition": (
                        "Resolve the load-bearing finding before treating the "
                        "conclusion as unconditional."
                    ),
                    "status": "open",
                }
            ]
            step["conditions"] = [
                {
                    "kind": "side_condition",
                    "reference": "SC001",
                    "condition": (
                        "The conclusion is conditional on resolving the linked "
                        "load-bearing finding."
                    ),
                }
            ]
        write_json(ledger_path, ledger)

        progress_path = self.audit / "PROGRESS.json"
        progress = read_json(progress_path)
        progress["conditional_units"] = (
            ["lem:main"] if unresolved_load_bearing else []
        )
        progress["open_high_priority_issues"] = (
            [issue["id"]]
            if unresolved_load_bearing and issue["severity"] in {"S0", "S1"}
            else []
        )
        write_json(progress_path, progress)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        if unresolved_load_bearing:
            report = report.replace(
                "| lem:main | verified | verified | valid | established | verified |",
                "| lem:main | conditionally_verified | verified | conditional | "
                "conditional | verified |",
            )
            report = report.replace(
                "| lem:main | C001 | verified | valid | established | verified |",
                "| lem:main | C001 | verified | conditional | conditional | verified |",
            )
        report = report.replace(
            "| lem:main | C001 | verified | "
            + ("conditional | conditional" if unresolved_load_bearing else "valid | established")
            + " | verified | not_applicable | S003/M001 | none | none |",
            "| lem:main | C001 | verified | "
            + ("conditional | conditional" if unresolved_load_bearing else "valid | established")
            + f" | verified | not_applicable | S003/M001 | none | {issue['id']} |",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")

        self.install_canonical_issue(issue, migrate=False)
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        issue_log = read_json(issue_path)
        issue_log["schema_version"] = 5
        write_json(issue_path, issue_log)

    def make_archivable_s1_audit(self) -> tuple[Path, dict]:
        ledger_path = self.make_complete_audit()
        self.set_expected_assessment("inconclusive")
        issue = self.make_schema5_issue(severity="S1", status="open")
        self.install_schema5_issue(ledger_path, issue)

        ledger = read_json(ledger_path)
        ledger["independent_check"].update(
            {
                "status": "agreed",
                "challenger_verdict": "conditionally_verified",
                "reconciled_verdict": "conditionally_verified",
                "disagreements": [],
                "resolution": "",
            }
        )
        self.seal_schema5_challenge(
            ledger_path,
            ledger,
            covered_issue_ids=["I-001"],
            artifact_text=(
                "# Historical challenge\n\n"
                "The fresh challenge confirms that I-001 leaves lem:main "
                "conditional pending repair.\n"
            ),
        )
        self.install_canonical_issue(issue, migrate=False)

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_finalize(
                argparse.Namespace(root=self.audit)
            )
        self.assertEqual(0, status)
        return ledger_path, issue

    def finalize_and_archive_current_issue(
        self,
        issue_id: str = "I-001",
    ) -> tuple[Path, dict]:
        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(
                0,
                proofcheck.cmd_finalize(argparse.Namespace(root=self.audit)),
            )
            self.assertEqual(
                0,
                proofcheck.cmd_archive_issue(
                    argparse.Namespace(root=self.audit, issue_id=issue_id)
                ),
            )
        archive_path = (
            self.audit
            / "audit"
            / "06_reports"
            / "history"
            / f"{issue_id}-origin.json"
        )
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        archived_issue = next(
            row
            for row in read_json(issue_path)["issues"]
            if row["id"] == issue_id
        )
        return archive_path, archived_issue

    def make_archivable_interface_origin_audit(
        self,
    ) -> tuple[Path, dict, dict]:
        self.make_complete_audit()
        record = self.make_interface_record(
            specification="ambiguous",
            target_verdict="not_assessable",
            code_to_documented="not_assessable",
        )
        issue = self.make_global_issue(
            finding_status="inconclusive",
            load_bearing=False,
            severity="S3",
            summary=(
                "The method interface has two unresolved population readings."
            ),
        )
        issue.update(
            {
                "interface_id": record["id"],
                "finding_class": "exposition_ambiguity",
                "affected_layer": "specification",
                "evidence_class": "observed",
                "estimator_target_status": "not_assessable",
                "implementation_inspection_status": "inspected",
                "code_to_documented_estimator": "not_assessable",
                "code_to_required_target": "consistent",
                "execution_provenance_status": "not_checked",
                "resolution_evidence_needed": [
                    "State the numerator and denominator laws explicitly."
                ],
                "origin_ref": {
                    "kind": "interface_record",
                    "interface_id": record["id"],
                    "evidence_spans": [
                        dict(
                            record["fitting_sample_laws"][0][
                                "evidence_spans"
                            ][0]
                        )
                    ],
                },
                "invalidation_kind": "scope_inconclusive",
            }
        )
        self.install_interface_issue(record, issue)
        archive_path, archived_issue = self.finalize_and_archive_current_issue()
        return archive_path, archived_issue, record

    def make_archivable_global_origin_audit(
        self,
    ) -> tuple[Path, dict, dict]:
        self.make_complete_audit()
        aspect = "constants_and_rates"
        check = {
            "aspect": aspect,
            "status": "defect",
            "evidence": (
                "The historical global check records a distinctive rate "
                "mismatch before repair."
            ),
            "affected_units": ["lem:main"],
            "issue_ids": ["I-001"],
        }
        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=False,
            severity="S2",
            summary="The global rate check records a repairable mismatch.",
        )
        issue["origin_ref"] = {
            "kind": "global_check",
            "aspect": aspect,
            "evidence_spans": [
                proofcheck.locked_span(
                    self.paper,
                    2,
                    4,
                    self.audit,
                    role="global_consistency_evidence",
                )
            ],
        }
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        global_pass = manifest["completion"]["global_consistency_pass"]
        canonical_check = next(
            row for row in global_pass["checks"] if row["aspect"] == aspect
        )
        canonical_check.update(check)
        global_pass["status"] = "completed_with_findings"
        write_json(manifest_path, manifest)
        self.set_expected_assessment("defects_found")
        self.install_canonical_issue(issue, migrate=False)
        archive_path, archived_issue = self.finalize_and_archive_current_issue()
        return archive_path, archived_issue, check

    def rebind_tampered_archived_failure_and_report(
        self,
        archive: dict,
        replacement_evidence: str,
    ) -> None:
        old_row = list(archive["projection"]["failure"][0])
        new_row = list(old_row)
        new_row[8] = replacement_evidence
        render_row = lambda row: "| " + " | ".join(
            proofcheck.escape_markdown(str(value)) for value in row
        ) + " |"

        report_record = archive["prior_artifacts"]["final_report"]
        report_text = base64.b64decode(
            report_record["content_base64"]
        ).decode("utf-8")
        old_report_row = render_row(old_row)
        new_report_row = render_row(new_row)
        self.assertEqual(1, report_text.count(old_report_row))
        report_text = report_text.replace(
            old_report_row,
            new_report_row,
            1,
        )
        report_record["content_base64"] = base64.b64encode(
            report_text.encode("utf-8")
        ).decode("ascii")
        report_record["sha256"] = proofcheck.sha256_text(report_text)

        prior_record = archive["prior_finalization_record"]
        final_report_row = next(
            row
            for row in prior_record["artifact_manifest"]
            if row["file"] == "audit/06_reports/FINAL_REPORT.md"
        )
        final_report_row["sha256"] = report_record["sha256"]
        prior_record["audit_state_sha256"] = proofcheck.canonical_sha256(
            prior_record["artifact_manifest"]
        )
        prior_record["record_payload_sha256"] = (
            proofcheck.finalization_payload_sha256(prior_record)
        )
        archive["prior_finalization_record_sha256"] = (
            proofcheck.canonical_sha256(prior_record)
        )
        archive["projection"]["failure"] = [new_row]
        archive["projection_sha256"] = proofcheck.canonical_sha256(
            archive["projection"]
        )
        archive["archive_payload_sha256"] = (
            proofcheck.resolution_archive_payload_sha256(archive)
        )

    def make_resolved_s1_lifecycle_audit(
        self,
    ) -> tuple[Path, Path, dict]:
        main_path = self.make_complete_audit()
        self.install_internal_dependency(main_path)
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        inventory_path = (
            self.audit
            / "audit"
            / "01_index"
            / "theorem_inventory.json"
        )
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        summary_path = (
            self.audit / "audit" / "06_reports" / "ISSUE_SUMMARY.md"
        )
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        progress_path = self.audit / "PROGRESS.json"
        baseline = {
            "main": read_json(main_path),
            "manifest": read_json(manifest_path),
            "registry": read_json(registry_path),
            "issues": read_json(issue_path),
            "summary": summary_path.read_text(encoding="utf-8"),
            "report": report_path.read_text(encoding="utf-8"),
            "progress": read_json(progress_path),
        }

        self.set_expected_assessment("inconclusive")
        historical_issue = self.make_schema5_issue(
            severity="S1",
            status="open",
        )
        self.install_schema5_issue(main_path, historical_issue)
        historical_report = report_path.read_text(encoding="utf-8")
        historical_report = historical_report.replace(
            "| lem:main | C001 | verified | conditional | conditional | "
            "verified | not_applicable | S003/M001 | D001 | none |",
            "| lem:main | C001 | verified | conditional | conditional | "
            "verified | not_applicable | S003/M001 | D001 | I-001 |",
        )
        report_path.write_text(
            historical_report,
            encoding="utf-8",
            newline="\n",
        )
        historical_ledger = read_json(main_path)
        historical_ledger["independent_check"].update(
            {
                "status": "agreed",
                "challenger_verdict": "conditionally_verified",
                "reconciled_verdict": "conditionally_verified",
                "disagreements": [],
                "resolution": "",
            }
        )
        self.seal_schema5_challenge(
            main_path,
            historical_ledger,
            covered_issue_ids=["I-001"],
            artifact_text=(
                "# Historical challenge\n\n"
                "The fresh challenge confirms that I-001 leaves lem:main "
                "conditional pending repair.\n"
            ),
        )
        self.install_canonical_issue(historical_issue, migrate=False)

        historical_errors, _ = proofcheck.check_audit_finalization(
            self.audit
        )
        self.assertEqual([], historical_errors)
        with contextlib.redirect_stdout(io.StringIO()):
            prior_status = proofcheck.cmd_finalize(
                argparse.Namespace(root=self.audit)
            )
        self.assertEqual(0, prior_status)
        prior_record = read_json(
            self.audit / "audit" / "06_reports" / "FINALIZATION.json"
        )

        historical_manifest = read_json(manifest_path)
        source_snapshot_sha256 = historical_manifest[
            "source_snapshot"
        ]["sha256"]
        with contextlib.redirect_stdout(io.StringIO()):
            archive_status = proofcheck.cmd_archive_issue(
                argparse.Namespace(
                    root=self.audit,
                    issue_id="I-001",
                )
            )
        self.assertEqual(0, archive_status)
        archive_path = (
            self.audit
            / "audit"
            / "06_reports"
            / "history"
            / "I-001-origin.json"
        )
        archive = read_json(archive_path)
        self.assertEqual(
            prior_record,
            archive["prior_finalization_record"],
        )
        self.assertEqual(
            {
                "manifest",
                "issue_log",
                "final_report",
                "inventory",
                "dependency_registry",
                "method_interface_registry",
                "ledgers",
            },
            set(archive["prior_artifacts"]),
        )
        self.assertTrue(archive["prior_sources"])
        self.assertEqual(
            "audit/06_reports/FINAL_REPORT.md",
            archive["prior_artifacts"]["final_report"]["file"],
        )
        self.assertEqual(
            {
                row["file"]
                for row in historical_manifest["source_snapshot"]["files"]
            },
            {row["file"] for row in archive["prior_sources"]},
        )
        sealed_records = [
            archive["prior_artifacts"]["manifest"],
            archive["prior_artifacts"]["issue_log"],
            archive["prior_artifacts"]["final_report"],
            archive["prior_artifacts"]["inventory"],
            archive["prior_artifacts"]["dependency_registry"],
            archive["prior_artifacts"]["method_interface_registry"],
            *archive["prior_artifacts"]["ledgers"],
            *archive["prior_sources"],
        ]
        for record in sealed_records:
            self.assertEqual(
                {"file", "sha256", "content_base64"},
                set(record),
            )
        archived_issue_log = read_json(issue_path)
        archived_issue = next(
            row
            for row in archived_issue_log["issues"]
            if row["id"] == "I-001"
        )
        historical_origin = archived_issue["historical_origin"]

        write_json(main_path, baseline["main"])
        write_json(manifest_path, baseline["manifest"])
        write_json(registry_path, baseline["registry"])
        write_json(issue_path, baseline["issues"])
        summary_path.write_text(
            baseline["summary"],
            encoding="utf-8",
            newline="\n",
        )
        report_path.write_text(
            baseline["report"],
            encoding="utf-8",
            newline="\n",
        )
        write_json(progress_path, baseline["progress"])

        current_ledger = read_json(main_path)
        current_ledger["independent_check"].update(
            {
                "required": True,
                "status": "agreed",
                "independence_level": "fresh_context_same_model",
                "challenger_verdict": "verified",
                "reconciled_verdict": "verified",
                "artifact": (
                    "audit/05_adversarial/"
                    "lem-main-post-repair-challenge.md"
                ),
                "disagreements": [],
                "resolution": "",
            }
        )
        write_json(main_path, current_ledger)
        self.seal_schema5_challenge(
            main_path,
            read_json(main_path),
            covered_issue_ids=["I-001"],
            artifact_text=(
                "# Post-repair challenge\n\n"
                "A fresh context rechecked the clean S003/M001 move, the "
                "D001 dependency use, and resolved issue I-001.\n"
            ),
        )

        resolved_issue = json.loads(json.dumps(historical_issue))
        resolved_issue.update(
            {
                "status": "resolved",
                "finding_status": "resolved",
                "resolution": (
                    "The proof move was repaired, D001 was rechecked, and the "
                    "affected result was independently verified."
                ),
                "source_revision": (
                    "The current schema-five ledger records the repaired "
                    "proof move and dependency closure."
                ),
                "recheck_evidence": [
                    "The current ledger and fresh challenge both verify lem:main."
                ],
                "source_snapshot_sha256": source_snapshot_sha256,
                "rechecked_units": ["lem:main"],
                "rechecked_dependency_uses": ["D001"],
                "reconciled_deliverables": [],
                "historical_origin": historical_origin,
                "current_resolution": {
                    "disposition": "repaired",
                    "current_ref": dict(historical_issue["origin_ref"]),
                    "mapping": (
                        "The archived failed move maps to the same S003/M001 "
                        "reference, which is clean in the current ledger."
                    ),
                    "verification_status": "verified_sufficient",
                    "evidence_spans": [
                        proofcheck.locked_span(
                            self.paper,
                            6,
                            6,
                            self.audit,
                            role="repair_verification",
                        )
                    ],
                    "required_rechecks": ["lem:main"],
                    "retired_dependency_uses": [],
                },
            }
        )
        self.install_canonical_issue(resolved_issue, migrate=False)
        return main_path, archive_path, resolved_issue

    def convert_resolved_lifecycle_to_removed_move(
        self,
        main_path: Path,
        issue: dict,
    ) -> dict:
        ledger = read_json(main_path)
        step = next(row for row in ledger["steps"] if row["id"] == "S003")
        move = next(
            row
            for row in step["inference"]["moves"]
            if row["id"] == "M001"
        )
        move["id"] = "M002"
        step["inference"]["conclusion_move"] = "M002"
        ledger["review"]["conclusion_results"][0]["support"]["move_id"] = (
            "M002"
        )
        write_json(main_path, ledger)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report_path.write_text(
            report_path.read_text(encoding="utf-8").replace(
                "| lem:main | C001 | verified | valid | established | "
                "verified | not_applicable | S003/M001 | D001 | none |",
                "| lem:main | C001 | verified | valid | established | "
                "verified | not_applicable | S003/M002 | D001 | none |",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.seal_schema5_challenge(
            main_path,
            read_json(main_path),
            covered_issue_ids=["I-001"],
            artifact_text=(
                "# Post-removal challenge\n\n"
                "A fresh context verified the retained lem:main ledger after "
                "the archived M001 move was removed and the clean M002 move "
                "was reconstructed.\n"
            ),
        )
        issue["resolution"] = (
            "The archived failed M001 move was removed while lem:main was "
            "retained and rechecked through clean move M002."
        )
        issue["source_revision"] = (
            "The retained current ledger no longer contains archived move "
            "S003/M001."
        )
        issue["recheck_evidence"] = [
            "The current ledger and fresh challenge verify retained lem:main."
        ]
        issue["current_resolution"].update(
            {
                "disposition": "removed",
                "current_ref": None,
                "mapping": (
                    "Archived move S003/M001 was deleted inside retained "
                    "lem:main; current move S003/M002 now establishes the "
                    "same conclusion."
                ),
            }
        )
        self.install_canonical_issue(issue, migrate=False)
        return issue

    def test_cmd_archive_issue_generated_s1_lifecycle_finalizes(self) -> None:
        _, _, issue = self.make_resolved_s1_lifecycle_audit()

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertEqual([], errors)
        self.assertEqual(
            "verified_sufficient",
            issue["current_resolution"]["verification_status"],
        )
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_finalize(
                argparse.Namespace(root=self.audit)
            )
        self.assertEqual(0, status)
        self.assertEqual(
            "passed",
            read_json(
                self.audit
                / "audit"
                / "06_reports"
                / "FINALIZATION.json"
            )["status"],
        )

    def test_archive_issue_seals_prior_method_interface_registry(self) -> None:
        archive_path, _, record = self.make_archivable_interface_origin_audit()
        archive = read_json(archive_path)
        sealed = archive["prior_artifacts"]["method_interface_registry"]
        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "METHOD_INTERFACE_REGISTRY.json"
        )
        sealed_bytes = base64.b64decode(sealed["content_base64"])
        sealed_registry = json.loads(sealed_bytes.decode("utf-8"))
        artifact_row = next(
            row
            for row in archive["prior_finalization_record"][
                "artifact_manifest"
            ]
            if row["file"] == sealed["file"]
        )

        self.assertEqual(
            "audit/03_dependencies/METHOD_INTERFACE_REGISTRY.json",
            sealed["file"],
        )
        self.assertEqual(proofcheck.sha256_file(registry_path), sealed["sha256"])
        self.assertEqual(registry_path.read_bytes(), sealed_bytes)
        self.assertEqual(sealed["sha256"], artifact_row["sha256"])
        self.assertEqual([record], sealed_registry["interfaces"])

    def test_resolved_interface_archive_recomputes_sealed_origin_failure(
        self,
    ) -> None:
        archive_path, archived_issue, _ = (
            self.make_archivable_interface_origin_audit()
        )
        baseline_errors: list[str] = []
        proofcheck.load_resolution_archive(
            archived_issue,
            self.audit,
            baseline_errors,
        )
        self.assertEqual([], baseline_errors)

        archive = read_json(archive_path)
        self.rebind_tampered_archived_failure_and_report(
            archive,
            json.dumps(
                {
                    "target_relation": {"verdict": "match"},
                    "implementation_relation": {"inspection_status": "inspected"},
                    "issue_ids": ["I-001"],
                },
                ensure_ascii=False,
            ),
        )
        write_json(archive_path, archive)
        resolved_issue = json.loads(json.dumps(archived_issue))
        resolved_issue["status"] = "resolved"
        resolved_issue["finding_status"] = "resolved"
        resolved_issue["historical_origin"]["sha256"] = (
            proofcheck.sha256_file(archive_path)
        )

        errors: list[str] = []
        proofcheck.load_resolution_archive(
            resolved_issue,
            self.audit,
            errors,
        )

        self.assertTrue(
            any("sealed canonical origin record" in error for error in errors),
            errors,
        )
        self.assertFalse(
            any("exact prior finalized report row" in error for error in errors),
            errors,
        )

    def test_global_archive_recomputes_failure_from_sealed_prior_manifest(
        self,
    ) -> None:
        archive_path, archived_issue, _ = self.make_archivable_global_origin_audit()
        baseline_errors: list[str] = []
        proofcheck.load_resolution_archive(
            archived_issue,
            self.audit,
            baseline_errors,
        )
        self.assertEqual([], baseline_errors)

        archive = read_json(archive_path)
        self.rebind_tampered_archived_failure_and_report(
            archive,
            json.dumps(
                {
                    "affected_units": ["lem:main"],
                    "aspect": "constants_and_rates",
                    "evidence": "A fabricated clean global-check result.",
                    "issue_ids": ["I-001"],
                    "status": "passed",
                },
                ensure_ascii=False,
            ),
        )
        write_json(archive_path, archive)
        resolved_issue = json.loads(json.dumps(archived_issue))
        resolved_issue["status"] = "resolved"
        resolved_issue["finding_status"] = "resolved"
        resolved_issue["historical_origin"]["sha256"] = (
            proofcheck.sha256_file(archive_path)
        )

        errors: list[str] = []
        proofcheck.load_resolution_archive(
            resolved_issue,
            self.audit,
            errors,
        )

        self.assertTrue(
            any("sealed canonical origin record" in error for error in errors),
            errors,
        )
        self.assertFalse(
            any("exact prior finalized report row" in error for error in errors),
            errors,
        )

    def test_archive_issue_retries_over_confined_temp_before_target_creation(
        self,
    ) -> None:
        self.make_archivable_s1_audit()
        archive_path = (
            self.audit
            / "audit"
            / "06_reports"
            / "history"
            / "I-001-origin.json"
        )
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        transaction_temp = proofcheck.proofcheck_temp_path(archive_path)
        transaction_lock = archive_path.with_name(
            f".{archive_path.name}.proofcheck.lock"
        )
        transaction_temp.write_text(
            "interrupted archive payload",
            encoding="utf-8",
            newline="\n",
        )

        freshness = proofcheck.check_finalization_freshness(self.audit)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = proofcheck.cmd_archive_issue(
                argparse.Namespace(root=self.audit, issue_id="I-001")
            )

        self.assertTrue(freshness["usable_finalization"], freshness)
        self.assertEqual(0, status)
        self.assertTrue(archive_path.is_file())
        self.assertFalse(transaction_temp.exists())
        self.assertFalse(transaction_lock.exists())
        self.assertNotIn(
            "recovered_existing_archive",
            json.loads(output.getvalue()),
        )

    def test_archive_issue_recovers_after_interrupted_issue_log_commit(
        self,
    ) -> None:
        self.make_archivable_s1_audit()
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        archive_path = (
            self.audit
            / "audit"
            / "06_reports"
            / "history"
            / "I-001-origin.json"
        )
        original_atomic_replace = proofcheck.atomic_replace_text

        def interrupt_issue_log_commit(path: Path, text: str) -> None:
            if path.resolve() == issue_path.resolve():
                raise OSError("simulated issue-log commit interruption")
            original_atomic_replace(path, text)

        with mock.patch.object(
            proofcheck,
            "atomic_replace_text",
            side_effect=interrupt_issue_log_commit,
        ):
            with self.assertRaisesRegex(
                OSError, "simulated issue-log commit interruption"
            ):
                proofcheck.cmd_archive_issue(
                    argparse.Namespace(root=self.audit, issue_id="I-001")
                )

        self.assertTrue(archive_path.is_file())
        transaction_lock = archive_path.with_name(
            f".{archive_path.name}.proofcheck.lock"
        )
        self.assertFalse(transaction_lock.exists())
        issue_before_recovery = next(
            row
            for row in read_json(issue_path)["issues"]
            if row["id"] == "I-001"
        )
        self.assertNotIn("historical_origin", issue_before_recovery)
        archive_sha256 = proofcheck.sha256_file(archive_path)
        archive = read_json(archive_path)
        expected_origin = proofcheck.historical_origin_from_archive(
            archive,
            archive_path,
            self.audit.resolve(),
        )
        transaction_temp = proofcheck.proofcheck_temp_path(archive_path)
        transaction_temp.write_text(
            "orphaned transaction payload",
            encoding="utf-8",
            newline="\n",
        )

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = proofcheck.cmd_archive_issue(
                argparse.Namespace(root=self.audit, issue_id="I-001")
            )
        payload = json.loads(output.getvalue())

        self.assertEqual(0, status)
        self.assertIs(True, payload["recovered_existing_archive"])
        self.assertEqual(archive_sha256, payload["archive_sha256"])
        self.assertEqual(archive_sha256, proofcheck.sha256_file(archive_path))
        self.assertFalse(transaction_temp.exists())
        self.assertFalse(transaction_lock.exists())
        recovered_issue = next(
            row
            for row in read_json(issue_path)["issues"]
            if row["id"] == "I-001"
        )
        self.assertEqual(expected_origin, recovered_issue["historical_origin"])

    def test_archive_issue_does_not_ignore_similar_temp_outside_history(
        self,
    ) -> None:
        self.make_archivable_s1_audit()
        outside_temp = (
            self.audit
            / "audit"
            / "06_reports"
            / ".I-001-origin.json.proofcheck.tmp"
        )
        outside_temp.write_text(
            "not a confined archive transaction",
            encoding="utf-8",
            newline="\n",
        )

        state_files = {
            row["file"]
            for row in proofcheck.audit_state_manifest(self.audit)
        }
        freshness = proofcheck.check_finalization_freshness(self.audit)

        self.assertIn(
            "audit/06_reports/.I-001-origin.json.proofcheck.tmp",
            state_files,
        )
        self.assertFalse(freshness["usable_finalization"], freshness)
        with self.assertRaisesRegex(
            ValueError,
            "requires a current passed finalization record",
        ):
            proofcheck.cmd_archive_issue(
                argparse.Namespace(root=self.audit, issue_id="I-001")
            )
        self.assertTrue(outside_temp.is_file())

    def test_archive_issue_rejects_invalid_orphan_archive(self) -> None:
        self.make_archivable_s1_audit()
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        archive_path = (
            self.audit
            / "audit"
            / "06_reports"
            / "history"
            / "I-001-origin.json"
        )
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(archive_path, {"archive_schema_version": 1})

        with self.assertRaisesRegex(
            ValueError, "Existing resolution archive cannot be adopted"
        ):
            proofcheck.cmd_archive_issue(
                argparse.Namespace(root=self.audit, issue_id="I-001")
            )

        issue = next(
            row
            for row in read_json(issue_path)["issues"]
            if row["id"] == "I-001"
        )
        self.assertNotIn("historical_origin", issue)
        self.assertEqual(
            {"archive_schema_version": 1}, read_json(archive_path)
        )

    def test_archive_issue_rejects_symlinked_history_ancestors(self) -> None:
        self.make_archivable_s1_audit()
        cases = (
            (self.audit / "audit", self.base / "redirected-audit"),
            (
                self.audit / "audit" / "06_reports",
                self.base / "redirected-reports",
            ),
        )
        for ancestor, redirected in cases:
            with self.subTest(ancestor=ancestor.relative_to(self.audit)):
                ancestor.rename(redirected)
                try:
                    ancestor.symlink_to(redirected, target_is_directory=True)
                except OSError:
                    redirected.rename(ancestor)
                    original_is_symlink = Path.is_symlink

                    def simulated_is_symlink(path: Path) -> bool:
                        return path == ancestor or original_is_symlink(path)

                    with mock.patch.object(
                        Path,
                        "is_symlink",
                        new=simulated_is_symlink,
                    ):
                        with self.assertRaisesRegex(
                            ValueError,
                            "Resolution history ancestor cannot be a symlink",
                        ):
                            proofcheck.cmd_archive_issue(
                                argparse.Namespace(
                                    root=self.audit,
                                    issue_id="I-001",
                                )
                            )
                    continue
                try:
                    with self.assertRaisesRegex(
                        ValueError,
                        "Resolution history ancestor cannot be a symlink",
                    ):
                        proofcheck.cmd_archive_issue(
                            argparse.Namespace(
                                root=self.audit,
                                issue_id="I-001",
                            )
                        )
                finally:
                    ancestor.unlink()
                    redirected.rename(ancestor)

    def test_removed_move_in_retained_affected_unit_finalizes(self) -> None:
        main_path, _, issue = self.make_resolved_s1_lifecycle_audit()
        self.convert_resolved_lifecycle_to_removed_move(
            main_path,
            issue,
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertEqual([], errors)

    def test_removed_disposition_rejects_whole_affected_unit_deletion(
        self,
    ) -> None:
        main_path, _, issue = self.make_resolved_s1_lifecycle_audit()
        self.convert_resolved_lifecycle_to_removed_move(
            main_path,
            issue,
        )
        main_path.unlink()

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "removed may retire only the failed origin inside a retained "
                "affected result" in error
                for error in errors
            ),
            errors,
        )

    def reseal_modified_resolution_archive(
        self,
        archive_path: Path,
        issue: dict,
        archive: dict,
    ) -> None:
        archive["archive_payload_sha256"] = (
            proofcheck.resolution_archive_payload_sha256(archive)
        )
        write_json(archive_path, archive)
        issue["historical_origin"]["sha256"] = proofcheck.sha256_file(
            archive_path
        )
        self.install_canonical_issue(issue, migrate=False)

    def test_resolved_s1_rejects_tampered_historical_archive(self) -> None:
        _, archive_path, _ = self.make_resolved_s1_lifecycle_audit()
        archive = read_json(archive_path)
        archive["projection"]["severity"][0][0] = "S0"
        write_json(archive_path, archive)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "historical_origin.sha256" in error
                or "archive payload hash" in error
                or "projection hash" in error
                for error in errors
            ),
            errors,
        )

    def test_resolved_s1_rejects_archive_issue_not_in_prior_issue_log(
        self,
    ) -> None:
        _, archive_path, issue = self.make_resolved_s1_lifecycle_audit()
        archive = read_json(archive_path)
        archive["issue_record"]["suggested_changes"][0]["proposal"] += (
            " This text was injected only into the archive."
        )
        archive["issue_record_sha256"] = proofcheck.canonical_sha256(
            archive["issue_record"]
        )
        self.reseal_modified_resolution_archive(
            archive_path,
            issue,
            archive,
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "archived issue is not the exact prior issue-log member"
                in error
                for error in errors
            ),
            errors,
        )

    def test_resolved_s1_rejects_tampered_sealed_ledger_bytes(
        self,
    ) -> None:
        _, archive_path, issue = self.make_resolved_s1_lifecycle_audit()
        archive = read_json(archive_path)
        ledger_record = archive["prior_artifacts"]["ledgers"][0]
        ledger = json.loads(
            base64.b64decode(ledger_record["content_base64"]).decode("utf-8")
        )
        step = next(row for row in ledger["steps"] if row["id"] == "S003")
        move = next(
            row
            for row in step["inference"]["moves"]
            if row["id"] == "M001"
        )
        move["rule"] += (
            " Tampered after prior finalization."
        )
        ledger_text = (
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"
        )
        ledger_record["content_base64"] = base64.b64encode(
            ledger_text.encode("utf-8")
        ).decode("ascii")
        ledger_record["sha256"] = proofcheck.sha256_text(ledger_text)
        archive["ledger_sha256s"]["lem:main"] = ledger_record["sha256"]
        self.reseal_modified_resolution_archive(
            archive_path,
            issue,
            archive,
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "prior_artifacts.ledgers[1] bytes are not bound by the "
                "prior finalization manifest" in error
                for error in errors
            ),
            errors,
        )

    def test_resolved_s1_rejects_failure_projection_not_matching_sealed_ledger(
        self,
    ) -> None:
        _, archive_path, issue = self.make_resolved_s1_lifecycle_audit()
        archive = read_json(archive_path)
        archive["projection"]["failure"][0][5] = (
            "A different archived claim."
        )
        archive["projection_sha256"] = proofcheck.canonical_sha256(
            archive["projection"]
        )
        self.reseal_modified_resolution_archive(
            archive_path,
            issue,
            archive,
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "archived failure projection does not match the sealed "
                "ledger move" in error
                for error in errors
            ),
            errors,
        )

    def test_resolved_s1_rejects_malformed_sealed_ledger_collection(
        self,
    ) -> None:
        _, archive_path, issue = self.make_resolved_s1_lifecycle_audit()
        archive = read_json(archive_path)
        archive["prior_artifacts"]["ledgers"] = {
            "lem:main": archive["prior_artifacts"]["ledgers"][0]
        }
        self.reseal_modified_resolution_archive(
            archive_path,
            issue,
            archive,
        )

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "prior_artifacts.ledgers must be a list" in error
                for error in errors
            ),
            errors,
        )

    def test_resolved_s1_rejects_malformed_historical_archive_closure(
        self,
    ) -> None:
        _, archive_path, issue = self.make_resolved_s1_lifecycle_audit()
        archive = read_json(archive_path)
        archive["required_closure"]["dependency_uses"] = ["D001"]
        archive["archive_payload_sha256"] = (
            proofcheck.resolution_archive_payload_sha256(archive)
        )
        write_json(archive_path, archive)
        issue["historical_origin"]["sha256"] = proofcheck.sha256_file(
            archive_path
        )
        self.install_canonical_issue(issue, migrate=False)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "archive required_closure.dependency_uses[1] must be an object"
                in error
                for error in errors
            ),
            errors,
        )

    def test_resolved_s1_rejects_missing_current_reference(self) -> None:
        _, _, issue = self.make_resolved_s1_lifecycle_audit()
        issue["current_resolution"]["current_ref"] = {
            "kind": "ledger_move",
            "unit_id": "lem:main",
            "step_id": "S003",
            "move_id": "M999",
        }
        self.install_canonical_issue(issue, migrate=False)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "current_resolution.current_ref does not resolve" in error
                for error in errors
            ),
            errors,
        )

    def test_resolved_s1_rejects_unrelated_replacement_reference(
        self,
    ) -> None:
        _, _, issue = self.make_resolved_s1_lifecycle_audit()
        issue["current_resolution"].update(
            {
                "disposition": "replaced",
                "current_ref": {
                    "kind": "ledger_move",
                    "unit_id": "lem:prior",
                    "step_id": "S001",
                    "move_id": "M001",
                },
                "mapping": (
                    "The archived move is claimed to map to a clean but "
                    "unrelated move in lem:prior."
                ),
            }
        )
        self.install_canonical_issue(issue, migrate=False)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "current_resolution.current_ref" in error
                and (
                    "affected" in error.lower()
                    or "unrelated" in error.lower()
                )
                for error in errors
            ),
            errors,
        )

    def test_resolved_s1_rejects_unrecorded_dependency_retirement(
        self,
    ) -> None:
        main_path, _, issue = self.make_resolved_s1_lifecycle_audit()
        ledger = read_json(main_path)
        step = next(row for row in ledger["steps"] if row["id"] == "S003")
        step["dependencies"] = []
        step["premise_uses"] = [
            premise
            for premise in step["premise_uses"]
            if premise.get("origin", {}).get("reference") != "D001"
        ]
        step["inference"]["moves"][0]["premise_ids"] = [
            premise_id
            for premise_id in step["inference"]["moves"][0]["premise_ids"]
            if premise_id != "P002"
        ]
        ledger["review"]["direct_dependencies"] = []
        ledger["review"]["conclusion_results"][0]["dependency_use_ids"] = []
        write_json(main_path, ledger)

        registry_path = (
            self.audit
            / "audit"
            / "03_dependencies"
            / "DEPENDENCY_REGISTRY.json"
        )
        registry = read_json(registry_path)
        registry["internal_uses"] = []
        write_json(registry_path, registry)

        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        report = report.replace(
            "| lem:main | C001 | verified | valid | established | verified | "
            "not_applicable | S003/M001 | D001 | none |",
            "| lem:main | C001 | verified | valid | established | verified | "
            "not_applicable | S003/M001 | none | none |",
        )
        report = report.replace(
            "| lem:main | D001 | lem:prior | C001 | internal_result | "
            "verified | passed | verified | none |",
            "None.",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")
        self.seal_schema5_challenge(
            main_path,
            read_json(main_path),
            covered_issue_ids=["I-001"],
        )

        issue["rechecked_dependency_uses"] = []
        issue["current_resolution"]["retired_dependency_uses"] = []
        self.install_canonical_issue(issue, migrate=False)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "retired_dependency_uses must equal" in error
                for error in errors
            ),
            errors,
        )

    def test_resolved_s1_rejects_stale_post_repair_challenge(self) -> None:
        main_path, _, _ = self.make_resolved_s1_lifecycle_audit()
        ledger = read_json(main_path)
        ledger["independent_check"]["challenged_ledger_sha256"] = "0" * 64
        write_json(main_path, ledger)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "challenged_ledger_sha256" in error
                and "stale" in error.lower()
                for error in errors
            ),
            errors,
        )

    def test_open_or_deferred_s0_s1_units_become_effectively_critical(
        self,
    ) -> None:
        main_path, _ = self.prepare_effective_critical_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        summary_path = self.audit / "audit" / "06_reports" / "ISSUE_SUMMARY.md"
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        baseline = {
            "main": read_json(main_path),
            "manifest": read_json(manifest_path),
            "report": report_path.read_text(encoding="utf-8"),
            "summary": summary_path.read_text(encoding="utf-8"),
            "issues": read_json(issue_path),
        }
        cases = (
            ("open_s0", "S0", "open"),
            ("deferred_s1", "S1", "deferred"),
        )
        for name, severity, status in cases:
            with self.subTest(case=name):
                write_json(main_path, baseline["main"])
                write_json(manifest_path, baseline["manifest"])
                report_path.write_text(
                    baseline["report"], encoding="utf-8", newline="\n"
                )
                summary_path.write_text(
                    baseline["summary"], encoding="utf-8", newline="\n"
                )
                write_json(issue_path, baseline["issues"])
                self.set_expected_assessment("inconclusive")
                issue = self.make_schema5_issue(
                    severity=severity, status=status
                )
                self.install_schema5_issue(main_path, issue)

                errors, _ = proofcheck.check_audit_finalization(self.audit)

                self.assertTrue(
                    any(
                        "lem:main" in error
                        and "challenge" in error.lower()
                        and (
                            "effective" in error.lower()
                            or "s0" in error.lower()
                            or "s1" in error.lower()
                        )
                        for error in errors
                    ),
                    errors,
                )

    def test_s2_does_not_expand_the_effective_critical_set(
        self,
    ) -> None:
        main_path, _ = self.prepare_effective_critical_audit()
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        summary_path = self.audit / "audit" / "06_reports" / "ISSUE_SUMMARY.md"
        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        baseline = {
            "main": read_json(main_path),
            "manifest": read_json(manifest_path),
            "report": report_path.read_text(encoding="utf-8"),
            "summary": summary_path.read_text(encoding="utf-8"),
            "issues": read_json(issue_path),
        }
        cases = (("open_s2", "S2", "open", "inconclusive"),)
        for name, severity, status, assessment in cases:
            with self.subTest(case=name):
                write_json(main_path, baseline["main"])
                write_json(manifest_path, baseline["manifest"])
                report_path.write_text(
                    baseline["report"], encoding="utf-8", newline="\n"
                )
                summary_path.write_text(
                    baseline["summary"], encoding="utf-8", newline="\n"
                )
                write_json(issue_path, baseline["issues"])
                if assessment != "no_defect_found":
                    self.set_expected_assessment(assessment)
                issue = self.make_schema5_issue(
                    severity=severity, status=status
                )
                self.install_schema5_issue(main_path, issue)

                errors, _ = proofcheck.check_audit_finalization(self.audit)
                main_challenge_errors = [
                    error
                    for error in errors
                    if "lem:main" in error and "challenge" in error.lower()
                ]

                self.assertEqual([], main_challenge_errors, errors)

    def test_resolved_s1_retains_issue_promoted_challenge_closure(
        self,
    ) -> None:
        main_path, _ = self.prepare_effective_critical_audit()
        issue = self.make_schema5_issue(
            severity="S1",
            status="resolved",
        )
        self.install_schema5_issue(main_path, issue)
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")

        self.assertNotIn(
            "lem:main",
            manifest["audit_scope"]["critical_units"],
        )
        critical, severe_by_unit = (
            proofcheck.effective_critical_requirements(
                manifest,
                [issue],
            )
        )
        self.assertIn("lem:main", critical)
        self.assertEqual({"I-001"}, severe_by_unit["lem:main"])

        _, summaries, _ = proofcheck.audit_ledgers(self.audit, True)
        summaries_by_id = {
            summary["unit_id"]: summary
            for summary in summaries
        }
        projection = proofcheck.canonical_issue_detail_projection(
            issue,
            summaries_by_id,
            [],
            critical,
            [],
            manifest["audit_scope"]["overall_assessment"],
            evidence_base=self.audit,
        )
        closure = projection["closure"][0]
        self.assertEqual("lem:main", closure[4])
        self.assertEqual("none", closure[5])
        self.assertEqual("open", closure[8])

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any(
                "lem:main" in error
                and "independent" in error.lower()
                and "challenge" in error.lower()
                for error in errors
            ),
            errors,
        )

    def test_effective_critical_challenge_must_be_fresh_and_issue_aware(
        self,
    ) -> None:
        main_path, _ = self.prepare_effective_critical_audit()
        self.set_expected_assessment("inconclusive")
        issue = self.make_schema5_issue(severity="S1", status="open")
        self.install_schema5_issue(main_path, issue)
        ledger = read_json(main_path)
        artifact = self.audit / "audit" / "05_adversarial" / "main-issue.md"
        artifact.write_text(
            "# Challenge\n\nThis stale challenge does not inspect I-001.\n",
            encoding="utf-8",
            newline="\n",
        )
        ledger["independent_check"] = {
            "required": True,
            "status": "agreed",
            "independence_level": "fresh_context_same_model",
            "challenger_verdict": "conditionally_verified",
            "reconciled_verdict": "conditionally_verified",
            "artifact": "audit/05_adversarial/main-issue.md",
            "disagreements": [],
            "resolution": "",
            "covered_issue_ids": [],
            "source_snapshot_sha256": "",
            "challenged_ledger_sha256": "",
            "challenge_artifact_sha256": "",
            "generated_utc": "",
        }
        write_json(main_path, ledger)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        for field in (
            "covered_issue_ids",
            "source_snapshot_sha256",
            "challenged_ledger_sha256",
            "challenge_artifact_sha256",
            "generated_utc",
        ):
            self.assertTrue(
                any(
                    (
                        "lem:main" in error
                        or "lem-main" in error
                    )
                    and field in error
                    for error in errors
                ),
                (field, errors),
            )

    def test_schema5_issue_rejects_legacy_free_text_evidence_fields(self) -> None:
        main_path, _ = self.prepare_effective_critical_audit()
        self.set_expected_assessment("inconclusive")
        issue = self.make_schema5_issue(severity="S2", status="open")
        issue.update(
            {
                "location": "paper.tex:6",
                "evidence": ["Legacy free-text evidence."],
                "downstream_consequences": ["Legacy authored propagation."],
                "possible_repair": "Legacy unstructured repair.",
            }
        )
        self.install_schema5_issue(main_path, issue)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        retired_errors = [
            error
            for error in errors
            if "I-001" in error
            and (
                "retired" in error.lower()
                or "inspection-only" in error.lower()
            )
        ]
        self.assertEqual(1, len(retired_errors), errors)
        for field in (
            "location",
            "evidence",
            "downstream_consequences",
            "possible_repair",
        ):
            self.assertIn(field, retired_errors[0])

    def test_global_issue_origin_requires_locked_backlinked_evidence(
        self,
    ) -> None:
        self.make_complete_audit()
        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=False,
            severity="S3",
            summary="The global source-resolution check found a presentation defect.",
        )
        issue["origin_ref"] = {
            "kind": "global_check",
            "aspect": "source_resolution",
            "evidence_spans": [
                proofcheck.locked_span(
                    self.paper,
                    2,
                    4,
                    self.audit,
                    role="global_consistency_evidence",
                )
            ],
        }
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        global_pass = manifest["completion"]["global_consistency_pass"]
        source_resolution = next(
            row
            for row in global_pass["checks"]
            if row["aspect"] == "source_resolution"
        )
        source_resolution.update(
            {
                "status": "defect",
                "evidence": (
                    "The locked theorem span exhibits the recorded presentation "
                    "defect."
                ),
                "affected_units": ["lem:main"],
                "issue_ids": ["I-001"],
            }
        )
        global_pass["status"] = "completed_with_findings"
        write_json(manifest_path, manifest)
        self.set_expected_assessment("defects_found")
        self.install_canonical_issue(issue, migrate=False)

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertEqual([], errors)
        detail_section = proofcheck.report_section(
            (
                self.audit
                / "audit"
                / "06_reports"
                / "FINAL_REPORT.md"
            ).read_text(encoding="utf-8"),
            "## Detailed findings",
        )
        failure_row = proofcheck.markdown_tables(
            detail_section or ""
        )[0][2]
        self.assertNotEqual("none", failure_row[1])
        self.assertNotEqual("none", failure_row[2])

        issue_without_evidence = json.loads(json.dumps(issue))
        issue_without_evidence["origin_ref"].pop("evidence_spans")
        self.install_canonical_issue(
            issue_without_evidence,
            migrate=False,
        )
        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertTrue(
            any(
                "I-001.origin_ref.evidence_spans" in error
                and "nonempty" in error.lower()
                for error in errors
            ),
            errors,
        )

    def test_resolved_global_check_can_map_to_clean_current_record(self) -> None:
        ledger_path = self.make_complete_audit()
        aspect = "source_resolution"
        historical_span = proofcheck.locked_span(
            self.paper,
            2,
            4,
            self.audit,
            role="global_consistency_evidence",
        )
        issue = self.make_global_issue(
            finding_status="defect",
            load_bearing=False,
            severity="S2",
            summary="The global source-resolution check found a repairable defect.",
        )
        issue["origin_ref"] = {
            "kind": "global_check",
            "aspect": aspect,
            "evidence_spans": [historical_span],
        }
        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        global_pass = manifest["completion"]["global_consistency_pass"]
        global_check = next(
            row for row in global_pass["checks"] if row["aspect"] == aspect
        )
        global_check.update(
            {
                "status": "defect",
                "evidence": (
                    "The historical global check records the source-resolution "
                    "defect before repair."
                ),
                "affected_units": ["lem:main"],
                "issue_ids": ["I-001"],
            }
        )
        global_pass["status"] = "completed_with_findings"
        write_json(manifest_path, manifest)
        self.set_expected_assessment("defects_found")
        self.install_canonical_issue(issue, migrate=False)

        historical_errors, _ = proofcheck.check_audit_finalization(
            self.audit
        )
        self.assertEqual([], historical_errors)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(
                0,
                proofcheck.cmd_finalize(argparse.Namespace(root=self.audit)),
            )
            self.assertEqual(
                0,
                proofcheck.cmd_archive_issue(
                    argparse.Namespace(root=self.audit, issue_id="I-001")
                ),
            )

        issue_path = self.audit / "audit" / "06_reports" / "ISSUE_LOG.json"
        archived_issue = next(
            row
            for row in read_json(issue_path)["issues"]
            if row["id"] == "I-001"
        )
        historical_origin = archived_issue["historical_origin"]

        manifest = read_json(manifest_path)
        global_pass = manifest["completion"]["global_consistency_pass"]
        global_check = next(
            row for row in global_pass["checks"] if row["aspect"] == aspect
        )
        global_check.update(
            {
                "status": "passed",
                "evidence": (
                    "The repaired canonical source-resolution check is clean "
                    "under the current locked evidence."
                ),
                "affected_units": [],
                "issue_ids": [],
            }
        )
        global_pass["status"] = "completed"
        write_json(manifest_path, manifest)
        self.set_expected_assessment("no_defect_found")
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report_path.write_text(
            report_path.read_text(encoding="utf-8").replace(
                "- Highest-consequence issue: I-001",
                "- Highest-consequence issue: none",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.seal_schema5_challenge(
            ledger_path,
            read_json(ledger_path),
            covered_issue_ids=[],
            artifact_text=(
                "# Post-repair global challenge\n\n"
                "The fresh check confirms the repaired global source-resolution "
                "record is clean and lem:main remains verified.\n"
            ),
        )

        current_span = proofcheck.locked_span(
            self.paper,
            2,
            4,
            self.audit,
            role="repair_verification",
        )
        resolved_issue = json.loads(json.dumps(issue))
        resolved_issue.update(
            {
                "status": "resolved",
                "finding_status": "resolved",
                "resolution": (
                    "The canonical global check was repaired and rerun cleanly."
                ),
                "source_revision": (
                    "The current global consistency record contains the clean "
                    "post-repair result."
                ),
                "recheck_evidence": [
                    "The current locked evidence and fresh challenge verify the repair."
                ],
                "source_snapshot_sha256": read_json(manifest_path)[
                    "source_snapshot"
                ]["sha256"],
                "rechecked_units": ["lem:main"],
                "rechecked_dependency_uses": [],
                "reconciled_deliverables": [],
                "historical_origin": historical_origin,
                "current_resolution": {
                    "disposition": "repaired",
                    "current_ref": {
                        "kind": "global_check",
                        "aspect": aspect,
                        "evidence_spans": [current_span],
                    },
                    "mapping": (
                        "The archived source_resolution finding maps to the "
                        "same canonical aspect after its clean rerun."
                    ),
                    "verification_status": "verified_sufficient",
                    "evidence_spans": [current_span],
                    "required_rechecks": ["lem:main"],
                    "retired_dependency_uses": [],
                },
            }
        )
        self.install_canonical_issue(resolved_issue, migrate=False)

        errors, _ = proofcheck.check_audit_finalization(self.audit)

        self.assertEqual([], errors)

    def test_overlapping_reviewed_proof_locations_fail(self) -> None:
        self.make_complete_audit()
        inventory_path = (
            self.audit / "audit" / "01_index" / "theorem_inventory.json"
        )
        inventory = read_json(inventory_path)
        manual = json.loads(json.dumps(inventory["units"][0]))
        manual["id"] = "lem:overlap"
        manual["label"] = "lem:overlap"
        manual["proof_association"] = {
            "status": "associated",
            "method": "reviewed_manual",
            "target": "lem:overlap",
            "evidence_occurrence_ids": [],
        }
        inventory["units"].append(manual)
        write_json(inventory_path, inventory)

        manifest_path = self.audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["audit_scope"]["excluded_units"] = [
            {
                "id": "lem:overlap",
                "reason": "Synthetic excluded unit used to test overlap detection.",
            }
        ]
        manifest["audit_scope"]["inventory_overrides"] = [
            {
                "unit_id": "lem:overlap",
                "kind": "manual_unit",
                "reason": "The synthetic unit is added for overlap validation.",
                "evidence": "Its reviewed proof span exactly duplicates lem:main.",
                "reviewed_unit_sha256": proofcheck.canonical_sha256(manual),
            }
        ]
        write_json(manifest_path, manifest)
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8").replace(
            "- Results not checked: none",
            "- Results not checked: lem:overlap",
        )
        report_path.write_text(report, encoding="utf-8", newline="\n")
        self.refresh_dependency_review()

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        self.assertTrue(
            any("Reviewed proof spans overlap" in error for error in errors),
            errors,
        )

    def test_public_example_refutation_contract_is_self_consistent(
        self,
    ) -> None:
        example = read_json(
            SCRIPT.parents[1]
            / "assets"
            / "templates"
            / "AUDIT_RECORD_EXAMPLES.json"
        )
        ledger = example["ledger_example"]
        result = ledger["review"]["conclusion_results"][0]
        support = result["support"]
        step = next(
            row for row in ledger["steps"] if row["id"] == support["step_id"]
        )
        move = next(
            row
            for row in step["inference"]["moves"]
            if row["id"] == support["move_id"]
        )
        conclusion = ledger["obligation"]["conclusions"][0]
        issue = example["issue_log_example"]["issues"][0]
        generated = example["generated_issue_report_example"]

        self.assertEqual("refuted", result["statement_status"])
        self.assertEqual("counterexample", move["failure"]["kind"])
        self.assertEqual(conclusion["claim"], move["failure"]["target"])
        self.assertEqual(
            "statement_refuted", issue["invalidation_kind"]
        )
        self.assertEqual(
            "counterexample", generated["failed_move"]["failure_kind"]
        )
        self.assertEqual(
            conclusion["claim"], generated["failed_move"]["target"]
        )
        self.assertEqual(
            "statement_refuted",
            generated["current_invalidation_effect"]["invalidation_kind"],
        )

        source_lines = ledger["source_lines"]
        self.assertEqual([120, 121, 122], [row["line"] for row in source_lines])
        for row in source_lines:
            self.assertEqual(
                proofcheck.sha256_text(row["text"]),
                row["sha256"],
            )
        source_line_by_number = {
            row["line"]: row["text"] for row in source_lines
        }
        flattened_unit_lines: list[int] = []
        for unit in ledger["source_units"]:
            start_line, end_line = unit["lines"]
            covered_lines = list(range(start_line, end_line + 1))
            flattened_unit_lines.extend(covered_lines)
            self.assertEqual(
                proofcheck.sha256_text(
                    "\n".join(
                        source_line_by_number[line] for line in covered_lines
                    )
                ),
                unit["source_sha256"],
            )
        self.assertEqual([120, 121, 122], flattened_unit_lines)
        self.assertEqual(
            {unit["id"] for unit in ledger["source_units"]},
            {step["source_unit_id"] for step in ledger["steps"]},
        )

        dependency = next(
            row
            for row in example["dependency_registry_example"]["internal_uses"]
            if row["use_id"] == "D001"
        )
        downstream_site = dependency["use_site"]
        self.assertEqual(210, downstream_site["start_line"])
        self.assertEqual(210, downstream_site["end_line"])
        self.assertEqual(
            proofcheck.sha256_text(downstream_site["quote"]),
            downstream_site["sha256"],
        )
        self.assertEqual(["paper.tex:210"], ledger["review"]["use_sites"])
        downstream_propagation = next(
            row
            for row in generated["propagation"]
            if row.get("use_id") == "D001"
        )
        self.assertEqual(
            downstream_site,
            downstream_propagation["use_site"],
        )

        failure_quote = "\n".join(
            row["text"] for row in source_lines if row["line"] in {120, 121}
        )
        self.assertEqual(failure_quote, generated["failure_site"]["quote"])
        self.assertEqual(
            proofcheck.sha256_text(failure_quote),
            generated["failure_site"]["sha256"],
        )
        origin_propagation = next(
            row for row in generated["propagation"] if row["relation"] == "origin"
        )
        self.assertEqual(
            generated["failure_site"],
            origin_propagation["use_site"],
        )
        premise_claims = [
            premise["claim"] for premise in step["premise_uses"]
        ]
        self.assertEqual(premise_claims, generated["failed_move"]["premises"])
        self.assertEqual(
            move["failure"]["evidence"],
            generated["failed_move"]["failure_evidence"],
        )
        self.assertEqual(
            {
                proofcheck.canonical_sha256(contract_ref)
                for contract_ref in issue["contract_refs"]
            },
            {
                proofcheck.canonical_sha256(row["contract_ref"])
                for row in generated["normalized_contract"]
            },
        )
        self.assertEqual(
            proofcheck.METHOD_INTERFACE_SCHEMA_VERSION,
            example["method_interface_schema_version"],
        )
        self.assertEqual(1, example["method_interface_schema_version"])

        self.assertEqual(
            "D001 is incorrect. The recorded proof of thm:main therefore "
            "does not establish its conclusion, but this finding does not "
            "by itself refute that downstream conclusion.",
            downstream_propagation["effect"],
        )
        self.assertNotIn("refuted", downstream_propagation["effect"].lower())
        promoted_resolution = example["promoted_challenge_example"]["resolution"]
        self.assertIn(
            "the recorded downstream proof remains invalid",
            promoted_resolution,
        )
        self.assertIn(
            "does not by itself refute the downstream conclusion",
            promoted_resolution,
        )

    def test_public_templates_expose_exact_reporting_contracts(self) -> None:
        template_root = SCRIPT.parents[1] / "assets" / "templates"
        report = (template_root / "FINAL_REPORT.md").read_text(encoding="utf-8")
        challenge_rows = proofcheck.markdown_table_rows(
            proofcheck.report_section(
                report,
                "## Independent critical-path challenges",
            )
            or ""
        )
        self.assertEqual(
            [
                "Result",
                "Challenge status",
                "Independence",
                "Covered issue IDs",
                "Challenger verdict",
                "Reconciled verdict",
                "Disagreements",
                "Artifact",
                "Source snapshot SHA256",
                "Challenged ledger SHA256",
                "Artifact SHA256",
                "Generated UTC",
                "Resolution",
            ],
            challenge_rows[0],
        )
        method_rows = proofcheck.markdown_table_rows(
            proofcheck.report_section(
                report,
                "## Method-interface findings",
            )
            or ""
        )
        self.assertEqual(
            [
                "Issue",
                "Finding class",
                "Interface ID",
                "Estimator-target status",
                "Implementation inspection",
                "Inspection mode",
                "Code to documented estimator",
                "Code to required target",
                "Execution provenance",
                "Affected layer",
            ],
            method_rows[0],
        )
        self.assertEqual(
            1,
            len(
                re.findall(
                    r"^- Method-interface schema version: 1$",
                    report,
                    re.MULTILINE,
                )
            ),
        )
        self.assertEqual(
            1,
            len(
                re.findall(
                    r"^- Declared external deliverables:\s*$",
                    report,
                    re.MULTILINE,
                )
            ),
        )

        check_plan = (template_root / "CHECK_PLAN.md").read_text(
            encoding="utf-8"
        )
        for required_wording in (
            "Every locked source_lines row contains its exact line text and "
            "matching SHA256; every source_unit.source_sha256 matches the "
            "newline-joined text of its exact range",
            "Every review.use_sites entry is one canonical file:line reference "
            "occurrence; every locked downstream use span, SHA256, and quote "
            "is exact",
            "Every generated finding reproduces the canonical locked quote, "
            "exact premises, and recorded failure evidence without paraphrase",
            "Downstream effects weaken dependency closure and proof support "
            "only to the level established; they do not refute a downstream "
            "conclusion without independent evidence",
            "Every method-interface record reports both implementation "
            "inspection status and inspection_mode",
            "Every critical challenge reports disagreements, resolution, "
            "artifact path, current artifact hash, and freshness fields",
            "The final-report Declared external deliverables scalar and table "
            "exactly reconcile with manifest report_deliverables",
        ):
            self.assertIn(required_wording, check_plan)

    def test_delivery_check_requires_current_usable_finalization(self) -> None:
        self.make_complete_audit()
        parser = proofcheck.build_parser()

        def run_delivery() -> tuple[int, dict]:
            args = parser.parse_args(
                ["delivery-check", "--root", str(self.audit)]
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = args.func(args)
            return status, json.loads(output.getvalue())

        status, result = run_delivery()
        self.assertEqual(1, status)
        self.assertEqual("NONFINAL", result["delivery_status"])
        self.assertFalse(result["usable_finalization"])

        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(
                0,
                proofcheck.cmd_finalize(argparse.Namespace(root=self.audit)),
            )
        status, result = run_delivery()
        self.assertEqual(0, status)
        self.assertEqual("FINAL", result["delivery_status"])
        self.assertTrue(result["usable_finalization"])

        self.paper.write_text(
            self.paper.read_text(encoding="utf-8") + "% source drift\n",
            encoding="utf-8",
            newline="\n",
        )
        status, result = run_delivery()
        self.assertEqual(1, status)
        self.assertEqual("NONFINAL", result["delivery_status"])
        self.assertFalse(result["usable_finalization"])
        self.assertTrue(result["reasons"])

    def test_archive_issue_does_not_require_hard_links(self) -> None:
        self.make_archivable_s1_audit()
        archive_path = (
            self.audit
            / "audit"
            / "06_reports"
            / "history"
            / "I-001-origin.json"
        )

        with mock.patch.object(
            proofcheck.os,
            "link",
            side_effect=AssertionError("hard links are unavailable"),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                status = proofcheck.cmd_archive_issue(
                    argparse.Namespace(root=self.audit, issue_id="I-001")
                )

        self.assertEqual(0, status)
        self.assertTrue(archive_path.is_file())

    def test_archive_issue_recovers_from_matching_lock_only_interruption(
        self,
    ) -> None:
        self.make_archivable_s1_audit()
        archive_path = (
            self.audit
            / "audit"
            / "06_reports"
            / "history"
            / "I-001-origin.json"
        )
        temporary = proofcheck.proofcheck_temp_path(archive_path)
        lock = archive_path.with_name(
            f".{archive_path.name}.proofcheck.lock"
        )
        original = proofcheck.atomic_write_text

        def interrupt_before_staging(path: Path, text: str) -> None:
            if path.resolve() == temporary.resolve():
                raise OSError("simulated lock-only interruption")
            original(path, text)

        with mock.patch.object(
            proofcheck,
            "utc_now",
            return_value="2030-01-01T00:00:00Z",
        ):
            with mock.patch.object(
                proofcheck,
                "atomic_write_text",
                side_effect=interrupt_before_staging,
            ):
                with self.assertRaisesRegex(
                    OSError, "simulated lock-only interruption"
                ):
                    proofcheck.cmd_archive_issue(
                        argparse.Namespace(root=self.audit, issue_id="I-001")
                    )

        self.assertTrue(lock.is_file())
        self.assertFalse(temporary.exists())
        self.assertFalse(archive_path.exists())
        lock_record = read_json(lock)
        self.assertEqual(1, lock_record["transaction_schema_version"])
        self.assertEqual(archive_path.name, lock_record["target"])
        self.assertRegex(lock_record["expected_sha256"], r"^[0-9a-f]{64}$")

        with mock.patch.object(
            proofcheck,
            "utc_now",
            return_value="2030-01-02T00:00:00Z",
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                status = proofcheck.cmd_archive_issue(
                    argparse.Namespace(root=self.audit, issue_id="I-001")
                )

        self.assertEqual(0, status)
        self.assertTrue(archive_path.is_file())
        self.assertFalse(temporary.exists())
        self.assertFalse(lock.exists())


class PortabilityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.source_dir = self.base / "inputs with spaces" / "理论"
        self.source_dir.mkdir(parents=True)
        self.paper = self.source_dir / "paper source.tex"
        self.paper.write_text(
            "\\newtheorem{lemma}{Lemma}\n"
            "\\begin{lemma}\\label{lem:portable}\n$x=x$.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nBy reflexivity.\n\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )

    def tearDown(self) -> None:
        try:
            self.paper.chmod(stat.S_IREAD | stat.S_IWRITE)
        except FileNotFoundError:
            pass
        self.temp.cleanup()

    def parse_and_run(self, argv: list[str]) -> tuple[int, dict]:
        args = proofcheck.build_parser().parse_args(argv)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = int(args.func(args))
        return status, json.loads(output.getvalue())

    def scaffold_args(
        self,
        output: Path,
        *,
        paper: Path | None = None,
        input_kind: str = "latex",
        publisher_pdf: Path | None = None,
        portable_sources: bool = False,
        visual_review_status: str = "not_started",
        visual_review_notes: str | None = None,
        project_root: Path | None = None,
    ) -> argparse.Namespace:
        return argparse.Namespace(
            paper=paper or self.paper,
            output=output,
            input_kind=input_kind,
            publisher_pdf=publisher_pdf,
            portable_sources=portable_sources,
            visual_review_status=visual_review_status,
            visual_review_notes=visual_review_notes,
            additional_source=None,
            fls=None,
            project_root=project_root,
        )

    def test_cli_requires_declared_input_kind(self) -> None:
        parser = proofcheck.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(
                    [
                        "scaffold",
                        "--paper",
                        str(self.paper),
                        "--output",
                        str(self.base / "audit"),
                    ]
                )

    def test_scaffold_cli_rejects_complete_visual_review_claim(self) -> None:
        parser = proofcheck.build_parser()
        help_output = io.StringIO()
        with contextlib.redirect_stdout(help_output):
            with self.assertRaises(SystemExit) as help_exit:
                parser.parse_args(["scaffold", "--help"])
        self.assertEqual(0, help_exit.exception.code)
        self.assertIn(
            "--visual-review-status {not_started,partial}",
            help_output.getvalue(),
        )

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as invalid_exit:
                parser.parse_args(
                    [
                        "scaffold",
                        "--paper",
                        str(self.base / "transcription.txt"),
                        "--input-kind",
                        "pdf_transcription",
                        "--publisher-pdf",
                        str(self.base / "publisher.pdf"),
                        "--visual-review-status",
                        "complete",
                        "--output",
                        str(self.base / "audit"),
                    ]
                )
        self.assertEqual(2, invalid_exit.exception.code)

    def test_doctor_runs_from_arbitrary_cwd_with_read_only_unicode_source(
        self,
    ) -> None:
        arbitrary_cwd = self.base / "arbitrary working directory" / "分析"
        arbitrary_cwd.mkdir(parents=True)
        output = self.base / "doctor target with spaces"
        self.paper.chmod(stat.S_IREAD)
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "doctor",
                    "--paper",
                    str(self.paper),
                    "--output",
                    str(output),
                    "--input-kind",
                    "latex",
                    "--portable-sources",
                ],
                cwd=arbitrary_cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        finally:
            self.paper.chmod(stat.S_IREAD | stat.S_IWRITE)

        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("doctor", result["command"])
        self.assertEqual("passed", result["status"])
        self.assertTrue(result["ready"])
        self.assertFalse(output.exists())
        self.assertTrue(
            all(row["status"] != "failed" for row in result["checks"])
        )

    def test_doctor_classifies_an_unusable_output_parent(self) -> None:
        blocker = self.base / "ordinary file"
        blocker.write_text("not a directory\n", encoding="utf-8")

        status, result = self.parse_and_run(
            [
                "doctor",
                "--paper",
                str(self.paper),
                "--output",
                str(blocker / "audit"),
                "--input-kind",
                "latex",
            ]
        )

        self.assertEqual(1, status)
        self.assertEqual("failed", result["status"])
        self.assertFalse(result["ready"])
        self.assertGreater(result["failures_by_category"]["output_write"], 0)
        self.assertTrue(
            any(
                row["category"] == "output_write"
                and row["status"] == "failed"
                for row in result["checks"]
            )
        )

    def test_doctor_new_mode_rejects_existing_directory_without_residue(self) -> None:
        output = self.base / "existing audit directory"
        output.mkdir()

        status, result = self.parse_and_run(
            [
                "doctor",
                "--mode",
                "new",
                "--paper",
                str(self.paper),
                "--output",
                str(output),
                "--input-kind",
                "latex",
            ]
        )

        self.assertEqual(1, status)
        self.assertEqual("failed", result["status"])
        self.assertFalse(result["ready"])
        self.assertEqual([], list(output.iterdir()))

    def test_doctor_resume_mode_requires_matching_audit_manifest(self) -> None:
        empty = self.base / "empty resume directory"
        empty.mkdir()
        status, result = self.parse_and_run(
            [
                "doctor",
                "--mode",
                "resume",
                "--paper",
                str(self.paper),
                "--output",
                str(empty),
                "--input-kind",
                "latex",
            ]
        )
        self.assertEqual(1, status)
        self.assertFalse(result["ready"])
        self.assertTrue(
            any(row["id"] == "resume_audit" for row in result["checks"])
        )
        self.assertEqual([], list(empty.iterdir()))

        helper = self.source_dir / "resume-helper.tex"
        helper.write_text("Helper source.\n", encoding="utf-8", newline="\n")
        self.paper.write_text(
            "\\input{resume-helper}\n" + self.paper.read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="\n",
        )
        audit = self.base / "valid resume audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                self.scaffold_args(audit, portable_sources=True)
            )
        status, result = self.parse_and_run(
            [
                "doctor",
                "--mode",
                "resume",
                "--paper",
                str(self.paper),
                "--output",
                str(audit),
                "--input-kind",
                "latex",
            ]
        )
        self.assertEqual(0, status)
        self.assertTrue(result["ready"])
        self.assertEqual("resume", result["mode"])

        status, result = self.parse_and_run(
            [
                "doctor",
                "--mode",
                "resume",
                "--paper",
                str(helper),
                "--output",
                str(audit),
                "--input-kind",
                "latex",
            ]
        )
        self.assertEqual(1, status)
        self.assertFalse(result["ready"])
        self.assertTrue(
            any(
                row["id"] == "resume_audit"
                and "authoritative paper" in row["detail"]
                for row in result["checks"]
            )
        )

    def test_doctor_resume_reconciles_pdf_provenance_and_input_kind(self) -> None:
        transcription = self.source_dir / "transcription.txt"
        transcription.write_text(
            "[Page 1]\nLemma 1. For every x, x=x.\n",
            encoding="utf-8",
            newline="\n",
        )
        publisher = self.source_dir / "publisher.pdf"
        publisher.write_bytes(b"%PDF-1.4\nrecorded publisher\n%%EOF\n")
        wrong_publisher = self.source_dir / "wrong-publisher.pdf"
        wrong_publisher.write_bytes(b"%PDF-1.4\ndifferent publisher\n%%EOF\n")
        audit = self.base / "pdf resume audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                self.scaffold_args(
                    audit,
                    paper=transcription,
                    input_kind="pdf_transcription",
                    publisher_pdf=publisher,
                    portable_sources=True,
                )
            )

        status, result = self.parse_and_run(
            [
                "doctor",
                "--mode",
                "resume",
                "--paper",
                str(transcription),
                "--publisher-pdf",
                str(wrong_publisher),
                "--output",
                str(audit),
                "--input-kind",
                "pdf_transcription",
            ]
        )
        self.assertEqual(1, status)
        self.assertFalse(result["ready"])
        self.assertTrue(
            any(
                row["id"] == "resume_audit"
                and "publisher PDF" in row["detail"]
                for row in result["checks"]
            )
        )

        status, result = self.parse_and_run(
            [
                "doctor",
                "--mode",
                "resume",
                "--paper",
                str(transcription),
                "--output",
                str(audit),
                "--input-kind",
                "latex",
            ]
        )
        self.assertEqual(1, status)
        self.assertFalse(result["ready"])
        self.assertTrue(
            any(
                row["id"] == "resume_audit"
                and "input kind" in row["detail"]
                for row in result["checks"]
            )
        )

        status, result = self.parse_and_run(
            [
                "doctor",
                "--mode",
                "resume",
                "--paper",
                str(transcription),
                "--publisher-pdf",
                str(publisher),
                "--output",
                str(audit),
                "--input-kind",
                "pdf_transcription",
            ]
        )
        self.assertEqual(0, status)
        self.assertTrue(result["ready"])

        nonportable = self.base / "nonportable pdf resume audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                self.scaffold_args(
                    nonportable,
                    paper=transcription,
                    input_kind="pdf_transcription",
                    publisher_pdf=publisher,
                )
            )
        publisher.unlink()
        status, result = self.parse_and_run(
            [
                "doctor",
                "--mode",
                "resume",
                "--paper",
                str(transcription),
                "--publisher-pdf",
                str(wrong_publisher),
                "--output",
                str(nonportable),
                "--input-kind",
                "pdf_transcription",
            ]
        )
        self.assertEqual(1, status)
        self.assertFalse(result["ready"])
        self.assertTrue(
            any(
                row["id"] == "resume_audit"
                and "Publisher PDF not found" in row["detail"]
                for row in result["checks"]
            )
        )

    def test_doctor_reports_probe_cleanup_failure(self) -> None:
        output = self.base / "doctor-cleanup-target"
        original_rmtree = proofcheck.shutil.rmtree
        try:
            with mock.patch.object(
                proofcheck.shutil,
                "rmtree",
                side_effect=OSError("simulated cleanup failure"),
            ):
                status, result = self.parse_and_run(
                    [
                        "doctor",
                        "--paper",
                        str(self.paper),
                        "--output",
                        str(output),
                        "--input-kind",
                        "latex",
                    ]
                )
        finally:
            for residue in output.parent.glob(".proofcheck-doctor-*"):
                original_rmtree(residue)

        self.assertEqual(1, status)
        self.assertFalse(result["ready"])
        self.assertTrue(
            any(
                row["id"] == "output_cleanup"
                and row["status"] == "failed"
                for row in result["checks"]
            )
        )

    def test_scaffold_rejects_raw_pdf_without_committing_workspace(self) -> None:
        raw_pdf = self.base / "paper.pdf"
        raw_pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
        output = self.base / "raw-pdf-audit"

        with self.assertRaisesRegex(ValueError, "raw PDF|Raw PDF|\\.pdf"):
            proofcheck.cmd_scaffold(
                self.scaffold_args(
                    output,
                    paper=raw_pdf,
                    input_kind="pdf_transcription",
                    publisher_pdf=raw_pdf,
                )
            )

        self.assertFalse(output.exists())
        self.assertEqual(
            [],
            list(output.parent.glob(f".{output.name}.*.proofcheck.stage")),
        )

    def test_pdf_transcription_bundle_relocates_without_original_sources(
        self,
    ) -> None:
        transcription = self.source_dir / "pages 1-2 transcription.txt"
        transcription.write_text(
            "[Page 1]\nLemma 1. For every x, x=x.\n"
            "[Page 2]\nProof. By reflexivity.\n",
            encoding="utf-8",
            newline="\n",
        )
        publisher_pdf = self.source_dir / "publisher proof.pdf"
        publisher_pdf.write_bytes(b"%PDF-1.4\nportable fixture\n%%EOF\n")
        audit = self.base / "portable PDF audit"
        with contextlib.redirect_stdout(io.StringIO()):
            status = proofcheck.cmd_scaffold(
                self.scaffold_args(
                    audit,
                    paper=transcription,
                    input_kind="pdf_transcription",
                    publisher_pdf=publisher_pdf,
                    portable_sources=True,
                    visual_review_status="partial",
                    visual_review_notes=(
                        "Pages 1 and 2, including the displayed equality, were "
                        "compared against the rendered publisher PDF."
                    ),
                )
            )
        self.assertEqual(0, status)

        manifest_path = audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        visual_review = manifest["input_provenance"]["visual_review"]
        visual_review.update(
            {
                "status": "complete",
                "reviewed_pages": ["1", "2"],
                "completed_utc": "2026-08-18T12:00:00Z",
            }
        )
        write_json(manifest_path, manifest)
        provenance = manifest["input_provenance"]
        self.assertEqual("pdf_transcription", provenance["kind"])
        self.assertTrue(provenance["portable_sources"])
        self.assertTrue(provenance["manual_inventory_required"])
        self.assertEqual(
            manifest["paper_file"], provenance["authoritative_source"]
        )
        self.assertNotIn("\\", manifest["paper_file"])
        self.assertNotIn("\\", provenance["publisher_pdf"]["file"])
        self.assertTrue(
            all("\\" not in value for value in provenance["original_locations"])
        )
        self.assertNotIn(
            "\\", provenance["publisher_pdf"]["original_location"]
        )
        bundled_text = proofcheck.resolve_stored_path(
            provenance["authoritative_source"], audit
        )
        bundled_pdf = proofcheck.resolve_stored_path(
            provenance["publisher_pdf"]["file"], audit
        )
        self.assertTrue(bundled_text.is_file())
        self.assertTrue(bundled_pdf.is_file())
        self.assertEqual(
            proofcheck.sha256_file(transcription),
            proofcheck.sha256_file(bundled_text),
        )
        self.assertEqual(
            proofcheck.sha256_file(publisher_pdf),
            provenance["publisher_pdf"]["sha256"],
        )
        self.assertEqual(
            publisher_pdf.stat().st_size,
            provenance["publisher_pdf"]["size_bytes"],
        )
        self.assertEqual("complete", provenance["visual_review"]["status"])
        self.assertEqual(
            ["1", "2"], provenance["visual_review"]["reviewed_pages"]
        )
        self.assertEqual(
            "2026-08-18T12:00:00Z",
            provenance["visual_review"]["completed_utc"],
        )

        canonical = provenance["authoritative_source"]
        legacy = canonical.replace("/", "\\")
        self.assertEqual(
            proofcheck.resolve_stored_path(canonical, audit),
            proofcheck.resolve_stored_path(legacy, audit),
        )
        if os.name == "nt":
            foreign = "/tmp/foreign-paper.tex"
            message = "Foreign POSIX absolute path"
        else:
            foreign = r"C:\foreign\paper.tex"
            message = "Foreign Windows absolute path"
        with self.assertRaisesRegex(ValueError, message):
            proofcheck.resolve_stored_path(foreign, audit)

        transcription.unlink()
        publisher_pdf.unlink()
        moved = self.base / "moved audit" / "跨平台"
        moved.parent.mkdir()
        audit.rename(moved)
        status, result = self.parse_and_run(
            ["status", "--root", str(moved)]
        )
        self.assertEqual(0, status)
        self.assertEqual("healthy_wip", result["workflow_state"])
        self.assertEqual([], result["progress"]["drift"])

    def test_pdf_complete_label_cannot_bypass_page_and_inventory_evidence(
        self,
    ) -> None:
        transcription = self.base / "transcription.txt"
        transcription.write_text(
            "[Page 1]\nLemma 1. For every x, x=x.\n",
            encoding="utf-8",
            newline="\n",
        )
        publisher_pdf = self.base / "publisher.pdf"
        publisher_pdf.write_bytes(b"%PDF-1.4\nfixture\n%%EOF\n")
        audit = self.base / "pdf-evidence-gates"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                self.scaffold_args(
                    audit,
                    paper=transcription,
                    input_kind="pdf_transcription",
                    publisher_pdf=publisher_pdf,
                    portable_sources=True,
                    visual_review_status="partial",
                    visual_review_notes=(
                        "The displayed equality was compared on page 1."
                    ),
                )
            )

        manifest_path = audit / "AUDIT_MANIFEST.json"
        manifest = read_json(manifest_path)
        manifest["input_provenance"]["visual_review"]["status"] = "complete"
        write_json(manifest_path, manifest)

        errors, _ = proofcheck.check_audit_finalization(audit)

        self.assertIn(
            "pdf_transcription visual_review.reviewed_pages must be a "
            "nonempty string list",
            errors,
        )
        self.assertIn(
            "pdf_transcription requires a nonempty manually reviewed "
            "theorem/proof inventory",
            errors,
        )
        self.assertIn("completion.inventory_reviewed must be true", errors)

    def test_portable_latex_detects_late_resolution_of_missing_input(
        self,
    ) -> None:
        project = self.source_dir / "portable project"
        project.mkdir()
        main = project / "main.tex"
        main.write_text(
            "\\input{late}\n"
            "\\newtheorem{lemma}{Lemma}\n"
            "\\begin{lemma}\\label{lem:late}\n$x=x$.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nBy reflexivity.\n\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        audit = self.base / "portable-late-input-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                self.scaffold_args(
                    audit,
                    paper=main,
                    portable_sources=True,
                )
            )
        manifest = read_json(audit / "AUDIT_MANIFEST.json")
        self.assertEqual(
            [], proofcheck.source_snapshot_freshness_errors(audit, manifest)
        )

        bundled_main = proofcheck.resolve_stored_path(
            manifest["paper_file"], audit
        )
        bundled_late = bundled_main.parent / "late.tex"
        bundled_late.write_text(
            "\\newcommand{\\latefact}{available}\n",
            encoding="utf-8",
            newline="\n",
        )

        freshness_errors = proofcheck.source_snapshot_freshness_errors(
            audit, manifest
        )
        self.assertTrue(
            any(
                "Source closure has new or unrecorded files" in error
                and str(bundled_late) in error
                for error in freshness_errors
            ),
            freshness_errors,
        )
        finalization_errors, _ = proofcheck.check_audit_finalization(audit)
        self.assertTrue(
            any(
                "Source closure has new or unrecorded files" in error
                for error in finalization_errors
            ),
            finalization_errors,
        )

    def test_portable_latex_requires_root_covering_relative_include(
        self,
    ) -> None:
        common_root = self.source_dir / "cross-directory project"
        manuscript_dir = common_root / "manuscript"
        shared_dir = common_root / "shared"
        manuscript_dir.mkdir(parents=True)
        shared_dir.mkdir()
        main = manuscript_dir / "main.tex"
        shared = shared_dir / "foo.tex"
        main.write_text(
            "\\input{../shared/foo}\n"
            "\\newtheorem{lemma}{Lemma}\n"
            "\\begin{lemma}\\label{lem:shared}\n$x=x$.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nBy reflexivity.\n\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        shared.write_text(
            "\\newcommand{\\sharedfact}{available}\n",
            encoding="utf-8",
            newline="\n",
        )
        narrow_output = self.base / "narrow-root-audit"

        with self.assertRaisesRegex(
            ValueError, "outside.*project_root|broader --project-root"
        ):
            proofcheck.cmd_scaffold(
                self.scaffold_args(
                    narrow_output,
                    paper=main,
                    portable_sources=True,
                    project_root=manuscript_dir,
                )
            )
        self.assertFalse(narrow_output.exists())
        self.assertEqual(
            [],
            list(
                narrow_output.parent.glob(
                    f".{narrow_output.name}.*.proofcheck.stage"
                )
            ),
        )

        portable = self.base / "broad-root-audit"
        with contextlib.redirect_stdout(io.StringIO()):
            proofcheck.cmd_scaffold(
                self.scaffold_args(
                    portable,
                    paper=main,
                    portable_sources=True,
                    project_root=common_root,
                )
            )
        manifest = read_json(portable / "AUDIT_MANIFEST.json")
        locked_paths = {
            proofcheck.resolve_stored_path(row["file"], portable)
            for row in manifest["source_snapshot"]["files"]
        }
        self.assertEqual(2, len(locked_paths))
        self.assertTrue(all(path.is_file() for path in locked_paths))

        main.unlink()
        shared.unlink()
        moved = self.base / "relocated broad-root audit"
        portable.rename(moved)
        status, result = self.parse_and_run(
            ["status", "--root", str(moved)]
        )
        self.assertEqual(0, status)
        self.assertEqual("healthy_wip", result["workflow_state"])
        self.assertEqual([], result["progress"]["drift"])

    def test_portable_latex_rejects_absolute_input_without_residue(
        self,
    ) -> None:
        project = self.source_dir / "absolute-input-project"
        manuscript_dir = project / "manuscript"
        shared_dir = project / "shared"
        manuscript_dir.mkdir(parents=True)
        shared_dir.mkdir()
        shared = shared_dir / "absolute.tex"
        shared.write_text(
            "\\newcommand{\\absolutefact}{available}\n",
            encoding="utf-8",
            newline="\n",
        )
        main = manuscript_dir / "main.tex"
        main.write_text(
            f"\\input{{{shared.resolve().as_posix()}}}\n"
            "\\newtheorem{lemma}{Lemma}\n"
            "\\begin{lemma}\\label{lem:absolute}\n$x=x$.\n"
            "\\end{lemma}\n"
            "\\begin{proof}\nBy reflexivity.\n\\end{proof}\n",
            encoding="utf-8",
            newline="\n",
        )
        output = self.base / "absolute-input-audit"

        with self.assertRaisesRegex(
            ValueError,
            "absolute or otherwise nonrelocatable inclusion after bundling",
        ):
            proofcheck.cmd_scaffold(
                self.scaffold_args(
                    output,
                    paper=main,
                    portable_sources=True,
                    project_root=project,
                )
            )

        self.assertFalse(output.exists())
        self.assertEqual(
            [],
            list(output.parent.glob(f".{output.name}.*.proofcheck.stage")),
        )

    def test_interrupted_scaffold_removes_staging_workspace(self) -> None:
        output = self.base / "interrupted audit"
        original = proofcheck.atomic_write_json
        calls = 0

        def interrupt_third_write(path: Path, value: object) -> None:
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError("simulated scaffold interruption")
            original(path, value)

        with mock.patch.object(
            proofcheck,
            "atomic_write_json",
            side_effect=interrupt_third_write,
        ):
            with self.assertRaisesRegex(
                OSError, "simulated scaffold interruption"
            ):
                proofcheck.cmd_scaffold(
                    self.scaffold_args(output, portable_sources=True)
                )

        self.assertFalse(output.exists())
        self.assertEqual(
            [],
            list(output.parent.glob(f".{output.name}.*.proofcheck.stage")),
        )

    def test_atomic_text_write_preserves_previous_committed_bytes(self) -> None:
        target = self.base / "atomic state.json"
        target.write_text("old committed bytes\n", encoding="utf-8")

        with mock.patch.object(
            proofcheck.os,
            "replace",
            side_effect=OSError("simulated commit interruption"),
        ):
            with self.assertRaisesRegex(
                OSError, "simulated commit interruption"
            ):
                proofcheck.atomic_write_text(target, "new incomplete bytes\n")

        self.assertEqual(
            "old committed bytes\n", target.read_text(encoding="utf-8")
        )

    def test_cross_drive_absolute_fallback_uses_posix_serialization(self) -> None:
        with mock.patch.object(
            proofcheck.os.path,
            "relpath",
            side_effect=ValueError("different drives"),
        ):
            stored = proofcheck.relative_or_absolute(self.paper, self.base)

        self.assertEqual(self.paper.resolve().as_posix(), stored)
        self.assertNotIn("\\", stored)


if __name__ == "__main__":
    unittest.main()
