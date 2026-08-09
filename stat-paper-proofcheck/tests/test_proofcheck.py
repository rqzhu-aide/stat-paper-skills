from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


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
                "lines": [2, 4],
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
                "lines": [5, 5],
                "kind": "other",
                "status": "non_substantive",
                "issue_ids": [],
            },
            {
                "id": "S003",
                "lines": [6, 6],
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
                "lines": [7, 7],
                "kind": "other",
                "status": "non_substantive",
                "issue_ids": [],
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
            "## Independent critical-path challenge\n\n"
            "| Result | Challenge status | Independence level | Challenger verdict | Reconciled verdict | Disagreements | Resolution | Artifact |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| lem:main | agreed | fresh_context_same_model | verified | verified | none | none | audit/05_adversarial/lem-main-challenge.md |\n\n"
            "## Issue summary\n\nNo issues.\n\n"
            "## Method-interface findings\n\nNone.\n\n"
            "## Proposed repairs\n\nNone.\n\n"
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
        prior["obligation"]["conclusions"][0]["source_spans"] = [
            dict(prior_span)
        ]
        prior_step = json.loads(json.dumps(prior["steps"][2]))
        prior_step["id"] = "S001"
        prior_step["lines"] = [1, 1]
        prior["steps"] = [prior_step]
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
        return prior_path, use

    def install_external_dependency(self, ledger_path: Path) -> tuple[Path, dict]:
        source_path = self.base / "external-reflexivity.txt"
        source_path.write_text(
            "External Result 1\nFor every real x, x equals x.\n",
            encoding="utf-8",
            newline="\n",
        )
        exact_statement = "For every real x, x equals x."
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
            "needed_form": "x equals x",
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
        return source_path, use

    def install_canonical_issue(
        self,
        issue: dict,
        *,
        ledger_path: Path | None = None,
        step_index: int = 0,
    ) -> None:
        if ledger_path is not None:
            ledger = read_json(ledger_path)
            ledger["steps"][step_index]["issue_ids"].append(issue["id"])
            write_json(ledger_path, ledger)
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
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        report = report_path.read_text(encoding="utf-8")
        if issue.get("status") in {"open", "deferred"}:
            report = report.replace(
                "- Highest-consequence issue: none",
                f"- Highest-consequence issue: {issue['id']}",
            )
        values = proofcheck.canonical_issue_row(issue)
        row = "| " + " | ".join(
            proofcheck.escape_markdown(value) for value in values
        ) + " |"
        report = report.replace(
            "## Issue summary\n\nNo issues.",
            "## Issue summary\n\n"
            "| ID | Severity | Confidence | Status | Finding status | Load-bearing | Finding class | Affected layer | Interface | Estimator target | Implementation inspection | Code to documented estimator | Code to required target | Execution provenance | Affected result | Affected results | Summary |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
            + row,
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
        return {
            "id": issue_id,
            "severity": severity,
            "confidence": "high",
            "status": "open",
            "finding_status": finding_status,
            "scope": "global",
            "load_bearing": load_bearing,
            "location": affected_result,
            "affected_result": affected_result,
            "affected_results": (
                [affected_result]
                if affected_results is None
                else list(affected_results)
            ),
            "summary": summary,
            "evidence": ["The locked audit artifacts record the finding."],
            "downstream_consequences": [
                "The stated affected results require calibrated treatment."
            ],
            "possible_repair": "Resolve the finding and recheck every affected result.",
        }

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
        evidence_and_consequences = (
            "Evidence: "
            + "; ".join(issue["evidence"])
            + " Consequences: "
            + "; ".join(issue["downstream_consequences"])
        )
        row = (
            f"| {issue['id']} | {issue['finding_class']} | {issue['interface_id']} | "
            f"{issue['estimator_target_status']} | "
            f"{issue['implementation_inspection_status']} | "
            f"{issue['code_to_documented_estimator']} | "
            f"{issue['code_to_required_target']} | "
            f"{issue['execution_provenance_status']} | "
            f"{issue['affected_layer']} | "
            f"{proofcheck.escape_markdown(evidence_and_consequences)} |"
        )
        report = report.replace(
            "## Method-interface findings\n\nNone.",
            "## Method-interface findings\n\n"
            "| Issue ID | Finding class | Interface ID | Estimator-target status | Implementation inspection | Code to documented estimator | Code to required target | Execution provenance | Affected layer | Evidence scope and consequence |\n"
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
        ledger = read_json(ledger_path)
        del ledger["evidence_contract_version"]
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("legacy free-text evidence is inspection-only" in error for error in errors),
            errors,
        )

    def test_legacy_ledger_remains_readable_in_nonfinal_mode(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
        del ledger["evidence_contract_version"]
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
        ledger = read_json(ledger_path)
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
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_source_indivisible_chain_requires_controlled_multiline_partition(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
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
        write_json(ledger_path, ledger)
        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertTrue(
            any("source_indivisible_chain needs a valid source_unit_kind" in error for error in errors),
            errors,
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
            any("single_move step must contain exactly one move" in error for error in errors),
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
        write_json(ledger_dir / "lem-conditional.ledger.json", conditional)

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

    def test_checkpoint_and_verbose_status_are_registered_in_the_cli(self) -> None:
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

        self.assertIs(proofcheck.cmd_checkpoint, checkpoint.func)
        self.assertEqual("lem:main", checkpoint.active_unit)
        self.assertFalse(checkpoint.clear_active_unit)
        self.assertTrue(status.verbose)

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
        errors, summary = proofcheck.check_ledger_data(ledger_path, False)
        self.assertEqual([], errors)
        self.assertEqual("draft", summary["validation_mode"])
        self.assertEqual(
            "inspection_only",
            summary["validation_scope"]["local_record_integrity"],
        )

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

    def test_resolved_interface_contract_detects_semantic_span_drift(self) -> None:
        self.make_complete_audit()
        record = self.make_interface_record()
        record["issue_ids"] = ["I-001"]
        manifest = read_json(self.audit / "AUDIT_MANIFEST.json")
        issue = {
            "id": "I-001",
            "severity": "S3",
            "confidence": "high",
            "status": "resolved",
            "finding_status": "resolved",
            "scope": "global",
            "load_bearing": False,
            "interface_id": "MI-001",
            "finding_class": "exposition_ambiguity",
            "affected_layer": "specification",
            "evidence_class": "observed",
            "estimator_target_status": "match",
            "implementation_inspection_status": "inspected",
            "code_to_documented_estimator": "consistent",
            "code_to_required_target": "consistent",
            "execution_provenance_status": "not_checked",
            "location": "paper.tex:2-4",
            "affected_result": "lem:main",
            "affected_results": ["lem:main"],
            "summary": "The interface wording was clarified.",
            "evidence": ["paper.tex:2-4"],
            "resolution_evidence_needed": ["State both fitting laws."],
            "downstream_consequences": ["none identified"],
            "possible_repair": "Clarification inserted.",
            "resolution": "The fitting laws are now explicit.",
            "source_revision": "test snapshot",
            "recheck_evidence": ["The target relation was reconstructed."],
            "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
            "rechecked_units": ["lem:main"],
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
        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            evidence_base=self.audit,
            interfaces={"MI-001": record},
            source_snapshot_id=manifest["source_snapshot"]["sha256"],
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
            "| lem:main | agreed | fresh_context_same_model | verified | verified |",
            "| lem:main | agreed | fresh_context_same_model | incorrect | verified |",
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

        self.assertIn("Finding status", summary)
        self.assertIn("Affected results", summary)
        self.assertIn("defect", summary)
        self.assertIn("lem:main, lem:prior", summary)

    def test_non_load_bearing_issue_remains_root_only(self) -> None:
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
            in_scope=["lem:main", "lem:prior"],
            reverse_graph=reverse_graph,
        )
        self.assertEqual([], errors)

        issue["affected_results"] = ["lem:main", "lem:prior"]
        errors, _ = proofcheck.validate_issues(
            [issue],
            set(),
            True,
            in_scope=["lem:main", "lem:prior"],
            reverse_graph=reverse_graph,
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

    def test_issue_summary_row_escapes_newline_and_vertical_bar(self) -> None:
        self.make_complete_audit()
        issue = self.make_global_issue(
            load_bearing=False,
            severity="S3",
            summary="The first line\nand the second | clause form one summary.",
        )
        self.install_canonical_issue(issue)

        errors, _ = proofcheck.check_audit_finalization(self.audit)
        report_path = self.audit / "audit" / "06_reports" / "FINAL_REPORT.md"
        section = proofcheck.report_section(
            report_path.read_text(encoding="utf-8"),
            "## Issue summary",
        )
        rows = proofcheck.markdown_table_rows(section or "")

        self.assertEqual([], errors)
        self.assertEqual(17, len(rows[2]))
        self.assertEqual(
            "The first line and the second | clause form one summary.",
            rows[2][-1],
        )

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

        step = ledger["steps"][2]
        step["restatement"] = second["claim"]
        step["checks"]["atomicity"] = {
            "status": "source_indivisible_chain",
            "source_unit_kind": "one_line",
            "partition_evidence": (
                "The source line supports the reflexive equality and its "
                "equivalent verbal conclusion."
            ),
            "evidence": "Two conclusion claims are recorded as separate moves.",
        }
        step["inference"]["moves"].append(
            {
                "id": "M002",
                "claim": second["claim"],
                "rule": "Equivalent restatement",
                "premise_ids": [],
                "prior_move_ids": ["M001"],
                "justification": (
                    "The second conclusion is the stated verbal form of M001."
                ),
            }
        )
        step["inference"]["conclusion_move"] = "M002"
        second_result = json.loads(
            json.dumps(ledger["review"]["conclusion_results"][0])
        )
        second_result["conclusion_id"] = "C002"
        second_result["support"] = {"step_id": "S003", "move_id": "M002"}
        ledger["review"]["conclusion_results"].append(second_result)
        ledger["review"]["conclusion_step_id"] = ""
        write_json(ledger_path, ledger)

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
        step = ledger["steps"][2]
        step["checks"]["atomicity"] = {
            "status": "source_indivisible_chain",
            "source_unit_kind": "one_line",
            "partition_evidence": (
                "The source line contains a domain observation followed by "
                "the equality conclusion."
            ),
            "evidence": "The two moves form one source-indivisible chain.",
        }
        step["inference"] = {
            "moves": [
                {
                    "id": "M001",
                    "claim": "x lies in the real-number equality domain",
                    "rule": "Domain extraction",
                    "premise_ids": ["P001"],
                    "prior_move_ids": [],
                    "justification": "P001 quantifies x over the real numbers.",
                },
                {
                    "id": "M002",
                    "claim": step["restatement"],
                    "rule": "Reflexivity of equality",
                    "premise_ids": [],
                    "prior_move_ids": ["M001"],
                    "justification": "Reflexivity applies on the established domain.",
                },
            ],
            "conclusion_move": "M002",
        }
        step["side_conditions"] = [
            {
                "id": "SC001",
                "generated_by": "M002",
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
                            "kind": "inference_move",
                            "reference": "M001",
                            "contribution": (
                                "M001 specializes the domain fact to this x."
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
        ledger["review"]["conclusion_results"][0]["support"]["move_id"] = "M002"
        write_json(ledger_path, ledger)

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
        self.assertEqual([], errors)

    def test_controlled_multiline_atomicity_requires_full_source_partition(self) -> None:
        ledger_path = self.make_complete_audit()
        ledger = read_json(ledger_path)
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

        errors, _ = proofcheck.check_ledger_data(ledger_path, True)
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


if __name__ == "__main__":
    unittest.main()
