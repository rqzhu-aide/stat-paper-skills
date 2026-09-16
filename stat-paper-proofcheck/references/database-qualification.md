# Reviewer qualification for the database pilot

Coordinator reference only. Read this before arranging independent review; workers receive their
checking instructions and case inputs, not grading keys or this receipt-building material.
The database records calibration evidence but does not run cases, grade mathematics, or authenticate
the declared model identity. Do not convert software test fixtures or a reviewer's confidence into
a passing qualification.

## Run and grade a balanced calibration

1. Choose at least one valid written proof and one flawed written proof with established reference
   answers and grading criteria. Use cases relevant to the intended mathematical work and reasoning
   difficulty. Keep their valid/invalid labels, reference answers, and grading criteria with the
   coordinator. Case IDs must be distinct across the entire session.
2. Dispatch the cases to a fresh checker context using the actual intended provider, model, effort,
   tools and isolation conditions. Supply the primary mathematical checklist in
   [checker-protocol.md](checker-protocol.md), the source arguments, and neutral case IDs. Do not
   supply prior paper judgments, expected answers, or hints about which case is flawed. Several
   cases may share one bounded dispatch; one call per record is unnecessary.
3. Ask for one saved response per case containing its ID, assessment of the written argument,
   substantive reasoning, and the exact defect or decisive justification. For example,
   `{case_id, argument_outcome, reasoning}` is a suitable calibration response convention. The
   qualification API treats these files as opaque bytes; it does not require the paper-review
   `WORKER_RESPONSE` shape or infer a grade from a verdict word.
4. Preserve every response unchanged before grading. The coordinator or a separate grader compares
   the actual reasoning with the reference answer. Record `pass`, `fail`, or `inconclusive` for each
   case with the grading rationale. A valid proof wrongly rejected fails; an invalid proof correctly
   diagnosed can pass even when its final statement happens to be true. This grade is about the
   checker, not the truth value of the calibration statement.
5. Preserve a coordinator evidence file containing the case inputs, reference answers/criteria,
   actual dispatch profile and isolation, case grades/reasons, response filenames, and limitations.
   A passing qualification requires nonempty valid and invalid case lists, distinct case IDs, and
   `pass` on every case. If evidence is missing or a case fails/remains inconclusive, record the
   limitation with `qualified: false`; arrange another genuine calibration if needed.
6. Record the receipt below. Use its qualification ID in the audit's `qualification_id` and in the
   independent submission envelope. The submission reviewer and `item-audit/1` protocol must match
   the qualification. Preserve fresh source-only isolation again for the actual paper review.

Reuse calibration for the same actual reviewer profile/configuration; moving to another fresh
context alone does not require rerunning it. A changed provider, model, effort, tools or isolation
configuration requires a new calibration record with a new ID. Update the audit through ordinary
authoring commands and use the new qualification for subsequent dispatch. Never replace the old
qualification record or represent a historical response as newly calibrated.

## Exact receipt shape

Submit with `python "<skill-root>/scripts/paper_audit.py" qualification record AUDIT.db --receipt RECEIPT.json`.
This dedicated command is packetless and creates immutable qualification records only.

| Object | Complete fields |
|---|---|
| Receipt | `contract_version: 3`, `request_id: string`, `edits: [Create]`, `blobs: [Blob]` |
| Create | `op: "create"`, `collection: "qualifications"`, `id: qualifications ID`, `expected_version: null`, `body: Qualification` |
| Qualification | `reviewer: nonempty string`, `profile: Profile`, `protocol_version: "item-audit/1"`, `valid_case_results: [Case]`, `invalid_case_results: [Case]`, `evidence_blob: SHA256`, `qualified: boolean`, `limitations: [nonempty string]` |
| Profile | `provider: nonempty string`, `model: nonempty string`, `effort: string|null`, `tools: [nonempty string]`, `context_isolation: nonempty string` |
| Case | `case_id: nonempty string`, `response_blob: SHA256`, `outcome: "pass"|"fail"|"inconclusive"` |
| Blob | `sha256: lowercase hexadecimal SHA256`, `encoding: "base64"`, `data: base64 string` |

All fields are required; unknown fields are rejected. Hash and base64-encode the exact file bytes,
not a reserialized worker object. Include each referenced response and the coordinator evidence
file in `blobs`, unless that identical blob is already stored. The command checks hashes, shapes,
referenced evidence availability, and the declared balanced passing conditions. It does not verify
the mathematical grading inside those blobs. A successful command alone does not establish competence.

[qualification-example-receipt.json](qualification-example-receipt.json) is a complete interface
example with both case classes, preserved example bytes, and `qualified: false`. No checker ran for
that example. Do not use its IDs, profile or grades as evidence for a paper audit.

## Mechanical assembly from real files

Generate fresh request and qualification IDs using `ids --kind request` and `ids --kind qualifications`.
Prepare `qualification-grading.json` with those `request_id` and `qualification_id`, the actual
`reviewer`, `profile`, `protocol_version`, `limitations`, and a `cases` array. Each case entry has
`case_id`, `class: "valid"|"invalid"`, `response_path`, and the actual graded `outcome`; include the
case input, reference criteria and grading rationale in this evidence file as well. Paths below are
relative to that file. The evidence file is coordinator-authored and has no separate enforced schema.

This standard-library snippet only packs that evidence and the unchanged response files:

```python
import base64, hashlib, json
from pathlib import Path

grading_path = Path("qualification-grading.json")
evidence_bytes = grading_path.read_bytes()
grading = json.loads(evidence_bytes)
blobs = {}

def preserve(raw):
    sha = hashlib.sha256(raw).hexdigest()
    blobs[sha] = {"sha256": sha, "encoding": "base64",
                  "data": base64.b64encode(raw).decode("ascii")}
    return sha

evidence_sha = preserve(evidence_bytes)
results = {"valid": [], "invalid": []}
for case in grading["cases"]:
    raw = (grading_path.parent / case["response_path"]).read_bytes()
    results[case["class"]].append({"case_id": case["case_id"],
        "response_blob": preserve(raw), "outcome": case["outcome"]})
qualified = bool(results["valid"] and results["invalid"]) and all(
    case["outcome"] == "pass" for rows in results.values() for case in rows)
body = {"reviewer": grading["reviewer"], "profile": grading["profile"],
        "protocol_version": grading["protocol_version"],
        "valid_case_results": results["valid"], "invalid_case_results": results["invalid"],
        "evidence_blob": evidence_sha, "qualified": qualified,
        "limitations": grading["limitations"]}
receipt = {"contract_version": 3, "request_id": grading["request_id"],
           "edits": [{"op": "create", "collection": "qualifications",
                      "id": grading["qualification_id"], "expected_version": None, "body": body}],
           "blobs": list(blobs.values())}
with Path("RECEIPT.json").open("x", encoding="utf-8") as output:
    json.dump(receipt, output, ensure_ascii=False, indent=2)
    output.write("\n")
```

The snippet computes hashes and packs the coordinator's recorded grades; it performs no scientific
grading. Inspect the generated receipt before recording it. Keep original response files and the
grading evidence for review. No legacy ledger, canary session, or separate calibration database is
required by this native interface.
