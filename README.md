# Statistical Paper Skills

Three independent, complementary Codex skills for statistics and machine-learning manuscripts.

| Skill | Version | Purpose |
|---|---|---|
| `stat-paper-writing` | v1.0 | Claim-preserving drafting, restructuring, polishing, and statistical-register repair |
| `stat-paper-reviewer` | v1.0 | Sequential review with novelty checks and a cautious AI-shaped prose alarm |
| `stat-paper-proofcheck` | v1.0 | Source-locked, line-by-line non-formal proof auditing with explicit dependency closure |

## Install

Copy any complete skill folder, or all three folders, into your Codex skills directory. Keep each folder intact, including its `agents`, references, scripts, assets, tests, and license files where present. The usual destination is `$CODEX_HOME/skills/`, or `~/.codex/skills/` when `CODEX_HOME` is unset.

Example invocations:

- `Use $stat-paper-writing to restructure this methods section without changing its mathematical claims.`
- `Use $stat-paper-reviewer to review this manuscript as a critical first-time statistical reader.`
- `Use $stat-paper-reviewer to assess whether recurrent patterned prose weakens claim traceability, without inferring authorship.`
- `Use $stat-paper-proofcheck to audit this theorem and its dependency closure line by line.`

External literature verification needs network access. The reviewer's bundled OpenAlex fallback also requires a [free API key](https://openalex.org/settings/api), preferably supplied through the `OPENALEX_API_KEY` environment variable.

The proofcheck helper and tests require Python 3.10 or newer and otherwise use only the Python standard library. Run its regression suite from the repository root with:

```bash
python -m unittest discover -s stat-paper-proofcheck/tests -p "test_*.py"
```

## Choosing and combining skills

Treat review, revision, and proof verification as independently authorized stages. Use `stat-paper-reviewer` for referee diagnosis, `stat-paper-writing` for drafting or presentation editing, and `stat-paper-proofcheck` for proof validity. For a combined request, complete the diagnostic stage before any authorized revision. The reviewer and proofchecker do not edit manuscript text, while the writer does not make referee judgments or assess proof validity. The proofchecker performs a rigorous non-formal audit and does not produce a Lean or kernel-checked certificate.

## Related resources

These projects informed the bundle or provide complementary paper-writing workflows:

- [maweiruc/proofread-stat-paper](https://github.com/maweiruc/proofread-stat-paper): grammar and technical review for LaTeX statistics papers.
- [fuhaoda/stats-paper-writing-agent-skills](https://github.com/fuhaoda/stats-paper-writing-agent-skills): statistical-paper drafting, auditing, and revision workflows.
- [brycewang-stanford/Auto-Empirical-Research-Skills](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills): a broader collection of skills for empirical research.
- [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills): reusable research skills for paper reading, writing, review, and scientific figures.

## Sources and licenses

- The reviewer's OpenAlex fallback is adapted from [wp-a/nature-academic-search](https://github.com/wp-a/nature-academic-search); its MIT notice is retained.
- The proofcheck skill carries its own retained MIT notice in [`stat-paper-proofcheck/LICENSE`](stat-paper-proofcheck/LICENSE).
- Broad-interest checks are informed by [Nature's editorial criteria](https://www.nature.com/nature/for-authors/editorial-criteria-and-processes).
- Writing guidance also draws on comparative reading of published statistical-methods papers.

Original bundle content is released under the root MIT license. Retained notices in individual skill folders continue to apply to their respective contents.
