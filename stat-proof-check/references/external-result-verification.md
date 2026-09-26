# External result verification

Use this reference when an external theorem, inequality, or technical fact is
load-bearing, whether or not it has an inline citation. For existing v1.5 folders
only, use [legacy-external-result-verification.md](legacy-external-result-verification.md).

## Identify and inspect the exact source

Retrieve the actual publication or authoritative source containing the result.
Confirm publication identity, theorem/equation locator, version or edition, and
relevant corrections. Metadata or a search-result page identifies a paper; it
does not establish theorem content. Capture the evidence used, with its bytes,
version, and source anchors or PDF page locators.

Read the theorem with inherited assumptions, meaning-determining definitions,
and surrounding conventions. Preserve domains, ordered quantifiers, probability
model, dependence, finite-sample or asymptotic regime, uniformity, normalization,
constant dependencies, regularity, and exact conclusion. Read further prerequisites
when they determine what the result actually says.

Unavailable essential text remains an unresolved dependency. Do not infer a
theorem's hypotheses from its title, familiar name, abstract, or another paper's
informal description. A bibliography defect alone is an attribution issue when the
exact result and its use have otherwise been verified.

## Record one supplier and each actual use

Keep one source-backed supplier identity for the exact external result. Preserve
the manuscript's declaration kind: a locally stated lemma remains a lemma even
when attributed elsewhere; a result introduced only as a citation can be an
`external_result`. Source inspection and each application are separate examinations.

At every use, identify:

- The exact supplier conclusion used, not merely its theorem number.
- Substitutions, rescaling, conditioning, and the target's needed form.
- Each applicable hypothesis and the manuscript evidence satisfying it.
- The consumer's scope, regime, event, and allowed constant dependencies.
- The actual contribution to the consumer's inference.

Save these facts in the assigned response. The coordinator records the exact target,
application, and scope using [graph-records.md](graph-records.md). Keep external
hypothesis evidence distinct from manuscript evidence satisfying it.

Share a current source inspection across uses when its consumed source and meaning
are unchanged. Batch related applications when their complete context fits, while
retaining distinct outcomes. A theorem may apply correctly at one use and fail at
another. A changed hypothesis, needed form, substitution, or source may require
renewed examination; an unchanged citation key does not prove currentness.

## Check contribution and applicability

A citation may refer to a shared assumption without applying the cited theorem.
Locate the actual premise. Distinguish using a theorem's conclusion from borrowing
a separable argument inside its proof. For the latter, identify that subargument
and its own inputs and restrictions. Its owner's full theorem is neither an
automatic premise nor automatic support for the borrowed step.

For example, a fixed-\(t\) theorem saying
\[
\Pr\{|Z_t|>r(\delta)\}\le\delta
\]
does not alone provide
\[
\Pr\{\sup_{t\in T}|Z_t|>r(\delta)\}\le\delta.
\]
If \(T\) is finite, a justified union bound can instead use failure allocation
\(\delta/|T|\), giving threshold \(r(\delta/|T|)\). An infinite or data-dependent
set needs its own argument and hypotheses. The supplier may be correct while
the manuscript application has a gap.

Do not import all hypotheses of an external theorem into the manuscript silently,
or discard an inconvenient requirement because a similar theorem might exist.
A reformulation needs the actual derivation. If a different verified result
repairs the argument, record the new route and preserve the original defect.

For a manuscript result that merely restates an external theorem, check the
restatement against the exact supplier, its setup, and the actual transformation.
The manuscript conclusion cannot act as its own premise.

## Save the conclusion at the correct level

Use `external_source` for exact supplier inspection and `application` for an exact use.
Follow the assigned packet/scaffold and generated role guidance for targets and response shape.
Independent workers use source targets for hidden canonical inferences, as in
[independent-checker.md](independent-checker.md). Joint reasoning and final composition remain
separate obligations. Explain missing prerequisites or incompatibilities using
[evidence-and-verdicts.md](evidence-and-verdicts.md).

A source match cannot replace application checking. A failed application does not
refute the external theorem. Preserve source limitations, per-use findings, and
the actual conditional support when the exact external evidence remains unavailable.
