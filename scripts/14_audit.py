"""Q4: the audit. SHAP contrast vs model what-if vs double ML (pre-specified adjustment) vs double ML (all controls).
Usage: python -I 14_audit.py <results_dir>"""
import sys, os, json
import numpy as np, pandas as pd
from scipy.stats import kendalltau
res = sys.argv[1]
S = pd.read_csv(os.path.join(res, "audit_shap_side.csv")); D = pd.read_csv(os.path.join(res, "dml_main.csv")); D = D[D["status"] == "ok"]
LAB = {"A1": "E-scooter vs bicycle", "A2": "E-bike vs bicycle", "B1": "30 km/h or less vs 50 km/h (urban)", "B2": "Night unlit vs night lit",
       "B3": "Adverse weather/surface vs normal", "B4": "Cycle facility present vs none", "B5": "Intersection vs none", "B6": "Urban vs non-urban",
       "C1": "Heavy-vehicle vs car opponent", "C2": "Single-vehicle vs motor-vehicle collision", "C3": "On cycle path vs carriageway",
       "D1": "Age 65+ vs 25-64", "D2": "Male vs female"}
m = D[D["variant"] == "main"][["factor", "group", "theta", "lo", "hi", "p", "q_bh", "rv"]].rename(columns={"theta": "dml", "lo": "dml_lo", "hi": "dml_hi"})
a = D[D["variant"] == "all_controls"][["factor", "group", "theta", "lo", "hi"]].rename(columns={"theta": "dml_allc", "lo": "allc_lo", "hi": "allc_hi"})
T = S.merge(m, on=["factor", "group"], how="inner").merge(a, on=["factor", "group"], how="left")
T["label"] = T["factor"].map(LAB)
T["same_sign"] = np.sign(T["shap_contrast_prob"]) == np.sign(T["dml"])
T["shap_in_ci"] = T["shap_contrast_prob"].between(T["dml_lo"], T["dml_hi"])
T["whatif_in_ci"] = T["whatif_prob"].between(T["dml_lo"], T["dml_hi"])
T["ratio_shap_dml"] = T["shap_contrast_prob"].abs() / T["dml"].abs()
T["dml_sig"] = T["q_bh"] < 0.05
T.to_csv(os.path.join(res, "audit_table.csv"), index=False)
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 200)
P = T[T["group"] == "all"].copy()
show = P[["label", "raw_diff", "shap_contrast_prob", "whatif_prob", "dml", "dml_lo", "dml_hi", "dml_allc", "allc_lo", "allc_hi"]].copy()
for c in show.columns[1:]: show[c] = (show[c] * 100).round(1)
show["q"] = P["q_bh"].map(lambda v: f"{v:.3g}"); show["same_sign"] = P["same_sign"].values; show["shap_in_CI"] = P["shap_in_ci"].values; show["|shap|/|dml|"] = P["ratio_shap_dml"].round(2).values
print("=== AUDIT, pooled (percentage points of killed-or-hospitalised probability) ==="); print(show.to_string(index=False))
def summ(X, name):
    sig = X[X["dml_sig"]]
    kt = kendalltau(X["shap_contrast_prob"].abs(), X["dml"].abs()).statistic
    return dict(set=name, n_factors=len(X), same_sign_all=round(X["same_sign"].mean(), 2), n_significant=len(sig),
                same_sign_sig=round(sig["same_sign"].mean(), 2) if len(sig) else np.nan, shap_inside_dml_ci=round(X["shap_in_ci"].mean(), 2),
                whatif_inside_dml_ci=round(X["whatif_in_ci"].mean(), 2), median_ratio=round(X["ratio_shap_dml"].median(), 2),
                share_shap_smaller=round((X["ratio_shap_dml"] < 1).mean(), 2), kendall_tau_rank=round(kt, 2))
sm = pd.DataFrame([summ(P, "pooled")] + [summ(T[T["group"] == g], g) for g in ("bicycle", "ebike", "escooter")] + [summ(T, "all estimates")])
sm.to_csv(os.path.join(res, "audit_summary.csv"), index=False)
print("\n=== AGREEMENT SUMMARY ==="); print(sm.to_string(index=False))
# why they disagree: pre-specified vs all-controls double ML, and all-controls double ML vs the model what-if
P["gap_total"] = P["shap_contrast_prob"] - P["dml"]; P["gap_bad_controls"] = P["dml_allc"] - P["dml"]; P["gap_model"] = P["shap_contrast_prob"] - P["dml_allc"]
g = P[["label", "gap_total", "gap_bad_controls", "gap_model"]].copy()
for c in g.columns[1:]: g[c] = (g[c] * 100).round(1)
print("\n=== WHERE THE GAP COMES FROM (pooled; points). total = SHAP - DML; bad_controls = DML(all controls) - DML; model = SHAP - DML(all controls) ===")
print(g.to_string(index=False))
by = T[T["group"] != "all"].pivot(index="factor", columns="group", values="dml").mul(100).round(1)
byq = T[T["group"] != "all"].pivot(index="factor", columns="group", values="q_bh")
print("\n=== DOUBLE ML BY MODE (points; * = FDR < 0.05) ===")
print((by.astype(str) + byq.map(lambda v: "*" if v < 0.05 else "")).rename(index=LAB).to_string())
