# Evaluation: `stat-paper-reviewer` skill

**Date:** 2026-08-30
**Scope:** All 16 files in `stat-paper-reviewer/` (SKILL.md, 9 references, 2 scripts, 2 test files, agents/openai.yaml, LICENSE). I ran the bundled test suite (19/19 pass on Python 3.11), smoke-tested both CLIs, and measured the token footprint of every load path.
**Benchmark:** Your stated intent, a structured review report covering (1) novelty, (2) theory, (3) computation, (4) writing, each scored 1-10.

---

## 1. Verdict

This is a far more mature skill than most: the review discipline (provenance labeling, first-reader sequencing, anti-hallucination rules, N/A-not-zero scoring, verified novelty search) is at a professional referee-training level, and the bundled scripts are production quality. It will reliably produce a rigorous, well-calibrated referee report.

Measured against your four-category intent, however, it under-delivers on the exact deliverable you described. The largest single gap is that **the skill's own scoring rubric actively countermands your 1-10 request**: it mandates a 1-5 integer scale and forbids "apparent precision between anchors even when the requested output format asks for them." Your canonical prompt ("score each category 1-10") supplies dimensions and a scale but not anchors, so under the skill's own definition it is *not* a "defined rubric," the default 1-5 rubric applies, and a faithful run will either return 1-5 scores or improvise an unanchored 1-10 mapping inconsistently across runs. Three of your four categories also lack a first-class home in the scorecard and checklists (details in §3).

Summary scores (1-10, using your scale):

| Area | Score | One-line basis |
|---|---:|---|
| Novelty coverage | 8 | Verification pipeline is excellent; the "assembly of known components" decision rule is implicit, not operational |
| Theory coverage | 6 | Assumption analysis and revision-vs-new-theory taxonomy are strong; no positive "does the proof seem reasonable" plausibility pass, only prohibitions |
| Computation coverage | 5 | Experiment/baseline design well covered; computational cost and scalability barely mentioned, unscored |
| Writing coverage | 7 | AI-prose machinery is sophisticated and defensible, but deliberately refuses your literal question and excludes editing-issue reporting |
| 1-10 category scoring | 3 | Actively blocked by the current rubric; no four-category preset; scores are off by default |
| Token efficiency | 5 | ~19-24k instruction tokens per full review, 2.5-4k of duplication, plus mandatory run-bundle ceremony worth 10-30k tokens per run |
| Scripts & engineering | 9 | Stdlib-only, portable, defensive, and 19/19 tests pass |
| Triggering (description) | 8 | 956 chars (within the 1024 limit), specific, encodes anti-triggers |
| Maintainability | 5 | Heavily eval-hardened patch layers duplicated across files; drift risk on every future edit |

---

## 2. What already works well

Worth naming explicitly, because these should survive any refactor. The two-axis fact base (provenance × support status) and the rule that a manuscript assertion is never "established" are exactly the discipline that keeps LLM reviews honest. The first-reader sequential pass with delayed-resolution accounting is a genuinely good reviewer methodology that most human referees don't formalize. The novelty pipeline (claim decomposition → cited-work verification → uncited-close-work search → evidence ceilings → bounded conclusion, never "proof of firstness") is the strongest part of the skill and directly serves your intent question 1. The scoring safeguards (N/A never zero, noncompensation, no unearned aggregate) are correct and should be preserved under any scale. The AI-writing module's false-positive safeguards and refusal to infer authorship are legally and professionally the right call. `academic_search.py` and `review_run.py` are careful pieces of software (atomic writes, hash-locking, symlink rejection, ORCID placeholder rejection, relevance-preserving re-rank), and the tests actually cover the failure modes that matter.

---

## 3. Sufficiency against your four categories

### 3.1 Novelty — mostly sufficient, one missing decision rule

Covered: claimed-distinction location (framework §1), gap-as-missing-capability check, external verification with citation status, contribution-form classification including "combination," bounded firstness language.

Gap: your actual question, *"when it is mainly putting several components together, is it targeting something that no other methods can do, or approximately do,"* never appears as an operational test. "Combination" is a label in novelty-verification §3, not a procedure. A run will classify the contribution as a combination and stop short of the judgment you care about.

Fix: add a short **combination test** to `novelty-verification.md` (or framework §1). When the contribution form is a combination: (a) does the combination deliver a capability that no publication in the verified comparison set achieves or approximates? (b) did making the assembly work require nontrivial new development (new identification argument, new analysis, non-obvious algorithmic step), or would a competent practitioner assemble it directly? (c) classify as *new primitive / enabling combination / convenience assembly*, and require the novelty conclusion to state which and why. This is ~10 lines and directly encodes your rule.

### 3.2 Theory — good on assumptions, asymmetric on proofs

Covered well: assumptions grouped by role with the "hidden / implausibly described as mild / hard to diagnose / incompatible with the application" test (framework §3) answers "are assumptions too strong." The remedy taxonomy (rewrite / reanalysis / new evidence / new theory / verification / author decision, framework §6) answers "revision vs fundamental new development" precisely; this is one of the skill's best matches to your intent.

Gap: on proofs, the skill is written almost entirely as prohibition ("Do not perform exhaustive proof checking or decide whether a theorem is mathematically correct," repeated in the description, boundaries, and QA). There is no positive procedure for the plausibility read you want ("do the proofs seem reasonable?"). In practice a faithful run tends to play safe and report "proof correctness unassessed," giving you less signal than you intend.

Fix: add a **theorem plausibility screen**, explicitly labeled as plausibility rather than verification so the defensibility boundary is intact. Checks: does the claimed rate/guarantee contradict known lower bounds or known results in special cases; do the theorem statements behave sensibly in degenerate or limiting cases; are quantifiers, constants, and convergence modes coherent across restatements; is the proof technique named/sketched and standard for this claim type; are all stated assumptions actually used, and is any needed assumption visibly absent. Output: "plausible / plausible with flagged risks / specific step challenged," with the existing rule that a challenge must name the exact step. This keeps your line-by-line exclusion while producing the "seems reasonable" judgment.

### 3.3 Computation — half covered

Covered well: framework §2 (does the algorithm implement the stated estimator; tuning/failure conditions adequate) answers "computationally correct" at the alignment level, and framework §4's fair-competitor/representative-settings/stress-settings checklist is a direct, strong match for "compared with a suitable set of alternatives on a representative set of settings."

Gap: *"is the cost heavy?"* has no home. "Computational budgets" appears once inside a list and "computational property" once in the novelty decomposition. Nothing asks for stated time/memory complexity, scaling evidence versus claim, wall-clock and hardware reporting, tuning-budget symmetry with baselines, or feasibility at realistic problem sizes; and there is no scoring dimension for it (the default 8 dimensions cover evidence and method-theory coherence, not cost).

Fix: add a compact **computational cost and practicality** block to framework §2 or §4 with those five checks, and a corresponding optional scoring dimension.

### 3.4 Writing — sophisticated, but deliberately answers a different question

Two deliberate design decisions here that you should confirm match your intent, because the skill enforces both with multiple hard rules:

First, it will never answer "does it look like it was written by AI?" directly. It reframes to claim-traceability defects and returns one of three public labels (Reportable recurrent pattern / No reportable pattern / Not assessable) plus a mandatory disclaimer that text cannot establish authorship. I would keep this: it is the defensible version for anything that touches real authors. But be aware the literal question in your intent statement gets a reframed answer by design.

Second, "is wording appropriate? any editing issues?" is largely excluded by design. The consequence gate plus several QA deletion rules ("Delete any purely cosmetic finding... even when the user requested sentence-by-sentence edits") means typo density, notation inconsistency without consequence, and reference formatting will not be reported even on request. If you want a scored *writing/presentation* category, the current rules will actively suppress part of its evidence base. Fix: add a narrow carve-out, when a writing score or writing assessment is requested, report *aggregate* editing-quality observations (density and classes of mechanical issues, notation stability, reference hygiene) without itemized copyedits, keeping the no-itemized-cosmetics rule.

One internal inconsistency worth fixing regardless: the QA ban on U+2013/U+2014 applies to the *entire response*, while other QA rules require preserving exact identifiers and quoted titles. A comparator titled with an en dash cannot be both preserved exactly and dash-free. Exempt verbatim quotes and identifiers from the dash rule.

### 3.5 The scorecard itself — the biggest gap

Your intended deliverable is four category scores on 1-10, present in every review. Current behavior: scores appear only when requested (SKILL.md core stance); the default scale is 1-5 integers with anchors; granularity beyond the anchors is forbidden even when requested; your four categories don't map onto the eight default dimensions (novelty maps to two of them; theory to two; computation and writing to none cleanly).

Fix, concretely:

1. Add a **four-category referee scorecard preset** to `scoring-rubric.md`: Novelty (fed by novelty-verification, including the combination test), Theory (framework §3 + plausibility screen), Computation & evidence (framework §2 + §4 + cost block), Writing & presentation (framework §5 + ai-writing-alarm + the aggregate editing carve-out). Keep N/A, noncompensation, and evidence rules exactly as they are.
2. Give it **native 1-10 anchors** (e.g., 1-2 not established / centrally deficient, 3-4 major unresolved gaps, 5-6 plausible but mixed, 7-8 strong with bounded concerns, 9-10 compelling in the reviewed scope), or keep 1-5 anchors and add an explicit published mapping rule for user-requested scales. Either works; pick one so runs are consistent.
3. Decide the default: if you want scores in every full review (your intent statement reads that way), change "unless the user asks" to "in every full review and whenever requested." If you'd rather keep them request-gated, at least put "with 1-10 category scores" into `agents/openai.yaml`'s default prompt so your canonical invocation asks for them.

### 3.6 Report structure

The default integrated review is organized by severity-ranked findings, not by your four categories. That is the right skeleton for a referee report, and the four-category scorecard (each row carrying a one-to-two-sentence verdict) is the cleanest way to give you the category-structured view on top of it. If you want more, add a "four-category audit" variant to `report-formats.md` rather than reorganizing the default.

---

## 4. Token efficiency

Estimates at ~3.7 bytes/token for this kind of prose; treat as ±15%.

| Component | Size | ~Tokens |
|---|---:|---:|
| Metadata (name + description, always in context) | 976 chars | ~264 |
| SKILL.md body (every trigger) | 25.7 KB / 225 lines | ~6,900 |
| Full review load (SKILL.md + 6 mandated refs) | | ~18,900 |
| Your canonical run (full + scores + novelty) | | ~23,800 |
| Focused review (SKILL.md + framework + QA) | | ~11,000 |

Assessment: the metadata cost is fine, and the routing table is genuine progressive disclosure done right. The two real cost drivers are below.

**Driver 1: duplication (~2.5-4k tokens per full load, plus maintenance risk).** Measured repetition: "edit specification" rules appear 22 times across 6 files; not-assessable rules in 7 files; the N/A scoring rules in 4 files; the `found independently and uncited` two-axis rule 7 times in 3 files; and the patterned-prose classification/scrubbing logic exists nearly in full in *both* SKILL.md (steps 7 and 10, ~1.5k tokens) and ai-writing-alarm.md (~2.8k). Roughly 40% of SKILL.md is terminal-check and boundary language restating rules that already live in a reference. These read as accumulated eval-hardening patches; they are currently mutually consistent, but every future edit risks divergence between copies.

Fix: one source of truth per rule family. Patterned-prose classification, mapping, and scrub rules live only in `ai-writing-alarm.md`; scoring safeguards only in `scoring-rubric.md`; two-axis status rules only in `novelty-verification.md`; the no-rewrite boundary stated once in SKILL.md's stance and once in `review-qa.md`'s checklist, nowhere else. Keep exactly one terminal checklist (review-qa.md) and make SKILL.md's step 10 a pointer to it. Realistic target: SKILL.md at ~2.5-3k tokens (roughly 60% smaller) with no behavior change intended; the full-review load drops to ~14-15k.

**Driver 2: the run-portability bundle is mandatory for every full review.** The full profile requires doctor → init → source map → 7 stage registrations (each of which first requires writing a durable artifact file) → status checks → finalize → final status. That is roughly 18+ process tool calls and a set of intermediate artifacts that substantially duplicate work the model does in context anyway; in practice this costs on the order of 10-30k tokens and real wall-clock per review. The machinery is well built and earns its keep for delegated multi-agent runs, resumable long reviews, and multi-file packets. For a single-PDF interactive review it is mostly ceremony.

Fix: make the bundle conditional, required for delegated, resumed, or multi-file runs or when you ask for an audit trail; for a single-manuscript interactive review, require only the source-map discipline (PDF page mapping and visual equation/table checks, which genuinely prevent errors) without init/stage/finalize. This is the single biggest efficiency lever, larger than all prose dedup combined.

**Smaller items.** `ai-writing-alarm.md` (~2.8k) is loaded during every full review's first pass even for obviously clean papers; you could load it only when the first pass actually records candidates or the user asks, at the cost of inlining a 5-line conservative candidate-noting heuristic in SKILL.md. The description is 956 chars, safely under the 1024 limit, but you're close; watch it when editing. Python cache directories created by local test runs are already ignored and do not ship in the packaged skill.

---

## 5. Engineering verification (ran here)

`python3 -m unittest discover -s tests`: **19/19 pass** (Python 3.11, Linux). Both CLIs' `--help` work from an unrelated working directory; `academic_search.py` correctly refuses to run without an API key and reports HTTP 429 hints; `review_run.py`'s fail-closed behavior (finalize blocked until stages exist, tamper detection, downstream invalidation) is tested and works. Minor notes: the routing table's "Full review" row omits `run-portability.md` even though the prose above it mandates it for every full review (make the table row match, or make the prose conditional per §4); `agents/openai.yaml` is fine as marketplace metadata.

---

## 6. Prioritized improvement plan

1. **Scoring preset (highest impact, small edit).** Four-category referee scorecard with native 1-10 anchors in `scoring-rubric.md`; decide default-on vs request-gated; update `openai.yaml` default prompt accordingly.
2. **Combination test** in `novelty-verification.md` (~10 lines): new primitive / enabling combination / convenience assembly, judged against the verified comparison set.
3. **Theorem plausibility screen** in `review-framework.md` §3 (~15 lines): positive checks, bounded output labels, existing exact-step rule for challenges.
4. **Computational cost block** in `review-framework.md` (~8 lines) plus the optional scoring dimension.
5. **Dedup refactor**: single source of truth per rule family; SKILL.md to ~2.5-3k tokens; one terminal checklist in `review-qa.md`. No intended behavior change, so do it after 1-4 and verify with the eval loop below.
6. **Make run-portability conditional** (delegated / resumed / multi-file / audit-trail requests); keep the source-map discipline always-on for PDFs.
7. **Small fixes**: exempt verbatim quotes and identifiers from the dash ban; add a writing-score carve-out for aggregate editing observations; and align the routing table with the run-portability rule.
8. **Add an eval set** (none exists today): 4-6 test manuscripts/excerpts with assertions, e.g. a combination-contribution paper (does the review apply the combination test and score novelty on 1-10), a partial manuscript (are missing dimensions N/A, never low scores), a "review and rewrite" request (does it stop at edit specifications), a clean well-written paper (No reportable pattern, no scrubbing violations), a heavy-cost method (is cost assessed). Run them before and after the refactor to confirm nothing regressed.

Items 1-4 close the gaps against your stated intent; 5-6 are the token-efficiency work; 8 protects both.

---

## 7. Bottom line

Sufficient today for a rigorous, defensible referee report; not yet sufficient for the specific structured deliverable you described. The four audits exist at roughly 80% (novelty), 60% (theory), 50% (computation), 70% (writing, by deliberate reframing), but the 1-10 four-category scorecard, the thing that ties your report together, is currently blocked by the skill's own rubric rules rather than merely missing. Token-wise the skill spends ~19-24k instruction tokens plus heavy process overhead per full review where ~14-15k with a conditional bundle protocol would preserve the same behavior. All of the fixes are edits to existing files; nothing needs to be redesigned.
