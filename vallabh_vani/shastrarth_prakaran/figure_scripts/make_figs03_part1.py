#!/usr/bin/env python3
"""Figures 1-4 for Lecture 3, Part 1 (session of 2026-07-25).

Writes build/figs03/fig1_*.png ... fig4_*.png (Part 2 owns fig5-fig8) and a
contact sheet in the scratch folder. House rules: Agg backend, DejaVu Sans,
width 6.2in, dpi 200, axes 0-100 both ways, axis off, IAST/English only,
rounded boxes, top-anchored body text. Horizontal positions are in data units
(0-100); vertical positions are given in inches from the top of the canvas so
that each canvas can be sized to its content.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Wedge  # noqa: E402
from PIL import Image  # noqa: E402

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"

plt.rcParams["font.family"] = "DejaVu Sans"
OUT = Path(__file__).resolve().parent / "figs03"
SHEET_DIR = Path(
    "/tmp/claude-0/-home-user-docling/52cfa96e-0437-507f-b456-a63b9493e8f7/scratchpad/l03p1"
)
W = 6.2
SPACING = 1.32


def lh(fs: float) -> float:
    """Line height in inches for a font size in points."""
    return fs * SPACING / 72.0


class Canvas:
    """Width 6.2in; x in data units 0-100, y given in inches from the top."""

    def __init__(self, height: float):
        self.h = height
        self.fig = plt.figure(figsize=(W, height), dpi=200)
        self.fig.patch.set_facecolor(PALE)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis("off")

    def y(self, inch: float) -> float:
        return 100.0 - inch / self.h * 100.0

    def d(self, inch: float) -> float:
        return inch / self.h * 100.0

    def box(self, x, top, w, height, edge=TEAL, face=SAND, lw=1.1, rounding=0.9):
        patch = FancyBboxPatch(
            (x, self.y(top + height)),
            w,
            self.d(height),
            boxstyle=f"round,pad=0.012,rounding_size={rounding}",
            linewidth=lw,
            edgecolor=edge,
            facecolor=face,
            zorder=2,
        )
        self.ax.add_patch(patch)

    def text(
        self, x, top, s, fs=6.8, color=INK, ha="left", weight="normal", style="normal"
    ):
        self.ax.text(
            x,
            self.y(top),
            s,
            fontsize=fs,
            color=color,
            ha=ha,
            va="top",
            weight=weight,
            style=style,
            zorder=5,
        )

    def lines(self, x, top, items, fs=6.8, ha="left"):
        """Draw items (text[, colour[, weight[, style]]]) one per line; return the inch below."""
        defaults = ["", INK, "normal", "normal"]
        for item in items:
            if isinstance(item, str):
                item = (item,)
            s, color, weight, style = (list(item) + defaults[len(item) :])[:4]
            if s:
                self.text(
                    x, top, s, fs=fs, color=color, ha=ha, weight=weight, style=style
                )
            top += lh(fs)
        return top

    def arrow(self, x1, top1, x2, top2, color=OCHRE, lw=1.3):
        a = FancyArrowPatch(
            (x1, self.y(top1)),
            (x2, self.y(top2)),
            arrowstyle="-|>",
            mutation_scale=9,
            linewidth=lw,
            color=color,
            zorder=4,
        )
        self.ax.add_patch(a)

    def seg(self, xs, tops, color=INK, lw=0.8):
        self.ax.plot(
            xs,
            [self.y(t) for t in tops],
            color=color,
            linewidth=lw,
            zorder=1,
            solid_capstyle="butt",
        )

    def inset(self, cx, cy_top, width_in, height_in):
        """Equal-aspect inset axes centred at data-x cx and cy_top inches from the top."""
        left = (cx / 100.0 * W - width_in / 2) / W
        bottom = (self.h - cy_top - height_in / 2) / self.h
        ia = self.fig.add_axes([left, bottom, width_in / W, height_in / self.h])
        ia.set_aspect("equal")
        ia.axis("off")
        ia.patch.set_alpha(0)
        return ia

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / name
        self.fig.savefig(
            path, dpi=200, bbox_inches="tight", pad_inches=0.12, facecolor=PALE
        )
        plt.close(self.fig)
        return path


def yin_yang(ia, dark=TEAL, light=SAND, edge=INK):
    ia.add_patch(Wedge((0, 0), 1, 90, 270, facecolor=light, edgecolor="none"))
    ia.add_patch(Wedge((0, 0), 1, -90, 90, facecolor=dark, edgecolor="none"))
    ia.add_patch(Circle((0, 0.5), 0.5, facecolor=light, edgecolor="none"))
    ia.add_patch(Circle((0, -0.5), 0.5, facecolor=dark, edgecolor="none"))
    ia.add_patch(Circle((0, 0.5), 0.13, facecolor=dark, edgecolor="none"))
    ia.add_patch(Circle((0, -0.5), 0.13, facecolor=light, edgecolor="none"))
    ia.add_patch(Circle((0, 0), 1, facecolor="none", edgecolor=edge, linewidth=0.9))
    ia.set_xlim(-1.08, 1.08)
    ia.set_ylim(-1.08, 1.08)


def cube(ia, color=INK):
    """The Necker ('Wittgenstein') cube, as drawn on the speaker's chart."""
    s, dd = 1.0, 0.42
    front = [(0, 0), (s, 0), (s, s), (0, s), (0, 0)]
    back = [(x + dd, y + dd) for x, y in front]
    ia.plot(*zip(*front), color=color, linewidth=0.9)
    ia.plot(*zip(*back), color=color, linewidth=0.9)
    for (x1, y1), (x2, y2) in zip(front[:4], back[:4]):
        ia.plot([x1, x2], [y1, y2], color=color, linewidth=0.9)
    ia.set_xlim(-0.06, s + dd + 0.06)
    ia.set_ylim(-0.06, s + dd + 0.06)


# --------------------------------------------------------------------------- Figure 1
def fig1():
    c = Canvas(4.40)
    c.text(
        50,
        0.10,
        "Three criteria of validity, and where each one breaks",
        fs=12,
        ha="center",
        weight="bold",
    )
    c.text(
        50,
        0.36,
        "“In our tradition and in European philosophy too, there are three criteria”",
        fs=7,
        ha="center",
        color=GREY,
        style="italic",
    )

    c.box(2, 0.56, 96, 0.50, edge=GREY, face=PALE, lw=0.9)
    c.text(
        50,
        0.63,
        "Also in our tradition:  anadhigata-abādhitārthakaṁ jñānaṁ pramāṇam",
        fs=7.6,
        ha="center",
        color=TEAL,
        weight="bold",
    )
    c.text(
        50,
        0.84,
        "knowledge whose information is not obtained from another source, and is not “cancel-worthy”",
        fs=6.8,
        ha="center",
    )

    cols = [
        (
            "Correspondence",
            ["yathārthānubhavaḥ pramāṇam"],
            [
                "As the object is, so is the",
                "experience: the two fit each",
                "other “like hands and gloves”.",
            ],
            [
                "At the moment of experience we",
                "cannot check it. The eye only",
                "says “water”: the mirage. And",
                "the experience that cancels it",
                "must itself be checked: an",
                "infinite regress, anavasthā.",
            ],
        ),
        (
            "Coherence",
            ["jñāna-prāmāṇya-vādins"],
            [
                "One knowledge coheres with the",
                "next; if they are compatible,",
                "it is pramāṇa.",
            ],
            [
                "Friends and fans “pamper” my",
                "illusion. Satyajit Ray’s",
                "Mahāpuruṣ: a Svāmī “raises” the",
                "sun from the train window, and",
                "a kāpuruṣa is taken for a",
                "mahāpuruṣa.",
            ],
        ),
        (
            "Pragmatic, utilitarian",
            ["vyavahāra-avisaṁvādi-", "phala-janakaṁ jñānam"],
            [
                "Act on it and the result comes:",
                "water found, thirst quenched.",
                "The Buddha first; “very lately”",
                "the U.S.A.",
            ],
            [
                "In the long term the concord is",
                "an illusion: bait thrown to",
                "animals, the circus bear on a",
                "motorbike, grain under the net,",
                "medicine that becomes a disease.",
            ],
        ),
    ]
    top, height = 1.22, 2.06
    for (head, sub, body, breaks), x in zip(cols, (2, 34.5, 67)):
        w = 31
        c.box(x, top, w, height, edge=TEAL, face=SAND)
        c.text(
            x + w / 2, top + 0.08, head, fs=8.8, ha="center", color=TEAL, weight="bold"
        )
        c.lines(
            x + w / 2,
            top + 0.33,
            [(s, TEAL, "normal", "italic") for s in sub],
            fs=6.8,
            ha="center",
        )
        t = c.lines(x + 1.8, top + 0.33 + 2 * lh(6.8) + 0.05, body, fs=6.8)
        t += 0.06
        c.text(x + 1.8, t, "Where it breaks", fs=7.0, color=MAROON, weight="bold")
        c.lines(x + 1.8, t + lh(7.0) + 0.01, breaks, fs=6.8)

    c.box(2, 3.42, 96, 0.86, edge=OCHRE, face=SAND, lw=1.2)
    c.text(
        50,
        3.49,
        "None of these criteria is complete",
        fs=8.6,
        ha="center",
        color=OCHRE,
        weight="bold",
    )
    c.lines(
        50,
        3.74,
        [
            "So pramāṇa-samplava begins to look good; yet pride in being “rational” — more “rationality supply”",
            "than “blood supply” — makes man fashion a pramāṇa-vyavasthā and ask: which pramāṇa and which",
            "apramāṇa are svataḥ, self-valid, and which parataḥ, valid only through another?",
        ],
        fs=6.9,
        ha="center",
    )
    return c.save("fig1_three_theories.png")


# --------------------------------------------------------------------------- Figure 2
def node(
    c, cx, top, w, height, title, gloss=(), edge=TEAL, face=SAND, tfs=7.8, gfs=6.4
):
    c.box(cx - w / 2, top, w, height, edge=edge, face=face, lw=1.0, rounding=0.8)
    c.text(cx, top + 0.06, title, fs=tfs, ha="center", color=edge, weight="bold")
    c.lines(cx, top + 0.06 + lh(tfs) + 0.01, gloss, fs=gfs, ha="center")


def fig2():
    c = Canvas(5.46)
    c.text(
        50,
        0.10,
        "The speaker’s chart, and the four camps on svataḥ and parataḥ",
        fs=12,
        ha="center",
        weight="bold",
    )
    c.text(
        50,
        0.36,
        "Redrawn in IAST from the chart shared in the session, with glosses from the speaker’s own words",
        fs=6.9,
        ha="center",
        color=GREY,
        style="italic",
    )

    node(c, 50, 0.58, 46, 0.25, "jñāna-pramāṇa-śāstra (epistemology)", tfs=8.2)
    c.seg([50, 50], [0.83, 0.96])
    c.seg([20, 60], [0.96, 0.96])
    for x in (20, 60):
        c.seg([x, x], [0.96, 1.06])
    node(
        c,
        20,
        1.06,
        32,
        0.48,
        "pramāṇa-samplava",
        ["“chaos”: whatever is understood", "now counts as pramāṇa"],
    )
    node(
        c,
        60,
        1.06,
        34,
        0.48,
        "pramāṇa-vyavasthā",
        ["“organized”: which knowledge is", "pramāṇa for which object"],
    )
    # level 3: both nodes hang from vyavasthā, as drawn on the chart
    c.seg([60, 60], [1.54, 1.65])
    c.seg([32, 66], [1.65, 1.65])
    for x in (32, 66):
        c.seg([x, x], [1.65, 1.75])
    node(c, 32, 1.75, 27, 0.36, "anirdhārita-prāmāṇya", ["validity undetermined"])
    node(c, 66, 1.75, 27, 0.36, "prāmāṇya-nirdhārita", ["validity determined"])
    leaves = [
        (11, "prāmāṇya", ["validity"]),
        (30, "aprāmāṇya", ["invalidity"]),
        (50, "lakṣaṇa", ["definition"]),
        (69, "anubhūti", ["experience"]),
        (88, "adhyavasāya", ["(niścaya)", "certainty"]),
    ]
    c.seg([66, 66], [2.11, 2.22])
    c.seg([11, 88], [2.22, 2.22])
    for x, _, _ in leaves:
        c.seg([x, x], [2.22, 2.32])
    for x, t, g in leaves:
        node(c, x, 2.32, 17, 0.46, t, g, tfs=7.4)
    for x in (11, 30):
        c.seg([x, x], [2.78, 2.87])
        c.seg([x - 4.6, x + 4.6], [2.87, 2.87])
        for dx, lab in ((-4.6, "svataḥ"), (4.6, "parataḥ")):
            c.seg([x + dx, x + dx], [2.87, 2.94])
            c.box(
                x + dx - 4.3,
                2.94,
                8.6,
                0.21,
                edge=TEAL,
                face=PALE,
                lw=0.8,
                rounding=0.5,
            )
            c.text(x + dx, 3.003, lab, fs=6.4, ha="center", color=TEAL, weight="bold")
    c.lines(
        42,
        2.90,
        [
            "svataḥ: “self valid”",
            "parataḥ: “validity” only “through” something else",
        ],
        fs=6.6,
    )

    c.seg([2, 98], [3.30, 3.30], color=GREY, lw=0.6)
    c.text(
        2,
        3.38,
        "The four camps, as the speaker lays them out",
        fs=8.6,
        color=TEAL,
        weight="bold",
    )
    gx, gw = 18.5, 22.0
    row_tops, row_h = (3.92, 4.48), 0.50
    c.text(
        gx + gw / 2,
        3.72,
        "aprāmāṇya svataḥ",
        fs=6.9,
        ha="center",
        color=TEAL,
        weight="bold",
    )
    c.text(
        gx + gw * 1.5 + 1.0,
        3.72,
        "aprāmāṇya parataḥ",
        fs=6.9,
        ha="center",
        color=TEAL,
        weight="bold",
    )
    for rt, lab in zip(row_tops, ("svataḥ", "parataḥ")):
        c.lines(
            9.2,
            rt + row_h / 2 - lh(6.9),
            [("prāmāṇya", TEAL, "bold"), (lab, TEAL, "bold")],
            fs=6.9,
            ha="center",
        )
    cells = [
        (0, 0, ["a “middle” vyavasthā:", "both svataḥ"]),
        (1, 0, ["the “constitution” of", "Vedānta current before", "Mahāprabhuji"]),
        (
            0,
            1,
            [
                "the Buddha: “by itself no",
                "understanding is valid”;",
                "invalidity is self-evident",
            ],
        ),
        (1, 1, ["both parataḥ"]),
    ]
    for col, row, body in cells:
        x = gx + col * (gw + 1.0)
        rt = row_tops[row]
        c.box(x, rt, gw, row_h, edge=TEAL, face=SAND, lw=0.9)
        n = len(body)
        c.lines(
            x + gw / 2, rt + (row_h - n * lh(6.6)) / 2 + 0.01, body, fs=6.6, ha="center"
        )

    mx, mw = 66.5, 31.5
    c.box(mx, 3.64, mw, 1.34, edge=MAROON, face=SAND, lw=1.6)
    c.text(
        mx + mw / 2,
        3.70,
        "Vallabha Vedānta",
        fs=8.6,
        ha="center",
        color=MAROON,
        weight="bold",
    )
    t = c.lines(
        mx + 1.8,
        3.93,
        [
            "takes none of the four as the",
            "criterion: an ardhajaratī,",
            "“half old, half young” —",
            "pramāṇa-samplava admitted,",
            "a vyavasthā only ad hoc.",
        ],
        fs=6.7,
    )
    c.lines(
        mx + 1.8,
        t + 0.05,
        [
            ("“In every chaos there is", MAROON, "normal", "italic"),
            ("cosmos, and in every", MAROON, "normal", "italic"),
            ("cosmos, chaos.”", MAROON, "normal", "italic"),
        ],
        fs=6.7,
    )
    yin_yang(c.inset(93.6, t + 0.05 + 1.5 * lh(6.7), 0.36, 0.36))

    c.lines(
        2,
        5.10,
        [
            (
                "The chart also shows the Wittgenstein cube (Figure 4) and the yin-yang image. The “middle” camp is named in the",
                GREY,
                "normal",
                "italic",
            ),
            (
                "text only conjecturally (‹Sāṅkhya›); the fourth camp is not named by the speaker.",
                GREY,
                "normal",
                "italic",
            ),
        ],
        fs=6.4,
    )
    return c.save("fig2_chart_four_camps.png")


# --------------------------------------------------------------------------- Figure 3
def fig3():
    c = Canvas(5.10)
    c.text(
        50,
        0.10,
        "Substance-cum-creator: why Brahman cannot be predicted",
        fs=12,
        ha="center",
        weight="bold",
    )
    cols = [
        (
            "Abrahamic God",
            TEAL,
            ["only a “creator”;", "not the “substance”", "of the “world”"],
        ),
        (
            "Śaṅkara’s Brahman",
            TEAL,
            [
                "not “substance”, but at",
                "least the “substratum”,",
                "ādhāra: the rope under",
                "the snake-illusion",
            ],
        ),
        (
            "Mahāprabhuji’s Brahman",
            MAROON,
            [
                "“substance-cum-creator”",
                "",
                "upādāna: saccidānanda, the",
                "“infinite conscious being”",
                "(substantial definition)",
                "",
                "kartā: kartum akartum",
                "anyathā kartuṁ samarthaḥ",
                "(functional definition)",
            ],
        ),
    ]
    top, height = 0.42, 1.52
    for (head, col, body), x in zip(cols, (2, 34.5, 67)):
        w = 31
        c.box(x, top, w, height, edge=col, face=SAND, lw=1.6 if col == MAROON else 1.0)
        c.text(
            x + w / 2, top + 0.08, head, fs=8.6, ha="center", color=col, weight="bold"
        )
        c.lines(x + w / 2, top + 0.34, body, fs=6.7, ha="center")
    c.arrow(82.5, 1.96, 82.5, 2.20)
    c.box(2, 2.22, 96, 0.48, edge=OCHRE, face=PALE, lw=1.1)
    c.text(
        50,
        2.28,
        "Therefore the world is līlā — “unplanned action”",
        fs=8.4,
        ha="center",
        color=OCHRE,
        weight="bold",
    )
    c.text(
        50,
        2.50,
        "“ko addhā veda … so aṅga veda yadi vā na veda”: who can know? even its overseer may not know (Ṛgveda 10.129)",
        fs=6.5,
        ha="center",
        style="italic",
    )

    btop, bh = 2.86, 2.10
    c.box(2, btop, 55, bh, edge=TEAL, face=SAND)
    c.text(
        29.5,
        btop + 0.08,
        "Predictability comes from a single sāmarthya",
        fs=8.0,
        ha="center",
        color=TEAL,
        weight="bold",
    )
    items = [
        (
            "kartum only",
            TEAL,
            ["H and O must make water; they", "cannot choose to become gold"],
        ),
        (
            "anyathā kartum only",
            TEAL,
            [
                "Mr. Bean; the monkey through the open",
                "window; the rats: predictably unpredictable",
            ],
        ),
        (
            "a limited sāmarthya",
            TEAL,
            ["politics, hospital, college, religion,", "family: predictable"],
        ),
        (
            "Brahman: all three",
            MAROON,
            ["kartum, akartum, anyathā kartum:", "not predictable"],
        ),
    ]
    t = btop + 0.36
    for lead, col, body in items:
        c.text(4.0, t, lead, fs=6.8, color=col, weight="bold")
        t = c.lines(6.0, t + lh(6.8), body, fs=6.6) + 0.07

    c.box(59, btop, 39, bh, edge=TEAL, face=PALE, lw=1.0)
    ia = c.inset(78.5, btop + 0.70, 1.22, 1.22)
    ia.add_patch(Circle((0, 0), 1.0, facecolor=SAND, edgecolor=TEAL, linewidth=1.2))
    ia.add_patch(
        Circle((0.30, -0.40), 0.50, facecolor=PALE, edgecolor=OCHRE, linewidth=1.1)
    )
    ia.text(
        0,
        0.62,
        "brahmatva:",
        fontsize=6.8,
        ha="center",
        va="center",
        color=TEAL,
        weight="bold",
    )
    ia.text(
        0,
        0.42,
        "the major circle of",
        fontsize=6.4,
        ha="center",
        va="center",
        color=INK,
    )
    ia.text(
        0, 0.25, "unpredictability", fontsize=6.4, ha="center", va="center", color=INK
    )
    ia.text(
        0.30,
        -0.32,
        "creation:",
        fontsize=6.4,
        ha="center",
        va="center",
        color=OCHRE,
        weight="bold",
    )
    ia.text(0.30, -0.52, "ad hoc", fontsize=6.4, ha="center", va="center", color=INK)
    ia.set_xlim(-1.05, 1.05)
    ia.set_ylim(-1.05, 1.05)
    c.lines(
        78.5,
        btop + 1.40,
        [
            "“In yin-yang fashion”: inside the",
            "major circle some predictability",
            "has come — “ad hoc”.",
            ("Absolute certainty is not possible.", MAROON, "bold"),
        ],
        fs=6.5,
        ha="center",
    )
    return c.save("fig3_brahman_unpredictable.png")


# --------------------------------------------------------------------------- Figure 4
def fig4():
    c = Canvas(5.18)
    c.text(
        50,
        0.10,
        "Mahāprabhuji’s ad hoc vyavasthā: which criterion, where",
        fs=12,
        ha="center",
        weight="bold",
    )
    c.text(
        50,
        0.36,
        "“We will not take any one criterion as complete” — so that every possibility of Brahman is “topped up”",
        fs=6.9,
        ha="center",
        color=GREY,
        style="italic",
    )
    rows = [
        (
            0.58,
            0.72,
            "Verification possible",
            [
                "empirical concepts of “day to day life”:",
                "the plastic rose — see it, smell it, touch it;",
                "the ventriloquist’s puppet",
            ],
            ["yathārthānubhava"],
            ["correspondence: the experience", "is true “according to the object”"],
        ),
        (
            1.42,
            0.72,
            "Verification not possible",
            [
                "infinity, existence, consciousness;",
                "the nuclear structure, disturbed when",
                "observed, “like the old pardā-nashīn women”",
            ],
            ["anadhigata-abādhitārtha-", "viṣayaka jñāna"],
            ["and the “coherence” of one", "knowledge with the next"],
        ),
        (
            2.26,
            0.96,
            "Fluctuating phenomena",
            [
                "Wittgenstein’s cube; the chameleon;",
                "brahmatva: “yad-yad-dhiyā …",
                "tat-tad-vapuḥ” (Bhāg. 3.9.11);",
                "Kṛṣṇa entering the arena,",
                "seen differently by each (10.43.17)",
            ],
            ["phala-avisaṁvādī jñāna"],
            [
                "wrestling with you, he is a",
                "wrestler; behaving as an innocent",
                "child, he is an innocent child",
            ],
        ),
        (
            3.34,
            0.72,
            "Verbal concepts",
            [
                "infinity, mathematical or astronomical;",
                "the Betāl Pacchīsī, the Arabian Nights;",
                "Brahman",
            ],
            ["śabda alone"],
            ["for Brahman: not pratyakṣa,", "not anumāna"],
        ),
    ]
    for top, height, head, body, chead, cbody in rows:
        c.box(2, top, 50, height, edge=TEAL, face=SAND)
        c.text(4.0, top + 0.07, head, fs=8.2, color=TEAL, weight="bold")
        c.lines(4.0, top + 0.07 + lh(8.2) + 0.02, body, fs=6.7)
        c.box(58, top, 40, height, edge=MAROON, face=SAND, lw=1.5)
        n_lines = len(chead) * lh(7.9) + len(cbody) * lh(6.7) + 0.03
        t = top + (height - n_lines) / 2
        t = c.lines(78, t, [(s, MAROON, "bold") for s in chead], fs=7.9, ha="center")
        c.lines(78, t + 0.03, cbody, fs=6.7, ha="center")
        mid = top + height / 2
        c.arrow(52.6, mid, 57.4, mid)
    cube(c.inset(45.3, 2.26 + 0.60, 0.58, 0.58))

    c.box(2, 4.20, 96, 0.84, edge=MAROON, face=SAND, lw=1.6)
    c.text(
        50,
        4.27,
        "Mahāprabhuji’s position",
        fs=8.6,
        ha="center",
        color=MAROON,
        weight="bold",
    )
    c.lines(
        50,
        4.50,
        [
            "Under the pressure of līlāvāda, pramāṇa-samplava is admitted and a vyavasthā is made only ad hoc.",
            "Pratyakṣa and anumāna remain pramāṇa — even hearing or reading the Veda is “empirical” —",
            "but about Brahman, a “verbal concept”, śabda alone is pramāṇa.",
        ],
        fs=6.9,
        ha="center",
    )
    return c.save("fig4_adhoc_vyavastha.png")


def contact_sheet(paths):
    ims = [Image.open(p).convert("RGB") for p in paths]
    width = max(im.width for im in ims)
    height = sum(im.height for im in ims) + 40 * (len(ims) - 1)
    sheet = Image.new("RGB", (width, height), "white")
    top = 0
    for im in ims:
        sheet.paste(im, (0, top))
        top += im.height + 40
    sheet.thumbnail((1600, 99999))
    SHEET_DIR.mkdir(parents=True, exist_ok=True)
    out = SHEET_DIR / "contact_part1.png"
    sheet.save(out)
    return out


if __name__ == "__main__":
    made = [fig1(), fig2(), fig3(), fig4()]
    for p in made:
        print(p.name, Image.open(p).size)
    print(contact_sheet(made))
