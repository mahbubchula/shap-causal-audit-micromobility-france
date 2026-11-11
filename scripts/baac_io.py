"""Shared loader for raw BAAC files. Everything is read as text; no value is altered
except: column names trimmed, 2022 'Accident_Id' renamed to 'Num_Acc', and
leading/trailing whitespace (incl. non-breaking spaces) stripped from values."""
import os, re
import pandas as pd

YEARS = list(range(2019, 2026))
TABLES = ("caract", "lieux", "vehicules", "usagers")
_WS = re.compile(r"^[\s  ]+|[\s  ]+$")

def load(raw_dir, table, year):
    p = os.path.join(raw_dir, f"{table}_{year}.csv")
    df = pd.read_csv(p, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    df.columns = [c.strip().strip('"') for c in df.columns]
    if "Accident_Id" in df.columns:
        df = df.rename(columns={"Accident_Id": "Num_Acc"})
    for c in df.columns:
        df[c] = df[c].str.replace(_WS, "", regex=True)
    df["year_file"] = year
    return df

def clean_id(s):
    """IDs such as '138 306 524' contain (non-breaking) spaces as thousands separators."""
    return s.str.replace(r"[\s  ]", "", regex=True)
