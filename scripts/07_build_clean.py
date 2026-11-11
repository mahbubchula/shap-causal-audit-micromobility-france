"""Build harmonised, linked tables 2019-2025 from raw BAAC files. No imputation, no row dropped.
Usage: python3 -I 07_build_clean.py <raw_dir> <interim_dir>
Outputs (gzip CSV): crashes, vehicles, users, micromobility_vehicles."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from baac_io import load, clean_id, YEARS
raw, out = sys.argv[1], sys.argv[2]

C = pd.concat([load(raw, "caract", y) for y in YEARS], ignore_index=True)
Lraw = pd.concat([load(raw, "lieux", y) for y in YEARS], ignore_index=True)
V = pd.concat([load(raw, "vehicules", y) for y in YEARS], ignore_index=True)
U = pd.concat([load(raw, "usagers", y) for y in YEARS], ignore_index=True)
n_raw = dict(C=len(C), V=len(V), U=len(U), killed=int((U["grav"] == "2").sum()))

# ---- crashes ----
C["dep"] = C["dep"].str.zfill(2)                                   # R1: 2019 lacks leading zero
C["date"] = pd.to_datetime(dict(year=C["an"].astype(int), month=C["mois"].astype(int), day=C["jour"].astype(int)))
hm = C["hrmn"].str.extract(r"^(\d{1,2}):(\d{2})$").astype(float)
C["hour"] = hm[0]; C["minute"] = hm[1]
C["lat_f"] = pd.to_numeric(C["lat"].str.replace(",", "."), errors="coerce")   # R2: comma decimals
C["lon_f"] = pd.to_numeric(C["long"].str.replace(",", "."), errors="coerce")
C["mainland"] = C["dep"].str.fullmatch(r"([0-8][0-9]|9[0-5]|2A|2B)")
# ---- lieux: R3 main location = first row per crash (file order); extra rows summarised ----
Lraw["vma_n"] = pd.to_numeric(Lraw["vma"], errors="coerce").where(lambda s: s.between(5, 130))
g = Lraw.groupby("Num_Acc", sort=False)
extra = g.agg(lieux_n_rows=("catr", "size"), vma_min_anyrow=("vma_n", "min"), vma_max_anyrow=("vma_n", "max"),
              vosp_cycle_anyrow=("vosp", lambda s: int(s.isin(["1", "2"]).any())))
Lmain = Lraw.drop_duplicates("Num_Acc").drop(columns=["year_file", "vma_n"])
first_missing = Lmain.set_index("Num_Acc")["vma"].isin(["-1", ""])
fillable = first_missing & extra["vma_max_anyrow"].notna().reindex(first_missing.index)
print(f"lieux: main-row vma missing {int(first_missing.sum())}; of which another row has a valid vma: {int(fillable.sum())}")
crashes = C.merge(Lmain, on="Num_Acc", how="left", validate="1:1").merge(extra, left_on="Num_Acc", right_index=True, how="left")
crashes = crashes.drop(columns=["adr", "voie", "v1", "v2", "pr", "pr1", "lartpc", "larrout"])   # free text / >60% missing / road ids

# ---- vehicles ----
V["id_vehicule"] = clean_id(V["id_vehicule"])
V["catv_i"] = pd.to_numeric(V["catv"], errors="coerce").astype("Int64")
V["mode"] = V["catv_i"].map({1: "bicycle", 50: "edp_motor", 60: "edp_nomotor", 80: "ebike"})
def vclass(c):
    if pd.isna(c): return "unknown"
    c = int(c)
    if c in (1, 80): return "cycle"
    if c in (50, 60): return "edp"
    if c in (2, 30, 31, 32, 33, 34, 41, 42, 43, 35, 36): return "ptw"
    if c in (7, 3): return "car"
    if c == 10: return "van"
    if c in (13, 14, 15, 16, 17, 37, 38, 20, 21): return "heavy"
    if c in (39, 40): return "rail"
    return "other"
V["vclass"] = V["catv_i"].map(vclass)

# ---- users ----
U["id_vehicule"] = clean_id(U["id_vehicule"])
if "id_usager" in U.columns: U["id_usager"] = clean_id(U["id_usager"].fillna(""))
an = pd.to_numeric(U["an_nais"], errors="coerce")
age = U["year_file"] - an
U["age"] = age.where(age.between(0, 105))                           # R4: implausible ages set missing
sec = U[["secu1", "secu2", "secu3"]]
U["helmet_recorded"] = (sec == "2").any(axis=1).astype(int)
U["equip_status"] = np.select([U["helmet_recorded"] == 1, U["secu1"] == "0", U["secu1"].isin(["8", "-1", ""])],
                              ["helmet", "none_recorded", "unknown"], default="other_equipment")

# ---- micromobility analysis table: one row per micromobility vehicle ----
M = V[V["mode"].notna()].copy()
drivers = U[U["catu"] == "1"].drop_duplicates("id_vehicule")        # never >1 driver per vehicle (audit step 05)
M = M.merge(drivers[["id_vehicule", "grav", "sexe", "age", "trajet", "equip_status", "helmet_recorded"]], on="id_vehicule", how="left")
M = M.rename(columns={"grav": "rider_grav"})
pas = U[U["catu"] == "2"].groupby("id_vehicule").size().rename("n_passengers")
ped = U[U["catu"] == "3"].groupby("id_vehicule").agg(n_ped_struck=("grav", "size"), ped_worst_grav=("grav", lambda s: "2" if (s == "2").any() else ("3" if (s == "3").any() else ("4" if (s == "4").any() else "1"))))
M = M.merge(pas, left_on="id_vehicule", right_index=True, how="left").merge(ped, left_on="id_vehicule", right_index=True, how="left")
M[["n_passengers", "n_ped_struck"]] = M[["n_passengers", "n_ped_struck"]].fillna(0).astype(int)
# opponent: classes of the OTHER vehicles in the same crash
nveh = V.groupby("Num_Acc").size().rename("n_vehicles")
cls = V.groupby("Num_Acc")["vclass"].agg(list)
M = M.merge(nveh, left_on="Num_Acc", right_index=True)
def opponent(row):
    others = list(cls[row["Num_Acc"]]); others.remove(row["vclass"])
    if not others: return "pedestrian" if row["n_ped_struck"] > 0 else "single"
    for k in ("heavy", "rail", "van", "car", "ptw", "cycle", "edp"):
        if k in others: return k
    return "other"
M["opponent"] = M.apply(opponent, axis=1)
M = M.merge(crashes, on=["Num_Acc", "year_file"], how="left", validate="m:1")

# ---- integrity after build ----
assert len(crashes) == n_raw["C"] and crashes["Num_Acc"].is_unique
assert len(V) == n_raw["V"] and V["id_vehicule"].is_unique
assert len(U) == n_raw["U"] and int((U["grav"] == "2").sum()) == n_raw["killed"]
assert M["id_vehicule"].is_unique and M["date"].notna().all()
os.makedirs(out, exist_ok=True)
for name, df in (("crashes", crashes), ("vehicles", V), ("users", U), ("micromobility_vehicles", M)):
    df.to_csv(os.path.join(out, f"{name}.csv.gz"), index=False, compression="gzip")
    print(f"{name:24s} rows={len(df):7d} cols={df.shape[1]}")
print("raw counts preserved:", n_raw)
print("micromobility vehicles by mode:", M["mode"].value_counts().to_dict())
print("riders without a driver row:", int(M["rider_grav"].isna().sum()))
print("opponent by mode (%):"); print((pd.crosstab(M["mode"], M["opponent"], normalize="index") * 100).round(1).to_string())
print("hour missing:", int(M["hour"].isna().sum()), "| age missing (%):", round(M["age"].isna().mean() * 100, 1))
print("columns in micromobility table:", list(M.columns))
