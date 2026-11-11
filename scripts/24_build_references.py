"""APA 7th reference list for the manuscript, built from the verified reference library.
Usage: python -I 24_build_references.py <literature_dir> <manuscript_dir>
Reads every refs_*.json in <literature_dir> plus cite_aliases.json ({citation key used in the text: key in the library}).
Writes <manuscript_dir>/references.tex (a natbib 'thebibliography' with author-year labels) for the keys cited in *.tex,
and <manuscript_dir>/references.bib as a record. Reports cited keys that are missing from the library."""
import sys, os, re, json, glob, unicodedata
lit, man = sys.argv[1:3]
LIB = {}
for f in sorted(glob.glob(os.path.join(lit, "refs_*.json"))):
    for r in json.load(open(f, encoding="utf-8")): LIB[r["key"]] = r
for r in LIB.values():                                    # byline = individual authors followed by a group name; drop the group members that Crossref lists after it
    au = r["authors"]; g = [i for i, x in enumerate(au) if "literal" in x]
    if g and 0 < g[0] < len(au) - 1: r["authors"] = au[:g[0] + 1]
ALIAS = json.load(open(os.path.join(lit, "cite_aliases.json"), encoding="utf-8")) if os.path.exists(os.path.join(lit, "cite_aliases.json")) else {}
text = "".join(open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(man, "*.tex")) if not os.path.basename(f).startswith(("references", "_", "preamble", "supplementary")))
cited = []
for m in re.finditer(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", text):
    for k in m.group(1).split(","):
        k = k.strip()
        if k and k not in cited: cited.append(k)
missing = [k for k in cited if ALIAS.get(k, k) not in LIB]
PROPER = set("""France French Paris Europe European Germany German Netherlands Dutch China Chinese Finland Finnish Helsinki Norway Norwegian Oslo Denmark Danish Sweden Swedish Switzerland Swiss
United States America American Australia Australian Britain British England London Italy Italian Spain Spanish Austria Austrian Belgium Belgian Japan Japanese Korea Korean Israel Berlin Munich Washington
Texas California Florida Austin Indianapolis Atlanta Los Angeles Rhône Shapley Bayesian Benjamini Hochberg Lyon Bordeaux Marseille Brussels Vienna Zurich Stockholm Copenhagen Singapore Taiwan India Indian
Brazil Canada Canadian Poland Polish Greece Greek Turkey Thailand Bangkok Queensland Victoria Barcelona Madrid Rome Milan Markov Monte Carlo Poisson Gaussian Pearl Tel Aviv Scandinavia Scandinavian Nordic
I Internet COVID-19 Python LightGBM XGBoost TreeSHAP TRIPOD+AI DoubleML""".split())
def esc(s):
    s = str(s)
    for a, b in (("\\", ""), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"), ("$", r"\$"), ("~", r"\textasciitilde{}"), ("^", r"\^{}")): s = s.replace(a, b)
    return re.sub(r"<[^>]+>", "", s)
def sentence_case(t):
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).strip().rstrip(".")
    words = t.split(" "); caps = sum(1 for w in words[1:] if w[:1].isupper() and len(w) > 3); longw = sum(1 for w in words[1:] if len(w) > 3)
    title_case = longw > 0 and caps / longw >= 0.6
    def low(part, first):
        core = re.sub(r"[^\w+]", "", part)
        if first or core in PROPER or core.rstrip("s") in PROPER or re.search(r"[A-Z].*[A-Z]|\d", core): return part
        return part[:1].lower() + part[1:]
    out, new = [], True
    for w in words:
        hyph = "-" in w and all(re.fullmatch(r"[A-Z][a-z]+[^\w]*", x) for x in w.split("-") if x)      # Black-Box, Object-Oriented
        if new: w2 = w[:1].upper() + w[1:]                                                              # first word and first word after a colon
        elif hyph: w2 = "-".join(low(x, False) for x in w.split("-"))
        elif title_case: w2 = low(w, False)
        else: w2 = w
        out.append(w2); new = w.endswith((":", "?", "!"))
    return " ".join(out)
def initials(given):
    parts = re.split(r"\s+", given.strip().replace(".", ". ").strip()); res = []
    for p in parts:
        if not p: continue
        res.append("-".join(x[:1].upper() + "." for x in p.split("-") if x))
    return " ".join(res)
def authors_list(a):
    def one(x): return esc(x["literal"]) if "literal" in x else (esc(x["family"]) + (", " + initials(x.get("given", "")) if x.get("given") else ""))
    names = [one(x) for x in a]
    if len(names) > 20: names = names[:19] + [r"\ldots"] + [names[-1]]; return ", ".join(names[:-2]) + ", " + names[-2] + " " + names[-1]
    if len(names) == 1: return names[0]
    if len(names) == 2: return names[0] + r", \& " + names[1]
    return ", ".join(names[:-1]) + r", \& " + names[-1]
def fam(x):
    """Family name, or the name of a group author; a trailing abbreviation in parentheses is used as the citation label."""
    if "literal" in x:
        m = re.search(r"\(([A-Z][A-Za-z]{1,9})\)\s*$", x["literal"])
        return esc(m.group(1) if m else x["literal"])
    return esc(x["family"])
def label(a, n_names=None):
    if len(a) == 1: return fam(a[0])
    if len(a) == 2: return fam(a[0]) + r" \BBA{} " + fam(a[1])
    if n_names and n_names > 1: return ", ".join(fam(x) for x in a[:n_names]) + (r", et~al." if len(a) > n_names else "")
    return fam(a[0]) + r" et~al."
def doi_url(r):
    if r.get("doi"): return r"\url{https://doi.org/" + r["doi"].strip() + "}"
    return (r"\url{" + r["url"].strip() + "}") if r.get("url") else ""
def pages(r):
    if r.get("pages"): return re.sub(r"\s*[-\u2013\u2014]+\s*", "--", str(r["pages"]))
    return ("Article " + str(r["article_number"])) if r.get("article_number") else ""
def entry(r, year_txt):
    A_ = authors_list(r["authors"]); A_ = A_ if A_.endswith(".") else A_ + "."; t = esc(sentence_case(r["title"])); typ = r.get("type", "article"); c = esc(r.get("container", "") or "")
    tail = doi_url(r); pg = pages(r)
    dot = "" if t.endswith(("?", "!")) else "."
    if typ in ("article", "inproceedings") and c:
        vol = (", \\textit{" + esc(r["volume"]) + "}") if r.get("volume") else ""; iss = ("(" + esc(r["issue"]) + ")") if r.get("issue") and r.get("volume") else ""
        body = f"{t}{dot} \\textit{{{c}}}{vol}{iss}" + (", " + pg if pg else "") + "."
    elif typ == "preprint": body = f"\\textit{{{t}}}{dot} " + (c or "Preprint") + "."
    elif typ == "chapter": body = f"{t}{dot} In \\textit{{{c}}}" + (" (pp. " + pg + ")" if pg else "") + ". " + (esc(r.get("publisher", "")) + "." if r.get("publisher") else "")
    elif typ == "dataset": body = f"\\textit{{{t}}} [Data set]. " + (esc(r.get("publisher", "")) + "." if r.get("publisher") else "")
    elif typ == "software": body = f"\\textit{{{t}}} [Computer software]. " + (esc(r.get("publisher", "")) + "." if r.get("publisher") else "")
    else: body = f"\\textit{{{t}}}. " + (esc(r.get("publisher", "") or c) + "." if (r.get("publisher") or c) else "")
    return f"{A_} ({year_txt}). {body} {tail}".replace("  ", " ").strip()
def skey(r):
    norm = lambda s: unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return ([norm(x.get("literal") or (x["family"] + " " + x.get("given", ""))) for x in r["authors"]], int(r.get("year") or 0), norm(r["title"]))
use = [(k, LIB[ALIAS.get(k, k)]) for k in cited if ALIAS.get(k, k) in LIB]; use.sort(key=lambda kr: skey(kr[1]))
# disambiguation: same label and year -> more names where author lists differ, letters where they are the same
labs = {k: label(r["authors"]) for k, r in use}; yrs = {k: str(r.get("year") or "n.d.") for k, r in use}
groups = {}
for k, r in use: groups.setdefault((labs[k], yrs[k]), []).append(k)
for (lb, y), ks in groups.items():
    if len(ks) < 2: continue
    lists = {k: tuple(fam(x) for x in dict(use)[k]["authors"]) for k in ks}
    if len(set(lists.values())) == len(ks) and all(len(v) > 2 for v in lists.values()):
        n = 2
        while n < 6 and len({v[:n] for v in lists.values()}) < len(ks): n += 1
        for k in ks: labs[k] = label(dict(use)[k]["authors"], n)
    else:
        for i, k in enumerate(ks): yrs[k] = yrs[k] + "abcdefgh"[i]
items = [f"\\bibitem[{{{labs[k]}({yrs[k]})}}]{{{k}}}\n{entry(r, yrs[k])}\n" for k, r in use]
open(os.path.join(man, "references.tex"), "w", encoding="utf-8").write("% Generated by scripts/24_build_references.py from the verified reference library. Do not edit by hand.\n\\begin{thebibliography}{" + str(len(items)) + "}\n\\setlength{\\itemsep}{2pt}\n\n" + "\n".join(items) + "\n\\end{thebibliography}\n")
with open(os.path.join(man, "references.bib"), "w", encoding="utf-8") as fh:
    for k, r in use:
        au = " and ".join(("{" + x["literal"] + "}") if "literal" in x else (x["family"] + ", " + x.get("given", "")) for x in r["authors"])
        fields = dict(author=au, year=r.get("year", ""), title=r["title"], journal=r.get("container", ""), volume=r.get("volume", ""), number=r.get("issue", ""), pages=r.get("pages", "") or r.get("article_number", ""), publisher=r.get("publisher", ""), doi=r.get("doi", ""), url=r.get("url", ""))
        fh.write("@" + {"article": "article", "inproceedings": "inproceedings", "book": "book", "chapter": "incollection"}.get(r.get("type"), "misc") + "{" + k + ",\n" + "".join(f"  {a} = {{{v}}},\n" for a, v in fields.items() if v) + "}\n\n")
print(f"  library {len(LIB)} | cited {len(cited)} | in list {len(items)} | missing {len(missing)}: {missing}")
print("  in library but not cited:", sorted(set(LIB) - {ALIAS.get(k, k) for k in cited})[:60])
