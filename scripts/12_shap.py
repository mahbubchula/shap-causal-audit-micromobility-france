"""Q2 and the SHAP side of Q4: global importance (locked test), stability (5 folds x 5 seeds),
out-of-fold SHAP contrasts and model what-ifs for every pre-specified factor.
Usage: python -I 12_shap.py <interim_dir> <results_dir> <models_dir>"""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, joblib
from scipy.stats import kendalltau
from scipy.special import expit
from sklearn.model_selection import GroupKFold
from sklearn.base import clone
from joblib import Parallel, delayed
from p1_common import *
interim, res_dir, mod_dir = sys.argv[1:4]
A, spec = load(interim); A = A[A["year"] >= 2020].reset_index(drop=True)
FEATS = sum(spec["tiers"].values(), []); best = json.load(open(os.path.join(res_dir, "best_params.json")))["lgbm"]
pipe0, ORDER = lgbm_pipe(FEATS, spec, best)

def contrib(pipe, X):
    Z = pipe.named_steps["pre"].transform(X[FEATS])
    c = pipe.named_steps["model"].booster_.predict(Z, pred_contrib=True)
    return pd.DataFrame(c[:, :-1], columns=ORDER, index=X.index), c.sum(axis=1)

# ---- 1. global importance on the locked test set (final model, fitted on development only) ----
final = joblib.load(os.path.join(mod_dir, "lgbm_final.joblib")); test = A[A["split"] == "test"]
S, _ = contrib(final, test)
imp = S.abs().mean().sort_values(ascending=False).rename("mean_abs_shap_logodds").to_frame()
tier_of = {f: t for t, fs in spec["tiers"].items() for f in fs}; imp["tier"] = imp.index.map(tier_of)
for m in ("bicycle", "ebike", "escooter"): imp[m] = S[test["mode"] == m].abs().mean()
imp["rank"] = np.arange(1, len(imp) + 1); imp.to_csv(os.path.join(res_dir, "shap_importance_test.csv"))
pd.set_option("display.width", 220)
print("=== GLOBAL SHAP IMPORTANCE, locked test (mean |SHAP|, log-odds) ==="); print(imp.round(3).to_string())

# ---- 2. stability and out-of-fold SHAP: 5 seeds x 5 grouped folds ----
WHATIF = {"A1": ({"mode": "escooter"}, {"mode": "bicycle"}), "A2": ({"mode": "ebike"}, {"mode": "bicycle"}),
          "B1": ({"vma": 30.0}, {"vma": 50.0}), "B2": ({"lum": "3"}, {"lum": "5"}),
          "B3": ({"atm": "2", "surf": "2"}, {"atm": "1", "surf": "1"}), "B4": ({"vosp": "1"}, {"vosp": "0"}),
          "B5": ({"int_type": "2"}, {"int_type": "1"}), "B6": ({"urban": 1}, {"urban": 0}),
          "C1": ({"opponent": "heavy"}, {"opponent": "car"}),
          "C2": ({"opponent": "single", "n_vehicles": 1.0, "col": "7"}, {"opponent": "car", "n_vehicles": 2.0, "col": "3"}),
          "C3": ({"situ": "5"}, {"situ": "1"}), "D1": ({"age": 72.0}, {"age": 44.0}), "D2": ({"sex": "male"}, {"sex": "female"}),
          "R10": ({}, {})}
def one_seed(seed):
    gkf = GroupKFold(5, shuffle=True, random_state=SEED + seed)
    Soof = pd.DataFrame(0.0, index=A.index, columns=ORDER); eta = np.zeros(len(A)); imps = []; wi = {}
    for k, (tr, te) in enumerate(gkf.split(A, A["ksi"], A["Num_Acc"])):
        p = clone(pipe0); p.set_params(model__random_state=SEED + 100 * seed + k).fit(A.iloc[tr][FEATS], A.iloc[tr]["ksi"])
        s, e = contrib(p, A.iloc[te]); Soof.iloc[te] = s.values; eta[te] = e; imps.append(s.abs().mean())
        if seed == 0:
            for f, (hi, lo) in WHATIF.items():
                if not hi: continue
                Xh, Xl = A.iloc[te][FEATS].copy(), A.iloc[te][FEATS].copy()
                for c, v in hi.items(): Xh[c] = v
                for c, v in lo.items(): Xl[c] = v
                wi.setdefault(f, np.zeros(len(A)))[te] = p.predict_proba(Xh)[:, 1] - p.predict_proba(Xl)[:, 1]
    return seed, Soof, eta, imps, wi
runs = Parallel(n_jobs=5)(delayed(one_seed)(s) for s in range(5))
all_imps = pd.DataFrame([i for r in runs for i in r[3]])                     # 25 x n_features
ranks = all_imps.rank(axis=1, ascending=False)
taus = [kendalltau(all_imps.iloc[i], all_imps.iloc[j]).statistic for i, j in itertools.combinations(range(len(all_imps)), 2)]
top10 = [set(r.nsmallest(10).index) for _, r in ranks.iterrows()]
jac = [len(a & b) / len(a | b) for a, b in itertools.combinations(top10, 2)]
stab = pd.DataFrame({"mean_abs_shap": all_imps.mean(), "rank_median": ranks.median(), "rank_min": ranks.min(), "rank_max": ranks.max()}).sort_values("rank_median")
stab.to_csv(os.path.join(res_dir, "shap_stability.csv"))
print(f"\n=== STABILITY over 25 models: Kendall tau mean {np.mean(taus):.3f} (min {np.min(taus):.3f}); top-10 Jaccard mean {np.mean(jac):.3f} (min {np.min(jac):.3f}) ===")
print(stab.head(15).round(3).to_string())
json.dump({"kendall_tau_mean": float(np.mean(taus)), "kendall_tau_min": float(np.min(taus)), "top10_jaccard_mean": float(np.mean(jac)), "top10_jaccard_min": float(np.min(jac))},
          open(os.path.join(res_dir, "shap_stability_summary.json"), "w"), indent=1)

# ---- 3. SHAP contrast and model what-if for each factor (seed 0, out-of-fold) ----
_, Soof, eta, _, wi = runs[0]
Soof.assign(eta=eta).to_parquet(os.path.join(res_dir, "oof_shap.parquet"))
FACTOR_FEATS = {"A1": ["mode"], "A2": ["mode"], "B1": ["vma"], "B2": ["lum"], "B3": ["atm", "surf"], "B4": ["vosp"], "B5": ["int_type"], "B6": ["urban"],
                "C1": ["opponent"], "C2": ["opponent", "n_vehicles", "col"], "C3": ["situ"], "D1": ["age"], "D2": ["sex"], "R10": []}
def shap_contrast(phi, e, t):
    """ATE-like contrast on the probability scale: swap each rider's attribution for the other arm's mean attribution."""
    m1, m0 = phi[t == 1].mean(), phi[t == 0].mean()
    d = np.where(t == 1, expit(e) - expit(e - phi + m0), expit(e - phi + m1) - expit(e))
    return d.mean(), m1 - m0
rows = []; rng = np.random.default_rng(SEED)
for f, feats in FACTOR_FEATS.items():
    if not feats: continue
    for grp in ("all", "bicycle", "ebike", "escooter"):
        if f in ("A1", "A2") and grp != "all": continue
        m = A[f"T_{f}"].notna().values & ((A["mode"] == grp).values if grp != "all" else True)
        t = A.loc[m, f"T_{f}"].values; phi = Soof.loc[m, feats].sum(axis=1).values; e = eta[m]; w = wi[f][m]; g = A.loc[m, "Num_Acc"].values
        if (t == 1).sum() < 200 or (t == 0).sum() < 200: continue
        sc, slo = shap_contrast(phi, e, t)
        idx_by = pd.Series(np.arange(len(t))).groupby(g).apply(lambda s: s.values).values
        bs, bw = [], []
        for _ in range(300):
            take = np.concatenate(idx_by[rng.integers(0, len(idx_by), len(idx_by))])
            bs.append(shap_contrast(phi[take], e[take], t[take])[0]); bw.append(w[take].mean())
        rows.append(dict(factor=f, group=grp, n=int(m.sum()), shap_contrast_logodds=slo, shap_contrast_prob=sc, shap_lo=np.quantile(bs, .025), shap_hi=np.quantile(bs, .975),
                         whatif_prob=w.mean(), whatif_lo=np.quantile(bw, .025), whatif_hi=np.quantile(bw, .975),
                         raw_diff=A.loc[m, "ksi"][t == 1].mean() - A.loc[m, "ksi"][t == 0].mean()))
out = pd.DataFrame(rows); out.to_csv(os.path.join(res_dir, "audit_shap_side.csv"), index=False)
print("\n=== SHAP CONTRAST and MODEL WHAT-IF by factor (pooled; percentage points) ===")
o = out[out["group"] == "all"].copy()
for c in ("shap_contrast_prob", "shap_lo", "shap_hi", "whatif_prob", "raw_diff"): o[c] = (o[c] * 100).round(2)
print(o[["factor", "n", "raw_diff", "shap_contrast_prob", "shap_lo", "shap_hi", "whatif_prob"]].to_string(index=False))
