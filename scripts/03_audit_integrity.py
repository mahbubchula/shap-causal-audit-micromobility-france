"""Keys, joins, duplicates and yearly totals.
Usage: python3 -I 03_audit_integrity.py <raw_dir> <out_dir>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from baac_io import load, clean_id, YEARS

raw, out = sys.argv[1], sys.argv[2]
pd.set_option("display.width", 250)
rec = []
for y in YEARS:
    c, l, v, u = (load(raw, t, y) for t in ("caract", "lieux", "vehicules", "usagers"))
    for d in (v, u):
        d["id_vehicule"] = clean_id(d["id_vehicule"])
    r = dict(year=y, crashes=len(c))
    r["caract_dup_keys"] = int(c["Num_Acc"].duplicated().sum())
    r["caract_full_dup_rows"] = int(c.duplicated().sum())
    r["an_mismatch"] = int((c["an"] != str(y)).sum())
    # lieux
    r["lieux_rows"] = len(l); r["lieux_crashes"] = l["Num_Acc"].nunique()
    r["lieux_multi"] = int((l.groupby("Num_Acc").size() > 1).sum())
    r["lieux_orphans"] = int((~l["Num_Acc"].isin(c["Num_Acc"])).sum())
    r["crash_no_lieux"] = int((~c["Num_Acc"].isin(l["Num_Acc"])).sum())
    # vehicules
    r["veh_rows"] = len(v)
    r["veh_dup_id"] = int(v["id_vehicule"].duplicated().sum())
    r["veh_dup_acc_numveh"] = int(v.duplicated(["Num_Acc", "num_veh"]).sum())
    r["veh_orphans"] = int((~v["Num_Acc"].isin(c["Num_Acc"])).sum())
    r["crash_no_veh"] = int((~c["Num_Acc"].isin(v["Num_Acc"])).sum())
    # usagers
    r["usr_rows"] = len(u)
    r["usr_full_dup_rows"] = int(u.drop(columns="year_file").duplicated().sum())
    if "id_usager" in u.columns:
        r["usr_dup_id"] = int(clean_id(u["id_usager"]).duplicated().sum())
    r["usr_orphans_acc"] = int((~u["Num_Acc"].isin(c["Num_Acc"])).sum())
    r["usr_orphans_veh"] = int((~u["id_vehicule"].isin(v["id_vehicule"])).sum())
    kv = set(zip(v["Num_Acc"], v["num_veh"]))
    r["usr_orphans_acc_numveh"] = int(sum((a, n) not in kv for a, n in zip(u["Num_Acc"], u["num_veh"])))
    r["veh_no_user"] = int((~v["id_vehicule"].isin(u["id_vehicule"])).sum())
    r["crash_no_user"] = int((~c["Num_Acc"].isin(u["Num_Acc"])).sum())
    # totals
    g = u["grav"].value_counts()
    r.update(killed=int(g.get("2", 0)), hosp=int(g.get("3", 0)), light=int(g.get("4", 0)),
             unhurt=int(g.get("1", 0)), grav_other=int(len(u) - sum(g.get(k, 0) for k in "1234")))
    dep = c["dep"]
    metro = dep.str.fullmatch(r"(0?[1-9]|[1-8][0-9]|9[0-5]|2A|2B)")
    r["crashes_metro"] = int(metro.sum())
    um = u.merge(c[["Num_Acc", "dep"]], on="Num_Acc", how="left")
    mm = um["dep"].str.fullmatch(r"(0?[1-9]|[1-8][0-9]|9[0-5]|2A|2B)").fillna(False)
    r["killed_metro"] = int(((um["grav"] == "2") & mm).sum())
    r["hosp_metro"] = int(((um["grav"] == "3") & mm).sum())
    r["light_metro"] = int(((um["grav"] == "4") & mm).sum())
    r["n_dep_codes"] = dep.nunique()
    r["dep_examples"] = " ".join(sorted(dep.unique())[:6]) + " ... " + " ".join(sorted(dep.unique())[-8:])
    rec.append(r)
df = pd.DataFrame(rec).set_index("year")
df.to_csv(os.path.join(out, "integrity_by_year.csv"))
print(df.drop(columns="dep_examples").T.to_string())
print("\ndep code examples:"); print(df["dep_examples"].to_string())
