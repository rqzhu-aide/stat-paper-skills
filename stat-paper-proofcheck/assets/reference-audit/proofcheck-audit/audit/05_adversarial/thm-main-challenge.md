# Independent challenge for `thm:main`

Working only from the blinded packet, I checked lines 26-30 against the normalized obligation. Lines 27-28 name Lemma 1's conclusion in exactly the registered form; line 29 consumes it through use D001, substitutes hat-theta_n - theta_0 = max_{1<=j<=m_n} |X_{n,j}| exactly from the stated definition, and folds the convergence-in-probability definition. The algebra is exact, so the only mathematical input is the refuted growing-maximum claim; nothing in this proof supplies independent control of the maximum. The written proof therefore leaves the conclusion not established. Verdict: gap.

<!-- proofcheck-challenge-binding-v1
{
  "schema_version": 1,
  "unit_id": "thm:main",
  "challenge_context_sha256": "f7c2f6125c838ad36a6cdfa4863db16802c368e7143522b046145715868f04bc",
  "challenger_verdict": "gap",
  "issue_assessments": [
    {
      "issue_id": "I-001",
      "target_contract_sha256": "2c1ef625adc0687b3a28e6316d2729c3cb809a138836cb444b1a8f049f548ec7",
      "assessment": "confirmed",
      "target_assessment": "The neutral target for thm:main is the growing-maximum premise consumed on line 29 through use D001. Re-derivation confirms the premise is exactly Lemma 1's refuted conclusion, and lines 26-30 supply no independent control of the maximum, so the target defect is confirmed at this unit.",
      "downstream_assessment": "thm:main has no recorded downstream uses; the propagation terminates here with the conclusion not established."
    }
  ]
}
-->
