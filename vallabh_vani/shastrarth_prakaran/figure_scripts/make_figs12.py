#!/usr/bin/env python3
"""Figures for Śāstrārtha Prakaraṇa, Lecture 12 (session of 2026-10-03).

Layout is computed top-down: every text block is measured with the Agg renderer
first, boxes are sized to their contents, and the figure height is set to the
sum of the blocks. Axes run 0-100 both ways; vertical sizes are converted from
inches. After drawing, every registered text is checked against its box.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import (  # noqa: E402
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    PathPatch,
    Polygon,
)
from matplotlib.path import Path as MPath  # noqa: E402

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"
CONCEALED = "#E6E0D8"

WIDTH_IN = 6.2
LS = 1.32
plt.rcParams["font.family"] = "DejaVu Sans"
OUT = Path(__file__).resolve().parent / "figs12"
OUT.mkdir(exist_ok=True)
PROBLEMS: list[str] = []

_MFIG = plt.figure(figsize=(WIDTH_IN, 6), dpi=200)
_MREN = _MFIG.canvas.get_renderer()


def measure(s: str, size: float, weight: str = "normal", style: str = "normal") -> tuple[float, float]:
    """Width and height of a text block, in inches."""
    t = _MFIG.text(0, 0, s, fontsize=size, fontweight=weight, fontstyle=style, linespacing=LS)
    bb = t.get_window_extent(renderer=_MREN)
    t.remove()
    return bb.width / 200, bb.height / 200


def xu(units: float) -> float:
    """Horizontal data units to inches."""
    return units * WIDTH_IN / 100


class Fig:
    def __init__(self, name: str, height_in: float):
        self.name = name
        self.h = height_in
        self.fig = plt.figure(figsize=(WIDTH_IN, height_in), dpi=200)
        self.fig.patch.set_facecolor(PALE)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis("off")
        self.checks: list[tuple[object, tuple[float, float, float, float], str]] = []

    def yu(self, inches: float) -> float:
        return inches * 100 / self.h

    def box(self, x, y, w, h, fc=SAND, ec=TEAL, lw=1.1, z=1):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                         mutation_scale=55, fc=fc, ec=ec, lw=lw, zorder=z))
        return (x, y, w, h)

    def text(self, x, y, s, size=6.6, color=INK, weight="normal", ha="center", va="top",
             style="normal", inside=None, label=""):
        t = self.ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va,
                         fontstyle=style, zorder=4, linespacing=LS)
        if inside is not None:
            self.checks.append((t, inside, label or s.split("\n")[0][:28]))
        return t

    def arrow(self, x1, y1, x2, y2, color=OCHRE, lw=1.3, ms=9):
        self.ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=ms,
                                          color=color, lw=lw, zorder=3))

    def save(self):
        self.fig.canvas.draw()
        ren = self.fig.canvas.get_renderer()
        inv = self.ax.transData.inverted()
        for t, (x, y, w, h), label in self.checks:
            bb = t.get_window_extent(renderer=ren)
            (x0, y0), (x1, y1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
            if x0 < x + 0.6 or x1 > x + w - 0.6 or y0 < y + 0.3 or y1 > y + h - 0.3:
                PROBLEMS.append(f"{self.name}: '{label}' text x[{x0:.1f},{x1:.1f}] y[{y0:.1f},{y1:.1f}]"
                                f" vs box x[{x:.1f},{x + w:.1f}] y[{y:.1f},{y + h:.1f}]")
        path = OUT / f"{self.name}.png"
        self.fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.12, facecolor=PALE)
        plt.close(self.fig)
        print("wrote", path.name, f"({self.h:.2f} in)")


# ------------------------------------------------------------------ blocks
# Each block knows its height in inches and draws itself below a top y (units).
class Title:
    def __init__(self, s, size=12.0, after=0.07):
        self.s, self.size, self.after = s, size, after
        self.hi = measure(s, size, "bold")[1] + after

    def draw(self, f, top):
        f.text(50, top, self.s, size=self.size, weight="bold")


class Sub:
    def __init__(self, s, size=7.3, after=0.12):
        self.s, self.size = s, size
        self.hi = measure(s, size, style="italic")[1] + after

    def draw(self, f, top):
        f.text(50, top, self.s, size=self.size, color=GREY, style="italic")


class Gap:
    def __init__(self, inches):
        self.hi = inches

    def draw(self, f, top):
        pass


class Columns:
    """A row of boxes, each with a centred header and a top-anchored body."""

    PT, GAP, PB = 0.075, 0.075, 0.09

    def __init__(self, cols, hsize=8.6, bsize=6.5, after=0.1, equal=True):
        # cols: list of dicts with x, w, head, body and optional ec, lw, fc, hcolor
        self.cols, self.hsize, self.bsize, self.after = cols, hsize, bsize, after
        need = []
        for c in cols:
            hw, hh = measure(c["head"], c.get("hsize", hsize), "bold")
            bw, bh = measure(c["body"], c.get("bsize", bsize)) if c["body"] else (0, 0)
            avail = xu(c["w"]) - 0.16
            if max(hw, bw) > avail:
                PROBLEMS.append(f"column '{c['head'][:20]}' too wide: {max(hw, bw):.2f} > {avail:.2f} in")
            c["_hh"], c["_bh"] = hh, bh
            need.append((hh, bh if c["body"] else None))
        hh_max = max(h for h, _ in need)
        self.box_hi = max(self.PT + hh_max + (self.GAP + b if b is not None else 0) + self.PB
                          for _, b in need)
        self.hi = self.box_hi + after
        self.equal = equal
        self.boxes = []

    def draw(self, f, top):
        bh_u = f.yu(self.box_hi)
        hh_max = max(c["_hh"] for c in self.cols)
        for c in self.cols:
            rect = f.box(c["x"], top - bh_u, c["w"], bh_u, fc=c.get("fc", SAND),
                         ec=c.get("ec", TEAL), lw=c.get("lw", 1.1))
            self.boxes.append(rect)
            cx = c["x"] + c["w"] / 2
            y = top - f.yu(self.PT)
            f.text(cx, y, c["head"], size=c.get("hsize", self.hsize),
                   color=c.get("hcolor", c.get("ec", TEAL)), weight="bold", inside=rect,
                   label=c["head"])
            if c["body"]:
                y -= f.yu(hh_max + self.GAP)
                f.text(cx, y, c["body"], size=c.get("bsize", self.bsize), inside=rect,
                       label=c["head"] + " body")
        self.top, self.bottom = top, top - bh_u


class Banner:
    def __init__(self, s, size=6.9, pad=0.085, after=0.0, fc=OCHRE, color="white"):
        self.s, self.size, self.pad, self.fc, self.color = s, size, pad, fc, color
        w, h = measure(s, size, "bold")
        if w > xu(96) - 0.2:
            PROBLEMS.append(f"banner too wide: {s[:30]}")
        self.box_hi = h + 2 * pad
        self.hi = self.box_hi + after

    def draw(self, f, top):
        h = f.yu(self.box_hi)
        rect = f.box(2, top - h, 96, h, fc=self.fc, ec=self.fc, lw=0.8)
        f.text(50, top - h / 2, self.s, size=self.size, color=self.color, weight="bold",
               va="center", inside=rect, label="banner")


class Custom:
    def __init__(self, hi, fn):
        self.hi, self.fn = hi, fn

    def draw(self, f, top):
        self.fn(f, top)


def build(name, blocks, top_pad=0.05, bottom_pad=0.04):
    total = top_pad + sum(b.hi for b in blocks) + bottom_pad
    f = Fig(name, total)
    y = 100 - f.yu(top_pad)
    for b in blocks:
        b.draw(f, y)
        y -= f.yu(b.hi)
    f.save()


# ------------------------------------------------------------------ Figure 1
def fig1():
    head_h = measure("EXPERIENCE", 9, "bold")[1]
    sub_h = measure("conditions", 6.9, style="italic")[1]
    draw_h = 0.62
    cap = "vertical vs\nhorizontal"
    cap_h = measure(cap, 5.6)[1]
    left_body = ("Equal lines look unequal; a near tree looks\n"
                 "bigger than the far mountain; the sun looks\n"
                 "tiny; the mirror shows your face; the rails\n"
                 "seem to meet. Each has its own conditions,\n"
                 "so none of this is wrong as experience.")
    right_body = ("The child: \u201cthe sun really is the size\n"
                  "of a football.\u201d\n\n"
                  "\u201cI am there, inside the mirror.\u201d\n\n"
                  "\u201cThe rails really do meet.\u201d\n\n"
                  "Sūradāsa's dog in the temple of glass,\n"
                  "seeing dogs on every side, glares and\n"
                  "glares until it dies.\n\n"
                  "What you see you do not accept; what\n"
                  "you accept you do not see: the object of\n"
                  "understanding is anya, other.")
    lb_h = measure(left_body, 6.5)[1]
    rb_h = measure(right_body, 6.5)[1]
    pt, g = 0.075, 0.06
    left_need = pt + head_h + g + sub_h + 0.1 + draw_h + 0.05 + cap_h + 0.12 + lb_h + 0.1
    right_need = pt + head_h + g + sub_h + 0.12 + rb_h + 0.1
    box_hi = max(left_need, right_need)

    def draw(f, top):
        bh = f.yu(box_hi)
        left = f.box(3, top - bh, 43, bh, ec=TEAL, lw=1.2)
        right = f.box(54, top - bh, 43, bh, ec=MAROON, lw=1.6)
        for cx, rect, head, sub, col in ((24.5, left, "EXPERIENCE", "conditions of perception: no illusion", TEAL),
                                         (75.5, right, "UNDERSTANDING", "taking the appearance for the thing", MAROON)):
            y = top - f.yu(pt)
            f.text(cx, y, head, size=9, color=col, weight="bold", inside=rect)
            y -= f.yu(head_h + g)
            f.text(cx, y, sub, size=6.9, color=col, style="italic", inside=rect)
        # drawings
        y_d_top = top - f.yu(pt + head_h + g + sub_h + 0.1)
        y_d_bot = y_d_top - f.yu(draw_h)
        ax = f.ax
        mid = (y_d_top + y_d_bot) / 2
        # equal lines: the vertical's length in inches equals the horizontal's
        L_in = 0.46
        hx0 = 11 - (L_in / (WIDTH_IN / 100)) / 2
        hx1 = 11 + (L_in / (WIDTH_IN / 100)) / 2
        ax.plot([hx0, hx1], [y_d_bot, y_d_bot], color=INK, lw=1.0)
        ax.plot([11, 11], [y_d_bot, y_d_bot + f.yu(L_in)], color=INK, lw=1.0)
        # Mueller-Lyer: closed (arrowheads) above, open (fins) below
        fin_x, fin_y = 2.2, f.yu(0.12)
        ya, yb = mid + f.yu(0.16), mid - f.yu(0.16)
        ax.plot([19, 29], [ya, ya], color=INK, lw=1.0)
        for sx, sgn in ((19, 1), (29, -1)):
            ax.plot([sx, sx + sgn * fin_x], [ya, ya + fin_y], color=INK, lw=1.0)
            ax.plot([sx, sx + sgn * fin_x], [ya, ya - fin_y], color=INK, lw=1.0)
        ax.plot([19, 29], [yb, yb], color=INK, lw=1.0)
        for sx, sgn in ((19, -1), (29, 1)):
            ax.plot([sx, sx + sgn * fin_x], [yb, yb + fin_y], color=INK, lw=1.0)
            ax.plot([sx, sx + sgn * fin_x], [yb, yb - fin_y], color=INK, lw=1.0)
        # tall near tree, small far mountain, small corner sun
        ground = y_d_bot
        ax.add_patch(Polygon([[38.6, ground + f.yu(0.05)], [41.4, ground + f.yu(0.24)],
                              [44.2, ground + f.yu(0.05)]], closed=True, fc="#D9CBB5", ec=GREY,
                             lw=0.8, zorder=2))
        ax.plot([35.2, 35.2], [ground, ground + f.yu(0.1)], color="#5B4636", lw=1.4, zorder=3)
        ax.add_patch(Polygon([[32.6, ground + f.yu(0.09)], [35.2, ground + f.yu(0.6)],
                              [37.8, ground + f.yu(0.09)]], closed=True, fc="#6E8B5E",
                             ec="#55704A", lw=0.7, zorder=3))
        ax.add_patch(Circle((43.6, y_d_top - f.yu(0.06)), 0.75, fc=OCHRE, ec=OCHRE, zorder=3))
        ax.plot([31, 45.4], [ground, ground], color=GREY, lw=0.6)
        y_cap = y_d_bot - f.yu(0.05)
        f.text(11, y_cap, cap, size=5.6, color=GREY, inside=left, label="cap1")
        f.text(24, y_cap, "closed vs open\narrow", size=5.6, color=GREY, inside=left, label="cap2")
        f.text(38.4, y_cap, "near tree, far\nmountain, sun", size=5.6, color=GREY, inside=left,
               label="cap3")
        y_body = y_cap - f.yu(cap_h + 0.12)
        f.text(24.5, y_body, left_body, size=6.5, inside=left, label="left body")
        f.text(75.5, top - f.yu(pt + head_h + g + sub_h + 0.12), right_body, size=6.5,
               inside=right, label="right body")
        f.arrow(47.2, top - bh / 2, 52.8, top - bh / 2, lw=1.5)
        f.text(50, top - bh / 2 - f.yu(0.06), "misread", size=5.4, color=OCHRE)

    build("fig1_experience_understanding", [
        Title("Where does the error lie? Experience and understanding"),
        Sub("anyakhyāti is a matter of understanding, not of experience"),
        Custom(box_hi + 0.12, draw),
        Banner("viṣayo Bhagavān, viṣayatā māyā-janyā\n"
               "the object as it is is Bhagavān; the object as we interpret it is born of Māyā",
               size=7.0),
    ])


# ------------------------------------------------------------------ Figure 2
def fig2():
    top_box = Columns([dict(x=22, w=56, head="SACCIDĀNANDA BRAHMAN",
                            body="sat = cit = ānanda: one homogeneous character (the dharmī)",
                            ec=MAROON, lw=1.6, hsize=9.2, bsize=6.8)], after=0.0)

    def split_arrow(f, top):
        bot = top - f.yu(0.5)
        f.arrow(50, top - f.yu(0.04), 50, bot + f.yu(0.04), lw=1.6)
        f.text(52, top - f.yu(0.09), "sa imam evātmānaṁ dvedhāpātayat", size=6.8, color=OCHRE,
               ha="left", style="italic")
        f.text(52, top - f.yu(0.27), "(BU 1.4.3): division, not vikāra", size=6.3, color=OCHRE,
               ha="left")
        f.text(4, top - f.yu(0.12), "gold → ornament is\nonly a partial example", size=6.0,
               color=GREY, ha="left", style="italic")

    xs, w = [3, 35.5, 68], 29
    mid = Columns([
        dict(x=xs[0], w=w, head="SATTĀ", body="existence with cetanā\nwithdrawn from it"),
        dict(x=xs[1], w=w, head="CETANĀ", body="consciousness with\npriyatā withdrawn"),
        dict(x=xs[2], w=w, head="PRIYATĀ", body="dearness, the \u201cface\u201d of\nānanda (TU 2.5.1)"),
    ], hsize=8.4, bsize=6.5, after=0.0)

    def note_arrows(f, top):
        f.text(50, top - f.yu(0.04), "three separated dharmas, no longer homogeneous", size=6.2,
               color=GREY, style="italic")
        for x in xs:
            f.arrow(x + w / 2, top - f.yu(0.19), x + w / 2, top - f.yu(0.4), lw=1.3)

    bot = Columns([
        dict(x=xs[0], w=w, head="PRAKṚTI", body="sattva · rajas · tamas"),
        dict(x=xs[1], w=w, head="PURUṢA",
             body="nirguṇa: not without qualities,\nbut without prakṛti's guṇas;\nformless, like consciousness"),
        dict(x=xs[2], w=w, head="ANTARYĀMIN",
             body="Īśvara: saccidānanda,\na non-split character;\nhe enters and hides within",
             ec=MAROON, lw=1.6),
    ], hsize=8.4, bsize=6.4, after=0.12)

    build("fig2_self_splitting", [
        Title("Not modification but self-splitting", after=0.1),
        top_box,
        Custom(0.52, split_arrow),
        mid,
        Custom(0.44, note_arrows),
        bot,
        Banner("first self-division, then self-multiplication: tat sṛṣṭvā tad evānuprāviśat (TU 2.6.1)",
               size=6.8),
    ])


# ------------------------------------------------------------------ Figure 3
def fig3():
    cols = Columns([
        dict(x=3, w=45, head="ŚAṄKARA", body=(
            "satyaṁ jñānam anantaṁ brahma (TU 2.1.1)\n"
            "= the svarūpa-lakṣaṇa, Brahman's own nature\n\n"
            "yato vā imāni bhūtāni jāyante (TU 3.1.1)\n"
            "= merely a kāraṇa-lakṣaṇa, a causal mark\n\n"
            "The world needs an added factor.\n"
            "Dongre Mahārāja's quip: \u201cpure gold cannot\n"
            "be shaped; add a little copper\u201d, and the\n"
            "copper is māyā.")),
        dict(x=52, w=45, head="VALLABHA", ec=MAROON, lw=1.6, body=(
            "Vyāsa's own definition: janmādy asya yataḥ\n"
            "(BS 1.1.2), proved by śāstra (BS 1.1.3)\n\n"
            "satyaṁ jñānam anantam describes Brahman\n"
            "a posteriori, after the self-splitting\n\n"
            "Pure gold can be shaped: gold biscuits.\n"
            "Copper is only for \u201crough use\u201d; red, yellow,\n"
            "blue and white golds are alloys.\n\n"
            "Avikṛta-pariṇāma: by self-splitting,\n"
            "with no copper added")),
    ], hsize=9, bsize=6.5, after=0.13)
    build("fig3_definitions_gold", [
        Title("Svarūpa-lakṣaṇa or kāraṇa-lakṣaṇa?"),
        Sub("two readings of the Upaniṣadic definitions of Brahman"),
        cols,
        Banner("every example is partial: sādṛśyam upamā bhede\n"
               "a resemblance between two different things must keep some difference", size=7.0),
    ])


# ------------------------------------------------------------------ Figure 4
def fig4():
    w = 30
    cols = Columns([
        dict(x=2.5, w=w, head="SAT → SATYA", body=(
            "satya = sat + tyat\n"
            "sat: what is revealed\n"
            "tyat: what is unrevealed\n\n"
            "No truth is wholly revealed\n"
            "or wholly unrevealed.\n\n"
            "The pen: show the point and\n"
            "the cylinder hides; show the\n"
            "cylinder and the point hides.")),
        dict(x=35, w=w, head="CIT → JÑĀNA", body=(
            "Consciousness is \u201ccategorical\u201d,\n"
            "self-dependent and formless.\n\n"
            "Knowledge must have an object:\n"
            "\u201cknowledge of what?\u201d\n\n"
            "When consciousness takes on\n"
            "a shape, it becomes jñāna.\n\n"
            "Every knowing hides an\n"
            "unknowing: na budhyate.")),
        dict(x=67.5, w=w, head="ĀNANDA → PRIYA, ANANTA", hsize=7.6, ec=MAROON, lw=1.6, body=(
            "Priya needs a lover:\n"
            "\u201cdear to whom?\u201d\n\n"
            "Ananta in two senses:\n"
            "1. no boundary of place\n"
            "(Bombay), of time (born\n"
            "1940), of object (\u201cI am\n"
            "not the laptop\u201d)\n"
            "2. innumerable names, forms,\n"
            "powers and functions")),
    ], hsize=8.4, bsize=6.4, after=0.13)
    build("fig4_satyam_jnanam_anantam", [
        Title("Satyaṁ jñānam anantam, read after the split"),
        Sub("each term is the a-posteriori face of one strand of Saccidānanda"),
        cols,
        Banner("anupraveśa: tat sṛṣṭvā tad evānuprāviśat (TU 2.6.1)\n"
               "the cause enters its effect: gold in the ornament, milk in the curd,\n"
               "the parents' eyes, nose and ears in the child", size=6.9),
    ])


# ------------------------------------------------------------------ Figure 5
def fig5():
    top = Columns([
        dict(x=3, w=44, head="LOGIC: YES OR NO", body=(
            "nothing in between yes and no\n\n"
            "if saguṇa, then not nirguṇa\n"
            "if finite, then not infinite\n"
            "if jaḍa, then not jīva, and back\n"
            "if Īśvara, then not jaḍa or jīva\n\n"
            "\u201cthey wanted to treat Brahman\n"
            "not as verbal but logical\u201d")),
        dict(x=53, w=44, head="ŚRUTI: BOTH, IN ONE BRAHMAN", ec=MAROON, lw=1.6, hsize=8.2, body=(
            "sac ca tyac ca: revealed, unrevealed\n"
            "niruktaṁ cāniruktaṁ ca: defined, undefined\n"
            "vijñānaṁ cāvijñānaṁ ca: knowing, unknowing\n"
            "satyaṁ cānṛtaṁ ca: truth, untruth\n"
            "(TU 2.6.1)\n\n"
            "Brahman is viruddha-dharmāśraya")),
    ], hsize=8.8, bsize=6.4, after=0.1)

    def neq(f, ytop):
        mid = top.top - (top.top - top.bottom) / 2
        f.text(50, mid, "≠", size=15, color=OCHRE, va="center")

    bottom = Columns([
        dict(x=3, w=44, head="ŚAṄKARA", ec=GREY, hcolor=GREY, fc=PALE, body=(
            "scolds the \u201clogician-bulls without\n"
            "horns or tails\u201d, then sets Brahman\n"
            "right by logic himself")),
        dict(x=53, w=44, head="VALLABHA", ec=MAROON, lw=1.6, fc=PALE, body=(
            "either let the logicians argue, or do\n"
            "not treat Brahman with logic at all:\n"
            "treat it as śruti-śāstra")),
    ], hsize=8.2, bsize=6.4, after=0.12)
    build("fig5_logic_vs_sruti", [
        Title("Logic's either/or and the śruti's both/and", after=0.12),
        top,
        Custom(0.0, neq),
        bottom,
        Banner("naiṣā tarkeṇa matir āpaneyā (Kaṭha 1.2.9): this understanding is not to be removed by reasoning",
               size=6.7),
    ])


# ------------------------------------------------------------------ Figure 6
def bulged_square(cx, cy, sx, sy, bulge_x, bulge_y):
    """A square (sx, sy in data units) whose sides bow outward."""
    hx, hy = sx / 2, sy / 2
    pts = [(cx - hx, cy - hy), (cx + hx, cy - hy), (cx + hx, cy + hy), (cx - hx, cy + hy)]
    verts, codes = [pts[0]], [MPath.MOVETO]
    for i in range(4):
        p0, p1 = pts[i], pts[(i + 1) % 4]
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        if p0[1] == p1[1]:  # horizontal side
            ctrl = (mx, my + (bulge_y if my > cy else -bulge_y) * 2)
        else:
            ctrl = (mx + (bulge_x if mx > cx else -bulge_x) * 2, my)
        verts += [ctrl, p1]
        codes += [MPath.CURVE3, MPath.CURVE3]
    verts.append(pts[0])
    codes.append(MPath.CLOSEPOLY)
    return MPath(verts, codes)


def fig6():
    head_h = measure("ONE GLOBE", 8.4, "bold")[1]
    t1 = "the continents are divided,\nyet none is apart from the\none globe of the earth"
    t2 = "blow it up: the square swells\ninto a circle; the \u201ccircular\nsquare\u201d is not mithyā"
    t3 = ("India's stock example:\n"
          "śaśa-śṛṅga, the hare's horn;\n"
          "but genetic engineering can\n"
          "now grow one.\n\n"
          "The West's: the circular\n"
          "square; but draw it on a\n"
          "balloon, or on the earth.\n\n"
          "No thing is mithyā; only\n"
          "our understanding can be.")
    draw_h = 1.05
    pt = 0.075
    need12 = pt + head_h + 0.08 + draw_h + 0.08 + max(measure(t1, 6.3)[1], measure(t2, 6.3)[1]) + 0.09
    need3 = pt + head_h + 0.08 + measure(t3, 6.3)[1] + 0.09
    box_hi = max(need12, need3)

    def draw(f, top):
        bh = f.yu(box_hi)
        ax = f.ax
        p1 = f.box(2.5, top - bh, 30, bh, ec=TEAL, fc=PALE)
        p2 = f.box(35, top - bh, 30, bh, ec=TEAL, fc=PALE)
        p3 = f.box(67.5, top - bh, 30, bh, ec=MAROON, lw=1.6, fc=PALE)
        y = top - f.yu(pt)
        f.text(17.5, y, "ONE GLOBE", size=8.4, color=TEAL, weight="bold", inside=p1)
        f.text(50, y, "SQUARE ON A BALLOON", size=8.4, color=TEAL, weight="bold", inside=p2)
        f.text(82.5, y, "WHAT IS MITHYĀ?", size=8.4, color=MAROON, weight="bold", inside=p3)
        d_top = y - f.yu(head_h + 0.08)
        d_mid = d_top - f.yu(draw_h / 2)
        r_in = 0.48
        ax.add_patch(Ellipse((17.5, d_mid), 2 * r_in / (WIDTH_IN / 100), f.yu(2 * r_in),
                             fc="#DCE6E4", ec=TEAL, lw=1.0, zorder=2))
        sx, sy = 1 / (WIDTH_IN / 100), f.yu(1)  # one inch in x and y units
        blobs = [
            [(-0.30, 0.12), (-0.18, 0.30), (-0.02, 0.24), (-0.06, 0.06), (-0.22, -0.02)],
            [(0.04, 0.22), (0.22, 0.30), (0.32, 0.12), (0.14, 0.04)],
            [(-0.26, -0.10), (-0.10, -0.06), (-0.04, -0.30), (-0.20, -0.36)],
            [(0.06, -0.08), (0.30, -0.04), (0.30, -0.26), (0.10, -0.28)],
        ]
        for b in blobs:
            ax.add_patch(Polygon([(17.5 + px * sx, d_mid + py * sy) for px, py in b], closed=True,
                                 fc="#C9B79A", ec=GREY, lw=0.6, zorder=3))
        # balloon stages: square -> bulging -> circle
        sizes = [(40.0, 0.19, 0.0), (48.8, 0.25, 0.02), (59.5, 0.32, 0.05)]
        for i, (cx, s_in, b_in) in enumerate(sizes):
            ax.add_patch(Ellipse((cx, d_mid), (s_in * 1.5) * sx, (s_in * 1.9) * sy, fc="#F3DCCB",
                                 ec=OCHRE, lw=0.8, zorder=2))
            ax.add_patch(PathPatch(bulged_square(cx, d_mid, s_in * 0.8 * sx, s_in * 0.8 * sy,
                                                 b_in * sx, b_in * sy),
                                   fc="none", ec=MAROON, lw=1.0, zorder=3))
            if i < 2:
                nx, ns, _ = sizes[i + 1]
                f.arrow(cx + s_in * 0.75 * sx + 0.5, d_mid, nx - ns * 0.75 * sx - 0.5, d_mid,
                        lw=1.0, ms=6)
        y_t = d_top - f.yu(draw_h + 0.08)
        f.text(17.5, y_t, t1, size=6.3, inside=p1, label="p1")
        f.text(50, y_t, t2, size=6.3, inside=p2, label="p2")
        f.text(82.5, y - f.yu(head_h + 0.08), t3, size=6.3, inside=p3, label="p3")

    build("fig6_anantamurti_globe", [
        Title("Avibhaktaṁ vibhaktimat: figures on a curved surface", after=0.1),
        Custom(box_hi + 0.13, draw),
        Banner("anantamūrti tad brahma avibhaktaṁ vibhaktimat (TDN 26)\n"
               "all shapes at once, divided yet undivided: sarvaṁ khalv idaṁ brahma", size=7.0),
    ])


# ------------------------------------------------------------------ Figure 7
def fig7():
    w = 30
    cols = Columns([
        dict(x=2.5, w=w, head="SVABHĀVA", body=(
            "by nature\n\n"
            "as a triangle comes from\n"
            "three lines: \u201cmathematical\u201d\n\n"
            "no choice: the triangle is\n"
            "\u201chelpless\u201d; four lines may\n"
            "look like a circle, a triangle\n"
            "or a square\n\n"
            "like the pull of a mass,\n"
            "or of a magnet")),
        dict(x=35, w=w, head="SĀMARTHYA", body=(
            "by power: yoga-bala\n\n"
            "governed by will, but the\n"
            "self is not involved: the\n"
            "yogī's many bodies, the\n"
            "digitally made musicians\n\n"
            "\u201cas if real, but it is not\n"
            "real\u201d: virtual reality\n\n"
            "a world made \u201cout of\n"
            "nothing\u201d is of this kind")),
        dict(x=67.5, w=w, head="ICCHĀ-MĀTRA", ec=MAROON, lw=1.6, body=(
            "by will alone (TDN 27)\n\n"
            "\u201cLet me multiply my sattā,\n"
            "my cetanā, my ānanda\u201d\n\n"
            "self-splitting and self-\n"
            "multiplication together,\n"
            "like pedals and the\n"
            "moving bicycle\n\n"
            "real, like a spark from fire;\n"
            "the will is satī, never false")),
    ], hsize=8.8, bsize=6.4, after=0.13)
    build("fig7_svabhava_samarthya_iccha", [
        Title("How could a world come from its source?"),
        Sub("three models, and Mahāprabhuji's tad-icchā-mātrataḥ"),
        cols,
        Banner("Brahman \u201cincludes everything and excludes nothing\u201d:\n"
               "a grand unification, so nothing in its world is virtual", size=7.0),
    ])


# ------------------------------------------------------------------ Figure 8
def fig8():
    rows = [
        ("JAḌA", "from the sad-aṁśa", [1, 0, 0],
         "formless by default;\nform by contingency\n(clay → pot, lamp, cup)"),
        ("JĪVA", "from the cid-aṁśa,\nlike sparks", [1, 1, 0],
         "formless; form from\nobject and body, as\nin a mirror"),
        ("ANTARYĀMIN", "from the ānandāṁśa,\nhaṁsa in the heart", [1, 1, 1],
         "ānanda is form itself:\nsākāra, sarvākāra\n(the viśvarūpa)"),
    ]
    head_h = measure("JAḌA", 8.2, "bold")[1]
    row_need = 0.0
    for name, sub, _, form in rows:
        row_need = max(row_need, 0.1 + head_h + 0.04 + measure(sub, 6.0)[1] + 0.12,
                       0.1 + measure(form, 6.1)[1] + 0.12)
    col_head_h = measure("SAT", 8.6, "bold")[1]
    x0, colw = 25, 15.5

    def grid(f, top):
        y = top
        for j, c in enumerate(["SAT", "CIT", "ĀNANDA"]):
            f.text(x0 + colw * j + colw / 2, y, c, size=8.6, color=TEAL, weight="bold")
        f.text(x0 + colw * 3 + 13.75, y, "FORM (ĀKĀRA)", size=8.6, color=MAROON, weight="bold")
        y -= f.yu(col_head_h + 0.06)
        rh = f.yu(row_need)
        for i, (name, sub, pattern, form) in enumerate(rows):
            last = i == 2
            ec, lw = (MAROON, 1.6) if last else (TEAL, 1.0)
            yb = y - rh
            lab = f.box(2.5, yb + 1.5, 20.5, rh - 3.0, ec=ec, lw=lw)
            f.text(12.75, y - 1.5 - f.yu(0.05), name, size=8.2, color=ec, weight="bold", inside=lab)
            f.text(12.75, y - 1.5 - f.yu(0.05 + head_h + 0.04), sub, size=6.0, inside=lab,
                   label=name + " sub")
            for j, on in enumerate(pattern):
                cx = x0 + colw * j
                cell = f.box(cx + 1.3, yb + 1.5, colw - 2.6, rh - 3.0, fc=SAND if on else CONCEALED,
                             ec=OCHRE if on else GREY, lw=0.9)
                f.text(cx + colw / 2, yb + rh / 2, "manifest" if on else "concealed\n(tirohita)",
                       size=6.4 if on else 6.0, color=INK if on else GREY, va="center",
                       weight="bold" if on else "normal", inside=cell, label=f"{name}{j}")
            fx = x0 + colw * 3 + 1
            fbox = f.box(fx + 0.3, yb + 1.5, 25.2, rh - 3.0, ec=ec, lw=lw, fc=PALE)
            f.text(fx + 12.9, y - 1.5 - f.yu(0.05), form, size=6.1, inside=fbox,
                   label=name + " form")
            y = yb

    grid_hi = col_head_h + 0.06 + 3 * row_need + 0.06
    note = "ataeva nirākārau pūrvāv ānanda-lopataḥ: where ānanda is eclipsed, form goes with it"
    note_h = measure(note, 6.6, style="italic")[1]

    def note_fn(f, top):
        f.text(50, top, note, size=6.6, color=OCHRE, style="italic")

    turned = Columns([
        dict(x=2.5, w=46, head="ŚAṄKARA", fc=PALE, body="jīva and jaḍa are sākāra;\nBrahman is nirākāra"),
        dict(x=51.5, w=46, head="MAHĀPRABHUJI", ec=MAROON, lw=1.6, fc=PALE,
             body="Brahman is sākāra; jaḍa and jīva\nare nirākāra by default"),
    ], hsize=8.2, bsize=6.5, after=0.12)
    build("fig8_anya_linata_grid", [
        Title("Pūrvayor anya-līnatā: manifest and concealed", after=0.12),
        Custom(grid_hi, grid),
        Custom(note_h + 0.12, note_fn),
        turned,
        Banner("the table turned: ānanda alone is capable of form (ākāra-samartha)", size=7.0),
    ])


if __name__ == "__main__":
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        fn()
    if PROBLEMS:
        print("\nLAYOUT CHECK FAILED:")
        for p in PROBLEMS:
            print("  ", p)
    else:
        print("\nlayout check: every registered text sits inside its box")
