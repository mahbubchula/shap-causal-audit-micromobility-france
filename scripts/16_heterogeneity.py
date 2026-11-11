"""Q5: group average effects for A1, B1 and B2 (plan section 9).
Group effects are means of the doubly robust score within each group; SEs clustered by departement;
intervals are Bonferroni-adjusted within each grouping variable (jointly valid).
Usage: python -I 16_heterogeneity.py <interim_dir> <results_dir>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from p1_dml import *
interim, res_dir = sys.argv[1:3]
A = pd.read_parquet(os.path.join(interim, "analysis_riders.parquet")); spec = json.load(open(os.path.join(interim, "feature_spec.json"))); CAT = spec["categorical"]
A = A[A["year"] >= 2020].reset_index(drop=True)
A["g_mode"] = A["mode"]; A["g_age"] = pd.cut(A["age"], [-1, 24, 64, 200], labels=["under 25", "25-64", "65+"]).astype(object)
A["g_sex"] = A["sex"]; A["g_urban"] = A["urban"].map({1: "urban", 0: "non-urban"})
A["g_opponent"] = np.where(A["opponent"].isin(["car", "van", "heavy", "ptw"]), "motor-vehicle opponent", "no motor-vehicle opponent")
E = encode(A, CAT)
for c in ("g_mode", "g_age", "g_sex", "g_urban", "g_opponent"): E[c] = A[c].values
LAB = {"A1": "E-scooter vs bicycle", "B1": "30 km/h or less vs 50 km/h (urban)", "B2": "Night unlit vs night lit"}
rows = []
for f in ("A1", "B1", "B2"):
    r, obj, d = fit_irm(E, f, adjustment(f), CAT, sens=False)
    score = obj.psi_elements["psi_b"][:, :, 0].mean(axis=1)            # doubly robust score, averaged over the 5 repetitions
    for gv in ("g_mode", "g_age", "g_sex", "g_urban", "g_opponent"):
        if (f == "A1" and gv == "g_mode") or (f == "B1" and gv == "g_urban"): continue
        ok = d[gv].notna().values; lv = [l for l in pd.unique(d.loc[ok, gv]) if (d.loc[ok, gv] == l).sum() >= 300 and d.loc[ok & (d[gv] == l).values, f"T_{f}"].nunique() == 2]
        ok = ok & d[gv].isin(lv).values
        X = pd.get_dummies(d.loc[ok, gv]).astype(float)[lv]
        fit = sm.OLS(score[ok], X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.loc[ok, "dep"])[0]})
        z = norm.ppf(1 - 0.05 / (2 * len(lv)))
        # Wald test that all group effects are equal
        Rm = np.zeros((len(lv) - 1, len(lv))); Rm[:, 0] = 1; Rm[np.arange(len(lv) - 1), np.arange(1, len(lv))] = -1
        p_eq = float(fit.wald_test(Rm, scalar=True).pvalue) if len(lv) > 1 else np.nan
        for l in lv:
            rows.append(dict(factor=f, label=LAB[f], grouping=gv[2:], group=l, n=int(X[l].sum()), effect=fit.params[l], se=fit.bse[l],
                             lo_joint=fit.params[l] - z * fit.bse[l], hi_joint=fit.params[l] + z * fit.bse[l], p_equal_across_groups=p_eq, overall=r["theta"]))
H = pd.DataFrame(rows); H.to_csv(os.path.join(res_dir, "heterogeneity_gate.csv"), index=False)
S = H.copy()
for c in ("effect", "se", "lo_joint", "hi_joint", "overall"): S[c] = (S[c] * 100).round(1)
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 100)
print(S[["label", "grouping", "group", "n", "effect", "lo_joint", "hi_joint", "p_equal_across_groups", "overall"]].round(4).to_string(index=False))
