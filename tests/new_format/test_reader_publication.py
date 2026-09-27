"""Prominent reader explanations must faithfully display the pinned evidence in context."""
from copy import deepcopy
import json
import re
import shutil
import subprocess

from support import CORE, R, TempCase, edit
from paper_core import projection, publish
from paper_core.canonical import digest
from test_reader_projection import blocked_premise_fixture, cyclic_premise_fixture


class ReaderPublicationTests(TempCase):
    def support_paper(self, *, alternative=False):
        fixture = blocked_premise_fixture(self.fixture(), alternative=alternative)
        with fixture.open(write=False) as db:
            dataset = projection.build_projection(db, audit_id=fixture.audit_id)
            envelope = publish.render_input(db, dataset, release=False, source_identity="reader-support-test")
        return dataset, envelope

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
        text = page.decode()
        starts = [0]
        for line in text.splitlines(keepends=True):
            starts.append(starts[-1] + len(line))

        class Fields(publish._Scan):
            def field_offset(self):
                line, column = self.getpos()
                return starts[line - 1] + column

            def handle_starttag(self, tag, attrs):
                super().handle_starttag(tag, attrs)
                self.elements[-1]["start"] = self.field_offset()

            def handle_endtag(self, tag):
                for row in reversed(self.stack):
                    if row["tag"] == tag:
                        row["end"] = self.field_offset() + len(tag) + 3
                        break
                super().handle_endtag(tag)

        scan = Fields()
        scan.feed(text)
        return [text[row["start"]:row["end"]].encode() for row in scan.elements
                if "data-reader-field" in row["attrs"] and "end" in row
                and (context is None or row["attrs"].get("data-reader-context") == context)
                and (field is None or row["attrs"]["data-reader-field"] == field)]

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

    def test_blocked_support_is_visible_and_linked_even_when_application_check_is_satisfied(self):
        dataset, envelope = self.support_paper()
        page = self.render(envelope, "support")
        self.assertEqual(publish.mechanical_acceptance(page, dataset)["status"], "pass")
        scan = publish._Scan()
        scan.feed(page.decode())
        notices = [row for row in scan.elements if "data-reader-support" in row["attrs"]]
        target = next(row for row in notices if row["attrs"].get("data-reader-detail") == "item:itm_thm"
                      and row["attrs"]["data-reader-support"] == "target:0")
        message = next(row for row in target["children"] if row["tag"] == "p" and
                       any("data-reader-support-message" in child["attrs"] for child in row["children"]))
        self.assertIn("Lemma 1", "".join(message["text"]))
        self.assertIn("private scope", "".join(message["text"]))
        for notice in notices:
            for ancestor in self.ancestors(notice):
                self.assertNotEqual(ancestor["tag"], "template")
                self.assertFalse(ancestor["tag"] == "details" and "open" not in ancestor["attrs"])
        self.assertIn(b'data-reader-support-link="application" data-reader-support-ref="uses:use_lem_thm:1"', page)
        self.assertIn(b'data-reader-support-link="blocking_scope" data-reader-support-ref="scopes:scp_supplier:1"', page)
        for before, after in ((b"The supplier depends on a private scope", b"The supplier has a verified scope"),
                              (b'data-reader-support-code="scope_unavailable"', b'data-reader-support-code="statement_refuted"'),
                              (b'data-reader-support-ref="scopes:scp_supplier:1"', b'data-reader-support-ref="scopes:scp_plain:1"')):
            self.assertEqual(publish.mechanical_acceptance(page.replace(before, after, 1), dataset)["status"], "fail")
        removed = re.sub(rb'<div class="proof-reader-notice"[^>]*data-reader-support="target:0"[^>]*>.*?</div>',
                         b"", page, count=1, flags=re.S)
        self.assertNotEqual(removed, page)
        self.assertEqual(publish.mechanical_acceptance(removed, dataset)["status"], "fail")

        for context in (b"target:0", b"application:0"):
            pattern = rb'(<div class="proof-reader-notice"[^>]*data-reader-support="' + context + rb'"[^>]*>.*?</div>)'
            collapsed = re.sub(pattern, rb'<details><summary>Support context</summary>\1</details>',
                               page, count=1, flags=re.S)
            self.assertNotEqual(collapsed, page)
            self.assertEqual(publish.mechanical_acceptance(collapsed, dataset)["status"], "fail")
            expanded = collapsed.replace(b"<details><summary>Support context", b"<details open><summary>Support context", 1)
            self.assertEqual(publish.mechanical_acceptance(expanded, dataset)["status"], "pass")

    def test_truncated_support_links_the_last_displayed_requirement(self):
        fixture = cyclic_premise_fixture(self.fixture())
        with fixture.open(write=False) as db:
            dataset = projection.build_projection(db, audit_id=fixture.audit_id)
            envelope = publish.render_input(db, dataset, release=False, source_identity="cyclic-reader-test")
        page = self.render(envelope, "cyclic-support")
        self.assertEqual(publish.mechanical_acceptance(page, dataset)["status"], "pass")
        scan = publish._Scan()
        scan.feed(page.decode())
        for identity in ("itm_lem", "itm_thm"):
            key = f"item:{identity}"
            explanation = dataset["details"][key]["reader"]["targets"][0]["support_explanation"]
            notice = next(row for row in scan.elements if row["attrs"].get("data-reader-detail") == key
                          and row["attrs"].get("data-reader-support") == "target:0")
            target = explanation["path_refs"][-1]
            pinned = f"{target['collection']}:{target['id']}:{target['version']}"
            self.assertTrue(any(row["attrs"].get("data-reader-support-link") == "target"
                                and row["attrs"].get("data-reader-support-ref") == pinned
                                and any(parent is notice for parent in self.ancestors(row)) for row in scan.elements))

    @staticmethod
    def ancestors(element):
        parent = element["parent"]
        while parent:
            yield parent
            parent = parent["parent"]

    def test_supported_alternative_has_no_target_warning_and_keeps_route_specific_warning(self):
        dataset, envelope = self.support_paper(alternative=True)
        page = self.render(envelope, "alternative")
        self.assertEqual(publish.mechanical_acceptance(page, dataset)["status"], "pass")
        self.assertNotIn(b'data-reader-detail="item:itm_thm" data-reader-support="target:0"', page)
        self.assertIn(b'data-reader-detail="item:itm_thm" data-reader-support="application:0"', page)

    def test_math_labels_render_in_pinned_fields_headings_and_links_with_safe_fallback(self):
        fixture = self.fixture().primary()
        label = r'Result $J_\lambda$ on $S$. Literal <script>alert(1)</script>.'
        with fixture.open() as db:
            for identity in ("itm_lem", "itm_thm"):
                row = db.head("items", identity)
                fixture.apply(db, [edit("replace", "items", identity, dict(row.body, label=label), row.version)], *fixture.ITEMS)
            dataset = projection.build_projection(db, audit_id=fixture.audit_id)
            envelope = publish.render_input(db, dataset, release=False, source_identity="math-label-test")
        page = self.render(envelope, "math-label")
        self.assertEqual(publish.mechanical_acceptance(page, dataset)["status"], "pass")
        labels = [row for row in self.fields(page, field="label") if b':2"' in row]
        self.assertTrue(labels)
        self.assertTrue(all(b"<math" in row and b"<script>" not in row and b"&lt;script&gt;" in row for row in labels))
        scan = publish._Scan()
        scan.feed(page.decode())
        headings = [e for e in scan.elements if e["tag"] == "h3" and "proof-detail-heading" in e["attrs"].get("class", "")]
        self.assertTrue(any(any(c["tag"] == "span" and "proof-formula" in c["attrs"].get("class", "")
                                for c in h["children"]) for h in headings))
        linked_labels = [e for e in scan.elements if e["tag"] == "span" and e["attrs"].get("data-reader-field") == "label"
                         and e["attrs"].get("data-reader-context", "").endswith((":from", ":to"))]
        self.assertTrue(linked_labels)
        self.assertTrue(all(any(a["tag"] == "a" for a in self.ancestors(e)) for e in linked_labels))
        self.assertIn(b'data-reader-ref="items:itm_lem:1" data-reader-field="statement.text"', page)
        altered = page.replace(labels[0], labels[0].replace(b"Result", b"Wrong result"), 1)
        self.assertEqual(publish.mechanical_acceptance(altered, dataset)["status"], "fail")
        for fragments in envelope["display"]["refs"].values():
            fragments.pop("label_html", None)
        fallback = self.render(envelope, "old-label-input")
        self.assertEqual(publish.mechanical_acceptance(fallback, dataset)["status"], "pass")
        self.assertTrue(any(b"$J_\\lambda$" in row and b"<math" not in row for row in self.fields(fallback, field="label")))

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
