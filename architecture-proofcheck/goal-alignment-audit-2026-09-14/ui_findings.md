# UI and retrieval alignment audit

Read-only production inspection and synthetic probes, 2026-09-14. No production files changed. Browser visual acceptance was not performed because the earlier local-HTML URL-policy restriction remains in force. These measurements do not establish browser load time or explain the earlier 20-hour run.

## 1. Local checks still retrieve the whole owning theorem

`packets.py:20,395-398` accepts only paper, item, part, and audit targets. An argument target is rejected. `statement_closure` at `packets.py:184-215` widens an intermediate item or a statement part to the owning major item, gathers all its parts and intermediate items, and then includes all their arguments.

The 100-step, 30-supplier probe requested only `items:itm_hidden0`. Its packet still contained 466 records and all 101 arguments, occupying 426,195 JSON bytes. Requesting `arguments:arg_0` instead returned the target-collection rejection. Checking many individual derivations would repeatedly retrieve this whole family.

Recommendation: allow a local argument/group/use as the work target, include that target's needed suppliers, scope, and source evidence, and reserve whole-theorem closure for whole-theorem composition or coverage work. Keep the current major-only visual graph.

## 2. The reader expands shared canonical records into many full copies

Canonical bodies are deduplicated by `projection.py:157-160`; this part is appropriate. Every boundary connection separately traces the shared hidden proof (`projection.py:589`). Each connection detail includes those shared records (`projection.py:514-558`). The renderer then emits all detail sections and full record bodies eagerly (`render_projection.mjs:894-897,902-911,957-1000`), even though only the selected detail is normally visible.

| Synthetic structure | Unique stored records | Full rendered record blocks | HTML bytes | Parsed elements |
| --- | ---: | ---: | ---: | ---: |
| 100 hidden steps, 10 suppliers | 426 | 4,706 | 9,210,762 | 176,950 |
| 100 hidden steps, 30 suppliers | 466 | 14,506 | 26,528,251 | 551,942 |

The canonical record count rises by 40, while the page grows by 17.3 MB because many connections share the same proof. The visible graph still contains only 31 major nodes in the larger case. Node render times were about 0.42 and 1.13 seconds, respectively, so the measured issue is eager duplicated page/DOM content, not a demonstrated slow renderer or browser.

Recommendation: retain canonical bodies and complete trace references once in the embedded dataset, then populate the existing lower reader for the selected item/connection. Generate full print content only when requested. Merely caching HTML strings would reduce repeated formatting but leave the large output and DOM unchanged.

## Supplement for the root worklist audit

The small unfinished probe had 14 unsatisfied obligations. `status` returned opaque IDs without target/kind metadata (`queries.py:181-182`). The selected missing obligation appeared in 15 code labels and zero links. Running the actual generated `buildIndex` function against the emitted record sections found zero search matches for that ID. This follows `render_projection.mjs:652` (plain missing-obligation labels) and `1840-1867` (search indexes record bodies/locations, not obligations). Root is covering the worklist recommendation.

## Reproduction

Run `ui_probe.py` in this directory using the shared Python runtime; it invokes `ui_inspect.mjs` through the shared Node runtime. All synthetic databases and render-input JSON are prefixed `ui_` here. Synthetic bodies are shape-validated and supplied with reference/facet indexes; this is a deterministic structural probe, not a manuscript verification run. Aggregate measurements are in `ui_results.json`.
