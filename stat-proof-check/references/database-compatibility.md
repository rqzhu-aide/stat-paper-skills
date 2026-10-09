# Compatibility

This package is stat-proof-check version 3.0.0, based on the exact 2.3.5 skill at ad40833c687932a06337188f1312f3b5492dca15.

New audits use coherent-proof-audit/1 and the coherent-examinations/1 feature. The physical database format remains 4. A shared SQL format does not imply compatible audit semantics.

Start a fresh database for this protocol. The v3 writer refuses legacy protocol mutations. Use the original compatible v2 runtime for saved v2 audits. Do not relabel an incomplete historical audit as complete under the smaller v3 task policy.

This source tree keeps its own scripts/paper_core and manifest, refreshed with scripts/build_manifest.py. It remains separate from the repository's shared core and Graphify. Install version 3.0.0 under the existing stat-proof-check skill name.
