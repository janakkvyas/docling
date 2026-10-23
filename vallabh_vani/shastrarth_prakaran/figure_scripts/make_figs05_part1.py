#!/usr/bin/env python3
"""Figures 1-4 for Lecture 5, Part 1 (Śāstrārtha Prakaraṇa, session of 2026-08-08).

Layout is computed top-down in points so that every box fits its text; the
canvas is then sized to the content and mapped onto axes running 0-100 both ways.
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

OUT = Path(__file__).resolve().parent / "figs05"
OUT.mkdir(exist_ok=True)

WIDTH_IN = 6.2
LS = 1.32  # body line spacing
MS = 45  # mutation scale for the rounded boxes (pad = 0.012 * MS units)


def body_h(size, n):
    return size * LS * n


def card_h(hsize=8.5, hlines=1, bsize=6.8, blines=0):
    h = 5 + hsize * 1.22 * hlines + 6
    if blines:
        h += 4 + body_h(bsize, blines)
    return h


class Fig:
    """Collects drawing commands with vertical positions in points from the top."""

    def __init__(self):
        self.cmds = []
        self.cur = 6.0  # top margin

    # ---- recording helpers -------------------------------------------------
    def title(self, text, sub=None):
        self.cmds.append(
            (
                "text",
                50,
                self.cur,
                text,
                dict(size=12, weight="bold", color=INK, ha="center"),
            )
        )
        self.cur += 17
        if sub:
            self.cmds.append(
                (
                    "text",
                    50,
                    self.cur,
                    sub,
                    dict(size=7.2, style="italic", color=GREY, ha="center"),
                )
            )
            self.cur += 10
        self.cur += 10

    def card(
        self,
        x,
        top,
        w,
        h,
        header=None,
        body=None,
        ec=TEAL,
        fc=SAND,
        lw=1.0,
        hsize=8.5,
        hlines=1,
        bsize=6.8,
        align="left",
        hcol=None,
    ):
        self.cmds.append(
            (
                "card",
                x,
                top,
                w,
                h,
                header,
                body,
                ec,
                fc,
                lw,
                hsize,
                hlines,
                bsize,
                align,
                hcol,
            )
        )

    def banner(self, top, text, size=7.0, ec=OCHRE, fc=SAND, nlines=2):
        h = 6 + body_h(size, nlines) + 5
        self.cmds.append(
            ("card", 2, top, 96, h, None, text, ec, fc, 1.1, 0, 0, size, "center", None)
        )
        return h

    def text(self, x, top, s, **kw):
        self.cmds.append(("text", x, top, s, kw))

    def line(self, x1, y1, x2, y2):
        self.cmds.append(("line", x1, y1, x2, y2))

    def arrow(self, x1, y1, x2, y2):
        self.cmds.append(("arrow", x1, y1, x2, y2))

    # ---- rendering -----------------------------------------------------------
    def render(self, name, bottom_margin=5.0):
        total = self.cur + bottom_margin
        height_in = total / 72.0
        fig = plt.figure(figsize=(WIDTH_IN, height_in))
        fig.patch.set_facecolor(PALE)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")

        def Y(pt):
            return 100.0 - pt * 100.0 / total

        def H(pt):
            return pt * 100.0 / total

        for c in self.cmds:
            kind = c[0]
            if kind == "text":
                _, x, top, s, kw = c
                ax.text(
                    x,
                    Y(top),
                    s,
                    ha=kw.get("ha", "left"),
                    va="top",
                    fontsize=kw.get("size", 6.8),
                    color=kw.get("color", INK),
                    style=kw.get("style", "normal"),
                    weight=kw.get("weight", "normal"),
                    linespacing=LS,
                )
            elif kind == "line":
                _, x1, y1, x2, y2 = c
                ax.plot(
                    [x1, x2], [Y(y1), Y(y2)], color=INK, lw=0.9, solid_capstyle="butt"
                )
            elif kind == "arrow":
                _, x1, y1, x2, y2 = c
                ax.add_patch(
                    FancyArrowPatch(
                        (x1, Y(y1)),
                        (x2, Y(y2)),
                        arrowstyle="-|>",
                        mutation_scale=9,
                        color=OCHRE,
                        lw=1.2,
                    )
                )
            elif kind == "card":
                (
                    _,
                    x,
                    top,
                    w,
                    h,
                    header,
                    body,
                    ec,
                    fc,
                    lw,
                    hsize,
                    hlines,
                    bsize,
                    align,
                    hcol,
                ) = c
                ax.add_patch(
                    FancyBboxPatch(
                        (x, Y(top + h)),
                        w,
                        H(h),
                        boxstyle="round,pad=0.012",
                        mutation_scale=MS,
                        fc=fc,
                        ec=ec,
                        lw=lw,
                    )
                )
                if header and not body:
                    # header-only box: centre the label vertically
                    ax.text(
                        x + w / 2,
                        Y(top + h / 2),
                        header,
                        ha="center",
                        va="center",
                        fontsize=hsize,
                        weight="bold",
                        color=hcol or ec,
                        linespacing=1.15,
                    )
                    continue
                y_cursor = top + 5
                if header:
                    ax.text(
                        x + w / 2,
                        Y(y_cursor),
                        header,
                        ha="center",
                        va="top",
                        fontsize=hsize,
                        weight="bold",
                        color=hcol or ec,
                        linespacing=1.15,
                    )
                    y_cursor += hsize * 1.22 * hlines + 4
                else:
                    y_cursor += 1
                if body:
                    if align == "center":
                        ax.text(
                            x + w / 2,
                            Y(y_cursor),
                            body,
                            ha="center",
                            va="top",
                            fontsize=bsize,
                            color=INK,
                            linespacing=LS,
                        )
                    else:
                        ax.text(
                            x + 1.5,
                            Y(y_cursor),
                            body,
                            ha="left",
                            va="top",
                            fontsize=bsize,
                            color=INK,
                            linespacing=LS,
                        )
        fig.savefig(
            OUT / name,
            dpi=200,
            bbox_inches="tight",
            pad_inches=0.12,
            facecolor=fig.get_facecolor(),
        )
        plt.close(fig)


# ---------------------------------------------------------------- Figure 1
def fig1():
    f = Fig()
    f.title(
        "Imperative or descriptive: where does scripture's authority lie?",
        "āmnāyasya kriyārthatvād ānarthakyam atadarthānām  (Mīmāṁsā Sūtra 1.2.1)",
    )

    h = card_h(8.5, 1, 6.8, 3)
    top = f.cur
    f.card(
        2,
        top,
        46.5,
        h,
        "Imperative statement · kartavya, vidhi",
        "Tells us our duty. The purpose of the Veda is\n"
        "to teach kartavya, so here the Veda is\n"
        "pramāṇa.",
    )
    f.card(
        51.5,
        top,
        46.5,
        h,
        "Descriptive statement · the story",
        "stutyarthena vidhīnāṁ syuḥ (MS 1.2.7): it only\n"
        "glorifies the injunction. True or false does\n"
        "not matter; no tātparya in the story itself.",
    )
    f.cur += h + 4
    f.arrow(25.25, f.cur, 25.25, f.cur + 13)
    f.arrow(74.75, f.cur, 74.75, f.cur + 13)
    f.text(
        50,
        f.cur + 2.5,
        "the same pair, and the same question, in every tradition",
        size=7.0,
        style="italic",
        color=OCHRE,
        ha="center",
    )
    f.cur += 17

    cols = [
        (
            "Veda: blow on jñāna-kāṇḍa",
            "Duty: the ritual injunctions.\n"
            "Story: Brahman is saccidānanda;\n"
            "from Brahman ākāśa, from ākāśa\n"
            "vāyu; Brahman gives the fruits.\n"
            "No imperative here, so by a\n"
            "'shortcut' this too is read as\n"
            "arthavāda: 'whether Brahman\n"
            "created the world is not\n"
            "important'.",
        ),
        (
            "Bible: Genesis and Moses",
            "Duty: the Ten Commandments.\n"
            "Story: Genesis, the world made\n"
            "in seven days, Sunday a holiday.\n"
            "Objection: where did seven days\n"
            "come from before God?\n"
            "Genesis kept as gauṇa,\n"
            "secondary, authority; those\n"
            "who questioned were burned.",
        ),
        (
            "Every religion: miracles",
            "Teaching given through stories\n"
            "of miracles: Christ; Buddhist\n"
            "and Jain stories; the Purāṇas;\n"
            "the vārtās. Spinoza: a miracle\n"
            "is what we do not understand,\n"
            "so no conclusion follows.\n"
            "Reformists: the duty is\n"
            "pramāṇa, not the story.",
        ),
    ]
    h = card_h(7.9, 1, 6.8, 9)
    w = 30.0
    for i, (hd, b) in enumerate(cols):
        f.card(2 + i * (w + 3.0), f.cur, w, h, hd, b, hsize=7.9)
    f.cur += h + 9

    f.text(
        50,
        f.cur,
        "In every religion the same triangle: priests who preach · "
        "interpreters of the text · those who question",
        size=6.8,
        style="italic",
        color=GREY,
        ha="center",
    )
    f.cur += 18

    f.cur += f.banner(
        f.cur,
        "Not karma-kāṇḍa against jñāna-kāṇḍa: the root question is hermeneutics. Do imperative\n"
        "or descriptive statements carry more authenticity? It touches the two kāṇḍas only 'accidentally'.",
    )
    f.cur += 9
    h = card_h(8.5, 1, 6.8, 1)
    f.card(
        2,
        f.cur,
        96,
        h,
        "Mahāprabhuji · śabda eva pramāṇam",
        "The glorification is also told by śabda, so the arthavāda too is pramāṇa.",
        ec=MAROON,
        fc=PALE,
        lw=1.6,
        align="center",
    )
    f.cur += h
    f.render("fig1_arthavada_hermeneutics.png")


# ---------------------------------------------------------------- Figure 2
def fig2():
    f = Fig()
    f.title(
        "The four vṛttis, and why the primary meaning is left",
        "abhidhā · lakṣaṇā · gauṇī · vyañjanā;  anvaya and tātparya are the regulators",
    )

    vr = [
        (
            "abhidhā",
            "the 'dictionary',\n'grammatical',\n'technological'\nmeaning: the\nprimary sense.\n"
            "'Gaṅgā' = the river.",
        ),
        (
            "lakṣaṇā",
            "śakya-sambandho\nlakṣaṇā: a sense\nrelated to the\nprimary one.\n"
            "gaṅgāyāṁ ghoṣaḥ:\nthe village is on\nthe bank.",
        ),
        (
            "gauṇī",
            "rūpaka, 'metaphor':\nthe qualities are\nsuperimposed.\n"
            "'lion', 'fox',\n'donkey', 'owl':\nall praise and\nall abuse.",
        ),
        (
            "vyañjanā",
            "tātparya-vṛtti: the\nprimary sense is\nnot cancelled.\n"
            "sūryo ’stam gataḥ:\n'the sun has set'\n= 'let's go for\nour walk'.",
        ),
    ]
    g = 3.2
    w = (96 - 3 * g) / 4
    h = card_h(8.8, 1, 6.7, 7)
    for i, (hd, b) in enumerate(vr):
        f.card(2 + i * (w + g), f.cur, w, h, hd, b, hsize=8.8, bsize=6.7)
    f.cur += h + 4
    f.arrow(25.25, f.cur, 25.25, f.cur + 13)
    f.arrow(74.75, f.cur, 74.75, f.cur + 13)
    f.text(
        50,
        f.cur + 2.5,
        "why the primary meaning is left",
        size=7.0,
        style="italic",
        color=OCHRE,
        ha="center",
    )
    f.cur += 17

    h = card_h(8.5, 1, 6.8, 4)
    f.card(
        2,
        f.cur,
        46.5,
        h,
        "anvayānupapatti",
        "The words do not connect: a village\n"
        "cannot be settled on a river, so\n"
        "'Gaṅgā' is taken as its bank.",
    )
    f.card(
        51.5,
        f.cur,
        46.5,
        h,
        "tātparyānupapatti",
        "The speaker's intention is incoherent:\n"
        "'Go fall in a well!' (the son jumped in);\n"
        "'you bathed me with fire'; 'as foolish\n"
        "as a donkey'.",
    )
    f.cur += h + 10

    h = card_h(8.0, 1, 6.8, 6)
    f.card(
        2,
        f.cur,
        46.5,
        h,
        "Śaṅkara · tātparyavat śabda pramāṇam",
        "Authority lies in tātparya, not in śabda.\n"
        "Road-sign arrows: take the turn, not the\n"
        "angle. The parrot's 'Pīr Nabī-jī, roṭī do!'\n"
        "and the mynah's 'Chāy lāo!' are words\n"
        "without tātparya: no one brings bread\n"
        "or tea.",
        hsize=8.0,
    )
    f.card(
        51.5,
        f.cur,
        46.5,
        h,
        "Mahāprabhuji · śabda eva pramāṇam",
        "The glorification in arthavāda is also\n"
        "told by śabda, so it too is pramāṇa.\n"
        "Tātparya is pramāṇa where it can be\n"
        "verified; where it cannot, śabda itself\n"
        "is pramāṇa.",
        ec=MAROON,
        fc=PALE,
        lw=1.6,
        hsize=8.0,
    )
    f.cur += h + 10

    f.cur += f.banner(
        f.cur,
        "Lakṣaṇā and gauṇī arise from anvayānupapatti or tātparyānupapatti; vyañjanā keeps the primary\n"
        "meaning. In this sense Śaṅkara did not accept śabda itself as pramāṇa.",
    )
    f.render("fig2_vrttis_tatparya.png")


# ---------------------------------------------------------------- Figure 3
def fig3():
    f = Fig()
    f.title(
        "Śabda, after the speaker's chart",
        "dhvani-rūpa and varṇa-rūpa;  laukikārtha and alaukikārtha saṅketaśālī",
    )

    # root
    top = f.cur
    f.card(42, top, 16, 20, "śabda", hsize=9.5)
    f.cur += 20
    y0 = f.cur
    f.line(50, y0 + 2, 50, y0 + 8)
    f.line(22, y0 + 8, 71, y0 + 8)
    f.line(22, y0 + 8, 22, y0 + 13)
    f.line(71, y0 + 8, 71, y0 + 13)
    f.cur += 14

    f.card(3, f.cur, 38, 20, "dhvani-rūpa · dhvanyātmaka", hsize=8.4)
    f.card(45, f.cur, 52, 20, "varṇa-rūpa · varṇātmaka", hsize=8.4)
    f.cur += 20
    y1 = f.cur
    # dhvani connectors
    kids = [(3, 7.5, "kaṭu"), (13.5, 15.5, "akaṭu-amadhura"), (32, 9, "madhura")]
    centres = [x + w / 2 for x, w, _ in kids]
    f.line(22, y1 + 2, 22, y1 + 8)
    f.line(centres[0], y1 + 8, centres[-1], y1 + 8)
    for cx in centres:
        f.line(cx, y1 + 8, cx, y1 + 13)
    # varna connectors
    f.line(71, y1 + 2, 71, y1 + 8)
    f.line(57.25, y1 + 8, 84.75, y1 + 8)
    f.line(57.25, y1 + 8, 57.25, y1 + 13)
    f.line(84.75, y1 + 8, 84.75, y1 + 13)
    f.cur += 14
    y2 = f.cur

    for x, w, label in kids:
        f.card(x, y2, w, 20, label, hsize=7.0)
    hv = card_h(7.6, 2, 0, 0) - 2
    f.card(45, y2, 24.5, hv, "laukikārtha\nsaṅketaśālī", hsize=7.6, hlines=2)
    f.card(
        72.5,
        y2,
        24.5,
        hv,
        "alaukikārtha\nsaṅketaśālī",
        hsize=7.6,
        hlines=2,
        ec=MAROON,
        fc=PALE,
        lw=1.6,
    )

    # varṇa column, below the two saṅketaśālī boxes
    y3 = y2 + hv
    hs = card_h(7.2, 1, 6.4, 1) - 2
    for x0, ec, fc, lw in ((45, TEAL, SAND, 1.0), (72.5, MAROON, PALE, 1.4)):
        cx = x0 + 12.25
        a, b = x0 + 5.375, x0 + 19.125
        f.line(cx, y3 + 2, cx, y3 + 7)
        f.line(a, y3 + 7, b, y3 + 7)
        f.line(a, y3 + 7, a, y3 + 12)
        f.line(b, y3 + 7, b, y3 + 12)
        f.card(
            x0,
            y3 + 13,
            10.75,
            hs,
            "kartavya",
            "imperative",
            ec=ec,
            fc=fc,
            lw=lw,
            hsize=7.2,
            bsize=6.4,
            align="center",
        )
        f.card(
            x0 + 13.75,
            y3 + 13,
            10.75,
            hs,
            "tattva",
            "descriptive",
            ec=ec,
            fc=fc,
            lw=lw,
            hsize=7.2,
            bsize=6.4,
            align="center",
        )
    y4 = y3 + 13 + hs + 9
    hb = card_h(8.2, 1, 6.6, 7)
    f.card(
        45,
        y4,
        24.5,
        hb,
        "verifiable",
        "From available sources\n"
        "of information we can\n"
        "check the action and its\n"
        "result; a cow can be\n"
        "shown. So tātparya can\n"
        "be judged: 'donkey' =\n"
        "as foolish as a donkey.",
        hsize=8.2,
        bsize=6.6,
    )
    f.card(
        72.5,
        y4,
        24.5,
        hb,
        "not verifiable",
        "Not 'supernatural', just\n"
        "not checkable: cowness,\n"
        "Andromeda's size,\n"
        "Bhagavān, Vaikuṇṭha,\n"
        "Prajāpati's vapā,\n"
        "Śaṅkara's father.\n"
        "Here: śabda eva pramāṇam.",
        ec=MAROON,
        fc=PALE,
        lw=1.6,
        hsize=8.2,
        bsize=6.6,
    )
    bottom = y4 + hb

    # dhvani column: one body card from below the three kids down to the same bottom
    yd = y2 + 20 + 9
    f.card(
        3,
        yd,
        38,
        bottom - yd,
        "bhāva, but no artha",
        "Sound carries bhāva, not meaning: a\n"
        "harsh sound gives a harsh bhāva, a\n"
        "sweet sound a sweet one. In English,\n"
        "'intonation': 'Kyoṁ āe?'\n\n"
        "Tabla bols are varṇātmaka yet\n"
        "meaningless; they convey only bhāva.\n"
        "Śivarañjanī played in a march set\n"
        "the soldiers dancing. The crow and\n"
        "the dog have tones for alarm, love\n"
        "and pain. Varṇātmaka speech gained\n"
        "'objectivity'; bhāva has to be added.",
        hsize=8.2,
        bsize=6.6,
    )
    f.cur = bottom + 10
    f.cur += f.banner(
        f.cur,
        "Dhvani conveys bhāva; varṇa conveys meaning. Where a meaning can be verified, its tātparya can\n"
        "be judged; where it cannot be verified in the world, Mahāprabhuji takes śabda itself as pramāṇa.",
    )
    f.render("fig3_sabda_chart.png")


# ---------------------------------------------------------------- Figure 4
def fig4():
    f = Fig()
    f.title(
        "When the utterance is there but the speaker is not",
        "two criteria for fixing tātparya (tātparya-nirṇaya)",
    )
    top = f.cur

    # left column: Mīmāṁsā's six liṅgas
    lingas = [
        ("1  upakrama–upasaṁhāra", "how the matter begins and how it concludes"),
        ("2  abhyāsa", "repetition (not the Gujarati abhyās, 'study')"),
        (
            "3  apūrvatā",
            "known subject, unknown predicate: 'Hitesh-bhāī\n"
            "brought this pen', not 'this is a pen'",
        ),
        (
            "4  phala",
            "a result, or else 'what do you want to say?'\n"
            "(the crow that caws and flies to another roof)",
        ),
        (
            "5  arthavāda",
            "praise, censure, history: the beggar's 'you are\n"
            "so generous!'; every dog a lion in its own lane",
        ),
        ("6  upapatti", "what you justify is what you mean"),
    ]
    y = top + 5 + 8.8 * 1.22 + 9
    rows = []
    for term, desc in lingas:
        n = desc.count("\n") + 1
        h = 4 + 7.4 * 1.22 + 3 + body_h(6.6, n) + 5
        rows.append((y, h, term, desc))
        y += h + 9
    left_bottom = y - 9 + 8

    # right column: Mahāprabhuji's added criterion
    yr = top + 5 + 8.8 * 1.22 + 7
    intro_y = yr
    yr += body_h(6.7, 4) + 12
    chain = ["Veda", "Gītā", "Brahmasūtra", "Bhāgavata"]
    chain_y = []
    for _ in chain:
        chain_y.append(yr)
        yr += 20 + 18
    yr -= 18
    yr += 10
    sutra_y = yr
    yr += 11
    eka_y = yr
    yr += 10 + 12
    avi_y = yr
    yr += body_h(6.6, 3) + 8
    right_bottom = yr

    bottom = max(left_bottom, right_bottom)
    f.card(2, top, 51, bottom - top, ec=TEAL, fc=PALE, lw=1.0)
    f.text(
        27.5,
        top + 5,
        "Mīmāṁsā · six liṅgas",
        size=8.8,
        weight="bold",
        color=TEAL,
        ha="center",
    )
    for y, h, term, desc in rows:
        f.card(4.5, y, 46, h, ec=TEAL, fc=SAND, lw=0.8)
        f.text(6.0, y + 4, term, size=7.4, weight="bold", color=TEAL)
        f.text(6.0, y + 4 + 7.4 * 1.22 + 3, desc, size=6.6, color=INK)

    f.card(56, top, 42, bottom - top, ec=MAROON, fc=PALE, lw=1.6)
    f.text(
        77,
        top + 5,
        "Mahāprabhuji · added criterion",
        size=8.8,
        weight="bold",
        color=MAROON,
        ha="center",
    )
    f.text(
        58.0,
        intro_y,
        "Every statement raises asambhāvanā\n"
        "('not possible') and viparīta-bhāvanā\n"
        "('not so, but otherwise'). What\n"
        "removes them is also pramāṇa.",
        size=6.7,
        color=INK,
    )
    for name, yc in zip(chain, chain_y):
        f.card(63, yc, 28, 20, name, ec=MAROON, fc=SAND, lw=1.1, hsize=7.8)
    for yc in chain_y[:-1]:
        f.arrow(77, yc + 20 + 3, 77, yc + 20 + 16)
        f.text(
            78.6,
            yc + 20 + 5.5,
            "its doubts removed by",
            size=6.0,
            style="italic",
            color=OCHRE,
        )
    f.text(
        77,
        sutra_y,
        "uttaraṁ pūrva-sandeha-vārakam",
        size=7.0,
        style="italic",
        color=MAROON,
        ha="center",
    )
    f.text(
        77, eka_y, "coordinated as one: ekavākyatā", size=6.6, color=INK, ha="center"
    )
    f.text(
        77,
        avi_y,
        "aviruddhaṁ tu yat tv asya pramāṇam:\n"
        "what does not conflict with these is\n"
        "pramāṇa; what conflicts is apramāṇa.",
        size=6.6,
        color=INK,
        ha="center",
    )

    f.cur = bottom + 9
    f.text(
        50,
        f.cur,
        "The news example: why would the Arab states befriend China? The information that removes the\n"
        "doubt: the protector they relied on cannot protect them.",
        size=6.6,
        style="italic",
        color=GREY,
        ha="center",
    )
    f.cur += body_h(6.6, 2) + 9
    f.cur += f.banner(
        f.cur,
        "Not a rejection but an addition: the six liṅgas stand, and the information that removes doubt\n"
        "is also pramāṇa (pramāṇaṁ tac catuṣṭayam). The label 'prasthāna-catuṣṭaya' is not Mahāprabhuji's.",
    )
    f.render("fig4_lingas_sandeha.png")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    fig4()
    print("figures written to", OUT)
