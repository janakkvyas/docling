#!/usr/bin/env python3
"""Figures for Śāstrārtha Prakaraṇa, Lecture 13 (session of 2026-10-17).

Layout is computed top-down: every text block is measured with the Agg renderer
first, boxes are sized to their contents, and the figure height is set to the
sum of the blocks. Axes run 0-100 both ways; vertical sizes are converted from
inches. After drawing, every registered text is checked against its box.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon  # noqa: E402

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
OUT = Path(__file__).resolve().parent / "figs13"
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

    def __init__(self, cols, hsize=8.6, bsize=6.5, after=0.1):
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
                   color=c.get("hcolor", c.get("ec", TEAL)), weight="bold", inside=rect, label=c["head"])
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


def labelled_box(f, x, y, w, h, head, body, ec=TEAL, fc=SAND, hsize=7.2, bsize=6.3, hcolor=None, lw=1.1):
    """A box with a centred bold header and top-anchored body; returns rect."""
    rect = f.box(x, y, w, h, fc=fc, ec=ec, lw=lw)
    hh = measure(head, hsize, "bold")[1]
    ty = y + h - f.yu(0.06)
    f.text(x + w / 2, ty, head, size=hsize, weight="bold", color=hcolor or ec, inside=rect, label=head)
    if body:
        f.text(x + w / 2, ty - f.yu(hh + 0.05), body, size=bsize, inside=rect, label=head + " body")
    return rect


# ------------------------------------------------------------------ Figure 1
def fig1():
    chain = ["Brahman", "ākāśa (space)", "vāyu (air)", "agni (fire)", "āpas (water)",
             "pṛthivī (earth)", "oṣadhi: \u201cchemical properties\u201d", "anna (food)", "puruṣa"]
    item_h, gap = 0.19, 0.075
    chain_hi = len(chain) * item_h + (len(chain) - 1) * gap
    sheaths = ["annamaya", "prāṇamaya", "manomaya", "vijñānamaya", "ānandamaya"]
    step = 0.185
    sheath_hi = chain_hi
    draw_hi = max(chain_hi, sheath_hi) + 0.14

    def draw(f, top):
        # left column: the causal chain
        f.text(21, top, "The causal chain (2.1.1)", size=7.8, weight="bold", color=TEAL)
        y = top - f.yu(0.16)
        ih, g = f.yu(item_h), f.yu(gap)
        for i, s in enumerate(chain):
            y0 = y - ih
            is_end = i in (0, len(chain) - 1)
            rect = f.box(6, y0, 30, ih, fc=SAND if not is_end else PALE,
                         ec=MAROON if i == 0 else TEAL, lw=1.4 if i == 0 else 1.0)
            f.text(21, y0 + ih / 2, s, size=6.5, va="center",
                   color=MAROON if i == 0 else INK, weight="bold" if is_end else "normal",
                   inside=rect, label=s)
            if i < len(chain) - 1:
                f.arrow(21, y0 - 0.3, 21, y0 - g + 0.3, ms=7, lw=1.1)
            y = y0 - g
        # right column: nested sheaths
        f.text(69, top, "The five sheaths, each puruṣa-vidha", size=7.8, weight="bold", color=TEAL)
        X0, X1 = 42, 97
        ytop = top - f.yu(0.16)
        ybot = ytop - f.yu(sheath_hi - 0.16)
        for i, s in enumerate(sheaths):
            dx = i * 4.2
            dy = f.yu(i * step)
            inner = i == len(sheaths) - 1
            x, y0, w, h = X0 + dx, ybot + dy * 0.75, X1 - X0 - 2 * dx, (ytop - ybot) - dy * 1.0 - dy * 0.75
            f.box(x, y0, w, h, fc=[SAND, PALE, SAND, PALE, SAND][i],
                  ec=MAROON if inner else TEAL, lw=1.5 if inner else 1.0)
            f.text(x + 1.2, y0 + h - f.yu(0.05), s, size=6.6, ha="left",
                   color=MAROON if inner else TEAL, weight="bold")
        # the bird format inside the innermost
        cx = (X0 + X1) / 2
        cy = ybot + (ytop - ybot) * 0.42
        f.text(cx, cy, "priyam śiraḥ\nmodaḥ | pramodaḥ\nānanda ātmā\nbrahma pucchaṁ pratiṣṭhā",
               size=5.7, va="center", color=MAROON)
        f.text(cx, ybot - f.yu(0.03), "each: śiras · dakṣiṇa pakṣa · uttara pakṣa · ātmā · puccha-pratiṣṭhā",
               size=5.4, va="top", color=GREY, style="italic")

    build("fig1_causal_chain_sheaths", [
        Title("Brahmavid āpnoti param: the procedure"),
        Sub("Taittirīya Upaniṣad 2.1–2.5 as read in class: from Brahman to the body of food, and inward again"),
        Custom(draw_hi, draw),
        Gap(0.1),
        Banner("Puruṣa = puri śete, whatever dwells in a body, not a male; a body need not be like ours:\nNyāya's bodies of water and air, Sagan's gaseous life on Jupiter"),
    ])


# ------------------------------------------------------------------ Figure 2
def fig2():
    names = ["ānandamaya", "vijñānamaya", "manomaya", "prāṇamaya", "annamaya"]
    heads = ["priyam\nśiraḥ", "śraddhā\nśiraḥ", "yajuḥ\nśiraḥ", "prāṇa\nśiraḥ", "the body\nof food"]
    row_hi = 0.62

    def draw(f, top):
        w, gap = 16.4, 3.0
        x = 3.0
        hh = f.yu(row_hi - 0.08)
        y0 = top - f.yu(0.04) - hh
        for i, (n, h) in enumerate(zip(names, heads)):
            inner = i == 0
            rect = f.box(x, y0, w, hh, fc=SAND if inner else PALE, ec=MAROON if inner else TEAL,
                         lw=1.5 if inner else 1.0)
            f.text(x + w / 2, y0 + hh - f.yu(0.05), n, size=6.9, weight="bold",
                   color=MAROON if inner else TEAL, inside=rect, label=n)
            f.text(x + w / 2, y0 + hh - f.yu(0.2), h, size=6.0, inside=rect, label=n + " head")
            if i < len(names) - 1:
                f.arrow(x + w + 0.3, y0 + hh / 2, x + w + gap - 0.3, y0 + hh / 2, ms=8)
            x += w + gap
        f.text(50, y0 - f.yu(0.03), "anvayaṁ puruṣa-vidhaḥ: each outer sheath is joined to, and shaped by, the one it houses",
               size=6.2, color=GREY, style="italic")

    cols = []
    ex = [("sword \u2192 scabbard", "A curved sword cannot enter\na straight sheath; the sheath\nhas the sword's shape."),
          ("letter \u2192 envelope", "The cover is sized to the\nletter or booklet it holds:\ntoo big or too small fails."),
          ("fist \u2192 glove", "The cloth took the fist's form;\nglove, sock and cap follow\nthe hand, foot and head."),
          ("village sign", "The tribal body outside the\nvillage: head, wings, base.\nA body can be any form.")]
    x = 2.0
    for h, b in ex:
        cols.append(dict(x=x, w=23.0, head=h, body=b, hsize=7.4, bsize=6.0))
        x += 24.0

    build("fig2_ananda_gives_form", [
        Title("Brahmavāde ānando ākāra-samarpakaḥ"),
        Sub("Where does the form come from? From the sword whose scabbard it is: ānanda is the giver of form"),
        Custom(row_hi + 0.2, draw),
        Columns(cols, after=0.1),
        Banner("The soul necessitates the body: āvaśyakatā as necessity, not requirement;\nhence a mukuṭ must be made to the size of Ṭhākurjī's śrī-mastaka"),
    ])


# ------------------------------------------------------------------ Figure 3
def fig3():
    steps = ["so 'kāmayata:\nmay I become many", "sa tapas taptvā\nidaṁ sarvam asṛjata", "tad evānuprāviśat:\nhe entered it",
             "sac ca tyac cābhavat:\nhe became both of each pair"]
    pairs = [("sat", "tyat"), ("nirukta", "anirukta"), ("nilayana", "anilayana"),
             ("vijñāna", "avijñāna"), ("satya", "anṛta")]
    glosses = ["revealed |\nunrevealed", "definable |\nundefinable", "hiding-place |\nno hiding-place",
               "knowing |\nunknowing", "true |\nuntrue"]
    flow_hi, pair_hi = 0.46, 0.62

    def draw(f, top):
        w, gap, x = 22.0, 2.5, 2.0
        hh = f.yu(flow_hi - 0.06)
        y0 = top - hh
        for i, s in enumerate(steps):
            last = i == len(steps) - 1
            rect = f.box(x, y0, w, hh, fc=SAND, ec=MAROON if last else TEAL, lw=1.4 if last else 1.0)
            f.text(x + w / 2, y0 + hh / 2, s, size=6.1, va="center",
                   color=MAROON if last else INK, inside=rect, label=s[:12])
            if not last:
                f.arrow(x + w + 0.3, y0 + hh / 2, x + w + gap - 0.3, y0 + hh / 2, ms=8)
            x += w + gap
        # pairs row
        pw, pg = 18.0, 1.5
        x = 50 - (5 * pw + 4 * pg) / 2
        ph = f.yu(pair_hi - 0.12)
        y1 = y0 - f.yu(0.12) - ph
        for (a, b), g in zip(pairs, glosses):
            rect = f.box(x, y1, pw, ph, fc=PALE, ec=TEAL, lw=0.9)
            f.text(x + pw / 2, y1 + ph - f.yu(0.05), f"{a} | {b}", size=6.6, weight="bold", color=TEAL,
                   inside=rect, label=a)
            f.text(x + pw / 2, y1 + ph - f.yu(0.2), g, size=5.6, color=GREY, inside=rect, label=a + " g")
            x += pw + pg

    cols = [dict(x=2, w=47, head="yato vā imāni bhūtāni jāyante",
                 body="kārya-lakṣaṇa from the angle of birth:\nthe language of cause and effect, of\n\u201cproduction\u201d; the śāstra's own definition,\njanmādy asya yataḥ.", hsize=7.6, bsize=6.3),
            dict(x=51, w=47, head="satyaṁ jñānam anantaṁ brahma",
                 body="kārya-lakṣaṇa from the angle of tattva:\nthe One who became many and entered;\nsat + tyat = satya; vijñāna and avijñāna\n= jñāna; satya and anṛta = his ānanda.", hsize=7.6, bsize=6.3, ec=MAROON, lw=1.4)]
    build("fig3_taittiriya_audit", [
        Title("The Upaniṣad audits its own account"),
        Sub("Taittirīya 2.6: the whole account of satya, jñāna and ananta is settled after the One becomes many"),
        Custom(flow_hi + pair_hi, draw),
        Columns(cols, after=0.1),
        Banner("Neither is a svarūpa-lakṣaṇa: the One is his own begetter and his own offspring,\nhis own cause and his own effect"),
    ])


# ------------------------------------------------------------------ Figure 4
def fig4():
    cols = [dict(x=2, w=47, head="Nyāya: the \u201cover-realist\u201d",
                 body="Substance comes first, its qualities after,\nso dravya is defined only negatively: that\nin which there is no atyantābhāva of guṇa;\nātmā likewise, by sukha, duḥkha, buddhi,\nicchā, dveṣa, dharma and adharma.\nNo tanmātras: what Sāṅkhya calls tanmātrā\nNyāya calls guṇa. Over-objectivism.",
                 hsize=8.2, bsize=6.3),
            dict(x=51, w=47, head="Sāṅkhya: \u201csubjecto-objectivism\u201d",
                 body="Quality comes first. Qualities are born of\nahaṅkāra, of self-awareness (lose it under\nanaesthesia and no question can be grasped);\nwhen they consolidate outside us they become\nbhūtas. Every thing is partly subjective, partly\nobjective. Kapila is an avatāra, so all the\nācāryas stand in Sāṅkhya's branch.",
                 hsize=8.2, bsize=6.3, ec=MAROON, lw=1.4)]
    cols2 = [dict(x=2, w=31, head="relative, then subjective",
                  body="The questioner is female objectively;\ndaughter, mother, sister, wife only in\nrelation; good to friends, bad to rivals.", hsize=7.0, bsize=5.9),
             dict(x=34.5, w=31, head="the one woman",
                  body="Kāminī to the lustful; food to the lion;\nthe door of hell to the vairāgī. Mahmud\ndestroyed what he found beautiful.", hsize=7.0, bsize=5.9),
             dict(x=67, w=31, head="the horizon",
                  body="In the photograph too, so not imagined;\nwider with height, 1° of 360°, different on\nthe moon: a limit of seeing, not an illusion.", hsize=7.0, bsize=5.9)]
    build("fig4_nyaya_sankhya", [
        Title("Nyāya against Sāṅkhya: where do qualities come from?"),
        Sub("The third question: tanmātras, and what the Naiyāyikas and the Sāṅkhyas make of the five elements"),
        Columns(cols, after=0.1),
        Columns(cols2, after=0.1),
        Banner("Neither a hundred percent objective nor a hundred percent subjective:\nKapila resolved what the logicians could not"),
    ])


# ------------------------------------------------------------------ Figure 5
def fig5():
    hi = 2.42

    def draw(f, top):
        yu = f.yu
        # root
        rw, rh = 36, yu(0.3)
        rx, ry = 50 - rw / 2, top - rh
        rect = f.box(rx, ry, rw, rh, fc=SAND, ec=MAROON, lw=1.5)
        f.text(50, ry + rh / 2, "Saccidānanda Brahman splits", size=7.6, weight="bold", color=MAROON,
               va="center", inside=rect, label="root")
        # three strands
        y1h = yu(0.64)
        y1 = ry - yu(0.22) - y1h
        strands = [(2, 28, "sattā", "prakṛti, with no cetanā:\npṛthivī, jala, tejas, vāyu, ākāśa\n(the Upaniṣad's order; Sāṅkhya's\nprakṛti, ahaṅkāra, tanmātrā not taken)"),
                   (33, 34, "cetanā", "the jīva, with no ānanda:\ndaivī, āsurī, carṣaṇī"),
                   (70, 28, "priyatā (ānanda)", "the antaryāmin, Īśvara,\nthe absolute soul within all")]
        for x, w, h, b in strands:
            rect = f.box(x, y1, w, y1h, fc=PALE, ec=TEAL, lw=1.0)
            f.text(x + w / 2, y1 + y1h - yu(0.05), h, size=7.0, weight="bold", color=TEAL, inside=rect, label=h)
            f.text(x + w / 2, y1 + y1h - yu(0.2), b, size=5.6, inside=rect, label=h + " b")
            sx = 50 if x == 33 else (rx + 3 if x == 2 else rx + rw - 3)
            f.arrow(sx, ry - 0.3, x + w / 2, y1 + y1h + 0.3, ms=7, lw=1.0)
        # four installed powers under the jīva
        y2h = yu(0.72)
        y2 = y1 - yu(0.3) - y2h
        powers = [("vidyā installed", "daivī jīva\n\u2192 svarūpa-lābha:\nthe gain of one's\nown svarūpa", TEAL, PALE),
                  ("avidyā installed", "āsurī jīva\n\u2192 janma-lābha,\ndeha-lābha: birth,\ndeath, the body", TEAL, PALE),
                  ("nothing installed", "carṣaṇī jīva\n\u2192 paribhramaṇa:\nwanders, bumps\nabout, travels free", GREY, CONCEALED),
                  ("puṣṭi installed", "\u2192 bhagavallābha:\nneither vidyā nor\navidyā; attached to\none's originality", MAROON, SAND)]
        pw, pg = 22.5, 2.3
        x = 50 - (4 * pw + 3 * pg) / 2
        for h, b, ec, fc in powers:
            rect = f.box(x, y2, pw, y2h, fc=fc, ec=ec, lw=1.5 if ec == MAROON else 1.0)
            f.text(x + pw / 2, y2 + y2h - yu(0.05), h, size=6.6, weight="bold", color=ec if ec != GREY else INK,
                   inside=rect, label=h)
            f.text(x + pw / 2, y2 + y2h - yu(0.2), b, size=5.8, inside=rect, label=h + " b")
            f.arrow(50, y1 - 0.3, x + pw / 2, y2 + y2h + 0.3, ms=7, lw=1.0)
            x += pw + pg
        f.text(50, y2 - yu(0.05), "\u201cConsciousness neither is born nor dies; it enters a body and leaves it\u201d: the mobile phone that goes along with the traveller",
               size=5.9, color=GREY, style="italic")

    build("fig5_installed_powers", [
        Title("The chart dictated in class: installed powers and their gains"),
        Sub("\u201cWrite it down\u201d: how the omniscient uses his avidyā-śakti to become the ignorant jīva, and what each power yields"),
        Custom(hi, draw),
        Banner("Whichever power Bhagavān installs in a portion of himself, its mode of conduct follows:\nthe traveller whom nobody receives keeps knocking about between taxi, bus and rickshaw"),
    ])


# ------------------------------------------------------------------ Figure 6
def fig6():
    cols = [dict(x=2, w=31, head="hareḥ śaktī",
                 body="Hari's powers, not the jīva's\nown: the punch does not hit\nits own fist, the tickle does\nnot tickle its author. Brahman,\nhead of the HUF, distributes\nits assets; each enjoys his\nshare. Neither jñāna for pride\nnor ajñāna for grief: līlā.",
                 hsize=8.2, bsize=6.2),
            dict(x=34.5, w=31, head="māyayaiva vinirmite",
                 body="Made by māyā, so they come\nand go by Bhagavān's will\nalone: vidyā hides, avidyā\nswells, the wanderer stops.\nMām eva ye prapadyante: when\nbhakti is present avidyā and\nvidyā both retire; otherwise\nno nitya-muktatā.",
                 hsize=8.2, bsize=6.2, ec=MAROON, lw=1.4),
            dict(x=67, w=31, head="jīvasyaiva nānyasya",
                 body="Of the jīva alone: not of the\njaḍa, not of the antaryāmin,\nwho is nitya-mukta because\nhe has neither. Duḥkhitva and\nanīśatā are the jīva's, until\nhe surrenders; then sukha and\nduḥkha are felt as līlā, as in\na thriller film.",
                 hsize=8.2, bsize=6.2)]
    cols2 = [dict(x=2, w=47, head="mokṣo 'py ekaḥ sargaḥ",
                  body="Nothing can bind Brahman, so nothing frees it;\nmukti is a creation like bondage: daivī sampad\nvimokṣāya, nibandhāyāsurī (Gītā 16.5), with vidyā\nor avidyā prominent in each.", hsize=7.4, bsize=6.0),
             dict(x=51, w=47, head="carṣaṇī: paribhramaṇa-śakti",
                  body="The Veda's name for man, the wanderer: eklā calo;\nthe gopīs through the forest; Gaṅgādās, Jamunādās,\nAmerikādās; ātmanaḥ svarūpa-lābho vidyayā,\ndeha-lābho 'vidyayā, and the roamer's gain by carṣaṇī.", hsize=7.4, bsize=6.0)]
    build("fig6_karika31_powers", [
        Title("Kārikā 31: vidyāvidye hareḥ śaktī māyayaiva vinirmite"),
        Sub("te jīvasyaiva nānyasya duḥkhitvaṁ cāpy anīśatā, with the Prakāśa on it"),
        Columns(cols, after=0.1),
        Columns(cols2, after=0.1),
        Banner("Na vidyā merī, na avidyā merī: the powers are Brahman's, lent out in līlā;\n\u201cdon't take it seriously\u201d"),
    ])


# ------------------------------------------------------------------ Figure 7
def fig7():
    hi = 2.34

    def draw(f, top):
        yu = f.yu
        # left stack: five limbs
        f.text(24, top, "The five limbs of avidyā (kārikā 32)", size=7.6, weight="bold", color=TEAL)
        y = top - yu(0.17)
        items = [("svarūpājñāna", "not knowing one's own svarūpa:\ncetanā joined to its ajñāna, as the\nsleeper who \u201cknew nothing at all\u201d", MAROON, SAND),
                 ("dehādhyāsa", "I am the body", TEAL, PALE),
                 ("indriyādhyāsa", "I have the senses", TEAL, PALE),
                 ("prāṇādhyāsa", "I am the breathing one", TEAL, PALE),
                 ("antaḥkaraṇādhyāsa", "I am mind, buddhi, ahaṅkāra", TEAL, PALE),
                 ("svarūpa-vismṛti", "not-knowing culminates in forgetting", MAROON, SAND)]
        for i, (h, b, ec, fc) in enumerate(items):
            big = i in (0,)
            bh = yu(0.57 if big else 0.2)
            y0 = y - bh
            rect = f.box(3, y0, 42, bh, fc=fc, ec=ec, lw=1.4 if ec == MAROON else 1.0)
            if big:
                f.text(24, y0 + bh - yu(0.05), h, size=6.8, weight="bold", color=ec, inside=rect, label=h)
                f.text(24, y0 + bh - yu(0.19), b, size=5.7, inside=rect, label=h + " b")
            else:
                f.text(4.5, y0 + bh / 2, h, size=6.4, weight="bold", color=ec, ha="left", va="center",
                       inside=rect, label=h)
                f.text(43.5, y0 + bh / 2, b, size=5.7, ha="right", va="center", inside=rect, label=h + " b")
            if i < len(items) - 1:
                f.arrow(24, y0 - 0.2, 24, y0 - yu(0.07) + 0.2, ms=6, lw=1.0)
            y = y0 - yu(0.07)
        f.text(24, y - yu(0.04), "the fourfold tādātmya-adhyāsa: \u201cidentification\u201d", size=5.6, color=GREY, style="italic")
        # right: the car
        f.text(74, top, "The car with the stuck accelerator", size=7.6, weight="bold", color=TEAL)
        cy = top - yu(0.17)
        ch = yu(1.78)
        rect = f.box(51, cy - ch, 46, ch, fc=SAND, ec=TEAL, lw=1.0)
        # car body
        bx, by, bw, bh = 56, cy - yu(0.62), 36, yu(0.3)
        f.ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.01", mutation_scale=55,
                                      fc=PALE, ec=INK, lw=1.0, zorder=2))
        f.ax.add_patch(Polygon([(bx + 7, by + bh), (bx + 11, by + bh + yu(0.17)), (bx + 25, by + bh + yu(0.17)),
                                (bx + 29, by + bh)], closed=True, fc=PALE, ec=INK, lw=1.0, zorder=2))
        for wx in (bx + 8, bx + 28):
            f.ax.add_patch(Circle((wx, by), yu(0.07), fc=INK, ec=INK, zorder=3))
        f.text(bx + bw / 2, by + bh / 2, "accelerator stuck, King's Circle, 1960s", size=5.4, va="center", color=INK)
        parts = [("accelerator = vidyā", "it \u201cexcites\u201d, moves forward"),
                 ("brake = avidyā", "it stops, holds back"),
                 ("gear", "forward, reverse: all three are functions")]
        py = by - yu(0.2)
        for h, b in parts:
            f.text(53, py, h, size=6.2, weight="bold", color=MAROON, ha="left", va="top", inside=rect, label=h)
            f.text(95, py, b, size=5.6, ha="right", va="top", inside=rect, label=h + " b")
            py -= yu(0.16)
        f.text(74, py - yu(0.02), "The driver decides when to change gear, brake or\naccelerate: Bhagavān installs and instigates the\npowers. To think \u201cI am the driver\u201d is the\ntādātmya-adhyāsa; yasya nāhaṅkṛto bhāvaḥ (Gītā 18.17).",
               size=5.7, va="top", inside=rect, label="driver")

    build("fig7_five_limbs_car", [
        Title("Kārikā 32: svarūpājñānam ekaṁ hi parva, and the fourfold adhyāsa"),
        Sub("Consciousness is one thing, knowledge another; the superimpositions wake a little vidyā and the sense of being sad"),
        Custom(hi, draw),
        Banner("We are driven by the powers, not their drivers; and thinking is a function of intellect,\nnot of consciousness (cogito ergo sum)"),
    ])


# ------------------------------------------------------------------ Figure 8
def fig8():
    hi = 2.0

    def draw(f, top):
        yu = f.yu
        # left: the way back
        f.text(25, top, "The way back: from forgetting to remembrance", size=7.4, weight="bold", color=TEAL)
        steps = [("āhāra-śuddhi", "what is \u201cinstalled\u201d in consciousness is kept pure"),
                 ("sattva-śuddhi", "the antaḥkaraṇa, like water, takes the colour mixed in"),
                 ("dhruvā smṛti", "steady remembrance of who I am: Brahmasambandha\nand the aṣṭākṣara as reminders against vismṛti"),
                 ("sarva-granthi-vipramokṣa", "all the \u201ccomplexes\u201d of the heart dissolve")]
        y = top - yu(0.17)
        for i, (h, b) in enumerate(steps):
            bh = yu(0.42 if "\n" in b else 0.31)
            y0 = y - bh
            last = i == len(steps) - 1
            rect = f.box(2, y0, 46, bh, fc=SAND if last else PALE, ec=MAROON if last else TEAL, lw=1.4 if last else 1.0)
            f.text(3.5, y0 + bh - yu(0.045), h, size=6.4, weight="bold", color=MAROON if last else TEAL,
                   ha="left", inside=rect, label=h)
            f.text(3.5, y0 + bh - yu(0.155), b, size=5.5, ha="left", inside=rect, label=h + " b")
            if not last:
                f.arrow(25, y0 - 0.2, 25, y0 - yu(0.06) + 0.2, ms=6, lw=1.0)
            y = y0 - yu(0.06)
        f.text(25, y - yu(0.03), "Chāndogya Upaniṣad 7.26.2", size=5.6, color=GREY, style="italic")
        # right: sun and moon
        f.text(75, top, "One light, two directions", size=7.4, weight="bold", color=TEAL)
        rx, ry, rw, rh = 52, top - yu(0.17) - yu(1.6), 46, yu(1.6)
        rect = f.box(rx, ry, rw, rh, fc=PALE, ec=TEAL, lw=1.0)
        sun = (64, ry + rh - yu(0.22))
        moon = (86, ry + rh - yu(0.22))
        f.ax.add_patch(Circle(sun, 3.2, fc=OCHRE, ec=OCHRE, zorder=3))
        f.ax.add_patch(Circle(moon, 2.6, fc=CONCEALED, ec=GREY, lw=0.8, zorder=3))
        f.text(sun[0], sun[1] + yu(0.11), "the sun", size=5.4, va="bottom", color=OCHRE, weight="bold")
        f.text(moon[0], moon[1] + yu(0.1), "the moon", size=5.4, va="bottom", color=GREY, weight="bold")
        heart = (75, ry + yu(0.3))
        f.ax.add_patch(FancyBboxPatch((heart[0] - 9, heart[1] - yu(0.1)), 18, yu(0.2), boxstyle="round,pad=0.01",
                                      mutation_scale=55, fc=SAND, ec=MAROON, lw=1.2, zorder=2))
        f.text(heart[0], heart[1], "our heart", size=5.8, va="center", color=MAROON, weight="bold")
        f.arrow(sun[0] + 1.5, sun[1] - yu(0.12), heart[0] - 4, heart[1] + yu(0.12), color=OCHRE, lw=1.6, ms=9)
        f.arrow(heart[0] + 4, heart[1] + yu(0.12), moon[0] - 1.5, moon[1] - yu(0.12), color=TEAL, lw=1.6, ms=9)
        f.text(53.5, ry + yu(0.58), "kṛpā: direct\nsunshine, intense,\ncoming down\nfrom Bhagavān", size=5.5, ha="left", va="center", color=OCHRE, inside=rect, label="krpa")
        f.text(96.8, ry + yu(0.58), "bhakti: reflected\nmoonlight, cool,\ngoing back\nto him", size=5.5, ha="right", va="center", color=TEAL, inside=rect, label="bhakti")
        f.text(75, ry + yu(0.08), "only the direction of coming and going has changed", size=5.3, va="center", color=GREY, style="italic", inside=rect, label="dir")

    build("fig8_smrti_krpa_bhakti", [
        Title("Not-knowing becomes forgetting, and the reminder; kṛpā and bhakti"),
        Sub("\u201cFirst of all we do not know our nature, and in the final end we forget about it\u201d; and the last question of the day"),
        Custom(hi, draw),
        Banner("Ghālib's \u201chad I not been\u201d is not Mahāprabhuji's approach:\nwhat I have become, I have become in Bhagavān's līlā"),
    ])


if __name__ == "__main__":
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        fn()
    print("PROBLEMS:", len(PROBLEMS))
    for p in PROBLEMS:
        print("  ", p)
