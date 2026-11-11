"""Code-adoption check for catv=50 and Paris-specific data quality.
Usage: python3 -I 06_audit_adoption_paris.py <raw_dir> <out_dir>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from baac_io import load, clean_id, YEARS
raw, out = sys.argv[1], sys.argv[2]
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 200)

C = pd.concat([load(raw, "caract", y) for y in YEARS], ignore_index=True)
V = pd.concat([load(raw, "vehicules", y) for y in YEARS], ignore_index=True)
C["dep"] = C["dep"].str.zfill(2)                      # 2019 lacks the leading zero
V["catv_i"] = pd.to_numeric(V["catv"], errors="coerce")
V = V.merge(C[["Num_Acc", "dep", "com", "mois", "agg", "lat", "long"]], on="Num_Acc", how="left")
V["ym"] = V["year_file"].astype(str) + "-" + V["mois"].str.zfill(2)

print("=== A. Possible 'spill' categories nationally (n vehicles) ===")
t = pd.crosstab(V["catv_i"], V["year_file"]).reindex([0, 99, 60, 50, 80, 1, 2, 30])
t.index = ["00 indeterminable", "99 other", "60 EDP no motor", "50 EDP motor", "80 e-bike", "01 bicycle", "02 moped", "30 scooter<50cc"]
print(t.to_string())

print("\n=== B. Adoption of code 50 by departement (mainland) ===")
metro = V["dep"].str.fullmatch(r"([0-8][0-9]|9[0-5]|2A|2B)")
E = V[(V["catv_i"] == 50) & metro]
by = pd.crosstab(E["dep"], E["year_file"]).reindex(sorted(V.loc[metro, "dep"].unique()), fill_value=0)
print("departements with zero code-50 vehicles, by year:", (by == 0).sum().to_dict(), "of", len(by))
print("departements with >=10:", (by >= 10).sum().to_dict())
first = E.groupby("dep")["ym"].min()
print("first month a departement used code 50 -> number of departements by year:", first.str[:4].value_counts().sort_index().to_dict())
by.to_csv(os.path.join(out, "edp_by_dep_year.csv"))
print("top 15 departements, code 50 by year:"); print(by.loc[by.sum(axis=1).sort_values(ascending=False).index[:15]].to_string())
conc = (by.loc[["75", "92", "93", "94"]].sum() / by.sum() * 100).round(1)
print("share of national code-50 vehicles in Paris + inner suburbs (%):", conc.to_dict())

print("\n=== C. Paris 2019 monthly code-50 counts (pre-period only; adoption lag check) ===")
p19 = E[(E["dep"] == "75") & (E["year_file"] == 2019)]
print(p19["mois"].astype(int).value_counts().sort_index().to_dict())
for dgrp, name in ((["92", "93", "94"], "inner suburbs"), (["69"], "Rhone"), (["13"], "B-d-Rhone"), (["33"], "Gironde"), (["31"], "Hte-Garonne"), (["06"], "Alpes-Mar."), (["59"], "Nord"), (["67"], "Bas-Rhin")):
    s = E[E["dep"].isin(dgrp) & (E["year_file"] == 2019)]["mois"].astype(int).value_counts().sort_index()
    print(f"  {name:14s}", s.reindex(range(1, 13), fill_value=0).tolist())

print("\n=== D. Paris data quality ===")
Pv = V[V["dep"] == "75"]
print("Paris commune codes used:", sorted(Pv["com"].unique())[:25], "| n distinct:", Pv["com"].nunique())
lat = pd.to_numeric(Pv["lat"].str.replace(",", "."), errors="coerce"); lon = pd.to_numeric(Pv["long"].str.replace(",", "."), errors="coerce")
inb = lat.between(48.80, 48.91) & lon.between(2.22, 2.47)
print("Paris vehicles with coordinates inside the Paris bounding box (%), by year:", (inb.groupby(Pv["year_file"]).mean() * 100).round(2).to_dict())
print("  same, code-50 only:", (inb[Pv["catv_i"] == 50].groupby(Pv["year_file"][Pv["catv_i"] == 50]).mean() * 100).round(2).to_dict())
print("Paris crashes 'agg' (2 = built-up):", Pv.drop_duplicates("Num_Acc")["agg"].value_counts().to_dict())

print("\n=== E. Monthly panel written (departement x month x mode) ===")
MM = {1: "bicycle", 50: "edp_motor", 80: "ebike", 60: "edp_nomotor"}
V["mode"] = V["catv_i"].map(MM)
allv = V.groupby(["dep", "ym"]).agg(all_vehicles=("catv_i", "size"), crashes=("Num_Acc", "nunique")).reset_index()
mm = V[V["mode"].notna()].groupby(["dep", "ym", "mode"]).size().unstack(fill_value=0).reset_index()
panel = allv.merge(mm, on=["dep", "ym"], how="left").fillna(0)
panel.to_csv(os.path.join(out, "panel_dep_month_vehicles.csv"), index=False)
print(panel.shape, "rows x cols;", panel["dep"].nunique(), "departements;", panel["ym"].nunique(), "months")
