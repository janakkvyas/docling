#!/usr/bin/env python3
"""Figures 5-8 for Lecture 5, Part 2 (Śāstrārtha Prakaraṇa, session of 2026-08-08).

Layout is computed top-down in points, with line breaks found by measuring the
rendered width of each word, so every box is sized to its text. The canvas is
then sized to the content and mapped onto axes running 0-100 both ways.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch
from matplotlib.textpath import TextPath

plt.rcParams["font.family"] = "DejaVu Sans"

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"

OUT = Path(__file__).resolve().parent / "figs05"
OUT.mkdir(exist_ok=True)

WIDTH_IN = 6.2
W_PT = WIDTH_IN * 72
U = W_PT / 100  # points per x-unit
LS = 1.32  # line spacing factor
MS = 45  # mutation scale: pad = 0.012 * MS units
BODY = 6.8
HEAD = 8.5
PADT = 6.0  # top/bottom inner padding of a card, points
MX = 7.0  # left/right inner margin of a card, points
GAP = 2.5  # gap between paragraphs, points


# --------------------------------------------------------------------------- text
_cache = {}


def text_width(s, size, weight="normal", style="normal"):
    key = (s, size, weight, style)
    if key not in _cache:
        if not s.strip():
            _cache[key] = 0.0
        else:
            fp = FontProperties(
                family="DejaVu Sans", weight=weight, style=style, size=size
            )
            _cache[key] = TextPath((0, 0), s, size=size, prop=fp).get_extents().width
    return _cache[key]


SAFETY = 5.0  # points held back from every measured line width


def wrap(s, size, maxw, weight="normal", style="normal"):
    """Greedy word wrap on measured widths; a word too long for the line is split at hyphens."""
    maxw -= SAFETY
    lines = []
    for seg in s.split("\n"):
        tokens = []  # (text, preceded_by_space)
        for word in seg.split(" "):
            if "-" in word and text_width(word, size, weight, style) > maxw:
                parts = word.split("-")
                for i, part in enumerate(parts):
                    tokens.append((part + ("-" if i < len(parts) - 1 else ""), i == 0))
            else:
                tokens.append((word, True))
        cur = ""
        for tok, spaced in tokens:
            trial = cur + (" " if cur and spaced else "") + tok
            if not cur or text_width(trial, size, weight, style) <= maxw:
                cur = trial
            else:
                lines.append(cur)
                cur = tok
        lines.append(cur)
    return lines


def layout(paras, maxw):
    """paras: list of (text, style[, color[, size]]); style uses b / i / n."""
    out = []
    for p in paras:
        text, st = p[0], p[1]
        color = p[2] if len(p) > 2 and p[2] else INK
        size = p[3] if len(p) > 3 and p[3] else BODY
        weight = "bold" if "b" in st else "normal"
        fstyle = "italic" if "i" in st else "normal"
        for ln in wrap(text, size, maxw, weight, fstyle):
            out.append((ln, weight, fstyle, color, size))
        out.append(None)  # paragraph gap
    if out and out[-1] is None:
        out.pop()
    return out


def height(lines):
    return sum(GAP if ln is None else ln[4] * LS for ln in lines)


# --------------------------------------------------------------------------- figure
class Fig:
    def __init__(self):
        self.cmds = []
        self.cur = 8.0

    def add(self, *cmd):
        self.cmds.append(cmd)

    def lines(self, x, top, lines, ha="left"):
        y = top
        for ln in lines:
            if ln is None:
                y += GAP
                continue
            s, weight, fstyle, color, size = ln
            self.add(
                "text",
                x,
                y,
                s,
                dict(size=size, weight=weight, style=fstyle, color=color, ha=ha),
            )
            y += size * LS
        return y

    def title(self, text, sub=None):
        self.add(
            "text",
            50,
            self.cur,
            text,
            dict(size=12, weight="bold", color=INK, ha="center"),
        )
        self.cur += 18
        if sub:
            sl = layout([(sub, "i", GREY, 7.2)], 90 * U)
            self.cur = self.lines(50, self.cur, sl, ha="center")
        self.cur += 10

    def card(
        self,
        x,
        top,
        w,
        header=None,
        paras=None,
        ec=TEAL,
        fc=SAND,
        lw=1.0,
        hsize=HEAD,
        hcolor=None,
        align="left",
        fixed_h=None,
        draw=True,
    ):
        maxw = w * U - 2 * MX
        hl = layout([(header, "b", hcolor or ec, hsize)], maxw) if header else []
        bl = layout(paras, maxw) if paras else []
        h = PADT + height(hl) + (3 if hl and bl else 0) + height(bl) + PADT
        if fixed_h:
            h = max(h, fixed_h)
        if draw:
            self.add("box", x, top, w, h, ec, fc, lw)
            y = self.lines(x + w / 2, top + PADT, hl, ha="center")
            if hl and bl:
                y += 3
            if align == "left":
                self.lines(x + MX / U, y, bl, ha="left")
            else:
                self.lines(x + w / 2, y, bl, ha="center")
        return h

    def banner(self, text, ec=OCHRE, size=7.0):
        h = self.card(
            2,
            self.cur,
            96,
            paras=[(text, "n", INK, size)],
            ec=ec,
            fc=SAND,
            lw=1.1,
            align="center",
        )
        self.cur += h
        return h

    def aside(self, text, size=6.8):
        al = layout([(text, "i", GREY, size)], 88 * U)
        self.cur = self.lines(50, self.cur, al, ha="center")

    def arrow(self, x1, y1, x2, y2, color=OCHRE, lw=1.3):
        self.add("arrow", x1, y1, x2, y2, color, lw)

    def ellipse(self, cx, cy, d, ec, fc, lw):
        self.add("ellipse", cx, cy, d, ec, fc, lw)

    def render(self, name, bottom=6.0):
        total = self.cur + bottom
        fig = plt.figure(figsize=(WIDTH_IN, total / 72), dpi=200)
        fig.patch.set_facecolor(PALE)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")
        ax.set_facecolor(PALE)

        def Y(pt):
            return 100 * (1 - pt / total)

        aspect = W_PT / total
        for cmd in self.cmds:
            kind = cmd[0]
            if kind == "text":
                _, x, y, s, kw = cmd
                kw = {"va": "top", **kw}
                ax.text(x, Y(y), s, **kw)
            elif kind == "box":
                _, x, top, w, h, ec, fc, lw = cmd
                ax.add_patch(
                    FancyBboxPatch(
                        (x, Y(top + h)),
                        w,
                        h * 100 / total,
                        boxstyle="round,pad=0.012",
                        mutation_scale=MS,
                        mutation_aspect=aspect,
                        ec=ec,
                        fc=fc,
                        lw=lw,
                    )
                )
            elif kind == "arrow":
                _, x1, y1, x2, y2, color, lw = cmd
                ax.add_patch(
                    FancyArrowPatch(
                        (x1, Y(y1)),
                        (x2, Y(y2)),
                        arrowstyle="-|>",
                        mutation_scale=9,
                        color=color,
                        lw=lw,
                        shrinkA=0,
                        shrinkB=0,
                    )
                )
            elif kind == "ellipse":
                _, cx, cy, d, ec, fc, lw = cmd
                ax.add_patch(
                    Ellipse((cx, Y(cy)), d / U, d * 100 / total, ec=ec, fc=fc, lw=lw)
                )
        path = OUT / name
        fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.12, facecolor=PALE)
        plt.close(fig)
        print("wrote", path.name, f"{WIDTH_IN:.1f} x {total / 72:.2f} in")


# --------------------------------------------------------------------------- Figure 5
def fig5():
    F = Fig()
    F.title(
        "Pramāṇa-vyavasthā: what each one divides",
        "after the speaker's chart: Buddha and Śaṅkara grade truth, Mahāprabhuji the time "
        "of the knower",
    )
    cols = [
        dict(
            x=2,
            w=28,
            ec=TEAL,
            lw=1.1,
            head="Buddha · two satyas",
            sub="divides truth itself",
            cards=[
                (
                    "saṁvṛti-satya",
                    "lokasaṁvṛti: the truth of the world, without which "
                    "its dealings do not run (vyāvahārika)",
                ),
                (
                    "paramārtha-satya",
                    "what the world does not accept, yet is; truth cannot be spoken",
                ),
                (
                    "truth has grades",
                    "full, half, quarter, three-quarter, and so for "
                    "untruth: Yudhiṣṭhira's aśvatthāmā hato naro vā kuñjaro vā",
                    GREY,
                ),
            ],
            aside="Method: to 'all is' he answers 'nothing is'; to 'nothing is', "
            "'something is'.",
        ),
        dict(
            x=33,
            w=28,
            ec=TEAL,
            lw=1.1,
            head="Śaṅkara · three satyas",
            sub="divides truth, inspired by Buddha",
            cards=[
                (
                    "prātibhāsika",
                    "what appears in deśa-kāla: the mirage seen from "
                    "afar, gone at the spot",
                ),
                (
                    "vyāvahārika",
                    "the truth beyond the framework of deśa-kāla, "
                    "as the speaker puts it",
                ),
                ("pāramārthika", "avācya: as with Buddha, it cannot be spoken"),
            ],
            aside="Not pramāṇa-saṁplava but pramāṇa-vyavasthā: a separate truth "
            "for each level.",
        ),
        dict(
            x=64,
            w=34,
            ec=MAROON,
            lw=1.8,
            head="Mahāprabhuji · four kālas",
            sub="divides the time of the knower; the prameya, Hari, stays one",
            cards=[
                ("1  upadeśa-kāla", "first instruction: pramāṇaṁ tac catuṣṭayam"),
                (
                    "2  upadiṣṭa-adhyavasāya-kāla",
                    "determining what was taught: one "
                    "meaning in all śāstra (kārikā 104)",
                ),
                (
                    "3  avyavasthita anubhava (sākṣātkāra) kāla",
                    "experience: everything is Brahman",
                ),
                (
                    "4  līlāvatāra-kāla",
                    "Bhagavān follows each bhāvanā and makes it true",
                ),
            ],
            aside="No difference of truth from kāla to kāla.",
        ),
    ]
    top = F.cur

    def column(c, draw, fixed=None):
        x, ec, W = c["x"], c["ec"], c["w"]
        y = top + 8
        hl = layout([(c["head"], "b", ec, 8.0)], W * U - 2 * MX)
        sl = layout([(c["sub"], "i", GREY, 6.8)], W * U - 2 * MX)
        if draw:
            F.add("box", x, top, W, fixed, ec, PALE, c["lw"])
            F.lines(x + W / 2, y, hl, ha="center")
            F.lines(x + W / 2, y + height(hl) + 2, sl, ha="center")
        y += height(hl) + 2 + height(sl) + 8
        for item in c["cards"]:
            lab, body = item[0], item[1]
            cec = item[2] if len(item) > 2 else ec
            h = F.card(
                x + 2,
                y,
                W - 4,
                header=lab,
                paras=[(body, "n")],
                ec=cec,
                hsize=7.4,
                hcolor=ec,
                draw=draw,
            )
            y += h + 6
        al = layout([(c["aside"], "i", GREY, 6.6)], (W - 4) * U)
        if draw:
            F.lines(x + W / 2, y + 2, al, ha="center")
        y += 2 + height(al) + 8
        return y - top

    hmax = max(column(c, False) for c in cols)
    for c in cols:
        column(c, True, hmax)
    F.cur = top + hmax + 12
    F.banner(
        "Buddha's teaching rests on two satyas and Śaṅkara's on three; Mahāprabhuji's "
        "upadeśa is divided into four kālas with no difference of truth between them. "
        "'Four pramāṇas' is the rule of the first kāla, not a narrow canon."
    )
    F.render("fig5_pramana_vyavastha.png")


# --------------------------------------------------------------------------- Figure 6
def fig6():
    F = Fig()
    F.title(
        "The four kālas: the circle of pramāṇa widens",
        "one prameya, Hari, throughout; the kāla changes what the knower can take as pramāṇa",
    )
    xs = dict(lab=(2, 23), pra=(27, 35), ill=(64, 34))
    F.add(
        "text",
        xs["lab"][0] + xs["lab"][1] / 2,
        F.cur,
        "kāla",
        dict(size=7.4, weight="bold", color=TEAL, ha="center"),
    )
    F.add(
        "text",
        xs["pra"][0] + xs["pra"][1] / 2,
        F.cur,
        "what counts as pramāṇa",
        dict(size=7.4, weight="bold", color=TEAL, ha="center"),
    )
    F.add(
        "text",
        xs["ill"][0] + xs["ill"][1] / 2,
        F.cur,
        "the speaker's illustrations",
        dict(size=7.4, weight="bold", color=TEAL, ha="center"),
    )
    F.cur += 16
    rows = [
        (
            "1 · upadeśa-kāla",
            "ādya-uccāraṇa, the first teaching",
            [
                (
                    "The four as one unit: Veda, Gītā, Brahmasūtra, Bhāgavata "
                    "(pramāṇaṁ tac catuṣṭayam).",
                    "n",
                ),
                (
                    "Manu and the rest only where they do not contradict; partly agreeing, "
                    "partly not: apramāṇa.",
                    "n",
                ),
            ],
            [
                (
                    "'ka for kamal', not yet kājal; A for Apple, B for Bat, C for Cat.",
                    "n",
                ),
                ("The medical student's textbook.", "n"),
            ],
        ),
        (
            "2 · upadiṣṭa-adhyavasāya-kāla",
            "determining what was taught",
            [
                ("All śāstra, read for the one meaning:", "n"),
                ("artho 'yam eva nikhilair api vedavākyaiḥ (kārikā 104)", "i", MAROON),
                ("Still śāstric: śābdika anubhava.", "n"),
            ],
            [
                ("kamal, kājal, kapūr, kānan: additions without cancellation.", "n"),
                ("The internship, where the symptoms are shown.", "n"),
            ],
        ),
        (
            "3 · avyavasthita anubhava (sākṣātkāra) kāla",
            "tāttvika anubhava",
            [
                (
                    "Everything is Brahman; the opposite of the tattva is a variety of the "
                    "tattva. Contradictions are experienced, not argued away.",
                    "n",
                )
            ],
            [
                (
                    "aṇv api brahma vyāpakam: Kṛṣṇa in Yaśodā's lap supports the cosmos.",
                    "n",
                ),
                ("A = B, B = C, so A = C; deva and rākṣasa both Brahman.", "n"),
                ("The doctor in practice.", "n"),
            ],
        ),
        (
            "4 · līlāvatāra-kāla",
            "Bhagavān follows your bhāvanā",
            [
                ("Every notion, true or false, is justified by Bhagavān:", "n"),
                (
                    "satyaṁ cānṛtaṁ ca satyam abhavat (Taittirīya Up. 2.6.1)",
                    "i",
                    MAROON,
                ),
                ("No gauṇārtha can falsify sad asac cāham (Gītā 9.19).", "n"),
            ],
            [
                ("The nucleus disturbed by being observed.", "n"),
                ("Raṇchoḍrāy seen as hero or as runaway.", "n"),
                ("Death to Karṇa; giver of life to Vasudeva and Devakī.", "n"),
            ],
        ),
    ]
    links = [
        "once the upadeśa is understood",
        "when the tattva itself is experienced",
        "where Bhagavān descends in līlā",
    ]
    for i, (lab, sub, pra, ill) in enumerate(rows):
        top = F.cur
        hl = F.card(
            xs["lab"][0],
            top,
            xs["lab"][1],
            header=lab,
            paras=[(sub, "i", GREY)],
            ec=MAROON,
            lw=1.6,
            hsize=7.6,
            draw=False,
            align="center",
        )
        hp = F.card(
            xs["pra"][0], top, xs["pra"][1], paras=pra, ec=TEAL, fc=PALE, draw=False
        )
        hi = F.card(
            xs["ill"][0], top, xs["ill"][1], paras=ill, ec=TEAL, fc=PALE, draw=False
        )
        h = max(hl, hp, hi)
        F.card(
            xs["lab"][0],
            top,
            xs["lab"][1],
            header=lab,
            paras=[(sub, "i", GREY)],
            ec=MAROON,
            lw=1.6,
            hsize=7.6,
            fixed_h=h,
            align="center",
        )
        F.card(xs["pra"][0], top, xs["pra"][1], paras=pra, ec=TEAL, fc=PALE, fixed_h=h)
        F.card(xs["ill"][0], top, xs["ill"][1], paras=ill, ec=TEAL, fc=PALE, fixed_h=h)
        F.cur = top + h
        if i < len(rows) - 1:
            cx = xs["lab"][0] + xs["lab"][1] / 2
            F.arrow(cx, F.cur + 3, cx, F.cur + 17)
            F.add(
                "text",
                cx + 2.2,
                F.cur + 5.5,
                links[i],
                dict(size=6.6, style="italic", color=OCHRE, ha="left"),
            )
            F.cur += 20
    F.cur += 12
    F.banner(
        "'For the beginners' the rule is four. Each later kāla widens access to the one "
        "prameya, Hari, without introducing a difference of truth."
    )
    F.render("fig6_four_kalas.png")


# --------------------------------------------------------------------------- Figure 7
def fig7():
    F = Fig()
    F.title(
        "Anvaya-vyatireka: logical and factual",
        "after the speaker's chart: which form does janmādy asya yataḥ intend?",
    )
    top = F.cur
    LX, RX, PW = 2, 52, 46
    D_OUT, D_IN = 96, 40

    def left(draw, fixed=None):
        if draw:
            F.add("box", LX, top, PW, fixed, TEAL, PALE, 1.1)
            F.add(
                "text",
                LX + PW / 2,
                top + 8,
                "Logical",
                dict(size=HEAD, weight="bold", color=TEAL, ha="center"),
            )
        y = top + 8 + HEAD * LS + 8
        for head, body in [
            ("tat-sattve tat-sattvam", "when this is, that is"),
            ("tad-abhāve tad-abhāvaḥ", "when this is absent, that is absent"),
        ]:
            y += (
                F.card(
                    LX + 3,
                    y,
                    PW - 6,
                    header=head,
                    paras=[(body, "n")],
                    ec=TEAL,
                    hsize=7.4,
                    draw=draw,
                )
                + 6
            )
        ex = layout(
            [
                (
                    "Example: if there is daylight, there is light; if no light, "
                    "no daylight.",
                    "i",
                    GREY,
                )
            ],
            (PW - 6) * U,
        )
        if draw:
            F.lines(LX + PW / 2, y + 2, ex, ha="center")
        y += 2 + height(ex) + 8
        y += (
            F.card(
                LX + 3,
                y,
                PW - 6,
                header="Applied to Brahman?",
                paras=[
                    (
                        "It would need brahmābhāve jagad-abhāvaḥ. But absolute being has "
                        "no absence:",
                        "n",
                    ),
                    (
                        "nāsato vidyate bhāvo nābhāvo vidyate sataḥ (Gītā 2.16)",
                        "i",
                        TEAL,
                    ),
                    ("Only temporal being can be bhāva or abhāva.", "n"),
                ],
                ec=GREY,
                hsize=7.4,
                hcolor=TEAL,
                draw=draw,
            )
            + 8
        )
        return y - top

    def right(draw, fixed=None):
        if draw:
            F.add("box", RX, top, PW, fixed, MAROON, PALE, 1.8)
            F.add(
                "text",
                RX + PW / 2,
                top + 8,
                "Factual",
                dict(size=HEAD, weight="bold", color=MAROON, ha="center"),
            )
        y = top + 8 + HEAD * LS + 8
        cx = RX + 16
        cy = y + D_OUT / 2
        if draw:
            F.ellipse(cx, cy, D_OUT, MAROON, SAND, 1.3)
            F.ellipse(cx, cy + 10, D_IN, MAROON, PALE, 1.3)
            F.add(
                "text",
                cx,
                cy - D_OUT / 2 + 9,
                "V",
                dict(size=9, weight="bold", color=MAROON, ha="center"),
            )
            F.add(
                "text",
                cx,
                cy + 10 - 5,
                "A",
                dict(size=9, weight="bold", color=MAROON, ha="center", va="center"),
            )
            ax_end = RX + 33
            F.arrow(cx + 3.0, cy - D_OUT / 2 + 15, ax_end, cy - D_OUT / 2 + 15)
            F.add(
                "text",
                ax_end + 1.0,
                cy - D_OUT / 2 + 15,
                "vyatireka",
                dict(size=7.2, weight="bold", color=MAROON, ha="left", va="center"),
            )
            F.arrow(cx + D_IN / 2 / U, cy + 10, ax_end, cy + 10)
            F.add(
                "text",
                ax_end + 1.0,
                cy + 10,
                "anvaya",
                dict(size=7.2, weight="bold", color=MAROON, ha="left", va="center"),
            )
        y += D_OUT + 10
        paras = [
            (
                "A · anvaya: Brahman wherever the world is born, stays, goes and "
                "dissolves.",
                "n",
            ),
            (
                "V · vyatireka: Brahman beyond that too. No tad-abhāva anywhere: where "
                "there is anvaya there is vyatireka, and where vyatireka, anvaya.",
                "n",
            ),
            (
                "The six that clears the boundary: inside, and outside too, "
                "not imprisoned in it.",
                "i",
                GREY,
            ),
            ("janmādy asya yato 'nvayād itarataś ca (Bhāgavata 1.1.1)", "i", MAROON),
        ]
        bl = layout(paras, (PW - 6) * U)
        if draw:
            F.lines(RX + 3, y, bl)
        y += height(bl) + 10
        return y - top

    h = max(left(False), right(False))
    left(True, h)
    right(True, h)
    F.cur = top + h + 10
    F.aside(
        "Śaṅkara: Brahman is neither cause nor effect; birth, stay and dissolution appear "
        "through sad-asad-anirvacanīya māyā, as the snake on the rope. 'There, there is "
        "brahma-abhāva.'"
    )
    F.cur += 10
    F.banner(
        "The uttara removes the pūrva's doubt: the sūtra leaves open which "
        "anvaya-vyatireka is meant; the Bhāgavata settles it as factual, because "
        "absolute being has no absence."
    )
    F.render("fig7_anvaya_vyatireka.png")


# --------------------------------------------------------------------------- Figure 8
def fig8():
    F = Fig()
    F.title(
        "Kārikās 8–9 with the Prakāśa",
        "each later text removes the doubt left by the earlier; after full knowledge, "
        "all speech is pramāṇa",
    )
    names = ["Veda", "Gītā", "Brahmasūtra", "Bhāgavata"]
    bw, gap = 19.5, 6.0
    top = F.cur
    hb = 24.0
    for i, n in enumerate(names):
        x = 2 + i * (bw + gap)
        F.add("box", x, top, bw, hb, MAROON, SAND, 1.4)
        F.add(
            "text",
            x + bw / 2,
            top + hb / 2,
            n,
            dict(size=HEAD, weight="bold", color=MAROON, ha="center", va="center"),
        )
        if i < 3:
            F.arrow(x + bw + 1.2, top + hb / 2, x + bw + gap - 1.2, top + hb / 2)
    F.cur = top + hb + 12
    cards = [
        (
            "Veda → Gītā",
            [
                ("Doubt", "b", TEAL),
                (
                    "apāṇipādo javano grahītā (Śvetāśvatara 3.19): are only prākṛta hands and "
                    "feet denied, or all?",
                    "n",
                ),
                ("Decided by", "b", TEAL),
                (
                    "sarvataḥ pāṇipādaṁ tat (Gītā 13.13): hands and feet everywhere, "
                    "not confined to one place.",
                    "n",
                ),
            ],
        ),
        (
            "Gītā → Brahmasūtra",
            [
                ("Doubt", "b", TEAL),
                (
                    "nityaḥ sarvagataḥ sthāṇuḥ (2.24) against mamaivāṁśo jīvaloke (15.7).",
                    "n",
                ),
                ("Decided by", "b", TEAL),
                (
                    "utkrānti-gaty-āgatīnām (BS 2.3.19): the jīva goes out, goes and comes, so "
                    "the vyaṣṭi is aṁśa; the samaṣṭi is all-pervading.",
                    "n",
                ),
            ],
        ),
        (
            "Brahmasūtra → Bhāgavata",
            [
                ("Doubt", "b", TEAL),
                (
                    "janmādy asya yataḥ (BS 1.1.2): which anvaya-vyatireka, logical or "
                    "factual?",
                    "n",
                ),
                ("Decided by", "b", TEAL),
                (
                    "anvayād itarataś ca (Bhāgavata 1.1.1): factual; Brahman in the world "
                    "and beyond it.",
                    "n",
                ),
            ],
        ),
    ]
    top = F.cur
    hs = [
        F.card(2 + i * 32.5, top, 31, header=h, paras=p, ec=TEAL, hsize=7.6, draw=False)
        for i, (h, p) in enumerate(cards)
    ]
    hmax = max(hs)
    for i, (h, p) in enumerate(cards):
        F.card(
            2 + i * 32.5, top, 31, header=h, paras=p, ec=TEAL, hsize=7.6, fixed_h=hmax
        )
    F.cur = top + hmax + 12
    h = F.card(
        2,
        F.cur,
        96,
        header="Lines 2–3 · in the upadeśa-kāla",
        paras=[
            (
                "aviruddhaṁ tu yat tv asya pramāṇam: Manu and the rest (twenty-eight "
                "smṛtis and more) are pramāṇa where they do not contradict the four; "
                "partly agreeing and partly conflicting, apramāṇa (etad viruddhaṁ … na "
                "tan mānaṁ kathañcana). Yet the Veda itself says yad vai kiṁ ca manur "
                "avadat tad bheṣajam, so the exclusion holds only for the "
                "upadeśa-kāla.",
                "n",
            )
        ],
        ec=TEAL,
        fc=PALE,
        lw=1.1,
        hsize=7.8,
    )
    F.cur += h + 12
    top = F.cur
    sub = [
        (
            "With śraddhā: bhagavat-sāmarthya",
            "an alaukika capacity in which everything can be; Śaivas take Śiva, "
            "Vaiṣṇavas Viṣṇu, and nobody goes to hell",
        ),
        (
            "By logic: bhagavat-sarvarūpatva",
            "all forms are his, the contradictory too; no corner is left out "
            "('brothers and sisters')",
        ),
    ]
    intro = layout(
        [
            (
                "athavā sarvarūpatvān nāmalīlāvibhedataḥ … pramāṇaṁ sarvam eva hi",
                "i",
                MAROON,
            ),
            (
                "vāṅmātram eva pramāṇam: every meaning is Bhagavān's form. Suspend what "
                "seems contradictory; it is resolved in two ways:",
                "n",
            ),
        ],
        96 * U - 2 * MX,
    )
    head_h = PADT + HEAD * LS + 3
    sub_top = top + head_h + height(intro) + 8
    hsub = max(
        F.card(
            5 + i * 46.5,
            sub_top,
            43.5,
            header=a,
            paras=[(b, "n")],
            ec=MAROON,
            hsize=7.4,
            draw=False,
        )
        for i, (a, b) in enumerate(sub)
    )
    total_h = sub_top - top + hsub + 8
    F.add("box", 2, top, 96, total_h, MAROON, PALE, 1.8)
    F.add(
        "text",
        50,
        top + PADT,
        "Kārikā 9 · after full knowledge",
        dict(size=7.8, weight="bold", color=MAROON, ha="center"),
    )
    F.lines(2 + MX / U, top + head_h, intro)
    for i, (a, b) in enumerate(sub):
        F.card(
            5 + i * 46.5,
            sub_top,
            43.5,
            header=a,
            paras=[(b, "n")],
            ec=MAROON,
            hsize=7.4,
            fixed_h=hsub,
        )
    F.cur = top + total_h + 12
    F.banner(
        "Verdict: four for the beginners, all śāstra once the siddhānta is grasped, all "
        "speech once Brahman is known; for the 'four-four' theory, 'Gaṇapati Bappā Moryā!'"
    )
    F.render("fig8_karikas_8_9.png")


if __name__ == "__main__":
    fig5()
    fig6()
    fig7()
    fig8()
