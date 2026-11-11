"""Build the rider-level analysis table for Paper 1 and run the outcome-dependent recording check (plan section 4).
Usage: python -I 10_build_analysis_table.py <interim_dir> <out_dir>"""
import sys, os, json
import numpy as np, pandas as pd
interim, out = sys.argv[1], sys.argv[2]
M = pd.read_csv(os.path.join(interim, "micromobility_vehicles.csv.gz"), dtype=str, keep_default_na=False)
n0 = len(M)
num = lambda s: pd.to_numeric(M[s], errors="coerce")
M["date"] = pd.to_datetime(M["date"])
keep = M["mode"].isin(["bicycle", "edp_motor", "ebike"]) & (M["mainland"] == "True") & M["rider_grav"].isin(["1", "2", "3", "4", "1.0", "2.0", "3.0", "4.0"])
flow = {"micromobility vehicles 2019-2025": n0, "mode in bicycle/e-scooter/e-bike": int(M["mode"].isin(["bicycle", "edp_motor", "ebike"]).sum()),
        "+ mainland": int((M["mode"].isin(["bicycle", "edp_motor", "ebike"]) & (M["mainland"] == "True")).sum()), "+ rider with known injury level": int(keep.sum())}
M = M[keep].copy()
def code(col, missing=("-1", "", "N/A", ".")):
    s = M[col].str.replace(r"\.0$", "", regex=True)
    return s.where(~s.isin(missing))
A = pd.DataFrame({"Num_Acc": M["Num_Acc"], "id_vehicule": M["id_vehicule"], "date": M["date"]})
g = pd.to_numeric(M["rider_grav"], errors="coerce").astype(int)
A["grav"] = g; A["ksi"] = g.isin([2, 3]).astype(int); A["killed"] = (g == 2).astype(int)
# tier 0
A["year"] = M["date"].dt.year; A["month"] = M["date"].dt.month; A["dow"] = M["date"].dt.dayofweek
A["hour"] = pd.to_numeric(M["hour"], errors="coerce"); A["dep"] = M["dep"]; A["urban"] = (code("agg") == "2").astype(int)
A["day_even"] = (M["date"].dt.day % 2 == 0).astype(int)                      # placebo (R10)
# tier 1
A["mode"] = M["mode"].map({"bicycle": "bicycle", "edp_motor": "escooter", "ebike": "ebike"})
A["age"] = pd.to_numeric(M["age"], errors="coerce")
A["sex"] = code("sexe").map({"1": "male", "2": "female"})
A["trip"] = code("trajet", missing=("-1", "0", "", "N/A"))
A["n_passengers"] = pd.to_numeric(M["n_passengers"], errors="coerce").fillna(0).astype(int)
# tier 2
for c in ("catr", "circ", "vosp", "prof", "plan", "infra", "lum", "atm", "surf"): A[c] = code(c)
A["int_type"] = code("int")
nbv = pd.to_numeric(M["nbv"], errors="coerce"); A["nbv"] = nbv.where(nbv.between(1, 12))
vma = pd.to_numeric(M["vma"], errors="coerce"); A["vma"] = vma.where(vma.between(5, 130))
A["vma_max_anyrow"] = pd.to_numeric(M["vma_max_anyrow"], errors="coerce"); A["vma_min_anyrow"] = pd.to_numeric(M["vma_min_anyrow"], errors="coerce")
A["vosp_cycle_anyrow"] = pd.to_numeric(M["vosp_cycle_anyrow"], errors="coerce")
# tier 3
A["situ"] = code("situ"); A["col"] = code("col"); A["opponent"] = M["opponent"]
A["n_vehicles"] = pd.to_numeric(M["n_vehicles"], errors="coerce").clip(upper=4)
A["ped_struck"] = (pd.to_numeric(M["n_ped_struck"], errors="coerce") > 0).astype(int)
A["obs"] = code("obs"); A["obsm"] = code("obsm"); A["choc"] = code("choc"); A["manv"] = code("manv", missing=("-1", "0", "", "N/A"))
# never-used variables kept only for the leakage demonstration (protocol b)
A["LEAK_equip"] = M["equip_status"]; A["LEAK_ped_worst_grav"] = M["ped_worst_grav"].replace("", "none")
# police-area flags
A["paris_police_area"] = A["dep"].isin(["75", "92", "93", "94"]).astype(int)
# treatments (plan section 7); NaN = outside the population for that factor
T = pd.DataFrame(index=A.index)
T["A1"] = np.where(A["mode"] == "escooter", 1.0, np.where(A["mode"] == "bicycle", 0.0, np.nan))
T["A2"] = np.where(A["mode"] == "ebike", 1.0, np.where(A["mode"] == "bicycle", 0.0, np.nan))
T["B1"] = np.where((A["urban"] == 1) & (A["vma"] <= 30), 1.0, np.where((A["urban"] == 1) & (A["vma"] == 50), 0.0, np.nan))
T["B2"] = np.where(A["lum"].isin(["3", "4"]), 1.0, np.where(A["lum"] == "5", 0.0, np.nan))
adverse = A["atm"].isin(["2", "3", "4", "5", "6"]) | A["surf"].isin(["2", "3", "4", "5", "6", "7"])
normal = A["atm"].isin(["1", "8"]) & (A["surf"] == "1")
T["B3"] = np.where(adverse, 1.0, np.where(normal, 0.0, np.nan))
T["B4"] = np.where(A["vosp"].isin(["1", "2"]), 1.0, np.where(A["vosp"] == "0", 0.0, np.nan))
T["B5"] = np.where(A["int_type"].isin(list("23456789")), 1.0, np.where(A["int_type"] == "1", 0.0, np.nan))
T["B6"] = A["urban"].astype(float)
two = A["n_vehicles"] == 2
T["C1"] = np.where(two & (A["opponent"] == "heavy"), 1.0, np.where(two & (A["opponent"] == "car"), 0.0, np.nan))
T["C2"] = np.where(A["opponent"] == "single", 1.0, np.where(A["opponent"].isin(["car", "van", "heavy", "ptw"]), 0.0, np.nan))
T["C3"] = np.where(A["situ"] == "5", 1.0, np.where(A["situ"] == "1", 0.0, np.nan))
T["D1"] = np.where(A["age"] >= 65, 1.0, np.where(A["age"].between(25, 64), 0.0, np.nan))
T["D2"] = np.where(A["sex"] == "male", 1.0, np.where(A["sex"] == "female", 0.0, np.nan))
T["R10"] = A["day_even"].astype(float)
A = pd.concat([A, T.add_prefix("T_")], axis=1)
A["split"] = np.where(A["year"] == 2019, "sensitivity_2019", np.where(A["year"] <= 2023, "development", "test"))
flow["main window 2020-2025"] = int((A["year"] >= 2020).sum())
TIERS = {"tier0": ["year", "month", "dow", "hour", "dep", "urban"],
         "tier1": ["mode", "age", "sex", "trip", "n_passengers"],
         "tier2": ["catr", "circ", "nbv", "vosp", "prof", "plan", "infra", "vma", "int_type", "lum", "atm", "surf"],
         "tier3": ["situ", "col", "opponent", "n_vehicles", "ped_struck", "obs", "obsm", "choc", "manv"]}
CATEG = ["dep", "mode", "sex", "trip", "catr", "circ", "vosp", "prof", "plan", "infra", "int_type", "lum", "atm", "surf", "situ", "col", "opponent", "obs", "obsm", "choc", "manv"]
json.dump({"tiers": TIERS, "categorical": CATEG}, open(os.path.join(interim, "feature_spec.json"), "w"), indent=1)
A.to_parquet(os.path.join(interim, "analysis_riders.parquet"), index=False)

pd.set_option("display.width", 220)
print("SAMPLE FLOW:"); [print(f"  {k}: {v}") for k, v in flow.items()]
main = A[A["year"] >= 2020]
print("\nMAIN SAMPLE by split and mode (n riders | killed-or-hospitalised % | killed n):")
t = main.groupby(["split", "mode"]).agg(n=("ksi", "size"), ksi_pct=("ksi", lambda s: round(s.mean() * 100, 1)), killed=("killed", "sum"))
print(t.to_string())
print("crashes:", main["Num_Acc"].nunique(), "| riders per crash >1:", int((main.groupby("Num_Acc").size() > 1).sum()))
print("\nTREATMENT ARMS, main sample (treated / reference / severe in treated / severe in reference):")
for c in [c for c in A.columns if c.startswith("T_")]:
    d = main[main[c].notna()]
    print(f"  {c[2:]:4s} {int((d[c]==1).sum()):6d} / {int((d[c]==0).sum()):6d} / {int(d.loc[d[c]==1,'ksi'].sum()):5d} / {int(d.loc[d[c]==0,'ksi'].sum()):5d}")

print("\nOUTCOME-DEPENDENT RECORDING CHECK (unknown rate %, severe vs not severe, by mode; main sample)")
allf = sum(TIERS.values(), []) + ["LEAK_equip"]
rows = []
for f in allf:
    unk = main[f].isna() if f != "LEAK_equip" else (main[f] == "unknown")
    for m, gdf in main.groupby("mode"):
        u = unk.loc[gdf.index]
        r1, r0 = u[gdf["ksi"] == 1].mean() * 100, u[gdf["ksi"] == 0].mean() * 100
        rows.append(dict(feature=f, mode=m, unk_severe=round(r1, 1), unk_not_severe=round(r0, 1), diff=round(r1 - r0, 1)))
chk = pd.DataFrame(rows); chk.to_csv(os.path.join(out, "outcome_dependent_recording.csv"), index=False)
w = chk.pivot(index="feature", columns="mode", values="diff"); w["max_abs"] = w.abs().max(axis=1)
overall = chk.groupby("feature")[["unk_severe", "unk_not_severe"]].mean().round(1)
w = w.join(overall).sort_values("max_abs", ascending=False)
print(w[w["max_abs"] >= 1.0].to_string())
print("\nFLAG >=10 points (remove):", list(w.index[w["max_abs"] >= 10]), "| 5-10 points (sensitivity):", list(w.index[(w["max_abs"] >= 5) & (w["max_abs"] < 10)]))
