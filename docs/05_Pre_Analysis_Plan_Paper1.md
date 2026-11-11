# Pre-Analysis Plan, Paper 1

**Working title:** Explaining is not intervening: a leakage-safe causal audit of explainable machine learning for e-scooter, e-bike and bicycle crash severity in France, 2020–2025.

Version 1.0, written 11 Nov 2026, before any outcome model was fitted. Its checksum is recorded in `decision_log.md`. Any later deviation is logged there with its reason.

## 1. Questions

| # | Question | Type |
|---|---|---|
| Q1 | How well can rider injury severity be predicted from crash circumstances, and how much do common validation shortcuts (random splits, global preprocessing, outcome-dependent variables) overstate that performance? | Methodological |
| Q2 | Which crash circumstances does an explainable ML model (SHAP) rank as most important for severe injury among e-scooter, e-bike and bicycle riders? | Application |
| Q3 | For a pre-specified list of factors, what is the adjusted effect on severe injury, estimated with double ML under an explicit adjustment set? | Causal |
| Q4 | Where and why do the SHAP reading and the double ML estimate of the same factor disagree? | Methodological (main contribution) |
| Q5 | Do the effects differ by mode, age, sex and setting? | Heterogeneity |
| Q6 | How fragile are the conclusions to police recording practice and to unobserved confounding? | Robustness |

## 2. Data and sample

- Source: BAAC 2019–2025, cleaned tables from Stage 3 (`data/interim/`).
- Unit: one rider (driver) of a bicycle (code 01), e-scooter-type device (code 50) or e-bike (code 80).
- Main window: crashes from 1 Jan 2020 to 31 Dec 2025, mainland France. 2019 is a sensitivity analysis because police were still adopting the new codes.
- Exclusions: non-motorised devices (code 60), riders with unknown injury level, vehicles with no rider row, overseas territories.

## 3. Outcome

- **Primary:** killed or hospitalised (injury codes 2 or 3) versus slightly injured or unhurt.
- **Secondary:** killed versus not killed. Reported only where there are at least 100 deaths in the analysed group.
- Known weakness: the "hospitalised" label is not a certified indicator and its use differs by area (4.5% of Paris e-scooter riders versus 23.7% outside the Paris region before 2023). Département is therefore an adjustment variable in every model, and robustness check R2 removes the Paris police area.

## 4. Variables

Variables are grouped into tiers by when they are determined. A factor's adjustment set contains only variables from the same or earlier tiers that it cannot affect.

| Tier | Meaning | Variables |
|---|---|---|
| 0 | Time and place | year, month, day of week, hour, département, urban or not (`agg`) |
| 1 | Rider and vehicle | mode, age, sex, trip purpose, number of passengers |
| 2 | Road and conditions | road category, traffic regime, lanes, reserved cycle facility (`vosp`), gradient, alignment, infrastructure, speed limit, intersection type, lighting, weather, surface |
| 3 | Crash configuration | position on the road (`situ`), collision type, opponent type, number of vehicles, pedestrian struck, fixed obstacle, mobile obstacle, impact point, manoeuvre |

**Never used as predictors:**
- Other people's injury levels in the same crash, including the worst pedestrian injury (derived from outcomes).
- Safety equipment and helmet status (unknown for about 60% of e-scooter riders, and suspected of being recorded more carefully in severe crashes).
- Identifiers, coordinates, commune, engine type (constant within mode), number of location rows (a file-structure artefact).

**Outcome-dependent recording check (run before modelling).** For every candidate variable, compare its unknown or missing rate between severe and non-severe riders within each mode. A variable is removed from the main feature set if the rates differ by 10 percentage points or more. Differences of 5–10 points are flagged and tested in a sensitivity analysis.

## 5. Data splits and leakage rules

| Rule | Implementation |
|---|---|
| Locked test set | Crashes in 2024–2025. Used once, after all tuning. |
| Development set | Crashes in 2020–2023. |
| Tuning | Five-fold cross-validation grouped by crash ID inside the development set. |
| Temporal check | Forward-chaining within development: train up to year y−1, validate on year y, for 2021, 2022 and 2023. |
| Preprocessing | Imputation, encoding and scaling are fitted inside each training fold through one pipeline object. |
| Double ML | Five-fold cross-fitting grouped by crash ID, repeated five times with different splits; median aggregation. |
| Seeds | Base seed 20261111. |

**Leakage quantification for Q1.** The same model is evaluated under four protocols and the differences are reported:
- (a) random row-level split with preprocessing fitted on all data;
- (b) protocol (a) plus the excluded outcome-dependent variables;
- (c) grouped by crash with in-fold preprocessing;
- (d) forward in time (the locked test).

## 6. Predictive models (Q1, Q2)

- Models: regularised logistic regression (baseline) and LightGBM gradient boosting. One pooled model with mode as a feature; mode-specific models as a sensitivity analysis.
- Tuning: random search, 30 configurations, selected on mean grouped-fold log loss.
- No resampling of classes, so predicted probabilities stay calibrated.
- Metrics: ROC AUC, precision–recall AUC, Brier score, log loss, calibration slope and intercept. All are reported overall and by mode, with bootstrap 95% intervals resampled by crash.
- SHAP: TreeSHAP on the locked test set. Global importance is mean absolute SHAP. Stability is measured as Kendall rank correlation of importance across the five grouped folds and five seeds.

## 7. Causal estimands (Q3)

All effects are conditional on a police-reported injury crash. They describe severity given that a crash was recorded, and say nothing about crash risk.

Estimator: augmented inverse-probability weighting (DoubleML interactive regression model), LightGBM for both nuisance models, propensity scores trimmed to [0.02, 0.98]. Standard errors are clustered by département from the influence function. An estimate is reported only if each arm has at least 200 riders and 30 severe outcomes.

| ID | Factor (treated vs reference) | Population | Tier | Adjusts for |
|---|---|---|---|---|
| A1 | E-scooter vs bicycle | Riders of both modes | 1 | Tier 0, other tier 1, tier 2 |
| A2 | E-bike vs bicycle | Riders of both modes | 1 | Tier 0, other tier 1, tier 2 |
| B1 | Speed limit 30 km/h or less vs 50 km/h | Urban crashes with those limits | 2 | Tiers 0–1, other tier 2 |
| B2 | Night without working street lighting vs night with lighting | Night crashes | 2 | Tiers 0–1, other tier 2 |
| B3 | Adverse weather or non-dry surface vs normal and dry | All | 2 | Tiers 0–1, other tier 2 except weather and surface |
| B4 | Reserved cycle facility present vs none | All with known `vosp` | 2 | Tiers 0–1, other tier 2 |
| B5 | Intersection vs no intersection | All | 2 | Tiers 0–1, other tier 2 |
| B6 | Urban vs outside urban area | All | 0 | Other tier 0, rider age, sex, mode |
| C1 | Opponent is a heavy vehicle vs a car | Two-party collisions with a car or heavy vehicle | 3 | Tiers 0–2 |
| C2 | Single-vehicle crash vs collision with a motor vehicle | Those two crash types | 3 | Tiers 0–2 |
| C3 | Crash on a cycle path vs on the carriageway | Those two positions | 3 | Tiers 0–2 |
| D1 | Age 65 or over vs 25–64 | Riders in those ages | 1 | Tier 0, sex, mode |
| D2 | Male vs female | Riders with known sex | 1 | Tier 0, age, mode |

A1, A2, D1 and D2 are adjusted contrasts between kinds of riders, not interventions. They are labelled that way in the paper.

Each of B1–D2 is estimated for all riders pooled and separately for each mode. Multiple testing: Benjamini–Hochberg false discovery rate at 5% across the whole family.

## 8. The audit (Q4)

For each factor, three quantities are placed side by side:

| Quantity | What it is |
|---|---|
| SHAP contrast | Mean SHAP value of the factor's raw feature among treated riders minus the mean among reference riders, on the probability scale, from the full predictive model (all tiers) |
| Model what-if | Average change in predicted probability when the factor is switched from reference to treated in the same model |
| Double ML effect | The estimate from Section 7 with its 95% interval |

A fourth estimate repeats double ML with all variables as controls, including later tiers. It separates two reasons for disagreement: adjusting for consequences of the factor, and regularisation bias in the predictive model.

Agreement is summarised by: the share of factors with the same sign; the share where the SHAP contrast lies inside the double ML interval; the ratio of magnitudes; and the Kendall rank correlation between the SHAP ranking and the double ML ranking of factors.

## 9. Heterogeneity (Q5)

- Group average effects for A1, B1 and B2 by pre-specified groups: mode, age band (under 25, 25–64, 65 and over), sex, urban or not, motor-vehicle opponent or not. Joint confidence intervals.
- A causal forest (EconML) is exploratory only: distribution of individual effects and which variables drive them.

## 10. Robustness (Q6)

| ID | Check |
|---|---|
| R1 | Include 2019 |
| R2 | Exclude the Paris police area (départements 75, 92, 93, 94) |
| R3 | Fatal outcome |
| R4 | Collisions with a motor vehicle only (better reported to police) |
| R5 | E-scooters restricted to départements with 10 or more code-50 vehicles in 2020 (early adopters) |
| R6 | Replace main-row location variables with any-row versions; and drop all location-file variables (2023 structure break) |
| R7 | Alternative nuisance learners (random forest; logistic regression) |
| R8 | Trimming at [0.01, 0.99] and [0.05, 0.95] |
| R9 | Partially linear model instead of the interactive model |
| R10 | Placebo factor: crash on an even vs odd day of the month. Expected effect: zero. |
| R11 | Sensitivity to unobserved confounding: robustness values from the DoubleML sensitivity analysis, benchmarked against the strongest observed confounder |

## 11. What has already been seen

- National rider injury levels by mode and year (counts).
- Before-2023 shares of killed-or-hospitalised e-scooter riders by area.
- Missing-value rates and code distributions by year.
- No predictive or causal model has been fitted.

## 12. Limits stated in advance

- Police data under-record single-rider and minor crashes, so the sample over-represents collisions with motor vehicles.
- Conditioning on a recorded crash can bias effects of any factor that also changes the chance of a crash being recorded.
- No exposure data: nothing here estimates risk per trip or per kilometre.
- Rental and private e-scooters cannot be separated.
