"""Q6: robustness checks R1-R11 (plan section 10) for the pooled factors.
Usage: python -I 15_robustness.py <interim_dir> <results_dir> <audit_dir>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from lightgbm import LGBMRegressor
import doubleml as dml
from p1_dml import *
interim, res_dir, audit_dir = sys.argv[1:4]
A0 = pd.read_parquet(os.path.join(interim, "analysis_riders.parquet")); spec = json.load(open(os.path.join(interim, "feature_spec.json"))); CAT = spec["categorical"]
FACTORS = ["A1", "A2", "B1", "B2", "B3", "B4", "B5", "C1", "C2", "C3", "D1", "D2"]     # B6 excluded: overlap failure in the main run
MAIN = A0[A0["year"] >= 2020].reset_index(drop=True)
early = pd.read_csv(os.path.join(audit_dir, "edp_by_dep_year.csv"), dtype={"dep": str}).set_index("dep")["2020"]; early = set(early[early >= 10].index)
LOC = ["catr", "circ", "nbv", "vosp", "prof", "plan", "infra", "vma", "surf"]

def rf_learners(xcols):
    mk = lambda s: Pipeline([("imp", SimpleImputer(strategy="median")), ("rf", RandomForestClassifier(n_estimators=200, min_samples_leaf=20, max_features=0.4, n_jobs=1, random_state=s))])
    return mk(SEED), mk(SEED + 1)
def logit_learners(xcols):
    ci = [i for i, c in enumerate(xcols) if c in CAT]; ni = [i for i, c in enumerate(xcols) if c not in CAT]
    def mk():
        pre = ColumnTransformer([("c", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=20), ci),
                                 ("n", Pipeline([("imp", SimpleImputer(strategy="median", add_indicator=True)), ("sc", StandardScaler())]), ni)])
        return Pipeline([("pre", pre), ("lr", LogisticRegression(C=0.3, max_iter=1500))])
    return mk(), mk()

def plr(E, f, xcols):
    d = E[E[f"T_{f}"].notna()].reset_index(drop=True); xcols = [c for c in xcols if d[c].nunique(dropna=False) > 1]
    data = dml.DoubleMLData(d[["ksi", f"T_{f}"] + xcols].astype({f"T_{f}": int}), y_col="ksi", d_cols=f"T_{f}", x_cols=xcols, force_all_x_finite="allow-nan")
    obj = dml.DoubleMLPLR(data, ml_l=learner(xcols, CAT, SEED, cls=LGBMRegressor), ml_m=learner(xcols, CAT, SEED + 1), n_folds=5, n_rep=5, draw_sample_splitting=False)
    obj.set_sample_splitting(grouped_splits(d["Num_Acc"].values)); obj.fit()
    th = obj.all_coef[0, :]; psi = obj.psi[:, :, 0]; J = obj.psi_elements["psi_a"][:, :, 0].mean(axis=0); n = len(d)
    codes = pd.factorize(d["dep"].values)[0]; G = codes.max() + 1
    v = np.array([(np.bincount(codes, weights=psi[:, k], minlength=G) ** 2).sum() / (n ** 2 * J[k] ** 2) * G / (G - 1) for k in range(len(th))])
    theta = np.median(th); se = np.sqrt(np.median(v + (th - theta) ** 2))
    return dict(n=n, theta=theta, se=se, lo=theta - 1.96 * se, hi=theta + 1.96 * se, p=2 * norm.sf(abs(theta / se)))

def run(check, f):
    base = dict(check=check, factor=f)
    try:
        A = MAIN; x = adjustment(f); kw = {}
        if check == "R1 include 2019": A = A0
        elif check == "R2 exclude Paris police area": A = MAIN[MAIN["paris_police_area"] == 0]
        elif check == "R3 fatal outcome": kw["ycol"] = "killed"
        elif check == "R4 motor-vehicle collisions only":
            if f == "C2": return dict(base, status="not applicable")
            A = MAIN[MAIN["opponent"].isin(["car", "van", "heavy", "ptw"])]
        elif check == "R5 e-scooters: early-adopter departements": A = MAIN[(MAIN["mode"] != "escooter") | MAIN["dep"].isin(early)]
        elif check == "R6a any-row location variables":
            A = MAIN.copy(); A["vma"] = A["vma"].fillna(A["vma_max_anyrow"]); A.loc[A["vosp"].isna() & (A["vosp_cycle_anyrow"] == 1), "vosp"] = "1"
        elif check == "R6b drop location-file variables": x = [c for c in x if c not in LOC]
        elif check == "R7a random forest nuisances": kw["learners"] = rf_learners
        elif check == "R7b logistic nuisances": kw["learners"] = logit_learners
        elif check == "R8a trim 0.01": kw["trim"] = 0.01
        elif check == "R8b trim 0.05": kw["trim"] = 0.05
        A = A.reset_index(drop=True); E = encode(A, CAT); t = E[f"T_{f}"]; y = E[kw.get("ycol", "ksi")]
        if not all(((t == a).sum() >= 200) and (y[t == a].sum() >= 30) for a in (0, 1)): return dict(base, status="not estimated: small arm")
        if check == "R9 partially linear model": return dict(base, status="ok", **plr(E, f, x))
        if check == "R11 benchmark: departement":
            r, obj, d = fit_irm(E, f, x, CAT)
            b = obj.sensitivity_benchmark(benchmarking_set=["dep"])
            return dict(base, status="ok", n=r["n"], theta=r["theta"], se=r["se"], lo=r["lo"], hi=r["hi"], p=r["p"], rv=r.get("rv"), rva=r.get("rva"),
                        bench_cf_y=float(b["cf_y"].iloc[0]), bench_cf_d=float(b["cf_d"].iloc[0]), bench_delta_theta=float(b["delta_theta"].iloc[0]))
        r, _, _ = fit_irm(E, f, x, CAT, sens=False, **kw)
        return dict(base, status="ok", **{k: r[k] for k in ("n", "n_treated", "theta", "se", "lo", "hi", "p", "ps_outside")})
    except Exception as e:
        return dict(base, status="error: " + str(e)[:160])
CHECKS = ["R1 include 2019", "R2 exclude Paris police area", "R3 fatal outcome", "R4 motor-vehicle collisions only", "R5 e-scooters: early-adopter departements",
          "R6a any-row location variables", "R6b drop location-file variables", "R7a random forest nuisances", "R7b logistic nuisances",
          "R8a trim 0.01", "R8b trim 0.05", "R9 partially linear model", "R11 benchmark: departement"]
res = Parallel(n_jobs=9)(delayed(run)(c, f) for c in CHECKS for f in FACTORS)
R = pd.DataFrame(res); R.to_csv(os.path.join(res_dir, "robustness.csv"), index=False)
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 300)
main = pd.read_csv(os.path.join(res_dir, "dml_main.csv")); main = main[(main["variant"] == "main") & (main["group"] == "all")].set_index("factor")
ok = R[R["status"] == "ok"]
W = ok.pivot(index="check", columns="factor", values="theta").mul(100).round(1).reindex(CHECKS)
W.loc["MAIN"] = (main.loc[FACTORS, "theta"] * 100).round(1); W = W.loc[["MAIN"] + CHECKS]
print("=== ESTIMATES (percentage points) ==="); print(W.to_string())
sig = ok.assign(s=np.where(ok["p"] < 0.05, np.where(ok["theta"] > 0, "+", "-"), "0")).pivot(index="check", columns="factor", values="s").reindex(CHECKS)
print("\n=== SIGN AND SIGNIFICANCE at 5% (+ / - / 0 = not significant) ==="); print(sig.to_string())
b = ok[ok["check"] == "R11 benchmark: departement"][["factor", "theta", "rv", "rva", "bench_cf_y", "bench_cf_d", "bench_delta_theta"]]
print("\n=== R11: robustness value vs a confounder as strong as departement ==="); print(b.round(4).to_string(index=False))
print("\nnot ok:"); print(R[R["status"] != "ok"][["check", "factor", "status"]].to_string(index=False))
