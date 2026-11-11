"""Tables for Paper 1 (main Tables 1-7 and supplementary Tables S1-S10), built only from saved results.
Usage: python -I 21_tables.py <results_dir> <interim_dir> <audit_dir> <out_dir>
Writes <out>/csv/*.csv, <out>/tex/*.tex, <out>/Tables_Paper1.xlsx and <out>/tables_preview.md."""
import sys, os, json, re
import numpy as np, pandas as pd
res, interim, aud, out = sys.argv[1:5]
A = pd.read_parquet(os.path.join(interim, "analysis_riders.parquet")); M = A[A["year"] >= 2020]
D = pd.read_csv(os.path.join(res, "dml_main.csv")); AT = pd.read_csv(os.path.join(res, "audit_table.csv"))
MODES = ["bicycle", "ebike", "escooter"]; ML = {"bicycle": "Bicycle", "ebike": "E-bike", "escooter": "E-scooter", "all": "All riders"}
FAC = {"A1": "E-scooter vs. bicycle", "A2": "E-bike vs. bicycle", "D1": "Age 65 or over vs. 25\u201364", "D2": "Male vs. female", "B1": "Speed limit \u226430 vs. 50 km/h (urban)",
       "B4": "Reserved cycle facility vs. none", "B5": "Intersection vs. no intersection", "B2": "Night without vs. with working street lighting",
       "B3": "Adverse weather or non-dry surface vs. normal and dry", "B6": "Urban vs. outside urban area", "C1": "Heavy-vehicle vs. car opponent",
       "C2": "Single-vehicle crash vs. collision with a motor vehicle", "C3": "Cycle path vs. roadway", "R10": "Placebo: even vs. odd day of the month"}
ORDER = ["A1", "A2", "D1", "D2", "B1", "B4", "B5", "B2", "B3", "B6", "C1", "C2", "C3"]
mn = lambda s: str(s).replace("-", "\u2212")
pp = lambda v, d=1: mn(f"{v * 100:+.{d}f}")
ci = lambda lo, hi, d=1: mn(f"{lo * 100:.{d}f} to {hi * 100:.{d}f}")
pf = lambda p: "<0.001" if p < 0.001 else f"{p:.3f}"
npct = lambda k, n: f"{int(k):,} ({k / n * 100:.1f})" if n else "\u2013"
TABLES = []
def add(tid, title, df, notes, colspec=None): TABLES.append(dict(id=tid, title=title, df=df.reset_index(drop=True), notes=notes, colspec=colspec))

# ---------------- Table 1: data sources ----------------
I = pd.read_csv(os.path.join(aud, "integrity_by_year.csv")); tot = I[["crashes", "lieux_rows", "veh_rows", "usr_rows"]].sum()
add("Table1", "Data sources: the four annual files of the French national police crash database (BAAC), 2019\u20132025",
    pd.DataFrame([["Characteristics", "Crash", f"{int(tot['crashes']):,}", "Date and time, lighting, weather, d\u00e9partement, urban area, intersection type, collision type"],
                  ["Locations", "Road record (one per crash until 2022; one or more from 2023)", f"{int(tot['lieux_rows']):,}", "Road category, traffic regime, number of lanes, reserved lane, gradient, alignment, infrastructure, position of the crash, surface condition, speed limit"],
                  ["Vehicles", "Vehicle", f"{int(tot['veh_rows']):,}", "Vehicle category, maneuver before the crash, fixed and mobile obstacle struck, point of initial impact"],
                  ["Users", "Person", f"{int(tot['usr_rows']):,}", "Role, injury severity, sex, year of birth, trip purpose, safety equipment"]],
                 columns=["File", "Unit of observation", "Records, 2019\u20132025", "Variables used"]),
    ["Source: Observatoire national interminist\u00e9riel de la s\u00e9curit\u00e9 routi\u00e8re, open data portal data.gouv.fr, Licence Ouverte 2.0.",
     "Files are linked on the crash identifier; users are linked to vehicles on the vehicle identifier. ",
     "Derivation of the analysis sample: 382,721 injury crashes involving any road user; 55,909 micromobility vehicles; 54,580 bicycles, e-bikes or e-scooters; 52,722 in mainland France; 52,510 with the injury level of the rider recorded; 46,920 riders in crashes from 2020 to 2025."], "p{2.2cm}p{3.6cm}rp{7.2cm}")

# ---------------- Table 2: composition by partition and mode ----------------
rows = []
for sp, lab in (("development", "Development set, 2020\u20132023"), ("test", "Locked test set, 2024\u20132025"), ("sensitivity_2019", "Sensitivity analysis, 2019")):
    for m in MODES + ["all"]:
        d = A[(A["split"] == sp)] if m == "all" else A[(A["split"] == sp) & (A["mode"] == m)]
        rows.append([lab, ML[m], f"{len(d):,}", f"{d['Num_Acc'].nunique():,}", npct(d["ksi"].sum(), len(d)), npct(d["killed"].sum(), len(d))])
add("Table2", "Composition of the study sample by data partition and transport mode",
    pd.DataFrame(rows, columns=["Partition", "Mode", "Riders", "Crashes", "Killed or hospitalized, n (%)", "Killed, n (%)"]),
    ["Riders of bicycles, e-bikes and motorized personal mobility devices (e-scooters) involved in police-reported injury crashes in mainland France.",
     "A crash may involve riders of more than one mode; the number of crashes in the row for all riders is therefore smaller than the sum over modes."])

# ---------------- Table 3: variables by tier ----------------
V = [("0", "Year", "year", "Characteristics", "Year of the crash"), ("0", "Month", "month", "Characteristics", "Month of the crash"), ("0", "Day of week", "dow", "Characteristics", "Derived from the date of the crash"),
     ("0", "Hour of day", "hour", "Characteristics", "Hour of the crash"), ("0", "D\u00e9partement", "dep", "Characteristics", "D\u00e9partement in which the crash occurred"), ("0", "Urban area", "urban", "Characteristics", "Crash inside a built-up area"),
     ("1", "Transport mode", "mode", "Vehicles", "Bicycle, e-bike or motorized personal mobility device"), ("1", "Age", "age", "Users", "Year of the crash minus year of birth"), ("1", "Sex", "sex", "Users", "Sex of the rider"),
     ("1", "Trip purpose", "trip", "Users", "Purpose of the trip at the time of the crash"), ("1", "Passengers", "n_passengers", "Users", "Number of other occupants of the rider's vehicle"),
     ("2", "Road category", "catr", "Locations", "Administrative category of the road"), ("2", "Traffic regime", "circ", "Locations", "One-way, two-way or divided roadways"), ("2", "Number of lanes", "nbv", "Locations", "Total number of traffic lanes"),
     ("2", "Cycle facility", "vosp", "Locations", "Presence and type of a reserved lane (cycle path, cycle lane, other reserved lane)"), ("2", "Gradient", "prof", "Locations", "Longitudinal profile of the road"), ("2", "Alignment", "plan", "Locations", "Horizontal alignment of the road"),
     ("2", "Infrastructure", "infra", "Locations", "Special infrastructure at the site (tunnel, bridge, roundabout approach and others)"), ("2", "Speed limit", "vma", "Locations", "Maximum authorized speed at the site, km/h"),
     ("2", "Intersection type", "int_type", "Characteristics", "Type of intersection, or none"), ("2", "Lighting", "lum", "Characteristics", "Daylight, twilight, or night with or without working street lighting"),
     ("2", "Weather", "atm", "Characteristics", "Atmospheric conditions"), ("2", "Surface condition", "surf", "Locations", "Condition of the road surface"),
     ("3", "Position on road", "situ", "Locations", "Position of the crash (roadway, cycle path, sidewalk and others)"), ("3", "Collision type", "col", "Characteristics", "Type of collision"),
     ("3", "Opponent type", "opponent", "Vehicles", "Category of the other party, derived from the other vehicles and pedestrians in the crash"), ("3", "Vehicles involved", "n_vehicles", "Vehicles", "Number of vehicles in the crash (four or more grouped)"),
     ("3", "Pedestrian struck", "ped_struck", "Users", "At least one pedestrian struck by the rider's vehicle"), ("3", "Fixed obstacle", "obs", "Vehicles", "Fixed obstacle struck"), ("3", "Mobile obstacle", "obsm", "Vehicles", "Mobile obstacle struck"),
     ("3", "Point of impact", "choc", "Vehicles", "Point of initial impact on the vehicle"), ("3", "Maneuver", "manv", "Vehicles", "Main maneuver before the crash")]
spec = json.load(open(os.path.join(interim, "feature_spec.json"))); CAT = set(spec["categorical"]); TN = {"0": "0: time and place", "1": "1: rider and vehicle", "2": "2: road and conditions", "3": "3: crash configuration"}
rows = []
for t, lab, c, src, dfn in V:
    typ = f"Categorical, {M[c].nunique()} levels" if c in CAT else (f"Binary" if M[c].dropna().nunique() == 2 else f"Numeric, {M[c].min():.0f}\u2013{M[c].max():.0f}")
    rows.append([TN[t], lab, src, typ, dfn, f"{M[c].isna().mean() * 100:.1f}"])
add("Table3", "Explanatory variables by temporal tier", pd.DataFrame(rows, columns=["Tier", "Variable", "Source file", "Type", "Definition", "Unknown (%)"]),
    ["Unknown (%) is the share of the 46,920 riders in the analysis sample (2020\u20132025) for whom the variable is not recorded. Unknown values are retained as a separate category or as missing values handled by the learner; no value is imputed outside the training folds.",
     "Safety equipment, the injury severity of other persons, identifiers and coordinates are excluded from all models (Figure 4)."], "p{2.6cm}p{2.5cm}p{2.0cm}p{2.6cm}p{5.6cm}r")

# ---------------- Table 4: characteristics by mode (items not shown in Figure 2) ----------------
def block(label, cond_known, items):
    r = [[label] + [""] * 4]
    for name, cond in items:
        cells = []
        for m in MODES + ["all"]:
            d = M if m == "all" else M[M["mode"] == m]; k = cond_known(d); cells.append(npct(cond(d)[k].sum(), int(k.sum())))
        r.append(["   " + name] + cells)
    return r
allk = lambda d: pd.Series(True, index=d.index)
rows = [["Riders, n"] + [f"{len(M[M['mode'] == m]):,}" for m in MODES] + [f"{len(M):,}"]]
rows += block("Rider", lambda d: d["sex"].notna(), [("Male", lambda d: d["sex"] == "male")])
rows += block("Trip purpose", lambda d: d["trip"].notna(), [("Commuting to work", lambda d: d["trip"] == "1"), ("Traveling to school", lambda d: d["trip"] == "2"), ("Professional use", lambda d: d["trip"] == "4"),
                                                           ("Leisure", lambda d: d["trip"] == "5"), ("Shopping or other", lambda d: d["trip"].isin(["3", "9"]))])
rows += block("Time and place", allk, [("Urban area", lambda d: d["urban"] == 1), ("Paris police area (d\u00e9partements 75, 92, 93, 94)", lambda d: d["paris_police_area"] == 1), ("Saturday or Sunday", lambda d: d["dow"] >= 5)])
rows += block("Lighting", lambda d: d["lum"].notna(), [("Daylight", lambda d: d["lum"] == "1"), ("Twilight", lambda d: d["lum"] == "2"), ("Night, street lighting on", lambda d: d["lum"] == "5"), ("Night, no working street lighting", lambda d: d["lum"].isin(["3", "4"]))])
rows += block("Weather and surface", lambda d: d["T_B3"].notna(), [("Adverse weather or non-dry surface", lambda d: d["T_B3"] == 1)])
rows += block("Speed limit", lambda d: d["vma"].notna(), [("30 km/h or less", lambda d: d["vma"] <= 30), ("31\u201349 km/h", lambda d: d["vma"].between(31, 49)), ("50 km/h", lambda d: d["vma"] == 50), ("More than 50 km/h", lambda d: d["vma"] > 50)])
rows += block("Road", lambda d: d["catr"].notna(), [("Communal road", lambda d: d["catr"] == "4"), ("Departmental road", lambda d: d["catr"] == "3"), ("Other road category", lambda d: ~d["catr"].isin(["3", "4"]))])
rows += block("Cycle facility at the site", lambda d: d["vosp"].notna(), [("Cycle path or cycle lane", lambda d: d["vosp"].isin(["1", "2"])), ("Other reserved lane", lambda d: d["vosp"] == "3"), ("None", lambda d: d["vosp"] == "0")])
rows += block("Intersection", lambda d: d["int_type"].notna(), [("At an intersection", lambda d: d["int_type"] != "1")])
rows += block("Position of the crash", lambda d: d["situ"].notna(), [("Roadway", lambda d: d["situ"] == "1"), ("Cycle path", lambda d: d["situ"] == "5"), ("Other position", lambda d: ~d["situ"].isin(["1", "5"]))])
rows += block("Crash configuration", allk, [("Pedestrian struck", lambda d: d["ped_struck"] == 1), ("Carrying at least one passenger", lambda d: d["n_passengers"] > 0)])
add("Table5", "Characteristics of riders and crashes by transport mode, 2020\u20132025", pd.DataFrame(rows, columns=["Characteristic", "Bicycle", "E-bike", "E-scooter", "All riders"]),
    ["Values are n (%) unless stated otherwise. Percentages are calculated among riders for whom the characteristic is recorded; the share of unknown values is given in Table 3.",
     "Injury severity, age, hour of the crash and type of opponent are shown in Figure 2 and are not repeated here."])

# ---------------- Table 5: pre-specified factors ----------------
ADJ = {"A1": "Tier 0; age, sex, trip purpose, passengers; Tier 2", "A2": "Tier 0; age, sex, trip purpose, passengers; Tier 2", "D1": "Tier 0; sex, mode", "D2": "Tier 0; age, mode",
       "B1": "Tiers 0\u20131; other Tier 2", "B4": "Tiers 0\u20131; other Tier 2", "B5": "Tiers 0\u20131; other Tier 2", "B2": "Tiers 0\u20131; other Tier 2", "B3": "Tiers 0\u20131; other Tier 2 except weather and surface",
       "B6": "Other Tier 0; age, sex, mode", "C1": "Tiers 0\u20132", "C2": "Tiers 0\u20132", "C3": "Tiers 0\u20132"}
POP = {"A1": "Riders of the two modes", "A2": "Riders of the two modes", "D1": "Riders aged 25 or over", "D2": "Riders of known sex", "B1": "Urban crashes with those limits", "B4": "Sites with the facility recorded",
       "B5": "All riders", "B2": "Crashes at night", "B3": "All riders", "B6": "All riders", "C1": "Two-party collisions with a car or heavy vehicle", "C2": "Those two crash types", "C3": "Those two positions"}
TIER = {"A1": 1, "A2": 1, "D1": 1, "D2": 1, "B1": 2, "B4": 2, "B5": 2, "B2": 2, "B3": 2, "B6": 0, "C1": 3, "C2": 3, "C3": 3}
Dm = D[(D["variant"] == "main") & (D["group"] == "all")].set_index("factor"); rows = []
for f in ORDER:
    t = M["T_" + f]; a, b = M[t == 1], M[t == 0]
    rows.append([f, FAC[f], POP[f], TIER[f], ADJ[f], int(Dm.loc[f, "n_x"]), f"{len(a):,}", f"{int(a['ksi'].sum()):,}", f"{len(b):,}", f"{int(b['ksi'].sum()):,}"])
add("Table4", "Pre-specified factors, populations and adjustment sets", pd.DataFrame(rows, columns=["ID", "Contrast (first-named vs. reference)", "Population", "Tier", "Adjustment set", "Covariates", "First-named group, n", "of whom severe", "Reference group, n", "of whom severe"]),
    ["Factors, populations and adjustment sets were fixed in the pre-analysis plan before any outcome model was fitted. Tiers are defined in Table 3. Severe denotes killed or hospitalized.",
     "Contrasts A1, A2, D1 and D2 compare kinds of riders and are interpreted as adjusted differences, not as effects of an intervention."], "lp{3.6cm}p{2.6cm}cp{3.4cm}rrrrr")

# ---------------- Table 6: double ML inference diagnostics ----------------
rows = []
for f in ORDER + ["R10"]:
    r = Dm.loc[f]
    rows.append([f, FAC[f], f"{r['se'] * 100:.2f}", f"{r['se_iid'] * 100:.2f}", f"{r['se'] / r['se_iid']:.2f}", pf(r["p"]), pf(r["q_bh"]) if pd.notna(r["q_bh"]) else "\u2013", f"{r['ps_auc']:.3f}", f"{r['ps_outside'] * 100:.1f}",
                 f"{r['rva'] * 100:.1f}" if pd.notna(r.get("rva")) else "\u2013", ci(r["theta_lo_sens"], r["theta_hi_sens"]) if pd.notna(r.get("theta_lo_sens")) else "\u2013"])
b6, pl = Dm.loc["B6"], Dm.loc["R10"]
add("Table6", "Inference diagnostics for the double machine learning estimates, all riders",
    pd.DataFrame(rows, columns=["ID", "Contrast", "SE, clustered (pp)", "SE, unclustered (pp)", "Ratio", "p", "q", "Propensity AUC", "Outside trimming bounds (%)", "RVa (%)", "Bounds under 3% confounding (pp)"]),
    ["Point estimates and 95% confidence intervals are given in Figure 7a. SE, standard error in percentage points (pp), clustered by d\u00e9partement or unclustered; q, Benjamini\u2013Hochberg false discovery rate across the 43 estimates of the main analysis.",
     "Propensity AUC is the cross-fitted discrimination of the model for group membership. Outside trimming bounds is the share of riders with an estimated propensity score below 0.02 or above 0.98.",
     "RVa is the robustness value for statistical significance: the share of residual variation in both the factor and the outcome that an unobserved confounder would need to explain for the 95% confidence interval to include zero. Bounds are the range of the estimate if such a confounder explained 3% of each. Robustness values for the point estimate are given in Figure 10d.",
     f"B6 does not satisfy the overlap condition ({b6['ps_outside'] * 100:.0f}% of propensity scores outside the trimming bounds); its estimate, {pp(b6['theta'])} ({ci(b6['lo'], b6['hi'])}), is not interpreted. The placebo estimate is {pp(pl['theta'])} ({ci(pl['lo'], pl['hi'])})."],
    "lp{4.2cm}rrrrrrrrr")

# ---------------- Table 7: agreement between SHAP and double ML (urban contrast excluded) ----------------
T = AT[AT["factor"] != "B6"].copy(); T["sig"] = T["q_bh"] < 0.05; T["same"] = np.sign(T["shap_contrast_prob"]) == np.sign(T["dml"])
T["in_ci"] = T["shap_contrast_prob"].between(T["dml_lo"], T["dml_hi"]); T["wi_ci"] = T["whatif_prob"].between(T["dml_lo"], T["dml_hi"])
T["ratio"] = T["shap_contrast_prob"].abs() / T["dml"].abs(); T["z"] = (T["shap_contrast_prob"] - T["dml"]) / ((T["dml_hi"] - T["dml_lo"]) / 3.92); rows = []
frac = lambda s: f"{int(s.sum())}/{len(s)} ({s.mean() * 100:.0f})" if len(s) else "\u2013"
for g in ["all", "bicycle", "ebike", "escooter", "any"]:
    d = T if g == "any" else T[T["group"] == g]; s = d[d["sig"]]
    rows.append(["All estimates" if g == "any" else ML[g], len(d), len(s), frac(d["same"]), frac(s["same"]), frac(d["in_ci"]), frac(d["wi_ci"]), frac(s["ratio"] < 1), f"{s['ratio'].median():.2f}" if len(s) else "\u2013", frac(d["z"].abs() > 1.96)])
add("Table7", "Agreement between the SHAP contrast and the double machine learning estimate",
    pd.DataFrame(rows, columns=["Set of estimates", "Estimates", "With q < 0.05", "Same sign, all", "Same sign, q < 0.05", "SHAP within 95% CI", "What-if within 95% CI", "SHAP smaller in magnitude, q < 0.05", "Median ratio, q < 0.05", "Standardized difference beyond \u00b11.96"]),
    ["Cells give the number of estimates meeting the criterion over the number considered, with the percentage in parentheses. The ratio is the absolute SHAP contrast divided by the absolute double ML estimate.",
     "The urban versus non-urban contrast is excluded because the overlap condition was not satisfied. Rank concordance between the readings is shown in Figure 7e."])

# ---------------- Supplementary tables ----------------
bp = json.load(open(os.path.join(res, "best_params.json")))["lgbm"]
SP = [("Number of leaves", "num_leaves", "Integer, 8\u201363"), ("Learning rate", "learning_rate", "Log-uniform, 0.02\u20130.12"), ("Number of trees", "n_estimators", "Integer, 150\u2013899"), ("Minimum riders per leaf", "min_child_samples", "Integer, 20\u2013199"),
      ("Row subsampling", "subsample", "Uniform, 0.6\u20131.0"), ("Column subsampling", "colsample_bytree", "Uniform, 0.5\u20131.0"), ("L2 regularization", "reg_lambda", "Log-uniform, 0.1\u201330"), ("Categorical smoothing", "cat_smooth", "Log-uniform, 5\u2013100")]
add("TableS1", "Hyperparameter search space and selected values of the gradient-boosting model", pd.DataFrame([[a, c, f"{bp[b]:.3g}" if isinstance(bp[b], float) else str(bp[b])] for a, b, c in SP], columns=["Hyperparameter", "Search distribution", "Selected value"]),
    ["Random search with 30 configurations, selected on mean log loss over five folds grouped by crash within the development set (2020\u20132023). The inverse regularization strength of the logistic regression was 0.3."])
tm = pd.read_csv(os.path.join(res, "test_metrics.csv")); rng3 = lambda r, k: f"{r[k]:.3f} ({r[k + '_lo']:.3f}\u2013{r[k + '_hi']:.3f})"
add("TableS2", "Predictive performance on the locked test set (2024\u20132025) by model and transport mode",
    pd.DataFrame([[{"LightGBM": "Gradient boosting", "Logistic": "Logistic regression"}[r["model"]], ML[r["group"]], f"{int(r['n']):,}", f"{r['prevalence'] * 100:.1f}", rng3(r, "roc_auc"), rng3(r, "pr_auc"), rng3(r, "brier"), f"{r['log_loss']:.3f}", f"{r['cal_slope']:.2f}", mn(f"{r['cal_intercept']:.2f}")] for _, r in tm.iterrows()],
                 columns=["Model", "Riders", "n", "Severe (%)", "ROC AUC (95% CI)", "PR AUC (95% CI)", "Brier score (95% CI)", "Log loss", "Calibration slope", "Calibration intercept"]),
    ["Confidence intervals are obtained by bootstrap resampling of crashes."])
L = pd.read_csv(os.path.join(res, "leakage_protocols.csv")); PN = ["Random split of riders, global preprocessing", "As above, plus outcome-dependent variables", "Oversampling to 50:50 before the random split", "Grouped by crash, 2020\u20132025, in-fold preprocessing",
                                                                 "Grouped by crash, 2020\u20132023", "Forward in time: locked test set, 2024\u20132025", "Forward chaining: validation on 2021", "Forward chaining: validation on 2022", "Forward chaining: validation on 2023"]
add("TableS3", "Performance of the gradient-boosting model under nine validation protocols",
    pd.DataFrame([[PN[i], f"{int(r['n']):,}", f"{r['prevalence'] * 100:.1f}", f"{r['roc_auc']:.3f}", f"{r['pr_auc']:.3f}", f"{r['brier']:.3f}", f"{r['log_loss']:.3f}", f"{r['cal_slope']:.2f}", mn(f"{r['cal_intercept']:.2f}")] for i, r in L.iterrows()],
                 columns=["Validation protocol", "n evaluated", "Severe (%)", "ROC AUC", "PR AUC", "Brier score", "Log loss", "Calibration slope", "Calibration intercept"]),
    ["Hyperparameters are identical across protocols. Oversampling changes the share of severe outcomes, so that only the ROC AUC is comparable for that protocol."])
C = pd.read_csv(os.path.join(aud, "outcome_dependent_recording.csv")); VL = {c: lab for _, lab, c, _, _ in V}; VL["LEAK_equip"] = "Safety equipment (excluded)"
W = C.pivot(index="feature", columns="mode", values=["unk_severe", "unk_not_severe", "diff"]); W = W.loc[W["diff"].abs().max(axis=1).sort_values(ascending=False).index]
add("TableS4", "Share of riders with each variable recorded as unknown, by injury severity and transport mode",
    pd.DataFrame([[VL.get(f, f)] + sum([[f"{W.loc[f, ('unk_severe', m)]:.1f}", f"{W.loc[f, ('unk_not_severe', m)]:.1f}", mn(f"{W.loc[f, ('diff', m)]:+.1f}")] for m in MODES], []) for f in W.index],
                 columns=["Variable"] + sum([[f"{ML[m]}: severe (%)", f"{ML[m]}: not severe (%)", f"{ML[m]}: difference"] for m in MODES], [])),
    ["Severe denotes killed or hospitalized. Differences are in percentage points (severe minus not severe). Variables are ordered by the largest absolute difference across modes."])
Im = pd.read_csv(os.path.join(res, "shap_importance_test.csv"), index_col=0); St = pd.read_csv(os.path.join(res, "shap_stability.csv"), index_col=0)
add("TableS5", "Mean absolute SHAP value of all variables on the locked test set and stability of the importance rank",
    pd.DataFrame([[int(r["rank"]), VL.get(f, f), r["tier"].replace("tier", ""), f"{r['mean_abs_shap_logodds']:.3f}"] + [f"{r[m]:.3f}" for m in MODES] + [f"{St.loc[f, 'rank_median']:.0f}", f"{St.loc[f, 'rank_min']:.0f}\u2013{St.loc[f, 'rank_max']:.0f}"] for f, r in Im.iterrows()],
                 columns=["Rank", "Variable", "Tier", "All riders", "Bicycle", "E-bike", "E-scooter", "Median rank, 25 refits", "Range of rank"]),
    ["SHAP values are in log-odds of a severe outcome. Refits are five seeds by five folds grouped by crash within the development set."])
rows = []
for g in ["all"] + MODES:
    for f in ORDER:
        d = AT[(AT["group"] == g) & (AT["factor"] == f)]
        if len(d):
            r = d.iloc[0]; rows.append([ML[g], f, FAC[f], f"{int(r['n']):,}", pp(r["raw_diff"]), pp(r["shap_contrast_prob"]), pp(r["whatif_prob"]), pp(r["dml"]), ci(r["dml_lo"], r["dml_hi"]), pf(r["p"]), pf(r["q_bh"])])
add("TableS6", "Unadjusted difference, SHAP contrast, model what-if and double machine learning estimate for all 43 estimates",
    pd.DataFrame(rows, columns=["Riders", "ID", "Contrast", "n", "Unadjusted (pp)", "SHAP contrast (pp)", "Model what-if (pp)", "Double ML (pp)", "95% CI", "p", "q"]),
    ["pp, percentage points of the probability of being killed or hospitalized. Estimates are omitted where either group contained fewer than 200 riders or 30 severe outcomes. B6 does not satisfy the overlap condition and is not interpreted."], "llp{4.4cm}rrrrrrrr")
Da = D[D["variant"] == "all_controls"].set_index("factor")
add("TableS7", "Double machine learning estimates under the pre-specified adjustment set and under all controls, all riders",
    pd.DataFrame([[f, FAC[f], int(Dm.loc[f, "n_x"]), pp(Dm.loc[f, "theta"]), ci(Dm.loc[f, "lo"], Dm.loc[f, "hi"]), int(Da.loc[f, "n_x"]), pp(Da.loc[f, "theta"]), ci(Da.loc[f, "lo"], Da.loc[f, "hi"]), pp(Da.loc[f, "theta"] - Dm.loc[f, "theta"])] for f in ORDER],
                 columns=["ID", "Contrast", "Covariates, pre-specified", "Estimate (pp)", "95% CI", "Covariates, all controls", "Estimate (pp)", "95% CI", "Change (pp)"]),
    ["All controls denotes adjustment for every explanatory variable other than those defining the factor, including variables in later tiers."], "lp{4.4cm}rrrrrrr")
H = pd.read_csv(os.path.join(res, "heterogeneity_gate.csv")); GN = {"mode": "Mode", "age": "Age", "sex": "Sex", "urban": "Setting", "opponent": "Opponent"}
add("TableS8", "Group average effects for three factors",
    pd.DataFrame([[r["factor"], FAC[r["factor"]], GN[r["grouping"]], r["group"].replace("-", "\u2013") if r["grouping"] == "age" else r["group"], f"{int(r['n']):,}", pp(r["effect"]), f"{r['se'] * 100:.2f}", ci(r["lo_joint"], r["hi_joint"]), pf(r["p_equal_across_groups"])] for _, r in H.iterrows()],
                 columns=["ID", "Contrast", "Grouping variable", "Group", "n", "Effect (pp)", "SE (pp)", "Joint 95% CI", "p, equality across groups"]),
    ["Group average effects are obtained by regressing the doubly robust score on group indicators, with standard errors clustered by d\u00e9partement and Bonferroni adjustment within each grouping variable."], "lp{3.6cm}llrrrrr")
R = pd.read_csv(os.path.join(res, "robustness.csv")); R5 = pd.read_csv(os.path.join(res, "robustness_r5_corrected.csv"))
CK = [("R1 include 2019", "Including 2019"), ("R2 exclude Paris police area", "Excluding the Paris police area"), ("R3 fatal outcome", "Fatal outcome"), ("R4 motor-vehicle collisions only", "Motor-vehicle collisions only"),
      ("R6a any-row location variables", "Any-row location variables"), ("R6b drop location-file variables", "Without location-file variables"), ("R7a random forest nuisances", "Random-forest nuisance models"),
      ("R7b logistic nuisances", "Logistic nuisance models"), ("R8a trim 0.01", "Trimming at 0.01"), ("R8b trim 0.05", "Trimming at 0.05"), ("R9 partially linear model", "Partially linear model")]
rows = []
for key, lab in CK:
    for _, r in R[(R["check"] == key) & (R["status"] == "ok")].iterrows(): rows.append([lab, r["factor"], FAC[r["factor"]], f"{int(r['n']):,}", pp(r["theta"]), ci(r["lo"], r["hi"]), pf(r["p"])])
for (_, r), lab in zip(R5.iterrows(), ("Early-adopter d\u00e9partements (both modes restricted)", "All other d\u00e9partements (both modes restricted)")): rows.append([lab, "A1", FAC["A1"], f"{int(r['n']):,}", pp(r["theta"]), ci(r["lo"], r["hi"]), pf(r["p"])])
add("TableS9", "Double machine learning estimates under each robustness check", pd.DataFrame(rows, columns=["Robustness check", "ID", "Contrast", "n", "Estimate (pp)", "95% CI", "p"]),
    ["The fatal-outcome check uses killed versus not killed as the outcome. Early-adopter d\u00e9partements are the ten d\u00e9partements that recorded ten or more e-scooter riders in 2020; this check was corrected after the first run so that both modes are restricted (deviation D6)."], "p{4.6cm}lp{4.4cm}rrrr")
B = R[R["check"] == "R11 benchmark: departement"].set_index("factor")
add("TableS10", "Sensitivity of the double machine learning estimates to unobserved confounding",
    pd.DataFrame([[f, FAC[f], pp(B.loc[f, "theta"]), f"{B.loc[f, 'rv'] * 100:.1f}", f"{B.loc[f, 'rva'] * 100:.1f}", f"{B.loc[f, 'bench_cf_y'] * 100:.1f}", f"{B.loc[f, 'bench_cf_d'] * 100:.1f}", pp(B.loc[f, "bench_delta_theta"])] for f in ORDER if f in B.index],
                 columns=["ID", "Contrast", "Estimate (pp)", "RV (%)", "RVa (%)", "Benchmark: outcome (%)", "Benchmark: factor (%)", "Change in estimate under benchmark (pp)"]),
    ["RV and RVa are the robustness values for the point estimate and for statistical significance. The benchmark is d\u00e9partement: the columns give the share of residual variation in the outcome and in the factor that it explains, and the change in the estimate that an unobserved confounder of the same strength would produce."], "lp{4.4cm}rrrrrr")

# ---------------- writers ----------------
for sub in ("csv", "tex"): os.makedirs(os.path.join(out, sub), exist_ok=True)
def tex(s):
    s = str(s)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"), ("\u2212", "$-$"), ("\u2264", r"$\leq$"), ("\u2265", r"$\geq$"), ("\u00b1", r"$\pm$"), ("\u2192", r"$\rightarrow$"), ("<", "$<$"), (">", "$>$")): s = s.replace(a, b)
    return re.sub(r"^(\s{3})", r"\\quad ", s)
md = ["# Tables, Paper 1\n", "Produced by `scripts/21_tables.py` from saved results. Each table is also written as CSV (`csv/`), LaTeX (`tex/`) and as a sheet of `Tables_Paper1.xlsx`.\n"]
with pd.ExcelWriter(os.path.join(out, "Tables_Paper1.xlsx")) as xw:
    for t in TABLES:
        df, tid = t["df"], t["id"]; num = tid.replace("Table", "Table ")
        df.to_csv(os.path.join(out, "csv", tid + ".csv"), index=False, encoding="utf-8-sig")
        x = pd.concat([pd.DataFrame([[f"{num}. {t['title']}"] + [""] * (df.shape[1] - 1)], columns=df.columns), pd.DataFrame([list(df.columns)], columns=df.columns), df.astype(str),
                       pd.DataFrame([[n] + [""] * (df.shape[1] - 1) for n in t["notes"]], columns=df.columns)]); x.to_excel(xw, sheet_name=tid, index=False, header=False)
        spec_ = t["colspec"] or ("l" + "r" * (df.shape[1] - 1)); wide = df.shape[1] > 6 or bool(t["colspec"])
        body = " \\\\\n".join(" & ".join(tex(v) for v in row) for row in df.astype(str).values)
        tab = "\\begin{tabular}{" + spec_ + "}\n\\toprule\n" + " & ".join(tex(c) for c in df.columns) + " \\\\\n\\midrule\n" + body + " \\\\\n\\bottomrule\n\\end{tabular}"
        if wide: tab = "\\resizebox{\\textwidth}{!}{%\n" + tab + "}"
        open(os.path.join(out, "tex", tid + ".tex"), "w", encoding="utf-8").write(
            "\\begin{table}[tp]\n\\centering\\small\n\\caption{" + tex(t["title"]) + "}\\label{tab:" + tid.lower() + "}\n\\begin{threeparttable}\n" + tab +
            "\n\\begin{tablenotes}[flushleft]\\footnotesize\n" + "\n".join("\\item " + tex(n) for n in t["notes"]) + "\n\\end{tablenotes}\n\\end{threeparttable}\n\\end{table}\n")
        md += [f"\n## {num}. {t['title']}\n", "| " + " | ".join(df.columns) + " |", "|" + "---|" * df.shape[1]] + ["| " + " | ".join(str(v).replace("|", "/").replace("   ", "\u2003") for v in row) + " |" for row in df.astype(str).values] + [""] + [f"*{n}*\n" for n in t["notes"]]
open(os.path.join(out, "tables_preview.md"), "w", encoding="utf-8").write("\n".join(md))
for t in TABLES: print(f"  {t['id']:8s} {t['df'].shape[0]:3d} rows x {t['df'].shape[1]:2d} cols  {t['title'][:70]}")
