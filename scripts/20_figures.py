"""Figures for Paper 1 (figure-studio 'atlas' palette on white panels).
Usage: python -I 20_figures.py <results_dir> <fig_dir> [--only fig01] [--preview <dir>] [--interim <dir>] [--audit <dir>]"""
import sys, os, textwrap, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "figlib"))
import numpy as np, pandas as pd, matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from scipy.stats import gaussian_kde
import fstudio as F, plots as P, plots_extra as X
ap = argparse.ArgumentParser(); ap.add_argument("res"); ap.add_argument("out"); ap.add_argument("--only", default=""); ap.add_argument("--preview", default="")
ap.add_argument("--interim", default="data/interim"); ap.add_argument("--audit", default="outputs/audit"); ap.add_argument("--geo", default="data/raw/geo/departements.geojson")
args = ap.parse_args()

# ---------- theme: atlas palette, white plotting panels, open frame, light gray grid ----------
F.use_theme("atlas")
WHITE, GRIDC, BAND = "#FFFFFF", "#E5E3DF", "#F4F4F2"
F.PANEL = WHITE; F.GRID = GRIDC
mpl.rcParams.update({"font.weight": "bold", "axes.facecolor": WHITE, "figure.facecolor": WHITE, "savefig.facecolor": WHITE,
                     "axes.spines.left": True, "axes.spines.bottom": True, "axes.edgecolor": F.INK2, "axes.linewidth": 0.8,
                     "xtick.major.size": 3, "ytick.major.size": 3, "grid.color": GRIDC, "grid.linewidth": 0.6})
PET, VER, SAF, TEAL, PUR, ROSE = "#0B4F6C", "#C8321A", "#D98A00", "#0E7C7B", "#5B3A8C", "#A01A58"   # deep variant of the atlas palette
F.C6 = [PET, VER, SAF, TEAL, PUR, ROSE]; F.G0, F.G1 = PET, VER; F.S4 = [PET, VER, SAF, PUR]
F.ORD = ["#F2C36B", "#E89A2B", "#C8321A", "#6E1423"]
F.HEAT = LinearSegmentedColormap.from_list("heat_deep", ["#EEF5F3", "#8CCBC3", "#2A9D97", "#0B4F6C", "#072A44"])
SEV1, SEV0 = ROSE, "#5F5C6B"                                   # severe / non-severe (kept distinct from the mode colors)
MODES = ["bicycle", "ebike", "escooter"]; MODE_LAB = {"bicycle": "Bicycle", "ebike": "E-bike", "escooter": "E-scooter"}
MODE_COL = {"bicycle": PET, "ebike": SAF, "escooter": VER}; MODE_MK = {"bicycle": "o", "ebike": "s", "escooter": "D"}
DIVW = LinearSegmentedColormap.from_list("div_white", ["#0B3C4F", "#2F8AA0", "#FFFFFF", "#E8743F", "#9E2410"])
VAR_LAB = {"LEAK_equip": "Safety equipment", "trip": "Trip purpose", "infra": "Infrastructure", "nbv": "Number of lanes", "manv": "Maneuver", "age": "Age",
           "vma": "Speed limit", "sex": "Sex", "vosp": "Cycle facility", "circ": "Traffic regime", "dep": "Département", "opponent": "Opponent type",
           "catr": "Road category", "urban": "Urban area", "col": "Collision type", "hour": "Hour of day", "mode": "Transport mode", "ped_struck": "Pedestrian struck",
           "prof": "Gradient", "year": "Year", "dow": "Day of week", "choc": "Point of impact", "lum": "Lighting", "month": "Month", "obsm": "Mobile obstacle",
           "obs": "Fixed obstacle", "int_type": "Intersection type", "situ": "Position on road", "n_vehicles": "Vehicles involved", "atm": "Weather",
           "n_passengers": "Passengers", "plan": "Alignment", "surf": "Surface condition"}
TIER_COL = {"tier0": PET, "tier1": TEAL, "tier2": SAF, "tier3": PUR}
TIER_LAB = {"tier0": "Tier 0: time and place", "tier1": "Tier 1: rider and vehicle", "tier2": "Tier 2: road and conditions", "tier3": "Tier 3: crash configuration"}
TIER_HEAD = {"tier1": "Rider and vehicle (Tier 1)", "tier2": "Road and conditions (Tier 2)", "tier3": "Crash configuration (Tier 3)"}
FAC = {"A1": "E-scooter vs. bicycle", "A2": "E-bike vs. bicycle", "D1": "Age 65+ vs. 25–64", "D2": "Male vs. female",
       "B1": "Speed limit ≤30 vs. 50 km/h", "B4": "Cycle facility vs. none", "B5": "Intersection vs. none", "B2": "Night: unlit vs. lit",
       "B3": "Adverse vs. normal conditions", "C1": "Heavy vehicle vs. car opponent", "C2": "Single-vehicle vs. collision", "C3": "Cycle path vs. roadway"}
ORDER = list(FAC)
FTIER = {"A1": "tier1", "A2": "tier1", "D1": "tier1", "D2": "tier1", "B1": "tier2", "B4": "tier2", "B5": "tier2", "B2": "tier2", "B3": "tier2", "C1": "tier3", "C2": "tier3", "C3": "tier3"}
SHORT = {"A1": "E-scooter", "A2": "E-bike", "D1": "Age 65+", "D2": "Male", "B1": "≤30 km/h", "B4": "Cycle facility", "B5": "Intersection", "B2": "Unlit night",
         "B3": "Adverse conditions", "C1": "Heavy vehicle", "C2": "Single vehicle", "C3": "Cycle path"}
HL_DEP = {"75": "Paris", "93": "Seine-Saint-Denis", "92": "Hauts-de-Seine", "94": "Val-de-Marne", "69": "Rhône", "33": "Gironde", "13": "Bouches-du-Rhône"}
_CACHE = {}
def riders():
    if "A" not in _CACHE: _CACHE["A"] = pd.read_parquet(os.path.join(args.interim, "analysis_riders.parquet"))
    return _CACHE["A"]
def audit():
    T = pd.read_csv(os.path.join(args.res, "audit_table.csv")); return T[T["factor"].isin(ORDER)]

def finish(fig, name):
    F.save(fig, os.path.join(args.out, name))
    if args.preview:                                   # low-resolution copy of the final PNG for visual checking
        from PIL import Image
        os.makedirs(args.preview, exist_ok=True); Image.MAX_IMAGE_PIXELS = None
        im = Image.open(os.path.join(args.out, "png", name + ".png")); im.thumbnail((1500, 1900)); im.save(os.path.join(args.preview, name + ".png"))

# ---------- generic helpers ----------
def note(ax, x, y, s, ha="left", va="top", fs=7.0, col=None, data=False, frame=True):
    """Explanatory note inside a panel (white box, thin rule)."""
    return ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=col or F.INK, linespacing=1.22, zorder=9, transform=ax.transData if data else ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.3", fc=WHITE, ec=F.RULE, lw=0.7) if frame else None)
def sgn(v, d=1): return F.minus(f"{v:+.{d}f}")
def pfmt(p): return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"
def wil(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h
def grouped_rows(order, head=0.9, gap=0.3):
    """Row positions (top to bottom) with a header slot before each tier group. Returns y (array) and [(y_header, tier)]."""
    y, heads, cur, last = [], [], 0.0, None
    for f in order:
        t = FTIER[f]
        if t != last:
            if last is not None: cur -= gap
            heads.append((cur, t)); cur -= head; last = t
        y.append(cur); cur -= 1.0
    return np.array(y), heads
def tier_heads(ax, heads, x=0.008, fs=7.2):
    for yh, t in heads:
        ax.text(x, yh, TIER_HEAD[t], transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=fs, color=TIER_COL[t], zorder=8, bbox=dict(fc=WHITE, ec="none", pad=1.2))
def bands(ax, y, h=0.5):
    for yy in y[::2]: ax.axhspan(yy - h, yy + h, color=BAND, lw=0, zorder=0)

# ---------- schematic helpers ----------
def canvas(ax, w, h):
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
def box(ax, x, y, w, h, head, body="", col=None, wrap=26, fs=6.7, head_fs=7.4, head_h=5.0, body_align="left", face=None):
    col = col or PET
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.4", fc=face or F.tint(col, 0.88), ec=col, lw=0.9, zorder=2))
    if head:
        ax.add_patch(FancyBboxPatch((x, y + h - head_h), w, head_h, boxstyle="round,pad=0,rounding_size=1.4", fc=col, ec=col, lw=0.9, zorder=3))
        ax.add_patch(Rectangle((x, y + h - head_h), w, head_h * 0.5, fc=col, ec="none", zorder=3))
        ax.text(x + w / 2, y + h - head_h / 2, head, ha="center", va="center", color="#FFFFFF", fontsize=head_fs, fontweight="bold", zorder=4)
    if body:
        lines = "\n".join(textwrap.fill(p, wrap) for p in body.split("\n"))
        top = y + h - (head_h if head else 0) - 1.6
        if body_align == "center":
            ax.text(x + w / 2, y + (h - (head_h if head else 0)) / 2, lines, ha="center", va="center", fontsize=fs, color=F.INK, linespacing=1.22, zorder=4)
        else:
            ax.text(x + 2.0, top, lines, ha="left", va="top", fontsize=fs, color=F.INK, linespacing=1.22, zorder=4)
def arrow(ax, p0, p1, col=None, lw=1.3, style="-|>", rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=9, lw=lw, color=col or F.INK2, connectionstyle=f"arc3,rad={rad}", linestyle=ls, zorder=5, shrinkA=0, shrinkB=0))

def node(ax, x, y, w, h, title, sub="", col=None, filled=True, fs=7.6, sfs=6.5, r=1.6):
    """Flow-chart node: short title and at most one short second line."""
    col = col or PET; tc = F.text_on(col) if filled else F.INK
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=col if filled else WHITE, ec=col, lw=1.1, zorder=3))
    if sub:
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center", fontsize=fs, color=tc, zorder=4); ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center", fontsize=sfs, color=tc, zorder=4, linespacing=1.1)
    else: ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs, color=tc, zorder=4, linespacing=1.12)
def link(ax, pts, col=None, head=True, lw=1.25):
    """Connector through the given points, with an arrowhead on the last segment."""
    col = col or F.INK2; xs, ys = zip(*pts)
    if len(pts) > 2: ax.plot(xs[:-1], ys[:-1], color=col, lw=lw, solid_capstyle="round", solid_joinstyle="round", zorder=2)
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>" if head else "-", mutation_scale=9, lw=lw, color=col, shrinkA=0, shrinkB=0, zorder=2))

def card(ax, x, y, w, h, title, sub="", col=None, accent="left", filled=False, fs=7.6, sfs=6.5, r=1.4):
    """Flow-chart card: white with a thin outline and one accent bar, or filled for the two key nodes."""
    col = col or PET; ec = col if filled else "#9A97A0"; tc = "#FFFFFF" if filled else F.INK; sc = "#FFFFFF" if filled else F.INK2
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=col if filled else WHITE, ec=ec, lw=0.9, zorder=3))
    if not filled and accent == "left": ax.add_patch(FancyBboxPatch((x, y), 2.2, h, boxstyle=f"round,pad=0,rounding_size={min(r, 1.0)}", fc=col, ec="none", zorder=4))
    if not filled and accent == "top": ax.add_patch(FancyBboxPatch((x, y + h - 2.0), w, 2.0, boxstyle=f"round,pad=0,rounding_size={min(r, 0.9)}", fc=col, ec="none", zorder=4))
    cx = x + w / 2 + (1.1 if (accent == "left" and not filled) else 0); top = 0.66 if accent != "top" or filled else 0.60
    if sub:
        ax.text(cx, y + h * top, title, ha="center", va="center", fontsize=fs, color=tc, zorder=5); ax.text(cx, y + h * 0.28, sub, ha="center", va="center", fontsize=sfs, color=sc, zorder=5, linespacing=1.1)
    else: ax.text(cx, y + h / 2 - (0.6 if accent == "top" and not filled else 0), title, ha="center", va="center", fontsize=fs, color=tc, zorder=5, linespacing=1.12)

def fig01():
    fig = F.new_figure(180, 150); ax = fig.add_subplot(111); W, H = 180, 150; canvas(ax, W, H); ax.set_xlim(-1, 181.5)
    NEU = "#6E6B76"; SOFT = F.tint(PET, 0.80)
    # ---- stage rail ----
    stages = [(138.5, "Data"), (114.5, "Variable\nordering"), (91.5, "Validation\ndesign"), (63.0, "Estimation"), (35.0, "Audit"), (9.5, "Stability")]
    ax.plot([6, 6], [stages[-1][0], stages[0][0]], color=F.RULE, lw=1.8, zorder=1)
    for i, (yc, lab) in enumerate(stages):
        ax.scatter(6, yc, s=170, color=WHITE, ec=PET, lw=1.4, zorder=3); ax.text(6, yc, str(i + 1), ha="center", va="center", fontsize=7.8, color=PET, zorder=4)
        ax.text(11.5, yc, lab, ha="left", va="center", fontsize=7.2, color=F.INK, linespacing=1.1)
    X0 = 32
    # ---- 1 data ----
    ax.text(X0, 148.6, "National police crash files (BAAC), 2019–2025", ha="left", va="center", fontsize=6.8, color=F.INK2)
    for k_, nm_ in enumerate(["Characteristics", "Locations", "Vehicles", "Users"]):
        card(ax, X0 + (k_ % 2) * 27.5, 139.3 - (k_ // 2) * 8.6, 26, 7.2, nm_, col=NEU, fs=6.9, r=1.1)
    link(ax, [(86.5, 138.5), (92.4, 138.5)])
    card(ax, 93, 131.5, 34, 14, "Linked record", "one row per rider", col=PET)
    link(ax, [(127.6, 138.5), (133.4, 138.5)])
    card(ax, 134, 131.5, 46, 14, "Analysis sample", "46,920 riders · 44,817 crashes", col=PET, filled=True)
    link(ax, [(157, 131.0), (157, 126.2), (46, 126.2), (46, 122.2)])
    # ---- 2 variable ordering ----
    tiers = [("Tier 0", "Time and place", PET), ("Tier 1", "Rider and vehicle", TEAL), ("Tier 2", "Road and conditions", SAF), ("Tier 3", "Crash configuration", PUR)]
    x = X0
    for hd, sb, col in tiers:
        card(ax, x, 109, 28, 12.6, hd, sb, col=col, accent="top", sfs=6.3); link(ax, [(x + 28.4, 115.3), (x + 31.6, 115.3)]); x += 32
    card(ax, x, 109, W - x, 12.6, "Outcome", "killed or hospitalized", col=VER, accent="top", sfs=6.1)
    ax.plot([X0, X0 + 124], [106.2, 106.2], color=F.INK2, lw=0.9); ax.plot([X0, X0], [106.2, 107.4], color=F.INK2, lw=0.9); ax.plot([X0 + 124, X0 + 124], [106.2, 107.4], color=F.INK2, lw=0.9)
    ax.text(X0 + 62, 103.6, "Each factor is adjusted only for variables in the same or earlier tiers", ha="center", va="center", fontsize=6.6, color=F.INK2)
    link(ax, [(106, 101.6), (106, 96.4)])
    # ---- 3 validation design (one hue, three depths) ----
    for x_, w_, t_, fc_, tc_ in ((X0, 19, "2019", "#E3E1DC", F.INK), (X0 + 20.5, 80, "2020–2023  ·  development  ·  29,208 riders", SOFT, F.INK), (X0 + 102, 46, "2024–2025  ·  locked test", PET, "#FFFFFF")):
        ax.add_patch(FancyBboxPatch((x_, 87.5), w_, 8.4, boxstyle="round,pad=0,rounding_size=1.0", fc=fc_, ec="none", zorder=3)); ax.text(x_ + w_ / 2, 91.7, t_, ha="center", va="center", fontsize=7.0, color=tc_, zorder=4)
    for xc, t_ in ((X0 + 9.5, "sensitivity"), (X0 + 60.5, "cross-validation grouped by crash"), (X0 + 125, "17,712 riders · evaluated once")): ax.text(xc, 84.9, t_, ha="center", va="center", fontsize=6.4, color=F.INK2)
    link(ax, [(106, 82.6), (106, 78.4)], head=False); ax.plot([56, 157], [78.4, 78.4], color=F.INK2, lw=1.25, solid_capstyle="round", zorder=2)
    link(ax, [(56, 78.4), (56, 73.4)]); link(ax, [(157, 78.4), (157, 73.4)])
    # ---- 4 estimation: predictive branch and causal branch ----
    card(ax, X0, 59, 48, 14, "Prediction", "gradient boosting · logistic regression", col=PET, sfs=6.2)
    link(ax, [(80.4, 66), (85.6, 66)])
    card(ax, 86, 59, 40, 14, "Explanation", "TreeSHAP attributions", col=TEAL)
    card(ax, 134, 59, 46, 14, "Causal estimation", "double machine learning", col=SAF)
    for xc, t_ in ((56, "nine validation protocols"), (106, "stability over 25 refits"), (157, "13 pre-specified factors")): ax.text(xc, 55.4, t_, ha="center", va="center", fontsize=6.4, color=F.INK2)
    link(ax, [(106, 52.6), (106, 43.0)]); link(ax, [(157, 52.6), (157, 35.0), (149.6, 35.0)])
    # ---- 5 audit (the key node) ----
    card(ax, 63, 28, 86, 14, "Audit of SHAP against double machine learning", "agreement in sign · magnitude · rank", col=VER, filled=True, sfs=6.6)
    link(ax, [(106, 27.6), (106, 21.6)], head=False); ax.plot([55, 157], [21.6, 21.6], color=F.INK2, lw=1.25, solid_capstyle="round", zorder=2)
    for xc in (55, 106, 157): link(ax, [(xc, 21.6), (xc, 17.0)])
    # ---- 6 stability of the findings ----
    card(ax, X0, 3, 46, 13.6, "Sources of disagreement", "adjustment set · predictive model", col=NEU, sfs=6.2)
    card(ax, 83, 3, 46, 13.6, "Heterogeneity", "group average effects", col=NEU)
    card(ax, 134, 3, 46, 13.6, "Robustness", "12 checks · unobserved confounding", col=NEU, sfs=6.2)
    finish(fig, "Fig01_methodological_framework")

def fig02():
    A = riders(); M = A[A["year"] >= 2020]
    fig = F.new_figure(180, 172); gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 0.95, 1.0])
    r1 = gs[0].subgridspec(1, 2); r2 = gs[1].subgridspec(1, 2); r3 = gs[2].subgridspec(1, 2, width_ratios=[1.32, 1.0], wspace=0.02)
    # (a) riders by mode and year
    ax = fig.add_subplot(r1[0]); ct = A.groupby(["year", "mode"]).size().unstack()
    ax.axvspan(2018.55, 2019.5, color=BAND, lw=0, zorder=0)
    ax.text(2019.02, 1750, "Codes\nbeing\nadopted", ha="center", va="center", fontsize=6.5, color=F.INK2, linespacing=1.05)
    ends = F.spread(np.log10([ct[m].iloc[-1] for m in MODES]), 0.31)
    for m, ye in zip(MODES, ends):
        X.glow_line(ax, ct.index, ct[m], MODE_COL[m]); X.ring_markers(ax, ct.index, ct[m], MODE_COL[m], s=22)
        ax.text(2025.45, 10 ** ye, f"{MODE_LAB[m]}\n{int(ct[m].iloc[-1]):,}", color=MODE_COL[m], va="center", ha="left", fontsize=7.2, linespacing=1.05)
        ax.text(2020, ct.loc[2020, m] * 0.80, f"{int(ct.loc[2020, m]):,}", color=MODE_COL[m], va="top", ha="center", fontsize=6.8)
    gr = ct.loc[2025] / ct.loc[2020]
    note(ax, 0.985, 0.045, f"Change, 2020 to 2025:\nbicycle ×{gr['bicycle']:.2f}, e-bike ×{gr['ebike']:.1f}, e-scooter ×{gr['escooter']:.1f}", ha="right", va="bottom", fs=6.6)
    F.plain_log(ax, [250, 500, 1000, 2500, 5000], "y"); ax.set_ylim(150, 9500); ax.set_xlim(2018.55, 2027.5); ax.set_xticks(range(2019, 2026))
    ax.set_xlabel("Year of crash"); ax.set_ylabel("Riders in injury crashes\n(logarithmic scale)"); F.ygrid(ax)
    F.panel(fig, ax, "a", "Riders in injury crashes, by year")
    # (b) injury severity composition
    ax = fig.add_subplot(r1[1]); lev = [(2, "Killed", F.ORD[3]), (3, "Hospitalized", F.ORD[2]), (4, "Slightly injured", F.ORD[0]), (1, "Unhurt", "#B8B4AC")]
    comp = pd.crosstab(M["mode"], M["grav"], normalize="index")
    for i, m in enumerate(MODES[::-1]):
        left = 0
        for g, lab, col in lev:
            v = comp.loc[m, g]; ax.barh(i, v, left=left, color=col, ec=WHITE, lw=0.8, height=0.56)
            if v >= 0.06: ax.text(left + v / 2, i, f"{v * 100:.1f}", ha="center", va="center", fontsize=7.4, color=F.text_on(col))
            left += v
        ax.text(0.0, i + 0.33, f"Killed {comp.loc[m, 2] * 100:.1f}%", ha="left", va="bottom", fontsize=6.8, color=F.ORD[3])
        ax.text(1.015, i, f"n = {int((M['mode'] == m).sum()):,}\nKilled or\nhospitalized\n{(comp.loc[m, 2] + comp.loc[m, 3]) * 100:.1f}%", va="center", ha="left", fontsize=6.6, color=F.INK, linespacing=1.1)
    ax.set_yticks(range(3), [MODE_LAB[m] for m in MODES[::-1]]); ax.set_xlim(0, 1.25); ax.set_ylim(-0.5, 2.62); ax.set_xticks([0, .25, .5, .75, 1]); F.pct_axis(ax, "x"); F.clean_left(ax)
    ax.set_xlabel("Share of riders, 2020–2025")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=c, ec="none", label=l) for _, l, c in lev], loc="upper center", bbox_to_anchor=(0.42, -0.25), ncol=4, fontsize=7.2, columnspacing=0.9, handlelength=1.0)
    F.panel(fig, ax, "b", "Injury severity, by transport mode")
    # (c) age distribution by mode
    ax = fig.add_subplot(r2[0]); xs = np.linspace(0, 96, 320)
    for i, m in enumerate(MODES[::-1]):
        d = M.loc[M["mode"] == m, "age"].dropna().values; k = gaussian_kde(d, bw_method=0.16)(xs); k = k / k.max() * 0.86
        ax.fill_between(xs, i, i + k, color=F.tint(MODE_COL[m], 0.35), lw=0, zorder=2); ax.plot(xs, i + k, color=MODE_COL[m], lw=1.5, zorder=3)
        q1, med, q3 = np.percentile(d, [25, 50, 75])
        ax.plot([med, med], [i, i + np.interp(med, xs, k)], color=F.INK, lw=1.1, zorder=4); ax.plot([q1, q3], [i - 0.07] * 2, color=MODE_COL[m], lw=3.0, solid_capstyle="butt", zorder=4)
        ax.text(97, i + 0.60, f"Median {med:.0f} years\n(quartiles {q1:.0f}–{q3:.0f})", ha="right", va="center", fontsize=6.8, color=F.INK, linespacing=1.1)
    ax.set_yticks(range(3), [MODE_LAB[m] for m in MODES[::-1]]); ax.set_ylim(-0.22, 3.0); ax.set_xlim(0, 98); ax.set_xticks(range(0, 91, 10)); F.clean_left(ax); F.ygrid(ax, "x")
    ax.set_xlabel("Rider age (years)")
    F.panel(fig, ax, "c", "Age distribution of riders")
    # (d) time of day
    ax = fig.add_subplot(r2[1])
    for a_, b_ in ((-0.5, 5.5), (21.5, 23.5)): ax.axvspan(a_, b_, color=BAND, lw=0, zorder=0)
    ax.text(2.5, 11.55, "Night", ha="center", va="top", fontsize=6.8, color=F.INK2)
    for m in MODES:
        h = M.loc[M["mode"] == m, "hour"].dropna().astype(int).value_counts(normalize=True).reindex(range(24), fill_value=0) * 100
        X.glow_line(ax, h.index, h.values, MODE_COL[m], lw=1.8, label=MODE_LAB[m]); pk = h.idxmax()
        night = h.loc[[22, 23, 0, 1, 2, 3, 4, 5]].sum(); _CACHE.setdefault("night", {})[m] = night
    nt = _CACHE["night"]
    note(ax, 0.30, 0.965, "Share between 22:00 and 05:59:\n" + ", ".join(f"{MODE_LAB[m].lower()} {nt[m]:.1f}%" for m in MODES), fs=6.5)
    ax.set_xlim(-0.5, 23.5); ax.set_ylim(0, 12); ax.set_xticks(range(0, 24, 3), [f"{h:02d}:00" for h in range(0, 24, 3)]); ax.tick_params(axis="x", labelsize=7.6)
    ax.set_xlabel("Hour of crash"); ax.set_ylabel("Share of riders (%)"); F.ygrid(ax)
    ax.legend(loc="center left", bbox_to_anchor=(0.01, 0.52), fontsize=7.2)
    F.panel(fig, ax, "d", "Distribution of crashes over the day")
    # (e) opponent share and (f) severe outcome by opponent
    opp = M["opponent"].where(M["opponent"].isin(["car", "van", "heavy", "ptw", "single"]), "other")
    cats = ["car", "van", "heavy", "ptw", "other", "single"]
    clab = ["Car", "Van", "Heavy vehicle", "Moped or\nmotorcycle", "Pedestrian, cycle\nor other", "No opponent\n(single vehicle)"]
    yy = np.arange(len(cats))[::-1]
    ax = fig.add_subplot(r3[0]); bands(ax, yy)
    for k, m in enumerate(MODES):
        s = opp[M["mode"] == m].value_counts(normalize=True).reindex(cats, fill_value=0) * 100; off = (1 - k) * 0.29
        ax.barh(yy + off, s.values, height=0.26, color=MODE_COL[m], ec=WHITE, lw=0.5, label=MODE_LAB[m], zorder=3)
        for y_, v in zip(yy + off, s.values): ax.text(v + 1.0, y_, f"{v:.1f}", va="center", ha="left", fontsize=6.1, color=F.INK)
    ax.set_yticks(yy, clab); ax.tick_params(axis="y", labelsize=7.6); ax.set_ylim(-0.6, len(cats) - 0.4); ax.set_xlim(0, 78); F.clean_left(ax); F.ygrid(ax, "x")
    ax.set_xlabel("Share of riders of each mode (%)"); ax.legend(loc="lower right", fontsize=7.2, bbox_to_anchor=(1.0, 0.16))
    F.panel(fig, ax, "e", "Crash opponent, by transport mode")
    ax = fig.add_subplot(r3[1]); bands(ax, yy)
    for k, m in enumerate(MODES):
        off = (1 - k) * 0.29
        for y_, c in zip(yy, cats):
            d = M[(M["mode"] == m) & (opp == c)]
            if len(d) < 50: continue
            p, lo, hi = wil(d["ksi"].sum(), len(d))
            ax.plot([lo * 100, hi * 100], [y_ + off] * 2, color=MODE_COL[m], lw=1.8, alpha=0.85, zorder=2)
            ax.scatter(p * 100, y_ + off, s=30, marker=MODE_MK[m], color=MODE_COL[m], ec=WHITE, lw=0.8, zorder=4)
            ax.text(hi * 100 + 1.2, y_ + off, f"{p * 100:.0f}", va="center", ha="left", fontsize=6.1, color=F.INK)
    ax.axvline(M["ksi"].mean() * 100, color=F.INK2, lw=0.9, ls=(0, (4, 3)), zorder=1); ax.text(77, 1.5, "Dashed line:\nall riders, 25.0%", fontsize=6.6, color=F.INK2, va="center", ha="right", linespacing=1.1)
    ax.set_yticks(yy, [""] * len(cats)); ax.set_ylim(-0.6, len(cats) - 0.4); ax.set_xlim(0, 78); F.clean_left(ax); F.ygrid(ax, "x")
    ax.set_xlabel("Killed or hospitalized (%, 95% CI)")
    F.panel(fig, ax, "f", "Severe outcome, by opponent")
    finish(fig, "Fig02_descriptive_overview")

def fig_recording():
    A = riders(); M = A[A["year"] >= 2020]
    C = pd.read_csv(os.path.join(args.audit, "outcome_dependent_recording.csv"))
    w = C.pivot(index="feature", columns="mode", values="diff"); order = w.abs().max(axis=1).sort_values(ascending=False).index
    top = list(order[:10])
    unk = lambda D, f: (D[f] == "unknown") if f == "LEAK_equip" else D[f].isna()
    fig = F.new_figure(180, 225); gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 0.74, 0.80])
    g1 = gs[0].subgridspec(1, 3); g3 = gs[2].subgridspec(1, 2, width_ratios=[1.0, 1.12])
    for j, m in enumerate(MODES):
        ax = fig.add_subplot(g1[j]); c = C[C["mode"] == m].set_index("feature").loc[top]; n = len(top); bands(ax, np.arange(n)[::-1])
        for r, f in enumerate(top):
            y = n - 1 - r; a, b = c.loc[f, "unk_not_severe"] / 100, c.loc[f, "unk_severe"] / 100
            ax.plot([a, b], [y, y], color="#A9A59D", lw=4.5, solid_capstyle="butt", zorder=1)
            ax.scatter(a, y, s=40, color=SEV0, ec=WHITE, lw=1, zorder=3); ax.scatter(b, y, s=40, color=SEV1, ec=WHITE, lw=1, zorder=3)
            big = abs(b - a) >= 0.10
            ax.text(max(a, b) + 0.035, y, sgn((b - a) * 100), va="center", ha="left", fontsize=7.2, color=SEV1 if big else F.INK)
        ax.set_yticks(range(n), [VAR_LAB[f] for f in top][::-1] if j == 0 else [""] * n); ax.set_ylim(-0.6, n - 0.4); ax.set_xlim(-0.03, 0.90)
        ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8]); F.pct_axis(ax, "x"); F.clean_left(ax); F.ygrid(ax, "x"); ax.set_xlabel("Share recorded as unknown")
        F.panel(fig, ax, "abc"[j], f"{MODE_LAB[m]} (n = {int((M['mode'] == m).sum()):,})")
    fig.axes[2].legend(handles=[Line2D([], [], marker="o", ls="", color=SEV0, mec=WHITE, ms=6.2, label="Slightly injured\nor unhurt"),
                               Line2D([], [], marker="o", ls="", color=SEV1, mec=WHITE, ms=6.2, label="Killed or\nhospitalized")],
                      loc="center right", fontsize=7.2, bbox_to_anchor=(1.0, 0.42), labelspacing=0.6, frameon=True, facecolor=WHITE, edgecolor=F.RULE)
    # (d) difference against the pre-specified thresholds
    ax = fig.add_subplot(gs[1]); feats = list(order[:18]); x = np.arange(len(feats))
    ax.axhspan(-40, -10, color=F.tint(ROSE, 0.78), lw=0, zorder=0); ax.axhspan(10, 40, color=F.tint(ROSE, 0.78), lw=0, zorder=0)
    ax.axhspan(-10, -5, color=F.tint(SAF, 0.70), lw=0, zorder=0); ax.axhspan(5, 10, color=F.tint(SAF, 0.70), lw=0, zorder=0)
    ax.axhline(0, color=F.INK2, lw=0.9)
    for k, m in enumerate(MODES):
        ax.scatter(x + (k - 1) * 0.2, w.loc[feats, m], s=36, color=MODE_COL[m], ec=WHITE, lw=0.9, zorder=3, label=MODE_LAB[m], marker=MODE_MK[m])
    ax.set_xticks(x, [VAR_LAB[f] for f in feats]); F.rotate(ax, 32); ax.tick_params(axis="x", labelsize=7.8); ax.set_ylim(-31, 13); ax.set_xlim(-0.6, len(feats) - 0.4)
    ax.set_ylabel("Difference in unknown rate\n(severe minus non-severe, points)"); F.ygrid(ax)
    ax.text(len(feats) - 0.5, -20, "Excluded from all models (difference of 10 points or more)", ha="right", va="center", fontsize=7.2, color=F.INK)
    ax.text(len(feats) - 0.5, -7.5, "Examined in a sensitivity analysis (5 to 10 points)", ha="right", va="center", fontsize=7.2, color=F.INK)
    ax.legend(loc="lower left", ncol=3, fontsize=7.4, bbox_to_anchor=(0.10, 0.02))
    F.panel(fig, ax, "d", "Difference in the unknown rate against the pre-specified thresholds")
    # (e) safety equipment: unknown rate by year, severity and mode
    ax = fig.add_subplot(g3[0]); yrs = list(range(2020, 2026)); u = unk(M, "LEAK_equip")
    for m in MODES:
        for sv, ls in ((1, "-"), (0, (0, (3, 2)))):
            k = (M["mode"] == m) & (M["ksi"] == sv); s = u[k].groupby(M.loc[k, "year"]).mean() * 100
            ax.plot(s.index, s.values, color=MODE_COL[m], lw=1.7, ls=ls, marker=MODE_MK[m], ms=4.2, mec=WHITE, mew=0.7, zorder=3)
    ax.set_xticks(yrs); ax.set_xlim(2019.7, 2025.3); ax.set_ylim(0, 100); ax.set_xlabel("Year of crash"); ax.set_ylabel("Safety equipment recorded\nas unknown (%)"); F.ygrid(ax)
    ax.legend(handles=[Line2D([], [], color=MODE_COL[m], marker=MODE_MK[m], mec=WHITE, ms=5, lw=1.6, label=MODE_LAB[m]) for m in MODES] +
              [Line2D([], [], color=F.INK2, lw=1.6, label="Killed or hospitalized"), Line2D([], [], color=F.INK2, lw=1.6, ls=(0, (3, 2)), label="Slightly injured or unhurt")],
              loc="upper center", ncol=2, fontsize=6.8, columnspacing=1.0, handlelength=2.2)
    F.panel(fig, ax, "e", "Safety equipment: unknown rate over time")
    # (f) unknown rate by variable and year (all riders)
    ax = fig.add_subplot(g3[1]); rows = top[:8]
    Z = np.array([[unk(M[M["year"] == yv], f).mean() * 100 for yv in yrs] for f in rows])
    im = ax.imshow(Z, cmap=F.HEAT, vmin=0, vmax=60, aspect="auto")
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            ax.text(j, i, f"{Z[i, j]:.1f}", ha="center", va="center", fontsize=7.0, color=F.text_on(mpl.colors.to_hex(F.HEAT(min(Z[i, j] / 60, 1)))))
    ax.set_xticks(range(len(yrs)), yrs); ax.set_yticks(range(len(rows)), [VAR_LAB[f] for f in rows]); ax.tick_params(length=0, labelsize=7.8)
    [sp.set_visible(False) for sp in ax.spines.values()]
    ax.set_xticks(np.arange(-.5, len(yrs)), minor=True); ax.set_yticks(np.arange(-.5, len(rows)), minor=True); ax.grid(which="minor", color=WHITE, lw=1.4); ax.tick_params(which="minor", length=0); ax.grid(which="major", visible=False)
    ax.set_xlabel("Year of crash")
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02); cb.set_label("Recorded as unknown (%)", fontsize=7.6); cb.outline.set_visible(False); cb.ax.tick_params(labelsize=7.2, length=2)
    F.panel(fig, ax, "f", "Unknown rate by variable and year")
    finish(fig, "Fig04_outcome_dependent_recording")

def fig_performance():
    from sklearn.metrics import roc_curve, precision_recall_curve
    T = pd.read_parquet(os.path.join(args.res, "test_predictions.parquet")); L = pd.read_csv(os.path.join(args.res, "leakage_protocols.csv"))
    Mx = pd.read_csv(os.path.join(args.res, "test_metrics.csv")).set_index(["model", "group"])
    fig = F.new_figure(180, 225); gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 0.86, 1.12])
    top = gs[0].subgridspec(1, 3); mid = gs[1].subgridspec(1, 2, width_ratios=[1.2, 1.0]); bot = gs[2].subgridspec(1, 2, width_ratios=[1.75, 1.0], wspace=0.02)
    GR = [("all", "All riders", F.INK)] + [(m, MODE_LAB[m], MODE_COL[m]) for m in MODES]
    sub = lambda g: T if g == "all" else T[T["mode"] == g]
    # (a) discrimination by mode
    ax = fig.add_subplot(top[0]); ax.plot([0, 1], [0, 1], color=F.INK2, lw=0.9, ls=(0, (4, 3)))
    for g, lab, col in GR:
        d = sub(g); f, t, _ = roc_curve(d["ksi"], d["p_lgbm"]); r = Mx.loc[("LightGBM", g)]
        ll = f"{lab}: {r['roc_auc']:.3f} ({r['roc_auc_lo']:.3f}–{r['roc_auc_hi']:.3f})"
        if g == "all": ax.plot(f, t, color=col, lw=1.3, ls=(0, (1, 1.2)), label=ll, zorder=4)
        else: X.glow_line(ax, f, t, col, lw=1.7, label=ll)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.005); ax.set_xlabel("False-positive rate"); ax.set_ylabel("True-positive rate"); F.ygrid(ax, "both")
    ax.legend(loc="lower right", fontsize=6.0, title="Area under the curve (95% CI)", title_fontsize=6.2, handlelength=1.2, borderaxespad=0.2)
    F.panel(fig, ax, "a", "ROC curves")
    # (b) precision-recall by mode
    ax = fig.add_subplot(top[1])
    for g, lab, col in GR:
        d = sub(g); pr, rc, _ = precision_recall_curve(d["ksi"], d["p_lgbm"]); r = Mx.loc[("LightGBM", g)]
        ll = f"{lab}: {r['pr_auc']:.3f} ({r['pr_auc_lo']:.3f}–{r['pr_auc_hi']:.3f})"
        if g == "all": ax.plot(rc, pr, color=col, lw=1.3, ls=(0, (1, 1.2)), label=ll, zorder=4)
        else:
            X.glow_line(ax, rc, pr, col, lw=1.7, label=ll)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.005); ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); F.ygrid(ax, "both")
    ax.legend(loc="lower left", fontsize=6.0, title="Area under the curve (95% CI)", title_fontsize=6.2, handlelength=1.2, borderaxespad=0.2)
    F.panel(fig, ax, "b", "Precision–recall curves")
    # (c) calibration, locked test
    ax = fig.add_subplot(top[2]); ax.plot([0, 1], [0, 1], color=F.INK2, lw=0.9, ls=(0, (4, 3)))
    for nm, col, mk, c in (("Gradient boosting", TEAL, "o", "p_lgbm"), ("Logistic regression", PUR, "s", "p_logit")):
        q = pd.qcut(T[c], 10, labels=False, duplicates="drop"); xs = T[c].groupby(q).mean(); ys = T["ksi"].groupby(q).mean()
        X.glow_line(ax, xs, ys, col, lw=1.6, label=nm); ax.scatter(xs, ys, s=24, color=col, ec=WHITE, lw=0.9, marker=mk, zorder=6)
    a, b = Mx.loc[("LightGBM", "all")], Mx.loc[("Logistic", "all")]
    note(ax, 0.975, 0.03, "Slope; intercept; Brier score\n" + f"Boosting: {a['cal_slope']:.2f}; " + sgn(a['cal_intercept'], 2) + f"; {a['brier']:.3f}\n" +
         f"Logistic: {b['cal_slope']:.2f}; " + sgn(b['cal_intercept'], 2) + f"; {b['brier']:.3f}", ha="right", va="bottom", fs=6.0)
    ax.set_xlim(0, 0.9); ax.set_ylim(0, 0.9); ax.set_xlabel("Predicted probability"); ax.set_ylabel("Observed proportion"); F.ygrid(ax, "both")
    ax.legend(loc="upper left", fontsize=6.6, handlelength=1.3)
    F.panel(fig, ax, "c", "Calibration")
    # (d) distribution of predicted probabilities by observed outcome
    ax = fig.add_subplot(mid[0]); names = [g[1] for g in GR]
    left = {lab: sub(g).loc[sub(g)["ksi"] == 0, "p_lgbm"].values for g, lab, _ in GR}; right = {lab: sub(g).loc[sub(g)["ksi"] == 1, "p_lgbm"].values for g, lab, _ in GR}
    X.split_violin(ax, names, left, right, colors=(SEV0, SEV1), width=0.42, bw=0.2)
    for i, lab in enumerate(names):
        ax.text(i - 0.03, 1.03, f"{np.median(left[lab]):.2f}", ha="right", va="bottom", fontsize=6.6, color=SEV0); ax.text(i + 0.03, 1.03, f"{np.median(right[lab]):.2f}", ha="left", va="bottom", fontsize=6.6, color=SEV1)
    ax.set_ylim(0, 1.12); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); ax.set_xlim(-0.6, 3.6); ax.set_ylabel("Predicted probability")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=F.tint(SEV0, 0.30), ec=SEV0, label="Slightly injured or unhurt"), plt.Rectangle((0, 0), 1, 1, fc=F.tint(SEV1, 0.30), ec=SEV1, label="Killed or hospitalized")],
              loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, fontsize=7.0, handlelength=1.1, columnspacing=1.2)
    F.panel(fig, ax, "d", "Predicted probability by outcome")
    # (e) decision curve
    ax = fig.add_subplot(mid[1]); yv = T["ksi"].values; ts = np.linspace(0.02, 0.80, 120); prev = yv.mean()
    ax.plot(ts, prev - (1 - prev) * ts / (1 - ts), color=F.INK2, lw=1.1, ls=(0, (4, 2)), label="Classify all riders as severe"); ax.axhline(0, color=F.INK, lw=0.9)
    for nm, c, col, ls in (("Gradient boosting", "p_lgbm", TEAL, "-"), ("Logistic regression", "p_logit", PUR, (0, (5, 1.5)))):
        p = T[c].values; nb = [((p >= t) & (yv == 1)).mean() - ((p >= t) & (yv == 0)).mean() * t / (1 - t) for t in ts]
        ax.plot(ts, nb, color=col, lw=1.7, ls=ls, label=nm)
    ax.set_ylim(-0.03, prev * 1.08); ax.set_xlim(0, 0.82); ax.set_xlabel("Threshold probability"); ax.set_ylabel("Net benefit"); F.ygrid(ax)
    ax.legend(loc="upper right", fontsize=6.8, handlelength=2.0)
    F.panel(fig, ax, "e", "Decision-curve analysis")
    # (f, g) validation protocols
    idx = [0, 1, 2, 3, 4, 6, 7, 8, 5]
    lab = ["Random split of riders,\nglobal preprocessing", "As above, plus outcome-\ndependent variables", "Oversampling before\nthe random split",
           "Grouped by crash,\n2020–2025", "Grouped by crash,\n2020–2023", "Forward chaining:\nvalidation on 2021", "Forward chaining:\nvalidation on 2022",
           "Forward chaining:\nvalidation on 2023", "Forward in time:\nlocked test, 2024–2025"]
    P9 = L.iloc[idx].reset_index(drop=True); n9 = len(P9); y = np.arange(n9)[::-1]; cols = [PET, SAF, SAF, PET, PET, TEAL, TEAL, TEAL, VER]
    for k, (col_, xl, ref, lim, ttl, fmt) in enumerate((("roc_auc", "Area under the ROC curve", P9.loc[n9 - 1, "roc_auc"], (0.80, 0.878), "Discrimination under nine validation protocols", "{:.3f}"),
                                                        ("cal_slope", "Calibration slope", 1.0, (0.85, 1.20), "Calibration slope", "{:.2f}"))):
        ax = fig.add_subplot(bot[k]); v = P9[col_].values; bands(ax, y)
        ax.axvline(ref, color=F.INK2, lw=0.9, ls=(0, (4, 3)), zorder=1)
        ax.hlines(y, ref, v, color=cols, lw=2.6, alpha=0.75, zorder=2); ax.scatter(v, y, s=52, color=cols, ec=WHITE, lw=1.1, zorder=3)
        for yy, vv in zip(y, v):
            ax.text(vv + (lim[1] - lim[0]) * 0.045 * (1 if vv >= ref else -1), yy, fmt.format(vv), va="center", ha="left" if vv >= ref else "right", fontsize=7.4)
        ax.set_yticks(y, lab if k == 0 else [""] * n9); ax.tick_params(axis="y", labelsize=7.6); ax.set_ylim(-0.6, n9 - 0.4); ax.set_xlim(*lim); ax.set_xlabel(xl); F.clean_left(ax); F.ygrid(ax, "x")
        if k == 0:
            for yy, n_ in zip(y, P9["n"]): ax.text(lim[0] + 0.0008, yy, f"n = {int(n_):,}", va="center", ha="left", fontsize=6.6, color=F.INK2)
            fig.legend(handles=[Line2D([], [], marker="o", ls="", color=c, mec=WHITE, ms=6.2, label=l) for c, l in
                                ((PET, "Cross-validation"), (SAF, "Cross-validation with a known source of leakage"), (TEAL, "Forward chaining"), (VER, "Locked test set"))],
                       loc="outside lower center", ncol=4, fontsize=7.4, columnspacing=1.2, handletextpad=0.2)
        F.panel(fig, ax, "fg"[k], ttl)
    finish(fig, "Fig05_validation_performance")

SHAPC = LinearSegmentedColormap.from_list("shap_like", ["#0B4F6C", "#5B3A8C", "#C8321A"])
def fig_shap():
    import json
    A = riders(); A = A[A["year"] >= 2020].reset_index(drop=True)
    I = pd.read_csv(os.path.join(args.res, "shap_importance_test.csv"), index_col=0); St = pd.read_csv(os.path.join(args.res, "shap_stability.csv"), index_col=0)
    S = pd.read_parquet(os.path.join(args.res, "oof_shap.parquet")); SS = json.load(open(os.path.join(args.res, "shap_stability_summary.json")))
    spec = json.load(open(os.path.join(args.interim, "feature_spec.json"))); CAT = set(spec["categorical"])
    top = list(I.index[:15]); n = len(top); y = np.arange(n)[::-1]; rng = np.random.default_rng(20261111)
    fig = F.new_figure(180, 225); gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.12, 0.84])
    g1 = gs[0].subgridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.03); g2 = gs[1].subgridspec(1, 3, width_ratios=[1.45, 1.0, 1.12]); g3 = gs[2].subgridspec(1, 2, width_ratios=[1.0, 1.0])
    # (a) global importance, with mode-specific values
    ax = fig.add_subplot(g1[0]); v = I.loc[top, "mean_abs_shap_logodds"].values; cols = [TIER_COL[t] for t in I.loc[top, "tier"]]; bands(ax, y)
    ax.barh(y, v, height=0.52, color=[F.tint(c, 0.15) for c in cols], ec="none", zorder=2)
    for m in MODES: ax.scatter(I.loc[top, m].values, y, s=15, marker=MODE_MK[m], fc=WHITE, ec=MODE_COL[m], lw=1.0, zorder=4)
    for yy, vv, f in zip(y, v, top): ax.text(max(vv, I.loc[f, MODES].max()) + 0.018, yy, f"{vv:.2f}", va="center", fontsize=7.2)
    ax.set_yticks(y, [VAR_LAB[f] for f in top]); ax.tick_params(axis="y", labelsize=8.0); ax.set_ylim(-0.7, n - 0.3); ax.set_xlim(0, 0.90); F.clean_left(ax); F.ygrid(ax, "x")
    ax.set_xlabel("Mean absolute SHAP value (log-odds), locked test set")
    sh = I.groupby("tier")["mean_abs_shap_logodds"].sum(); sh = sh / sh.sum() * 100
    ia = ax.inset_axes([0.37, 0.07, 0.61, 0.50]); ia.set_facecolor(WHITE); left = 0
    for t in TIER_COL:
        ia.barh(0, sh[t], left=left, color=TIER_COL[t], ec=WHITE, lw=0.8, height=0.5); ia.text(left + sh[t] / 2, 0, f"{sh[t]:.0f}%", ha="center", va="center", fontsize=7.0, color=F.text_on(TIER_COL[t])); left += sh[t]
    ia.set_xlim(0, 100); ia.set_ylim(-2.75, 0.8); ia.axis("off"); ia.text(0, 0.36, "Share of total attribution (all 32 variables)", fontsize=6.8, va="bottom", ha="left", color=F.INK)
    for i, t in enumerate(TIER_COL):
        ia.scatter(2.5 + (i % 2) * 55, -0.72 - (i // 2) * 0.55, s=24, marker="s", color=TIER_COL[t], lw=0); ia.text(6 + (i % 2) * 55, -0.72 - (i // 2) * 0.55, TIER_LAB[t], fontsize=6.0, va="center", ha="left", color=F.INK)
    ia.text(0, -1.95, "Bars: all riders. Open markers: riders of each mode", fontsize=6.3, va="center", ha="left", color=F.INK)
    for i, m in enumerate(MODES):
        ia.scatter(2.5 + i * 30, -2.48, s=17, marker=MODE_MK[m], fc=WHITE, ec=MODE_COL[m], lw=1.0); ia.text(6 + i * 30, -2.48, MODE_LAB[m], fontsize=6.3, va="center", ha="left", color=F.INK)
    F.panel(fig, ax, "a", "Global importance of the fifteen leading variables")
    # (b) rank stability over 25 refits
    ax = fig.add_subplot(g1[1]); st = St.loc[top]; bands(ax, y)
    ax.hlines(y, st["rank_min"], st["rank_max"], color=cols, lw=5.5, alpha=0.70, zorder=2, capstyle="round")
    ax.scatter(st["rank_median"], y, s=44, color=cols, ec=WHITE, lw=1.1, zorder=3)
    ax.set_yticks(y, [""] * n); ax.set_ylim(-0.7, n - 0.3); ax.set_xlim(0.2, 23.5); ax.set_xticks([1, 5, 10, 15, 20]); F.clean_left(ax); F.ygrid(ax, "x")
    ax.set_xlabel("Importance rank across 25 refits\n(median and range)")
    note(ax, 0.975, 0.975, f"Rank correlation between refits\n(Kendall τ): mean {SS['kendall_tau_mean']:.2f}, minimum {SS['kendall_tau_min']:.2f}\nOverlap of the ten leading variables\n(Jaccard): mean {SS['top10_jaccard_mean']:.2f}", ha="right", fs=6.3)
    F.panel(fig, ax, "b", "Stability of the ranking")
    # (c) SHAP summary plot (beeswarm) for the twelve leading variables
    ax = fig.add_subplot(g2[0]); t12 = top[:12]; sel = rng.choice(len(S), 6000, replace=False); width = 0.36
    for row, f in enumerate(t12[::-1]):
        sv = S[f].values[sel]
        if f in CAT: fv = A[f].map(A.groupby(f)["ksi"].mean()).values[sel]      # categories ordered by their share of severe outcomes
        else: fv = A[f].astype(float).values[sel]
        ok = ~np.isnan(fv); rank = np.full(len(sv), np.nan); rank[ok] = (np.argsort(np.argsort(fv[ok])) + 0.5) / ok.sum()
        if len(np.unique(fv[ok])) <= 12:                                         # few levels: color by level, not by rank
            lv = np.unique(fv[ok]); rank[ok] = np.searchsorted(lv, fv[ok]) / max(len(lv) - 1, 1)
        edges = np.linspace(sv.min(), sv.max() + 1e-9, 61); b = np.clip(np.digitize(sv, edges) - 1, 0, 59); off = np.zeros(len(sv)); cmax = np.bincount(b).max()
        for k in np.unique(b):
            idx = np.where(b == k)[0]; idx = idx[rng.permutation(len(idx))]; s_ = width * np.sqrt(len(idx) / cmax); off[idx] = np.linspace(-s_, s_, len(idx)) if len(idx) > 1 else 0
        if (~ok).any(): ax.scatter(sv[~ok], row + off[~ok], color="#8F8B83", s=2.6, lw=0, rasterized=True, zorder=2)
        ax.scatter(sv[ok], row + off[ok], c=rank[ok], cmap=SHAPC, vmin=0, vmax=1, s=2.6, lw=0, rasterized=True, zorder=3)
    ax.axvline(0, color=F.INK2, lw=0.8, zorder=1); ax.set_yticks(range(len(t12)), [VAR_LAB[f] + ("†" if f in CAT else "") for f in t12[::-1]]); ax.tick_params(axis="y", labelsize=7.8)
    ax.set_ylim(-0.7, len(t12) - 0.3); ax.set_xlim(-2.6, 2.6); F.clean_left(ax); F.ygrid(ax, "x"); ax.set_xlabel("SHAP value (log-odds of a severe outcome)")
    cax = ax.inset_axes([0.66, 0.045, 0.30, 0.022]); cb = fig.colorbar(mpl.cm.ScalarMappable(cmap=SHAPC), cax=cax, orientation="horizontal")
    cb.set_ticks([0, 1], labels=["Low", "High"]); cb.ax.tick_params(labelsize=6.6, length=0, pad=1); cb.outline.set_visible(False); cax.set_title("Variable value", fontsize=6.6, pad=2, color=F.INK)
    F.panel(fig, ax, "c", "SHAP summary plot")
    # (d) age and (e) speed limit: SHAP dependence plots, with the number of riders beneath
    sub = rng.choice(len(S), 9000, replace=False)
    sp = g2[1].subgridspec(2, 1, height_ratios=[4, 0.7], hspace=0.04); ax = fig.add_subplot(sp[0]); axn = fig.add_subplot(sp[1], sharex=ax); bins = np.arange(5, 91, 5)
    ax.scatter(A["age"].values[sub] + rng.uniform(-0.4, 0.4, len(sub)), S["age"].values[sub], c=[MODE_COL[m] for m in A["mode"].values[sub]], s=2.2, alpha=0.38, lw=0, rasterized=True, zorder=2)
    for m in MODES:
        k = (A["mode"] == m).values & A["age"].notna().values; b = pd.cut(A.loc[k, "age"], bins); g = S.loc[k, "age"].groupby(b.values, observed=True)
        mu, cnt = g.mean(), g.size(); ok = cnt >= 40; xs = np.array([iv.mid for iv in mu.index])[ok.values]
        X.glow_line(ax, xs, mu[ok].values, MODE_COL[m], lw=1.7, label=MODE_LAB[m])
    cnt = pd.cut(A["age"], bins).value_counts().sort_index(); axn.bar([iv.mid for iv in cnt.index], cnt.values, width=4.2, color="#A9A59D", lw=0)
    ax.axhline(0, color=F.INK2, lw=0.8); ax.set_ylabel("SHAP value (log-odds)"); F.ygrid(ax); ax.set_xlim(5, 90); ax.set_ylim(-0.75, 1.75); ax.tick_params(axis="x", labelbottom=False, length=0)
    axn.set_yticks([]); axn.spines["left"].set_visible(False); axn.set_xlabel("Rider age (years)"); axn.text(0.985, 0.9, "Riders", transform=axn.transAxes, ha="right", va="top", fontsize=6.2, color=F.INK2)
    ax.legend(loc="upper left", fontsize=6.8, title="Points: riders\nLines: mean by mode", title_fontsize=6.4, handlelength=1.3)
    F.panel(fig, ax, "d", "Age dependence")
    sp = g2[2].subgridspec(2, 1, height_ratios=[4, 0.7], hspace=0.04); ax = fig.add_subplot(sp[0]); axn = fig.add_subplot(sp[1], sharex=ax); lims = [30, 50, 70, 80, 90]
    pos = A["vma"].map({l: i for i, l in enumerate(lims)}).values[sub]; okp = ~np.isnan(pos); mo = pd.Series(A["mode"].values[sub]).map({m: (j - 1) * 0.22 for j, m in enumerate(MODES)}).values
    ax.scatter(pos[okp] + mo[okp] + rng.uniform(-0.09, 0.09, okp.sum()), S["vma"].values[sub][okp], c=[MODE_COL[m] for m in A["mode"].values[sub][okp]], s=2.2, alpha=0.38, lw=0, rasterized=True, zorder=2)
    for j, m in enumerate(MODES):
        k = (A["mode"] == m).values; g = S.loc[k, "vma"].groupby(A.loc[k, "vma"].values); mu, cnt = g.mean(), g.size()
        xs = [i for i, l in enumerate(lims) if l in mu.index and cnt[l] >= 40]; ys = [mu[lims[i]] for i in xs]
        X.glow_line(ax, xs, ys, MODE_COL[m], lw=1.7); ax.scatter(xs, ys, s=24, color=MODE_COL[m], ec=WHITE, lw=0.9, zorder=6, marker=MODE_MK[m])
    cn = A["vma"].value_counts(); axn.bar(range(len(lims)), [cn.get(l, 0) for l in lims], width=0.6, color="#A9A59D", lw=0)
    ax.axhline(0, color=F.INK2, lw=0.8); ax.set_xlim(-0.5, len(lims) - 0.5); ax.set_ylim(-0.5, 1.0); ax.set_ylabel("SHAP value (log-odds)"); F.ygrid(ax); ax.tick_params(axis="x", labelbottom=False, length=0)
    axn.set_yticks([]); axn.spines["left"].set_visible(False); axn.set_xticks(range(len(lims)), [str(l) for l in lims]); axn.set_xlabel("Speed limit (km/h)"); axn.text(0.985, 0.9, "Riders", transform=axn.transAxes, ha="right", va="top", fontsize=6.2, color=F.INK2)
    F.panel(fig, ax, "e", "Speed-limit dependence")
    # (f) opponent type
    OL = {"heavy": "Heavy vehicle", "single": "No opponent", "rail": "Tram or train", "van": "Van", "car": "Car", "ptw": "Moped or motorcycle", "other": "Other vehicle", "cycle": "Bicycle", "edp": "Mobility device", "pedestrian": "Pedestrian"}
    ax = fig.add_subplot(g3[0]); mu = S["opponent"].groupby(A["opponent"].values).mean().sort_values(); cn = A["opponent"].value_counts(); mu = mu[cn[mu.index] >= 150]; yy = np.arange(len(mu)); bands(ax, yy)
    ax.axvline(0, color=F.INK2, lw=0.8)
    for k, m in enumerate(MODES):
        km = (A["mode"] == m).values; g = S.loc[km, "opponent"].groupby(A.loc[km, "opponent"].values); mm_, cc = g.mean(), g.size(); off = (1 - k) * 0.24
        for y_, c in zip(yy, mu.index):
            if c in mm_.index and cc[c] >= 40: ax.scatter(mm_[c], y_ + off, s=26, marker=MODE_MK[m], color=MODE_COL[m], ec=WHITE, lw=0.8, zorder=4)
    ax.set_yticks(yy, [OL[c] for c in mu.index]); ax.tick_params(axis="y", labelsize=7.4); ax.set_ylim(-0.6, len(mu) - 0.4); F.clean_left(ax); F.ygrid(ax, "x"); ax.set_xlabel("Mean SHAP value (log-odds)")
    F.panel(fig, ax, "f", "Attribution by opponent")
    # (g) hour of day
    ax = fig.add_subplot(g3[1])
    for a_, b_ in ((-0.5, 5.5), (21.5, 23.5)): ax.axvspan(a_, b_, color=BAND, lw=0, zorder=0)
    for m in MODES:
        km = (A["mode"] == m).values & A["hour"].notna().values; g = S.loc[km, "hour"].groupby(A.loc[km, "hour"].astype(int).values); mm_, cc = g.mean(), g.size(); ok = cc >= 40
        hh_ = mm_.where(ok).reindex(range(24)); X.glow_line(ax, hh_.index, hh_.values, MODE_COL[m], lw=1.6)
    ax.axhline(0, color=F.INK2, lw=0.8); ax.set_xlim(-0.5, 23.5); ax.set_xticks(range(0, 24, 6), [f"{h:02d}:00" for h in range(0, 24, 6)]); ax.set_xlabel("Hour of crash"); ax.set_ylabel("Mean SHAP value (log-odds)"); F.ygrid(ax)
    ax.text(2.5, 0.03, "Night", transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=6.6, color=F.INK2)
    F.panel(fig, ax, "g", "Attribution by hour")
    finish(fig, "Fig06_shap_importance_stability")

def fig_audit():
    from scipy.stats import norm
    T = audit(); Pd = T[T["group"] == "all"].set_index("factor").loc[ORDER]; y, heads = grouped_rows(ORDER, head=0.95, gap=0.35)
    fig = F.new_figure(180, 225); gs = fig.add_gridspec(3, 1, height_ratios=[1.30, 0.84, 1.04]); mid = gs[1].subgridspec(1, 2, width_ratios=[1.0, 1.08]); bot = gs[2].subgridspec(1, 3, width_ratios=[1.38, 0.80, 0.92])
    # (a) sampling distribution of the double ML estimate, with the three other readings
    ax = fig.add_subplot(gs[0]); ax.axvline(0, color=F.INK2, lw=0.9, zorder=1); xs = np.linspace(-19, 36, 2200)
    for yy, f in zip(y, ORDER):
        r = Pd.loc[f]; c = TIER_COL[FTIER[f]]; m, se = r["dml"] * 100, (r["dml_hi"] - r["dml_lo"]) * 100 / 3.92
        d = norm.pdf(xs, m, se); d = d / d.max() * 0.50; k = d > 0.003
        ax.plot([-19, 36], [yy, yy], color=GRIDC, lw=0.6, zorder=1)
        ax.fill_between(xs[k], yy, yy + d[k], color=F.tint(c, 0.35), lw=0, zorder=2); ax.plot(xs[k], yy + d[k], color=c, lw=1.1, zorder=3)
        ax.plot([r["dml_lo"] * 100, r["dml_hi"] * 100], [yy, yy], color=c, lw=2.8, solid_capstyle="round", zorder=4); ax.scatter(m, yy, s=26, color=WHITE, ec=c, lw=1.5, zorder=6)
        ax.scatter(r["raw_diff"] * 100, yy - 0.26, s=26, marker="D", fc=WHITE, ec=F.INK2, lw=1.0, zorder=5)
        ax.scatter(r["whatif_prob"] * 100, yy - 0.36, s=20, marker="s", fc=WHITE, ec=F.INK, lw=1.0, zorder=5)
        ax.scatter(r["shap_contrast_prob"] * 100, yy - 0.19, s=30, marker="^", color=F.INK, ec=WHITE, lw=0.6, zorder=6)
    XR, XS, XD = 44.5, 53.5, 74.5
    for yy, f in zip(y, ORDER):
        r = Pd.loc[f]; star = "*" if r["q_bh"] < 0.05 else ""
        ax.text(XR, yy, sgn(r["raw_diff"] * 100), va="center", ha="right", fontsize=7.3, color=F.INK2); ax.text(XS, yy, sgn(r["shap_contrast_prob"] * 100), va="center", ha="right", fontsize=7.3, color=F.INK)
        ax.text(XD, yy, F.minus(f"{r['dml'] * 100:+.1f} ({r['dml_lo'] * 100:.1f} to {r['dml_hi'] * 100:.1f})") + star, va="center", ha="right", fontsize=7.3, color=TIER_COL[FTIER[f]])
    for x_, t_ in ((XR, "Unadjusted"), (XS, "SHAP"), (XD, "Double ML (95% CI)")): ax.text(x_, heads[0][0], t_, va="center", ha="right", fontsize=7.2, color=F.INK2)
    tier_heads(ax, heads)
    ax.set_yticks(y, [FAC[f] for f in ORDER]); ax.set_ylim(y.min() - 0.7, 0.6); ax.set_xlim(-19, 75.5); ax.set_xticks(range(-15, 36, 5)); F.clean_left(ax); F.ygrid(ax, "x")
    ax.set_xlabel("Difference in the probability of being killed or hospitalized (percentage points)", x=0.36)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=F.tint(F.INK2, 0.40), ec=F.INK2, lw=0.8, label="Double ML: sampling distribution,\nestimate and 95% CI"),
                       Line2D([], [], marker="^", ls="", color=F.INK, mec=WHITE, ms=6.2, label="SHAP contrast"), Line2D([], [], marker="s", ls="", mfc=WHITE, mec=F.INK, ms=5.0, label="Model what-if"),
                       Line2D([], [], marker="D", ls="", mfc=WHITE, mec=F.INK2, ms=5.2, label="Unadjusted difference")],
              loc="upper center", bbox_to_anchor=(0.36, -0.105), ncol=4, fontsize=7.2, columnspacing=1.3, handletextpad=0.4)
    F.panel(fig, ax, "a", "Four readings of each pre-specified factor, all riders (* false discovery rate < 0.05)")
    # (b) SHAP contrast against double ML, all estimates
    ax = fig.add_subplot(mid[0]); lim = (-9, 23)
    ax.plot(lim, lim, color=F.INK2, lw=0.9, ls=(0, (4, 3)), zorder=1); ax.axhline(0, color=F.RULE, lw=0.8); ax.axvline(0, color=F.RULE, lw=0.8)
    sg = T[T["q_bh"] < 0.05]; b = np.polyfit(sg["dml"], sg["shap_contrast_prob"], 1); xs2 = np.array([-6, 21])
    ax.plot(xs2, b[0] * xs2 + b[1] * 100, color=F.INK, lw=1.4, zorder=2)
    for g, col, mk, lab in (("all", F.INK, "o", "All riders"), ("bicycle", PET, "o", "Bicycle"), ("ebike", SAF, "s", "E-bike"), ("escooter", VER, "D", "E-scooter")):
        d = T[T["group"] == g]; s_ = d["q_bh"] < 0.05
        ax.hlines(d.loc[s_, "shap_contrast_prob"] * 100, d.loc[s_, "dml_lo"] * 100, d.loc[s_, "dml_hi"] * 100, color=col, lw=0.9, alpha=0.70, zorder=2)
        ax.scatter(d.loc[s_, "dml"] * 100, d.loc[s_, "shap_contrast_prob"] * 100, s=36 if g == "all" else 27, color=col, ec=WHITE, lw=0.9, marker=mk, zorder=4, label=lab)
        ax.scatter(d.loc[~s_, "dml"] * 100, d.loc[~s_, "shap_contrast_prob"] * 100, s=36 if g == "all" else 27, fc=WHITE, ec=col, lw=1.1, marker=mk, zorder=3)
    note(ax, 0.975, 0.035, f"{len(T)} estimates; {len(sg)} with FDR < 0.05\nSolid line: least-squares fit to these, slope {b[0]:.2f}\nDashed line: equality. Whiskers: 95% CI (FDR < 0.05)", ha="right", va="bottom", fs=6.2)
    ax.set_xlim(*lim); ax.set_ylim(-15, 23); ax.set_yticks([-10, 0, 10, 20]); ax.set_xlabel("Double ML estimate (points)"); ax.set_ylabel("SHAP contrast (points)", fontsize=8.6); F.ygrid(ax, "both")
    ax.legend(loc="upper left", fontsize=6.8, title="Filled: FDR < 0.05", title_fontsize=6.6)
    F.panel(fig, ax, "b", "SHAP contrast against double ML")
    # (c) SHAP contrast as a fraction of the double ML estimate (bullet chart)
    ax = fig.add_subplot(mid[1]); Sg = Pd[Pd["q_bh"] < 0.05].copy(); Sg["ratio"] = Sg["shap_contrast_prob"].abs() / Sg["dml"].abs(); Sg = Sg.sort_values("ratio"); yy = np.arange(len(Sg))
    for i, (f, rt) in enumerate(Sg["ratio"].items()):
        for lo_, hi_, shd in ((0, 0.5, "#F1F0ED"), (0.5, 0.8, "#E4E2DD"), (0.8, 1.0, "#D2CFC8")): ax.barh(i, hi_ - lo_, left=lo_, height=0.76, color=shd, lw=0, zorder=1)
        ax.barh(i, rt, height=0.30, color=TIER_COL[FTIER[f]], lw=0, zorder=3); ax.plot([1, 1], [i - 0.38, i + 0.38], color=F.INK, lw=1.8, zorder=4)
        ax.text(1.03, i, f"{rt:.2f}", va="center", ha="left", fontsize=7.2)
    ax.set_yticks(yy, [FAC[f] for f in Sg.index]); ax.tick_params(axis="y", labelsize=7.6); ax.set_xlim(0, 1.15); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_ylim(-0.6, len(Sg) - 0.4); F.clean_left(ax)
    ax.set_xlabel("SHAP contrast as a fraction of the\ndouble ML estimate (1 = equal)")
    F.panel(fig, ax, "c", "Attenuation of the SHAP contrast")
    # (d) SHAP-style plot: out-of-fold SHAP values of the defining variable(s) in the two groups of each factor
    from scipy.stats import kendalltau
    qs = ["raw_diff", "shap_contrast_prob", "whatif_prob", "dml"]; qn = ["Unadjusted", "SHAP", "What-if", "Double ML"]
    A = riders(); A = A[A["year"] >= 2020].reset_index(drop=True); S = pd.read_parquet(os.path.join(args.res, "oof_shap.parquet")); rng = np.random.default_rng(20261111)
    DEF = {"A1": ["mode"], "A2": ["mode"], "B1": ["vma"], "B2": ["lum"], "B3": ["atm", "surf"], "B4": ["vosp"], "B5": ["int_type"], "C1": ["opponent"], "C2": ["opponent", "n_vehicles", "col"], "C3": ["situ"], "D1": ["age"], "D2": ["sex"]}
    ax = fig.add_subplot(bot[0]); xl = (-1.7, 2.3); edges = np.linspace(xl[0], xl[1], 91)
    for i, f in enumerate(ORDER):
        t = A["T_" + f].values; sv = S[DEF[f]].sum(axis=1).values; ax.plot(xl, [i, i], color=GRIDC, lw=0.6, zorder=1)
        for grp, col, side in ((1, VER, -1), (0, PET, 1)):
            idx = np.where(t == grp)[0]; idx = rng.choice(idx, min(len(idx), 1400), replace=False); v = np.clip(sv[idx], xl[0] + 0.02, xl[1] - 0.02)
            b = np.clip(np.digitize(v, edges) - 1, 0, 89); off = np.zeros(len(v)); cmax = max(np.bincount(b).max(), 1)
            for k in np.unique(b):
                j = np.where(b == k)[0]; off[j] = 0.05 + np.arange(len(j)) / cmax * 0.38
            ax.scatter(v, i + side * off, s=1.5, color=col, alpha=0.85, lw=0, rasterized=True, zorder=2)
            ax.plot([sv[t == grp].mean()] * 2, [i + side * 0.04, i + side * 0.44], color=F.INK, lw=1.5, zorder=4, solid_capstyle="butt")
    ax.axvline(0, color=F.INK2, lw=0.8, zorder=1); ax.set_xlim(*xl); ax.set_ylim(len(ORDER) - 0.45, -0.6); ax.set_yticks(range(len(ORDER)), [SHORT[f] for f in ORDER]); ax.tick_params(axis="y", length=0, labelsize=7.2)
    for i, f in enumerate(ORDER): ax.get_yticklabels()[i].set_color(TIER_COL[FTIER[f]])
    ax.spines["left"].set_visible(False); F.ygrid(ax, "x"); ax.set_xlabel("SHAP value (log-odds)")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=VER, ms=4.5, label="First-named group"), Line2D([], [], marker="o", ls="", color=PET, ms=4.5, label="Reference group"), Line2D([], [], color=F.INK, lw=1.5, label="Group mean")],
              loc="center right", bbox_to_anchor=(1.0, 0.50), fontsize=6.4, handletextpad=0.3, frameon=True, facecolor=WHITE, edgecolor=F.RULE, borderpad=0.4)
    F.panel(fig, ax, "d", "SHAP values in the two groups compared")
    ax = fig.add_subplot(bot[1]); K = np.array([[kendalltau(Pd[a].abs(), Pd[b_].abs())[0] for b_ in qs] for a in qs])
    for i in range(4):
        for j in range(4):
            if i == j: ax.text(j, i, "–", ha="center", va="center", fontsize=7.4, color=F.MUTED); continue
            colr = mpl.colors.to_hex(F.HEAT(max(K[i, j], 0))); dm = "dml" in (qs[i], qs[j])
            ax.add_patch(FancyBboxPatch((j - 0.44, i - 0.44), 0.88, 0.88, boxstyle="round,pad=0,rounding_size=0.12", fc=colr, ec=F.INK if dm else "none", lw=0.9, zorder=2))
            ax.text(j, i, f"{K[i, j]:.2f}", ha="center", va="center", fontsize=7.6, color=F.text_on(colr), zorder=3)
    ax.set_xlim(-0.55, 3.55); ax.set_ylim(3.55, -0.55); ax.set_xticks(range(4), ["Un-\nadjusted", "SHAP", "What-\nif", "Double\nML"], fontsize=7.0); ax.set_yticks(range(4), qn, fontsize=7.2); ax.tick_params(length=0); [sp.set_visible(False) for sp in ax.spines.values()]
    ax.set_xlabel("Kendall τ between rankings\n(12 factors, all riders)", fontsize=8.2)
    F.panel(fig, ax, "e", "Rank concordance")
    # (e) standardized difference between SHAP and double ML
    ax = fig.add_subplot(bot[2]); T2 = T.copy(); T2["z"] = (T2["shap_contrast_prob"] - T2["dml"]) / ((T2["dml_hi"] - T2["dml_lo"]) / 3.92)
    grp = ["all", "bicycle", "ebike", "escooter"]; gl = ["All riders", "Bicycle", "E-bike", "E-scooter"]; zmax = 8.6
    ax.axvspan(-1.96, 1.96, color=BAND, lw=0, zorder=0); ax.axvline(0, color=F.INK2, lw=0.8)
    for i, g in enumerate(grp[::-1]):
        d = T2[T2["group"] == g].sort_values("z"); offs = np.linspace(-0.3, 0.3, len(d)); cnt = {1: 0, -1: 0}
        for (_, r), o in zip(d.iterrows(), offs):
            c = TIER_COL[FTIER[r["factor"]]]; s_ = r["q_bh"] < 0.05
            ax.scatter(r["z"], i + o, s=27, fc=c if s_ else WHITE, ec=WHITE if s_ else c, lw=0.9 if s_ else 1.1, zorder=4)
        for side in (1, -1):
            out = d[(d["z"] * side) > 1.96]
            for k, (_, r) in enumerate(out.iterrows()):
                ax.text(side * (zmax - 0.15), i + 0.2 - 0.3 * k, SHORT[r["factor"]], va="center", ha="right" if side > 0 else "left", fontsize=6.0, color=TIER_COL[FTIER[r["factor"]]])
    ax.set_yticks(range(4), gl[::-1]); ax.set_ylim(-0.6, 3.75); ax.set_xlim(-zmax, zmax); ax.set_xticks([-4, -2, 0, 2, 4]); F.clean_left(ax); F.ygrid(ax, "x")
    ax.set_xlabel("(SHAP − double ML) /\nstandard error")
    ax.text(0, 3.70, "Within the 95% interval", ha="center", va="top", fontsize=6.3, color=F.INK2, bbox=dict(fc=BAND, ec="none", pad=0.8))
    F.panel(fig, ax, "f", "Standardized difference")
    finish(fig, "Fig07_audit_shap_double_ml")

def fig_sources():
    T = audit(); Pd = T[T["group"] == "all"].set_index("factor").loc[ORDER]; y, heads = grouped_rows(ORDER)
    fig = F.new_figure(180, 218); gs = fig.add_gridspec(3, 1, height_ratios=[1.3, 0.10, 1.0]); tp = gs[0].subgridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.03); bot = gs[2].subgridspec(1, 2, width_ratios=[1.25, 1.0])
    # (a) shift of the double ML estimate when later-tier variables are added (arrow chart)
    ax = fig.add_subplot(tp[0]); ax.axvline(0, color=F.INK2, lw=0.9, zorder=1)
    for yy, f in zip(y, ORDER):
        r = Pd.loc[f]; c = TIER_COL[FTIER[f]]; a, b_ = r["dml"] * 100, r["dml_allc"] * 100
        ax.plot([r["dml_lo"] * 100, r["dml_hi"] * 100], [yy + 0.08] * 2, color=F.tint(c, 0.42), lw=7.5, solid_capstyle="round", zorder=2)
        ax.plot([r["allc_lo"] * 100, r["allc_hi"] * 100], [yy - 0.30] * 2, color=F.INK2, lw=0.9, zorder=2, marker="|", ms=4, mew=0.9)
        ax.scatter(b_, yy - 0.30, s=10, color=F.INK2, zorder=3)
        if abs(b_ - a) > 0.25: ax.annotate("", (b_, yy + 0.08), (a, yy + 0.08), arrowprops=dict(arrowstyle="-|>", color=c, lw=1.7, mutation_scale=9, shrinkA=0, shrinkB=0), zorder=5)
        ax.scatter(a, yy + 0.08, s=30, color=c, ec=WHITE, lw=0.9, zorder=6)
        ax.text(31.6, yy, f"{sgn(a)} → {sgn(b_)}", va="center", ha="right", fontsize=7.0, color=F.INK)
    ax.text(31.6, heads[0][0], "Estimate: set → all", va="center", ha="right", fontsize=6.8, color=F.INK2)
    tier_heads(ax, heads)
    ax.set_yticks(y, [FAC[f] for f in ORDER]); ax.set_ylim(y.min() - 0.7, 0.55); ax.set_xlim(-8, 32); ax.set_xticks(range(-5, 21, 5)); F.clean_left(ax); F.ygrid(ax, "x"); ax.set_xlabel("Double ML estimate (points)", x=0.36)
    F.panel(fig, ax, "a", "Shift of the estimate when later-tier variables are added")
    # (b) stepwise decomposition of the difference between SHAP and double ML
    ax = fig.add_subplot(tp[1]); bad = (Pd["dml_allc"] - Pd["dml"]) * 100; mod = (Pd["shap_contrast_prob"] - Pd["dml_allc"]) * 100; tot = bad + mod
    ax.axvline(0, color=F.INK2, lw=0.9, zorder=1); bands(ax, y)
    for yy, f in zip(y, ORDER):
        ax.barh(yy + 0.17, bad[f], left=0, height=0.30, color=PUR, lw=0, zorder=3); ax.barh(yy - 0.17, mod[f], left=bad[f], height=0.30, color=TEAL, lw=0, zorder=3)
        ax.plot([bad[f]] * 2, [yy - 0.34, yy + 0.34], color=F.INK2, lw=0.7, zorder=4); ax.scatter(tot[f], yy - 0.17, s=24, marker="D", fc=WHITE, ec=F.INK, lw=1.1, zorder=5)
        ax.text(6.9, yy, sgn(tot[f]), va="center", ha="right", fontsize=7.2)
    ax.text(6.9, heads[0][0], "Total", va="center", ha="right", fontsize=7.0, color=F.INK2)
    ax.set_yticks(y, [""] * len(y)); ax.set_ylim(y.min() - 0.7, 0.55); ax.set_xlim(-5.6, 7.1); ax.set_xticks([-4, -2, 0, 2, 4]); F.clean_left(ax); F.ygrid(ax, "x"); ax.set_xlabel("SHAP minus double ML (points)", x=0.42)
    F.panel(fig, ax, "b", "Sources of the difference")
    # shared legend for (a) and (b)
    lg = fig.add_subplot(gs[1]); lg.axis("off")
    lg.legend(handles=[Line2D([], [], color=F.tint(F.INK2, 0.35), lw=6.5, solid_capstyle="round", marker="o", mfc=F.INK2, mec=WHITE, ms=5.2, label="Pre-specified adjustment set: estimate and 95% CI"),
                       Line2D([], [], color=F.INK2, lw=1.6, marker=">", ms=5, label="Shift when all controls are added"),
                       Line2D([], [], color=F.INK2, lw=0.9, marker="|", ms=5, label="All controls: estimate and 95% CI"),
                       plt.Rectangle((0, 0), 1, 1, fc=PUR, ec="none", label="Step 1: adjustment for later-tier variables"), plt.Rectangle((0, 0), 1, 1, fc=TEAL, ec="none", label="Step 2: predictive model against double ML"),
                       Line2D([], [], marker="D", ls="", mfc=WHITE, mec=F.INK, ms=5.2, label="Total difference")],
              loc="center", ncol=3, fontsize=6.9, columnspacing=1.6, handletextpad=1.0, handlelength=2.2)
    # (c) SHAP contrast against each double ML variant
    ax = fig.add_subplot(bot[0]); lim = (-7, 22); sx = Pd["shap_contrast_prob"] * 100
    ax.plot(lim, lim, color=F.INK2, lw=0.9, ls=(0, (4, 3)), zorder=1); ax.axhline(0, color=F.RULE, lw=0.8); ax.axvline(0, color=F.RULE, lw=0.8)
    for f in ORDER: ax.plot([Pd.loc[f, "dml"] * 100, Pd.loc[f, "dml_allc"] * 100], [sx[f]] * 2, color="#8F8B83", lw=1.4, zorder=2)
    b1 = np.polyfit(Pd["dml"], Pd["shap_contrast_prob"], 1); b2 = np.polyfit(Pd["dml_allc"], Pd["shap_contrast_prob"], 1); xs = np.array([-6, 19])
    ax.plot(xs, b1[0] * xs + b1[1] * 100, color=VER, lw=1.3, zorder=2); ax.plot(xs, b2[0] * xs + b2[1] * 100, color=PET, lw=1.3, zorder=2)
    ax.scatter(Pd["dml"] * 100, sx, s=36, color=VER, ec=WHITE, lw=0.9, zorder=4, label=f"Pre-specified set (slope {b1[0]:.2f})")
    ax.scatter(Pd["dml_allc"] * 100, sx, s=32, marker="s", color=PET, ec=WHITE, lw=0.9, zorder=4, label=f"All controls (slope {b2[0]:.2f})")
    for f in ("C1", "C2", "D1", "A2"):
        ax.text(max(Pd.loc[f, "dml"], Pd.loc[f, "dml_allc"]) * 100 + 0.8, sx[f] - 0.1, SHORT[f], va="center", ha="left", fontsize=6.6, color=F.INK)
    ax.text(min(Pd.loc["C3", "dml"], Pd.loc["C3", "dml_allc"]) * 100 - 0.2, sx["C3"] + 1.3, SHORT["C3"], va="center", ha="center", fontsize=6.6, color=F.INK)
    ax.set_xlim(*lim); ax.set_ylim(*lim); ax.set_xlabel("Double ML estimate (points)"); ax.set_ylabel("SHAP contrast (points)"); F.ygrid(ax, "both")
    ax.legend(loc="upper left", fontsize=6.8, title="Double ML adjusted for", title_fontsize=6.8)
    note(ax, 0.975, 0.035, "Gray links join the two double ML\nestimates of the same factor", ha="right", va="bottom", fs=6.2)
    F.panel(fig, ax, "c", "SHAP contrast against both double ML estimates")
    # (d) mean absolute difference by pairing
    ax = fig.add_subplot(bot[1]); mad = lambda a, b_: (Pd[a] - Pd[b_]).abs().mean() * 100
    vals = np.array([[mad("shap_contrast_prob", "dml"), mad("shap_contrast_prob", "dml_allc")], [mad("whatif_prob", "dml"), mad("whatif_prob", "dml_allc")]]); xg = np.arange(2)
    for i in range(2):
        ax.plot([xg[i] - 0.2, xg[i] + 0.2], vals[i], color="#8F8B83", lw=1.4, zorder=2)
        for j, col in enumerate((VER, PET)):
            xv = xg[i] + (-0.2 if j == 0 else 0.2); ax.vlines(xv, 0, vals[i, j], color=col, lw=3.0, alpha=0.75, zorder=2); ax.scatter(xv, vals[i, j], s=64, marker="os"[j], color=col, ec=WHITE, lw=1.0, zorder=4)
            ax.text(xv, vals[i, j] + 0.06, f"{vals[i, j]:.2f}", ha="center", va="bottom", fontsize=7.4)
        ax.text(xg[i], 0.42, sgn((vals[i, 1] / vals[i, 0] - 1) * 100, 0) + "%", ha="center", va="center", fontsize=7.0, color=F.INK2)
    ax.set_xticks(xg, ["SHAP contrast", "Model what-if"]); ax.set_xlim(-0.6, 1.6); ax.set_ylim(0, vals.max() * 1.45); ax.set_ylabel("Mean absolute difference from\ndouble ML (points)"); F.ygrid(ax)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=VER, mec=WHITE, ms=6.5, label="Pre-specified adjustment set"), Line2D([], [], marker="s", ls="", color=PET, mec=WHITE, ms=6.2, label="All controls")],
              loc="upper center", fontsize=6.8, title="Double ML adjusted for", title_fontsize=6.8)
    F.panel(fig, ax, "d", "Mean absolute difference, 12 factors")
    finish(fig, "Fig08_sources_of_disagreement")

def fig_groups():
    D = pd.read_csv(os.path.join(args.res, "dml_main.csv")); D = D[(D["variant"] == "main") & (D["group"] != "all")]
    H = pd.read_csv(os.path.join(args.res, "heterogeneity_gate.csv")); A = riders(); nm = A[A["year"] >= 2020]["mode"].value_counts()
    facs = [f for f in ORDER if f not in ("A1", "A2")]
    fig = F.new_figure(180, 225); gs = fig.add_gridspec(4, 1, height_ratios=[1.22, 1.0, 1.0, 1.16])
    # (a) bubble matrix: estimate by factor and mode
    ax = fig.add_subplot(gs[0]); CL = {"D1": "Age 65+\nvs. 25–64", "D2": "Male\nvs. female", "B1": "≤30 vs.\n50 km/h", "B4": "Cycle facility\nvs. none", "B5": "Intersection\nvs. none", "B2": "Night: unlit\nvs. lit",
                                      "B3": "Adverse vs.\nnormal", "C1": "Heavy vehicle\nvs. car", "C2": "Single vehicle\nvs. collision", "C3": "Cycle path vs.\nroadway"}
    for j in range(len(facs)):
        if j % 2 == 0: ax.axvspan(j - 0.5, j + 0.5, color=BAND, lw=0, zorder=0)
    for i, m in enumerate(MODES):
        d = D[D["group"] == m].set_index("factor")
        for j, f in enumerate(facs):
            if f not in d.index or d.loc[f, "status"] != "ok":
                ax.text(j, i, "Not\nestimated", ha="center", va="center", fontsize=6.2, color=F.MUTED, linespacing=1.05); continue
            r = d.loc[f]; th = r["theta"] * 100; col = VER if th > 0 else PET; s_ = r["q_bh"] < 0.05
            ax.scatter(j, i - 0.13, s=22 + 21 * min(abs(th), 20), fc=col if s_ else WHITE, ec=col, lw=1.4, alpha=1.0, zorder=3)
            ax.text(j, i + 0.33, sgn(th) + ("*" if s_ else ""), ha="center", va="center", fontsize=7.2, color=F.INK)
            ax.text(j, i + 0.47, F.minus(f"({r['lo'] * 100:.1f} to {r['hi'] * 100:.1f})"), ha="center", va="center", fontsize=5.9, color=F.INK2)
    ax.set_xlim(-0.5, len(facs) - 0.5); ax.set_ylim(2.62, -0.62); ax.set_yticks(range(3), [f"{MODE_LAB[m]}\n(n = {int(nm[m]):,})" for m in MODES]); ax.tick_params(axis="y", length=0, labelsize=7.8)
    ax.set_xticks(range(len(facs)), [CL[f] for f in facs], fontsize=6.9); ax.xaxis.tick_top(); ax.tick_params(axis="x", length=0, pad=2); [sp.set_visible(False) for sp in ax.spines.values()]
    for t in ("tier1", "tier2", "tier3"):
        js = [j for j, f in enumerate(facs) if FTIER[f] == t]
        ax.plot([js[0] - 0.42, js[-1] + 0.42], [2.72, 2.72], color=TIER_COL[t], lw=2.2, clip_on=False, solid_capstyle="butt"); ax.text(np.mean(js), 2.80, TIER_HEAD[t], ha="center", va="top", fontsize=6.8, color=TIER_COL[t], clip_on=False)
    fig.legend(handles=[Line2D([], [], marker="o", ls="", color=VER, ms=7, label="Panel a: higher probability"), Line2D([], [], marker="o", ls="", color=PET, ms=7, label="lower probability"),
                        Line2D([], [], marker="o", ls="", mfc=WHITE, mec=F.INK2, mew=1.3, ms=7, label="open marker: FDR \u2265 0.05"),
                        Line2D([], [], color=F.tint(F.INK2, 0.35), lw=6.0, solid_capstyle="round", label="Panels b\u2013d: joint 95% CI"), Line2D([], [], color=F.INK2, lw=2.0, label="pointwise 95% CI"),
                        Line2D([], [], color=VER, lw=1.0, ls=(0, (4, 3)), label="overall estimate")],
               loc="outside lower center", ncol=6, fontsize=6.8, columnspacing=1.2, handletextpad=0.5)
    F.panel(fig, ax, "a", "Double ML estimates by factor and transport mode (points, 95% CI; * FDR < 0.05)")
    # (b-d) group average effects: one strip per factor, groups on a common horizontal axis
    GL = {"mode": "Mode", "age": "Age", "sex": "Sex", "urban": "Setting", "opponent": "Opponent"}; GCOL = {"mode": PET, "age": TEAL, "sex": SAF, "urban": PUR, "opponent": ROSE}
    GR = {"mode": ["bicycle", "ebike", "escooter"], "age": ["under 25", "25-64", "65+"], "sex": ["male", "female"], "urban": ["urban", "non-urban"], "opponent": ["motor-vehicle opponent", "no motor-vehicle opponent"]}
    NAME = {"bicycle": "Bicycle", "ebike": "E-bike", "escooter": "E-scooter", "under 25": "Under 25", "25-64": "25–64", "65+": "65 and\nover", "male": "Male", "female": "Female",
            "urban": "Urban", "non-urban": "Non-urban", "motor-vehicle opponent": "Motor\nvehicle", "no motor-vehicle opponent": "No motor\nvehicle"}
    xp, span, cur = {}, {}, 0.0
    for g, members in GR.items():
        x0 = cur
        for mbr in members: xp[(g, mbr)] = cur; cur += 1.0
        span[g] = (x0 - 0.5, cur - 0.5); cur += 0.45
    for k, (f, ttl, lim) in enumerate((("A1", "E-scooter vs. bicycle", (-13, 16)), ("B1", "Speed limit ≤30 vs. 50 km/h", (-13.5, 6)), ("B2", "Night: unlit vs. lit", (-30, 56)))):
        ax = fig.add_subplot(gs[k + 1]); h = H[H["factor"] == f]; ov = h["overall"].iloc[0] * 100; rng_ = lim[1] - lim[0]; top = lim[1] + rng_ * 0.20; btm = lim[0] - rng_ * 0.16
        for gi, g in enumerate(GR):
            ax.axvspan(*span[g], color=BAND if gi % 2 == 0 else WHITE, lw=0, zorder=0); hh = h[h["grouping"] == g]
            ptxt = f" ({pfmt(hh['p_equal_across_groups'].iloc[0])})" if len(hh) else ""
            ax.text(np.mean(span[g]), top - rng_ * 0.03, GL[g] + ptxt, ha="center", va="top", fontsize=6.8, color=GCOL[g])
            if hh.empty:
                ax.text(np.mean(span[g]), lim[1] - rng_ * 0.20, "Not applicable:\nthe contrast is\nbetween modes" if f == "A1" else "Not applicable:\nurban crashes only", ha="center", va="center", fontsize=6.4, color=F.MUTED, linespacing=1.1); continue
            for mbr in GR[g]:
                x = xp[(g, mbr)]; r = hh[hh["group"] == mbr]
                if r.empty:
                    ax.text(x, (lim[0] + lim[1]) / 2, "Not applicable" if (f == "A1" and g == "mode") else "Not\nestimated", ha="center", va="center", fontsize=6.2, color=F.MUTED, rotation=0, linespacing=1.05); continue
                r = r.iloc[0]; e, se = r["effect"] * 100, r["se"] * 100; c = GCOL[g]
                ax.plot([x, x], [max(r["lo_joint"] * 100, lim[0] - rng_ * 0.02), min(r["hi_joint"] * 100, lim[1] + rng_ * 0.02)], color=F.tint(c, 0.40), lw=7.0, solid_capstyle="round", zorder=2)
                ax.plot([x, x], [e - 1.96 * se, e + 1.96 * se], color=c, lw=2.0, solid_capstyle="round", zorder=3); ax.scatter(x, e, s=34, color=WHITE, ec=c, lw=1.5, zorder=5)
                ax.text(x + 0.16, e, sgn(e), ha="left", va="center", fontsize=6.9, color=F.INK); ax.text(x, btm + rng_ * 0.015, f"n = {int(r['n']):,}", ha="center", va="bottom", fontsize=6.0, color=F.INK2)
        ax.axhline(0, color=F.INK2, lw=0.9, zorder=1); ax.axhline(ov, color=VER, lw=1.0, ls=(0, (4, 3)), zorder=1)
        ax.set_xlim(-0.5, cur - 0.95); ax.set_ylim(btm, top); ax.set_ylabel("Effect (points)"); F.ygrid(ax)
        if k == 2: ax.set_xticks([xp[key] for key in xp], [NAME[key[1]] for key in xp], fontsize=7.0); ax.tick_params(axis="x", length=0)
        else: ax.set_xticks([]); 
        F.panel(fig, ax, "bcd"[k], f"{ttl}: group average effects (overall estimate {sgn(ov)} points)")
    finish(fig, "Fig09_effects_by_mode_and_group")

def fig_robustness():
    R = pd.read_csv(os.path.join(args.res, "robustness.csv")); R = R[R["status"] == "ok"]; R5 = pd.read_csv(os.path.join(args.res, "robustness_r5_corrected.csv"))
    M = pd.read_csv(os.path.join(args.res, "dml_main.csv")); M = M[(M["variant"] == "main") & (M["group"] == "all") & (M["status"] == "ok")].set_index("factor")
    raw_all = audit().query("group == 'all'").set_index("factor").loc["A1", "raw_diff"]
    cols = ["A1", "A2", "D1", "D2", "B1", "B4", "C1", "C2", "C3"]
    SH = {"A1": "E-scooter\nvs. bicycle", "A2": "E-bike\nvs. bicycle", "D1": "Age 65+\nvs. 25–64", "D2": "Male\nvs. female", "B1": "≤30 vs.\n50 km/h", "B4": "Cycle\nfacility", "C1": "Heavy\nvehicle", "C2": "Single\nvehicle", "C3": "Cycle\npath"}
    checks = [("R1 include 2019", "Including 2019"), ("R2 exclude Paris police area", "Excluding the Paris police area"), ("R3 fatal outcome", "Fatal outcome"),
              ("R4 motor-vehicle collisions only", "Motor-vehicle collisions only"), ("R5c", "Early-adopter départements"), ("R6a any-row location variables", "Any-row location variables"),
              ("R6b drop location-file variables", "Without location-file variables"), ("R7a random forest nuisances", "Random-forest nuisance models"),
              ("R7b logistic nuisances", "Logistic nuisance models"), ("R8a trim 0.01", "Trimming at 0.01"), ("R8b trim 0.05", "Trimming at 0.05"), ("R9 partially linear model", "Partially linear model")]
    est = np.full((len(checks), len(cols)), np.nan); sig = np.zeros_like(est, bool); a1 = []
    for i, (key, lab) in enumerate(checks):
        for j, f in enumerate(cols):
            if key == "R5c":
                if f == "A1": r = R5.iloc[0]; est[i, j] = r["theta"]; sig[i, j] = r["p"] < 0.05; a1.append((lab, r["theta"], r["lo"], r["hi"], r["p"]))
                continue
            d = R[(R["check"] == key) & (R["factor"] == f)]
            if len(d):
                est[i, j] = d["theta"].iloc[0]; sig[i, j] = d["p"].iloc[0] < 0.05
                if f == "A1": a1.append((lab, d["theta"].iloc[0], d["lo"].iloc[0], d["hi"].iloc[0], d["p"].iloc[0]))
    main = M.loc[cols, "theta"].values; ratio = est / main
    fig = F.new_figure(180, 225); gs = fig.add_gridspec(3, 1, height_ratios=[1.22, 1.0, 0.72]); mid = gs[1].subgridspec(1, 2, width_ratios=[1.3, 1.0])
    ax = fig.add_subplot(gs[0]); im = ax.imshow(np.clip(ratio, 0, 2), cmap=DIVW, vmin=0, vmax=2, aspect="auto")
    for i in range(est.shape[0]):
        for j in range(est.shape[1]):
            if np.isnan(est[i, j]): ax.text(j, i, "–", ha="center", va="center", fontsize=7.4, color=F.INK2); continue
            c = F.text_on(mpl.colors.to_hex(DIVW(np.clip(ratio[i, j], 0, 2) / 2)))
            ax.text(j, i, sgn(est[i, j] * 100) + ("" if sig[i, j] else "†"), ha="center", va="center", fontsize=7.4, color=c)
    ax.set_xticks(range(len(cols)), [SH[f] + "\n" + sgn(m * 100) for f, m in zip(cols, main)], fontsize=7.4)
    ax.xaxis.tick_top(); ax.tick_params(axis="x", length=0, pad=3); ax.tick_params(axis="y", length=0, labelsize=8)
    ax.set_yticks(range(len(checks)), [c[1] for c in checks]); [sp.set_visible(False) for sp in ax.spines.values()]
    ax.set_xticks(np.arange(-.5, len(cols)), minor=True); ax.set_yticks(np.arange(-.5, len(checks)), minor=True); ax.grid(which="minor", color=F.RULE, lw=0.8); ax.tick_params(which="minor", length=0); ax.grid(which="major", visible=False)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.015); cb.set_label("Ratio to the main estimate", fontsize=7.8); cb.set_ticks([0, 0.5, 1, 1.5, 2]); cb.outline.set_visible(False); cb.ax.tick_params(labelsize=7.4, length=2)
    F.panel(fig, ax, "a", "Estimates under each robustness check (main estimate beneath each heading; † p ≥ 0.05)")
    # (b) e-scooter versus bicycle under every check, with confidence intervals
    ax = fig.add_subplot(mid[0]); rows = [("Main analysis", M.loc["A1", "theta"], M.loc["A1", "lo"], M.loc["A1", "hi"], M.loc["A1", "p"])] + a1; yb = np.arange(len(rows))[::-1]; bands(ax, yb)
    ax.axvspan(M.loc["A1", "lo"] * 100, M.loc["A1", "hi"] * 100, color=F.tint(VER, 0.82), lw=0, zorder=0); ax.axvline(0, color=F.INK2, lw=0.9)
    for yy_, (lab, th, lo, hi, p) in zip(yb, rows):
        s_ = p < 0.05; ax.plot([lo * 100, hi * 100], [yy_] * 2, color=VER, lw=2.0, alpha=0.85, zorder=2)
        ax.scatter(th * 100, yy_, s=38 if lab != "Main analysis" else 52, fc=VER if s_ else WHITE, ec=WHITE if s_ else VER, lw=1.1, zorder=4)
        ax.text(11.4, yy_, F.minus(f"{th * 100:+.1f} ({lo * 100:.1f} to {hi * 100:.1f})"), va="center", ha="right", fontsize=6.8)
    ax.set_yticks(yb, [r[0] for r in rows]); ax.tick_params(axis="y", labelsize=7.4); ax.set_ylim(-0.6, len(rows) - 0.4); ax.set_xlim(-2.2, 11.6); ax.set_xticks([-2, 0, 2, 4]); F.clean_left(ax); F.ygrid(ax, "x")
    ax.set_xlabel("Double ML estimate (points, 95% CI)", x=0.26)
    F.panel(fig, ax, "b", "E-scooter vs. bicycle under each check")
    # (c) unadjusted and adjusted difference by recording context
    ax = fig.add_subplot(mid[1]); ctx = [(f"All départements\n(n = {int(M.loc['A1', 'n']):,})", raw_all, M.loc["A1", "theta"], M.loc["A1", "lo"], M.loc["A1", "hi"]),
                                         (f"Ten early-adopter\ndépartements\n(n = {int(R5.iloc[0]['n']):,})", R5.iloc[0]["raw_diff"], R5.iloc[0]["theta"], R5.iloc[0]["lo"], R5.iloc[0]["hi"]),
                                         (f"All other\ndépartements\n(n = {int(R5.iloc[1]['n']):,})", R5.iloc[1]["raw_diff"], R5.iloc[1]["theta"], R5.iloc[1]["lo"], R5.iloc[1]["hi"])]
    yc = np.arange(3)[::-1]; bands(ax, yc); ax.axvline(0, color=F.INK2, lw=0.9)
    for yy_, (lab, raw, th, lo, hi) in zip(yc, ctx):
        ax.annotate("", (th * 100, yy_), (raw * 100, yy_), arrowprops=dict(arrowstyle="-|>", color="#8F8B83", lw=1.2, mutation_scale=8, shrinkA=4, shrinkB=5), zorder=1)
        ax.plot([lo * 100, hi * 100], [yy_] * 2, color=VER, lw=2.2, alpha=0.85, zorder=2); ax.scatter(th * 100, yy_, s=46, color=VER, ec=WHITE, lw=1.0, zorder=4)
        ax.scatter(raw * 100, yy_, s=34, marker="D", fc=WHITE, ec=F.INK2, lw=1.1, zorder=4)
        ax.text(raw * 100 - 1.0, yy_, sgn(raw * 100), ha="right", va="center", fontsize=6.8, color=F.INK2); ax.text(hi * 100 + 0.6, yy_, sgn(th * 100), ha="left", va="center", fontsize=6.8, color=VER)
    ax.set_yticks(yc, [c[0] for c in ctx]); ax.tick_params(axis="y", labelsize=7.0); ax.set_ylim(-1.3, 2.55); ax.set_xlim(-19.5, 9.5); F.clean_left(ax); F.ygrid(ax, "x"); ax.set_xlabel("Difference (points)")
    ax.legend(handles=[Line2D([], [], marker="D", ls="", mfc=WHITE, mec=F.INK2, ms=5.6, label="Unadjusted"), Line2D([], [], marker="o", color=VER, mec=WHITE, ms=6.2, lw=2.0, alpha=0.9, label="Double ML (95% CI)")],
              loc="lower center", fontsize=6.8, ncol=2, columnspacing=1.0, handletextpad=0.3)
    F.panel(fig, ax, "c", "By recording context")
    # (d) sensitivity to unobserved confounding
    B = R[R["check"] == "R11 benchmark: departement"].set_index("factor").loc[cols]
    ax = fig.add_subplot(gs[2]); x = np.arange(len(cols)); e = B["theta"].abs() * 100; sh = B["bench_delta_theta"].abs() * 100
    ax.bar(x - 0.19, e, width=0.36, color=VER, ec=WHITE, lw=0.6, label="Absolute main estimate", zorder=3)
    ax.bar(x + 0.19, sh, width=0.36, color=PET, ec=WHITE, lw=0.6, label="Change produced by an unobserved confounder as strong as département", zorder=3)
    for xi, a_, b_, rv in zip(x, e, sh, B["rv"] * 100):
        ax.text(xi - 0.19, a_ + 0.3, f"{a_:.1f}", ha="center", va="bottom", fontsize=6.6, color=F.INK); ax.text(xi + 0.19, b_ + 0.3, f"{b_:.1f}", ha="center", va="bottom", fontsize=6.6, color=F.INK)
        ax.text(xi, max(a_, b_) + 2.3, f"RV {rv:.1f}%", ha="center", va="bottom", fontsize=7.0, color=F.INK)
    ax.set_xticks(x, [SH[f] for f in cols], fontsize=7.2); ax.set_ylabel("Percentage points"); ax.set_ylim(0, 27); F.ygrid(ax); ax.set_xlim(-0.6, len(cols) - 0.4)
    ax.legend(loc="upper left", fontsize=7.0, bbox_to_anchor=(0.0, 1.0), ncol=2, columnspacing=1.4)
    F.panel(fig, ax, "d", "Sensitivity to unobserved confounding (RV, robustness value)")
    finish(fig, "Fig10_robustness")


def _geo():
    import json
    g = json.load(open(args.geo, encoding="utf-8")); k = np.cos(np.radians(46.5)); out = {}
    for ft in g["features"]:
        gm = ft["geometry"]; polys = [gm["coordinates"]] if gm["type"] == "Polygon" else gm["coordinates"]
        out[ft["properties"]["code"]] = [np.column_stack([np.array(p[0])[:, 0] * k, np.array(p[0])[:, 1]]) for p in polys]
    return out, k
def choropleth(ax, geo, k, color_of, inset=True, lw=0.35):
    """France by departement, with an enlarged inset of Paris and the three adjoining departements."""
    from matplotlib.collections import PolyCollection
    def draw(a, w):
        polys, cols = [], []
        for code, rings in geo.items():
            for r in rings: polys.append(r); cols.append(color_of(code))
        a.add_collection(PolyCollection(polys, facecolors=cols, edgecolors=WHITE, linewidths=w, zorder=2)); a.set_aspect("equal")
    draw(ax, lw); ax.set_xlim(-7.6 * k, 9.8 * k); ax.set_ylim(41.2, 51.3); ax.axis("off")
    if inset:
        ia = ax.inset_axes([0.0, 0.16, 0.30, 0.30]); draw(ia, 0.6); ia.set_xlim(2.13 * k, 2.62 * k); ia.set_ylim(48.70, 49.02); ia.set_xticks([]); ia.set_yticks([])
        for sp in ia.spines.values(): sp.set_visible(True); sp.set_color(F.INK2); sp.set_linewidth(0.8)
        ia.set_title("Paris area", fontsize=6.4, pad=2, color=F.INK); ax.plot([2.37 * k], [48.86], marker="s", ms=4.5, mfc="none", mec=F.INK2, mew=0.8, zorder=5)
def cbar(fig, ax, cmap, norm, label, ticks=None, fmt=None, extend="neither"):
    cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, orientation="horizontal", fraction=0.045, pad=0.02, shrink=0.78, extend=extend)
    cb.set_label(label, fontsize=7.6); cb.outline.set_visible(False); cb.ax.tick_params(labelsize=7.0, length=2)
    if ticks is not None: cb.set_ticks(ticks, labels=[fmt(t) if fmt else str(t) for t in ticks])
    cb.ax.minorticks_off()

def fig_geography():
    from matplotlib.colors import LogNorm, Normalize
    A = riders(); M = A[A["year"] >= 2020].reset_index(drop=True); S = pd.read_parquet(os.path.join(args.res, "oof_shap.parquet")); geo, k = _geo(); MISS = "#D9D6D0"
    WARM = LinearSegmentedColormap.from_list("warm_deep", ["#FFF4E0", "#F2C36B", "#E89A2B", "#C8321A", "#6E1423"])
    g = M.groupby("dep"); n = g.size(); ok = n >= 50
    fig = F.new_figure(180, 152); gs = fig.add_gridspec(2, 3)
    def panel(pos, letter, title, values, cmap, norm, label, ticks=None, fmt=None, extend="neither"):
        ax = fig.add_subplot(gs[pos]); choropleth(ax, geo, k, lambda c: MISS if (c not in values.index or pd.isna(values[c])) else cmap(norm(values[c])))
        cbar(fig, ax, cmap, norm, label, ticks, fmt, extend); F.panel(fig, ax, letter, title); return ax
    # (a) riders
    panel((0, 0), "a", "Riders, 2020–2025", n.astype(float), F.HEAT, LogNorm(20, 9000), "Riders in injury crashes (log scale)", [30, 100, 300, 1000, 3000], lambda t: f"{t:,}")
    # (b) e-scooter share
    panel((0, 1), "b", "E-scooter share", (g["mode"].apply(lambda s: (s == "escooter").mean()) * 100).where(ok), F.HEAT, Normalize(0, 45), "E-scooter riders (% of riders)", [0, 15, 30, 45], extend="max")
    # (c) adoption of the vehicle code
    by = pd.read_csv(os.path.join(args.audit, "edp_by_dep_year.csv"), dtype={"dep": str}).set_index("dep"); yrs = [int(c) for c in by.columns]
    first = by.apply(lambda r: next((y for y, v in zip(yrs, r.values) if v >= 10), np.nan), axis=1)
    YC = dict(zip(yrs, ["#072A44", "#0B4F6C", "#1E7F86", "#2A9D97", "#6CBDB5", "#A9D9D2", "#DDEFEB"]))
    from matplotlib.colors import ListedColormap, BoundaryNorm
    panel((0, 2), "c", "Adoption of the code", first, ListedColormap([YC[y] for y in yrs]), BoundaryNorm(np.arange(yrs[0] - 0.5, yrs[-1] + 1), len(yrs)), "First year with ten or more e-scooters", yrs)
    # (d) recorded severity
    panel((1, 0), "d", "Recorded severity", (g["ksi"].mean() * 100).where(ok), WARM, Normalize(5, 60), "Killed or hospitalized (% of riders)", [5, 20, 40, 60], extend="max")
    # (e) SHAP attribution of departement
    panel((1, 1), "e", "SHAP attribution", S["dep"].groupby(M["dep"].values).mean().where(ok), DIVW, Normalize(-1.5, 1.5), "Mean SHAP value of département (log-odds)", [-1.5, -0.75, 0, 0.75, 1.5], lambda t: sgn(t, 2) if t else "0", extend="both")
    # (f) unadjusted e-scooter minus bicycle difference
    r = M[M["mode"].isin(["bicycle", "escooter"])].groupby(["dep", "mode"])["ksi"].agg(["mean", "size"]).unstack()
    dif = ((r[("mean", "escooter")] - r[("mean", "bicycle")]) * 100).where((r[("size", "escooter")] >= 30) & (r[("size", "bicycle")] >= 30))
    panel((1, 2), "f", "E-scooter minus bicycle", dif, DIVW, Normalize(-30, 30), "Unadjusted difference in severe share (points)", [-30, -15, 0, 15, 30], lambda t: sgn(t, 0) if t else "0", extend="both")
    print("  map coverage:", int(ok.sum()), "departements with 50+ riders;", int(dif.notna().sum()), "with 30+ riders of each mode;", int(first.notna().sum()), "reached ten e-scooters")
    finish(fig, "Fig03_geography")


def graphical_abstract():
    """Graphical abstract, 330 x 132 mm (ratio 2.5:1): data and geography, method, six findings, four messages."""
    T = audit(); Pd = T[T["group"] == "all"].set_index("factor"); A = riders(); M = A[A["year"] >= 2020]; nm = M["mode"].value_counts(); ks = M.groupby("mode")["ksi"].mean() * 100
    L = pd.read_csv(os.path.join(args.res, "leakage_protocols.csv")); R5 = pd.read_csv(os.path.join(args.res, "robustness_r5_corrected.csv")); geo, k = _geo()
    W, H = 330, 132; fig = plt.figure(figsize=(F.mm(W), F.mm(H))); fig._panels = []
    bg = fig.add_axes([0, 0, 1, 1]); canvas(bg, W, H)
    def sub(x, y, w, h):
        a = fig.add_axes([x / W, y / H, w / W, h / H]); a.tick_params(labelsize=6.8, length=2, pad=1.5); return a
    def head(x, y, t): bg.text(x, y, t, ha="left", va="center", fontsize=8.4, color=F.INK2)
    def ttl(x, y, t): bg.text(x, y, t, ha="left", va="center", fontsize=8.6, color=F.INK)
    # ---- header ----
    bg.text(6, 124.6, "Do SHAP attributions agree with causal estimates?", ha="left", va="center", fontsize=14.5, color=F.INK)
    bg.text(6, 116.6, "Injury severity of e-scooter, e-bike, and bicycle riders in police-reported crashes, France, 2020–2025", ha="left", va="center", fontsize=9.0, color=F.INK2)
    for i, t_ in enumerate([f"{len(M):,} riders", f"{M['Num_Acc'].nunique():,} crashes", "96 départements", "13 pre-specified factors"]):
        node(bg, 196 + i * 32.6, 118.4, 31, 8.6, t_, col=F.INK2, filled=False, fs=7.8, r=1.2)
    bg.plot([6, 324], [112.2, 112.2], color=F.RULE, lw=1.0)
    # ---- 1 data and geography ----
    head(6, 107.6, "DATA: RECORDED SEVERITY VARIES BY PLACE")
    WARM = LinearSegmentedColormap.from_list("warm_deep", ["#FFF4E0", "#F2C36B", "#E89A2B", "#C8321A", "#6E1423"]); g = M.groupby("dep")["ksi"].agg(["mean", "size"]); val = (g["mean"] * 100).where(g["size"] >= 50)
    ax = sub(3, 44, 46, 60); choropleth(ax, geo, k, lambda c: "#D9D6D0" if (c not in val.index or pd.isna(val[c])) else WARM(min(max((val[c] - 5) / 55, 0), 1)), lw=0.25)
    cb = sub(9, 40.6, 30, 1.8); cb.imshow(np.linspace(0, 1, 100)[None, :], cmap=WARM, aspect="auto"); cb.set_yticks([]); cb.set_xticks([0, 99], ["5%", "60%"]); cb.tick_params(length=0, labelsize=6.6, pad=1); [sp.set_visible(False) for sp in cb.spines.values()]
    bg.text(24, 35.6, "killed or hospitalized", ha="center", va="center", fontsize=6.8, color=F.INK2)
    bg.text(24, 31.6, f"Paris {val['75']:.1f}%  ·  highest {val.max():.1f}%", ha="center", va="center", fontsize=6.8, color=F.INK)
    for i, m in enumerate(MODES):
        node(bg, 50, 89 - i * 20.5, 26, 14.5, MODE_LAB[m], f"{int(nm[m]):,} riders", col=MODE_COL[m], fs=8.6, sfs=7.0, r=1.4)
        bg.text(63, 86.5 - i * 20.5, f"{ks[m]:.1f}% severe, unadjusted", ha="center", va="center", fontsize=6.0, color=F.INK2)
    # ---- 2 method ----
    head(84, 107.6, "METHOD")
    node(bg, 84, 88, 32, 15.5, "Prediction", "gradient boosting", col=PET, fs=9.4, sfs=7.4); node(bg, 120, 88, 32, 15.5, "SHAP", "attributions", col=TEAL, fs=9.4, sfs=7.4)
    bg.text(118, 84.6, "developed on 2020–2023, tested once on 2024–2025", ha="center", va="center", fontsize=6.6, color=F.INK2)
    node(bg, 84, 65, 68, 14.5, "Causal estimation", "double machine learning", col=SAF, fs=9.4, sfs=7.4)
    bg.text(118, 61.6, "adjustment sets fixed by the temporal order of variables", ha="center", va="center", fontsize=6.6, color=F.INK2)
    node(bg, 84, 40, 68, 16, "Audit", "direction · magnitude · rank · sources", col=VER, fs=9.8, sfs=7.4)
    bg.text(118, 36.4, "12 robustness checks, placebo, sensitivity analysis", ha="center", va="center", fontsize=6.6, color=F.INK2)
    link(bg, [(76.6, 72.2), (83.4, 72.2)], lw=1.4); link(bg, [(116.4, 95.7), (119.6, 95.7)], lw=1.4)
    bg.plot([156.3, 156.3], [95.7, 51.5], color=F.INK2, lw=1.4, zorder=2); bg.plot([152.4, 156.3], [95.7, 95.7], color=F.INK2, lw=1.4, zorder=2); bg.plot([152.4, 156.3], [72.2, 72.2], color=F.INK2, lw=1.4, zorder=2)
    link(bg, [(156.3, 51.5), (152.6, 51.5)], lw=1.4); link(bg, [(152.4, 44.5), (163.6, 44.5)], lw=1.4)
    # ---- 3 findings: six small charts ----
    head(166, 107.6, "FINDINGS")
    CX = [166, 221, 276]; Y1, H1, Y2, H2 = 76.5, 22.5, 36.5, 23.5
    # (1) SHAP against double ML
    ttl(CX[0], 102.6, "1  Same direction, smaller size"); ax = sub(CX[0] + 8, Y1, 40, H1); lim = (-9, 23); ax.plot(lim, lim, color=F.INK2, lw=0.8, ls=(0, (4, 3)))
    sg = T[T["q_bh"] < 0.05]; b = np.polyfit(sg["dml"], sg["shap_contrast_prob"], 1); xs = np.array([-6, 21]); ax.plot(xs, b[0] * xs + b[1] * 100, color=F.INK, lw=1.3)
    ax.scatter(T["dml"] * 100, T["shap_contrast_prob"] * 100, s=13, color=[TIER_COL[FTIER[f]] for f in T["factor"]], ec=WHITE, lw=0.5, zorder=3)
    ax.set_xlim(*lim); ax.set_ylim(-9, 23); ax.set_xticks([0, 10, 20]); ax.set_yticks([0, 10, 20]); ax.set_xlabel("Causal estimate (points)", fontsize=6.8, labelpad=0.5); ax.set_ylabel("SHAP (points)", fontsize=6.8, labelpad=0.5); F.ygrid(ax, "both")
    ax.text(0.04, 0.95, "17 of 17 effects\nagree in sign", transform=ax.transAxes, ha="left", va="top", fontsize=6.6, color=F.INK, linespacing=1.1); ax.text(0.97, 0.05, f"slope {b[0]:.2f}", transform=ax.transAxes, ha="right", va="bottom", fontsize=6.8)
    # (2) attenuation by factor
    ttl(CX[1], 102.6, "2  SHAP understates the effect"); S9 = Pd[(Pd["q_bh"] < 0.05) & Pd.index.isin(ORDER)].copy(); S9["ratio"] = S9["shap_contrast_prob"].abs() / S9["dml"].abs(); S9 = S9.sort_values("ratio")
    ax = sub(CX[1] + 17, Y1, 31, H1); yy = np.arange(len(S9)); ax.barh(yy, S9["ratio"], height=0.66, color=[TIER_COL[FTIER[f]] for f in S9.index], zorder=2); ax.axvline(1, color=F.INK, lw=1.2)
    for y_, v_ in zip(yy, S9["ratio"]): ax.text(v_ - 0.02 if v_ > 0.5 else v_ + 0.02, y_, f"{v_:.2f}", va="center", ha="right" if v_ > 0.5 else "left", fontsize=5.6, color="#FFFFFF" if v_ > 0.5 else F.INK, zorder=4)
    ax.set_yticks(yy, [SHORT[f] for f in S9.index], fontsize=6.0); ax.tick_params(axis="y", length=0); ax.set_xlim(0, 1.22); ax.set_xticks([0, 0.5, 1.0]); ax.set_ylim(-0.6, len(S9) - 0.4); ax.spines["left"].set_visible(False)
    ax.set_xlabel("SHAP as a fraction of the causal estimate", fontsize=6.8, labelpad=0.5)
    # (3) validation shortcuts
    ttl(CX[2], 102.6, "3  Shortcuts inflate accuracy"); ax = sub(CX[2] + 20, Y1, 28, H1); vv = [L.loc[5, "roc_auc"], L.loc[0, "roc_auc"], L.loc[2, "roc_auc"]]; yy = [2, 1, 0]
    ax.barh(yy, [x - 0.78 for x in vv], left=0.78, height=0.6, color=[VER, PET, SAF], zorder=2)
    for y_, v_ in zip(yy, vv): ax.text(v_ + 0.003, y_, f"{v_:.3f}", va="center", ha="left", fontsize=6.8, color=F.INK)
    ax.set_yticks(yy, ["Tested on\nlater years", "Random\nsplit", "Oversampling\nbefore split"], fontsize=6.4); ax.tick_params(axis="y", length=0); ax.set_xlim(0.78, 0.895); ax.set_xticks([0.80, 0.85]); ax.set_ylim(-0.6, 2.6); ax.spines["left"].set_visible(False)
    ax.set_xlabel("ROC AUC of one fixed model", fontsize=6.8, labelpad=0.5)
    # (4) e-scooter against bicycle by recording context
    ttl(CX[0], 63.8, "4  E-scooter advantage vanishes"); ax = sub(CX[0] + 19, Y2, 29, H2); ax.axvline(0, color=F.INK2, lw=0.8)
    ctx = [("All areas", Pd.loc["A1", "raw_diff"], Pd.loc["A1", "dml"], Pd.loc["A1", "dml_lo"], Pd.loc["A1", "dml_hi"]), ("Early-recording\nareas", R5.iloc[0]["raw_diff"], R5.iloc[0]["theta"], R5.iloc[0]["lo"], R5.iloc[0]["hi"]),
           ("Other areas", R5.iloc[1]["raw_diff"], R5.iloc[1]["theta"], R5.iloc[1]["lo"], R5.iloc[1]["hi"])]
    for y_, (lab, raw, th, lo, hi) in zip([2, 1, 0], ctx):
        ax.annotate("", (th * 100, y_), (raw * 100, y_), arrowprops=dict(arrowstyle="-|>", color="#8F8B83", lw=1.0, mutation_scale=6, shrinkA=3, shrinkB=3.5), zorder=1)
        ax.plot([lo * 100, hi * 100], [y_, y_], color=VER, lw=1.8, zorder=2); ax.scatter(th * 100, y_, s=20, color=VER, ec=WHITE, lw=0.6, zorder=4); ax.scatter(raw * 100, y_, s=16, marker="D", fc=WHITE, ec=F.INK2, lw=0.9, zorder=4)
        ax.text(hi * 100 + 0.8, y_, sgn(th * 100), ha="left", va="center", fontsize=6.6, color=VER); ax.text(raw * 100, y_ + 0.3, sgn(raw * 100), ha="center", va="bottom", fontsize=6.2, color=F.INK2)
    ax.set_yticks([2, 1, 0], [c[0] for c in ctx], fontsize=6.4); ax.tick_params(axis="y", length=0); ax.set_xlim(-17, 10); ax.set_xticks([-10, 0]); ax.set_ylim(-0.6, 2.75); ax.spines["left"].set_visible(False)
    ax.set_xlabel("E-scooter minus bicycle (points)", fontsize=6.8, labelpad=0.5)
    bg.text(CX[0] + 0.5, 60.2, "◇ unadjusted   ● adjusted", ha="left", va="center", fontsize=5.8, color=F.INK2)
    # (5) adjusted effects
    ttl(CX[1], 63.8, "5  What raises or lowers severity"); E = Pd.loc[[f for f in ORDER if Pd.loc[f, "q_bh"] < 0.05]].sort_values("dml"); ax = sub(CX[1] + 17, Y2, 31, H2); yy = np.arange(len(E)); ax.axvline(0, color=F.INK2, lw=0.8)
    ax.barh(yy, E["dml"] * 100, height=0.66, color=[VER if x > 0 else PET for x in E["dml"]], zorder=2); ax.hlines(yy, E["dml_lo"] * 100, E["dml_hi"] * 100, color=F.INK, lw=0.8, zorder=3)
    for y_, (f, r_) in zip(yy, E.iterrows()): ax.text(max(r_["dml_hi"] * 100, 0) + 0.8, y_, sgn(r_["dml"] * 100), va="center", ha="left", fontsize=5.6, color=F.INK)
    ax.set_yticks(yy, [SHORT[f] for f in E.index], fontsize=6.0); ax.tick_params(axis="y", length=0); ax.set_xlim(-8, 29); ax.set_xticks([0, 10, 20]); ax.set_ylim(-0.6, len(E) - 0.4); ax.spines["left"].set_visible(False)
    ax.set_xlabel("Adjusted effect (points, 95% CI)", fontsize=6.8, labelpad=0.5)
    # (6) aligned adjustment sets
    ttl(CX[2], 63.8, "6  Aligned adjustment closes the gap"); P12 = Pd.loc[ORDER]; b1 = np.polyfit(P12["dml"], P12["shap_contrast_prob"], 1)[0]; b2 = np.polyfit(P12["dml_allc"], P12["shap_contrast_prob"], 1)[0]
    ax = sub(CX[2] + 20, Y2, 28, H2); ax.barh([1, 0], [b1, b2], height=0.56, color=[SAF, TEAL], zorder=2); ax.axvline(1, color=F.INK, lw=1.2)
    for y_, v_ in zip([1, 0], [b1, b2]): ax.text(v_ - 0.03, y_, f"{v_:.2f}", va="center", ha="right", fontsize=7.4, color="#FFFFFF")
    ax.set_yticks([1, 0], ["Pre-specified\nadjustment", "Same variables\nas the model"], fontsize=6.4); ax.tick_params(axis="y", length=0); ax.set_xlim(0, 1.12); ax.set_xticks([0, 0.5, 1.0]); ax.set_ylim(-0.6, 1.6); ax.spines["left"].set_visible(False)
    ax.set_xlabel("Slope of SHAP on the causal estimate", fontsize=6.8, labelpad=0.5)
    # ---- 4 messages ----
    bg.plot([6, 324], [26.4, 26.4], color=F.RULE, lw=1.0)
    msgs = [("For analysts", "SHAP gives the direction of an effect,\nnot its magnitude", TEAL), ("For model builders", "Test on later years and check whether\nrecording depends on the outcome", SAF),
            ("For safety statistics", "Compare modes only after adjusting for\nplace; severity labels vary by area", PET), ("For policy", "Separate riders from heavy vehicles\nand address single-vehicle crashes", VER)]
    for i, (hd, tx, col) in enumerate(msgs):
        x = 6 + i * 80.5; bg.add_patch(FancyBboxPatch((x, 4), 3.0, 18.5, boxstyle="round,pad=0,rounding_size=1.2", fc=col, ec="none"))
        bg.text(x + 6, 18.6, hd, ha="left", va="center", fontsize=9.2, color=col); bg.text(x + 6, 9.6, tx, ha="left", va="center", fontsize=7.8, color=F.INK, linespacing=1.15)
    finish(fig, "GraphicalAbstract")


FIGS = {"fig01": fig01, "fig02": fig02, "fig03": fig_geography, "fig04": fig_recording, "fig05": fig_performance, "fig06": fig_shap, "fig07": fig_audit, "fig08": fig_sources, "fig09": fig_groups, "fig10": fig_robustness, "ga": graphical_abstract}
for k, fn in FIGS.items():
    if not args.only or args.only == k: fn()
