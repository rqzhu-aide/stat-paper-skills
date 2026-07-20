# Introduction Guidance

## Job of the section

Make the contribution necessary before making it impressive. By the end, the reader should know the target, what current approaches already provide, the unresolved obstacle, the paper's key move, the evidence promised, and the scope.

## Diagnose the current draft

Identify the first failure:

- context begins too broadly and takes too long to reach the problem;
- a method name appears before the statistical need;
- the gap is only "no one has done this";
- related work is an author-by-author chronology;
- the contribution list contains several unranked claims;
- the introduction promises theory, computation, or robustness not delivered later;
- notation arrives before the reader understands its purpose.

Repair the earliest failure before polishing later paragraphs.

## Core architecture

Use these functions, not necessarily one paragraph per function:

1. **Target:** State the scientific, inferential, predictive, or interpretive goal.
2. **Current capability:** Explain what established approaches already do well.
3. **Obstacle:** Name the precise mismatch, failure, cost, or unresolved question.
4. **Key move:** Give the paper's central idea without full technical detail.
5. **Evidence contract:** State what the theory and experiments will establish.
6. **Contribution and scope:** Rank the contributions and state the principal boundary.

The gap should be a missing capability, not merely a missing publication. Examples include an unavailable observable target, invalid inference after selection, a computational bottleneck, unstable interpretation, or theory that applies only to an oracle object.

## Related work

Organize literature by question, assumption, or methodological distinction. For each cluster, state:

1. what is established;
2. what remains unavailable for the present target;
3. how the proposed work differs;
4. what idea or tool is retained from prior work.

Do not weaken prior work to manufacture novelty.

## Contribution paragraph

Rank contributions by dependency. A useful order is:

1. conceptual or statistical target;
2. method or construction;
3. theoretical guarantee;
4. computational or empirical consequence.

If the contributions are independent, provide a genuine unifying claim or reconsider whether they belong in one manuscript. If they depend on one another, state that dependency.

## If a presentation mode is needed

- **Compact and direct:** Reach the obstacle quickly, compress background, and give a short ranked contribution paragraph.
- **Explanatory and intuition-led:** Expose the structural tension through a representative regime or nearby-regime contrast that retains the paper's hard part, then introduce the key move after the failure is visible.
- **Formal and structure-led:** Define the inferential regime and distinguish target, oracle, and feasible object early. Preview the theorem chain precisely.
- **Evidence-led and comparative:** Open with the decision or performance question, define the comparison criteria, and state what later evidence must show.

## Abstract connection

For an abstract, compress the same logic into one movement:

`target -> limitation -> key move -> main result -> evidence -> boundary`

Avoid section previews, dense contribution counts, unexplained acronyms, and tuning details.

## Review checklist

- Can a reader state the problem and main contribution after one reading?
- Does the obstacle logically create the need for the key move?
- Is related work organized around the present question?
- Are contributions ranked and supported later?
- Is the main boundary visible before the paper begins to generalize?
- Is the selected mode appropriate for the audience and conceptual depth?
