"""Value distributions and missingness by year, for all rows and for the micromobility subset.
Usage: python3 -I 05_audit_values.py <raw_dir> <out_dir>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from baac_io import load, clean_id, YEARS
raw, out = sys.argv[1], sys.argv[2]
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 400)

C, L, V, U = [], [], [], []
for y in YEARS:
    c = load(raw, "caract", y); l = load(raw, "lieux", y).drop_duplicates("Num_Acc")  # first row = main location
    v = load(raw, "vehicules", y); u = load(raw, "usagers", y)
    C.append(c); L.append(l); V.append(v); U.append(u)
C, L, V, U = (pd.concat(x, ignore_index=True) for x in (C, L, V, U))
for d in (V, U): d["id_vehicule"] = clean_id(d["id_vehicule"])
V["catv_i"] = pd.to_numeric(V["catv"], errors="coerce")
MM = {1: "bicycle", 50: "EDP_motor", 60: "EDP_nomotor", 80: "ebike"}
V["mode"] = V["catv_i"].map(MM)

def dist(df, col, top=14):
    t = pd.crosstab(df[col].replace("", "(blank)"), df["year_file"])
    t = t.loc[t.sum(axis=1).sort_values(ascending=False).index]
    if len(t) > top:
        t = pd.concat([t.iloc[:top], t.iloc[top:].sum().to_frame("(other)").T])
    return (t / t.sum() * 100).round(1)

MISS = {"", "-1", "N/A", "."}
def missing_table(df, cols, extra=None):
    extra = extra or {}
    r = {}
    for c_ in cols:
        bad = df[c_].isin(MISS | extra.get(c_, set()))
        r[c_] = bad.groupby(df["year_file"]).mean().mul(100).round(1)
    return pd.DataFrame(r).T

print("######## 1. MISSINGNESS (% of rows blank / -1 / N/A), all crashes ########")
print("-- caract --"); print(missing_table(C, ["hrmn", "lum", "agg", "int", "atm", "col", "adr", "lat", "long", "com"]).to_string())
print("-- lieux (main row) --"); print(missing_table(L, ["catr", "circ", "nbv", "vosp", "prof", "plan", "larrout", "surf", "infra", "situ", "vma"]).to_string())
print("-- vehicules --"); print(missing_table(V, ["senc", "catv", "obs", "obsm", "choc", "manv", "motor"]).to_string())
print("-- usagers --"); print(missing_table(U, ["place", "catu", "grav", "sexe", "an_nais", "trajet", "secu1", "secu2", "secu3", "locp", "actp", "etatp"]).to_string())

print("\n######## 2. CODE DISTRIBUTIONS BY YEAR (% of rows) ########")
for name, df, cols in (("caract", C, ["lum", "agg", "int", "atm", "col"]),
                       ("lieux", L, ["catr", "circ", "vosp", "situ", "infra", "surf", "vma", "nbv"]),
                       ("vehicules", V, ["catv", "motor", "obsm", "choc"]),
                       ("usagers", U, ["catu", "grav", "sexe", "trajet", "secu1", "secu2", "secu3"])):
    for c_ in cols:
        print(f"-- {name}.{c_} --"); print(dist(df, c_).to_string())

print("\n######## 3. FORMAT CHECKS ########")
lat = pd.to_numeric(C["lat"].str.replace(",", "."), errors="coerce"); lon = pd.to_numeric(C["long"].str.replace(",", "."), errors="coerce")
C["lat_f"], C["lon_f"] = lat, lon
metro = C["dep"].str.fullmatch(r"(0?[1-9]|[1-8][0-9]|9[0-5]|2A|2B)")
inbox = lat.between(41, 51.5) & lon.between(-5.5, 10)
print("lat/long numeric & non-zero (% all):", ((lat.notna() & lon.notna() & (lat != 0)).groupby(C["year_file"]).mean() * 100).round(2).to_dict())
print("metro crashes with coords inside mainland box (%):", (inbox[metro].groupby(C["year_file"][metro]).mean() * 100).round(2).to_dict())
print("lat uses comma decimal (%):", (C["lat"].str.contains(",").groupby(C["year_file"]).mean() * 100).round(1).to_dict())
print("hrmn formats:", C.groupby("year_file")["hrmn"].agg(lambda s: s.str.replace(r"\d", "9", regex=True).value_counts().head(3).to_dict()).to_dict())
an = pd.to_numeric(U["an_nais"], errors="coerce"); age = U["year_file"] - an
print("age <0 or >105 (n):", ((age < 0) | (age > 105)).groupby(U["year_file"]).sum().to_dict())
print("dep code lengths:", C.groupby("year_file")["dep"].agg(lambda s: s.str.len().value_counts().to_dict()).to_dict())
print("com code lengths:", C.groupby("year_file")["com"].agg(lambda s: s.str.len().value_counts().to_dict()).to_dict())

print("\n######## 4. MICROMOBILITY SUBSET ########")
M = V[V["mode"].notna()].copy()
print("-- vehicles by mode and year --"); print(pd.crosstab(M["mode"], M["year_file"], margins=True).to_string())
print("-- catv x motor (all years, n) --"); print(pd.crosstab(M["mode"], M["motor"]).to_string())
print("-- motor code by year for bicycles (catv=1), % --"); print(dist(M[M["mode"] == "bicycle"], "motor").to_string())
print("-- motor code by year for EDP_motor, % --"); print(dist(M[M["mode"] == "EDP_motor"], "motor").to_string())
# riders
R = U.merge(M[["id_vehicule", "mode"]], on="id_vehicule", how="inner")
print("-- users attached to micromobility vehicles: catu by mode (n) --"); print(pd.crosstab(R["mode"], R["catu"]).to_string())
drv = R[R["catu"] == "1"]
print("-- drivers per vehicle: vehicles with 0 / 1 / 2+ drivers --")
nd = drv.groupby("id_vehicule").size().reindex(M["id_vehicule"]).fillna(0).astype(int)
print(pd.crosstab(M["mode"].values, np.minimum(nd.values, 2)).to_string())
print("-- rider (catu=1) injury severity by mode and year (n) --")
print(pd.crosstab([drv["mode"], drv["grav"]], drv["year_file"]).to_string())
print("-- rider missingness (%), by mode --")
for m_, g in drv.groupby("mode"):
    print(m_); print(missing_table(g, ["sexe", "an_nais", "trajet", "secu1", "secu2", "secu3", "grav"]).to_string())
drv = drv.assign(helmet=(drv[["secu1", "secu2", "secu3"]] == "2").any(axis=1),
                 secu_known=~(drv["secu1"].isin(["-1", "8", ""])))
print("-- helmet recorded among riders with known equipment (%), by mode and year --")
print((drv[drv["secu_known"]].groupby(["mode", "year_file"])["helmet"].mean().unstack() * 100).round(1).to_string())
print("-- share of riders with equipment unknown (-1 or 8), % --")
print(((1 - drv.groupby(["mode", "year_file"])["secu_known"].mean()).unstack() * 100).round(1).to_string())
# pedestrians struck by micromobility vehicles
ped = R[R["catu"] == "3"]
print("-- pedestrians linked to a micromobility vehicle, by mode and year (n) --"); print(pd.crosstab(ped["mode"], ped["year_file"], margins=True).to_string())
print("-- their severity (n) --"); print(pd.crosstab(ped["mode"], ped["grav"]).to_string())
M.merge(C[["Num_Acc", "dep", "com", "mois", "jour", "an"]], on="Num_Acc").to_csv(os.path.join(out, "_mm_vehicles_tmp.csv"), index=False)
