# Claim-Preserving Prose Polishing

## Scope and meaning

Distinguish a light polish of grammar and local clarity, substantive polishing of paragraph architecture and explanation, and structural revision of sections. Work within the requested scope. Perform checks privately and return or apply the improved text; an ordinary polish needs no audit report or approval for a supported edit.

Before rewriting, identify the passage's job, claim, mathematical objects, evidence level, and boundary. Protect:

- equations, symbols, indices, macros, labels, and cross-references;
- negation, logical direction, quantifiers, conditioning, and sources of randomness;
- finite-sample, asymptotic, oracle, feasible, empirical, and computational scope;
- uncertainty, modality, causal status, and novelty claims;
- numerical values, units, and citations.

Preserve scientific content while changing explanation order, headings, sentence subjects, and paragraph boundaries as authorized. Inspect dependencies of formal statements, assumptions, estimands, numerical conclusions, and causal interpretations before editing. Exact mathematical tokens remain unchanged unless notation normalization is requested.

For conflicting representations, uncertain equivalence, missing support, or a proposed substantive correction, use [support-and-author-decisions.md](support-and-author-decisions.md), the detailed action rule. Continue supported edits elsewhere. Do not hide a scientific change inside a polish.

## Revise at the needed scale

For paper-level work, follow [manuscript-workflow.md](manuscript-workflow.md) to read and plan, work focused sections, and reconcile. For a local edit, use only the checks relevant to that passage; no fixed sequence of separate passes is required.

## Prose core for drafting and revision

For drafting, apply this subsection; the revision-specific checks elsewhere in this guide need not be loaded solely to draft a section.

**Sentence and cohesion.** Unpack stacked nouns into the relation among named objects. Keep subjects near their verbs and antecedents unambiguous. Start from the dependency created by the previous sentence and place new information where it receives emphasis. Use stable terms, especially for oracle versus feasible, population versus empirical, and exact versus approximate objects. Transitions should express a substantive connection rather than announce another section.

**Paragraph development.** Introduce the reader's question, claim, or obstacle before dense detail and notation at its use. Let the paragraph develop that purpose. Combine fragments answering one question and split overloaded reasoning at a change of purpose. Sustained comparisons may need substantial space; transitions may be brief. Use no word quota or repeated paragraph skeleton. Remove repeated openings and summaries without erasing necessary qualifications.

**Economy and register.** Remove language that changes neither meaning nor navigation. Preserve a professional authorial voice and already clear sentences. For specialist terminology, evidence verbs, tone, or software-manual register, use [wording-register.md](wording-register.md).

## Statistical prose mechanics

**Definitions.** Explain why an object is needed and keep its mathematical type clear. A definition does not itself imply existence, uniqueness, identification, or estimability.

**Assumptions.** Preserve who assumes what, under which law or regime, and for which result. Explain the supplied restriction instead of relying on unsupported descriptions such as mild or standard. Do not add an editor-proposed assumption to make the prose work.

**Evidence level.** Preserve the manuscript's attributed status: a proved result under stated assumptions, a numerical result in reported settings, an empirical pattern that suggests a conclusion, or an unproved mechanism that motivates it. A theorem environment or attached proof does not justify changing states or claims to proves or establishes. Likewise, preserve qualifications such as may, can, typically, and under Assumption 2 unless a supported substantive correction is authorized.

For proof prose, including a local polish, use [theoretical-proofs.md](theoretical-proofs.md) for the proof-ending boundary. This is exposition work, not a proof-completeness judgment.

**Comparisons.** Name the metric, comparison basis, information available, and scope. Replace outperforms with the reported advantage when it is not uniform across settings or criteria.

**Limitations.** Place a restriction beside the claim it qualifies. Repeat it when a distant passage could otherwise mislead, using a short reference where sufficient. Consolidate caveats without making a headline unconditional or concealing a theory-to-implementation gap.

## Mathematics and displays

Introduce a display with its purpose and explain its consequence or mechanism, rather than paraphrasing every symbol. Preserve punctuation and grammatical integration. Check whether respectively, conditional, marginal, uniform, and independent match the displayed relation. Any authorized notation change must propagate consistently.

## Compare and deliver

Compare source and revision for the protected content above, including the relationships among symbols, conditioning, convergence modes, constants, and theorem references. Check that supplied citation support still matches its clause, values and units agree, and terminology remains consistent across affected captions, algorithms, and supplements.

Watch particularly for changes from some to all, pointwise to uniform, association to effect, oracle to feasible, approximate to exact, observed to established, can to guarantees, or one setting to general settings. These are changes of scientific force, not stylistic alternatives.

For a local edit, deliver the text directly. For a longer revision, summarize the principal changes and validation, with unresolved input and any authorized substantive correction stated separately. Keep a reviewable diff and avoid an exhaustive style log. For a difficult specialist or claim-preservation choice, consult [polishing-examples.md](polishing-examples.md); routine edits need no examples file.
