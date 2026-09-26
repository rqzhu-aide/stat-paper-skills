---
name: stat-proof-write
description: Draft, expand, and polish proofs for statistical and machine-learning papers. Use only when the user explicitly invokes $stat-proof-write. Clarify derivations, compressed probabilistic arguments, and the connection between equations and prose. Supports local derivation within stated assumptions; does not replace an independent proof audit or general manuscript editing.
metadata:
  version: "0.3.1"
---

# Statistical Proof Writing

Use this skill only when the user explicitly invokes `$stat-proof-write`.

Write research-paper proofs that a statistics PhD student outside the paper's subfield can follow without repeatedly reconstructing missing arguments. Aim for purposeful detail, conventional language, and a visible line of reasoning. A natural proof can be concise or long, and can contain many equations. Its distinguishing feature is that the reader knows what each calculation establishes and why the next step follows.

Treat an impression of AI writing as an editorial concern, not evidence of authorship. Do not introduce errors, mannerisms, or artificial variation to make prose seem human. Improve the mathematical exposition itself.

## Explain the argument to a first-time reader

Assume graduate training in probability, statistical inference, and linear algebra, but not familiarity with the paper's specialized methods, notation, or proof techniques. A sequence of correct facts, definitions, and estimates is not enough: explain why these particular facts are being introduced and how they address the problem currently facing the reader. Preserve the research content while making its reasoning accessible at this level.

Distinguish what the reader has seen from what the reader can be expected to remember and use. At a new stage, after a long derivation, or when returning from auxiliary lemmas, briefly recall the relevant notation together with its meaning and the conclusion now sought. For example, remind the reader that a symbol denotes the actual variance and that an error must be negligible relative to it. Restating a key formula or assumption is useful when it saves a search through earlier pages; do not repeat the entire setup at every transition.

When a specialized concept first does mathematical work, explain its relevant meaning and consequence. For example, identify a zero first projection through the conditional-mean identity it requires and explain the improved bound it permits. Naming a concept or defining a symbol once does not establish that the reader understands its role. Standard graduate tools can be named directly, but show their application when conditioning, scaling, or a less familiar object makes it nontrivial.

Before a substantial construction or change of argument, identify the specific need it serves. For example, explain why a usual variance bound is too large at the required scale before introducing a kernel with a vanishing first projection. After the calculation, explain what has been gained and how it advances the proof. Keep these explanations mathematical and local; do not add generic encouragement or repeatedly announce that the next step is important.

Distinguish explaining from reporting. "This gives a factor of k/n" reports a feature of a formula. Explaining identifies why that factor matters, such as making an error negligible relative to the target variance. "Define the following kernel" introduces notation; explaining says which dependence or averaging problem that kernel lets us handle. Supply only connections justified by the mathematics.

Make definitions earn their place. Introduce auxiliary notation close to the problem it resolves, connect a lemma to its later use, and explain an assumption through the step it permits. Avoid paragraphs that read like private working notes: define an object, list properties, invoke a result, and move on without connecting these choices.

## Establish the argument before editing

Read the statement, relevant definitions and assumptions, the complete proof in scope, and the results it uses. For a local edit, read enough surrounding material to understand the step and its destination. Preserve the paper's notation, normalization, labels, and authorial voice.

Identify the target conclusion, main reduction, substantive intermediate steps, and the places where the reader must supply missing reasoning. Use this understanding to write the manuscript's proof outline and local transitions, not only to plan the edit privately. Distinguish a compressed valid calculation from a missing argument. The former calls for expansion; the latter needs mathematical work or an explicit author note.

- **Polish an existing proof:** preserve its mathematical claims and route by default. Expand justified algebra and probability calculations directly. Do not silently strengthen assumptions, change a rate, or replace the theorem with an easier one.
- **Draft or complete a proof:** work from the stated assumptions and supplied argument. Derive needed steps when possible. Do not fabricate a lemma or hide an unresolved step behind polished prose. If a consequential gap remains, identify its exact location and what is needed while completing independent portions.
- **Give feedback only:** explain the main reading difficulties with concrete locations and representative repairs. Do not rewrite the whole proof unless requested.

This skill requires checking the mathematical steps it writes. It does not require a separate audit workflow, audit database, or correctness certificate. Do not start a separate proofcheck skill implicitly. If an edit exposes a substantive error that changes the result or requires an author decision, distinguish that issue from the exposition changes.

## Allocate detail by the work the reader must do

Expand a transition when it combines several operations, uses a consequential assumption, changes the scope of a claim, or produces the rate needed by the theorem. Common examples include adding and subtracting a population term, conditioning on a training sample, changing norms, controlling a supremum, absorbing a term, or comparing powers of sample size and dimension. For these passages, use the completeness of a well-written graduate homework solution: explain the choice of argument, show the intermediate calculation, and justify its decisive steps. Select such passages by the work a statistics PhD student outside the subfield would need to do, even if a specialist would call the step routine.

Write multistep equality and inequality chains vertically in an `aligned`, `align`, or `align*` environment, with successive transformations on separate rows. Do not leave a horizontal chain inside an otherwise multiline display. A display being short enough to fit on the page is not a reason to put its derivation on one line. Keep single identities and parallel definitions compact; they are not chains of reasoning.

Introduce the calculation with its purpose. Immediately after the display, explain the key transitions in their displayed order, associating each reason with the equality, inequality, or expression it justifies. For example, identify the conditioning that permits factorization, the centering that makes a term vanish, and the assumption that makes the final bound small. Naming several tools before the display or writing "this proves the claim" afterward does not provide this explanation.

Use one meaningful transformation per row and distinguish equality from inequality. Do not add duplicate rows that merely reformat an expression. If several independent calculations would make the explanation hard to match to the lines, separate them into displays and explain each locally. Break at changes of mathematical task, for example from a deterministic bound to a stochastic order.

Treat displays as parts of sentences, with appropriate punctuation. Align related equalities or inequalities at their relation symbols, and keep long explanations outside the display. Number results that need later reference according to the manuscript's conventions; do not label every intermediate line. Use short step annotations only when they make the corresponding justification easier to locate.

Keep elementary transitions compact when the intended graduate reader can verify them at sight and they are not the point of the argument. Homework-style detail means exposing the reasoning, not proving every standard inequality or narrating each arithmetic operation. Develop the first nontrivial application fully enough to follow; later applications may be shorter if their substitutions and conditions remain clear. Detail should follow the reader's needs and the requested depth, not an arbitrary length target.

Read [worked-revisions.md](references/worked-revisions.md) when drafting a substantial proof or repairing its organization, compressed derivations, conditioning, or rate arguments. It gives examples of the intended level of exposition, including a proof outline connected to supporting lemmas and a detailed calculation within that outline; adapt their decisions rather than their wording.

## Let prose and displays do different jobs

Use prose to identify the local target, explain the choice of argument, state conditions, and interpret the result of a calculation. Use displays to show the decomposition, cancellation, inequality, or limit. An explanation should answer why a step is valid or useful, not read its symbols aloud. When a display contains consequential steps, explain them afterward even if the paragraph before it named the tool.

The substantive progression is purpose, calculation, justification, and consequence. Vary the sentence structure naturally; do not turn that progression into a repeated four-sentence template. One sentence after a short display may explain both its decisive step and why the result is useful.

Diagnose imbalance by function, not by counting equations:

| Reading difficulty | Revision |
|---|---|
| Dense displays with no direction | State what is being bounded and why; divide at changes of argument. |
| Fluent prose that conceals the calculation | Replace vague claims with the missing mathematical lines. |
| An explanation repeats every displayed symbol | Retain only the reason, condition, or consequence the display does not express. |
| Many short, isolated displays | Combine related transformations into one aligned derivation; keep incidental definitions inline. |
| One display contains several distinct arguments | Separate them and explain the transition. |
| Correct facts appear without a reason for selecting them | Explain the obstacle, the needed property, and what the calculation contributes. |
| A display chains several equalities across one row | Put successive transformations on separate aligned rows and explain the key steps afterward. |
| A key step is called standard, immediate, or routine | Name the actual result and show its application if the conclusion is not visible. |

Do not enforce an equation-to-text ratio or a minimum proof length. Single definitions and immediate identities need no ceremonial introduction or explanation. A substantive derivation needs the local guidance described above, even in a short proof.

## Organize around the mathematical task

For a substantial proof, include an outline of its major steps in the actual manuscript. Begin by recalling the target and the key objects needed to understand it, including the normalization or convergence statement when consequential. Then explain the main reduction and the mathematical contribution of each step. A useful outline says what must be shown and why those conclusions together establish the theorem; an inventory such as "decompose, bound, and apply Slutsky" does not. A short proof can begin with the decisive identity.

When a major step relies on an existing lemma, proposition, or earlier calculation, identify that result in the outline. State the intermediate conclusion or bound it provides and how that resolves the step, using the manuscript's actual labels. The outline should be understandable without opening the cited lemmas. For a step developed within the proof, describe the argument that will establish it without creating an unnecessary lemma. If a sequence of prerequisite lemmas precedes the main proof, put the outline before that sequence so the reader knows what the lemmas are for; briefly reorient the reader when the main proof resumes. An outline or step list in an accompanying explanation does not substitute for this guidance inside the proof document. Use connected prose or numbered steps according to the argument's length and structure; do not prescribe a fixed number of steps.

Introduce a decomposition before discussing its terms. Give terms names when they will be reused or treated differently, and explain their roles when helpful. Avoid layers of one-use symbols. Preserve brief reminders of key notation, assumptions, and the current target when they help the reader follow a new stage; concision is not a reason to make the reader reconstruct that context.

Use paragraphs for changes of purpose. Numbered steps or descriptive subheadings help in a long proof with genuinely separate tasks; they make a short lemma cumbersome. Do not turn every estimate into a claim or lemma. Introduce an auxiliary lemma when it isolates a substantial reusable argument or materially clarifies the main proof.

Work out the first representative case. For a repeated case, identify the substitution, symmetry, or bound that makes the same argument apply. Recheck changes in dependence, boundary behavior, constants, or index sets before saying the proof is analogous.

At each major step, make the local goal and its place in the outline recognizable. When invoking its supporting lemma, recall the needed conclusion in the present notation and explain why it applies; do not leave the reader with only a lemma number. At a real checkpoint, state what is established and what remains. At the end, show how the major steps combine to give the exact theorem, including the final substitution, normalization, or probability argument when it is not immediate. A stock proof-ending sentence cannot supply this connection.

For a requested full proof, retain the necessary derivations in the proof or a precisely referenced appendix. Do not improve its apparent flow by silently turning it into a sketch or moving the difficult step out of view. Follow explicit venue or length constraints while keeping the argument accessible.

## Use familiar, precise statistical language

Name theorems, lemmas, and substantive proof sections by the result the reader obtains: the object being studied and the property established, such as an identity, variance bound, relative-error bound, or consistency conclusion. A reader scanning the titles should be able to tell what each result contributes. Prefer "Sample-variance representation of the additive estimator" to "Exact additive cancellation," and "Ratio consistency of the variance estimator" to a title that names only the kernel setup. Mention a proof technique when it distinguishes a familiar result, but do not let the technique replace the conclusion in the title.

Match the name to the result actually stated. A finite-sample error bound should not be named consistency or negligibility unless the stated conditions imply that limiting conclusion. When a result has several parts, name its main usable conclusion or its closely related conclusions; do not turn the title into a full statement. Preserve informative existing names, result numbers, and reference labels. Use consistent descriptions in the proof outline and the corresponding steps. Ordinary navigation headings such as "Setup" or "Proof of Theorem 1" need no forced replacement.

Prefer verbs that state the mathematical operation: define, decompose, condition on, bound, substitute, sum, integrate, and apply. Prefer the actual statistical object: estimator, residual, estimation error, conditional variance, empirical process, remainder, or event.

Replace unnecessary labels with their meaning. For example, "instantiate the concentration machinery" can become "apply Bernstein's inequality to the centered summands" if that is the actual argument. "The error budget is closed" can become "the remainder is of smaller order than the leading term," followed by the needed comparison. Wording alone does not justify the claim.

Retain established specialist terms when they are accurate, including coupling, localization, contraction, orthogonality, leave-one-out analysis, and generic chaining. A technical word is not unnatural merely because it is advanced. Explain what it means in this application instead of substituting a vague everyday word. Likewise, do not label a term bias, variance, or a martingale difference unless it has that role.

Use direct, restrained transitions such as "For the second term," "Conditional on the training sample," or "Substituting this bound gives." Avoid promotional adjectives, invented names for routine steps, repeated announcements of progress, and unsupported "clearly" or "obviously." Do not replace them with equally empty phrases such as "a careful analysis shows."

Keep the manuscript's authorial voice. Remove assistant commentary, explanations addressed to an editor, and claims about making the text human from the proof itself. Use no long dashes in newly written prose.

## Make statistical mechanisms visible

Give extra attention to these transitions when they occur; do not impose them on unrelated proofs.

- **Conditioning and centering:** identify what is held fixed, what remains random, and why a conditional mean is zero. Cross-fitting alone is not a displayed calculation or a substitute for a residual-centering assumption. Do not infer independence between overlapping training folds.
- **Deterministic and probabilistic bounds:** indicate whether an inequality holds for every realization, on a specified event, or in expectation. When working on a high-probability event, explain how its complement is handled in the final probability statement if needed.
- **Pointwise and uniform claims:** state the relevant index set and show the device that makes the bound simultaneous. A pointwise bound does not become uniform by changing the prose.
- **Rates and constants:** show the rate before and after the theorem's normalization. When discarding or absorbing a term, give the comparison or smallness condition if it is not immediate. Keep consequential dependence on dimension, tuning parameters, or indices visible; respect established constant conventions without cataloguing irrelevant constants.
- **Invoked results:** name the result, the object to which it is applied, and the relevant hypotheses or earlier verification. For a nontrivial borrowed theorem, make parameter substitutions and the resulting bound recognizable. Use supplied or verified references; do not invent citations, theorem numbers, or stronger versions of a result.

## Calibrate to the supplied examples

[source-observations.md](references/source-observations.md) records selected proof passages from the three papers in `examples/`, with page and result anchors. Read it when calibrating overall style, explanatory depth, or a comparison with those papers. Inspect the relevant PDF pages if the exact display or wording matters. The notes support routine use without rereading all three papers.

These papers illustrate choices, not mandatory templates. Their equation-heavy passages, compressed rate arguments, and occasional awkward wording should not be copied uncritically. Transfer the explanation of purpose, intermediate calculations, and local justifications. Do not imitate an author's distinctive prose or infer that a passage is optimal because a researcher wrote it.

## Final reading and delivery

Read the revised proof as a statistics PhD student encountering the subfield's argument for the first time. Check that the manuscript itself explains the major steps, connects them to their supporting results, and makes their final combination clear. At a change of stage, ask what notation or concept the reader must recall and supply a brief reminder where needed. At each substantial construction, ask whether its purpose is apparent before the reader has to absorb its notation. At each derivation, check that successive transformations occupy separate rows, the following prose explains the key steps, and no consequential transition depends on unspoken specialist knowledge. Replace generic signposting with the missing mathematical connection.

Recheck newly written derivations and compare the theorem, assumptions, quantifiers, normalizations, convergence modes, labels, and citations with the original. Check that result titles describe their stated conclusions and that the outline uses the same descriptions. Preserve clear passages. For file edits, inspect affected rendered output when the environment supports it, especially long aligned displays and cross-references; otherwise state any material rendering limitation without implying compilation.

Deliver the requested proof or edits, with a short explanation of the main changes when useful. Keep editorial notes and unresolved mathematical issues outside manuscript-ready text. Do not burden an ordinary writing request with audit reports, style scores, equation quotas, or claims of independent proof verification.
