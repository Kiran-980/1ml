# forecasting

## Forecasting and time series

**Documented:** Forecast evaluation must train on information preceding each forecast origin. Rolling-origin evaluation can measure the actual multi-step horizon. Naive and seasonal-naive methods are benchmarks. Point, quantile, and distributional forecasts have different scoring requirements. Percentage errors can be unsuitable near zero; scaled errors require a meaningful baseline denominator. [Forecasting: Principles and Practice, chapter 5](https://otexts.com/fpp3/toolbox.html)

**Decision synthesis:** First specify entity, time frequency, origin, horizon, update cadence, and which covariates are available at prediction time. Compare naive/seasonal-naive with trend/seasonality models, lag-feature models, and appropriately supported global models. Recompute lag/rolling features within each fold with strictly historical inputs. Evaluate every business-relevant horizon; a one-step score does not validate a month-ahead decision. Forecast unknown future covariates separately or use explicit scenarios; do not feed realized future values into evaluation. Decide whether the deployment predicts future values for known series, entirely new series, or both, and split accordingly.

**Additional documented branches:** Daily/subdaily data can have multiple seasonalities; moving holidays need explicit treatment. Very short histories restrict feasible complexity. Long histories can contain changing relationships. Missingness and outliers require contextual handling. [FPP chapter 13](https://otexts.com/fpp3/practical.html)

**Decision synthesis:** Separate missing observation from genuine zero demand, and demand from sales limited by stockouts. For intermittent/low counts, compare count/intermittent-demand approaches and evaluate stock/service consequences; do not choose a method from skew alone. For hierarchical totals, require coherent aggregate forecasts and score both levels. Escalate unsupported events, unavailable historical covariate vintages, or insufficient seasonal coverage rather than inventing confidence.

### Forecast model choices and evaluation exceptions

Resolve the following choices when the selected task is forecasting:

| Evidence and objective | Forecast candidate/design | Follow-up if it fails |
|---|---|---|
| Level/trend/seasonality is the main predictable structure | Compare an appropriate exponential-smoothing/ETS model with naive baselines | Inspect changing seasonality, short history, outliers, and residual dependence |
| Serial correlation remains important | Compare ARIMA/seasonal ARIMA with justified differencing and order selection | Check residual structure and horizon errors; avoid endless differencing/search to force a diagnostic result |
| Known/planned drivers or lagged predictors add information | Regression/dynamic regression or a lag-feature learner | Validate driver availability and scenarios; add an error process only when its assumptions fit |
| Many related short series | Compare pooled/global learning with local baselines and cold-start cohorts | Check whether pooling transfers useful information or hides heterogeneous series |
| Many intermittent/low-count observations | Compare methods designed for that process and the ordering/service objective | Verify zeros/stockouts/exposure; avoid a universal percentage-error ranking |

ETS represents level/trend/seasonal components while ARIMA models temporal autocorrelation; they are complementary candidates, not a hierarchy determined by a normality test. [FPP ARIMA and ETS](https://otexts.com/fpp3/arima.html)

For stationarity-dependent choices, ADF tests a unit-root null, while KPSS tests level/trend stationarity depending on its configuration. Lag/trend specification, finite sample size, and structural change affect interpretation. Conflicting/non-significant results call for diagnostic investigation and forecast comparison, not proof of stationarity or a fixed transform rule. Other models can directly represent trends, so neither test is a universal forecasting gate. [ADF](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html), [KPSS](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.kpss.html)

At a fixed origin, a seven-step recursive forecast must use its own predicted intermediate targets when those targets are unavailable. A rolling one-step evaluation may use a newly observed target only after its real arrival time. Both are valid for different deployment schedules; do not present the latter as fixed-origin seven-step performance. Direct horizon models are another candidate. Reproduce any refitting/update cadence in backtests.

Known calendar values and genuinely committed plans can be used for future timestamps. Realized future weather/sales/revised economic statistics cannot be treated as known at the origin. Scenario-conditioned intervals do not automatically include uncertainty about the assumed future drivers; distinguish them from full predictive uncertainty. [FPP regression forecasting](https://otexts.com/fpp3/regression.html)

For a selected forecast path, return to [metric aggregation](../../skills/evaluation/references/metrics-policy.md#27-aggregation-and-incomplete-targets) and [system validation](../../skills/validate/references/system-evidence.md). If timing/driver support is missing, return to acquisition; do not proceed just because a forecaster fit successfully.
