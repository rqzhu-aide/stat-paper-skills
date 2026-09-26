"""Prominent reader explanations must faithfully display the pinned evidence in context."""
from copy import deepcopy
import json
import re
import shutil
import subprocess

from support import CORE, R, TempCase, edit
from paper_core import projection, publish
from paper_core.canonical import digest


class ReaderPublicationTests(TempCase):
    def reader_paper(self, *, with_parts=False):
        fixture = self.fixture().primary()
        with fixture.open() as db:
            theorem = db.head("items", "itm_thm")
            setup = db.head("scopes", "scp_plain")
            use = db.head("uses", "use_lem_thm")
            step = fixture.item_edit("itm_step", "intermediate_result", "Internal bound", "anc_thm", "anc_thm_proof")
            step["body"]["owner_id"] = "itm_thm"
            new_statement = {"form": "synopsis", "text": "New synopsis, distinct from the exact audited statement."}
            edits = [
                edit("replace", "items", theorem.id, dict(theorem.body, statement=new_statement,
                    proof_idea=r"Use $a_n \le 1$, then the criterion. Literal <script>alert(1)</script>."), theorem.version),
                fixture.item_edit("itm_setup", "assumption", "Assumption A", "anc_lem", "anc_lem_proof"),
                edit("replace", "scopes", setup.id, dict(setup.body, assumptions=[R("items", "itm_setup")],
                    conditions=[r"$n > 0$"], binders=[{"symbol": "n", "domain": "positive integers", "quantifier": "forall"}]), setup.version),
                edit("replace", "uses", use.id, dict(use.body, reason="Supplies the first bound.", regime=r"$n > 0$"), use.version),
                edit("create", "uses", "use_second", dict(use.body, reason="Supplies a different contribution.", regime=r"$n > 1$")),
                edit("create", "application_details", "use_second", {"use_id": "use_second", "group_id": "grp_thm",
                    "needed_form": {"form": "verbatim", "text": "Lemma 1 text"}, "substitutions": [], "state": "registered"}),
                step,
                edit("create", "uses", "use_internal", dict(use.body, **{"from": R("items", "itm_step")}, reason="Internal step.")),
                edit("create", "application_details", "use_internal", {"use_id": "use_internal", "group_id": "grp_thm",
                    "needed_form": {"form": "transcription", "text": "Internal bound"}, "substitutions": [], "state": "draft"}),
                edit("create", "findings", "fnd_reader", {"audit_id": fixture.audit_id, "target": R("groups", "grp_thm"),
                    "category": "inconclusive", "lifecycle": "open", "description": "The final bound is unable to verify.",
                    "evidence_refs": ["anc_thm_proof"], "check_refs": [], "affected_uses": [],
                    "impact_reason": "The recorded proof needs this bound.", "resolution": None})
            ]
            if with_parts:
                for suffix in ("one", "two"):
                    edits.append(edit("create", "parts", "prt_" + suffix, {"item_id": "itm_thm", "label": "Part " + suffix,
                        "statement": {"form": "transcription", "text": "Distinct assertion " + suffix},
                        "passages": [], "scope_id": None, "origin": "source"}))
            fixture.apply(db, edits)
            dataset = projection.build_projection(db, audit_id=fixture.audit_id)
            envelope = publish.render_input(db, dataset, release=False, source_identity="reader-test")
        return dataset, envelope

    def render(self, envelope, name="reader"):
        node = shutil.which("node")
        if not node:
            self.skipTest("shared Node is unavailable")
        source, output = self.path(name + ".json"), self.path(name + ".html")
        source.write_text(json.dumps(envelope), encoding="utf-8")
        result = subprocess.run([node, str(CORE / "renderer" / "render_projection.mjs"), str(source), str(output)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return output.read_bytes()

    @staticmethod
    def fields(page, *, context=None, field=None):
        pattern = rb'<(?P<tag>div|span)[^>]*data-reader-field="[^"]+"[^>]*>.*?</(?P=tag)>'
        rows = [match[0] for match in re.finditer(pattern, page, flags=re.S)]
        if context:
            rows = [row for row in rows if f'data-reader-context="{context}"'.encode() in row]
        if field:
            rows = [row for row in rows if f'data-reader-field="{field}"'.encode() in row]
        return rows

    def test_reader_displays_pinned_claim_strategy_contexts_and_unresolved_evidence(self):
        dataset, envelope = self.reader_paper()
        page = self.render(envelope)
        self.assertEqual(publish.mechanical_acceptance(page, dataset)["status"], "pass")
        exact = [row for row in self.fields(page, context="target:0", field="statement.text")
                 if b'data-reader-detail="item:itm_thm"' in row]
        self.assertEqual(len(exact), 1)
        self.assertIn(b'data-reader-ref="items:itm_thm:1"', exact[0])
        self.assertIn(b"Theorem 1 text", exact[0])
        strategy = self.fields(page, context="strategy", field="proof_idea")
        self.assertEqual(len(strategy), 1)
        self.assertIn(b"<math", strategy[0])
        self.assertNotIn(b"<script>", strategy[0])
        self.assertIn(b"&lt;script&gt;", strategy[0])
        self.assertIn(b"Proof-strategy summary not recorded", page)
        self.assertIn(b"The final bound is unable to verify.", page)
        apps = dataset["details"]["item:itm_thm"]["reader"]["applications"]
        self.assertEqual(len(apps), 3)
        self.assertFalse(any("use_internal" in edge["primary_use_ids"] for edge in dataset["connections"]))

    def test_overview_tampering_fails_even_with_intact_hidden_record_copies(self):
        dataset, envelope = self.reader_paper()
        page = self.render(envelope)
        self.assertEqual(publish.mechanical_acceptance(page, dataset)["status"], "pass")
        for context, field in (("strategy", "proof_idea"), ("target:0", "statement.text"),
                               (None, "regime"), (None, "description"), (None, "conditions.0")):
            row = self.fields(page, context=context, field=field)[0]
            with self.subTest(context=context, field=field):
                altered = re.sub(rb'>.*</div>$', b'>Altered text</div>', row, flags=re.S)
                for replacement in (altered, b"", b"<template>" + row + b"</template>"):
                    result = publish.mechanical_acceptance(page.replace(row, replacement, 1), dataset)
                    self.assertEqual(result["status"], "fail", result)
        reasons = [row for row in self.fields(page, field="reason") if b'data-reader-detail="item:itm_thm"' in row]
        self.assertGreaterEqual(len(reasons), 2)
        text_a = re.search(rb'>(.*)</div>$', reasons[0], re.S)[1]
        text_b = re.search(rb'>(.*)</div>$', reasons[1], re.S)[1]
        altered = page.replace(reasons[0], reasons[0].replace(text_a, text_b), 1)
        self.assertEqual(publish.mechanical_acceptance(altered, dataset)["status"], "fail")
        # Correct source markers moving together must still belong to the correct supplier row.
        swapped = page.replace(reasons[0], b"READER_SWAP", 1).replace(reasons[1], reasons[0], 1).replace(b"READER_SWAP", reasons[1], 1)
        self.assertEqual(publish.mechanical_acceptance(swapped, dataset)["status"], "fail")
        wrong_supplier = page.replace(b'data-reader-from="items:itm_step:1"', b'data-reader-from="items:itm_lem:1"', 1)
        self.assertNotEqual(wrong_supplier, page)
        self.assertEqual(publish.mechanical_acceptance(wrong_supplier, dataset)["status"], "fail")
        exact = next(row for row in self.fields(page, context="target:0", field="statement.text")
                     if b'data-reader-detail="item:itm_thm"' in row)
        synopsis = self.fields(page, context="target:0:synopsis", field="statement.text")[0]
        swapped = page.replace(exact, b"READER_SWAP", 1).replace(synopsis, exact, 1).replace(b"READER_SWAP", synopsis, 1)
        self.assertEqual(publish.mechanical_acceptance(swapped, dataset)["status"], "fail")

    def test_older_projection_remains_readable_with_explicit_unavailable_context(self):
        dataset, envelope = self.reader_paper()
        older = deepcopy(dataset)
        for detail in older["details"].values():
            detail.pop("reader", None)
        envelope["projection"] = older
        page = self.render(envelope, "older")
        self.assertEqual(publish.mechanical_acceptance(page, older)["status"], "pass")
        self.assertIn(b"Structured", page)
        self.assertIn(b"unavailable", page)

    def test_historical_inline_application_keeps_its_required_form(self):
        fixture = self.fixture().primary()
        with fixture.open() as db:
            use = db.head("uses", "use_lem_thm")
            application = db.head("application_details", use.id)
            # Model a preserved format-3 body, as in the storage migration tests.
            # Current authoring normalizes this shape into a separate extension.
            body = dict(use.body, **{field: application.body[field]
                        for field in ("group_id", "needed_form", "substitutions")})
            db.begin_immediate()
            revision = db.max_revision() + 1
            db.insert_commit(revision=revision, parent_revision=revision - 1, base_revision=revision - 1,
                request_id="historical_reader_fixture", request_digest=digest(body), receipt={})
            db.insert_version("uses", use.id, use.version + 1, revision, body)
            db.set_head("uses", use.id, use.version + 1)
            db.insert_version("application_details", use.id, application.version + 1, revision, None)
            db.set_head("application_details", use.id, application.version + 1)
            db.commit()
            dataset = projection.build_projection(db, audit_id=fixture.audit_id)
            envelope = publish.render_input(db, dataset, release=False, source_identity="reader-test")
        page = self.render(envelope, "historical-inline-application")
        acceptance = publish.mechanical_acceptance(page, dataset)
        self.assertEqual(acceptance["status"], "pass", acceptance)
        row = dataset["details"]["item:itm_thm"]["reader"]["applications"][0]
        self.assertEqual(row["application_ref"], row["use_ref"])
        fields = self.fields(page, field="needed_form.text")
        self.assertEqual(len(fields), 2)  # Result card and connection card.
        self.assertTrue(all(b"Lemma 1 text" in field for field in fields))
        self.assertNotIn(b"Recorded summary connection", page)
        self.assertIn(b"Recorded application", page)
        missing = page.replace(fields[0], b"", 1)
        self.assertEqual(publish.mechanical_acceptance(missing, dataset)["status"], "fail")

    def test_parts_keep_their_own_labels_statements_and_assessments(self):
        dataset, envelope = self.reader_paper(with_parts=True)
        page = self.render(envelope, "parts")
        self.assertEqual(publish.mechanical_acceptance(page, dataset)["status"], "pass")
        targets = dataset["details"]["item:itm_thm"]["reader"]["targets"]
        self.assertEqual([row["target_ref"]["id"] for row in targets], ["itm_thm", "prt_one", "prt_two"])
        self.assertEqual([row["exact_state"] for row in targets[1:]], ["missing", "missing"])
        labels = [self.fields(page, context=f"target:{i}", field="label")[0] for i in (1, 2)]
        swapped = page.replace(labels[0], b"READER_SWAP", 1).replace(labels[1], labels[0], 1).replace(b"READER_SWAP", labels[1], 1)
        self.assertEqual(publish.mechanical_acceptance(swapped, dataset)["status"], "fail")
