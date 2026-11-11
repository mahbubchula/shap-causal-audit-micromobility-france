#!/usr/bin/env bash
# Rebuilds every result, table and figure from the public BAAC files.
# Usage: PY=/path/to/python ./run_all.sh     (Python 3.13 with requirements.txt installed)
set -euo pipefail
PY="${PY:-python3}"; S=scripts
mkdir -p data/raw/baac data/raw/geo data/interim outputs/audit outputs/results outputs/models figures tables

# 1. Download the 28 BAAC files (2019-2025) and record their SHA-256 checksums
"$PY" -I $S/01_download_baac.py data/raw/baac outputs/audit/download_manifest.csv
# Departement boundaries for the map figure (confirm the licence of this file before reuse)
[ -f data/raw/geo/departements.geojson ] || curl -sSL -o data/raw/geo/departements.geojson \
  https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson

# 2. Data audit and cleaned tables
"$PY" -I $S/02_audit_schema.py    data/raw/baac outputs/audit
"$PY" -I $S/03_audit_integrity.py data/raw/baac outputs/audit
"$PY" -I $S/04_audit_quirks.py    data/raw/baac
"$PY" -I $S/05_audit_values.py    data/raw/baac outputs/audit
"$PY" -I $S/06_audit_adoption_paris.py data/raw/baac outputs/audit
"$PY" -I $S/07_build_clean.py     data/raw/baac data/interim

# 3. Analysis table and outcome-dependent recording check
"$PY" -I $S/10_build_analysis_table.py data/interim outputs/audit

# 4. Prediction, validation protocols and SHAP
"$PY" -I $S/11_predictive_models.py data/interim outputs/results outputs/models
"$PY" -I $S/12_shap.py              data/interim outputs/results outputs/models

# 5. Double machine learning, audit, robustness and group effects (several hours in total)
"$PY" -I $S/13_dml_main.py       data/interim outputs/results
"$PY" -I $S/14_audit.py          outputs/results
"$PY" -I $S/15_robustness.py     data/interim outputs/results outputs/audit
"$PY" -I $S/15b_robustness_r5_check.py data/interim outputs/results outputs/audit
"$PY" -I $S/16_heterogeneity.py  data/interim outputs/results

# 6. Figures and tables
"$PY" -I $S/20_figures.py outputs/results figures
"$PY" -I $S/21_tables.py  outputs/results data/interim outputs/audit tables
