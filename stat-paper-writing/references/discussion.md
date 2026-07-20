# Discussion Guidance

## Job of the section

Explain what the paper changes in statistical understanding or practice, how strongly the evidence supports that change, where it stops, and what follows next.

## Diagnose the current draft

Look for:

- a repetition of the abstract or contribution list;
- a generic paragraph claiming broad impact;
- limitations detached from the claims they weaken;
- future work listed without connection to unresolved mechanisms;
- practical recommendations stronger than the theory or experiments support;
- no distinction between conceptual and practical contribution.

## Core architecture

Use these functions:

1. **Main understanding:** State the central statistical lesson, not only the method name.
2. **Practical capability:** Explain what analysis, decision, or computation is now possible.
3. **Evidence strength:** Distinguish what is proved, simulated, observed, or conjectured.
4. **Use conditions:** State when the method is most informative or appropriate.
5. **Limitations by mechanism:** Identify which link weakens and how conclusions change.
6. **Transferability:** Separate components that transfer directly from those needing a new target, nuisance model, algorithm, or proof.
7. **Next question:** Derive future work from a concrete unresolved issue.

## Limitations

Attach each limitation to a claim. Useful forms include:

- the target omits a component relevant in some settings;
- the theorem applies to an oracle rather than the feasible procedure;
- robustness is demonstrated only over a limited perturbation set;
- computation scales poorly in a governing dimension;
- interpretation is associational rather than causal;
- the empirical study cannot distinguish two mechanisms.

State direction when known: conservative, anti-conservative, unstable, unidentified, or computationally prohibitive.

## Future work

For each extension, state what new ingredient is required. Avoid saying only that the method could be extended to more models or data.

## If a presentation mode is needed

- **Compact and direct:** Give the main lesson, practical condition, strongest limitation, and next step without retelling results.
- **Explanatory and intuition-led:** Return to the motivating tension and synthesize which mechanism, dependence path, or tradeoff the paper has clarified.
- **Formal and structure-led:** Separate proved scope, unproved extensions, assumption-sensitive claims, and open theoretical links.
- **Evidence-led and comparative:** Summarize what the comparisons establish, where results are uncertain, and what decision changes under the evidence.

## Review checklist

- Does the discussion add synthesis rather than summary?
- Are conceptual and practical contributions distinguished?
- Is every limitation connected to a central claim?
- Are recommendations calibrated to the evidence?
- Does future work identify the missing mathematical, computational, or empirical ingredient?
- Is the selected mode consistent with the paper's depth and audience?
