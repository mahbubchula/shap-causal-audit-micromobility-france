"""Diagnose and correct robustness check R5 for factor A1 (e-scooter vs bicycle).
The first implementation restricted only e-scooter riders to early-adopter departements and kept cyclists everywhere,
which removes overlap outside those departements. The corrected version restricts BOTH arms.
Usage: python -I 15b_robustness_r5_check.py <interim_dir> <results_dir> <audit_dir>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from p1_dml import *
interim, res_dir, audit_dir = sys.argv[1:4]
A = pd.read_parquet(os.path.join(interim, "analysis_riders.parquet")); spec = json.load(open(os.path.join(interim, "feature_spec.json"))); CAT = spec["categorical"]
A = A[A["year"] >= 2020].reset_index(drop=True)
early = pd.read_csv(os.path.join(audit_dir, "edp_by_dep_year.csv"), dtype={"dep": str}).set_index("dep")["2020"]; early = sorted(early[early >= 10].index)
print("early-adopter departements:", early)
R = pd.read_csv(os.path.join(res_dir, "robustness.csv"))
print("first implementation, A1:", R[(R["check"].str.startswith("R5")) & (R["factor"] == "A1")][["n", "n_treated", "theta", "lo", "hi", "ps_outside"]].round(4).to_dict("records"))
rows = []
for name, D in (("R5 corrected: both modes, early-adopter departements", A[A["dep"].isin(early)]),
                ("R5 complement: both modes, all other departements", A[~A["dep"].isin(early)])):
    D = D.reset_index(drop=True); E = encode(D, CAT)
    r, _, d = fit_irm(E, "A1", adjustment("A1"), CAT, sens=False)
    raw = d.loc[d["T_A1"] == 1, "ksi"].mean() - d.loc[d["T_A1"] == 0, "ksi"].mean()
    rows.append(dict(check=name, factor="A1", status="ok", raw_diff=raw, **{k: r[k] for k in ("n", "n_treated", "theta", "se", "lo", "hi", "p", "ps_outside")}))
    print(name, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in rows[-1].items() if k not in ("check", "factor", "status")})
pd.DataFrame(rows).to_csv(os.path.join(res_dir, "robustness_r5_corrected.csv"), index=False)
