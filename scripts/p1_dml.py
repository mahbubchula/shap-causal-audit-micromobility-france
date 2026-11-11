"""Double ML helpers for Paper 1: adjustment sets, grouped cross-fitting, departement-clustered inference."""
import numpy as np, pandas as pd, warnings
from scipy.stats import norm
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
from lightgbm import LGBMClassifier
import doubleml as dml
warnings.filterwarnings("ignore")
SEED = 20261111
T0 = ["year", "month", "dow", "hour", "dep", "urban"]; T1 = ["mode", "age", "sex", "trip", "n_passengers"]
T2 = ["catr", "circ", "nbv", "vosp", "prof", "plan", "infra", "vma", "int_type", "lum", "atm", "surf"]
T3 = ["situ", "col", "opponent", "n_vehicles", "ped_struck", "obs", "obsm", "choc", "manv"]
ALL = T0 + T1 + T2 + T3
DEFINING = {"A1": ["mode"], "A2": ["mode"], "B1": ["vma"], "B2": ["lum"], "B3": ["atm", "surf"], "B4": ["vosp"], "B5": ["int_type"], "B6": ["urban"],
            "C1": ["opponent"], "C2": ["opponent", "n_vehicles", "col", "obsm"], "C3": ["situ"], "D1": ["age"], "D2": ["sex"], "R10": []}
def adjustment(f):
    """Pre-specified adjustment sets (plan section 7)."""
    if f in ("A1", "A2"): return T0 + ["age", "sex", "trip", "n_passengers"] + T2
    if f in ("B1", "B2", "B3", "B4", "B5"): return [c for c in T0 + T1 + T2 if c not in DEFINING[f]]
    if f == "B6": return ["year", "month", "dow", "hour", "dep", "age", "sex", "mode"]
    if f in ("C1", "C2", "C3", "R10"): return T0 + T1 + T2
    if f == "D1": return T0 + ["sex", "mode"]
    if f == "D2": return T0 + ["age", "mode"]
def all_controls(f): return [c for c in ALL if c not in DEFINING[f]]

def encode(A, categorical):
    """Relabel categories as integer codes (-1 = missing). A pure relabelling: uses no outcome and no cross-row statistic."""
    E = A.copy()
    for c in categorical:
        E[c] = pd.Categorical(E[c]).codes.astype("int32")
    return E

LGB = dict(n_estimators=300, learning_rate=0.05, num_leaves=24, min_child_samples=80, subsample=0.75, subsample_freq=1,
           colsample_bytree=0.6, reg_lambda=2.0, cat_smooth=30, n_jobs=1, verbose=-1)
def learner(xcols, categorical, seed, cls=LGBMClassifier, **kw):
    cat_idx = [i for i, c in enumerate(xcols) if c in categorical]
    p = dict(LGB); p.update(kw)
    return cls(categorical_feature=cat_idx, random_state=seed, **p)

def grouped_splits(groups, n_rep=5, n_folds=5, seed=SEED):
    idx = np.arange(len(groups))
    return [[(tr, te) for tr, te in GroupKFold(n_folds, shuffle=True, random_state=seed + r).split(idx, groups=groups)] for r in range(n_rep)]

def cluster_inference(obj, clusters):
    """Median aggregation over repetitions with a cluster-robust variance from the influence function (score derivative = -1 for the ATE score)."""
    th = obj.all_coef[0, :]; psi = obj.psi[:, :, 0]; n = psi.shape[0]
    codes = pd.factorize(clusters)[0]; G = codes.max() + 1
    v_cl = np.array([(np.bincount(codes, weights=psi[:, k], minlength=G) ** 2).sum() / n ** 2 * G / (G - 1) for k in range(psi.shape[1])])
    v_iid = (psi ** 2).mean(axis=0) / n
    theta = np.median(th)
    se_cl = np.sqrt(np.median(v_cl + (th - theta) ** 2)); se_iid = np.sqrt(np.median(v_iid + (th - theta) ** 2))
    return theta, se_cl, se_iid

def fit_irm(E, f, xcols, categorical, tcol=None, ycol="ksi", trim=0.02, n_rep=5, sens=True, learners=None, seed=SEED):
    tcol = tcol or f"T_{f}"
    d = E[E[tcol].notna()].reset_index(drop=True)
    xcols = [c for c in xcols if d[c].nunique(dropna=False) > 1]
    data = dml.DoubleMLData(d[[ycol, tcol] + xcols].astype({tcol: int}), y_col=ycol, d_cols=tcol, x_cols=xcols, force_all_x_finite="allow-nan")
    ml_g, ml_m = learners(xcols) if learners else (learner(xcols, categorical, seed), learner(xcols, categorical, seed + 1))
    obj = dml.DoubleMLIRM(data, ml_g=ml_g, ml_m=ml_m, n_folds=5, n_rep=n_rep, score="ATE", trimming_threshold=trim, draw_sample_splitting=False)
    obj.set_sample_splitting(grouped_splits(d["Num_Acc"].values, n_rep=n_rep, seed=seed))
    obj.fit(store_predictions=True)
    theta, se_cl, se_iid = cluster_inference(obj, d["dep"].values)
    m_hat = obj.predictions["ml_m"][:, :, 0].mean(axis=1); t = d[tcol].values
    r = dict(n=len(d), n_treated=int(t.sum()), n_ref=int((1 - t).sum()), theta=theta, se=se_cl, se_iid=se_iid, se_package=float(obj.se[0]),
             lo=theta - 1.96 * se_cl, hi=theta + 1.96 * se_cl, p=2 * norm.sf(abs(theta / se_cl)),
             ps_auc=roc_auc_score(t, m_hat), ps_outside=float(((m_hat < trim) | (m_hat > 1 - trim)).mean()), n_x=len(xcols))
    if sens:
        try:
            obj.sensitivity_analysis(cf_y=0.03, cf_d=0.03, rho=1.0, level=0.95)
            sp = obj.sensitivity_params
            r.update(rv=float(sp["rv"][0]), rva=float(sp["rva"][0]), theta_lo_sens=float(sp["theta"]["lower"][0]), theta_hi_sens=float(sp["theta"]["upper"][0]))
        except Exception as e:
            r.update(sens_error=str(e)[:80])
    return r, obj, d
