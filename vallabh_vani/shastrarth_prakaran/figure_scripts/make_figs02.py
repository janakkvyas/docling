#!/usr/bin/env python3
"""Figures for Lecture 2 (2026-07-18) of the Śāstrārtha Prakaraṇa series.

House style: matplotlib Agg, DejaVu Sans, width 6.2 in, dpi 200, axes 0-100 both ways,
IAST and English only. Every text drawn inside a box is registered with that box and
checked for overflow after rendering.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon  # noqa: E402

plt.rcParams["font.family"] = "DejaVu Sans"

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"

OUT = Path(__file__).resolve().parent / "figs02"
W = 6.2
PAD = 1.2  # box pad in x data units (boxstyle pad 0.012 x mutation_scale 100)


class Fig:
    def __init__(self, h: float):
        self.h = h
        self.asp = W / h
        self.fig = plt.figure(figsize=(W, h))
        self.fig.patch.set_facecolor(PALE)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis("off")
        self.checks: list[tuple[object, tuple[float, float, float, float], str]] = []
        self.free: list[object] = []

    # ---------- primitives ----------
    def box(self, x, y, w, h, edge=TEAL, fill=SAND, lw=1.2):
        p = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012",
            mutation_scale=100,
            mutation_aspect=self.asp,
            fc=fill,
            ec=edge,
            lw=lw,
            zorder=1,
        )
        self.ax.add_patch(p)
        return (x, y, w, h)

    def text(
        self,
        x,
        y,
        s,
        size=6.8,
        color=INK,
        ha="left",
        va="top",
        weight="normal",
        style="normal",
        inside=None,
        label="",
        ls=1.35,
        z=5,
    ):
        t = self.ax.text(
            x,
            y,
            s,
            ha=ha,
            va=va,
            fontsize=size,
            color=color,
            fontweight=weight,
            style=style,
            linespacing=ls,
            zorder=z,
        )
        if inside is not None:
            self.checks.append((t, inside, label or s[:30]))
        else:
            self.free.append(t)
        return t

    def header(self, b, s, color=TEAL, size=8.8, dy=2.0):
        x, y, w, h = b
        return self.text(
            x + w / 2,
            y + h - dy,
            s,
            size=size,
            color=color,
            ha="center",
            weight="bold",
            inside=b,
        )

    def ellipse(self, cx, cy, rx, edge=INK, fill="none", lw=1.0, z=2, ls="-"):
        e = Ellipse(
            (cx, cy),
            2 * rx,
            2 * rx * self.asp,
            fc=fill,
            ec=edge,
            lw=lw,
            zorder=z,
            linestyle=ls,
        )
        self.ax.add_patch(e)
        return e

    def arrow(
        self, x1, y1, x2, y2, color=OCHRE, lw=1.3, style="-|>", ms=9, both=False, z=3
    ):
        st = "<|-|>" if both else style
        a = FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle=st,
            mutation_scale=ms,
            color=color,
            lw=lw,
            zorder=z,
            shrinkA=0,
            shrinkB=0,
        )
        self.ax.add_patch(a)

    def line(self, xs, ys, color=GREY, lw=0.8, z=2, ls="-"):
        self.ax.plot(
            xs, ys, color=color, lw=lw, zorder=z, linestyle=ls, solid_capstyle="round"
        )

    def title(self, s, sub=None):
        self.text(50, 98.2, s, size=12, color=INK, ha="center", weight="bold")
        if sub:
            self.text(50, 92.6, sub, size=7.2, color=GREY, ha="center", style="italic")

    # ---------- checking ----------
    def check(self, name: str) -> list[str]:
        self.fig.canvas.draw()
        r = self.fig.canvas.get_renderer()
        inv = self.ax.transData.inverted()
        problems = []
        for t, (x, y, w, h), label in self.checks:
            bb = t.get_window_extent(renderer=r)
            (x0, y0), (x1, y1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
            tol = 0.15
            if x0 < x - tol or x1 > x + w + tol or y0 < y - tol or y1 > y + h + tol:
                problems.append(
                    f"{name}: '{label}' text [{x0:.1f},{x1:.1f}]x[{y0:.1f},{y1:.1f}]"
                    f" outside box [{x:.1f},{x + w:.1f}]x[{y:.1f},{y + h:.1f}]"
                )
        for t in self.free + [c[0] for c in self.checks]:
            bb = t.get_window_extent(renderer=r)
            (x0, y0), (x1, y1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
            if (
                x0 < 0.5
                or x1 > 99.5
                or y0 < getattr(self, "ybot", 0.0) + 0.2
                or y1 > 99.8
            ):
                problems.append(f"{name}: text '{t.get_text()[:30]}' leaves the canvas")
        return problems

    def crop_bottom(self, margin: float = 1.0) -> None:
        """Raise the lower y-limit to just below the lowest artist and shrink the figure
        height in proportion, so the physical scale (inches per unit) is unchanged."""
        self.fig.canvas.draw()
        r = self.fig.canvas.get_renderer()
        inv = self.ax.transData.inverted()
        lows = []
        for a in list(self.ax.patches) + list(self.ax.texts) + list(self.ax.lines):
            bb = a.get_window_extent(renderer=r)
            lows.append(inv.transform((bb.x0, bb.y0))[1])
        ybot = max(0.0, min(lows) - margin)
        self.ybot = ybot
        self.ax.set_ylim(ybot, 100)
        self.fig.set_size_inches(W, self.h * (100 - ybot) / 100)

    def save(self, name: str) -> list[str]:
        self.crop_bottom()
        probs = self.check(name)
        OUT.mkdir(exist_ok=True)
        self.fig.savefig(
            OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.12, facecolor=PALE
        )
        plt.close(self.fig)
        return probs


def annulus_sector(cx, cy, r_in, r_out, a0, a1, asp, n=40):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r_out * math.cos(a), cy + r_out * asp * math.sin(a)))
    for i in range(n + 1):
        a = math.radians(a1 + (a0 - a1) * i / n)
        pts.append((cx + r_in * math.cos(a), cy + r_in * asp * math.sin(a)))
    return pts


# =====================================================================
def fig1() -> list[str]:
    f = Fig(4.9)
    f.title(
        "Two ways of defining",
        "every definition is part of a description, but not every description is a definition",
    )

    # Aristotelian
    L = f.box(3, 31, 45, 56, edge=TEAL)
    f.header(L, "Aristotelian definition")
    f.text(
        25.5,
        81.2,
        "genus cum differentia",
        size=7,
        color=GREY,
        ha="center",
        style="italic",
        inside=L,
    )
    f.ellipse(14.5, 66.0, 8.6, edge=TEAL, fill=PALE, lw=1.1)
    f.ellipse(14.5, 63.5, 3.4, edge=MAROON, fill=SAND, lw=1.1)
    f.text(14.5, 74.1, "G", size=8, color=TEAL, ha="center", weight="bold", inside=L)
    f.text(14.5, 65.5, "D", size=8, color=MAROON, ha="center", weight="bold", inside=L)
    f.text(
        25.5, 73.0, "G = genus: animal\nD = differentia: rational", size=6.8, inside=L
    )
    f.text(
        25.5,
        64.5,
        "“Man is rational animal”",
        size=6.8,
        style="italic",
        color=TEAL,
        inside=L,
    )
    f.text(
        6,
        52.0,
        "A differentia differentiates only within\n"
        "a stated genus. And the general is known\n"
        "only from many particulars, the particular\n"
        "only through the general: anyonyāśraya.\n"
        "Yet that is how our intellect works (the\n"
        "prasādiyā in the lane points to a havelī).\n"
        "“Aristotle was not wrong.”",
        size=6.6,
        inside=L,
    )

    # Indian lakṣaṇa
    R = f.box(52, 31, 45, 56, edge=MAROON)
    f.header(R, "Indian lakṣaṇa", color=MAROON)
    f.text(
        74.5,
        81.2,
        "asādhāraṇa-dharma-bodhakaṁ vākyam",
        size=7,
        color=GREY,
        ha="center",
        style="italic",
        inside=R,
    )
    f.ellipse(68.5, 65.5, 9.2, edge=TEAL, fill=PALE, lw=1.0)
    f.ellipse(80.5, 65.5, 9.2, edge=TEAL, fill="none", lw=1.0)
    f.text(
        63.8,
        69.9,
        "butterfly\nbat\nmosquito\nfly",
        size=5.9,
        color=INK,
        ha="center",
        inside=R,
    )
    f.text(85.4, 68.5, "man\nmonkey", size=5.9, color=INK, ha="center", inside=R)
    f.text(
        74.5, 67.1, "bird", size=7.4, color=MAROON, ha="center", weight="bold", inside=R
    )
    f.text(
        66.0,
        52.8,
        "winged",
        size=6.2,
        color=TEAL,
        ha="center",
        style="italic",
        inside=R,
    )
    f.text(
        83.0,
        52.8,
        "two-footed",
        size=6.2,
        color=TEAL,
        ha="center",
        style="italic",
        inside=R,
    )
    f.text(
        55,
        48.6,
        "dvipadatve sati pakṣavattvaṁ pakṣitvam",
        size=6.6,
        style="italic",
        color=MAROON,
        inside=R,
    )
    f.text(
        55,
        45.2,
        "birdhood: having wings while two-footed.\n"
        "The uncommon property alone; no genus\n"
        "need be stated. The intellect tags the most\n"
        "striking feature, as airport staff tag\n"
        "luggage.",
        size=6.6,
        inside=R,
    )

    B = f.box(3, 11, 94, 13.5, edge=OCHRE, fill=SAND)
    f.text(
        50,
        22.4,
        "Both must be free of ativyāpti (too broad), avyāpti (too narrow) and asambhava (impossible).",
        size=7.2,
        ha="center",
        weight="bold",
        inside=B,
    )
    f.text(
        50,
        16.6,
        "“It must not be too broad. It must not be too narrow. Or it must not be impossible.”",
        size=6.8,
        ha="center",
        style="italic",
        color=GREY,
        inside=B,
    )
    return f.save("fig1_definition.png")


# =====================================================================
def fig2() -> list[str]:
    f = Fig(5.2)
    f.title(
        "The paribhāṣā as nested circles",
        "after the speaker’s chart: each wider circle is the genus of the one inside it",
    )
    cx, cy = 26.5, 52.0
    f.text(cx, 87.6, "saccidānanda", size=9, color=TEAL, ha="center", style="italic")
    f.ellipse(cx, cy, 22.0, edge=TEAL, fill=SAND, lw=1.3)
    f.ellipse(cx, cy, 14.5, edge=TEAL, fill=PALE, lw=1.3)
    f.ellipse(cx, cy, 6.6, edge=MAROON, fill=SAND, lw=1.6)
    f.text(cx, 75.6, "B · Brahman", size=7.4, color=TEAL, ha="center", weight="bold")
    f.text(cx, 65.6, "P · Paramātmā", size=7.4, color=TEAL, ha="center", weight="bold")
    f.text(cx, 55.0, "B\nBhagavān", size=7.2, color=MAROON, ha="center", weight="bold")

    A = f.box(55, 67, 42, 19.5, edge=TEAL)
    f.header(A, "Brahman · all in all", size=8.4)
    f.text(
        57.5,
        81.4,
        "sad-advaita: unified being",
        size=6.7,
        style="italic",
        color=TEAL,
        inside=A,
    )
    f.text(
        57.5,
        78.0,
        "Everything is made from it; whatever has\n"
        "being, even a pen or a whiteboard without\n"
        "soul. sarvaṁ khalv idaṁ brahma",
        size=6.5,
        inside=A,
    )
    Bx = f.box(55, 42, 42, 19.5, edge=TEAL)
    f.header(Bx, "Paramātmā · one in all", size=8.4)
    f.text(
        57.5,
        56.4,
        "cid-advaita: unified consciousness",
        size=6.7,
        style="italic",
        color=TEAL,
        inside=Bx,
    )
    f.text(
        57.5,
        53.0,
        "Brahman entered into all it became; each\n"
        "individual consciousness a tiny bubble in\n"
        "its ocean. Dopamine works “like Paramātmā”.",
        size=6.5,
        inside=Bx,
    )
    C = f.box(55, 17, 42, 19.5, edge=MAROON)
    f.header(C, "Bhagavān · one for all", size=8.4, color=MAROON)
    f.text(
        57.5, 31.4, "ānanda-vyatireka", size=6.7, style="italic", color=MAROON, inside=C
    )
    f.text(
        57.5,
        28.0,
        "aiśvarya, vīrya, yaśas, śrī, jñāna, vairāgya;\n"
        "for Jains and Buddhists, omniscience.\n"
        "Not seen in our consciousness: transcendent.",
        size=6.5,
        inside=C,
    )

    a = math.radians(32)
    f.line(
        [cx + 22.0 * math.cos(a), 53.8],
        [cy + 22.0 * f.asp * math.sin(a), 76.5],
        color=TEAL,
        lw=0.8,
    )
    f.line([cx + 14.5, 53.8], [cy, 51.5], color=TEAL, lw=0.8)
    a = math.radians(-35)
    f.line(
        [cx + 6.6 * math.cos(a), 53.8],
        [cy + 6.6 * f.asp * math.sin(a), 26.5],
        color=MAROON,
        lw=0.8,
    )

    D = f.box(3, 3, 94, 9.5, edge=MAROON, fill=SAND)
    f.text(
        50,
        11.0,
        "bhagavattve sati paramātmatve sati brahmatvam",
        size=8.6,
        ha="center",
        weight="bold",
        style="italic",
        color=MAROON,
        inside=D,
    )
    f.text(
        50,
        6.6,
        "Where Bhagavān is, Paramātmā is; where Paramātmā is, Brahman is; but not the reverse.",
        size=6.8,
        ha="center",
        inside=D,
    )
    return f.save("fig2_bpb.png")


# =====================================================================
COLS3 = (3.0, 36.0, 69.0)
CW3 = 28.0


def fig3() -> list[str]:
    f = Fig(5.4)
    f.title(
        "Praviṣṭa and apraviṣṭa: what is worth inquiring into",
        "yathā mahānti bhūtāni … praviṣṭāny apraviṣṭāni, tathā teṣu na teṣv aham (Bhāgavata 2.9.34)",
    )
    c1, c2, c3 = (x + CW3 / 2 for x in COLS3)

    P1 = f.box(COLS3[0], 47, CW3, 40, edge=TEAL)
    f.header(P1, "Gold", size=8.6)
    f.ellipse(c1, 69.0, 10.4, edge=OCHRE, fill=PALE, lw=1.0, ls="--")
    for dx, y, s in [
        (-4.9, 73.6, "earring"),
        (4.9, 73.6, "ring"),
        (-4.9, 65.2, "“dollar”"),
        (4.9, 65.2, "necklace"),
    ]:
        f.text(c1 + dx, y, s, size=6.0, ha="center", color=INK)
    f.text(c1, 79.6, "gold", size=6.4, ha="center", color=OCHRE, style="italic")
    f.text(
        COLS3[0] + 2.3,
        55.0,
        "present in the earring, and\nalso beyond it, in the ring\nand the necklace",
        size=6.4,
        inside=P1,
    )

    P2 = f.box(COLS3[1], 47, CW3, 40, edge=TEAL)
    f.header(P2, "Ākāśa", size=8.6)
    f.ellipse(c2, 69.0, 10.4, edge=TEAL, fill=PALE, lw=0.8, ls=":")
    f.ellipse(c2, 68.0, 5.2, edge=TEAL, fill="none", lw=1.2)
    f.ellipse(c2, 68.0, 3.8, edge=INK, fill=SAND, lw=0.8)
    f.text(c2, 69.1, "matter", size=5.8, ha="center")
    f.text(
        c2, 78.0, "un-entered ākāśa", size=6.0, ha="center", color=TEAL, style="italic"
    )
    f.text(
        COLS3[1] + 2.3,
        55.0,
        "entered ākāśa: only as much\nas the matter; un-entered\nākāśa is bigger",
        size=6.4,
        inside=P2,
    )

    P3 = f.box(COLS3[2], 47, CW3, 40, edge=MAROON)
    f.header(P3, "Bhagavān", size=8.6, color=MAROON)
    f.ellipse(c3, 69.0, 10.4, edge=MAROON, fill=PALE, lw=1.0, ls="--")
    for dx, y in [(-4.6, 73.0), (4.6, 73.0), (-4.6, 65.5), (4.6, 65.5)]:
        f.ax.add_patch(
            FancyBboxPatch(
                (c3 + dx - 2.1, y - 1.6),
                4.2,
                3.2,
                boxstyle="round,pad=0.2",
                fc=SAND,
                ec=GREY,
                lw=0.6,
                zorder=3,
            )
        )
    f.text(c3, 70.4, "in all", size=6.0, ha="center", color=MAROON)
    f.text(c3, 79.6, "beyond all", size=6.0, ha="center", color=MAROON, style="italic")
    f.text(
        COLS3[2] + 2.3,
        55.0,
        "“I am in all, at the same\ntime beyond all”: in them,\nand not in them",
        size=6.4,
        inside=P3,
    )

    A = f.box(COLS3[0], 24, CW3, 16, edge=TEAL)
    f.header(A, "Abrahamic religions", size=8.0)
    f.text(COLS3[0] + 2.3, 33.6, "God transcendent only", size=6.6, inside=A)
    f.text(
        COLS3[0] + 2.3,
        29.8,
        "(the speaker’s characterization)",
        size=5.9,
        color=GREY,
        style="italic",
        inside=A,
    )
    Bx = f.box(COLS3[1], 24, CW3, 16, edge=TEAL)
    f.header(Bx, "Tribal religions", size=8.0)
    f.text(COLS3[1] + 2.3, 33.6, "God immanent only", size=6.6, inside=Bx)
    f.text(
        COLS3[1] + 2.3,
        29.8,
        "(the speaker’s characterization)",
        size=5.9,
        color=GREY,
        style="italic",
        inside=Bx,
    )
    C = f.box(COLS3[2], 24, CW3, 16, edge=MAROON)
    f.header(C, "Veda and Vedānta", size=8.0, color=MAROON)
    f.text(
        COLS3[2] + 2.3,
        33.6,
        "transcendental cum immanent:\nnot purely the one, not\npurely the other, but both",
        size=6.4,
        inside=C,
    )

    D = f.box(3, 9, 94, 10.5, edge=OCHRE, fill=SAND)
    f.text(
        50,
        18.0,
        "etāvad eva jijñāsyaṁ … anvaya-vyatirekābhyāṁ yat syāt sarvatra sarvadā (Bhāgavata 2.9.35)",
        size=7.0,
        ha="center",
        style="italic",
        weight="bold",
        color=MAROON,
        inside=D,
    )
    f.text(
        50,
        13.4,
        "Not what is merely everywhere, nor what is nowhere, but what is in all and beyond all.",
        size=6.8,
        ha="center",
        inside=D,
    )
    return f.save("fig3_pravishta.png")


# =====================================================================
def fig4() -> list[str]:
    f = Fig(5.2)
    f.title(
        "One lakṣaṇa, two roads",
        "the Bhāgavata’s mark: present in its own locus and also absent from it",
    )
    T = f.box(20, 73, 60, 12.5, edge=GREY, fill=SAND)
    f.header(T, "Shared starting point: advaita", size=8.4)
    f.text(
        50,
        79.4,
        "praviṣṭāny apraviṣṭāni: entered into things, and not entered",
        size=6.8,
        ha="center",
        style="italic",
        inside=T,
    )
    f.arrow(40, 71.5, 25.5, 64.0)
    f.arrow(60, 71.5, 74.5, 64.0)

    L = f.box(3, 27, 44, 35, edge=TEAL)
    f.header(L, "Śaṅkara prasthāna: pāribhāṣika mithyā", size=7.5)
    f.text(
        5.5,
        56.8,
        "svādhikaraṇa-niṣṭha-atyantābhāva-pratiyogitā",
        size=6.6,
        style="italic",
        color=TEAL,
        inside=L,
    )
    f.text(
        5.5,
        53.4,
        "being the counterpositive of an absolute\n"
        "absence that resides in one’s own locus.\n"
        "Locus (adhikaraṇa): the pen on my finger,\n"
        "me on the settee, all of us in the room.\n"
        "Not “appearing false”: some eighty percent\n"
        "of things appear real, twenty false\n"
        "(the horizon, a mirror image).\n"
        "So the world is mithyā: only Brahman,\n"
        "no Paramātmā, no Bhagavān.",
        size=6.5,
        inside=L,
    )

    R = f.box(53, 27, 44, 35, edge=MAROON)
    f.header(R, "Vallabha prasthāna: the lakṣaṇa of Brahman", size=7.5, color=MAROON)
    f.text(
        55.5,
        56.8,
        "bhagavattve sati paramātmatve sati brahmatvam",
        size=6.6,
        style="italic",
        color=MAROON,
        inside=R,
    )
    f.text(
        55.5,
        53.4,
        "The same mark defines Brahman: in things\n"
        "and beyond them, immanent as well as\n"
        "transcendental.\n"
        "Bhagavattva is in Paramātmā here, not there;\n"
        "paramātmatva is in Brahman here, not there\n"
        "(the whiteboard has no ātmā, so no\n"
        "Paramātmā: only Brahman).\n"
        "So Brahman, Paramātmā and Bhagavān\n"
        "all are: such is the advaita.",
        size=6.5,
        inside=R,
    )

    D = f.box(3, 12, 94, 9.0, edge=OCHRE, fill=SAND)
    f.text(
        50,
        19.4,
        "Both start from advaita; at this turn the roads part.",
        size=7.2,
        ha="center",
        weight="bold",
        inside=D,
    )
    f.text(
        50,
        15.4,
        "“For them this is mithyā; for us it is Brahman.”",
        size=6.8,
        ha="center",
        style="italic",
        color=GREY,
        inside=D,
    )
    return f.save("fig4_fork.png")


# =====================================================================
def pairbox(f: Fig, x, y, w, s, edge=MAROON, size=6.6):
    h = 5.0
    f.ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.4", fc=PALE, ec=edge, lw=0.9, zorder=3
        )
    )
    f.text(
        x + w / 2,
        y + h / 2,
        s,
        size=size,
        ha="center",
        va="center",
        inside=(x - 0.4, y - 0.4, w + 0.8, h + 0.8),
    )


def fig5() -> list[str]:
    f = Fig(4.8)
    f.title(
        "Interdependence is not unreality",
        "īśvara and īśitavya: the ruler and the ruled",
    )

    L = f.box(3, 25, 37.5, 61, edge=TEAL)
    f.header(L, "The Advaitin’s inference", size=8.6)
    f.text(
        5.5,
        80.2,
        "īśitavyam anapekṣya neśvaro\nneśitavyam api tadvad īśvaram",
        size=6.6,
        style="italic",
        color=TEAL,
        inside=L,
    )
    f.text(
        5.5,
        72.4,
        "No ruler without the ruled, no ruled\n"
        "without the ruler: each depends on\n"
        "the other, therefore neither exists.\n"
        "What remains is only Brahman:\n"
        "no Paramātmā, no Bhagavān.",
        size=6.6,
        inside=L,
    )
    pairbox(f, 6.0, 48.5, 12.5, "īśvara", edge=TEAL)
    pairbox(f, 25.0, 48.5, 12.5, "īśitavya", edge=TEAL)
    f.arrow(18.9, 51.0, 24.6, 51.0, color=TEAL, both=True, ms=7, lw=1.0)
    f.text(
        21.75,
        44.6,
        "so neither is real?",
        size=6.6,
        ha="center",
        color=TEAL,
        style="italic",
        inside=L,
    )
    f.text(
        5.5,
        33.8,
        "the half-verse is given as heard,\npending verification",
        size=5.9,
        color=GREY,
        style="italic",
        inside=L,
    )

    R = f.box(46, 25, 51, 61, edge=MAROON)
    f.header(R, "Mahāprabhuji’s answer", size=8.6, color=MAROON)
    f.text(
        48.5,
        80.2,
        "“In things, interdependency causes no\ntrouble.” Both members exist.",
        size=6.6,
        inside=R,
    )
    # row 1
    pairbox(f, 49.0, 67.0, 18.5, "Śaṅkarācārya")
    pairbox(f, 75.0, 67.0, 18.5, "Śaṅkara-bhāṣya")
    f.arrow(67.9, 69.5, 74.6, 69.5, both=True, ms=7, lw=1.0)
    f.text(
        71.5,
        64.6,
        "each is what it is because of the other",
        size=6.2,
        ha="center",
        style="italic",
        color=GREY,
        inside=R,
    )
    # row 2
    pairbox(f, 49.0, 51.0, 11.5, "bhāī")
    pairbox(f, 63.5, 51.0, 11.5, "bhābhī")
    pairbox(f, 81.5, 51.0, 12.0, "bhatrījo")
    f.text(
        62.0, 53.4, "+", size=8, ha="center", va="center", color=MAROON, weight="bold"
    )
    f.arrow(75.4, 53.5, 81.1, 53.5, both=True, ms=7, lw=1.0)
    f.text(
        71.5,
        48.6,
        "ek bhāī, bījī bhābhī, trījo bhatrījo",
        size=6.2,
        ha="center",
        style="italic",
        color=GREY,
        inside=R,
    )
    # row 3
    pairbox(f, 48.6, 35.5, 13.0, "Brahman")
    pairbox(f, 65.0, 35.5, 13.0, "Paramātmā")
    pairbox(f, 81.4, 35.5, 13.0, "Bhagavān")
    f.arrow(62.0, 38.0, 64.6, 38.0, both=True, ms=6, lw=1.0)
    f.arrow(78.4, 38.0, 81.0, 38.0, both=True, ms=6, lw=1.0)
    f.text(
        71.5,
        33.1,
        "not synonyms: names that depend on one another,",
        size=6.2,
        ha="center",
        style="italic",
        color=GREY,
        inside=R,
    )
    f.text(
        71.5,
        29.5,
        "a “gravitation” towards one another",
        size=6.2,
        ha="center",
        style="italic",
        color=GREY,
        inside=R,
    )

    D = f.box(3, 10, 94, 9.0, edge=OCHRE, fill=SAND)
    f.text(
        50,
        17.5,
        "“Interdependency does not mean mithyā.”",
        size=7.6,
        ha="center",
        weight="bold",
        color=MAROON,
        inside=D,
    )
    f.text(
        50,
        13.4,
        "If being interdependent meant that neither comes about, neither would come about.",
        size=6.6,
        ha="center",
        style="italic",
        color=GREY,
        inside=D,
    )
    return f.save("fig5_interdependence.png")


# =====================================================================
def fig6() -> list[str]:
    f = Fig(4.6)
    f.title(
        "The anubandha-catuṣṭaya",
        "granthārtha anivārya: what every grantha must state or indicate (after the speaker’s chart)",
    )
    T = f.box(28, 73.5, 44, 11.5, edge=TEAL)
    f.header(T, "granthārtha anivārya", size=8.6)
    f.text(
        50,
        79.3,
        "the author states or indicates it; if not, the\ncommentator must clarify it",
        size=6.4,
        ha="center",
        inside=T,
    )
    cw, gap = 21.25, 3.0
    x0s = [3.0 + i * (cw + gap) for i in range(4)]
    xs = [x + cw / 2 for x in x0s]
    f.line([50, 50], [72.0, 67.5], color=TEAL, lw=1.0)
    f.line([xs[0], xs[-1]], [67.5, 67.5], color=TEAL, lw=1.0)
    for x in xs:
        f.line([x, x], [67.5, 63.4], color=TEAL, lw=1.0)

    heads = ["adhikārī", "viṣaya", "sambandha", "prayojana"]
    subs = ["for whom?", "what subject?", "how dealt with?", "for what purpose?"]
    gen = [
        "the readership it is\nwritten for: look before\nyou join the queue",
        "the subject matter to\nbe expounded",
        "explain, propound,\nelaborate, criticize,\nor teach disciples?",
        "the purpose for which\nit is written",
    ]
    nib = [
        "Nibandha: stated in\nthe earlier kārikās",
        "Nibandha: bhagavattve\nsati paramātmatve sati\nbrahmatvam",
        "Nibandha: upadeśa-\nnyāya, teaching; not\nvāda-nyāya, polemic",
        "Nibandha: to bring to\nKṛṣṇa-sevā those who,\nafter reading śāstra,\ndo not serve Kṛṣṇa",
    ]
    for i, x in enumerate(x0s):
        b = f.box(x, 27, cw, 35, edge=TEAL)
        f.header(b, heads[i], size=8.6)
        f.text(
            xs[i],
            56.6,
            subs[i],
            size=6.4,
            ha="center",
            style="italic",
            color=GREY,
            inside=b,
        )
        f.text(x + 1.4, 52.6, gen[i], size=6.3, inside=b)
        f.text(x + 1.4, 42.0, nib[i], size=6.3, color=MAROON, inside=b)

    D = f.box(3, 12, 94, 10.0, edge=OCHRE, fill=SAND)
    f.text(
        50,
        20.3,
        "Bismillah’s shehnāī plays for the one who listens, not for the one who sleeps.",
        size=7.2,
        ha="center",
        weight="bold",
        inside=D,
    )
    f.text(
        50,
        16.0,
        "Without adhikārī, viṣaya, sambandha and prayojana, any field becomes a lafḍā.",
        size=6.8,
        ha="center",
        style="italic",
        color=GREY,
        inside=D,
    )
    return f.save("fig6_anubandha.png")


# =====================================================================
def fig7() -> list[str]:
    f = Fig(5.4)
    f.title("Three kinds of concept", "and the pramāṇa on which each rests")
    cols = [
        (
            COLS3[0],
            TEAL,
            "Perceptual concept",
            "jaggery, sugar and honey are\nall sweet, but each sweetness\nis known only by tasting",
            "pramāṇa: pratyakṣa",
        ),
        (
            COLS3[1],
            TEAL,
            "Logical concept",
            "four ducks, two shot: 4 − 2 = 2,\nwhether ducks or laḍḍūs;\nmathematics, geometry, the\ntriangle (Piaget’s small child\ncannot answer yet)",
            "pramāṇa: anumāna, reasoning",
        ),
        (
            COLS3[2],
            MAROON,
            "Verbal concept",
            "the octopus on the sea floor,\nknown from a book; infinity,\nwhich none can see or infer;\nBrahman: satyaṁ jñānam\nanantaṁ brahma",
            "pramāṇa: śabda",
        ),
    ]
    for x, edge, h, b, p in cols:
        bx = f.box(x, 59, CW3, 29, edge=edge)
        f.header(bx, h, size=8.2, color=edge)
        f.text(x + 2.0, 82.0, b, size=6.3, inside=bx)
        f.text(
            x + CW3 / 2,
            63.6,
            p,
            size=6.6,
            ha="center",
            weight="bold",
            color=edge,
            inside=bx,
        )

    L = f.box(3, 30, 44, 23, edge=TEAL)
    f.header(L, "The Cārvāka’s ladder", size=8.2)
    for i, s in enumerate(["pratyakṣa", "anumāna", "śabda"]):
        pairbox(f, 6.0 + i * 14.0, 40.6, 11.4, s, edge=TEAL, size=6.4)
    f.arrow(19.6, 43.1, 17.8, 43.1, color=TEAL, ms=7, lw=1.0)
    f.arrow(33.6, 43.1, 31.8, 43.1, color=TEAL, ms=7, lw=1.0)
    f.text(
        25.0,
        37.6,
        "each rests on the one to its left:\nperception is primordial",
        size=6.2,
        ha="center",
        style="italic",
        color=GREY,
        inside=L,
    )

    R = f.box(53, 30, 44, 23, edge=MAROON)
    f.header(R, "Mahāprabhuji and Vedānta", size=8.2, color=MAROON)
    pairbox(f, 56.5, 41.0, 16.0, "pratyakṣa", edge=TEAL, size=6.4)
    pairbox(f, 77.5, 41.0, 16.0, "anumāna", edge=TEAL, size=6.4)
    f.ax.add_patch(
        FancyBboxPatch(
            (56.5, 35.6),
            37.0,
            3.6,
            boxstyle="round,pad=0.4",
            fc=SAND,
            ec=MAROON,
            lw=1.0,
            zorder=3,
        )
    )
    f.text(
        75.0,
        37.4,
        "śabda runs through both",
        size=6.4,
        ha="center",
        va="center",
        color=MAROON,
        weight="bold",
        inside=R,
    )
    f.text(
        75.0,
        33.6,
        "na so 'sti pratyayo loke yaḥ śabdānugamād ṛte",
        size=6.0,
        ha="center",
        style="italic",
        color=GREY,
        inside=R,
    )

    D = f.box(3, 12, 94, 12.0, edge=OCHRE, fill=SAND)
    f.text(
        50,
        22.3,
        "A lakṣaṇa shows only possibility; proof needs pramāṇa.",
        size=7.2,
        ha="center",
        weight="bold",
        inside=D,
    )
    f.text(
        50,
        18.6,
        "Brahman, like infinity, is a purely verbal concept, so its pramāṇa too is verbal.",
        size=6.8,
        ha="center",
        inside=D,
    )
    f.text(
        50,
        15.2,
        "The exception is when Brahman manifests itself: the case of Puṣṭi.",
        size=6.4,
        ha="center",
        style="italic",
        color=GREY,
        inside=D,
    )
    return f.save("fig7_concepts.png")


# =====================================================================
def fig8() -> list[str]:
    f = Fig(5.6)
    f.title(
        "Four pramāṇas, one dome",
        "etac catuṣṭayam ekavākyatāpannam: separate them and all four collapse",
    )
    cx, cy, r_in, r_out = 50.0, 50.5, 13.5, 23.5
    blocks = [
        (146, 180, "1", TEAL),
        (112, 146, "2", TEAL),
        (68, 112, "", MAROON),
        (34, 68, "3", TEAL),
        (0, 34, "4", TEAL),
    ]
    for a0, a1, lab, edge in blocks:
        pts = annulus_sector(cx, cy, r_in, r_out, a0, a1, f.asp)
        fill = SAND if edge == TEAL else "#EBD3CC"
        f.ax.add_patch(
            Polygon(
                pts,
                closed=True,
                fc=fill,
                ec=edge,
                lw=1.3 if edge == TEAL else 1.8,
                zorder=3,
            )
        )
        if lab:
            am = math.radians((a0 + a1) / 2)
            rm = (r_in + r_out) / 2
            f.text(
                cx + rm * math.cos(am),
                cy + rm * f.asp * math.sin(am),
                lab,
                size=9,
                ha="center",
                va="center",
                weight="bold",
                color=TEAL,
            )
    f.text(
        cx,
        cy + 18.5 * f.asp,
        "Śrī Kṛṣṇa",
        size=7.0,
        ha="center",
        va="center",
        weight="bold",
        color=MAROON,
    )
    f.line([cx - r_out - 3, cx + r_out + 3], [cy, cy], color=GREY, lw=1.4)
    top = cy + r_out * f.asp
    f.text(
        cx,
        top + 9.6,
        "the keystone: resolves the contradictions\nand holds all four together",
        size=6.6,
        ha="center",
        style="italic",
        color=MAROON,
    )
    f.line([cx, cx], [top + 3.6, top + 0.6], color=OCHRE, lw=0.9)
    f.text(
        cx,
        cy - 3.1,
        "uttaraṁ pūrva-sandeha-vārakam: each removes the doubt the one before it leaves",
        size=6.6,
        ha="center",
        style="italic",
        color=GREY,
    )

    def outer(adeg):
        a = math.radians(adeg)
        return cx + (r_out + 0.6) * math.cos(a), cy + (r_out + 0.6) * f.asp * math.sin(
            a
        )

    labels = [
        (3.5, 63.0, "1 · Vedas", "make the thing known\n(vastu-bodhaka)", 163, "L"),
        (3.5, 82.0, "2 · Gītā", "Bhagavān’s words, for\nArjuna’s doubt", 129, "L"),
        (
            75.5,
            82.0,
            "3 · Brahmasūtra",
            "binding on all, like a\nSupreme Court judgement",
            51,
            "R",
        ),
        (
            75.5,
            63.0,
            "4 · Bhāgavata",
            "samādhi-bhāṣā: the\ndemonstration in līlā",
            17,
            "R",
        ),
    ]
    for x, y, h, b, ang, side in labels:
        box = (x - 0.8, y - 9.2, 23.6, 10.8)
        f.text(x, y, h, size=7.6, weight="bold", color=TEAL, inside=box)
        f.text(x, y - 3.2, b, size=6.4, inside=box)
        bx, by = outer(ang)
        sx = 23.4 if side == "L" else 74.6
        f.line([sx, bx], [y - 1.4, by], color=OCHRE, lw=0.8)

    L = f.box(3, 20, 45, 21, edge=MAROON)
    f.header(L, "Pramāṇa: valid source of knowledge", size=8.0, color=MAROON)
    f.text(
        5.5,
        34.6,
        "The four together are one pramāṇa, in\n"
        "coordination (ekavākyatā), like four pens\n"
        "leaning on one another, or an arch.\n"
        "Vallabhācārya accepted four pramāṇas,\n"
        "not four prasthānas.",
        size=6.5,
        inside=L,
    )
    R = f.box(52, 20, 45, 21, edge=TEAL)
    f.header(R, "Prasthāna: departure point", size=8.0)
    f.text(
        54.5,
        34.6,
        "Where schools set out apart: the Śaṅkara,\n"
        "the Rāmānuja and the Vallabha prasthāna.\n"
        "Counting the texts commented on (Śaṅkara\n"
        "three, Madhva six) does not measure an\n"
        "ācārya; an editor’s title page proves nothing.",
        size=6.5,
        inside=R,
    )
    return f.save("fig8_dome.png")


def main() -> int:
    problems: list[str] = []
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        problems += fn()
    for p in problems:
        print("OVERFLOW", p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
