"""Figure environments for the manuscript, with captions taken from figures/figure_captions.md.
Usage: python -I 23_manuscript_figures.py <figure_captions_md> <manuscript_figs_dir>"""
import sys, os, re
src, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
SPEC = {2: ("Fig02_descriptive_overview", "descriptive", 0.74), 3: ("Fig03_geography", "geography", 0.7), 4: ("Fig04_outcome_dependent_recording", "recording", 0.83),
        5: ("Fig05_validation_performance", "performance", 0.77), 6: ("Fig06_shap_importance_stability", "shap", 0.77), 7: ("Fig07_audit_shap_double_ml", "audit", 0.76),
        8: ("Fig08_sources_of_disagreement", "sources", 0.79), 9: ("Fig09_effects_by_mode_and_group", "groups", 0.81), 10: ("Fig10_robustness", "robustness", 0.78)}
def tex(s):
    s = re.sub(r"\*\*\((.+?)\)\*\*", r"(\1)", s); s = re.sub(r"\*(.+?)\*", r"\\textit{\1}", s)
    for a, b in (("%", r"\%"), ("&", r"\&"), ("_", r"\_"), ("#", r"\#"), ("\u2212", "$-$"), ("\u2264", r"$\leq$"), ("\u2265", r"$\geq$"), ("\u00b1", r"$\pm$"), ("\u03c4", r"$\tau$"), ("<", "$<$"), ("\u2013", "--")): s = s.replace(a, b)
    return s
md = open(src, encoding="utf-8").read(); parts = re.split(r"(?m)^## Figure (\d+)\. ", md)
for i in range(1, len(parts), 2):
    k = int(parts[i]); title, _, body = parts[i + 1].partition("\n")
    if k not in SPEC: continue
    f, lab, h = SPEC[k]; cap = tex(title.strip().rstrip(".") + ". " + " ".join(body.split()))
    open(os.path.join(out, f"fig{k:02d}.tex"), "w", encoding="utf-8").write(
        "\\begin{figure}[!tp]\n\\centering\n\\fig[" + str(h) + "]{" + f + "}\n\\caption{" + cap + "}\n\\label{fig:" + lab + "}\n\\end{figure}\n")
print("  wrote", len(SPEC), "figure files")
