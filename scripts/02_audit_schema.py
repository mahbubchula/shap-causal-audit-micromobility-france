"""Audit file structure of every raw BAAC file: encoding, separator, columns, rows.
Usage: python3 -I 02_audit_schema.py <raw_dir> <out_dir>
"""
import sys, os, csv, io, collections
import pandas as pd

raw_dir, out_dir = sys.argv[1], sys.argv[2]
YEARS = range(2019, 2026); TABLES = ("caract", "lieux", "vehicules", "usagers")

def sniff(path):
    b = open(path, "rb").read()
    bom = b.startswith(b"\xef\xbb\xbf")
    try:
        txt = b.decode("utf-8-sig"); enc = "utf-8"
    except UnicodeDecodeError:
        txt = b.decode("latin-1"); enc = "latin-1"
    head = txt.split("\n", 1)[0]
    sep = max(";,\t", key=head.count)
    return enc, bom, sep, txt

rows, cols_by = [], collections.defaultdict(dict)
for t in TABLES:
    for y in YEARS:
        p = os.path.join(raw_dir, f"{t}_{y}.csv")
        enc, bom, sep, txt = sniff(p)
        df = pd.read_csv(io.StringIO(txt), sep=sep, dtype=str, keep_default_na=False, quoting=csv.QUOTE_MINIMAL)
        df.columns = [c.strip().strip('"') for c in df.columns]
        n_lines = txt.rstrip("\n").count("\n")  # data lines (excl. header)
        rows.append(dict(table=t, year=y, encoding=enc, bom=bom, sep=repr(sep), n_rows=len(df),
                         n_text_lines=n_lines, n_cols=df.shape[1], columns=" ".join(df.columns)))
        cols_by[t][y] = list(df.columns)
out = pd.DataFrame(rows)
out.to_csv(os.path.join(out_dir, "schema_by_file.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(out.drop(columns="columns").to_string(index=False))
for t in TABLES:
    print(f"\n== {t}: column presence by year ==")
    allc = []
    for y in YEARS:
        for c in cols_by[t][y]:
            if c not in allc: allc.append(c)
    for c in allc:
        pres = "".join("x" if c in cols_by[t][y] else "." for y in YEARS)
        flag = "" if pres == "x" * len(YEARS) else "   <-- not in all years"
        print(f"  {c:<14}{pres}{flag}")
    print("  (years:", " ".join(str(y) for y in YEARS), ")")
    orders = {tuple(cols_by[t][y]) for y in YEARS}
    print("  distinct column orders:", len(orders))
