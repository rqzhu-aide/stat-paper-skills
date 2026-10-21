# Independent practical-comparison cases

These are synthetic comparison packets, not verified publications. Method labels below identify supplied alternatives, not real bibliographic records. Use only this material and keep the cases separate.

## A. Different machinery, same practical answer

The proposal N and established procedure S target the same population mean from the same observed data under the same assumptions. Their reported confidence intervals are algebraically identical, and the supplied numerical checks confirm identical estimates, interval endpoints, and coverage across the studied settings. N uses a new representation, but takes three times the wall-clock time with the same hardware and tuning budget. No gain in robustness, usability, data requirements, interpretation, or applicable settings is identified. The manuscript advertises a new practical ability to answer this inferential question; a separate conceptual contribution of the representation remains to be assessed.

## B. Existing components, substantially cheaper implementation

Method F combines published computational components without changing the statistical estimator. The supplied numerical verification gives the same outputs within a prespecified tolerance, with matching coverage and precision over the intended workload. It reduces total wall-clock time, including tuning, from 40 minutes to 2 minutes, using the same hardware and lower peak memory. The implementation is available. The authors claim an engineering and practical contribution rather than a new inferential guarantee. The comparison uses the same data, assumptions, and information for both methods.

## C. Similar estimates, different inferential questions

The proposed method targets a simultaneous confidence band over an entire response curve under clustered sampling. The supplied alternative provides pointwise intervals under independent observations. On one dataset they produce very similar estimated curves and both reject a selected point null. The packet gives neither simultaneous coverage nor a dependence extension for the alternative. The scientific use requires statements about the entire curve with clustered observations.

## D. Theoretical contribution with prospective application

A paper supplies a shorter proof and a unifying representation of an existing guarantee. Its stated purpose is conceptual and theoretical. The theorem's output and current implementation do not change; the paper explicitly describes computational applications as future possibilities. The supplied comparisons allow examination of the proof's conceptual distinction, but no experiments demonstrate a practical gain and no practical superiority is claimed.

## E. A possible substitute with insufficient detail

The manuscript's bibliography omits an older procedure from a different method family. A supplied abstract says that it answers the same general scientific question. Its exact target, required information, assumptions, uncertainty statement, implementation, and operating regimes are unavailable. The proposal claims that existing methods cannot answer the question. No full text or independent record verification is available in this packet.

## F. A different conclusion without reliable inference

Both methods target the same estimand and report nominal 95 percent intervals under the same data model. The proposal gives narrower intervals and rejects a null that the alternative does not reject on one application. In the supplied repeated simulations with known truth, the proposal's coverage is about 85 percent and the alternative's about 95 percent; the reported Monte Carlo uncertainty is too small to explain the discrepancy. The manuscript presents the changed significance conclusion as a practical advantage, without acknowledging the coverage loss.
