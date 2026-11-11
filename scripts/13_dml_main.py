"""Q3: double ML estimates for the pre-specified factors (plan section 7), pooled and by mode,
plus the 'all controls' variant used in the audit.
Usage: python -I 13_dml_main.py <interim_dir> <results_dir>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from p1_dml import *
interim, res_dir = sys.argv[1:3]
A = pd.read_parquet(os.path.join(interim, "analysis_riders.parquet")); spec = json.load(open(os.path.join(interim, "feature_spec.json")))
A = A[A["year"] >= 2020].reset_index(drop=True); E = encode(A, spec["categorical"]); CAT = spec["categorical"]
FACTORS = ["A1", "A2", "B1", "B2", "B3", "B4", "B5", "B6", "C1", "C2", "C3", "D1", "D2"]
tasks = [(f, "all", "main") for f in FACTORS] + [(f, "all", "all_controls") for f in FACTORS] + [("R10", "all", "main")]
tasks += [(f, m, "main") for f in FACTORS[2:] for m in ("bicycle", "ebike", "escooter")]
def run(f, grp, variant):
    D = E if grp == "all" else E[A["mode"].values == grp]
    t = D[f"T_{f}"]; y = D["ksi"]
    base = dict(factor=f, group=grp, variant=variant)
    ok = all(((t == a).sum() >= 200) and (y[t == a].sum() >= 30) for a in (0, 1))
    if not ok: return dict(base, status="not estimated: arm below 200 riders or 30 severe outcomes")
    x = adjustment(f) if variant == "main" else all_controls(f)
    if grp != "all": x = [c for c in x if c != "mode"]
    try:
        r, _, _ = fit_irm(D, f, x, CAT)
        return dict(base, status="ok", **r)
    except Exception as e:
        return dict(base, status="error: " + str(e)[:150])
res = Parallel(n_jobs=9, verbose=0)(delayed(run)(*t) for t in tasks)
R = pd.DataFrame(res)
# Benjamini-Hochberg across the main family (placebo excluded)
fam = (R["variant"] == "main") & (R["factor"] != "R10") & (R["status"] == "ok")
p = R.loc[fam, "p"].values; o = np.argsort(p); q = np.empty(len(p)); q[o] = np.minimum.accumulate((p[o] * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1]
R.loc[fam, "q_bh"] = np.minimum(q, 1); R.to_csv(os.path.join(res_dir, "dml_main.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
S = R[R["status"] == "ok"].copy()
for c in ("theta", "se", "se_iid", "lo", "hi"): S[c] = (S[c] * 100).round(2)
print("=== POOLED, pre-specified adjustment (percentage points; SE clustered by departement) ===")
print(S[(S["group"] == "all") & (S["variant"] == "main")][["factor", "n", "n_treated", "theta", "se", "se_iid", "lo", "hi", "p", "q_bh", "ps_auc", "ps_outside", "rv", "rva"]].round(4).to_string(index=False))
print("\n=== POOLED, all controls (audit variant) ===")
print(S[(S["group"] == "all") & (S["variant"] == "all_controls")][["factor", "n", "theta", "se", "lo", "hi", "ps_auc", "ps_outside"]].round(4).to_string(index=False))
print("\n=== BY MODE, pre-specified adjustment ===")
print(S[S["group"] != "all"][["factor", "group", "n", "n_treated", "theta", "se", "lo", "hi", "p", "q_bh", "ps_outside"]].round(4).to_string(index=False))
print("\nnot estimated / errors:"); print(R[R["status"] != "ok"][["factor", "group", "variant", "status"]].to_string(index=False))
print("check: package SE vs my iid SE (pooled main), ratio:", (R.loc[fam & (R["group"] == "all"), "se_package"] / R.loc[fam & (R["group"] == "all"), "se_iid"]).round(3).tolist())
