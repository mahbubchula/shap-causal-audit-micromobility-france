"""Download BAAC annual files (2019-2025) from data.gouv.fr and write a checksum manifest.

Usage: python3 -I 01_download_baac.py <raw_dir> <manifest_csv>
Selection rule: for each (year, table) take the resource whose title matches
<table>-<year>.csv (name variants allowed). If several match, take the one
with the latest last_modified and list every candidate in the manifest.
"""
import csv, hashlib, json, re, sys, urllib.request, datetime, os

DATASET = "53698f4ca3a729239d2036df"
API = f"https://www.data.gouv.fr/api/1/datasets/{DATASET}/"
YEARS = range(2019, 2026)
PAT = re.compile(r"^(car[a-z]*|lieux|vehicules|usagers)[-_](\d{4})\.csv$", re.I)
TABLE = {"c": "caract", "l": "lieux", "v": "vehicules", "u": "usagers"}

raw_dir, manifest = sys.argv[1], sys.argv[2]
os.makedirs(raw_dir, exist_ok=True)
with urllib.request.urlopen(API) as r:
    meta = json.load(r)
with open(os.path.join(raw_dir, "_datagouv_metadata.json"), "w") as f:
    json.dump(meta, f)

cands = {}
for res in meta["resources"]:
    m = PAT.match(res["title"].strip())
    if not m:
        continue
    table, year = TABLE[m.group(1)[0].lower()], int(m.group(2))
    if year in YEARS:
        cands.setdefault((year, table), []).append(res)

rows = []
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
for year in YEARS:
    for table in ("caract", "lieux", "vehicules", "usagers"):
        cs = sorted(cands.get((year, table), []), key=lambda r: r.get("last_modified") or "", reverse=True)
        if not cs:
            print("MISSING", year, table); continue
        res = cs[0]
        dest = os.path.join(raw_dir, f"{table}_{year}.csv")
        urllib.request.urlretrieve(res["url"], dest)
        data = open(dest, "rb").read()
        rows.append({
            "year": year, "table": table, "local_file": os.path.basename(dest),
            "source_title": res["title"], "source_url": res["url"],
            "source_last_modified": res.get("last_modified"), "resource_id": res.get("id"),
            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "n_candidates": len(cs), "other_candidates": " | ".join(c["title"] for c in cs[1:]),
            "downloaded_utc": now,
        })
        print(year, table, len(data), res["title"], f"(candidates: {len(cs)})")
with open(manifest, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("licence:", meta.get("license"), "| dataset last_update:", meta.get("last_update"), "| files:", len(rows))
