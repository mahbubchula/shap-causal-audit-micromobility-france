# Paper 1: Interim Results (11 Nov 2026)

Everything here comes from scripts 10–14 and the tables in `outputs/results/`. Robustness checks (script 15) and heterogeneity are still to be added. Effects are in percentage points of the probability that a rider is killed or hospitalised, given a police-reported injury crash.

## 1. Sample

| Mode | Development 2020–2023 | Test 2024–2025 | Killed or hospitalised |
|---|---|---|---|
| Bicycle | 20,276 | 9,764 | 27–28% |
| E-bike | 2,230 | 1,696 | 26–27% |
| E-scooter | 6,702 | 6,252 | 17–21% |
| Total | 29,208 | 17,712 | 25% |

## 2. Outcome-dependent recording

| Variable | Unknown among severe | Unknown among non-severe |
|---|---|---|
| Safety equipment | 31.7% | 54.6% |
| Trip purpose | 20.1% | 24.4% |
| Infrastructure | 2.0% | 6.7% |

Equipment status differs by up to 27 points (bicycles), so it is excluded from all models. Trip purpose and infrastructure fall in the 5–10 point band for at least one mode and are kept, pending the sensitivity analysis.

## 3. Prediction (locked test set, 2024–2025)

| Model | Group | ROC AUC (95% CI) | PR AUC | Brier | Calibration slope |
|---|---|---|---|---|---|
| LightGBM | All | 0.818 (0.811–0.825) | 0.622 | 0.138 | 0.92 |
| LightGBM | Bicycle | 0.832 (0.823–0.841) | 0.661 | 0.142 | 0.90 |
| LightGBM | E-bike | 0.847 (0.824–0.869) | 0.701 | 0.127 | 1.03 |
| LightGBM | E-scooter | 0.774 (0.760–0.788) | 0.487 | 0.135 | 0.95 |
| Logistic | All | 0.810 (0.802–0.817) | 0.602 | 0.142 | 0.88 |

## 4. Leakage comparison (same LightGBM settings)

| Protocol | ROC AUC | PR AUC | Calibration slope |
|---|---|---|---|
| (a) Random rows, all years, global preprocessing | 0.840 | 0.651 | 1.00 |
| (b) = (a) plus outcome-dependent variables | 0.843 | 0.658 | 1.01 |
| (a+) Oversample to 50:50 before splitting | 0.865 | not comparable | 1.14 |
| (c) Grouped by crash, all years | 0.839 | 0.648 | 1.00 |
| (c) Grouped by crash, development only | 0.846 | 0.655 | 0.98 |
| (d) Forward in time: train 2020–23, test 2024–25 | 0.818 | 0.622 | 0.92 |

- Grouping by crash changes almost nothing (0.840 vs 0.839): only 1,916 of 44,817 crashes involve more than one rider.
- Testing forward in time lowers ROC AUC by about 0.03 against cross-validation within 2020–2023, and calibration worsens. Part of this is a shift in composition: e-scooters are 23% of the development set and 35% of the test set.
- Oversampling before splitting inflates ROC AUC by about 0.026.

## 5. SHAP importance (locked test set)

Top ten by mean absolute SHAP (log-odds): département 0.78, age 0.31, opponent type 0.23, road category 0.15, speed limit 0.14, urban 0.13, trip purpose 0.12, collision type 0.09, hour 0.08, mode 0.08.

Stability over 25 refits (5 seeds × 5 grouped folds): Kendall rank correlation 0.88 on average (minimum 0.81); top-10 overlap (Jaccard) 0.85 on average (minimum 0.67). The top three never change rank.

## 6. Double ML estimates and the audit (pooled)

| Factor | Raw difference | SHAP contrast | Model what-if | Double ML (95% CI) | FDR q | Double ML, all controls |
|---|---|---|---|---|---|---|
| E-scooter vs bicycle | −9.0 | +1.6 | +1.1 | +2.1 (0.8 to 3.3) | 0.002 | +0.7 |
| E-bike vs bicycle | −0.7 | +3.1 | +2.7 | +5.1 (3.0 to 7.1) | <0.001 | +4.6 |
| 30 km/h or less vs 50 km/h (urban) | −11.5 | −1.7 | −2.1 | −2.0 (−3.5 to −0.6) | 0.011 | −1.8 |
| Night unlit vs night lit | +26.1 | +1.3 | +1.5 | +1.4 (−5.8 to 8.6) | 0.79 | +0.6 |
| Adverse weather or surface vs normal | −4.0 | −0.1 | −0.6 | −0.1 (−2.1 to 1.8) | 0.92 | −0.9 |
| Cycle facility present vs none | −15.7 | −0.8 | −1.2 | −2.2 (−3.8 to −0.7) | 0.011 | −1.3 |
| Intersection vs none | −8.6 | +0.4 | +1.2 | −0.2 (−1.0 to 0.6) | 0.78 | +1.0 |
| Urban vs non-urban (not reliably identified) | −42.5 | −7.3 | −6.2 | −28.2 (−37.2 to −19.2) | <0.001 | −11.3 |
| Heavy-vehicle vs car opponent | +19.8 | +17.1 | +17.0 | +17.6 (13.3 to 21.8) | <0.001 | +17.3 |
| Single-vehicle vs motor-vehicle collision | +15.3 | +9.0 | +11.2 | +12.5 (8.4 to 16.6) | <0.001 | +9.1 |
| On cycle path vs carriageway | −15.2 | −1.2 | −1.2 | −4.5 (−6.9 to −2.2) | <0.001 | −3.6 |
| Age 65+ vs 25–64 | +32.1 | +11.5 | +10.4 | +12.9 (6.4 to 19.4) | <0.001 | +8.3 |
| Male vs female | +8.3 | +1.3 | +1.4 | +2.0 (1.0 to 3.0) | <0.001 | +1.3 |

Placebo (even vs odd day of month): −0.3 (−1.0 to 0.4), as expected.

### Agreement between SHAP and double ML

| Set | Factors | Same sign | Same sign among significant | SHAP inside double ML interval | Median size ratio (SHAP ÷ double ML) | Rank correlation |
|---|---|---|---|---|---|---|
| Pooled | 13 | 92% | 100% (10 of 10) | 85% | 0.76 | 0.69 |
| Bicycle | 11 | 91% | 100% (7 of 7) | 73% | 0.71 | 0.64 |
| E-bike | 9 | 78% | 100% (1 of 1) | 89% | 0.40 | 0.50 |
| E-scooter | 10 | 60% | 100% (3 of 3) | 70% | 0.49 | 0.42 |

What the audit shows:
- SHAP and double ML agree on direction for every statistically reliable factor.
- SHAP is systematically smaller: in 85% of pooled factors, by a median of about a quarter. The gap is largest for infrastructure factors (cycle path 0.26 of the double ML size, cycle facility 0.38).
- Most of the gap appears when double ML is also made to adjust for later-tier variables (the "all controls" column moves toward SHAP). This is the cost of holding fixed things the factor itself changes.
- Raw differences are misleading in sign as well as size. E-scooter riders look 9 points less likely to be severely injured than cyclists, but in comparable circumstances they are 2 points more likely.

### Fragility

- **Urban vs non-urban** fails the overlap requirement (33% of propensity scores outside the bounds). The estimate should not be interpreted.
- **Robustness values are small for the infrastructure effects.** An unobserved confounder explaining about 1.9% (30 km/h) or 1.7% (cycle facility) of the remaining variation in both the factor and the outcome would be enough to remove the effect. Opponent type (8.7%), age (7.1%) and single-vehicle crash (6.0%) are sturdier.
- Clustering by département widens standard errors, in some cases by a factor of two to five. Unclustered errors would overstate precision.

## 7. Double ML by mode (FDR < 0.05 marked *)

| Factor | Bicycle | E-bike | E-scooter |
|---|---|---|---|
| 30 km/h or less vs 50 km/h | −2.6* | −4.2 | −0.6 |
| Cycle facility present vs none | −3.2* | +0.3 | +0.2 |
| Heavy-vehicle vs car opponent | +18.7* | not estimated | +11.6 |
| Single-vehicle vs motor-vehicle collision | +9.9* | +6.4 | +14.3* |
| On cycle path vs carriageway | −5.3* | −5.7 | −3.6 |
| Age 65+ vs 25–64 | +14.0* | +9.7 | not estimated |
| Male vs female | +1.4 | +2.0 | +3.5* |

Three mode-specific estimates were not produced because an arm had fewer than 200 riders or 30 severe outcomes.

## 8. Group average effects (script 16)

Intervals are Bonferroni-adjusted within each grouping variable. These analyses are exploratory.

| Effect | Group | Estimate (joint interval) | Test of equal effects |
|---|---|---|---|
| E-scooter vs bicycle | Male | +3.1 (1.5 to 4.6) | p = 0.003 |
| | Female | −0.9 (−3.6 to 1.8) | |
| E-scooter vs bicycle | No motor-vehicle opponent | +5.6 (2.0 to 9.2) | p = 0.004 |
| | Motor-vehicle opponent | +0.9 (−0.6 to 2.4) | |
| E-scooter vs bicycle | Non-urban | +7.4 (1.6 to 13.1) | p = 0.023 |
| | Urban | +1.3 (0.0 to 2.6) | |
| 30 km/h or less vs 50 km/h | Male | −2.8 (−4.3 to −1.3) | p = 0.007 |
| | Female | 0.0 (−2.6 to 2.6) | |
| 30 km/h or less vs 50 km/h | Age 65+ | −6.0 (−11.7 to −0.3) | p = 0.20 |
| Night unlit vs night lit | Non-urban | +23.9 (1.7 to 46.1) | p = 0.019 |
| | Urban | −0.1 (−7.5 to 7.3) | |

Of 13 tests of equal effects, only the male–female difference in the e-scooter contrast passes a Bonferroni threshold for 13 tests (0.0038).

## 9. Robustness (scripts 15 and 15b)

Estimates in percentage points. "ns" marks estimates not significant at 5%.

| Check | E-scooter vs bicycle | E-bike vs bicycle | 30 km/h | Cycle facility | Heavy opponent | Single-vehicle | Cycle path | Age 65+ | Male |
|---|---|---|---|---|---|---|---|---|---|
| Main | +2.1 | +5.1 | −2.0 | −2.2 | +17.6 | +12.5 | −4.5 | +12.9 | +2.0 |
| R1 include 2019 | +2.7 | +5.1 | −1.8 | −2.0 | +18.5 | +11.6 | −4.4 | +13.3 | +2.1 |
| R2 exclude Paris police area | +2.7 | +6.7 | −3.0 | −3.1 | +19.3 | +15.2 | −6.3 | +18.2 | +2.5 |
| R3 fatal outcome | +0.8 ns | +1.0 ns | −0.3 ns | −0.4 ns | +9.7 | +4.5 | −1.6 | +5.9 | +0.9 |
| R4 motor-vehicle collisions only | +0.6 ns | +4.5 | −1.8 | −0.9 ns | +17.6 | n/a | −5.0 | +12.3 | +1.8 |
| R5 early-adopter départements (corrected, both modes) | +0.9 ns | – | – | – | – | – | – | – | – |
| R6a any-row location variables | +2.0 | +5.1 | −2.0 | −2.2 | +17.5 | +12.5 | −4.7 | +12.9 | +2.0 |
| R6b drop location-file variables | +0.8 ns | +5.2 | −3.1 | −3.3 | +18.2 | +14.4 | −3.9 | +12.9 | +2.0 |
| R7a random forest nuisances | +1.5 | +3.9 | −2.8 | −3.8 | +17.5 | +9.6 | −5.0 | +15.0 | +2.6 |
| R7b logistic nuisances | +1.2 | +4.4 | −1.6 | −3.2 | +17.7 | +11.5 | −4.7 | +13.4 | +2.9 |
| R8 trimming 0.01 / 0.05 | +2.3 / +1.8 | +5.3 / +4.7 | −2.0 / −2.0 | −2.1 / −2.4 | +17.3 / +18.2 | +12.3 / +12.4 | −4.2 / −4.5 | +12.9 / +13.1 | +2.0 / +2.0 |
| R9 partially linear model | +2.4 | +3.4 | −2.4 | −1.7 | +16.7 | +11.3 | −2.2 | +15.8 | +2.0 |

- Unlit night, adverse weather and intersections remain null throughout, with two isolated exceptions (unlit night under the partially linear model; intersections for the fatal outcome).
- **Sturdy:** heavy-vehicle opponent, single-vehicle crash, cycle path, age 65+ and male sex keep their sign and significance in every check, including the fatal outcome.
- **Hold for the main outcome but not for deaths:** e-bike vs bicycle, 30 km/h, cycle facility. Deaths are rare, so this may reflect power as much as substance.
- **Fragile:** e-scooter vs bicycle. It is positive in every valid check (+0.6 to +2.7) but loses significance for deaths, for motor-vehicle collisions only, without location-file variables, and within early-adopter départements (+0.9, interval −0.4 to 2.2). Outside those départements it is +3.1 (0.9 to 5.3). The raw difference is −0.1 inside early-adopter départements and −14.1 outside.

### Sensitivity to an unobserved confounder as strong as département (R11)

| Factor | Estimate | Robustness value | Shift from a département-strength confounder |
|---|---|---|---|
| E-scooter vs bicycle | +2.1 | 1.4% | 0.5 |
| E-bike vs bicycle | +5.1 | 3.4% | 0.9 |
| 30 km/h or less | −2.0 | 1.9% | 3.9 |
| Cycle facility | −2.2 | 1.7% | 2.0 |
| Heavy-vehicle opponent | +17.6 | 8.7% | 0.4 |
| Single-vehicle crash | +12.5 | 6.0% | 6.2 |
| Cycle path | −4.5 | 1.8% | 1.0 |
| Age 65+ | +12.9 | 7.1% | 8.8 |
| Male | +2.0 | 2.1% | 1.5 |

A hidden confounder as strong as département could remove the 30 km/h and cycle-facility effects, and most of the male effect. It would not remove the opponent, single-vehicle, cycle-path, age, e-bike or e-scooter estimates.

## 10. Agreement statistics as reported in the paper (added 11 Nov 2026)

The paper reports agreement between SHAP and double ML without the urban vs non-urban contrast, which fails the overlap condition (deviations D4 and D7). These figures replace the 13-factor summary in Section 6 wherever the two differ.

| Set | Estimates | FDR < 0.05 | Same sign, all | Same sign, FDR < 0.05 | SHAP inside 95% CI | Median ratio, FDR < 0.05 |
|---|---|---|---|---|---|---|
| All riders | 12 | 9 | 11/12 | 9/9 | 11/12 | 0.72 |
| Bicycle | 10 | 6 | 9/10 | 6/6 | 8/10 | 0.75 |
| E-bike | 8 | 0 | 6/8 | – | 8/8 | – |
| E-scooter | 9 | 2 | 5/9 | 2/2 | 7/9 | 0.52 |
| All estimates | 39 | 17 | 31/39 | 17/17 | 34/39 | 0.71 |

Descriptive additions (deviation D8), 12 factors, all riders:
- Slope of the SHAP contrast on double ML: 0.83 with the pre-specified adjustment set, 0.97 with all controls.
- Mean absolute difference from double ML: SHAP 1.20 points (pre-specified) and 0.90 (all controls); model what-if 1.23 and 0.90.
- Kendall rank correlation with the double ML ranking: SHAP 0.73, model what-if 0.58, unadjusted difference 0.39.

Tables are built by `scripts/21_tables.py` and written to `tables/` (CSV, LaTeX, Excel, Markdown preview).
