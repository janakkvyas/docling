#!/usr/bin/env python3
"""Figures for Śāstrārtha Prakaraṇa, Lecture 8 (2026-08-29).

Layout rules: every card's text is drawn first (header centred near the top,
body top-anchored below it), measured with the Agg renderer, and the rounded
box is then sized to fit underneath, so boxes grow downward with their text.
All vertical spacing is given in points, so a figure looks the same at any
canvas height; each figure is drawn twice, the second time on a canvas cut to
the height of its content. Any text crossing its box edge is reported.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.family"] = "DejaVu Sans"

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"

OUT = Path(__file__).resolve().parent / "figs08"
OUT.mkdir(exist_ok=True)

PROBLEMS: list[str] = []

X3 = [3, 35.3, 67.6]
W3 = 29.4


class Canvas:
    def __init__(
        self, name: str, height: float, title: str, subtitle: str | None = None
    ):
        self.name = name
        self.height = height
        self.fig = plt.figure(figsize=(6.2, height), dpi=200, facecolor=PALE)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis("off")
        self.renderer = self.fig.canvas.get_renderer()
        t = self.ax.text(
            50,
            100 - self.pt(4),
            title,
            ha="center",
            va="top",
            fontsize=12,
            fontweight="bold",
            color=INK,
        )
        self.cursor = self.extent(t)[1] - self.pt(6)
        if subtitle:
            s = self.ax.text(
                50,
                self.cursor,
                subtitle,
                ha="center",
                va="top",
                fontsize=7.2,
                style="italic",
                color=GREY,
            )
            self.cursor = self.extent(s)[1] - self.pt(7)

    def pt(self, p: float) -> float:
        """Convert points to vertical data units on this canvas."""
        return p / 72 * 100 / self.height

    # ---- measurement -------------------------------------------------
    def extent(self, artist):
        bb = artist.get_window_extent(renderer=self.renderer)
        inv = self.ax.transData.inverted()
        (x0, y0), (x1, y1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
        return x0, y0, x1, y1

    # ---- primitives --------------------------------------------------
    def box(self, x, y, w, h, fc=SAND, ec=TEAL, lw=1.1, z=1):
        if x < 2 or x + w > 98 or y < 0 or y + h > 100:
            PROBLEMS.append(
                f"{self.name}: box outside canvas at x={x:.1f}-{x + w:.1f}, y={y:.1f}-{y + h:.1f}"
            )
        p = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012",
            mutation_scale=45,
            fc=fc,
            ec=ec,
            lw=lw,
            zorder=z,
        )
        self.ax.add_patch(p)

    def arrow(self, x0, y0, x1, y1, color=OCHRE, lw=1.3, ms=11):
        self.ax.add_patch(
            FancyArrowPatch(
                (x0, y0),
                (x1, y1),
                arrowstyle="-|>",
                mutation_scale=ms,
                color=color,
                lw=lw,
                zorder=3,
                shrinkA=0,
                shrinkB=0,
            )
        )

    def text(
        self,
        x,
        y,
        s,
        size=6.7,
        color=INK,
        ha="center",
        style="normal",
        weight="normal",
        ls=1.33,
        va="top",
    ):
        return self.ax.text(
            x,
            y,
            s,
            ha=ha,
            va=va,
            fontsize=size,
            color=color,
            style=style,
            fontweight=weight,
            linespacing=ls,
            zorder=4,
        )

    def check(self, label, artist, x, w, y_bottom=None, y_top=None, margin=1.1):
        x0, y0, x1, y1 = self.extent(artist)
        if x0 < x + margin - 0.01 or x1 > x + w - margin + 0.01:
            PROBLEMS.append(
                f"{self.name}: OVERFLOW (width) in '{label[:45]}': "
                f"text {x0:.1f}-{x1:.1f} vs box {x:.1f}-{x + w:.1f}"
            )
        if y_bottom is not None and y0 < y_bottom + self.pt(1.5):
            PROBLEMS.append(f"{self.name}: OVERFLOW (bottom) in '{label[:45]}'")
        if y_top is not None and y1 > y_top - self.pt(1.5):
            PROBLEMS.append(f"{self.name}: OVERFLOW (top) in '{label[:45]}'")

    # ---- cards -------------------------------------------------------
    def row(self, specs, ytop, gap=7):
        """Cards sharing a top edge; equal heights. Returns (next_top, bottom)."""
        placed = []
        for s in specs:
            x, w = s["x"], s["w"]
            ec = s.get("ec", TEAL)
            tcolor = s.get("tcolor", INK if ec == GREY else ec)
            y = ytop - self.pt(5)
            arts = []
            if s.get("title"):
                t = self.text(
                    x + w / 2,
                    y,
                    s["title"],
                    size=s.get("tsize", 8.4),
                    color=tcolor,
                    weight="bold",
                    ls=1.2,
                )
                arts.append(("title", t))
                y = self.extent(t)[1] - self.pt(3.4)
            if s.get("text"):
                if s.get("align") == "center":
                    b = self.text(x + w / 2, y, s["text"], size=s.get("bsize", 6.7))
                else:
                    b = self.text(
                        x + 1.7, y, s["text"], size=s.get("bsize", 6.7), ha="left"
                    )
                arts.append(("text", b))
            placed.append((s, arts, min(self.extent(a)[1] for _, a in arts)))
        bottom = min(p[2] for p in placed) - self.pt(5.5)
        for s, arts, _ in placed:
            ec = s.get("ec", TEAL)
            self.box(
                s["x"],
                bottom,
                s["w"],
                ytop - bottom,
                fc=s.get("fc", SAND),
                ec=ec,
                lw=1.6 if ec == MAROON else 1.1,
            )
            for kind, a in arts:
                self.check(
                    f"{kind}:{s.get('title') or s.get('text')}",
                    a,
                    s["x"],
                    s["w"],
                    y_bottom=bottom,
                    y_top=ytop,
                )
        return bottom - self.pt(gap), bottom

    def banner(self, text, ytop, x=3, w=94, size=7.0, color=INK, bold=False):
        t = self.text(
            x + w / 2,
            ytop - self.pt(4.5),
            text,
            size=size,
            color=color,
            ls=1.35,
            weight="bold" if bold else "normal",
        )
        yb = self.extent(t)[1] - self.pt(5)
        self.box(x, yb, w, ytop - yb, fc=SAND, ec=OCHRE, lw=1.4)
        self.check("banner:" + text, t, x, w, y_bottom=yb, y_top=ytop)
        return yb

    def finish(self, bottom, save):
        if save:
            path = OUT / f"{self.name}.png"
            self.fig.savefig(
                path, dpi=200, bbox_inches="tight", pad_inches=0.12, facecolor=PALE
            )
            print(
                "wrote",
                path.name,
                f"height {self.height:.2f} in, lowest y {bottom:.1f}",
            )
        plt.close(self.fig)
        return bottom


# ---------------------------------------------------------------- Figure 1
def fig1(H, save):
    c = Canvas(
        "fig1_laws",
        H,
        "The laws of thought — and the Veda that broke them first",
        "Aristotelian “laws of thought”, still taken as the criteria of “rationality”",
    )
    y, b1 = c.row(
        [
            dict(
                x=X3[0],
                w=W3,
                title="1 · Law of\nidentity",
                tsize=7.8,
                text="“A is A.”\nAs a doctrine: advaita,\npure abheda.",
            ),
            dict(
                x=X3[1],
                w=W3,
                title="2 · Law of\nnon-contradiction",
                tsize=7.8,
                text="“A cannot be both B and not B”:\neither B or not-B — it cannot\nbe both.",
            ),
            dict(
                x=X3[2],
                w=W3,
                title="3 · Law of\nexcluded middle",
                tsize=7.8,
                text="“There cannot be any term\nbetween A and not A”: black or\nnot-black. (Yet what is neither\nyellow nor blue may be green.)",
            ),
        ],
        c.cursor,
        gap=22,
    )
    for x in X3:
        c.arrow(x + W3 / 2, b1 - c.pt(2), x + W3 / 2, y + c.pt(2))
    c.text(
        51.6,
        (b1 + y) / 2,
        "broken by",
        size=6.8,
        color=OCHRE,
        style="italic",
        va="center",
        ha="left",
    )
    y, _ = c.row(
        [
            dict(
                x=X3[0],
                w=W3,
                ec=MAROON,
                fc=PALE,
                title="aitadātmyam idaṁ sarvam",
                tsize=6.9,
                text="(Chāndogya 6.8.7) All this that\nis seen is identical with\nBrahman.",
            ),
            dict(
                x=X3[1],
                w=W3,
                ec=MAROON,
                fc=PALE,
                title="brahma dāśā brahma dāsā",
                tsize=6.9,
                text="(AV Paippalāda 8.9.11) Black and\nwhite, sin and merit, atomic and\nvast, joy and sorrow — all\ncontradictory, and all Brahman.",
            ),
            dict(
                x=X3[2],
                w=W3,
                ec=MAROON,
                fc=PALE,
                title="samo nāgena samo maśakena",
                tsize=6.9,
                text="(Bṛhadāraṇyaka 1.3.22) Equal to\nthe elephant and the mosquito;\naṇor aṇīyān mahato mahīyān\n(Kaṭha 1.2.20): a middle term.",
            ),
        ],
        y,
        gap=8,
    )
    yb = c.banner(
        "Science swept these laws away later; the Veda had broken them first.\n"
        "What they mark is a limitation of rationality — not a limitation of reality.",
        y,
        bold=True,
        color=MAROON,
    )
    return c.finish(yb, save)


# ---------------------------------------------------------------- Figure 2
def fig2(H, save):
    c = Canvas("fig2_altars", H, "A limit of rationality, not of reality")
    top = c.cursor
    # right column first: who sacrificed on which altar
    h = c.text(74.5, top - c.pt(1), "Whose altar?", size=8.6, weight="bold")
    y = c.extent(h)[1] - c.pt(5)
    y, _ = c.row(
        [
            dict(
                x=52,
                w=45,
                title="Altar of śruti — Śaṅkara, first",
                text="Brahman a fortress the logicians’ hired soldiers\ncannot enter; “it moves, it does not move”\n(Īśā 5): attributes against the laws of thought.",
            )
        ],
        y,
        gap=5,
    )
    y, _ = c.row(
        [
            dict(
                x=52,
                w=45,
                ec=MAROON,
                fc=PALE,
                title="Vallabha — receives the merit",
                text="Whatever merit that sacrifice earned, Vallabha\ngot it and took it: tarkāpratiṣṭhānāt (BS 2.1.11).",
            )
        ],
        y,
        gap=5,
    )
    y, _ = c.row(
        [
            dict(
                x=52,
                w=45,
                title="Altar of pratyakṣa — science",
                text="Light observed to be both particle and wave.",
            )
        ],
        y,
        gap=5,
    )
    _, right_bottom = c.row(
        [
            dict(
                x=52,
                w=45,
                ec=GREY,
                fc=PALE,
                title="The charge (Mrudula Marfatia)",
                text="“On the altar of the authority of Veda\nVallabhacharya slaughtered the rationality.”",
            )
        ],
        y,
        gap=8,
    )
    # left column: reality and, inside it, rationality
    t1 = c.text(25.5, top - c.pt(5), "REALITY", size=9, color=MAROON, weight="bold")
    t2 = c.text(
        25.5, c.extent(t1)[1] - c.pt(3), "“Reality is fully contradictory”", size=6.9
    )
    t3 = c.text(
        25.5,
        c.extent(t2)[1] - c.pt(5),
        "sur-real: “above” the reality that\nrationality grasps",
        size=6.6,
        color=GREY,
        style="italic",
    )
    inner_top = c.extent(t3)[1] - c.pt(7)
    t4 = c.text(
        25.5, inner_top - c.pt(5), "RATIONALITY", size=8.6, color=TEAL, weight="bold"
    )
    t5 = c.text(
        25.5,
        c.extent(t4)[1] - c.pt(3.4),
        "grasps a “portion” of reality,\nbound by the laws of thought;\n“rational” = what it can grasp",
        size=6.6,
    )
    inner_bottom = c.extent(t5)[1] - c.pt(5.5)
    t6 = c.text(
        25.5,
        inner_bottom - c.pt(6),
        "irrational: what contradicts\nrationality",
        size=6.6,
        color=GREY,
        style="italic",
    )
    natural_bottom = c.extent(t6)[1] - c.pt(6)
    outer_bottom = min(natural_bottom, right_bottom)
    # centre the sur-real / rationality / irrational group in any spare height
    shift = (natural_bottom - outer_bottom) / 2
    for t in (t3, t4, t5, t6):
        tx, ty = t.get_position()
        t.set_position((tx, ty - shift))
    inner_top -= shift
    inner_bottom -= shift
    c.box(3, outer_bottom, 45, top - outer_bottom, fc=SAND, ec=MAROON, lw=1.6, z=1)
    c.box(9, inner_bottom, 33, inner_top - inner_bottom, fc=PALE, ec=TEAL, lw=1.2, z=2)
    c.check("rationality", t5, 9, 33, y_bottom=inner_bottom, y_top=inner_top)
    for t in (t1, t2, t3, t6):
        c.check("reality", t, 3, 45, y_bottom=outer_bottom, y_top=top)
    yb = c.banner(
        "“Someone sacrificed on the altar of śruti, someone on the altar of logic, someone on the altar of fact —\n"
        "what is there in this to raise such a hue and cry?”",
        outer_bottom - c.pt(8),
    )
    return c.finish(yb, save)


# ---------------------------------------------------------------- Figure 3
def fig3(H, save):
    c = Canvas("fig3_third", H, "Tādātmya: a third category")
    y, b = c.row(
        [
            dict(
                x=X3[0],
                w=W3,
                title="Abheda",
                text="“A is A” — the law of identity:\nadvaita, pure abheda.",
            ),
            dict(
                x=X3[1],
                w=W3,
                title="Bheda",
                text="“A cannot be both B and not B”:\nA and B are different.",
            ),
            dict(
                x=X3[2],
                w=W3,
                ec=GREY,
                fc=PALE,
                title="Bhedābheda",
                text="A mere combination of the two —\ntādātmya is not this either.",
            ),
        ],
        c.cursor,
        gap=18,
    )
    c.text(
        50,
        (b + y) / 2,
        "a third category — none of these, nor their mixture",
        size=6.8,
        color=OCHRE,
        style="italic",
        va="center",
    )
    y, b = c.row(
        [
            dict(
                x=10,
                w=80,
                ec=MAROON,
                fc=PALE,
                tsize=9,
                align="center",
                title="Tādātmya — Mahāprabhuji’s main principle",
                text="“A is equivalent to both B and not B” — an abheda that tolerates bheda (bheda-sahiṣṇu abheda):\n"
                "a third quality, neither bheda nor abheda, functioning both ways at once.",
            )
        ],
        y,
        gap=18,
    )
    c.text(
        50,
        (b + y) / 2,
        "reality is full of it",
        size=6.8,
        color=OCHRE,
        style="italic",
        va="center",
    )
    ex = [
        ("The poles", "Sunset on one side and sunrise\non the other, simultaneously."),
        ("Blood", "White and red cells — protector\nand destroyer — in one blood."),
        ("Gaṇapati", "Pārvatī’s yakṣa, given an elephant\ncalf’s head and devahood."),
        ("The bat", "An animal — and it flies."),
        ("The whale", "A fish, and also an animal."),
        ("Light", "Particle and wave: science’s\nsacrifice on the altar of pratyakṣa."),
    ]
    y, _ = c.row(
        [
            dict(x=X3[i], w=W3, title=t, text=s, tsize=8.0)
            for i, (t, s) in enumerate(ex[:3])
        ],
        y,
        gap=6.5,
    )
    y, _ = c.row(
        [
            dict(x=X3[i], w=W3, title=t, text=s, tsize=8.0)
            for i, (t, s) in enumerate(ex[3:])
        ],
        y,
        gap=8,
    )
    yb = c.banner(
        "Everyone accepts tādātmya somewhere — Śaṅkara between māyā and the māyika,\n"
        "Madhva between avatāra and avatārī. Mahāprabhuji applies it to all of Brahman’s activity:\n"
        "“in a nutshell”, this is Śuddhādvaita.",
        y,
    )
    return c.finish(yb, save)


# ---------------------------------------------------------------- Figure 4
def fig4(H, save):
    c = Canvas("fig4_formats", H, "Many formats of tādātmya, one formula")
    cells = [
        ("Formal", "The form is alike: me and a\nstatue or a photo of me."),
        (
            "Utilitarian · pragmatic",
            "The same work gets done:\nmotorbike, car, train, plane;\nmedicines of different make-up.",
        ),
        ("Substantial", "One substance: a gold crown —\nand a gold toilet."),
        (
            "Virtual",
            "All the qualities, not the\nsubstance: artificial rose\nperfume smells of the rose.",
        ),
        None,
        (
            "Illusory",
            "An illusion shows tādātmya\nwith its adhiṣṭhāna, what it is\nset up on.",
        ),
        (
            "Contingent",
            "Light is no colour; coloured\nglass gives it red, blue, yellow.",
        ),
        (
            "Imposed (āropita)",
            "Red: stop. Green: go. Yellow:\nget ready — and in Italy, red\nmeans “at your own risk”.",
        ),
        (
            "Tao",
            "This in that, that in this:\nmayi te teṣu cāpy aham\n(Bhagavadgītā 9.29).",
        ),
    ]
    y = c.cursor
    for r in range(3):
        specs = []
        for col in range(3):
            cell = cells[r * 3 + col]
            if cell is None:
                specs.append(
                    dict(
                        x=X3[col],
                        w=W3,
                        ec=MAROON,
                        fc=PALE,
                        tsize=10.5,
                        align="center",
                        title="A ≡ B",
                        text="there is an A, there is a B —\nduality — and they are identical:\n“its name is samanvaya”",
                    )
                )
            else:
                specs.append(
                    dict(x=X3[col], w=W3, title=cell[0], text=cell[1], tsize=8.2)
                )
        y, _ = c.row(specs, y, gap=5 if r < 2 else 8)
    yb = c.banner(
        "Understand tādātmya and the whole of Śuddhādvaita is understood;\n"
        "miss it, and every later line evaporates like camphor from its paper packet.",
        y,
        bold=True,
        color=MAROON,
    )
    return c.finish(yb, save)


# ---------------------------------------------------------------- Figure 5
def fig5(H, save):
    c = Canvas("fig5_condition", H, "Illusion goes when its condition goes")
    y, b = c.row(
        [
            dict(
                x=3,
                w=45.5,
                title="Śaṅkara’s model",
                text="ignorance (ajñāna)  →  illusion (bhrama)\ndestroy ignorance by brahma-jñāna  →\nthe world-illusion comes to an end",
            ),
            dict(
                x=51.5,
                w=45.5,
                ec=MAROON,
                fc=PALE,
                title="“Point one”",
                text="ignorance and illusion are different phenomena:\nthe knowledge can be present and the illusion\nstays; it ends only when its condition ends",
            ),
        ],
        c.cursor,
        gap=18,
    )
    c.arrow(50, b - c.pt(2), 50, y + c.pt(2))
    c.text(
        52,
        (b + y) / 2,
        "for example",
        size=6.8,
        color=OCHRE,
        style="italic",
        va="center",
        ha="left",
    )
    q = 22.0
    xs = [3, 3 + q + 2, 3 + 2 * (q + 2), 3 + 3 * (q + 2)]
    ex = [
        ("Mirror", "We know I am not in\nthe mirror; the\nreflection still appears."),
        (
            "Rainbow",
            "We know there is no\nrainbow; it appears in\nrain and in a fountain:\na “defect”, not\nignorance.",
        ),
        (
            "Jaundice",
            "Knowing it is white,\nwe still see yellow;\nit goes when the\njaundice goes.",
        ),
        (
            "Horizon",
            "Known to be nothing,\nit is still seen; rising,\nit widens 3, 6, 12, 24,\n48 miles; from a rocket,\nthe whole hemisphere.",
        ),
    ]
    y, _ = c.row(
        [
            dict(x=xs[i], w=q, title=t, text=s, tsize=8.2, bsize=6.6)
            for i, (t, s) in enumerate(ex)
        ],
        y,
        gap=8,
    )
    yb = c.banner(
        "Bhagavān’s avidyā-śakti limits our understanding, so “Vallabhacharya slaughtered the rationality”\n"
        "is itself such an illusion — a limited horizon. Widen it a little and the problem is solved.",
        y,
    )
    return c.finish(yb, save)


# ---------------------------------------------------------------- Figure 6
def fig6(H, save):
    c = Canvas(
        "fig6_buddhi",
        H,
        "The functions of buddhi",
        "smṛtir vyatītaviṣayā matir āgāmigocarā · buddhis tātkālikī proktā prajñā traikālikī matā",
    )
    lab1 = c.text(
        36.75, c.cursor, "receptive intelligence", size=6.9, color=GREY, style="italic"
    )
    c.text(
        85.75, c.cursor, "creative intelligence", size=6.9, color=GREY, style="italic"
    )
    top = c.extent(lab1)[1] - c.pt(4)
    y, b = c.row(
        [
            dict(
                x=3,
                w=20.9,
                title="Smṛti · past",
                tsize=8.0,
                bsize=6.5,
                text="vyatīta-viṣayā: memory.\nThe old live in it:\n“when we were little…”",
            ),
            dict(
                x=26.3,
                w=20.9,
                title="Buddhi · present",
                tsize=8.0,
                bsize=6.5,
                text="tātkālikī: grasps what\nis happening now. The\nanimal at the mirror\nfails, and is deluded.",
            ),
            dict(
                x=49.6,
                w=20.9,
                title="Mati · future",
                tsize=8.0,
                bsize=6.5,
                text="āgāmi-gocarā: what is\nto come. Children live\nin dreams: Grandpa’s\nhorse, Nanda’s shoes.",
            ),
            dict(
                x=74.5,
                w=22.5,
                ec=TEAL,
                fc=PALE,
                title="Pratibhā",
                tsize=8.0,
                bsize=6.5,
                text="navanavonmeṣa-\nśālinī: creative\nintelligence, by which\nsomething new is made.",
            ),
        ],
        top,
        gap=24,
    )
    axis_y = b - c.pt(8)
    c.arrow(4, axis_y, 69.5, axis_y, lw=1.2, ms=9)
    for x, s in [(13.45, "past"), (36.75, "present"), (60.05, "future")]:
        c.text(x, axis_y - c.pt(9), s, size=6.4, color=OCHRE, va="baseline")
    y, b = c.row(
        [
            dict(
                x=3,
                w=67.5,
                ec=MAROON,
                fc=PALE,
                title="Prajñā · all three times",
                tsize=8.6,
                text="traikālikī: aware of past, present and future — a work born of prajñā can never\n"
                "be wrong. The world is born of Brahman’s prajñā, not of smṛti.",
            )
        ],
        y,
        gap=8,
    )
    yb = c.banner(
        "Stuck in any one function: disease. All in coordination, in proportion: health —\n"
        "like vāta, pitta and kapha, or the white cells. Out of proportion even truth becomes untruth;\n"
        "the omniscient made the world proportionate and mutually dependent.",
        y,
        size=6.8,
    )
    return c.finish(yb, save)


# ---------------------------------------------------------------- Figure 7
def fig7(H, save):
    c = Canvas("fig7_obstacles", H, "One kārikā, two obstructions to bhajana removed")
    top = c.cursor
    chip_h = c.pt(14)
    c.text(
        12.0, top - chip_h / 2, "senses of māyā:", size=7.0, weight="bold", va="center"
    )
    chips = [
        ("prajñā · wisdom", TEAL, 15.5),
        ("icchā · will", TEAL, 12.5),
        ("sarvabhavana-sāmarthya", MAROON, 25.0),
        ("trick · fooling", TEAL, 15.5),
    ]
    x = 23.0
    for s, col, w in chips:
        c.box(
            x,
            top - chip_h,
            w,
            chip_h,
            fc=PALE,
            ec=col,
            lw=1.4 if col == MAROON else 1.0,
        )
        t = c.text(
            x + w / 2,
            top - chip_h / 2,
            s,
            size=6.6,
            color=col,
            va="center",
            weight="bold" if col == MAROON else "normal",
        )
        c.check("chip " + s, t, x, w)
        x += w + 1.5
    y = top - chip_h - c.pt(10)
    cols, wcol = [3, 36.0, 69.0], [28.5, 28.5, 28.0]
    rows = [
        (
            (
                "Obstruction 1",
                "“the prapañca is mithyā”:\nprapañco mithyā dṛśyatvāt\nsvapnavat — then bhajana,\nbhakta and Bhagavān are\nall mithyā",
            ),
            (
                "prapañco bhagavatkāryas\ntadrūpo māyayābhavat",
                "the world is Bhagavān’s\neffect, of his very form,\nthrough his sarvabhavana-\nsāmarthya: a product of\nhis wisdom",
            ),
            (
                "Hence",
                "the prapañca is not mithyā:\nbhajana as relish of a world\nidentical with him stays\npossible",
            ),
        ),
        (
            (
                "Obstruction 2",
                "“the jīva is vyāpaka”: then\nwhy set Brahman apart?\nBhajana becomes null\nand void",
            ),
            (
                "tacchaktyāvidyayā tv asya\njīvasaṁsāra ucyate",
                "his avidyā-śakti limits\nthe jīva’s understanding:\nsaṁsāra and illusion arise",
            ),
            (
                "Hence",
                "a jīva that has illusion is\nnot vyāpaka but aṇu — so\nit should do bhajana",
            ),
        ),
    ]
    for r, (o, k, h) in enumerate(rows):
        ny, b = c.row(
            [
                dict(x=cols[0], w=wcol[0], title=o[0], text=o[1], tsize=8.2, bsize=6.6),
                dict(
                    x=cols[1],
                    w=wcol[1],
                    ec=MAROON,
                    fc=PALE,
                    title=k[0],
                    text=k[1],
                    tsize=7.6,
                    bsize=6.6,
                ),
                dict(
                    x=cols[2],
                    w=wcol[2],
                    ec=OCHRE,
                    tcolor=OCHRE,
                    title=h[0],
                    text=h[1],
                    tsize=8.2,
                    bsize=6.6,
                ),
            ],
            y,
            gap=6 if r == 0 else 8,
        )
        mid = (y + b) / 2
        c.arrow(cols[0] + wcol[0] + 0.7, mid, cols[1] - 0.7, mid)
        c.arrow(cols[1] + wcol[1] + 0.7, mid, cols[2] - 0.7, mid)
        y = ny
    yb = c.banner(
        "Prakāśa (as heard): ata ubhaya-nirākaraṇārthaṁ jaḍa-jīvayoḥ svarūpam ucyate —\n"
        "the svarūpa of jaḍa and jīva is stated so as to remove both obstructions.",
        y,
    )
    return c.finish(yb, save)


# ---------------------------------------------------------------- Figure 8
def fig8(H, save):
    c = Canvas("fig8_shuddha", H, "Śuddha and advaita: in whose sense?")
    l = c.text(
        25.75, c.cursor, "readings set aside", size=8.2, color=TEAL, weight="bold"
    )
    c.text(
        74.25, c.cursor, "Mahāprabhuji’s sense", size=8.2, color=MAROON, weight="bold"
    )
    top = c.extent(l)[1] - c.pt(5)
    yl, _ = c.row(
        [
            dict(
                x=3,
                w=45.5,
                title="śuddhayor advaitam",
                tsize=8.2,
                text="the advaita of the pure jaḍa and jīva with\nBrahman — so the impure would stand outside\n"
                "Brahman’s advaita. Yet Śrīnāthajī partook of\nTāj Bībī’s bhoga and Mohanā Bhaṅgī’s kaḍhī.",
            )
        ],
        top,
        gap=5,
    )
    yl, _ = c.row(
        [
            dict(
                x=3,
                w=45.5,
                title="śuddhaṁ ca tad advaitaṁ ca",
                tsize=8.2,
                text="an advaita that is pure — pure as against\nwhat? If it is advaita, there is no dvaita\nleft to exclude.",
            )
        ],
        yl,
        gap=5,
    )
    yl, _ = c.row(
        [
            dict(
                x=3,
                w=45.5,
                ec=GREY,
                fc=PALE,
                title="Mārtaṇḍa: “free of relation with māyā”",
                tsize=8.0,
                text="a “limited meaning”: as a mere quarrel with\nthe Śāṅkaras it becomes jalpa, not vāda.",
            )
        ],
        yl,
        gap=8,
    )
    yr, _ = c.row(
        [
            dict(
                x=51.5,
                w=45.5,
                ec=MAROON,
                fc=PALE,
                title="ŚUDDHA — no cause but Brahman",
                tsize=8.4,
                text="na prākṛtaḥ · nāpi paramāṇujanyaḥ ·\nnāpi vivartātmā · nāpy adṛṣṭādi-dvārā jātaḥ ·\n"
                "nāpy asataḥ sattārūpaḥ. Prakṛti, atoms, māyā,\nadṛṣṭa are all Brahman’s own:\nsac ca tyac cābhavat (Taittirīya 2.6.1).",
            )
        ],
        top,
        gap=5,
    )
    yr, _ = c.row(
        [
            dict(
                x=51.5,
                w=45.5,
                ec=MAROON,
                fc=PALE,
                title="ADVAITA — cause and effect",
                tsize=8.4,
                text="bhagavat-kārya (A) is also bhagavad-rūpa (B):\nA ≡ B, tādātmya. Otherwise the non-existent\nwould have existence (asataḥ sattā).",
            )
        ],
        yr,
        gap=8,
    )
    yb = c.banner(
        "Hence vāda, not jalpa: Mahāprabhuji states his own doctrine,\n"
        "with no quarrel with Śaṅkara, Rudra’s avatāra. The root meaning of Śuddhādvaita:\n"
        "the prapañca is not mithyā, and the jīva is not vyāpaka.",
        min(yl, yr),
        bold=True,
        color=MAROON,
        size=6.8,
    )
    return c.finish(yb, save)


def build(fn):
    """Draw once on a tall canvas, then again on a canvas cut to the content."""
    probe_h = 9.0
    lowest = fn(probe_h, False)
    content_in = (100 - lowest) / 100 * probe_h
    fn(round(content_in + 0.04, 3), True)


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        build(f)
    # each figure is drawn twice; report each problem once
    seen = []
    for p in PROBLEMS:
        if p not in seen:
            seen.append(p)
    print("\n".join(seen) if seen else "no overflow detected")
