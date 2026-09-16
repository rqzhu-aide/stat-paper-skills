"""Controller assignments: bounded complete context and per-task mathematical inputs."""
from __future__ import annotations

import unittest
from unittest import mock

import support
from support import R, TempCase, edit

from paper_core import bindings, packets
from paper_core.canonical import canonical_bytes
from paper_core.errors import ConflictError, InvalidRequest
from paper_core.validation import State


def task(id, target, kind, *, role="primary", action="check", prerequisites=(), **extra):
    return dict(id=id, target=target, kind=kind, role=role, action=action,
                prerequisite_ids=list(prerequisites), draft_refs=[], judgment_refs=[],
                owner=R("items", "itm_thm"), argument=R("arguments", "arg_thm"), **extra)


def selection(*units):
    """One tuple of tasks represents a whole context unit, not a model invocation."""
    return {"units": [{"id": f"unit_{i}", "task_ids": [t["id"] for t in ts],
                       "prerequisite_unit_ids": [f"unit_{i-1}"] if i else []}
                      for i, ts in enumerate(units)],
            "tasks": [t for ts in units for t in ts],
            "context": {"owner": R("items", "itm_thm"), "argument": R("arguments", "arg_thm")},
            "conditional_on_task_ids": [], "analysis_complete": True}


def record_keys(packet):
    return {(entry["ref"]["collection"], entry["ref"]["id"]) for entry in packet["records"]}


class WorkPacketTests(TempCase):
    def setUp(self):
        super().setUp()
        self.fx = self.fixture().audit()
        self.application = task("task_app", R("uses", "use_lem_thm"), "application")
        self.derivation = task("task_der", R("groups", "grp_thm"), "derivation")

    def prepare(self, db, selected=None, **kwargs):
        return packets.prepare_assignment(db, audit_id="aud_1", mode=kwargs.pop("mode", "primary"),
            selection=selected or selection((self.application, self.derivation)), **kwargs)

    def test_one_unit_carries_all_joint_inputs_but_not_the_suppliers_proof(self):
        with self.fx.open() as db:
            self.fx.apply(db, [
                self.fx.item_edit("itm_second", "lemma", "Lemma 2", "anc_lem", "anc_lem_proof"),
                edit("create", "uses", "use_second", dict(db.head("uses", "use_lem_thm").body,
                                                          **{"from": R("items", "itm_second")}))])
            result = self.prepare(db)
            keys = record_keys(result["packet"])
            self.assertTrue(result["prepared"])
            self.assertTrue({("uses", "use_lem_thm"), ("uses", "use_second"),
                             ("items", "itm_lem"), ("items", "itm_second"),
                             ("anchors", "anc_thm_proof")} <= keys)
            self.assertNotIn(("anchors", "anc_lem_proof"), keys)
            self.assertNotIn(("arguments", "arg_lem"), keys)
            self.assertNotIn(("groups", "grp_lem"), keys)

    def test_explicit_proof_borrowing_adds_the_borrowed_proof(self):
        with self.fx.open() as db:
            use = db.head("uses", "use_lem_thm")
            self.fx.apply(db, [edit("replace", "uses", use.id, dict(use.body, type="proof_argument"), use.version)])
            result = self.prepare(db)
            self.assertIn(("anchors", "anc_lem_proof"), record_keys(result["packet"]))
            application = result["manifest"]["work"]["tasks"][0]
            self.assertTrue(any(r["ref"]["id"] == "anc_lem_proof" for r in application["consumed_inputs"]))

    def test_coherent_assignment_includes_successor_composition_with_its_own_slot(self):
        composition = task("task_comp", R("arguments", "arg_thm"), "composition",
                           prerequisites=("task_app", "task_der"))
        with self.fx.open() as db:
            result = self.prepare(db, selection((self.application, self.derivation), (composition,)))
            self.assertEqual(["task_app", "task_der", "task_comp"], result["assigned_task_ids"])
            self.assertEqual(2, len(result["selected_unit_ids"]))
            self.assertEqual(3, len(result["manifest"]["work"]["tasks"]))
            self.assertEqual(["task_app", "task_der", "task_comp"],
                             [t["id"] for t in result["packet"]["instructions"]["tasks"]])
            self.assertNotIn("work", result["packet"])
            self.assertEqual(result["manifest"], db.packet(result["packet_id"])["manifest"])

    def test_task_bindings_do_not_consume_sibling_composition_or_upstream_proof(self):
        composition = task("task_comp", R("arguments", "arg_thm"), "composition")
        with self.fx.open() as db:
            result = self.prepare(db, selection((self.application, self.derivation), (composition,)))
            app, der, comp = result["manifest"]["work"]["tasks"]
            app_keys = {(r["ref"]["collection"], r["ref"]["id"]) for r in app["consumed_inputs"]}
            self.assertNotIn(("arguments", "arg_thm"), app_keys)
            self.assertNotIn(("anchors", "anc_lem_proof"), app_keys)
            self.assertIn(("arguments", "arg_thm"),
                          {(r["ref"]["collection"], r["ref"]["id"]) for r in comp["consumed_inputs"]})

    def test_unrelated_thousand_sibling_groups_do_not_enlarge_local_packet(self):
        with self.fx.open() as db:
            before = self.prepare(db)
            self.fx.apply(db, [self.fx.group_edit(f"grp_sibling_{i}", "arg_thm", "itm_thm", "anc_thm_proof")
                               for i in range(1000)])
            after = self.prepare(db)
            self.assertEqual(record_keys(before["packet"]), record_keys(after["packet"]))
            self.assertEqual(before["size"], after["size"])

    def test_only_selected_audit_context_is_collected(self):
        with self.fx.open() as db:
            original = db.head("audits", "aud_1")
            self.fx.apply(db, [edit("create", "audits", "aud_unrelated", dict(original.body))], mode="primary")
            result = self.prepare(db)
            self.assertNotIn(("audits", "aud_unrelated"), record_keys(result["packet"]))

    def test_exact_worker_size_is_the_size_of_persisted_bytes(self):
        with self.fx.open() as db:
            result = self.prepare(db)
            raw = db.get_blob(db.packet(result["packet_id"])["payload_sha256"])
            self.assertEqual(canonical_bytes(result["packet"]), raw)
            self.assertEqual(len(raw), result["size"]["worker_bytes"])

    def test_oversized_first_unit_stores_nothing_and_has_actionable_diagnostic(self):
        with self.fx.open() as db:
            before = db.conn.execute("SELECT COUNT(*) FROM packets").fetchone()[0]
            result = self.prepare(db, max_bytes=200)
            self.assertFalse(result["prepared"])
            self.assertEqual("OVERSIZED_CONTEXT", result["diagnostics"][0]["code"])
            self.assertGreater(result["diagnostics"][0]["measured_or_lower_bound_bytes"], 200)
            self.assertEqual(before, db.conn.execute("SELECT COUNT(*) FROM packets").fetchone()[0])

    def test_fit_keeps_complete_first_unit_and_defers_complete_next_unit(self):
        fidelity = task("task_source", R("items", "itm_lem"), "source_fidelity", action="compare_source")
        with self.fx.open() as db:
            one = self.prepare(db, selection((fidelity,)))
            result = self.prepare(db, selection((fidelity,), (self.application, self.derivation)),
                                  max_bytes=one["size"]["worker_bytes"] + 10)
            self.assertTrue(result["prepared"])
            self.assertEqual(["task_source"], result["assigned_task_ids"])
            self.assertEqual(["unit_1"], result["deferred"])
            self.assertFalse(result["packet"]["truncated"])

    def test_record_ceiling_is_enforced_before_a_partial_packet_is_saved(self):
        with self.fx.open() as db, mock.patch.object(packets, "MAX_WORK_RECORDS", 3):
            result = self.prepare(db)
            self.assertFalse(result["prepared"])
            self.assertEqual("OVERSIZED_CONTEXT", result["diagnostics"][0]["code"])

    def test_invalid_byte_limits_and_excess_units_are_rejected(self):
        with self.fx.open() as db:
            for limit in (0, -1, True, 1048577):
                with self.subTest(limit=limit), self.assertRaises(InvalidRequest):
                    self.prepare(db, max_bytes=limit)
            with self.assertRaises(InvalidRequest):
                self.prepare(db, selection(*[(self.application,)] * 11))

    def test_changed_selection_snapshot_is_not_prepared(self):
        with self.fx.open() as db:
            selected = selection((self.application,))
            selected["revision"] = db.max_revision() - 1
            with self.assertRaises(ConflictError):
                self.prepare(db, selected)

    def test_incomplete_analysis_never_dispatches_partial_graph(self):
        with self.fx.open() as db:
            selected = selection((self.application,))
            selected["analysis_complete"] = False
            result = self.prepare(db, selected)
            self.assertFalse(result["prepared"])
            self.assertEqual("ANALYSIS_INCOMPLETE", result["diagnostics"][0]["code"])

    def test_generic_extension_refuses_work_packet_without_losing_whitelist(self):
        with self.fx.open() as db:
            result = self.prepare(db)
            with self.assertRaises(InvalidRequest) as caught:
                packets.get_packet(db, extend=result["packet_id"], request={"targets": [],
                    "source_anchor_ids": [], "source_paths": [], "reason": "more context"})
            self.assertEqual("WORK_PACKET_EXTENSION", caught.exception.code)

    def test_independent_worker_receives_no_primary_task_outline(self):
        independent = task("private_obligation", R("arguments", "arg_thm"), "composition", role="independent")
        with self.fx.open() as db:
            result = self.prepare(db, selection((independent,)), mode="independent")
            raw = canonical_bytes(result["packet"]).decode("utf-8")
            self.assertEqual([], packets.blinding_violations(result["packet"]))
            for hidden in ("private_obligation", "grp_thm", "unit_0", "conditional_on_task_ids"):
                self.assertNotIn(hidden, raw)
            self.assertIn("work", result["manifest"])
            self.assertEqual("aud_1", result["packet"]["declared_scope"]["audit_id"])

    def test_blinding_validator_rejects_outline_even_without_forbidden_records(self):
        self.assertTrue(packets.blinding_violations({"records": [], "work": {}}))
        self.assertTrue(packets.blinding_violations({"records": [], "instructions": {"tasks": []}}))

    def test_independent_part_can_use_the_explicit_parent_audit(self):
        with self.fx.open() as db:
            self.fx.apply(db, [edit("create", "parts", "prt_thm", {"item_id": "itm_thm", "label": "Part 1",
                "statement": {"form": "verbatim", "text": "Part statement"},
                "passages": [{"role": "statement", "anchor_id": "anc_thm"}], "scope_id": None,
                "origin": "source"})])
            independent = task("private_part", R("parts", "prt_thm"), "composition", role="independent")
            result = self.prepare(db, selection((independent,)), mode="independent")
            self.assertTrue(result["prepared"])
            self.assertEqual([R("parts", "prt_thm")], result["packet"]["targets"])


class WorkBindingTests(TempCase):
    def setUp(self):
        super().setUp()
        self.fx = self.fixture().audit()
        self.application = task("task_app", R("uses", "use_lem_thm"), "application")
        self.derivation = task("task_der", R("groups", "grp_thm"), "derivation")

    prepare = WorkPacketTests.prepare

    def test_caption_and_unconsumed_proof_changes_do_not_stale_application(self):
        with self.fx.open() as db:
            result = self.prepare(db)
            spec = result["manifest"]["work"]["tasks"][0]
            lemma = db.head("items", "itm_lem")
            self.fx.apply(db, [edit("replace", "items", lemma.id,
                dict(lemma.body, caption="Changed caption", passages=lemma.body["passages"] +
                     [{"role": "evidence", "anchor_id": "anc_thm_proof"}]), lemma.version)])
            self.assertEqual({"records": [], "relations": []},
                bindings.task_binding_changes(State(db, []), spec, packet=result["manifest"]))

    def test_consumed_statement_change_is_reported(self):
        with self.fx.open() as db:
            result = self.prepare(db)
            spec = result["manifest"]["work"]["tasks"][0]
            lemma = db.head("items", "itm_lem")
            self.fx.apply(db, [edit("replace", "items", lemma.id,
                dict(lemma.body, statement={"form": "verbatim", "text": "Different statement"}), lemma.version)])
            changes = bindings.task_binding_changes(State(db, []), spec, packet=result["manifest"])
            self.assertTrue(any(r["ref"]["id"] == "itm_lem" for r in changes["records"]))

    def test_cosmetic_group_member_version_does_not_defeat_facet_comparison(self):
        with self.fx.open() as db:
            result = self.prepare(db)
            spec = result["manifest"]["work"]["tasks"][0]
            use = db.head("uses", "use_lem_thm")
            self.fx.apply(db, [edit("replace", "uses", use.id, dict(use.body, uncertainty="editorial note"), use.version)])
            self.assertEqual({"records": [], "relations": []},
                bindings.task_binding_changes(State(db, []), spec, packet=result["manifest"]))

    def test_added_joint_input_changes_membership(self):
        with self.fx.open() as db:
            result = self.prepare(db)
            spec = result["manifest"]["work"]["tasks"][0]
            self.fx.apply(db, [self.fx.item_edit("itm_second", "lemma", "Lemma 2", "anc_lem", "anc_lem_proof"),
                edit("create", "uses", "use_extra", dict(db.head("uses", "use_lem_thm").body,
                                                          **{"from": R("items", "itm_second")}))])
            changes = bindings.task_binding_changes(State(db, []), spec, packet=result["manifest"])
            self.assertTrue(any(r["relation"] == "uses_in_group" for r in changes["relations"]))

    def test_extra_evidence_requires_original_packet_provenance(self):
        with self.fx.open() as db:
            result = self.prepare(db)
            spec = result["manifest"]["work"]["tasks"][0]
            self.assertEqual([], bindings.task_binding_changes(State(db, []), spec,
                evidence_refs=["anc_thm_proof"], packet=result["manifest"])["records"])
            changes = bindings.task_binding_changes(State(db, []), spec,
                evidence_refs=["anc_lem_proof"], packet=result["manifest"])
            self.assertTrue(changes["records"])

    def test_prospective_composition_binds_generated_checks_but_application_does_not(self):
        composition = task("task_comp", R("arguments", "arg_thm"), "composition")
        with self.fx.open() as db:
            result = self.prepare(db, selection((self.application, self.derivation), (composition,)))
            self.fx.apply(db, [self.fx.check_edit("chk_new_der", R("groups", "grp_thm"), "derivation")], mode="primary")
            check = self.fx.check_edit("chk_comp", R("arguments", "arg_thm"), "composition")["body"]
            bound = bindings.compute_bindings(State(db, []), "checks", check,
                                               packet=db.packet(result["packet_id"]))
            self.assertTrue(any(r["ref"]["id"] == "chk_new_der" for r in bound["records"]))
            app = self.fx.check_edit("chk_app", R("uses", "use_lem_thm"), "application")["body"]
            app_bound = bindings.compute_bindings(State(db, []), "checks", app,
                                                   packet=db.packet(result["packet_id"]))
            self.assertFalse(any(r["ref"]["collection"] == "checks" for r in app_bound["records"]))


if __name__ == "__main__":
    unittest.main()
