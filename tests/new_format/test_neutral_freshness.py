"""A source-only judgment keeps the setup actually delivered to its reviewer."""
from unittest import mock

from support import R, TempCase, edit
from test_review import entry, judgment, mapping_request, source_target, worker_response
from paper_core import assessment, controller, packets, review
from paper_core.canonical import canonical_bytes
from paper_core.errors import ConflictError
from paper_core.bindings import binding_changes
from paper_core.validation import State


class NeutralFreshnessTests(TempCase):
    def setUp(self):
        super().setUp()
        self.fx = self.fixture().primary()
        self.db = self.fx.open()
        self.addCleanup(self.db.close)

    def prepare(self, target="itm_lem"):
        result = controller.prepare_work(self.db, audit_id="aud_1", mode="independent", focus=R("items", target))
        self.assertTrue(result["prepared"], result)
        return result

    def submit(self, prepared, name="lem"):
        worker = worker_response(prepared["packet_id"], [judgment(source_target(f"anc_{name}_proof", "The written argument"),
                                                               evidence=(f"anc_{name}_proof",))])
        envelope = {"contract_version": 4, "request_id": self.fx.request_id(), "packet_id": prepared["packet_id"],
            "rebase_packet_id": None, "reviewer": "checker-A", "qualification_id": "qua_r1",
            "exposure": "source_only", "exposure_note": "Fresh source-only reviewer."}
        return controller.submit_work(self.db, envelope_bytes=canonical_bytes(envelope), response_bytes=canonical_bytes(worker))

    def mapping(self, result, name="lem"):
        private = self.fx.packet(self.db, f"items:itm_{name}", mode="reconcile")
        return mapping_request(self.fx, private["packet_id"], result["response_id"], [entry(0, R("arguments", f"arg_{name}"))])

    def change_setup(self):
        scope = self.db.head("scopes", "scp_plain")
        self.fx.apply(self.db, [self.fx.item_edit("itm_setup", "assumption", "Previously uninspected setup", "anc_thm", "anc_thm_proof"),
            edit("replace", "scopes", scope.id, dict(scope.body, assumptions=[R("items", "itm_setup")]), scope.version)])

    def freshness(self, check):
        snapshot = assessment.Snapshot(self.db, self.db.max_revision())
        return assessment.judgment_freshness(snapshot, self.db.head("checks", check), superseded=False)

    def test_setup_change_between_prepare_and_submit_is_not_accepted(self):
        original = self.prepare()
        self.change_setup()
        result = self.submit(original)
        self.assertEqual("conflict", result["state"], result)
        self.assertNotIn("response_id", result, result)
        self.assertIn("setup", result["error"]["message"])

    def test_pending_response_cannot_be_mapped_against_changed_setup(self):
        original = self.prepare()
        result = self.submit(original)
        self.assertIn("response_id", result, result)
        self.change_setup()
        before = self.db.max_revision()
        with self.assertRaises(ConflictError):
            review.map_response(self.db, mapping=self.mapping(result))
        self.assertEqual(before, self.db.max_revision())
        self.assertEqual("needs_revision", self.db.head("responses", result["response_id"]).body["state"])

    def test_primary_rationale_change_does_not_invalidate_source_review_before_mapping(self):
        original = self.prepare()
        group = self.db.head("groups", "grp_lem")
        self.fx.apply(self.db, [edit("replace", "groups", group.id,
            dict(group.body, rationale="Different coordinator exposition of the same source argument"), group.version)])
        result = self.submit(original)
        self.assertIn("response_id", result, result)
        mapped = review.map_response(self.db, mapping=self.mapping(result))
        self.assertEqual("accepted", mapped["state"])
        self.assertEqual("current", self.freshness(mapped["checks"][0]["check_id"])["freshness"])

    def reassign_setup(self, collection, identity):
        record = self.db.head(collection, identity)
        self.fx.apply(self.db, [edit("replace", collection, identity,
                                   dict(record.body, scope_id="scp_new"), record.version)])

    def test_setup_attachments_are_checked_at_submission_and_mapping(self):
        cases = (("groups", "grp_lem", "lem"), ("arguments", "arg_lem", "lem"),
                 ("application_details", "use_lem_thm", "thm"), ("target_specs", "tgt_lem", "lem"))
        for stage in ("submit", "map"):
            for collection, identity, name in cases:
                with self.subTest(stage=stage, collection=collection):
                    self.fx = self.fixture(stage + collection).audit()
                    self.db = self.fx.open()
                    self.addCleanup(self.db.close)
                    self.fx.apply(self.db, [edit("create", "scopes", "scp_new", {
                        "argument_id": "arg_thm" if collection == "application_details" else None,
                        "parent_id": "scp_plain", "assumptions": [], "binders": [],
                        "conditions": ["Additional applicable condition"], "evidence_refs": ["anc_thm"]})])
                    if collection == "application_details":
                        group = self.db.head("groups", "grp_thm")
                        self.fx.apply(self.db, [edit("replace", "groups", group.id,
                            dict(group.body, scope_id="scp_new"), group.version)])
                    self.fx.primary()
                    original = self.prepare("itm_" + name)
                    if name == "lem":
                        self.assertNotIn("anc_thm", [ref["id"] for ref in original["manifest"]["read_set"]])
                    pending = self.submit(original, name) if stage == "map" else None
                    self.reassign_setup(collection, identity)
                    if stage == "submit":
                        result = self.submit(original, name)
                        self.assertEqual("conflict", result["state"], result)
                        self.assertNotIn("response_id", result)
                    else:
                        before = self.db.max_revision()
                        with self.assertRaises(ConflictError):
                            review.map_response(self.db, mapping=self.mapping(pending, name))
                        self.assertEqual(before, self.db.max_revision())

    def test_added_equivalent_inference_keeps_pending_source_review_usable(self):
        original = self.prepare()
        pending = self.submit(original)
        group = self.db.head("groups", "grp_lem")
        self.fx.apply(self.db, [edit("create", "groups", "grp_added", dict(group.body))])
        changes = packets.independent_context_changes(State(self.db, []), original["manifest"])
        self.assertEqual({"records": [], "relations": []}, changes)
        mapped = review.map_response(self.db, mapping=self.mapping(pending))
        self.assertEqual("accepted", mapped["state"])
        check_id = mapped["checks"][0]["check_id"]
        self.fx.apply(self.db, [edit("create", "groups", "grp_later", dict(group.body))])
        self.assertEqual("needs_review", self.freshness(check_id)["freshness"])

    def test_added_inference_with_new_setup_invalidates_pending_source_review(self):
        original = self.prepare()
        pending = self.submit(original)
        group = self.db.head("groups", "grp_lem")
        self.fx.apply(self.db, [edit("create", "scopes", "scp_new", {
            "argument_id": None, "parent_id": None, "assumptions": [], "binders": [],
            "conditions": ["Additional applicable condition"], "evidence_refs": ["anc_thm"]}),
            edit("create", "groups", "grp_added", dict(group.body, scope_id="scp_new"))])
        changes = packets.independent_context_changes(State(self.db, []), original["manifest"])
        self.assertTrue(any(row["relation"] == "groups_in_argument" for row in changes["relations"]))
        with self.assertRaises(ConflictError):
            review.map_response(self.db, mapping=self.mapping(pending))

    def test_historical_selector_entries_keep_recognized_broad_digests(self):
        original = self.prepare()
        for row in original["manifest"]["work"]["source_context_inputs"]:
            row.pop("setup_digest", None)
        binding = packets.independent_context_binding(State(self.db, []), original["manifest"])
        selector = next(row for row in binding["records"] if row["ref"]["id"] == "grp_lem")
        self.assertIn("setup_digest", selector)
        self.assertEqual("inference", selector["facet"])
        group = self.db.head("groups", "grp_lem")
        self.fx.apply(self.db, [edit("replace", "groups", group.id,
            dict(group.body, rationale="Same source, revised coordinator wording"), group.version)])
        self.assertEqual({"records": [], "relations": []}, binding_changes(State(self.db, []), binding))
        broad = dict(selector)
        broad.pop("setup_digest")
        self.assertTrue(binding_changes(State(self.db, []), {"records": [broad], "relations": []})["records"])

    def prepare_old_selector_packet(self, *, omitted_scope=None):
        build, members, scope = packets._assignment_packet, packets._neutral_members, packets._neutral_scope

        def old_build(*args, **kwargs):
            manifest, packet = build(*args, **kwargs)
            manifest["work"].pop("neutral_setup_selection")
            for row in manifest["work"]["source_context_inputs"]:
                row.pop("setup_digest", None)
            return manifest, packet

        def old_members(closure, relation, ref):
            return [] if relation == "target_specs_for_target" else members(closure, relation, ref)

        def old_scope(closure, scope_id):
            return None if scope_id == omitted_scope else scope(closure, scope_id)

        with mock.patch.object(packets, "_assignment_packet", side_effect=old_build), \
                mock.patch.object(packets, "_neutral_members", side_effect=old_members), \
                mock.patch.object(packets, "_neutral_scope", side_effect=old_scope):
            return self.prepare()

    def test_existing_packet_without_missing_exact_setup_remains_usable(self):
        original = self.prepare_old_selector_packet()
        pending = self.submit(original)
        self.assertIn("response_id", pending, pending)
        mapped = review.map_response(self.db, mapping=self.mapping(pending))
        self.assertEqual("accepted", mapped["state"])
        check_id = mapped["checks"][0]["check_id"]
        self.assertEqual(1, self.db.binding("checks", check_id, 1)["bindings"]["neutral_setup_validated"])
        with mock.patch.object(packets, "independent_context_changes", side_effect=AssertionError("already validated")):
            self.assertEqual("current", self.freshness(check_id)["freshness"])

    def assert_legacy_omission_is_rejected(self, original):
        self.assertNotIn("anc_thm", [ref["id"] for ref in original["manifest"]["read_set"]])
        rejected = self.submit(original)
        self.assertEqual("conflict", rejected["state"], rejected)
        self.assertIn("omitted applicable source or setup", rejected["error"]["message"])
        # Emulate a response preserved and later mapped by the previous writer.
        with mock.patch.object(packets, "independent_context_binding", return_value=None):
            pending = self.submit(original)
        self.assertIn("response_id", pending, pending)
        with self.assertRaisesRegex(ConflictError, "omitted applicable source or setup"):
            review.map_response(self.db, mapping=self.mapping(pending))
        with mock.patch.object(packets, "independent_context_binding", return_value=None):
            mapped = review.map_response(self.db, mapping=self.mapping(pending))
        check_id = mapped["checks"][0]["check_id"]
        self.assertNotIn("neutral_setup_validated", self.db.binding("checks", check_id, 1)["bindings"])
        before = self.db.max_revision()
        snapshot = assessment.Snapshot(self.db, before)
        reuse = mock.Mock()
        reuse.get.side_effect = AssertionError("missing independent context cannot use generic source reuse")
        changed = assessment.judgment_freshness(snapshot, self.db.head("checks", check_id),
                                               superseded=False, reuse_index=reuse)
        self.assertEqual("needs_review", changed["freshness"])
        self.assertFalse(changed["reused"])
        self.assertIn("omitted applicable source or setup", str(changed["changes"]))
        self.assertEqual(before, self.db.max_revision())

    def test_existing_packet_with_omitted_exact_setup_requires_new_review(self):
        self.fx = self.fixture("legacy_exact").audit()
        self.db = self.fx.open()
        self.addCleanup(self.db.close)
        spec = self.db.head("target_specs", "tgt_lem")
        self.fx.apply(self.db, [edit("create", "scopes", "scp_exact", {
            "argument_id": None, "parent_id": None, "assumptions": [], "binders": [],
            "conditions": ["Exact setup omitted by the earlier selector"], "evidence_refs": ["anc_thm"]}),
            edit("replace", "target_specs", spec.id, dict(spec.body, scope_id="scp_exact"), spec.version)])
        self.fx.primary()
        original = self.prepare_old_selector_packet()
        self.assert_legacy_omission_is_rejected(original)

    def test_existing_packet_with_omitted_discharged_setup_requires_new_review(self):
        group = self.db.head("groups", "grp_lem")
        self.fx.apply(self.db, [edit("create", "scopes", "scp_discharged", {
            "argument_id": "arg_lem", "parent_id": None, "assumptions": [], "binders": [],
            "conditions": ["An additional premise must be discharged"], "evidence_refs": ["anc_thm"]}),
            edit("replace", "groups", group.id, dict(group.body, discharges=["scp_discharged"]), group.version)])
        original = self.prepare_old_selector_packet(omitted_scope="scp_discharged")
        self.assert_legacy_omission_is_rejected(original)

    def test_existing_mapped_check_keeps_valid_delivered_context_current(self):
        original = self.prepare_old_selector_packet()
        with mock.patch.object(packets, "independent_context_binding", return_value=None):
            pending = self.submit(original)
            mapped = review.map_response(self.db, mapping=self.mapping(pending))
        self.assertEqual("current", self.freshness(mapped["checks"][0]["check_id"])["freshness"])

    def test_existing_mapped_check_rechecks_original_setup_attachment(self):
        original = self.prepare_old_selector_packet()
        self.fx.apply(self.db, [edit("create", "scopes", "scp_new", {
            "argument_id": None, "parent_id": None, "assumptions": [], "binders": [],
            "conditions": ["Additional setup never delivered"], "evidence_refs": ["anc_thm"]})])
        self.reassign_setup("groups", "grp_lem")
        with mock.patch.object(packets, "independent_context_binding", return_value=None):
            pending = self.submit(original)
            mapped = review.map_response(self.db, mapping=self.mapping(pending))
        changed = self.freshness(mapped["checks"][0]["check_id"])
        self.assertEqual("needs_review", changed["freshness"])
        self.assertTrue(any(row["ref"]["id"] == "grp_lem" for row in changed["changes"]["records"]))

    def extra_context(self, original):
        self.fx.apply(self.db, [edit("create", "scopes", "scp_extra", {"argument_id": None, "parent_id": None,
            "assumptions": [], "binders": [], "conditions": [], "evidence_refs": ["anc_thm"]}),
            {**self.fx.item_edit("itm_extra_context", "definition", "Auxiliary definition", "anc_thm", "anc_thm_proof"),
             "body": {**self.fx.item_edit("itm_extra_context", "definition", "Auxiliary definition", "anc_thm", "anc_thm_proof")["body"],
                      "scope_id": "scp_extra"}}])
        return controller.extend_work(self.db, packet_id=original["packet_id"], request={
            "source_refs": [self.db.head("items", "itm_extra_context").pinned], "reason": "Auxiliary definition is needed."})

    def change_extra_setup(self):
        scope = self.db.head("scopes", "scp_extra")
        self.fx.apply(self.db, [edit("replace", "scopes", scope.id, dict(scope.body, conditions=["different regime"]), scope.version)])

    def test_mapped_check_keeps_context_only_setup_binding(self):
        extended = self.extra_context(self.prepare())
        result = self.submit(extended)
        mapped = review.map_response(self.db, mapping=self.mapping(result))
        check_id = mapped["checks"][0]["check_id"]
        bound = self.db.binding("checks", check_id, 1)["bindings"]
        self.assertTrue(any(row["ref"]["id"] == "scp_extra" for row in bound["records"]))
        self.change_extra_setup()
        changed = self.freshness(check_id)
        self.assertEqual("needs_review", changed["freshness"])
        self.assertTrue(any(row["ref"]["id"] == "scp_extra" for row in changed["changes"]["records"]))

    def test_mapped_check_keeps_context_only_exact_setup_selection(self):
        original = self.prepare()
        extended = self.extra_context(original)
        context = self.db.head("items", "itm_extra_context")
        self.fx.apply(self.db, [edit("create", "target_specs", "tgt_extra", {
            "target": context.ref, "statement_ref": context.pinned, "statement": None, "scope_id": "scp_extra",
            "evidence_refs": ["anc_thm"], "state": "draft", "fidelity_ref": None})])
        # An exact specification that adds no source/setup does not demand a new
        # source reading solely because its private record acquired an ID.
        result = self.submit(extended)
        self.assertIn("response_id", result, result)
        renewed = controller.extend_work(self.db, packet_id=self.prepare()["packet_id"], request={
            "source_refs": [context.pinned], "reason": "Auxiliary definition is needed."})
        submitted = self.submit(renewed)
        mapped = review.map_response(self.db, mapping=self.mapping(submitted))
        check_id = mapped["checks"][0]["check_id"]
        bound = self.db.binding("checks", check_id, 1)["bindings"]
        self.assertTrue(any(row["ref"]["id"] == "tgt_extra" and "setup_digest" in row for row in bound["records"]))
        self.fx.apply(self.db, [edit("create", "scopes", "scp_new", {
            "argument_id": None, "parent_id": None, "assumptions": [], "binders": [],
            "conditions": ["Different applicable setup"], "evidence_refs": ["anc_lem"]})])
        self.reassign_setup("target_specs", "tgt_extra")
        changed = self.freshness(check_id)
        self.assertEqual("needs_review", changed["freshness"])
        self.assertTrue(any(row["ref"]["id"] == "tgt_extra" for row in changed["changes"]["records"]))

    def test_context_only_setup_race_is_rechecked_inside_mapping_transaction(self):
        extended = self.extra_context(self.prepare())
        result = self.submit(extended)
        mapping = self.mapping(result)
        authority = self.db.packet(mapping["packet_id"])["manifest"]
        self.assertNotIn("scp_extra", [ref["id"] for ref in authority["read_set"]])
        accept = review.accept
        changed_revision = []

        def interleave(*args, **kwargs):
            self.change_extra_setup()
            changed_revision.append(self.db.max_revision())
            return accept(*args, **kwargs)

        with mock.patch.object(review, "accept", side_effect=interleave):
            with self.assertRaises(ConflictError):
                review.map_response(self.db, mapping=mapping)
        self.assertEqual(changed_revision[0], self.db.max_revision())
        self.assertEqual("needs_revision", self.db.head("responses", result["response_id"]).body["state"])
