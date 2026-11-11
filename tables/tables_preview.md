# Tables, Paper 1

Produced by `scripts/21_tables.py` from saved results. Each table is also written as CSV (`csv/`), LaTeX (`tex/`) and as a sheet of `Tables_Paper1.xlsx`.


## Table 1. Data sources: the four annual files of the French national police crash database (BAAC), 2019–2025

| File | Unit of observation | Records, 2019–2025 | Variables used |
|---|---|---|---|
| Characteristics | Crash | 382,721 | Date and time, lighting, weather, département, urban area, intersection type, collision type |
| Locations | Road record (one per crash until 2022; one or more from 2023) | 430,628 | Road category, traffic regime, number of lanes, reserved lane, gradient, alignment, infrastructure, position of the crash, surface condition, speed limit |
| Vehicles | Vehicle | 653,712 | Vehicle category, maneuver before the crash, fixed and mobile obstacle struck, point of initial impact |
| Users | Person | 871,534 | Role, injury severity, sex, year of birth, trip purpose, safety equipment |

*Source: Observatoire national interministériel de la sécurité routière, open data portal data.gouv.fr, Licence Ouverte 2.0.*

*Files are linked on the crash identifier; users are linked to vehicles on the vehicle identifier. *

*Derivation of the analysis sample: 382,721 injury crashes involving any road user; 55,909 micromobility vehicles; 54,580 bicycles, e-bikes or e-scooters; 52,722 in mainland France; 52,510 with the injury level of the rider recorded; 46,920 riders in crashes from 2020 to 2025.*


## Table 2. Composition of the study sample by data partition and transport mode

| Partition | Mode | Riders | Crashes | Killed or hospitalized, n (%) | Killed, n (%) |
|---|---|---|---|---|---|
| Development set, 2020–2023 | Bicycle | 20,276 | 19,410 | 5,560 (27.4) | 756 (3.7) |
| Development set, 2020–2023 | E-bike | 2,230 | 2,198 | 612 (27.4) | 112 (5.0) |
| Development set, 2020–2023 | E-scooter | 6,702 | 6,654 | 1,118 (16.7) | 106 (1.6) |
| Development set, 2020–2023 | All riders | 29,208 | 27,917 | 7,290 (25.0) | 974 (3.3) |
| Locked test set, 2024–2025 | Bicycle | 9,764 | 9,328 | 2,728 (27.9) | 396 (4.1) |
| Locked test set, 2024–2025 | E-bike | 1,696 | 1,661 | 442 (26.1) | 62 (3.7) |
| Locked test set, 2024–2025 | E-scooter | 6,252 | 6,190 | 1,287 (20.6) | 123 (2.0) |
| Locked test set, 2024–2025 | All riders | 17,712 | 16,900 | 4,457 (25.2) | 581 (3.3) |
| Sensitivity analysis, 2019 | Bicycle | 4,727 | 4,578 | 1,367 (28.9) | 172 (3.6) |
| Sensitivity analysis, 2019 | E-bike | 248 | 246 | 92 (37.1) | 15 (6.0) |
| Sensitivity analysis, 2019 | E-scooter | 615 | 611 | 95 (15.4) | 10 (1.6) |
| Sensitivity analysis, 2019 | All riders | 5,590 | 5,404 | 1,554 (27.8) | 197 (3.5) |

*Riders of bicycles, e-bikes and motorized personal mobility devices (e-scooters) involved in police-reported injury crashes in mainland France.*

*A crash may involve riders of more than one mode; the number of crashes in the row for all riders is therefore smaller than the sum over modes.*


## Table 3. Explanatory variables by temporal tier

| Tier | Variable | Source file | Type | Definition | Unknown (%) |
|---|---|---|---|---|---|
| 0: time and place | Year | Characteristics | Numeric, 2020–2025 | Year of the crash | 0.0 |
| 0: time and place | Month | Characteristics | Numeric, 1–12 | Month of the crash | 0.0 |
| 0: time and place | Day of week | Characteristics | Numeric, 0–6 | Derived from the date of the crash | 0.0 |
| 0: time and place | Hour of day | Characteristics | Numeric, 0–23 | Hour of the crash | 0.0 |
| 0: time and place | Département | Characteristics | Categorical, 96 levels | Département in which the crash occurred | 0.0 |
| 0: time and place | Urban area | Characteristics | Binary | Crash inside a built-up area | 0.0 |
| 1: rider and vehicle | Transport mode | Vehicles | Categorical, 3 levels | Bicycle, e-bike or motorized personal mobility device | 0.0 |
| 1: rider and vehicle | Age | Users | Numeric, 0–97 | Year of the crash minus year of birth | 1.4 |
| 1: rider and vehicle | Sex | Users | Categorical, 2 levels | Sex of the rider | 1.2 |
| 1: rider and vehicle | Trip purpose | Users | Categorical, 6 levels | Purpose of the trip at the time of the crash | 23.8 |
| 1: rider and vehicle | Passengers | Users | Numeric, 0–3 | Number of other occupants of the rider's vehicle | 0.0 |
| 2: road and conditions | Road category | Locations | Categorical, 8 levels | Administrative category of the road | 0.0 |
| 2: road and conditions | Traffic regime | Locations | Categorical, 4 levels | One-way, two-way or divided roadways | 6.6 |
| 2: road and conditions | Number of lanes | Locations | Numeric, 1–12 | Total number of traffic lanes | 7.1 |
| 2: road and conditions | Cycle facility | Locations | Categorical, 4 levels | Presence and type of a reserved lane (cycle path, cycle lane, other reserved lane) | 2.6 |
| 2: road and conditions | Gradient | Locations | Categorical, 4 levels | Longitudinal profile of the road | 0.0 |
| 2: road and conditions | Alignment | Locations | Categorical, 4 levels | Horizontal alignment of the road | 0.0 |
| 2: road and conditions | Infrastructure | Locations | Categorical, 9 levels | Special infrastructure at the site (tunnel, bridge, roundabout approach and others) | 5.4 |
| 2: road and conditions | Speed limit | Locations | Numeric, 5–110 | Maximum authorized speed at the site, km/h | 3.1 |
| 2: road and conditions | Intersection type | Characteristics | Categorical, 9 levels | Type of intersection, or none | 0.0 |
| 2: road and conditions | Lighting | Characteristics | Categorical, 5 levels | Daylight, twilight, or night with or without working street lighting | 0.0 |
| 2: road and conditions | Weather | Characteristics | Categorical, 9 levels | Atmospheric conditions | 0.0 |
| 2: road and conditions | Surface condition | Locations | Categorical, 9 levels | Condition of the road surface | 0.0 |
| 3: crash configuration | Position on road | Locations | Categorical, 7 levels | Position of the crash (roadway, cycle path, sidewalk and others) | 0.0 |
| 3: crash configuration | Collision type | Characteristics | Categorical, 7 levels | Type of collision | 0.8 |
| 3: crash configuration | Opponent type | Vehicles | Categorical, 10 levels | Category of the other party, derived from the other vehicles and pedestrians in the crash | 0.0 |
| 3: crash configuration | Vehicles involved | Vehicles | Numeric, 1–4 | Number of vehicles in the crash (four or more grouped) | 0.0 |
| 3: crash configuration | Pedestrian struck | Users | Binary | At least one pedestrian struck by the rider's vehicle | 0.0 |
| 3: crash configuration | Fixed obstacle | Vehicles | Categorical, 18 levels | Fixed obstacle struck | 0.0 |
| 3: crash configuration | Mobile obstacle | Vehicles | Categorical, 7 levels | Mobile obstacle struck | 0.1 |
| 3: crash configuration | Point of impact | Vehicles | Categorical, 10 levels | Point of initial impact on the vehicle | 0.1 |
| 3: crash configuration | Maneuver | Vehicles | Categorical, 26 levels | Main maneuver before the crash | 8.5 |

*Unknown (%) is the share of the 46,920 riders in the analysis sample (2020–2025) for whom the variable is not recorded. Unknown values are retained as a separate category or as missing values handled by the learner; no value is imputed outside the training folds.*

*Safety equipment, the injury severity of other persons, identifiers and coordinates are excluded from all models (Figure 4).*


## Table 5. Characteristics of riders and crashes by transport mode, 2020–2025

| Characteristic | Bicycle | E-bike | E-scooter | All riders |
|---|---|---|---|---|
| Riders, n | 30,040 | 3,926 | 12,954 | 46,920 |
| Rider |  |  |  |  |
|  Male | 22,753 (76.4) | 2,521 (64.6) | 9,582 (75.5) | 34,856 (75.2) |
| Trip purpose |  |  |  |  |
|  Commuting to work | 5,000 (21.1) | 944 (28.8) | 2,776 (31.5) | 8,720 (24.4) |
|  Traveling to school | 902 (3.8) | 77 (2.4) | 616 (7.0) | 1,595 (4.5) |
|  Professional use | 729 (3.1) | 284 (8.7) | 152 (1.7) | 1,165 (3.3) |
|  Leisure | 13,392 (56.6) | 1,428 (43.6) | 3,718 (42.1) | 18,538 (51.9) |
|  Shopping or other | 3,631 (15.4) | 542 (16.5) | 1,561 (17.7) | 5,734 (16.0) |
| Time and place |  |  |  |  |
|  Urban area | 24,657 (82.1) | 3,463 (88.2) | 12,492 (96.4) | 40,612 (86.6) |
|  Paris police area (départements 75, 92, 93, 94) | 9,634 (32.1) | 1,616 (41.2) | 4,692 (36.2) | 15,942 (34.0) |
|  Saturday or Sunday | 6,708 (22.3) | 754 (19.2) | 2,542 (19.6) | 10,004 (21.3) |
| Lighting |  |  |  |  |
|  Daylight | 23,784 (79.2) | 3,003 (76.5) | 8,925 (68.9) | 35,712 (76.1) |
|  Twilight | 1,716 (5.7) | 206 (5.2) | 771 (6.0) | 2,693 (5.7) |
|  Night, street lighting on | 3,817 (12.7) | 629 (16.0) | 2,814 (21.7) | 7,260 (15.5) |
|  Night, no working street lighting | 721 (2.4) | 88 (2.2) | 443 (3.4) | 1,252 (2.7) |
| Weather and surface |  |  |  |  |
|  Adverse weather or non-dry surface | 4,086 (14.1) | 617 (16.3) | 2,030 (16.0) | 6,733 (14.8) |
| Speed limit |  |  |  |  |
|  30 km/h or less | 8,977 (30.8) | 1,604 (42.5) | 4,585 (36.5) | 15,166 (33.4) |
|  31–49 km/h | 43 (0.1) | 6 (0.2) | 18 (0.1) | 67 (0.1) |
|  50 km/h | 15,647 (53.7) | 1,799 (47.7) | 7,665 (61.0) | 25,111 (55.2) |
|  More than 50 km/h | 4,459 (15.3) | 361 (9.6) | 296 (2.4) | 5,116 (11.3) |
| Road |  |  |  |  |
|  Communal road | 18,668 (62.1) | 2,829 (72.1) | 9,478 (73.2) | 30,975 (66.0) |
|  Departmental road | 9,887 (32.9) | 925 (23.6) | 2,842 (21.9) | 13,654 (29.1) |
|  Other road category | 1,485 (4.9) | 172 (4.4) | 634 (4.9) | 2,291 (4.9) |
| Cycle facility at the site |  |  |  |  |
|  Cycle path or cycle lane | 8,182 (27.9) | 1,293 (34.4) | 3,681 (29.1) | 13,156 (28.8) |
|  Other reserved lane | 1,461 (5.0) | 214 (5.7) | 900 (7.1) | 2,575 (5.6) |
|  None | 19,637 (67.1) | 2,249 (59.9) | 8,062 (63.8) | 29,948 (65.6) |
| Intersection |  |  |  |  |
|  At an intersection | 15,981 (53.2) | 2,248 (57.3) | 7,258 (56.0) | 25,487 (54.3) |
| Position of the crash |  |  |  |  |
|  Roadway | 22,882 (76.2) | 2,783 (70.9) | 9,577 (73.9) | 35,242 (75.1) |
|  Cycle path | 4,836 (16.1) | 826 (21.0) | 1,896 (14.6) | 7,558 (16.1) |
|  Other position | 2,312 (7.7) | 316 (8.1) | 1,479 (11.4) | 4,107 (8.8) |
| Crash configuration |  |  |  |  |
|  Pedestrian struck | 1,589 (5.3) | 310 (7.9) | 1,117 (8.6) | 3,016 (6.4) |
|  Carrying at least one passenger | 273 (0.9) | 90 (2.3) | 769 (5.9) | 1,132 (2.4) |

*Values are n (%) unless stated otherwise. Percentages are calculated among riders for whom the characteristic is recorded; the share of unknown values is given in Table 3.*

*Injury severity, age, hour of the crash and type of opponent are shown in Figure 2 and are not repeated here.*


## Table 4. Pre-specified factors, populations and adjustment sets

| ID | Contrast (first-named vs. reference) | Population | Tier | Adjustment set | Covariates | First-named group, n | of whom severe | Reference group, n | of whom severe |
|---|---|---|---|---|---|---|---|---|---|
| A1 | E-scooter vs. bicycle | Riders of the two modes | 1 | Tier 0; age, sex, trip purpose, passengers; Tier 2 | 22 | 12,954 | 2,405 | 30,040 | 8,288 |
| A2 | E-bike vs. bicycle | Riders of the two modes | 1 | Tier 0; age, sex, trip purpose, passengers; Tier 2 | 22 | 3,926 | 1,054 | 30,040 | 8,288 |
| D1 | Age 65 or over vs. 25–64 | Riders aged 25 or over | 1 | Tier 0; sex, mode | 8 | 5,372 | 2,932 | 27,665 | 6,231 |
| D2 | Male vs. female | Riders of known sex | 1 | Tier 0; age, mode | 8 | 34,856 | 9,547 | 11,502 | 2,200 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Urban crashes with those limits | 2 | Tiers 0–1; other Tier 2 | 21 | 14,917 | 1,756 | 24,132 | 5,623 |
| B4 | Reserved cycle facility vs. none | Sites with the facility recorded | 2 | Tiers 0–1; other Tier 2 | 22 | 13,156 | 1,967 | 29,948 | 9,190 |
| B5 | Intersection vs. no intersection | All riders | 2 | Tiers 0–1; other Tier 2 | 22 | 25,487 | 5,385 | 21,432 | 6,362 |
| B2 | Night without vs. with working street lighting | Crashes at night | 2 | Tiers 0–1; other Tier 2 | 22 | 1,252 | 548 | 7,260 | 1,284 |
| B3 | Adverse weather or non-dry surface vs. normal and dry | All riders | 2 | Tiers 0–1; other Tier 2 except weather and surface | 21 | 6,733 | 1,408 | 38,685 | 9,654 |
| B6 | Urban vs. outside urban area | All riders | 0 | Other Tier 0; age, sex, mode | 8 | 40,612 | 7,849 | 6,308 | 3,898 |
| C1 | Heavy-vehicle vs. car opponent | Two-party collisions with a car or heavy vehicle | 3 | Tiers 0–2 | 23 | 1,588 | 710 | 25,847 | 6,430 |
| C2 | Single-vehicle crash vs. collision with a motor vehicle | Those two crash types | 3 | Tiers 0–2 | 23 | 5,604 | 2,290 | 34,528 | 8,837 |
| C3 | Cycle path vs. roadway | Those two positions | 3 | Tiers 0–2 | 23 | 7,558 | 934 | 35,242 | 9,718 |

*Factors, populations and adjustment sets were fixed in the pre-analysis plan before any outcome model was fitted. Tiers are defined in Table 3. Severe denotes killed or hospitalized.*

*Contrasts A1, A2, D1 and D2 compare kinds of riders and are interpreted as adjusted differences, not as effects of an intervention.*


## Table 6. Inference diagnostics for the double machine learning estimates, all riders

| ID | Contrast | SE, clustered (pp) | SE, unclustered (pp) | Ratio | p | q | Propensity AUC | Outside trimming bounds (%) | RVa (%) | Bounds under 3% confounding (pp) |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | E-scooter vs. bicycle | 0.63 | 0.60 | 1.04 | <0.001 | 0.002 | 0.805 | 0.0 | 0.7 | −2.3 to 6.5 |
| A2 | E-bike vs. bicycle | 1.04 | 0.92 | 1.13 | <0.001 | <0.001 | 0.698 | 0.0 | 2.4 | 0.6 to 9.6 |
| D1 | Age 65 or over vs. 25–64 | 3.30 | 0.94 | 3.52 | <0.001 | <0.001 | 0.808 | 0.0 | 6.2 | 7.5 to 18.3 |
| D2 | Male vs. female | 0.50 | 0.49 | 1.02 | <0.001 | <0.001 | 0.647 | 0.0 | 1.3 | −0.8 to 4.9 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | 0.73 | 0.55 | 1.32 | 0.005 | 0.011 | 0.834 | 0.0 | 1.1 | −5.2 to 1.2 |
| B4 | Reserved cycle facility vs. none | 0.79 | 0.59 | 1.33 | 0.005 | 0.011 | 0.824 | 0.1 | 0.9 | −6.2 to 1.8 |
| B5 | Intersection vs. no intersection | 0.42 | 0.42 | 0.98 | 0.650 | 0.776 | 0.756 | 0.3 | 0.0 | −3.3 to 2.9 |
| B2 | Night without vs. with working street lighting | 3.69 | 2.63 | 1.40 | 0.700 | 0.792 | 0.806 | 0.3 | 0.0 | −2.0 to 4.9 |
| B3 | Adverse weather or non-dry surface vs. normal and dry | 0.99 | 0.73 | 1.36 | 0.895 | 0.921 | 0.745 | 0.0 | 0.0 | −4.2 to 3.9 |
| B6 | Urban vs. outside urban area | 4.60 | 0.87 | 5.28 | <0.001 | <0.001 | 0.864 | 32.6 | 10.7 | −35.4 to −21.0 |
| C1 | Heavy-vehicle vs. car opponent | 2.17 | 1.69 | 1.28 | <0.001 | <0.001 | 0.703 | 0.0 | 7.3 | 11.7 to 23.4 |
| C2 | Single-vehicle crash vs. collision with a motor vehicle | 2.08 | 0.89 | 2.33 | <0.001 | <0.001 | 0.840 | 0.0 | 5.3 | 6.3 to 18.7 |
| C3 | Cycle path vs. roadway | 1.19 | 0.86 | 1.39 | <0.001 | <0.001 | 0.928 | 2.8 | 1.2 | −12.2 to 3.1 |
| R10 | Placebo: even vs. odd day of the month | 0.37 | 0.35 | 1.07 | 0.413 | – | 0.511 | 0.0 | 0.0 | −2.6 to 2.0 |

*Point estimates and 95% confidence intervals are given in Figure 7a. SE, standard error in percentage points (pp), clustered by département or unclustered; q, Benjamini–Hochberg false discovery rate across the 43 estimates of the main analysis.*

*Propensity AUC is the cross-fitted discrimination of the model for group membership. Outside trimming bounds is the share of riders with an estimated propensity score below 0.02 or above 0.98.*

*RVa is the robustness value for statistical significance: the share of residual variation in both the factor and the outcome that an unobserved confounder would need to explain for the 95% confidence interval to include zero. Bounds are the range of the estimate if such a confounder explained 3% of each. Robustness values for the point estimate are given in Figure 10d.*

*B6 does not satisfy the overlap condition (33% of propensity scores outside the trimming bounds); its estimate, −28.2 (−37.2 to −19.2), is not interpreted. The placebo estimate is −0.3 (−1.0 to 0.4).*


## Table 7. Agreement between the SHAP contrast and the double machine learning estimate

| Set of estimates | Estimates | With q < 0.05 | Same sign, all | Same sign, q < 0.05 | SHAP within 95% CI | What-if within 95% CI | SHAP smaller in magnitude, q < 0.05 | Median ratio, q < 0.05 | Standardized difference beyond ±1.96 |
|---|---|---|---|---|---|---|---|---|---|
| All riders | 12 | 9 | 11/12 (92) | 9/9 (100) | 11/12 (92) | 9/12 (75) | 9/9 (100) | 0.72 | 1/12 (8) |
| Bicycle | 10 | 6 | 9/10 (90) | 6/6 (100) | 8/10 (80) | 9/10 (90) | 6/6 (100) | 0.75 | 2/10 (20) |
| E-bike | 8 | 0 | 6/8 (75) | – | 8/8 (100) | 8/8 (100) | – | – | 0/8 (0) |
| E-scooter | 9 | 2 | 5/9 (56) | 2/2 (100) | 7/9 (78) | 7/9 (78) | 2/2 (100) | 0.52 | 2/9 (22) |
| All estimates | 39 | 17 | 31/39 (79) | 17/17 (100) | 34/39 (87) | 33/39 (85) | 17/17 (100) | 0.71 | 5/39 (13) |

*Cells give the number of estimates meeting the criterion over the number considered, with the percentage in parentheses. The ratio is the absolute SHAP contrast divided by the absolute double ML estimate.*

*The urban versus non-urban contrast is excluded because the overlap condition was not satisfied. Rank concordance between the readings is shown in Figure 7e.*


## Table S1. Hyperparameter search space and selected values of the gradient-boosting model

| Hyperparameter | Search distribution | Selected value |
|---|---|---|
| Number of leaves | Integer, 8–63 | 30 |
| Learning rate | Log-uniform, 0.02–0.12 | 0.0244 |
| Number of trees | Integer, 150–899 | 474 |
| Minimum riders per leaf | Integer, 20–199 | 163 |
| Row subsampling | Uniform, 0.6–1.0 | 0.719 |
| Column subsampling | Uniform, 0.5–1.0 | 0.529 |
| L2 regularization | Log-uniform, 0.1–30 | 1.21 |
| Categorical smoothing | Log-uniform, 5–100 | 59.5 |

*Random search with 30 configurations, selected on mean log loss over five folds grouped by crash within the development set (2020–2023). The inverse regularization strength of the logistic regression was 0.3.*


## Table S2. Predictive performance on the locked test set (2024–2025) by model and transport mode

| Model | Riders | n | Severe (%) | ROC AUC (95% CI) | PR AUC (95% CI) | Brier score (95% CI) | Log loss | Calibration slope | Calibration intercept |
|---|---|---|---|---|---|---|---|---|---|
| Gradient boosting | All riders | 17,712 | 25.2 | 0.818 (0.811–0.825) | 0.622 (0.606–0.637) | 0.138 (0.135–0.142) | 0.432 | 0.92 | −0.14 |
| Gradient boosting | Bicycle | 9,764 | 27.9 | 0.832 (0.823–0.841) | 0.661 (0.644–0.678) | 0.142 (0.138–0.147) | 0.442 | 0.90 | −0.18 |
| Gradient boosting | E-bike | 1,696 | 26.1 | 0.847 (0.824–0.869) | 0.701 (0.656–0.745) | 0.127 (0.116–0.138) | 0.404 | 1.02 | 0.01 |
| Gradient boosting | E-scooter | 6,252 | 20.6 | 0.774 (0.760–0.788) | 0.487 (0.460–0.516) | 0.135 (0.130–0.141) | 0.425 | 0.95 | −0.08 |
| Logistic regression | All riders | 17,712 | 25.2 | 0.810 (0.802–0.817) | 0.602 (0.584–0.616) | 0.142 (0.139–0.145) | 0.442 | 0.88 | −0.19 |
| Logistic regression | Bicycle | 9,764 | 27.9 | 0.824 (0.816–0.834) | 0.639 (0.620–0.658) | 0.146 (0.142–0.151) | 0.452 | 0.88 | −0.21 |
| Logistic regression | E-bike | 1,696 | 26.1 | 0.835 (0.812–0.859) | 0.684 (0.640–0.732) | 0.132 (0.121–0.142) | 0.418 | 0.92 | −0.09 |
| Logistic regression | E-scooter | 6,252 | 20.6 | 0.764 (0.750–0.778) | 0.466 (0.440–0.494) | 0.138 (0.133–0.144) | 0.433 | 0.88 | −0.17 |

*Confidence intervals are obtained by bootstrap resampling of crashes.*


## Table S3. Performance of the gradient-boosting model under nine validation protocols

| Validation protocol | n evaluated | Severe (%) | ROC AUC | PR AUC | Brier score | Log loss | Calibration slope | Calibration intercept |
|---|---|---|---|---|---|---|---|---|
| Random split of riders, global preprocessing | 46,920 | 25.0 | 0.840 | 0.651 | 0.131 | 0.410 | 1.00 | 0.01 |
| As above, plus outcome-dependent variables | 46,920 | 25.0 | 0.843 | 0.658 | 0.129 | 0.406 | 1.01 | 0.01 |
| Oversampling to 50:50 before the random split | 70,346 | 50.0 | 0.865 | 0.852 | 0.150 | 0.461 | 1.14 | −0.00 |
| Grouped by crash, 2020–2025, in-fold preprocessing | 46,920 | 25.0 | 0.839 | 0.648 | 0.131 | 0.411 | 1.00 | −0.00 |
| Grouped by crash, 2020–2023 | 29,208 | 25.0 | 0.846 | 0.655 | 0.129 | 0.403 | 0.98 | −0.01 |
| Forward in time: locked test set, 2024–2025 | 17,712 | 25.2 | 0.818 | 0.622 | 0.138 | 0.432 | 0.92 | −0.14 |
| Forward chaining: validation on 2021 | 7,450 | 24.8 | 0.828 | 0.614 | 0.136 | 0.422 | 0.95 | −0.08 |
| Forward chaining: validation on 2022 | 7,852 | 25.2 | 0.847 | 0.654 | 0.129 | 0.404 | 0.99 | 0.03 |
| Forward chaining: validation on 2023 | 7,993 | 24.7 | 0.831 | 0.641 | 0.133 | 0.416 | 0.90 | −0.07 |

*Hyperparameters are identical across protocols. Oversampling changes the share of severe outcomes, so that only the ROC AUC is comparable for that protocol.*


## Table S4. Share of riders with each variable recorded as unknown, by injury severity and transport mode

| Variable | Bicycle: severe (%) | Bicycle: not severe (%) | Bicycle: difference | E-bike: severe (%) | E-bike: not severe (%) | E-bike: difference | E-scooter: severe (%) | E-scooter: not severe (%) | E-scooter: difference |
|---|---|---|---|---|---|---|---|---|---|
| Safety equipment (excluded) | 20.6 | 47.4 | −26.9 | 24.1 | 50.5 | −26.4 | 50.5 | 65.8 | −15.3 |
| Trip purpose | 14.9 | 23.7 | −8.7 | 14.4 | 17.4 | −3.0 | 31.0 | 32.1 | −1.1 |
| Infrastructure | 1.4 | 7.3 | −5.9 | 2.8 | 7.7 | −4.8 | 1.8 | 5.1 | −3.3 |
| Number of lanes | 3.5 | 7.8 | −4.4 | 5.8 | 10.5 | −4.7 | 4.9 | 8.2 | −3.3 |
| Maneuver | 9.5 | 7.9 | +1.6 | 9.0 | 5.3 | +3.8 | 12.4 | 9.0 | +3.5 |
| Age | 0.0 | 1.5 | −1.5 | 0.0 | 1.1 | −1.1 | 0.0 | 2.7 | −2.7 |
| Speed limit | 4.5 | 2.5 | +1.9 | 5.8 | 3.3 | +2.5 | 3.4 | 2.9 | +0.4 |
| Sex | 0.0 | 1.3 | −1.3 | 0.0 | 0.9 | −0.9 | 0.0 | 2.5 | −2.5 |
| Cycle facility | 1.5 | 2.9 | −1.4 | 2.6 | 5.0 | −2.4 | 1.9 | 2.5 | −0.7 |
| Traffic regime | 5.2 | 6.5 | −1.3 | 5.7 | 5.9 | −0.2 | 6.1 | 8.3 | −2.2 |
| Collision type | 0.9 | 1.2 | −0.3 | 0.4 | 0.3 | +0.1 | 0.2 | 0.3 | −0.1 |
| Alignment | 0.0 | 0.0 | +0.0 | 0.1 | 0.0 | +0.1 | 0.0 | 0.0 | −0.0 |
| Gradient | 0.0 | 0.0 | +0.0 | 0.1 | 0.0 | +0.1 | 0.0 | 0.1 | −0.1 |
| Position on road | 0.0 | 0.0 | −0.0 | 0.1 | 0.0 | +0.1 | 0.0 | 0.0 | −0.0 |
| Point of impact | 0.1 | 0.0 | +0.1 | 0.1 | 0.0 | +0.1 | 0.1 | 0.1 | +0.0 |
| Mobile obstacle | 0.1 | 0.1 | +0.0 | 0.0 | 0.0 | +0.0 | 0.1 | 0.1 | +0.1 |
| Surface condition | 0.1 | 0.0 | +0.0 | 0.1 | 0.0 | +0.1 | 0.0 | 0.0 | −0.0 |
| Pedestrian struck | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Urban area | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Opponent type | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Passengers | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Fixed obstacle | 0.1 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Vehicles involved | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Month | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Transport mode | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Lighting | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | −0.0 |
| Intersection type | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | −0.0 |
| Hour of day | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Day of week | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Département | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Road category | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |
| Weather | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | −0.0 |
| Year | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 | 0.0 | 0.0 | +0.0 |

*Severe denotes killed or hospitalized. Differences are in percentage points (severe minus not severe). Variables are ordered by the largest absolute difference across modes.*


## Table S5. Mean absolute SHAP value of all variables on the locked test set and stability of the importance rank

| Rank | Variable | Tier | All riders | Bicycle | E-bike | E-scooter | Median rank, 25 refits | Range of rank |
|---|---|---|---|---|---|---|---|---|
| 1 | Département | 0 | 0.775 | 0.820 | 0.809 | 0.697 | 1 | 1–1 |
| 2 | Age | 1 | 0.308 | 0.334 | 0.326 | 0.261 | 2 | 2–2 |
| 3 | Opponent type | 3 | 0.232 | 0.227 | 0.258 | 0.232 | 3 | 3–3 |
| 4 | Road category | 2 | 0.149 | 0.158 | 0.137 | 0.138 | 5 | 4–6 |
| 5 | Speed limit | 2 | 0.141 | 0.159 | 0.137 | 0.113 | 5 | 4–6 |
| 6 | Urban area | 0 | 0.127 | 0.149 | 0.117 | 0.095 | 5 | 4–6 |
| 7 | Trip purpose | 1 | 0.123 | 0.126 | 0.121 | 0.120 | 7 | 7–7 |
| 8 | Collision type | 3 | 0.085 | 0.092 | 0.080 | 0.076 | 8 | 8–9 |
| 9 | Hour of day | 0 | 0.080 | 0.076 | 0.080 | 0.088 | 13 | 11–14 |
| 10 | Transport mode | 1 | 0.077 | 0.054 | 0.219 | 0.074 | 10 | 8–14 |
| 11 | Pedestrian struck | 3 | 0.072 | 0.064 | 0.082 | 0.083 | 10 | 8–13 |
| 12 | Maneuver | 3 | 0.072 | 0.074 | 0.064 | 0.071 | 12 | 9–15 |
| 13 | Gradient | 2 | 0.069 | 0.072 | 0.072 | 0.063 | 11 | 9–13 |
| 14 | Traffic regime | 2 | 0.061 | 0.064 | 0.045 | 0.061 | 14 | 11–17 |
| 15 | Year | 0 | 0.056 | 0.050 | 0.070 | 0.062 | 19 | 16–23 |
| 16 | Number of lanes | 2 | 0.051 | 0.055 | 0.057 | 0.043 | 19 | 16–21 |
| 17 | Day of week | 0 | 0.049 | 0.050 | 0.035 | 0.050 | 27 | 22–29 |
| 18 | Point of impact | 3 | 0.043 | 0.045 | 0.043 | 0.040 | 18 | 14–21 |
| 19 | Lighting | 2 | 0.041 | 0.037 | 0.045 | 0.046 | 17 | 13–22 |
| 20 | Month | 0 | 0.039 | 0.039 | 0.037 | 0.038 | 22 | 19–29 |
| 21 | Mobile obstacle | 3 | 0.037 | 0.033 | 0.040 | 0.043 | 23 | 16–27 |
| 22 | Fixed obstacle | 3 | 0.037 | 0.035 | 0.040 | 0.039 | 24 | 21–27 |
| 23 | Intersection type | 2 | 0.037 | 0.036 | 0.035 | 0.039 | 15 | 12–19 |
| 24 | Position on road | 3 | 0.033 | 0.033 | 0.036 | 0.034 | 22 | 16–29 |
| 25 | Sex | 1 | 0.028 | 0.026 | 0.034 | 0.029 | 18 | 15–23 |
| 26 | Vehicles involved | 3 | 0.026 | 0.032 | 0.025 | 0.019 | 27 | 23–29 |
| 27 | Cycle facility | 2 | 0.024 | 0.026 | 0.025 | 0.020 | 25 | 21–29 |
| 28 | Weather | 2 | 0.020 | 0.021 | 0.021 | 0.017 | 29 | 25–30 |
| 29 | Infrastructure | 2 | 0.018 | 0.019 | 0.016 | 0.018 | 26 | 21–29 |
| 30 | Passengers | 1 | 0.018 | 0.011 | 0.018 | 0.028 | 30 | 29–31 |
| 31 | Alignment | 2 | 0.004 | 0.004 | 0.004 | 0.004 | 31 | 29–31 |
| 32 | Surface condition | 2 | 0.002 | 0.002 | 0.002 | 0.002 | 32 | 32–32 |

*SHAP values are in log-odds of a severe outcome. Refits are five seeds by five folds grouped by crash within the development set.*


## Table S6. Unadjusted difference, SHAP contrast, model what-if and double machine learning estimate for all 43 estimates

| Riders | ID | Contrast | n | Unadjusted (pp) | SHAP contrast (pp) | Model what-if (pp) | Double ML (pp) | 95% CI | p | q |
|---|---|---|---|---|---|---|---|---|---|---|
| All riders | A1 | E-scooter vs. bicycle | 42,994 | −9.0 | +1.6 | +1.1 | +2.1 | 0.8 to 3.3 | <0.001 | 0.002 |
| All riders | A2 | E-bike vs. bicycle | 33,966 | −0.7 | +3.1 | +2.7 | +5.1 | 3.0 to 7.1 | <0.001 | <0.001 |
| All riders | D1 | Age 65 or over vs. 25–64 | 33,037 | +32.1 | +11.5 | +10.4 | +12.9 | 6.4 to 19.4 | <0.001 | <0.001 |
| All riders | D2 | Male vs. female | 46,358 | +8.3 | +1.3 | +1.4 | +2.0 | 1.0 to 3.0 | <0.001 | <0.001 |
| All riders | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 39,049 | −11.5 | −1.7 | −2.1 | −2.0 | −3.5 to −0.6 | 0.005 | 0.011 |
| All riders | B4 | Reserved cycle facility vs. none | 43,104 | −15.7 | −0.8 | −1.2 | −2.2 | −3.8 to −0.7 | 0.005 | 0.011 |
| All riders | B5 | Intersection vs. no intersection | 46,919 | −8.6 | +0.4 | +1.2 | −0.2 | −1.0 to 0.6 | 0.650 | 0.776 |
| All riders | B2 | Night without vs. with working street lighting | 8,512 | +26.1 | +1.3 | +1.5 | +1.4 | −5.8 to 8.6 | 0.700 | 0.792 |
| All riders | B3 | Adverse weather or non-dry surface vs. normal and dry | 45,418 | −4.0 | −0.1 | −0.6 | −0.1 | −2.1 to 1.8 | 0.895 | 0.921 |
| All riders | B6 | Urban vs. outside urban area | 46,920 | −42.5 | −7.3 | −6.2 | −28.2 | −37.2 to −19.2 | <0.001 | <0.001 |
| All riders | C1 | Heavy-vehicle vs. car opponent | 27,435 | +19.8 | +17.1 | +17.0 | +17.6 | 13.3 to 21.8 | <0.001 | <0.001 |
| All riders | C2 | Single-vehicle crash vs. collision with a motor vehicle | 40,132 | +15.3 | +9.0 | +11.2 | +12.5 | 8.4 to 16.6 | <0.001 | <0.001 |
| All riders | C3 | Cycle path vs. roadway | 42,800 | −15.2 | −1.2 | −1.2 | −4.5 | −6.9 to −2.2 | <0.001 | <0.001 |
| Bicycle | D1 | Age 65 or over vs. 25–64 | 22,807 | +31.4 | +11.2 | +10.9 | +14.0 | 8.2 to 19.8 | <0.001 | <0.001 |
| Bicycle | D2 | Male vs. female | 29,765 | +10.4 | +1.3 | +1.2 | +1.4 | −0.0 to 2.7 | 0.053 | 0.104 |
| Bicycle | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 23,685 | −13.4 | −1.8 | −2.4 | −2.6 | −4.6 to −0.5 | 0.014 | 0.029 |
| Bicycle | B4 | Reserved cycle facility vs. none | 27,819 | −19.8 | −1.0 | −1.5 | −3.2 | −5.3 to −1.2 | 0.002 | 0.004 |
| Bicycle | B5 | Intersection vs. no intersection | 30,040 | −9.9 | +0.4 | +1.0 | −0.0 | −1.1 to 1.1 | 0.999 | 0.999 |
| Bicycle | B2 | Night without vs. with working street lighting | 4,538 | +31.4 | +1.3 | +1.6 | +2.6 | −8.4 to 13.5 | 0.645 | 0.776 |
| Bicycle | B3 | Adverse weather or non-dry surface vs. normal and dry | 28,923 | −6.0 | −0.2 | −0.7 | −0.4 | −3.0 to 2.2 | 0.742 | 0.818 |
| Bicycle | B6 | Urban vs. outside urban area | 30,040 | −41.9 | −7.4 | −6.2 | −27.7 | −37.0 to −18.4 | <0.001 | <0.001 |
| Bicycle | C1 | Heavy-vehicle vs. car opponent | 17,637 | +19.9 | +17.0 | +16.7 | +18.7 | 14.1 to 23.3 | <0.001 | <0.001 |
| Bicycle | C2 | Single-vehicle crash vs. collision with a motor vehicle | 25,837 | +16.4 | +8.9 | +11.0 | +9.9 | 6.4 to 13.5 | <0.001 | <0.001 |
| Bicycle | C3 | Cycle path vs. roadway | 27,718 | −18.5 | −1.2 | −1.2 | −5.3 | −8.3 to −2.2 | <0.001 | 0.002 |
| E-bike | D1 | Age 65 or over vs. 25–64 | 3,235 | +32.5 | +10.7 | +9.8 | +9.7 | −3.5 to 22.8 | 0.149 | 0.229 |
| E-bike | D2 | Male vs. female | 3,901 | +3.5 | +1.3 | +1.4 | +2.0 | −0.8 to 4.7 | 0.164 | 0.236 |
| E-bike | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 3,314 | −14.7 | −1.7 | −2.0 | −4.2 | −9.1 to 0.6 | 0.085 | 0.146 |
| E-bike | B4 | Reserved cycle facility vs. none | 3,542 | −17.8 | −0.8 | −1.0 | +0.3 | −4.9 to 5.5 | 0.897 | 0.921 |
| E-bike | B5 | Intersection vs. no intersection | 3,926 | −10.3 | +0.5 | +1.4 | +1.3 | −2.1 to 4.6 | 0.450 | 0.586 |
| E-bike | B3 | Adverse weather or non-dry surface vs. normal and dry | 3,792 | −5.8 | −0.2 | −0.7 | +5.0 | −4.1 to 14.2 | 0.282 | 0.391 |
| E-bike | B6 | Urban vs. outside urban area | 3,926 | −49.1 | −7.1 | −6.4 | −37.4 | −49.2 to −25.7 | <0.001 | <0.001 |
| E-bike | C2 | Single-vehicle crash vs. collision with a motor vehicle | 3,268 | +12.7 | +8.6 | +10.9 | +6.4 | −1.8 to 14.6 | 0.126 | 0.200 |
| E-bike | C3 | Cycle path vs. roadway | 3,609 | −15.1 | −1.0 | −0.9 | −5.7 | −12.8 to 1.5 | 0.119 | 0.197 |
| E-scooter | D2 | Male vs. female | 12,692 | +5.5 | +1.4 | +1.7 | +3.5 | 1.9 to 5.1 | <0.001 | <0.001 |
| E-scooter | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 12,050 | −7.2 | −1.5 | −1.6 | −0.6 | −2.3 to 1.1 | 0.493 | 0.623 |
| E-scooter | B4 | Reserved cycle facility vs. none | 11,743 | −5.3 | −0.5 | −0.5 | +0.2 | −2.3 to 2.6 | 0.900 | 0.921 |
| E-scooter | B5 | Intersection vs. no intersection | 12,953 | −4.3 | +0.5 | +1.6 | −1.1 | −2.6 to 0.4 | 0.161 | 0.236 |
| E-scooter | B2 | Night without vs. with working street lighting | 3,257 | +18.4 | +1.3 | +1.4 | −2.3 | −12.9 to 8.3 | 0.668 | 0.776 |
| E-scooter | B3 | Adverse weather or non-dry surface vs. normal and dry | 12,703 | +1.3 | −0.1 | −0.3 | +1.3 | −1.6 to 4.2 | 0.367 | 0.493 |
| E-scooter | B6 | Urban vs. outside urban area | 12,954 | −33.7 | −7.5 | −6.3 | −28.6 | −36.1 to −21.1 | <0.001 | <0.001 |
| E-scooter | C1 | Heavy-vehicle vs. car opponent | 7,689 | +13.0 | +17.3 | +17.2 | +11.6 | −0.8 to 23.9 | 0.066 | 0.118 |
| E-scooter | C2 | Single-vehicle crash vs. collision with a motor vehicle | 11,027 | +15.7 | +9.1 | +11.6 | +14.3 | 9.1 to 19.5 | <0.001 | <0.001 |
| E-scooter | C3 | Cycle path vs. roadway | 11,473 | −7.5 | −1.1 | −1.3 | −3.6 | −7.4 to 0.2 | 0.066 | 0.118 |

*pp, percentage points of the probability of being killed or hospitalized. Estimates are omitted where either group contained fewer than 200 riders or 30 severe outcomes. B6 does not satisfy the overlap condition and is not interpreted.*


## Table S7. Double machine learning estimates under the pre-specified adjustment set and under all controls, all riders

| ID | Contrast | Covariates, pre-specified | Estimate (pp) | 95% CI | Covariates, all controls | Estimate (pp) | 95% CI | Change (pp) |
|---|---|---|---|---|---|---|---|---|
| A1 | E-scooter vs. bicycle | 22 | +2.1 | 0.8 to 3.3 | 31 | +0.7 | −0.4 to 1.9 | −1.3 |
| A2 | E-bike vs. bicycle | 22 | +5.1 | 3.0 to 7.1 | 31 | +4.6 | 2.6 to 6.5 | −0.5 |
| D1 | Age 65 or over vs. 25–64 | 8 | +12.9 | 6.4 to 19.4 | 31 | +8.3 | 3.7 to 13.0 | −4.6 |
| D2 | Male vs. female | 8 | +2.0 | 1.0 to 3.0 | 31 | +1.3 | 0.4 to 2.2 | −0.7 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | 21 | −2.0 | −3.5 to −0.6 | 30 | −1.8 | −3.1 to −0.5 | +0.2 |
| B4 | Reserved cycle facility vs. none | 22 | −2.2 | −3.8 to −0.7 | 31 | −1.3 | −3.1 to 0.5 | +0.9 |
| B5 | Intersection vs. no intersection | 22 | −0.2 | −1.0 to 0.6 | 31 | +1.0 | −0.0 to 2.0 | +1.2 |
| B2 | Night without vs. with working street lighting | 22 | +1.4 | −5.8 to 8.6 | 31 | +0.6 | −5.5 to 6.7 | −0.8 |
| B3 | Adverse weather or non-dry surface vs. normal and dry | 21 | −0.1 | −2.1 to 1.8 | 30 | −0.9 | −2.7 to 1.0 | −0.7 |
| B6 | Urban vs. outside urban area | 8 | −28.2 | −37.2 to −19.2 | 31 | −11.3 | −16.1 to −6.6 | +16.8 |
| C1 | Heavy-vehicle vs. car opponent | 23 | +17.6 | 13.3 to 21.8 | 30 | +17.3 | 13.3 to 21.4 | −0.2 |
| C2 | Single-vehicle crash vs. collision with a motor vehicle | 23 | +12.5 | 8.4 to 16.6 | 28 | +9.1 | 6.2 to 12.1 | −3.4 |
| C3 | Cycle path vs. roadway | 23 | −4.5 | −6.9 to −2.2 | 31 | −3.6 | −5.8 to −1.3 | +1.0 |

*All controls denotes adjustment for every explanatory variable other than those defining the factor, including variables in later tiers.*


## Table S8. Group average effects for three factors

| ID | Contrast | Grouping variable | Group | n | Effect (pp) | SE (pp) | Joint 95% CI | p, equality across groups |
|---|---|---|---|---|---|---|---|---|
| A1 | E-scooter vs. bicycle | Age | under 25 | 12,587 | +2.7 | 0.90 | 0.6 to 4.9 | 0.161 |
| A1 | E-scooter vs. bicycle | Age | 65+ | 4,754 | −3.1 | 3.15 | −10.6 to 4.4 | 0.161 |
| A1 | E-scooter vs. bicycle | Age | 25–64 | 25,048 | +2.8 | 0.83 | 0.9 to 4.8 | 0.161 |
| A1 | E-scooter vs. bicycle | Sex | male | 32,335 | +3.1 | 0.69 | 1.5 to 4.6 | 0.003 |
| A1 | E-scooter vs. bicycle | Sex | female | 10,122 | −0.9 | 1.21 | −3.6 to 1.8 | 0.003 |
| A1 | E-scooter vs. bicycle | Setting | urban | 37,149 | +1.3 | 0.57 | −0.0 to 2.6 | 0.023 |
| A1 | E-scooter vs. bicycle | Setting | non-urban | 5,845 | +7.4 | 2.57 | 1.6 to 13.1 | 0.023 |
| A1 | E-scooter vs. bicycle | Opponent | motor-vehicle opponent | 31,858 | +0.9 | 0.66 | −0.6 to 2.4 | 0.004 |
| A1 | E-scooter vs. bicycle | Opponent | no motor-vehicle opponent | 11,136 | +5.6 | 1.60 | 2.0 to 9.2 | 0.004 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Mode | bicycle | 23,685 | −2.5 | 1.03 | −5.0 to −0.1 | 0.509 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Mode | escooter | 12,050 | −1.2 | 0.83 | −3.2 to 0.8 | 0.509 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Mode | ebike | 3,314 | −1.4 | 1.77 | −5.6 to 2.9 | 0.509 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Age | under 25 | 11,797 | −1.9 | 0.88 | −4.0 to 0.3 | 0.198 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Age | 65+ | 3,302 | −6.0 | 2.36 | −11.7 to −0.3 | 0.198 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Age | 25–64 | 23,347 | −1.6 | 0.84 | −3.6 to 0.4 | 0.198 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Sex | male | 28,234 | −2.8 | 0.67 | −4.3 to −1.3 | 0.007 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Sex | female | 10,283 | −0.0 | 1.15 | −2.6 to 2.6 | 0.007 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Opponent | motor-vehicle opponent | 28,947 | −2.2 | 0.79 | −3.9 to −0.4 | 0.621 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | Opponent | no motor-vehicle opponent | 10,102 | −1.6 | 0.95 | −3.8 to 0.5 | 0.621 |
| B2 | Night without vs. with working street lighting | Mode | bicycle | 4,538 | +4.5 | 4.60 | −6.5 to 15.5 | 0.419 |
| B2 | Night without vs. with working street lighting | Mode | escooter | 3,257 | −1.3 | 4.33 | −11.7 to 9.0 | 0.419 |
| B2 | Night without vs. with working street lighting | Mode | ebike | 717 | −3.9 | 8.23 | −23.6 to 15.8 | 0.419 |
| B2 | Night without vs. with working street lighting | Age | 25–64 | 5,392 | +2.4 | 4.18 | −6.9 to 11.8 | 0.921 |
| B2 | Night without vs. with working street lighting | Age | under 25 | 2,776 | +1.9 | 4.93 | −9.1 to 13.0 | 0.921 |
| B2 | Night without vs. with working street lighting | Sex | male | 6,616 | +1.2 | 3.57 | −6.9 to 9.2 | 0.704 |
| B2 | Night without vs. with working street lighting | Sex | female | 1,767 | +3.8 | 7.17 | −12.3 to 19.9 | 0.704 |
| B2 | Night without vs. with working street lighting | Setting | urban | 7,918 | −0.1 | 3.30 | −7.5 to 7.3 | 0.019 |
| B2 | Night without vs. with working street lighting | Setting | non-urban | 594 | +23.9 | 9.91 | 1.7 to 46.1 | 0.019 |
| B2 | Night without vs. with working street lighting | Opponent | motor-vehicle opponent | 6,168 | +1.4 | 3.81 | −7.2 to 9.9 | 0.872 |
| B2 | Night without vs. with working street lighting | Opponent | no motor-vehicle opponent | 2,344 | +2.0 | 4.26 | −7.5 to 11.6 | 0.872 |

*Group average effects are obtained by regressing the doubly robust score on group indicators, with standard errors clustered by département and Bonferroni adjustment within each grouping variable.*


## Table S9. Double machine learning estimates under each robustness check

| Robustness check | ID | Contrast | n | Estimate (pp) | 95% CI | p |
|---|---|---|---|---|---|---|
| Including 2019 | A1 | E-scooter vs. bicycle | 48,336 | +2.7 | 1.4 to 3.9 | <0.001 |
| Including 2019 | A2 | E-bike vs. bicycle | 38,941 | +5.1 | 3.1 to 7.1 | <0.001 |
| Including 2019 | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 43,646 | −1.8 | −3.1 to −0.5 | 0.008 |
| Including 2019 | B2 | Night without vs. with working street lighting | 9,456 | +2.3 | −4.8 to 9.4 | 0.519 |
| Including 2019 | B3 | Adverse weather or non-dry surface vs. normal and dry | 50,826 | +0.0 | −2.0 to 2.0 | 0.984 |
| Including 2019 | B4 | Reserved cycle facility vs. none | 48,325 | −2.0 | −3.5 to −0.6 | 0.006 |
| Including 2019 | B5 | Intersection vs. no intersection | 52,509 | +0.0 | −0.8 to 0.8 | 0.961 |
| Including 2019 | C1 | Heavy-vehicle vs. car opponent | 30,992 | +18.5 | 14.1 to 22.9 | <0.001 |
| Including 2019 | C2 | Single-vehicle crash vs. collision with a motor vehicle | 45,107 | +11.6 | 7.8 to 15.4 | <0.001 |
| Including 2019 | C3 | Cycle path vs. roadway | 48,037 | −4.4 | −6.6 to −2.1 | <0.001 |
| Including 2019 | D1 | Age 65 or over vs. 25–64 | 37,125 | +13.3 | 6.8 to 19.9 | <0.001 |
| Including 2019 | D2 | Male vs. female | 51,948 | +2.1 | 1.2 to 3.0 | <0.001 |
| Excluding the Paris police area | A1 | E-scooter vs. bicycle | 28,668 | +2.7 | 0.9 to 4.5 | 0.003 |
| Excluding the Paris police area | A2 | E-bike vs. bicycle | 22,716 | +6.7 | 4.1 to 9.3 | <0.001 |
| Excluding the Paris police area | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 23,700 | −3.0 | −4.6 to −1.5 | <0.001 |
| Excluding the Paris police area | B2 | Night without vs. with working street lighting | 4,889 | +4.8 | −2.5 to 12.0 | 0.196 |
| Excluding the Paris police area | B3 | Adverse weather or non-dry surface vs. normal and dry | 29,652 | −0.2 | −3.3 to 3.0 | 0.920 |
| Excluding the Paris police area | B4 | Reserved cycle facility vs. none | 29,200 | −3.1 | −5.1 to −1.2 | 0.001 |
| Excluding the Paris police area | B5 | Intersection vs. no intersection | 30,978 | −0.1 | −1.3 to 1.1 | 0.863 |
| Excluding the Paris police area | C1 | Heavy-vehicle vs. car opponent | 20,239 | +19.3 | 14.5 to 24.1 | <0.001 |
| Excluding the Paris police area | C2 | Single-vehicle crash vs. collision with a motor vehicle | 28,107 | +15.2 | 11.1 to 19.3 | <0.001 |
| Excluding the Paris police area | C3 | Cycle path vs. roadway | 28,218 | −6.3 | −9.0 to −3.7 | <0.001 |
| Excluding the Paris police area | D1 | Age 65 or over vs. 25–64 | 21,444 | +18.2 | 15.5 to 20.9 | <0.001 |
| Excluding the Paris police area | D2 | Male vs. female | 30,799 | +2.5 | 1.2 to 3.8 | <0.001 |
| Fatal outcome | A1 | E-scooter vs. bicycle | 42,994 | +0.8 | −0.1 to 1.7 | 0.086 |
| Fatal outcome | A2 | E-bike vs. bicycle | 33,966 | +1.0 | −0.0 to 2.0 | 0.052 |
| Fatal outcome | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 39,049 | −0.3 | −0.8 to 0.1 | 0.173 |
| Fatal outcome | B2 | Night without vs. with working street lighting | 8,512 | +0.9 | −0.9 to 2.8 | 0.316 |
| Fatal outcome | B3 | Adverse weather or non-dry surface vs. normal and dry | 45,418 | −0.1 | −0.8 to 0.7 | 0.867 |
| Fatal outcome | B4 | Reserved cycle facility vs. none | 43,104 | −0.4 | −1.2 to 0.3 | 0.239 |
| Fatal outcome | B5 | Intersection vs. no intersection | 46,919 | −1.6 | −2.4 to −0.7 | <0.001 |
| Fatal outcome | C1 | Heavy-vehicle vs. car opponent | 27,435 | +9.7 | 6.4 to 13.0 | <0.001 |
| Fatal outcome | C2 | Single-vehicle crash vs. collision with a motor vehicle | 40,132 | +4.5 | 2.4 to 6.5 | <0.001 |
| Fatal outcome | C3 | Cycle path vs. roadway | 42,800 | −1.6 | −2.6 to −0.7 | <0.001 |
| Fatal outcome | D1 | Age 65 or over vs. 25–64 | 33,037 | +5.9 | 3.1 to 8.8 | <0.001 |
| Fatal outcome | D2 | Male vs. female | 46,358 | +0.9 | 0.4 to 1.5 | <0.001 |
| Motor-vehicle collisions only | A1 | E-scooter vs. bicycle | 31,858 | +0.6 | −0.8 to 2.0 | 0.414 |
| Motor-vehicle collisions only | A2 | E-bike vs. bicycle | 25,279 | +4.5 | 2.1 to 6.9 | <0.001 |
| Motor-vehicle collisions only | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 28,947 | −1.8 | −3.3 to −0.3 | 0.022 |
| Motor-vehicle collisions only | B2 | Night without vs. with working street lighting | 6,168 | +1.1 | −7.8 to 9.9 | 0.814 |
| Motor-vehicle collisions only | B3 | Adverse weather or non-dry surface vs. normal and dry | 33,362 | −0.1 | −2.3 to 2.1 | 0.938 |
| Motor-vehicle collisions only | B4 | Reserved cycle facility vs. none | 32,111 | −0.9 | −2.5 to 0.7 | 0.270 |
| Motor-vehicle collisions only | B5 | Intersection vs. no intersection | 34,528 | +0.3 | −0.7 to 1.3 | 0.586 |
| Motor-vehicle collisions only | C1 | Heavy-vehicle vs. car opponent | 27,435 | +17.6 | 13.3 to 21.8 | <0.001 |
| Motor-vehicle collisions only | C3 | Cycle path vs. roadway | 32,518 | −5.0 | −7.3 to −2.6 | <0.001 |
| Motor-vehicle collisions only | D1 | Age 65 or over vs. 25–64 | 24,125 | +12.3 | 6.5 to 18.1 | <0.001 |
| Motor-vehicle collisions only | D2 | Male vs. female | 34,469 | +1.8 | 0.8 to 2.8 | <0.001 |
| Any-row location variables | A1 | E-scooter vs. bicycle | 42,994 | +2.0 | 0.8 to 3.3 | 0.001 |
| Any-row location variables | A2 | E-bike vs. bicycle | 33,966 | +5.1 | 3.0 to 7.1 | <0.001 |
| Any-row location variables | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 39,049 | −2.0 | −3.4 to −0.6 | 0.005 |
| Any-row location variables | B2 | Night without vs. with working street lighting | 8,512 | +1.3 | −5.8 to 8.3 | 0.727 |
| Any-row location variables | B3 | Adverse weather or non-dry surface vs. normal and dry | 45,418 | −0.1 | −2.0 to 1.8 | 0.902 |
| Any-row location variables | B4 | Reserved cycle facility vs. none | 43,104 | −2.2 | −3.8 to −0.6 | 0.006 |
| Any-row location variables | B5 | Intersection vs. no intersection | 46,919 | −0.0 | −0.8 to 0.8 | 0.935 |
| Any-row location variables | C1 | Heavy-vehicle vs. car opponent | 27,435 | +17.5 | 13.4 to 21.6 | <0.001 |
| Any-row location variables | C2 | Single-vehicle crash vs. collision with a motor vehicle | 40,132 | +12.5 | 8.3 to 16.7 | <0.001 |
| Any-row location variables | C3 | Cycle path vs. roadway | 42,800 | −4.7 | −7.1 to −2.3 | <0.001 |
| Any-row location variables | D1 | Age 65 or over vs. 25–64 | 33,037 | +12.9 | 6.4 to 19.4 | <0.001 |
| Any-row location variables | D2 | Male vs. female | 46,358 | +2.0 | 1.0 to 3.0 | <0.001 |
| Without location-file variables | A1 | E-scooter vs. bicycle | 42,994 | +0.8 | −0.4 to 2.1 | 0.198 |
| Without location-file variables | A2 | E-bike vs. bicycle | 33,966 | +5.2 | 3.2 to 7.3 | <0.001 |
| Without location-file variables | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 39,049 | −3.1 | −4.7 to −1.5 | <0.001 |
| Without location-file variables | B2 | Night without vs. with working street lighting | 8,512 | +2.3 | −4.7 to 9.3 | 0.514 |
| Without location-file variables | B3 | Adverse weather or non-dry surface vs. normal and dry | 45,418 | +0.5 | −1.4 to 2.4 | 0.593 |
| Without location-file variables | B4 | Reserved cycle facility vs. none | 43,104 | −3.3 | −5.0 to −1.5 | <0.001 |
| Without location-file variables | B5 | Intersection vs. no intersection | 46,919 | −0.8 | −1.6 to 0.0 | 0.053 |
| Without location-file variables | C1 | Heavy-vehicle vs. car opponent | 27,435 | +18.2 | 14.2 to 22.1 | <0.001 |
| Without location-file variables | C2 | Single-vehicle crash vs. collision with a motor vehicle | 40,132 | +14.4 | 9.7 to 19.2 | <0.001 |
| Without location-file variables | C3 | Cycle path vs. roadway | 42,800 | −3.9 | −5.8 to −2.0 | <0.001 |
| Without location-file variables | D1 | Age 65 or over vs. 25–64 | 33,037 | +12.9 | 6.4 to 19.4 | <0.001 |
| Without location-file variables | D2 | Male vs. female | 46,358 | +2.0 | 1.0 to 3.0 | <0.001 |
| Random-forest nuisance models | A1 | E-scooter vs. bicycle | 42,994 | +1.5 | 0.5 to 2.5 | 0.003 |
| Random-forest nuisance models | A2 | E-bike vs. bicycle | 33,966 | +3.9 | 2.2 to 5.6 | <0.001 |
| Random-forest nuisance models | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 39,049 | −2.8 | −4.5 to −1.1 | 0.001 |
| Random-forest nuisance models | B2 | Night without vs. with working street lighting | 8,512 | +4.6 | −0.3 to 9.5 | 0.063 |
| Random-forest nuisance models | B3 | Adverse weather or non-dry surface vs. normal and dry | 45,418 | −0.6 | −2.3 to 1.2 | 0.541 |
| Random-forest nuisance models | B4 | Reserved cycle facility vs. none | 43,104 | −3.8 | −5.4 to −2.1 | <0.001 |
| Random-forest nuisance models | B5 | Intersection vs. no intersection | 46,919 | −0.7 | −1.6 to 0.2 | 0.105 |
| Random-forest nuisance models | C1 | Heavy-vehicle vs. car opponent | 27,435 | +17.5 | 13.6 to 21.5 | <0.001 |
| Random-forest nuisance models | C2 | Single-vehicle crash vs. collision with a motor vehicle | 40,132 | +9.6 | 6.3 to 12.8 | <0.001 |
| Random-forest nuisance models | C3 | Cycle path vs. roadway | 42,800 | −5.0 | −7.5 to −2.5 | <0.001 |
| Random-forest nuisance models | D1 | Age 65 or over vs. 25–64 | 33,037 | +15.0 | 8.4 to 21.5 | <0.001 |
| Random-forest nuisance models | D2 | Male vs. female | 46,358 | +2.6 | 1.6 to 3.7 | <0.001 |
| Logistic nuisance models | A1 | E-scooter vs. bicycle | 42,994 | +1.2 | 0.3 to 2.2 | 0.009 |
| Logistic nuisance models | A2 | E-bike vs. bicycle | 33,966 | +4.4 | 2.7 to 6.2 | <0.001 |
| Logistic nuisance models | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 39,049 | −1.6 | −3.1 to −0.2 | 0.029 |
| Logistic nuisance models | B2 | Night without vs. with working street lighting | 8,512 | +1.1 | −3.4 to 5.6 | 0.624 |
| Logistic nuisance models | B3 | Adverse weather or non-dry surface vs. normal and dry | 45,418 | −0.8 | −2.4 to 0.8 | 0.317 |
| Logistic nuisance models | B4 | Reserved cycle facility vs. none | 43,104 | −3.2 | −5.1 to −1.3 | <0.001 |
| Logistic nuisance models | B5 | Intersection vs. no intersection | 46,919 | −0.4 | −1.3 to 0.4 | 0.325 |
| Logistic nuisance models | C1 | Heavy-vehicle vs. car opponent | 27,435 | +17.7 | 14.0 to 21.5 | <0.001 |
| Logistic nuisance models | C2 | Single-vehicle crash vs. collision with a motor vehicle | 40,132 | +11.5 | 7.8 to 15.1 | <0.001 |
| Logistic nuisance models | C3 | Cycle path vs. roadway | 42,800 | −4.7 | −7.4 to −2.0 | <0.001 |
| Logistic nuisance models | D1 | Age 65 or over vs. 25–64 | 33,037 | +13.4 | 7.1 to 19.7 | <0.001 |
| Logistic nuisance models | D2 | Male vs. female | 46,358 | +2.9 | 1.8 to 4.0 | <0.001 |
| Trimming at 0.01 | A1 | E-scooter vs. bicycle | 42,994 | +2.3 | 0.9 to 3.6 | 0.002 |
| Trimming at 0.01 | A2 | E-bike vs. bicycle | 33,966 | +5.3 | 3.1 to 7.4 | <0.001 |
| Trimming at 0.01 | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 39,049 | −2.0 | −3.5 to −0.6 | 0.005 |
| Trimming at 0.01 | B2 | Night without vs. with working street lighting | 8,512 | +1.0 | −7.3 to 9.2 | 0.813 |
| Trimming at 0.01 | B3 | Adverse weather or non-dry surface vs. normal and dry | 45,418 | −0.1 | −2.1 to 1.8 | 0.907 |
| Trimming at 0.01 | B4 | Reserved cycle facility vs. none | 43,104 | −2.1 | −3.7 to −0.5 | 0.008 |
| Trimming at 0.01 | B5 | Intersection vs. no intersection | 46,919 | −0.2 | −1.0 to 0.6 | 0.650 |
| Trimming at 0.01 | C1 | Heavy-vehicle vs. car opponent | 27,435 | +17.3 | 12.4 to 22.1 | <0.001 |
| Trimming at 0.01 | C2 | Single-vehicle crash vs. collision with a motor vehicle | 40,132 | +12.3 | 8.2 to 16.4 | <0.001 |
| Trimming at 0.01 | C3 | Cycle path vs. roadway | 42,800 | −4.2 | −6.9 to −1.4 | 0.003 |
| Trimming at 0.01 | D1 | Age 65 or over vs. 25–64 | 33,037 | +12.9 | 6.2 to 19.6 | <0.001 |
| Trimming at 0.01 | D2 | Male vs. female | 46,358 | +2.0 | 1.0 to 3.0 | <0.001 |
| Trimming at 0.05 | A1 | E-scooter vs. bicycle | 42,994 | +1.8 | 0.7 to 2.9 | 0.001 |
| Trimming at 0.05 | A2 | E-bike vs. bicycle | 33,966 | +4.7 | 2.9 to 6.6 | <0.001 |
| Trimming at 0.05 | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 39,049 | −2.0 | −3.4 to −0.6 | 0.004 |
| Trimming at 0.05 | B2 | Night without vs. with working street lighting | 8,512 | +3.2 | −0.5 to 6.9 | 0.091 |
| Trimming at 0.05 | B3 | Adverse weather or non-dry surface vs. normal and dry | 45,418 | −0.1 | −1.9 to 1.6 | 0.902 |
| Trimming at 0.05 | B4 | Reserved cycle facility vs. none | 43,104 | −2.4 | −3.9 to −1.0 | <0.001 |
| Trimming at 0.05 | B5 | Intersection vs. no intersection | 46,919 | −0.2 | −1.0 to 0.6 | 0.643 |
| Trimming at 0.05 | C1 | Heavy-vehicle vs. car opponent | 27,435 | +18.2 | 15.2 to 21.2 | <0.001 |
| Trimming at 0.05 | C2 | Single-vehicle crash vs. collision with a motor vehicle | 40,132 | +12.4 | 8.6 to 16.3 | <0.001 |
| Trimming at 0.05 | C3 | Cycle path vs. roadway | 42,800 | −4.5 | −6.4 to −2.6 | <0.001 |
| Trimming at 0.05 | D1 | Age 65 or over vs. 25–64 | 33,037 | +13.1 | 7.1 to 19.2 | <0.001 |
| Trimming at 0.05 | D2 | Male vs. female | 46,358 | +2.0 | 1.1 to 3.0 | <0.001 |
| Partially linear model | A1 | E-scooter vs. bicycle | 42,994 | +2.4 | 1.6 to 3.3 | <0.001 |
| Partially linear model | A2 | E-bike vs. bicycle | 33,966 | +3.4 | 2.1 to 4.7 | <0.001 |
| Partially linear model | B1 | Speed limit ≤30 vs. 50 km/h (urban) | 39,049 | −2.4 | −3.6 to −1.2 | <0.001 |
| Partially linear model | B2 | Night without vs. with working street lighting | 8,512 | +4.2 | 0.3 to 8.1 | 0.036 |
| Partially linear model | B3 | Adverse weather or non-dry surface vs. normal and dry | 45,418 | +0.4 | −0.9 to 1.8 | 0.514 |
| Partially linear model | B4 | Reserved cycle facility vs. none | 43,104 | −1.7 | −2.7 to −0.7 | 0.001 |
| Partially linear model | B5 | Intersection vs. no intersection | 46,919 | −0.3 | −1.1 to 0.5 | 0.417 |
| Partially linear model | C1 | Heavy-vehicle vs. car opponent | 27,435 | +16.7 | 13.9 to 19.5 | <0.001 |
| Partially linear model | C2 | Single-vehicle crash vs. collision with a motor vehicle | 40,132 | +11.3 | 7.1 to 15.6 | <0.001 |
| Partially linear model | C3 | Cycle path vs. roadway | 42,800 | −2.2 | −3.5 to −0.9 | <0.001 |
| Partially linear model | D1 | Age 65 or over vs. 25–64 | 33,037 | +15.8 | 12.7 to 18.8 | <0.001 |
| Partially linear model | D2 | Male vs. female | 46,358 | +2.0 | 1.0 to 2.9 | <0.001 |
| Early-adopter départements (both modes restricted) | A1 | E-scooter vs. bicycle | 20,214 | +0.9 | −0.4 to 2.2 | 0.181 |
| All other départements (both modes restricted) | A1 | E-scooter vs. bicycle | 22,780 | +3.1 | 0.9 to 5.3 | 0.005 |

*The fatal-outcome check uses killed versus not killed as the outcome. Early-adopter départements are the ten départements that recorded ten or more e-scooter riders in 2020; this check was corrected after the first run so that both modes are restricted (deviation D6).*


## Table S10. Sensitivity of the double machine learning estimates to unobserved confounding

| ID | Contrast | Estimate (pp) | RV (%) | RVa (%) | Benchmark: outcome (%) | Benchmark: factor (%) | Change in estimate under benchmark (pp) |
|---|---|---|---|---|---|---|---|
| A1 | E-scooter vs. bicycle | +2.1 | 1.4 | 0.7 | 5.9 | 4.2 | −0.5 |
| A2 | E-bike vs. bicycle | +5.1 | 3.4 | 2.4 | 5.6 | 2.3 | −0.9 |
| D1 | Age 65 or over vs. 25–64 | +12.9 | 7.1 | 6.2 | 10.8 | 16.3 | +8.8 |
| D2 | Male vs. female | +2.0 | 2.1 | 1.3 | 9.5 | 1.0 | +1.5 |
| B1 | Speed limit ≤30 vs. 50 km/h (urban) | −2.0 | 1.9 | 1.1 | 7.9 | 37.7 | −3.8 |
| B4 | Reserved cycle facility vs. none | −2.2 | 1.7 | 0.9 | 7.0 | 24.4 | −2.0 |
| B5 | Intersection vs. no intersection | −0.2 | 0.2 | 0.0 | 6.8 | 12.0 | −0.9 |
| B2 | Night without vs. with working street lighting | +1.4 | 1.2 | 0.0 | 4.2 | 34.2 | +5.0 |
| B3 | Adverse weather or non-dry surface vs. normal and dry | −0.1 | 0.1 | 0.0 | 7.0 | 7.9 | −0.7 |
| C1 | Heavy-vehicle vs. car opponent | +17.6 | 8.7 | 7.3 | 7.2 | 5.2 | −0.4 |
| C2 | Single-vehicle crash vs. collision with a motor vehicle | +12.5 | 6.0 | 5.3 | 7.7 | 34.0 | −6.2 |
| C3 | Cycle path vs. roadway | −4.5 | 1.8 | 1.2 | 6.7 | 6.0 | −1.0 |

*RV and RVa are the robustness values for the point estimate and for statistical significance. The benchmark is département: the columns give the share of residual variation in the outcome and in the factor that it explains, and the change in the estimate that an unobserved confounder of the same strength would produce.*
