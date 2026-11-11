"""Q1: predictive models with leakage-safe tuning, and the leakage comparison (plan sections 5-6).
Usage: python -I 11_predictive_models.py <interim_dir> <results_dir> <models_dir>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, joblib
from scipy.stats import loguniform, randint, uniform
from sklearn.model_selection import GroupKFold, KFold, RandomizedSearchCV, GridSearchCV
from sklearn.base import clone
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from p1_common import *
interim, res_dir, mod_dir = sys.argv[1:4]
A, spec = load(interim)
A = A[A["year"] >= 2020].reset_index(drop=True)
FEATS = sum(spec["tiers"].values(), [])
dev, test = A[A["split"] == "development"].reset_index(drop=True), A[A["split"] == "test"].reset_index(drop=True)
assert dev["date"].max() < test["date"].min() and not set(dev["Num_Acc"]) & set(test["Num_Acc"])
print(f"development n={len(dev)} ({dev['date'].min().date()}..{dev['date'].max().date()}), test n={len(test)} ({test['date'].min().date()}..{test['date'].max().date()})")

# ---------- 1. tuning inside development, grouped by crash ----------
gkf = GroupKFold(n_splits=5)
pipe, order = lgbm_pipe(FEATS, spec)
space = {"model__num_leaves": randint(8, 64), "model__learning_rate": loguniform(0.02, 0.12), "model__n_estimators": randint(150, 900),
         "model__min_child_samples": randint(20, 200), "model__subsample": uniform(0.6, 0.4), "model__colsample_bytree": uniform(0.5, 0.5),
         "model__reg_lambda": loguniform(0.1, 30), "model__cat_smooth": loguniform(5, 100)}
rs = RandomizedSearchCV(pipe, space, n_iter=30, scoring="neg_log_loss", cv=gkf, n_jobs=8, random_state=SEED, refit=True)
rs.fit(dev[FEATS], dev["ksi"], groups=dev["Num_Acc"])
best = {k.replace("model__", ""): (v.item() if hasattr(v, "item") else v) for k, v in rs.best_params_.items()}
print("LightGBM best grouped-CV log loss:", round(-rs.best_score_, 4), "| params:", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in best.items()})
gs = GridSearchCV(logit_pipe(FEATS, spec), {"model__C": [0.003, 0.01, 0.03, 0.1, 0.3, 1, 3, 10]}, scoring="neg_log_loss", cv=gkf, n_jobs=8)
gs.fit(dev[FEATS], dev["ksi"], groups=dev["Num_Acc"])
print("Logistic best grouped-CV log loss:", round(-gs.best_score_, 4), "| C:", gs.best_params_["model__C"])
json.dump({"lgbm": best, "logit_C": gs.best_params_["model__C"]}, open(os.path.join(res_dir, "best_params.json"), "w"), indent=1)

# ---------- 2. locked test (protocol d): fit on development, predict 2024-2025 once ----------
final = rs.best_estimator_; p_test = final.predict_proba(test[FEATS])[:, 1]
p_test_lr = gs.best_estimator_.predict_proba(test[FEATS])[:, 1]
joblib.dump(final, os.path.join(mod_dir, "lgbm_final.joblib")); joblib.dump(gs.best_estimator_, os.path.join(mod_dir, "logit_final.joblib"))
test.assign(p_lgbm=p_test, p_logit=p_test_lr)[["Num_Acc", "id_vehicule", "mode", "ksi", "p_lgbm", "p_logit"]].to_parquet(os.path.join(res_dir, "test_predictions.parquet"), index=False)
rows = []
for name, pp in (("LightGBM", p_test), ("Logistic", p_test_lr)):
    for grp, m in [("all", np.ones(len(test), bool))] + [(k, (test["mode"] == k).values) for k in ("bicycle", "ebike", "escooter")]:
        r = metrics(test["ksi"][m], pp[m]); r.update(model=name, group=grp)
        for met, fn in (("roc_auc", roc_auc_score), ("pr_auc", average_precision_score), ("brier", brier_score_loss)):
            lo, hi = boot_ci(test["ksi"][m], pp[m], test["Num_Acc"][m], fn, B=500); r[met + "_lo"], r[met + "_hi"] = lo, hi
        rows.append(r)
tm = pd.DataFrame(rows); tm.to_csv(os.path.join(res_dir, "test_metrics.csv"), index=False)
pd.set_option("display.width", 250)
print("\n=== LOCKED TEST 2024-2025 (95% CI by crash bootstrap) ===")
show = tm.assign(ROC=lambda d: d.apply(lambda r: f"{r.roc_auc:.3f} [{r.roc_auc_lo:.3f}, {r.roc_auc_hi:.3f}]", axis=1),
                 PR=lambda d: d.apply(lambda r: f"{r.pr_auc:.3f} [{r.pr_auc_lo:.3f}, {r.pr_auc_hi:.3f}]", axis=1),
                 Brier=lambda d: d.apply(lambda r: f"{r.brier:.4f} [{r.brier_lo:.4f}, {r.brier_hi:.4f}]", axis=1))
print(show[["model", "group", "n", "prevalence", "ROC", "PR", "Brier", "cal_slope", "cal_intercept"]].round(3).to_string(index=False))

# ---------- 3. leakage comparison, same hyperparameters throughout ----------
def oof(X, y, splitter, groups, feats, extra_cat=(), global_pre=False):
    p = np.zeros(len(y)); pipe, _ = lgbm_pipe(feats, spec, best, extra_cat)
    if global_pre:                                          # preprocessing fitted on ALL rows before splitting
        pre = clone(pipe.named_steps["pre"]).fit(X[feats]); Z = pre.transform(X[feats])
        for tr, te in splitter.split(Z, y, groups):
            m = clone(pipe.named_steps["model"]).fit(Z[tr], y.iloc[tr]); p[te] = m.predict_proba(Z[te])[:, 1]
    else:
        for tr, te in splitter.split(X, y, groups):
            m = clone(pipe).fit(X.iloc[tr][feats], y.iloc[tr]); p[te] = m.predict_proba(X.iloc[te][feats])[:, 1]
    return p
LEAK = FEATS + ["LEAK_equip", "LEAK_ped_worst_grav"]; XC = ("LEAK_equip", "LEAK_ped_worst_grav")
kf = KFold(5, shuffle=True, random_state=SEED)
prot = []
def add(label, y, p, note): r = metrics(y, p); r.update(protocol=label, note=note); prot.append(r)
add("(a) random rows, all years, global preprocessing", A["ksi"], oof(A, A["ksi"], kf, None, FEATS, global_pre=True), "common practice")
add("(b) = (a) + outcome-dependent variables", A["ksi"], oof(A, A["ksi"], kf, None, LEAK, XC, global_pre=True), "equipment status, worst pedestrian injury")
# addition to the plan: oversampling the minority class BEFORE splitting (logged as a deviation)
rng = np.random.default_rng(SEED); pos = np.flatnonzero(A["ksi"].values == 1); neg = np.flatnonzero(A["ksi"].values == 0)
os_idx = np.concatenate([neg, rng.choice(pos, len(neg), replace=True)]); O = A.iloc[os_idx].reset_index(drop=True)
add("(a+) oversample to 50:50 BEFORE splitting, random rows", O["ksi"], oof(O, O["ksi"], kf, None, FEATS, global_pre=True), "addition to plan; prevalence changed, so compare ROC only")
add("(c) grouped by crash, all years, in-fold preprocessing", A["ksi"], oof(A, A["ksi"], GroupKFold(5), A["Num_Acc"], FEATS), "isolates grouping")
add("(c-dev) grouped by crash, development only", dev["ksi"], oof(dev, dev["ksi"], GroupKFold(5), dev["Num_Acc"], FEATS), "plan protocol (c)")
add("(d) forward in time: train 2020-23, test 2024-25", test["ksi"], p_test, "locked test")
for y_ in (2021, 2022, 2023):
    tr, va = dev[dev["year"] < y_], dev[dev["year"] == y_]
    m = clone(lgbm_pipe(FEATS, spec, best)[0]).fit(tr[FEATS], tr["ksi"])
    add(f"forward chain: train <{y_}, validate {y_}", va["ksi"], m.predict_proba(va[FEATS])[:, 1], "temporal check")
pr = pd.DataFrame(prot); pr.to_csv(os.path.join(res_dir, "leakage_protocols.csv"), index=False)
print("\n=== LEAKAGE COMPARISON (LightGBM, identical hyperparameters) ===")
print(pr[["protocol", "n", "prevalence", "roc_auc", "pr_auc", "brier", "log_loss", "cal_slope"]].round(4).to_string(index=False))
