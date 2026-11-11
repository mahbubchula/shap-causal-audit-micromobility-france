"""LaTeX tables sized for the manuscript page (main Tables 1-7) and for the supplement (Tables S1-S10).
Usage: python -I 22_manuscript_tables.py <tables_csv_dir> <tables_preview_md> <manuscript_tables_dir>
Reads the CSV files written by 21_tables.py; titles and notes are taken from the Markdown preview so that wording stays in one place."""
import sys, os, re
import pandas as pd
csv_dir, preview, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
REP = (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"), ("\u2212", "$-$"), ("\u2264", r"$\leq$"), ("\u2265", r"$\geq$"), ("\u00b1", r"$\pm$"),
       ("\u2192", r"$\rightarrow$"), ("<", "$<$"), (">", "$>$"), ("\u2003", r"\quad "))
def tex(s):
    s = "" if pd.isna(s) else str(s)
    for a, b in REP: s = s.replace(a, b)
    return re.sub(r"^\s{3}", r"\\quad ", s)
US = (("d\u00e9partement", "d\u00e9partement"), ("kilometre", "kilometer"), ("colour", "color"), ("regularis", "regulariz"), ("standardis", "standardiz"), ("hospitalised", "hospitalized"), ("motorised", "motorized"),
      ("Standardis", "Standardiz"), ("Hospitalised", "Hospitalized"), ("analys", "analyz"), ("recognis", "recogniz"), ("Travelling", "Traveling"), ("travelling", "traveling"), ("programme", "program"), ("smoothing", "smoothing"))
def us(s):
    for a, b in US: s = s.replace(a, b)
    return s.replace("analyzis", "analysis").replace("Analyzis", "Analysis")
# titles and notes from the preview
md = open(preview, encoding="utf-8").read(); META = {}
for m in re.finditer(r"(?m)^## (Table S?\d+)\. (.+)$", md):
    tid = m.group(1).replace(" ", ""); nxt = md.find("\n## ", m.end()); blk = md[m.end():nxt if nxt > 0 else len(md)]
    META[tid] = dict(title=us(m.group(2).strip()), notes=[us(n) for n in re.findall(r"(?m)^\*(.+)\*$", blk)])
def read(tid):
    df = pd.read_csv(os.path.join(csv_dir, tid + ".csv"), dtype=str, keep_default_na=False, encoding="utf-8-sig"); df.columns = [re.sub(r"\.\d+$", "", c) for c in df.columns]
    return df.map(us) if hasattr(df, "map") else df.applymap(us)
def notes_block(notes, width=r"\linewidth"):
    return "\\par\\vspace{3pt}\\begin{minipage}{" + width + "}\\footnotesize\\raggedright\\textit{Note.} " + " ".join(tex(n) for n in notes) + "\\end{minipage}\n"
def write(tid, body):
    open(os.path.join(out, tid + ".tex"), "w", encoding="utf-8").write(body)
def table(tid, df, spec, heads, size=r"\footnotesize", env="tabularx", rowfmt=None, place="!tp", stretch=1.08, sep="3.5pt"):
    """Main-text table: full text width, wrapped headers, APA-style title above and note beneath."""
    rows = []
    for i, r in enumerate(df.values):
        cells = rowfmt(i, list(r)) if rowfmt else [tex(v) for v in r]; rows.append(cells if isinstance(cells, str) else " & ".join(cells) + r" \\")
    begin = r"\begin{tabularx}{\linewidth}{" + spec + "}" if env == "tabularx" else r"\begin{tabular}{" + spec + "}"
    write(tid, "\\begin{table}[" + place + "]\n\\caption{" + tex(META[tid]["title"]) + "}\\label{tab:" + tid.lower() + "}\n" + size + "\\setlength{\\tabcolsep}{" + sep + "}\\renewcommand{\\arraystretch}{" + str(stretch) + "}\n" +
          begin + "\n\\toprule\n" + " & ".join(heads) + " \\\\\n\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{" + env + "}\n" + notes_block(META[tid]["notes"]) + "\\end{table}\n")
H = lambda s: r"\multicolumn{1}{c}{\shortstack[c]{" + s.replace("%", r"\%").replace("|", r"\\") + "}}"
HL = lambda s: r"\shortstack[l]{" + s.replace("%", r"\%").replace("|", r"\\") + "}"

# Table 1
d = read("Table1"); table("Table1", d, r"@{}p{2.3cm}p{4.1cm}r>{\raggedright\arraybackslash}X@{}", [HL("File"), HL("Unit of observation"), H("Records,|2019\u20132025"), HL("Variables used")])
# Table 2
d = read("Table2")
def r2(i, r):
    first = i % 4 == 0; cells = [tex(r[0]) if first else ""] + [tex(v) for v in r[1:]]
    return ("\\addlinespace[2pt]\n" if first and i else "") + " & ".join(cells) + r" \\"
table("Table2", d, r"@{}>{\raggedright\arraybackslash}p{4.3cm}lrr>{\raggedleft\arraybackslash}X>{\raggedleft\arraybackslash}p{2.2cm}@{}", [HL("Partition"), HL("Mode"), H("Riders"), H("Crashes"), H("Killed or|hospitalized, n (%)"), H("Killed,|n (%)")], rowfmt=r2)
# Table 3
d = read("Table3"); seen = set()
def r3(i, r):
    first = r[0] not in seen; seen.add(r[0]); cells = [tex(r[0]) if first else ""] + [tex(v) for v in r[1:]]
    return ("\\addlinespace[2pt]\n" if first and i else "") + " & ".join(cells) + r" \\"
table("Table3", d, r"@{}>{\raggedright\arraybackslash}p{2.35cm}>{\raggedright\arraybackslash}p{2.35cm}>{\raggedright\arraybackslash}p{1.95cm}>{\raggedright\arraybackslash}p{2.55cm}>{\raggedright\arraybackslash}Xr@{}",
      [HL("Tier"), HL("Variable"), HL("Source file"), HL("Type"), HL("Definition"), H("Unknown|(%)")], size=r"\scriptsize", rowfmt=r3, stretch=1.02, place="!tp")
# Table 4
d = read("Table5")
def r4(i, r):
    if all(v == "" for v in r[1:]): return "\\addlinespace[2pt]\n\\textit{" + tex(r[0]) + r"} & & & & \\"
    return " & ".join(tex(v) for v in r) + r" \\"
table("Table5", d, r"@{}>{\raggedright\arraybackslash}Xrrrr@{}", [HL("Characteristic"), H("Bicycle"), H("E-bike"), H("E-scooter"), H("All riders")], size=r"\scriptsize", rowfmt=r4, stretch=0.98, place="!tp")
# Table 5 (group size and severe count merged)
d = read("Table4"); c = list(d.columns); d5 = pd.DataFrame({"ID": d[c[0]], "Contrast": d[c[1]], "Population": d[c[2]], "Tier": d[c[3]], "Adjustment set": d[c[4]], "k": d[c[5]],
                                                          "g1": d.iloc[:, 6] + " (" + d.iloc[:, 7] + ")", "g0": d.iloc[:, 8] + " (" + d.iloc[:, 9] + ")"})
table("Table4", d5, r"@{}l>{\raggedright\arraybackslash}p{3.3cm}>{\raggedright\arraybackslash}p{2.9cm}c>{\raggedright\arraybackslash}Xrrr@{}",
      [HL("ID"), HL("Contrast (first-named|vs. reference)"), HL("Population"), H("Tier"), HL("Adjustment set"), H("Covar-|iates"), H("First-named|group, n|(severe)"), H("Reference|group, n|(severe)")], size=r"\scriptsize")
# Table 6
d = read("Table6"); N = r">{\raggedleft\arraybackslash}p{0.92cm}"
table("Table6", d, r"@{}l>{\raggedright\arraybackslash}X" + N * 8 + r">{\raggedleft\arraybackslash}p{1.75cm}@{}",
      [HL("ID"), HL("Contrast"), H("SE,|clustered|(pp)"), H("SE, un-|clustered|(pp)"), H("Ratio"), H("\\textit{p}"), H("\\textit{q}"), H("Propen-|sity|AUC"), H("Outside|trimming|bounds (%)"), H("RVa|(%)"), H("Bounds under|3% confound-|ing (pp)")],
      size=r"\scriptsize", sep="2.5pt")
# Table 7
d = read("Table7"); N = r">{\centering\arraybackslash}p{1.32cm}"
table("Table7", d, r"@{}>{\raggedright\arraybackslash}Xcc" + N * 7 + "@{}",
      [HL("Set of|estimates"), H("Esti-|mates"), H("With|\\textit{q} $<$ 0.05"), H("Same sign,|all"), H("Same sign,|\\textit{q} $<$ 0.05"), H("SHAP within|95% CI"), H("What-if within|95% CI"),
       H("SHAP smaller,|\\textit{q} $<$ 0.05"), H("Median ratio,|\\textit{q} $<$ 0.05"), H("Standardized|difference|beyond $\\pm$1.96")], size=r"\scriptsize", sep="2.5pt")

# ---------------- supplement: generic long tables ----------------
def longtab(tid, landscape, size=r"\scriptsize"):
    df = read(tid); n = df.shape[1]; W = 24.0 if landscape else 16.2
    wid = [max(len(str(cn)) * 0.55, df.iloc[:, j].map(len).quantile(0.9)) for j, cn in enumerate(df.columns)]; wid = [min(max(w, 5), 46) for w in wid]; tot = sum(wid)
    cm = [W * w / tot - 0.25 for w in wid]; text = [not re.fullmatch(r"[\d,.\u2212+\-\s()<%to\u2013/]*", "".join(df.iloc[:, j].head(12))) for j in range(n)]
    spec = "@{}" + "".join((r">{\raggedright\arraybackslash}p{%.2fcm}" if text[j] else r">{\raggedleft\arraybackslash}p{%.2fcm}") % cm[j] for j in range(n)) + "@{}"
    head = " & ".join(r"\raggedright\arraybackslash " + tex(cn) if text[j] else tex(cn) for j, cn in enumerate(df.columns)) + r" \\"
    num = tid.replace("TableS", "S"); body = "\n".join(" & ".join(tex(v) for v in r) + r" \\" for r in df.values)
    s = (size + "\\setlength{\\tabcolsep}{3pt}\\renewcommand{\\arraystretch}{1.05}\n\\begin{longtable}{" + spec + "}\n\\caption{" + tex(META[tid]["title"]) + "}\\label{tab:" + tid.lower() + "}\\\\\n\\toprule\n" + head +
         "\n\\midrule\n\\endfirsthead\n\\multicolumn{" + str(n) + "}{@{}l}{\\textit{Table " + num + " (continued)}}\\\\\n\\toprule\n" + head + "\n\\midrule\n\\endhead\n\\bottomrule\n\\endfoot\n" + body + "\n\\end{longtable}\n" +
         "\\vspace{-6pt}\\noindent" + notes_block(META[tid]["notes"]).replace("\\par\\vspace{3pt}", "") + "\\normalsize\n")
    write(tid, ("\\begin{landscape}\n" + s + "\\end{landscape}\n") if landscape else s + "\\clearpage\n")
for tid, land in (("TableS1", False), ("TableS2", True), ("TableS3", True), ("TableS4", True), ("TableS5", False), ("TableS6", True), ("TableS7", True), ("TableS8", True), ("TableS9", True), ("TableS10", True)): longtab(tid, land)
print("  wrote", len(os.listdir(out)), "table files to", out)
