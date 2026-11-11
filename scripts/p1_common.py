"""Shared helpers for Paper 1: data loading, leakage-safe pipelines, metrics."""
import json, os, warnings
import numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss
from lightgbm import LGBMClassifier
warnings.filterwarnings("ignore")
SEED = 20261111

def load(interim):
    A = pd.read_parquet(os.path.join(interim, "analysis_riders.parquet"))
    spec = json.load(open(os.path.join(interim, "feature_spec.json")))
    for c in spec["categorical"] + ["LEAK_equip", "LEAK_ped_worst_grav"]:
        A[c] = A[c].astype("object").where(A[c].notna(), None)
    return A, spec

def split_cols(features, spec, extra_cat=()):
    cat = [f for f in features if f in spec["categorical"] or f in extra_cat]
    return cat, [f for f in features if f not in cat]

def lgbm_pipe(features, spec, params=None, extra_cat=()):
    cat, num = split_cols(features, spec, extra_cat)
    pre = ColumnTransformer([("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, encoded_missing_value=-1, dtype=np.int32), cat),
                             ("num", "passthrough", num)], verbose_feature_names_out=False)
    p = dict(objective="binary", n_estimators=400, learning_rate=0.05, num_leaves=31, min_child_samples=50, subsample=0.8, subsample_freq=1,
             colsample_bytree=0.8, reg_lambda=1.0, cat_smooth=10, n_jobs=1, random_state=SEED, verbose=-1)
    p.update(params or {})
    return Pipeline([("pre", pre), ("model", LGBMClassifier(categorical_feature=list(range(len(cat))), **p))]), cat + num

def logit_pipe(features, spec, C=1.0, extra_cat=()):
    cat, num = split_cols(features, spec, extra_cat)
    pre = ColumnTransformer([("cat", Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="missing")),
                                               ("oh", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=20))]), cat),
                             ("num", Pipeline([("imp", SimpleImputer(strategy="median", add_indicator=True)), ("sc", StandardScaler())]), num)])
    return Pipeline([("pre", pre), ("model", LogisticRegression(C=C, max_iter=2000))])

def metrics(y, p):
    y = np.asarray(y); p = np.clip(np.asarray(p), 1e-6, 1 - 1e-6)
    lp = np.log(p / (1 - p))
    cal = LogisticRegression(C=1e6, max_iter=1000).fit(lp.reshape(-1, 1), y)
    return dict(n=len(y), prevalence=y.mean(), roc_auc=roc_auc_score(y, p), pr_auc=average_precision_score(y, p), brier=brier_score_loss(y, p),
                log_loss=log_loss(y, p), cal_slope=cal.coef_[0, 0], cal_intercept=cal.intercept_[0])

def boot_ci(y, p, groups, fn, B=1000, seed=SEED):
    """Bootstrap by crash (cluster bootstrap)."""
    rng = np.random.default_rng(seed); y = np.asarray(y); p = np.asarray(p)
    idx_by = pd.Series(np.arange(len(y))).groupby(np.asarray(groups)).apply(lambda s: s.values)
    arrs = idx_by.values; out = []
    for _ in range(B):
        take = np.concatenate(arrs[rng.integers(0, len(arrs), len(arrs))])
        if y[take].min() == y[take].max(): continue
        out.append(fn(y[take], p[take]))
    return np.quantile(out, [0.025, 0.975])
