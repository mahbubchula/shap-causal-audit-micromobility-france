"""Investigate structural quirks found in step 03.
Usage: python3 -I 04_audit_quirks.py <raw_dir>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from baac_io import load, clean_id
raw = sys.argv[1]
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)

print("=== A. lieux multi-row crashes (2023-2025) ===")
for y in (2022, 2023, 2025):
    l = load(raw, "lieux", y); c = load(raw, "caract", y)
    n = l.groupby("Num_Acc").size().rename("n_rows")
    print(y, "rows per crash:", n.value_counts().sort_index().to_dict())
    if n.max() > 1:
        m = c.merge(n, left_on="Num_Acc", right_index=True)
        m["multi"] = m["n_rows"] > 1
        print("  share multi by intersection code (int):")
        print("  ", m.groupby("int")["multi"].mean().round(3).to_dict())
        multi = l[l["Num_Acc"].isin(n[n > 1].index)]
        cols = [c_ for c_ in l.columns if c_ not in ("Num_Acc", "year_file")]
        differ = {c_: round(float((multi.groupby("Num_Acc")[c_].nunique() > 1).mean()), 3) for c_ in cols}
        print("  share of multi-row crashes where the column differs between rows:"); print("  ", differ)
        ex = n[n > 1].index[:2]
        print(l[l["Num_Acc"].isin(ex)].drop(columns="year_file").to_string(index=False))
        first = l.drop_duplicates("Num_Acc")
        print("  file sorted by Num_Acc:", l["Num_Acc"].is_monotonic_increasing or l["Num_Acc"].is_monotonic_decreasing,
              "| rows of one crash contiguous:", (l["Num_Acc"] != l["Num_Acc"].shift()).sum() == l["Num_Acc"].nunique())

print("\n=== B. vehicules 2025: extra text line ===")
p = os.path.join(raw, "vehicules_2025.csv")
lines = open(p, encoding="utf-8").read().split("\n")
bad = [(i, ln) for i, ln in enumerate(lines) if ln.strip() and ln.count(";") != lines[0].count(";")]
print("lines with wrong field count:", bad[:5], "| trailing empty lines:", sum(1 for ln in lines[-3:] if ln == ""))

print("\n=== C. 2019 duplicate (Num_Acc, num_veh) in vehicules ===")
v = load(raw, "vehicules", 2019)
d = v[v.duplicated(["Num_Acc", "num_veh"], keep=False)].sort_values(["Num_Acc", "num_veh"])
print(len(d), "rows;", d["Num_Acc"].nunique(), "crashes; num_veh values:", d["num_veh"].value_counts().head(5).to_dict())
print(d.head(6).drop(columns="year_file").to_string(index=False))

print("\n=== D. vehicles with no user row, by year and vehicle category ===")
for y in range(2019, 2026):
    v = load(raw, "vehicules", y); u = load(raw, "usagers", y)
    v["id_vehicule"] = clean_id(v["id_vehicule"]); u["id_vehicule"] = clean_id(u["id_vehicule"])
    nu = v[~v["id_vehicule"].isin(u["id_vehicule"])]
    cat = nu["catv"].astype(int).value_counts()
    print(y, "total:", len(nu), "| top catv:", cat.head(4).to_dict(), "| EDP(50):", int(cat.get(50, 0)), "e-bike(80):", int(cat.get(80, 0)), "bicycle(1):", int(cat.get(1, 0)))

print("\n=== E. grav codes other than 1-4, and full-duplicate user rows ===")
for y in range(2019, 2026):
    u = load(raw, "usagers", y)
    oth = u[~u["grav"].isin(list("1234"))]["grav"].value_counts().to_dict()
    dup = u[u.drop(columns="year_file").duplicated(keep=False)]
    print(y, "grav other:", oth, "| full-dup user rows:", len(dup), "| of which catu:", dup["catu"].value_counts().to_dict() if len(dup) else {})
