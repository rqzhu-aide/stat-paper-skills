# Independent offline comparison packets

These are hypothetical manuscripts and comparator excerpts supplied for review. They are not verified bibliographic records. Do not search externally or combine the cases into one paper.

## A. Same interval, different implementation

Manuscript N observes iid variables X_i in [0,1] and targets their common mean mu. For each alpha in (0,1), it returns the sample mean plus or minus sqrt(log(2/alpha)/(2n)), claiming coverage at least 1-alpha under the stated assumptions. Its implementation makes three passes through the sample. It claims the first available finite-sample interval for this target and a new practical capability. A separate contribution claim concerns an alternative proof organization.

The supplied comparator S, uncited in N, states the same assumptions, target, interval formula, and coverage guarantee, and computes the interval in one pass. Its relevant method and theorem text are provided in full here; its publication date and bibliographic identity are not independently verified. A supplied matched comparison reports identical interval endpoints, 3 seconds for N versus 1 second for S, and no difference in memory or required inputs. No evidence about robustness or ease of implementation is supplied.

Request: Assess overlap, remaining practical usefulness, and what can be concluded about novelty. Include a novelty score if supportable, otherwise state its status. Do not infer publication priority from the packet order.

## B. Established components, unresolved development

Manuscript J combines an existing interval construction with an existing calibration routine to claim simultaneous coverage under clustered sampling. The manuscript calls the combination immediate but does not supply the argument establishing that the calibration routine remains valid under its dependence assumptions. Its stated target and assumptions are clear.

The supplied abstract of comparator T says it constructs simultaneous bands for clustered observations. Its exact dependence conditions, construction, and proof are unavailable. Neither the manuscript nor the abstract resolves whether T already achieves J's claimed capability, or whether making J's components work together requires a nontrivial new argument. No other comparator is supplied.

Request: Assess whether J is an enabling combination or a convenience assembly, explain the evidence for your judgment, and give a novelty score if supportable. Use only this packet.

## C. Positioning without comparator content

Manuscript P's introduction says its estimator is the first to combine adaptive weighting with interval estimation. It supplies no references, comparator statements, algorithm details, theorem, or empirical comparison. The claimed target is a conditional mean in a sparse regression model.

Request: Assess what the supplied material establishes about distinctiveness and practical value, and state whether a novelty score is supportable. Use only this excerpt.
