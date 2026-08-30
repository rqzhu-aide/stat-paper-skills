# Introduction Guidance

## Job of the section

Make the contribution necessary before making it impressive. By the end, the reader should know the target, what current approaches provide according to supplied sources, the unresolved obstacle, the paper's key move, the evidence promised, and the scope.

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
2. **Current capability:** Explain what supplied established approaches already do well.
3. **Obstacle:** Name the precise mismatch, failure, cost, or unresolved question supported by the available material.
4. **Key move:** Give the paper's central idea without full technical detail.
5. **Evidence contract:** State what the formal results and experiments are reported to establish.
6. **Contribution and scope:** Rank the supported contributions and state the principal boundary.

The gap should be a missing capability, not merely a missing publication. Examples include an unavailable observable target, invalid inference after selection, a computational bottleneck, unstable interpretation, or a stated result that applies only to an oracle object.

## Related work

Organize literature by question, assumption, or methodological distinction. For each cluster, state:

1. what the supplied sources establish;
2. what remains unavailable for the present target according to those sources;
3. how the proposed work differs;
4. what idea or tool is retained from prior work.

Do not weaken prior work or extrapolate beyond supplied sources to manufacture novelty.

## Contribution paragraph

For contribution identities, hierarchy, dependency, and rank, load [argument-architecture.md](argument-architecture.md). Do not infer a contribution identity from a theorem, estimator, experiment, or section topic.

## Abstract connection

For an abstract, compress the same logic into one movement:

`target -> limitation -> key move -> main result -> evidence -> boundary`

Avoid section previews, dense contribution counts, unexplained acronyms, and tuning details.

## Review checklist

- Can a reader state the problem and main contribution after one reading?
- Does the stated obstacle create the need for the key move?
- Is related work organized around the present question?
- Are contributions ranked and visibly supported later?
- Is the main boundary visible before the paper begins to generalize?
- Are novelty and priority claims limited to the supplied evidence?
