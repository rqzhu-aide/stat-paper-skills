# Statistical Paper Skills

Two independent, complementary Codex skills for statistics and machine-learning manuscripts.

| Skill | Version | Purpose |
|---|---|---|
| `stat-paper-writing` | v1.0 | Claim-preserving drafting, restructuring, polishing, and statistical-register repair |
| `stat-paper-reviewer` | v1.0 | Sequential review with novelty checks and a cautious AI-shaped prose alarm |

## Install

Copy either complete skill folder, or both folders, into your Codex skills directory. Keep each folder's `agents`, `references`, `scripts`, and license files together. The usual destination is `$CODEX_HOME/skills/`, or `~/.codex/skills/` when `CODEX_HOME` is unset.

Example invocations:

- `Use $stat-paper-writing to restructure this methods section without changing its mathematical claims.`
- `Use $stat-paper-reviewer to review this manuscript as a critical first-time statistical reader.`
- `Use $stat-paper-reviewer to assess whether recurrent patterned prose weakens claim traceability, without inferring authorship.`

External literature verification needs network access. The reviewer's bundled OpenAlex fallback also requires a [free API key](https://openalex.org/settings/api), preferably supplied through the `OPENALEX_API_KEY` environment variable.

## Requests for both review and revision

Treat review and revision as two independently authorized stages. Complete the referee diagnosis first with `stat-paper-reviewer`; if manuscript revision is also requested, use `stat-paper-writing` afterward against the supplied manuscript and bounded findings. The reviewer does not draft or edit manuscript text, and the writer does not make referee judgments. A request for only one stage does not authorize the other.

## Related resources

These projects informed the bundle or provide complementary paper-writing workflows:

- [maweiruc/proofread-stat-paper](https://github.com/maweiruc/proofread-stat-paper): grammar and technical review for LaTeX statistics papers.
- [fuhaoda/stats-paper-writing-agent-skills](https://github.com/fuhaoda/stats-paper-writing-agent-skills): statistical-paper drafting, auditing, and revision workflows.
- [brycewang-stanford/Auto-Empirical-Research-Skills](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills): a broader collection of skills for empirical research.
- [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills): reusable research skills for paper reading, writing, review, and scientific figures.

## Sources and licenses

- The reviewer's OpenAlex fallback is adapted from [wp-a/nature-academic-search](https://github.com/wp-a/nature-academic-search); its MIT notice is retained.
- Broad-interest checks are informed by [Nature's editorial criteria](https://www.nature.com/nature/for-authors/editorial-criteria-and-processes).
- Writing guidance also draws on comparative reading of published statistical-methods papers.

Original bundle content is released under the root MIT license. The retained upstream notice applies to the adapted reviewer component.
