#!/usr/bin/env python3
"""Figures for Śāstrārtha Prakaraṇa, Lecture 9 (session of 2026-09-05).

Layout is planned in inches from the top of each figure and converted to
axes units (0-100 both ways), so every box is sized to its text.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.family"] = "DejaVu Sans"

OUT = Path(__file__).resolve().parent / "figs09"
OUT.mkdir(exist_ok=True)

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"

W = 6.2          # figure width, inches
LS = 1.32        # line spacing for body text
PAD_X = 0.012 * 70           # rounding pad, axes x-units
PAD_IN = PAD_X / 100 * W     # the same pad, inches


def lh(size):
    """Height of one body line, inches."""
    return size * LS / 72


class Fig:
    def __init__(self, h):
        self.h = h
        self.fig = plt.figure(figsize=(W, h), facecolor=PALE)
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")
        ax.set_facecolor(PALE)
        self.ax = ax

    # inches-from-top -> axes y ; inches -> axes height
    def Y(self, t):
        return 100 - t / self.h * 100

    def H(self, d):
        return d / self.h * 100

    def box(self, x, top, w, d, ec=TEAL, fc=SAND, lw=1.0, ls="-"):
        # The rounding pad grows the patch outward by PAD_X axes units
        # (= PAD_IN inches) on every side; inset the rectangle by the same
        # amount so the visible box spans exactly x..x+w and top..top+d.
        self.ax.add_patch(FancyBboxPatch(
            (x + PAD_X, self.Y(top + d - PAD_IN)), w - 2 * PAD_X,
            self.H(d - 2 * PAD_IN),
            boxstyle="round,pad=0.012", mutation_scale=70,
            mutation_aspect=W / self.h, fc=fc, ec=ec, lw=lw, ls=ls, zorder=1))

    def title(self, s, t=0.24, size=12):
        self.ax.text(50, self.Y(t), s, ha="center", va="center",
                     fontsize=size, color=INK, fontweight="bold")

    def header(self, x, top, s, color=TEAL, size=8.5):
        """Header whose cap line sits at `top`; baseline-aligned."""
        base = top + 0.72 * size / 72
        self.ax.text(x, self.Y(base), s, ha="center", va="baseline",
                     fontsize=size, color=color, fontweight="bold", zorder=3)

    def text(self, x, top, lines, size=6.8, color=INK, style="normal",
             weight="normal", ha="center"):
        self.ax.text(x, self.Y(top), "\n".join(lines), ha=ha, va="top",
                     fontsize=size, color=color, linespacing=LS,
                     fontstyle=style, fontweight=weight, zorder=3)

    def footer(self, lines, size=7.0):
        d = len(lines) * 0.145 + 0.10
        top = self.h - 0.05 - d
        self.box(3, top, 94, d, ec=OCHRE, fc=OCHRE, lw=0.8)
        self.ax.text(50, self.Y(top + d / 2), "\n".join(lines),
                     ha="center", va="center", fontsize=size, color="white",
                     fontweight="bold", linespacing=1.3, zorder=3)

    def arrow(self, x1, t1, x2, t2, color=OCHRE, lw=1.4, style="-|>"):
        self.ax.add_patch(FancyArrowPatch(
            (x1, self.Y(t1)), (x2, self.Y(t2)), arrowstyle=style,
            mutation_scale=10, color=color, lw=lw, zorder=2))

    def save(self, name):
        self.fig.savefig(OUT / name, dpi=200, bbox_inches="tight",
                         pad_inches=0.12, facecolor=PALE)
        plt.close(self.fig)


def panel(f, x, top, w, d, head, lines, sub=None, ec=TEAL, fc=SAND, lw=1.0,
          ls="-", hsize=8.5, size=6.8, hcolor=None, subsize=6.6,
          substyle="italic", subweight="normal", subcolor=GREY):
    """A rounded box with a centred header, optional sub-line, and a
    top-anchored body."""
    f.box(x, top, w, d, ec=ec, fc=fc, lw=lw, ls=ls)
    cx = x + w / 2
    f.header(cx, top + 0.11, head, color=hcolor or ec, size=hsize)
    body_top = top + 0.33
    if sub:
        f.text(cx, top + 0.31, [sub], size=subsize, color=subcolor,
               style=substyle, weight=subweight)
        body_top = top + 0.49
    f.text(cx, body_top, lines, size=size)


def need(n, sub=True, size=6.8):
    """Box height needed for n body lines."""
    return (0.49 if sub else 0.33) + n * lh(size) + 0.12


# ---------------------------------------------------------------- Figure 1
def fig1():
    h = 4.8
    f = Fig(h)
    ax = f.ax

    def circle(cx, cy, r, ec, fc, lw):
        ax.add_patch(Ellipse((cx, cy), 2 * r, 2 * r * W / h, ec=ec, fc=fc,
                             lw=lw, zorder=1))

    f.title("Two circles, not synonyms")
    circle(33, 52, 27, TEAL, SAND, 1.2)
    circle(33, 40, 15.5, MAROON, PALE, 1.8)
    ax.text(33, 81.2, "TĀDĀTMYA", ha="center", va="baseline", fontsize=8.5,
            color=TEAL, fontweight="bold", zorder=3)
    ax.text(33, 78.4, "\n".join([
        "the wider circle",
        "svābhāvika · āgantuka · aupādhika",
        "āropita (names, posts) · practical",
        "even a madman's (Zweig's prisoner)",
    ]), ha="center", va="top", fontsize=6.8, color=INK, linespacing=LS,
        zorder=3)
    ax.text(33, 46.4, "VIRUDDHA-DHARMĀŚRAYA", ha="center", va="baseline",
            fontsize=8, color=MAROON, fontweight="bold", zorder=3)
    ax.text(33, 43.6, "\n".join([
        "two opposed properties",
        "on equal, real footing",
        "in one substrate",
        "⇒ tādātmya is necessary",
    ]), ha="center", va="top", fontsize=6.8, color=INK, linespacing=LS,
        zorder=3)
    f.box(66, 1.05, 31, 2.25, ec=GREY, fc=PALE, ls="--")
    f.header(81.5, 1.16, "NO TĀDĀTMYA", color=GREY)
    f.text(81.5, 1.40, [
        "Mirror: we are not in it, yet we",
        "appear in it. The not-being is",
        "pāramārthika; the appearing",
        "is not.",
        "",
        "Mirage: no water in the desert,",
        "yet water appears; it 'is' only",
        "in the sense that it is seen.",
        "",
        "One property real, the other",
        "only apparent: not on an",
        "equal footing.",
    ])
    ax.add_patch(FancyArrowPatch((65.5, 56), (59.6, 56), arrowstyle="-",
                                 color=GREY, lw=1.0, zorder=2))
    f.footer([
        "Wherever there is a true viruddha-dharmāśraya there is tādātmya;",
        "wherever there is tādātmya, there need not be viruddha-dharmāśraya.",
    ])
    f.save("fig1_circles.png")


# ---------------------------------------------------------------- Figure 2
def fig2():
    left = [
        "Light and darkness cannot stay together;",
        "so subject and object cannot coexist.",
        "The subject can never be the object;",
        "kartā cannot be karma.",
        "",
        "The objectivity seen in the subject",
        "is therefore kalpita: adhyāsa, the root",
        "of every anartha, which the",
        "brahma-jijñāsā is begun to remove.",
        "",
        "Existentialists: to act as pour-soi,",
        "treating oneself as an object,",
        "is 'bad faith'.",
    ]
    right = [
        "Noun is being, verb is becoming (Yāska):",
        "each needs the other.",
        "Svara is not laya, yet every svara shows",
        "a laya and every laya a svara.",
        "Seed hides fruit; fruit hides seed.",
        "Singer and tabla player: opposed,",
        "not contradictory.",
        "",
        "Consciousness is svaprakāśa; the self",
        "raises itself by itself (Gītā 6.5).",
        "Tad ātmānaṁ svayam akuruta (TU 2.7.1):",
        "Brahman is kartā and karma at once.",
    ]
    d = need(len(left))
    h = 0.48 + d + 0.16 + 0.39 + 0.05
    f = Fig(h)
    f.title("Opposed: contradictory or complementary?")
    panel(f, 3, 0.48, 45, d, "OPPOSITION AS CONTRADICTION", left,
          sub="Śaṅkara (and, in parallel, the existentialists)")
    panel(f, 52, 0.48, 45, d, "OPPOSITION AS COMPLEMENT", right,
          sub="Vallabhācārya, as the speaker reads him", ec=MAROON, lw=2.0)
    f.footer([
        "“How much badness is there in the bad faith?” — opposition need not",
        "make the unity mithyā.",
    ])
    f.save("fig2_complementary.png")


# ---------------------------------------------------------------- Figure 3
def fig3():
    row1 = [
        ("SVĀBHĀVIKA", "by default", [
            "there from the start;",
            "neither acquired later",
            "nor imposed from outside",
        ]),
        ("ĀGANTUKA", "acquired, yet real", [
            "not there at first, comes later,",
            "and is real, not bhrānti:",
            "a child's moustache, the hair",
            "that grows, later the baldness",
        ]),
        ("AUPĀDHIKA", "from an upādhi", [
            "shows only beside another:",
            "tall beside a hill man,",
            "short beside a Northern",
            "European",
        ]),
    ]
    d1 = need(4)
    d2 = need(3)
    d3 = need(3, sub=False)
    t1 = 0.48
    t2 = t1 + d1 + 0.14
    tl = t2 + d2 + 0.17
    t3 = tl + 0.15
    h = t3 + d3 + 0.16 + 0.39 + 0.05
    f = Fig(h)
    f.title("Grades of tādātmya (and of bheda)")
    for (hd, sub, lines), x in zip(row1, (3, 35.5, 68)):
        panel(f, x, t1, 29, d1, hd, lines, sub=sub)
    panel(f, 3, t2, 45, d2, "ĀROPITA", [
        "names (Suresh, Dīkṣita); posts (collector, CEO);",
        "road-signal colours; the owl at Sarasvatī's feet.",
        "Done intentionally; not prātibhāsika.",
    ], sub="imputed, yet real once imputed", ec=MAROON, lw=2.0)
    panel(f, 52, t2, 45, d2, "BHRĀNTI-KALPITA", [
        "'Dīpak Siṅghjī' for Dīkṣita; the snake",
        "on the rope; for Śaṅkara, the tādātmya of",
        "pure and māyic Brahman (bhrānti-pratipanna)",
    ], sub="mistaken", ec=GREY, fc=PALE, ls="--")
    f.ax.text(50, f.Y(tl), "Two directions of imputation", ha="center",
              va="center", fontsize=8, color=TEAL, fontweight="bold")
    panel(f, 3, t3, 45, d3, "ABHEDE BHEDĀROPA", [
        "rāhoḥ śiraḥ, 'Rāhu's head': Rāhu is the head,",
        "yet the genitive speaks of two",
        "= abheda-sahiṣṇu bheda (bheda predominates)",
    ], hsize=8)
    panel(f, 52, t3, 45, d3, "BHEDE ABHEDĀROPA", [
        "mamātmā bhadrasenaḥ, 'Bhadrasena is my self':",
        "two persons, spoken of as one",
        "= bheda-sahiṣṇu abheda (abheda predominates)",
    ], hsize=8)
    f.footer([
        "Āropita is not kalpita: Śaṅkara treats them as one; for the speaker,",
        "what is imputed becomes real after the imputation.",
    ])
    f.save("fig3_kinds.png")


# ---------------------------------------------------------------- Figure 4
def fig4():
    rows = [
        (["“X is a human being”", "(only this much, from far away)"],
         ["“X is male” or “X is female”", "(found on observing closely)"],
         "come closer", TEAL),
        (["a drop of blood,", "as perceived"],
         ["its elements, worked out in", "the pathology laboratory"],
         "analyse", TEAL),
        (["Vedic doctrine:", "vaidikas tu etāvān eva siddhāntaḥ"],
         ["Vaiṣṇava śāstra: kiñcid adhikam —",
          "Brahman analysed as Viṣṇutva"], "Vaiṣṇava śāstra", MAROON),
    ]
    rd = 0.12 + 2 * lh(6.8) + 0.12
    t0 = 0.74
    gap = 0.16
    tn = t0 + 3 * rd + 2 * gap + 0.16
    h = tn + 2 * lh(6.6) + 0.16 + 0.39 + 0.05
    f = Fig(h)
    f.title("Seen from afar, seen up close")
    for x, lab in ((22, "DISTANT VIEW"), (77.5, "CLOSE VIEW · ANALYSIS")):
        f.header(x, 0.50, lab, size=8.5)
    for i, (left, right, lab, rc) in enumerate(rows):
        top = t0 + i * (rd + gap)
        f.box(3, top, 38, rd)
        f.text(22, top + 0.12, left)
        f.box(58, top, 39, rd, ec=rc, lw=2.0 if rc == MAROON else 1.0)
        f.text(77.5, top + 0.12, right)
        mid = top + rd / 2
        f.arrow(42.5, mid, 56.5, mid)
        f.ax.text(49.5, f.Y(mid - 0.05), lab, ha="center", va="bottom",
                  fontsize=6.4, color=OCHRE, fontstyle="italic")
    f.text(50, tn, [
        "Bālabodha: Śiva and Viṣṇu are both benefactors of the world;",
        "purāṇeṣv api sarveṣu tat-tad-rūpo haris tathā — Hari in the form of"
        " each deity.",
    ], size=6.6, color=GREY, style="italic")
    f.footer([
        "Different, even opposed, yet complementary — and nothing complements",
        "without a common substance: tādātmya, not contradiction.",
    ])
    f.save("fig4_far_near.png")


# ---------------------------------------------------------------- Figure 5
def fig5():
    cols = [
        (3, "ŚAṄKARA", TEAL, 1.0, "bheda", [
            "(though an abhedavādī)",
            "",
            "Māyā is not Brahman's own",
            "śakti; the world is māyā's",
            "pariṇāma.",
            "",
            "Brahman: avācya, yet definable",
            "as what is never cancelled.",
            "Māyā: speakable, not definable",
            "(anirvacanīya).",
            "",
            "Cancel māyā and the world is",
            "cancelled with it.",
        ]),
        (35.5, "BHĀSKARA", TEAL, 1.0, "bhedābheda", [
            "mutual implication, like the",
            "dhanavān and his dhana",
            "",
            "Māyā is Brahman's own",
            "potentiality; the world is",
            "śakti-pariṇāma.",
            "",
            "Śakti is definable and real.",
            "",
            "The world's drawbacks do not",
            "touch Brahman.",
        ]),
        (68, "VALLABHA", MAROON, 2.0, "tādātmya", [
            "Svarūpa-pariṇāma: Brahman",
            "itself becomes the world —",
            "ātma-kṛteḥ pariṇāmāt",
            "(BS 1.4.26).",
            "",
            "Śakti is only the instrument:",
            "the artist and his skill, the",
            "hand that lifts the napkin.",
            "",
            "Avikṛta: transformed, yet",
            "untransformed.",
        ]),
    ]
    d = need(13)
    h = 0.48 + d + 0.16 + 0.39 + 0.05
    f = Fig(h)
    f.title("Śakti and śaktimān: three stands")
    for x, hd, ec, lw, rel, lines in cols:
        panel(f, x, 0.48, 29, d, hd, lines, sub=rel, ec=ec, lw=lw,
              subsize=8, substyle="italic", subweight="bold", subcolor=ec)
    f.footer([
        "Who stands at the front? Śaṅkara and Bhāskara deploy the śakti;",
        "Mahāprabhuji brings the śaktimān first.",
    ])
    f.save("fig5_three_acaryas.png")


# ---------------------------------------------------------------- Figure 6
def fig6():
    trio = [
        (3, "THESIS · ŚAṄKARA", TEAL, 1.0, [
            "the world is the pariṇāma",
            "of an indefinable śakti,",
            "so it too is unreal",
        ]),
        (35.5, "ANTITHESIS · BHĀSKARA", TEAL, 1.0, [
            "śakti is definable: śakti and",
            "śaktimān imply each other;",
            "real, and Brahman unaffected",
        ]),
        (68, "SYNTHESIS · VALLABHA", MAROON, 2.0, [
            "avikṛta-pariṇāma: Brahman",
            "itself, transformed yet",
            "untransformed",
        ]),
    ]
    d1 = need(3, sub=False)
    d2 = need(6)
    t1 = 0.66
    t2 = t1 + d1 + 0.20
    h = t2 + d2 + 0.16 + 0.39 + 0.05
    f = Fig(h)
    f.title("Out of nothing, or out of itself?")
    f.ax.text(50, f.Y(0.49), "Hegel's triad, as the speaker applies it",
              ha="center", va="center", fontsize=7, color=GREY,
              fontstyle="italic")
    for x, hd, ec, lw, lines in trio:
        panel(f, x, t1, 29, d1, hd, lines, ec=ec, lw=lw, hsize=8)
    mid = t1 + d1 / 2
    f.arrow(32.4, mid, 35.0, mid)
    f.arrow(64.9, mid, 67.5, mid)
    panel(f, 3, t2, 45, d2, "CREATION EX NIHILO", [
        "God creates something out of nothing",
        "by divine power: the world is neither",
        "a modification of divinity nor of",
        "divine power.",
        "Looking at the something, you cannot",
        "recognize the nothing.",
    ], sub="the Abrahamic view, as the speaker characterizes it",
        ec=GREY, fc=PALE, ls="--", subsize=6.4)
    panel(f, 52, t2, 45, d2, "OUT OF ITSELF", [
        "The world is the sat-pariṇāma of",
        "Brahman's sat-aṁśa: from sat one infers",
        "sat; from one's own consciousness,",
        "a causal consciousness.",
        "Like the spider's web and parachute:",
        "a capacity there by default.",
    ], sub="Mahāprabhuji", ec=MAROON, lw=2.0, subsize=6.4)
    f.footer([
        "Brahman is kartā and karma, knower and known, subject and object —",
        "“this synthesis is Mahāprabhuji's philosophy”.",
    ])
    f.save("fig6_creation.png")


# ---------------------------------------------------------------- Figure 7
def fig7():
    colx = [(15, "NAIVE"), (43, "CRITICAL"), (71, "CONDITIONAL")]
    cw = 25
    rows = [
        ("REALISM", [
            ["whatever appears is real:", "Sūradāsa's dog in the glass",
             "temple, barking at itself"],
            ["not all that appears is", "true, nor all mithyā:",
             "analyse each case", "critically"],
            ["real under a condition:", "a man is categorically a",
             "man, an uncle only", "conditionally"],
        ]),
        ("IDEALISM", [
            ["everything is idea, nothing", "outside the mind: almost",
             "Śaṅkara's principle, and", "Buddha's"],
            ["even a dream draws on what", "was seen outside: assess",
             "the idea critically"],
            ["an idea is idea only under", "a condition; otherwise it",
             "may be real"],
        ]),
    ]
    rd = 0.12 + 4 * lh(6.6) + 0.10
    t1 = 0.70
    t2 = t1 + rd + 0.12
    t3 = t2 + rd + 0.20
    d3 = need(5, sub=False, size=6.6)
    h = t3 + d3 + 0.16 + 0.39 + 0.05
    f = Fig(h)
    f.title("Realisms, idealisms, and Mahāprabhuji's stand")
    for x, lab in colx:
        f.header(x + cw / 2, 0.47, lab, size=8)
    for top, (rl, cells) in zip((t1, t2), rows):
        f.ax.text(8.5, f.Y(top + rd / 2), rl, ha="center", va="center",
                  fontsize=8, color=TEAL, fontweight="bold", rotation=90)
        for (x, _), lines in zip(colx, cells):
            f.box(x, top, cw, rd)
            f.text(x + cw / 2, top + 0.12, lines, size=6.6)
    panel(f, 3, t3, 21, d3, "HUME", [
        "everything is", "doubtful — even", "tomorrow's sunrise",
    ], ec=GREY, fc=PALE, ls="--", hsize=8, size=6.6)
    f.arrow(24.9, t3 + d3 / 2, 29.0, t3 + d3 / 2)
    panel(f, 29.5, t3, 24.5, d3, "KANT", [
        "woken from “dogmatic", "slumber”: the thing as it",
        "is is unknowable; as it", "appears, knowable",
    ], hsize=8, size=6.6)
    panel(f, 57.5, t3, 39.5, d3, "MAHĀPRABHUJI", [
        "the thing as it is: real, and partly",
        "knowable; the thing as it appears:",
        "knowable but not real — an interactive",
        "reality, with our own chilli-masālā",
        "added",
    ], ec=MAROON, lw=2.0, hsize=8, size=6.6)
    f.footer([
        "Neither a naive realist nor a naive idealist — whether critical or",
        "conditional is left for a future dialogue.",
    ])
    f.save("fig7_realism.png")


# ---------------------------------------------------------------- Figure 8
def fig8():
    boxes = [
        (3, "PRAPAÑCA", "prakṛṣṭa pañca", MAROON, 2.0, SAND, "-", [
            "earth, water, fire, air, ākāśa:",
            "the Lord's effect, objectively",
            "real. We are its products —",
            "can the pot call clay its",
            "imagination?",
        ]),
        (35.5, "PARTIAL CONSCIOUSNESS", "the Lord's avidyā-śakti", TEAL, 1.0,
         SAND, "-", [
             "a 'magical power': we see that",
             "it happens, not how. Not all-",
             "encompassing, it grasps half a",
             "picture and adds its own",
             "chilli-masālā.",
         ]),
        (68, "SAṀSĀRA", "saṁsarati: it creeps in", GREY, 1.0, PALE, "--", [
            "termites, a cockroach, a virus,",
            "the hour hand: a khichḍī of",
            "reality and imagination —",
            "'my child' (the DNA tests)",
        ]),
    ]
    d1 = need(5)
    t1 = 0.50
    tl = t1 + d1 + 0.05
    t2 = tl + 0.24
    d2 = need(3, sub=False)
    h = t2 + d2 + 0.16 + 0.39 + 0.05
    f = Fig(h)
    f.title("Prapañca and saṁsāra")
    for x, hd, sub, ec, lw, fc, ls, lines in boxes:
        panel(f, x, t1, 29, d1, hd, lines, sub=sub, ec=ec, fc=fc, lw=lw,
              ls=ls, hsize=8, subsize=6.5)
    mid = t1 + d1 / 2
    f.arrow(32.4, mid, 35.0, mid)
    f.arrow(64.9, mid, 67.5, mid)
    f.ax.text(50, f.Y(tl), "the arrows: interaction", ha="center",
              va="top", fontsize=6.4, color=OCHRE, fontstyle="italic")
    panel(f, 3, t2, 94, d2, "KŪPA-MAṆḌŪKA-NYĀYA", [
        "The frog circles its well three times, then three hundred, and asks:",
        "“Is the ocean this big?” The infinity of reality cannot be measured",
        "by a finite intellect, a frog in the well of the skull.",
    ], hsize=8)
    f.footer([
        "Saṁsāra is mithyā; the prapañca is not — not knowing their",
        "difference is the whole trouble.",
    ])
    f.save("fig8_prapanca.png")


if __name__ == "__main__":
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        fn()
    print("figures written to", OUT)
