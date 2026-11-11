# Pre-analysis plan: integrity record and deviations

The pre-analysis plan (`05_Pre_Analysis_Plan_Paper1.md`, version 1.0) was frozen on 11 November 2026 at 08:10:29 UTC, before any outcome model was fitted.

SHA-256 of the frozen file: `7b44260fbf35b94cf134eb122cfd027a0b15e87992f7cb25a92ac07d7d341965`

Verify with `shasum -a 256 docs/05_Pre_Analysis_Plan_Paper1.md`.

Outcome information viewed before the plan was frozen: national rider injury levels by mode and year (counts); shares of killed-or-hospitalised e-scooter riders by area before 2023; missing-value rates and code distributions by year. No predictive or causal model had been fitted.

## Deviations

| # | Deviation | Reason |
|---|---|---|
| D1 | Added leakage protocol (a+): oversampling the minority class to 50:50 before a random row split | A widespread practice in crash-severity papers; the plan's four protocols did not cover it. Added before seeing any protocol result. |
| D2 | Added protocol (c) on all years, alongside the planned development-only version | Separates the effect of grouping by crash from the effect of time |
| D3 | SHAP values for the audit are computed out-of-fold on the whole 2020–2025 sample (grouped five-fold), in log-odds, and converted to the probability scale at each rider's own predicted risk. Global importance is still reported on the locked test set. | Out-of-fold values avoid in-sample explanations and match the population used by double ML. LightGBM's exact TreeSHAP works in log-odds. |
| D4 | Factor B6 (urban vs non-urban) is reported as not reliably identified and is left out of the robustness checks | 33% of estimated propensity scores fall outside [0.02, 0.98]: département almost determines whether a crash is urban, so the two groups do not overlap |
| D5 | The SHAP intervals in the audit reflect resampling of riders only, with the model held fixed | Stated so they are not read as full uncertainty; model-refit variation is reported separately through the 25-model stability analysis |
| D6 | Robustness check R5 was re-run for the e-scooter vs bicycle contrast with both modes restricted to the ten early-adopter départements. The first version (only e-scooter riders restricted, cyclists kept everywhere) is retained in `robustness.csv` but not interpreted. | The first version removed all e-scooter riders from 86 départements while keeping cyclists there, so the estimate (−12.9 points) relied on extrapolation and not on comparable riders. Found when reading the robustness output; corrected in `15b_robustness_r5_check.py`. |
| D7 | The agreement statistics between SHAP and double ML (Table 7, Figure 6) are reported for 12 factors and 39 estimates, leaving out the urban vs non-urban contrast (B6). The earlier summary in `audit_summary.csv` covered 13 factors and 43 estimates. | B6 fails the overlap condition (D4), so an agreement statistic that counts it would rest on an estimate that is not interpreted. With B6 left out: 17 estimates have a false discovery rate below 0.05 (9 for all riders), sign agreement among them is 17/17, the SHAP contrast lies inside the double ML interval for 34/39, and the median ratio is 0.72 for all riders. |
| D8 | Three descriptive summaries were added when the figures were redesigned, all computed from saved results without refitting: the least-squares slope of the SHAP contrast on double ML with all controls (0.97, against 0.83 for the pre-specified set), the mean absolute difference between each model-based reading and the two double ML estimates (1.20 and 1.23 points falling to 0.90), and Kendall rank correlations between the four readings (SHAP vs double ML 0.73). | They quantify the decomposition already planned in Section 8 of the plan. They are labelled as descriptive and were not pre-specified. |
