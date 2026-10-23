#!/usr/bin/env python3
"""Figures for Lecture 7 of the Śāstrārtha Prakaraṇa translation series.

Writes eight PNGs into figs07/ next to this script and reports any text that
crosses its container box or overlaps another text.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

plt.rcParams["font.family"] = "DejaVu Sans"

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"

OUT = Path(__file__).resolve().parent / "figs07"
OUT.mkdir(exist_ok=True)

# (axes, text artist, container (x, y, w, h) in data units, label)
CHECKS = []


def new_fig(height):
    fig = plt.figure(figsize=(6.2, height), facecolor=PALE, dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, fc=SAND, ec=TEAL, lw=1.0, ls="-"):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.012,rounding_size=1.2",
            fc=fc, ec=ec, lw=lw, ls=ls,
        )
    )
    return (x, y, w, h)


def register(ax, t, cont, label):
    CHECKS.append((ax, t, cont, label))
    return t


def header(ax, cont, text, color=TEAL, size=8.5, off=1.8):
    x, y, w, h = cont
    t = ax.text(x + w / 2, y + h - off, text, ha="center", va="top",
                fontsize=size, fontweight="bold", color=color)
    return register(ax, t, cont, "H:" + text[:28])


def body(ax, cont, text, top=6.5, size=6.8, color=INK, ha="left", pad=2.0,
         style="normal", weight="normal", ls=1.38):
    x, y, w, h = cont
    tx = {"left": x + pad, "center": x + w / 2, "right": x + w - pad}[ha]
    t = ax.text(tx, y + h - top, text, ha=ha, va="top", fontsize=size,
                color=color, style=style, fontweight=weight, linespacing=ls,
                multialignment=ha)
    return register(ax, t, cont, "B:" + text[:28].replace("\n", " "))


def free_text(ax, x, y, text, cont, size=6.6, color=GREY, ha="center",
              va="top", style="normal", weight="normal"):
    t = ax.text(x, y, text, ha=ha, va=va, fontsize=size, color=color,
                style=style, fontweight=weight, linespacing=1.3,
                multialignment=ha)
    return register(ax, t, cont, "T:" + text[:28].replace("\n", " "))


def arrow(ax, x1, y1, x2, y2, color=OCHRE, lw=1.3, ms=9):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=ms, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def title(ax, text, size=11.5, y=98.2):
    t = ax.text(50, y, text, ha="center", va="top", fontsize=size,
                fontweight="bold", color=MAROON)
    return register(ax, t, (0.5, 0, 99, 100), "title")


def banner(ax, y, h, text, fc=OCHRE, ec=None, color="white", size=7.0,
           top=2.0, lw=1.0, weight="normal", style="normal"):
    cont = box(ax, 2, y, 96, h, fc=fc, ec=ec or fc, lw=lw)
    body(ax, cont, text, top=top, size=size, color=color, ha="center",
         weight=weight, style=style)
    return cont


def check(fig, name):
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    mine = [c for c in CHECKS if c[0].figure is fig]
    problems = []
    boxes = []
    for ax, t, cont, label in mine:
        bb = t.get_window_extent(renderer=rend)
        x, y, w, h = cont
        X0, Y0 = ax.transData.transform((x, y))
        X1, Y1 = ax.transData.transform((x + w, y + h))
        m = 3  # pixels of breathing room at dpi 200
        if bb.x0 < X0 + m or bb.x1 > X1 - m or bb.y0 < Y0 + m or bb.y1 > Y1 - m:
            problems.append(f"  OUTSIDE {label!r}: text {bb.x0:.0f},{bb.y0:.0f}-"
                            f"{bb.x1:.0f},{bb.y1:.0f} box {X0:.0f},{Y0:.0f}-{X1:.0f},{Y1:.0f}")
        boxes.append((label, bb))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][1], boxes[j][1]
            if a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1:
                problems.append(f"  OVERLAP {boxes[i][0]!r} with {boxes[j][0]!r}")
    print(name, "OK" if not problems else "PROBLEMS")
    for p in problems:
        print(p)


def save(fig, name):
    check(fig, name)
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.12,
                facecolor=PALE)
    plt.close(fig)


# ---------------------------------------------------------------- Figure 1
def fig1():
    fig, ax = new_fig(4.6)
    title(ax, "The Six Limbs of the Veda: Tools for Fixing What a Term Means")
    free_text(ax, 50, 93.0,
              "śikṣā kalpo vyākaraṇaṁ niruktaṁ chando jyotiṣam   (cf. Muṇḍaka Upaniṣad 1.1.5)",
              (1, 0, 98, 100), size=7.2, style="italic")
    cells = [
        ("Śikṣā · phonetics",
         "The training in phonetics:\nhow to pronounce."),
        ("Kalpa · execution",
         "How to execute it: the\nprocedure of the rite."),
        ("Vyākaraṇa · analysis",
         "vi + ākaraṇa: the analysis of a\nterm, any meaningful sound\nunit — not just \"grammar\".\n\n"
         "\"He must come before he dies\":\ndictionary meaning versus the\nmeaning of the phrase."),
        ("Nirukta · etymology",
         "The back-history of a word:\nhow it was born and came\ninto use.\n\n"
         "parisphuraṇa → phaḍphaḍānā\nJagannātha → \"juggernaut\""),
        ("Chandas · metre",
         "Gāyatrī 3 × 8 = 24 syllables;\nanuṣṭubh 32.\n\n"
         "daivoddhāra-prayatnātmā: 8.\n\"dīvo dharyo pretnā ātmā\"\nbreaks the metre, and a ghost\nstory grows to explain it."),
        ("Jyotiṣa · astronomy",
         "Astronomy, not astrology:\nwhich work should be done\nat what time."),
    ]
    xs = [2, 35, 68]
    rows = [(56, 33), (20, 33)]
    for i, (hd, tx) in enumerate(cells):
        r, c = divmod(i, 3)
        y, h = rows[r]
        cont = box(ax, xs[c], y, 30, h)
        header(ax, cont, hd)
        body(ax, cont, tx, top=7.0)
    banner(ax, 4, 12,
           "Without these six the meaning of the Veda is not understood; the same tools serve the Gītā,\n"
           "the Brahmasūtra and the Bhāgavata — and law and science too (the \"God particle\").",
           size=7.0, top=2.6)
    save(fig, "fig1_vedangas.png")


# ---------------------------------------------------------------- Figure 2
def fig2():
    fig, ax = new_fig(4.8)
    title(ax, "Purāṇa and Veda: Two Presumptions")
    left = box(ax, 2, 44, 46, 46, fc=SAND, ec=TEAL)
    header(ax, left, "Modern Indology")
    body(ax, left,
         "The Veda came first; the Purāṇas\nappeared later.\n\n"
         "A monotheist lens (one God, in heaven):\nwhere many devatās appear, something\nseems to have gone wrong.\n\n"
         "Hence a somewhat negative view of\nthe Purāṇas.", top=7.0)
    right = box(ax, 52, 44, 46, 46, fc=PALE, ec=MAROON, lw=1.8)
    header(ax, right, "The tradition (the speaker's approach)", color=MAROON)
    body(ax, right,
         "The Purāṇa came first, as the concept;\nthe Veda is its verbal outlet.\n\n"
         "When the Veda grew hard to understand,\nthe concept was revealed again — so the\n"
         "Veda's language is older, the Purāṇa's\nnewer.\n\n"
         "purāṇaṁ hṛdayam: a thing comes first\nin the heart as a framework; speech\nthen plasters and paints it.",
         top=7.0)
    mid = box(ax, 2, 22, 96, 18, fc=SAND, ec=TEAL)
    header(ax, mid, "The analogy: constitution and preamble")
    body(ax, mid,
         "The preamble stands before the constitution, yet it is consulted only when interpreting\n"
         "the constitution becomes difficult: prior as concept, brought forward when needed.",
         top=7.0, ha="center")
    banner(ax, 3, 15,
           "The inquiry is not which came first. It is: if the Purāṇa belongs to the literature of the Veda,\n"
           "is its coordination (ekavākyatā) with the Veda necessary — and by what criterion?",
           size=7.0, top=3.6)
    save(fig, "fig2_purana_preamble.png")


# ---------------------------------------------------------------- Figure 3
def fig3():
    fig, ax = new_fig(5.0)
    title(ax, "Thesis, Antithesis, Synthesis: Karma, Jñāna, Bhakti")
    free_text(ax, 50, 93.4,
              "Hegel: all progress runs in a three-tier cycle, each synthesis becoming a new thesis",
              (1, 0, 98, 100), size=7.0, style="italic")
    xs = [2, 35, 68]
    for x, lab in zip(xs, ["THESIS", "ANTITHESIS", "SYNTHESIS"]):
        free_text(ax, x + 15, 88.6, lab, (x, 85.5, 30, 4.5), size=7.6, color=OCHRE,
                  weight="bold")
    marx = [("Feudalism", "Whoever holds the stick\nowns the buffalo."),
            ("Capitalism", "Power with whoever holds\ncapital and production."),
            ("Socialism", "Capital in the hands of the\npublic, not one individual.")]
    for x, (hd, tx) in zip(xs, marx):
        cont = box(ax, x, 70.5, 30, 14, fc=PALE, ec=GREY, lw=0.8)
        header(ax, cont, "Marx: " + hd, color=GREY, size=7.4, off=1.6)
        body(ax, cont, tx, top=5.6, size=6.5, color=GREY)
    for x in (32, 65):
        arrow(ax, x + 0.3, 77.5, x + 2.7, 77.5, color=GREY, lw=1.0, ms=7)
    main = [
        ("Karma-yoga", TEAL, TEAL, 1.0, SAND,
         "For the desirous (kāminām):\nfulfil desire — not any way\nyou like, but by the\nprescribed course.\n\n"
         "The deva serves the rite:\ndevaḥ karmārthaḥ."),
        ("Jñāna-yoga", TEAL, TEAL, 1.0, SAND,
         "For the disenchanted\n(nirviṇṇa): understand that\neverything depends on\neverything else.\n\n"
         "The rite is negated and no\ndeva appears: nothing to do,\nonly to understand."),
        ("Bhakti-yoga", MAROON, MAROON, 1.8, PALE,
         "Neither disenchanted nor\nover-attached: a balance of\nattachment and detachment.\n\n"
         "The rite serves the deva:\nkarma for the devatā. The\nPurāṇas teach it deva by deva."),
    ]
    for x, (hd, hc, ec, lw, fc, tx) in zip(xs, main):
        cont = box(ax, x, 27, 30, 39, fc=fc, ec=ec, lw=lw)
        header(ax, cont, hd, color=hc, size=9)
        body(ax, cont, tx, top=7.4)
    for x in (32, 65):
        arrow(ax, x + 0.2, 46.5, x + 2.8, 46.5, lw=1.6, ms=10)
    banner(ax, 2, 21,
           "nirviṇṇānāṁ jñānayogo … karmayogas tu kāminām … na nirviṇṇo nātisakto bhaktiyogo 'sya siddhidaḥ\n"
           "(Bhāgavata Purāṇa 11.20.7–8)\n\n"
           "In synthesis, thesis and antithesis combine — \"a cocktail\".\n"
           "So the Purāṇa teaches tattva and practice as one.",
           fc=SAND, ec=OCHRE, color=INK, size=6.9, top=2.6, lw=1.2)
    save(fig, "fig3_dialectic.png")


# ---------------------------------------------------------------- Figure 4
def fig4():
    fig, ax = new_fig(5.0)
    title(ax, "Primacy by Identification with Brahman")
    top = box(ax, 10, 80, 80, 11, fc=SAND, ec=TEAL)
    header(ax, top, "Brahman", size=9)
    body(ax, top, "All devas are born from Brahman; as devas (devatvena) they are all equal.",
         top=6.4, ha="center")
    panels = [("Viṣṇu Purāṇa", "Viṣṇu", ("Śiva", "Devī")),
              ("Śiva Purāṇa", "Śiva", ("Viṣṇu", "Devī")),
              ("Devī Purāṇa", "Devī", ("Śiva", "Viṣṇu"))]
    for x, (hd, centre, others) in zip([2, 35, 68], panels):
        arrow(ax, x + 15, 79.6, x + 15, 74.4, lw=1.3, ms=8)
        p = box(ax, x, 36, 30, 38, fc=PALE, ec=TEAL)
        header(ax, p, hd, size=8.2)
        c = box(ax, x + 5, 52, 20, 12, fc=SAND, ec=MAROON, lw=1.6)
        free_text(ax, x + 15, 62.2, centre, c, size=8.6, color=MAROON, weight="bold")
        free_text(ax, x + 15, 58.0, "taken as Brahman:\nthe centre", c, size=6.3, color=INK)
        for k, other in enumerate(others):
            ox = x + 1.5 + 14 * k
            o = box(ax, ox, 39, 13, 8.5, fc=SAND, ec=GREY, lw=0.8)
            free_text(ax, ox + 6.5, 46.0, other, o, size=7.0, color=TEAL, weight="bold")
            free_text(ax, ox + 6.5, 43.0, "his bhakta", o, size=6.2, color=INK)
            arrow(ax, ox + 6.5, 47.7, x + 15 + (k - 0.5) * 6, 51.4, color=GREY, lw=0.9, ms=6)
    analog = [("Mother and father", "Each teaches the child to\nrespect the other; neither\nsays \"respect me\"."),
              ("The cricket captain", "The other ten play under the\ncaptain — until another is\nmade captain."),
              ("Turns on the camel", "The villagers salute whoever\nhappens to be riding when\nthey arrive.")]
    for x, (hd, tx) in zip([2, 35, 68], analog):
        cont = box(ax, x, 14, 30, 19, fc=SAND, ec=OCHRE)
        header(ax, cont, hd, color=OCHRE, size=8)
        body(ax, cont, tx, top=6.4, size=6.6)
    banner(ax, 2, 9,
           "Subordination is voluntary, not factual: the team work of the devatās to explain Brahman.",
           fc=PALE, ec=MAROON, color=MAROON, size=7.3, top=3.0, lw=1.8, weight="bold")
    save(fig, "fig4_primacy.png")


# ---------------------------------------------------------------- Figure 5
def fig5():
    fig, ax = new_fig(5.6)
    title(ax, "Kārikā 12 and the Prakāśa: From Contradiction to Ekavākyatā")
    k = box(ax, 2, 84, 96, 8, fc=PALE, ec=MAROON, lw=1.6)
    body(ax, k,
         "sūryādirūpadhṛg brahmakāṇḍe jñānāṅgam īryate | purāṇeṣv api sarveṣu tattadrūpo haris tathā ||",
         top=2.4, ha="center", size=7.3, color=MAROON, style="italic")
    a = box(ax, 2, 67, 45, 12.5)
    header(ax, a, "1 · The doubt (āśaṅkā)", size=8)
    body(ax, a, "Veda and Purāṇa at times propound otherwise:\nkarma here, Brahman there, a deva elsewhere.",
         top=5.8, size=6.6)
    b = box(ax, 53, 67, 45, 12.5)
    header(ax, b, "2 · The answer", size=8)
    body(ax, b, "They are aṅgas: read them by their\nintention (abhiprāya).", top=5.8, size=6.6)
    arrow(ax, 47.4, 73.2, 52.6, 73.2)
    arrow(ax, 75.5, 83.6, 75.5, 79.9, lw=1.0, ms=7)
    c = box(ax, 2, 37, 45, 25)
    header(ax, c, "3 · Brahma-kāṇḍa: sūryādirūpadhṛk", size=8)
    body(ax, c,
         "Hari in the forms of Sūrya and the rest is\nan auxiliary of knowledge: upāsanā for\njñāna-siddhi.\n\n"
         "Some hold: upāsanā → citta-śuddhi →\nbrahma-jñāna (an impasse, says the\nspeaker).",
         top=6.0, size=6.6)
    d = box(ax, 53, 37, 45, 25, fc=PALE, ec=MAROON, lw=1.8)
    header(ax, d, "4 · Purāṇas: tattadrūpo hariḥ", color=MAROON, size=8)
    body(ax, d,
         "Hari is in each Purāṇa's deity.\n\n"
         "Mahāprabhuji's siddhānta: the deity gives a\nfruit → māhātmya-jñāna → bhakti → uplift.\n\n"
         "phaladāna-dvārā … bhakti-dvārā iti siddhāntaḥ",
         top=6.0, size=6.6)
    arrow(ax, 70, 66.6, 26, 62.4, lw=1.1, ms=8)
    arrow(ax, 77, 66.6, 77, 62.4, lw=1.1, ms=8)
    e = box(ax, 2, 19, 96, 13)
    header(ax, e, "5 · Viśiṣṭa-śeṣatva", size=8)
    body(ax, e,
         "Durgā, Gaṇapati and the rest stand as āvaraṇa-devatās around the one in the centre;\n"
         "yet not bhinnārtha, for centre and corner alike are Hari.",
         top=5.8, size=6.7, ha="center")
    arrow(ax, 24.5, 36.6, 30, 32.4, lw=1.1, ms=8)
    arrow(ax, 75.5, 36.6, 70, 32.4, lw=1.1, ms=8)
    f = box(ax, 2, 2, 96, 13, fc=SAND, ec=MAROON, lw=1.8)
    header(ax, f, "6 · Ekavākyatā", color=MAROON, size=8.2)
    body(ax, f, "sādhana-rūpaḥ phala-rūpaś ca svayam eva — He is the means and He is the fruit.",
         top=5.6, size=6.9, ha="center", color=MAROON)
    body(ax, f, "Next session: kārikā 23, prapañco bhagavat-kāryaḥ …",
         top=9.4, size=6.4, ha="center", color=GREY, style="italic")
    arrow(ax, 50, 18.6, 50, 15.4, lw=1.1, ms=8)
    save(fig, "fig5_karika12.png")


# ---------------------------------------------------------------- Figure 6
def fig6():
    fig, ax = new_fig(5.4)
    title(ax, "The Upāsanā Dilemma and the Ghāṭ")
    t = box(ax, 18, 82, 64, 10)
    header(ax, t, "Brahman is everywhere", size=8.5)
    body(ax, t, "unlimited by space, time and thing (deśa-kāla-vastu-aparicchinna)",
         top=5.6, ha="center", size=6.8)
    q = box(ax, 30, 69.5, 40, 7.5, fc=PALE, ec=OCHRE, lw=1.4)
    free_text(ax, 50, 75.0, "Is the upāsaka Brahman?", q, size=8.2, color=OCHRE, weight="bold")
    arrow(ax, 50, 81.6, 50, 77.4)
    yes = box(ax, 4, 52, 40, 12.5)
    header(ax, yes, "If yes", size=8)
    body(ax, yes, "Brahman has no need of\nBrahman's upāsanā.", top=5.6, ha="center")
    no = box(ax, 56, 52, 40, 12.5)
    header(ax, no, "If no", size=8)
    body(ax, no, "Brahman is not everywhere:\nthen it is not Brahman.", top=5.6, ha="center")
    arrow(ax, 38, 69.2, 26, 64.9)
    arrow(ax, 62, 69.2, 74, 64.9)
    aside = box(ax, 10, 38.5, 80, 9.5, fc=PALE, ec=GREY, lw=0.8, ls="--")
    body(ax, aside,
         "upa-āsana = sitting near, in front of — but in front of what is everywhere?\n"
         "(Dracula could come from any side: reading with one's back to the wall.)",
         top=2.2, ha="center", size=6.6, color=GREY, style="italic")
    xs = np.linspace(4, 96, 200)
    upper = 30.5 + 1.0 * np.sin(xs / 7.0)
    lower = 21.0 + 1.0 * np.sin(xs / 7.0 + 0.8)
    ax.add_patch(Polygon(np.column_stack([np.r_[xs, xs[::-1]], np.r_[upper, lower[::-1]]]),
                         closed=True, fc=TEAL, ec=TEAL, alpha=0.20, lw=0))
    ax.plot(xs, upper, color=TEAL, lw=1.0)
    ax.plot(xs, lower, color=TEAL, lw=1.0)
    river = (4, 20, 92, 12)
    free_text(ax, 9, 27.6, "Gaṅgā", river, size=8.4, color=TEAL, style="italic",
              weight="bold", ha="left")
    ghats = [(26, "Ṛṣikeś"), (42, "Haridvār"), (60, "Prayāg"), (78, "Kāśī")]
    for gx, name in ghats:
        uy = 30.5 + 1.0 * np.sin(gx / 7.0)
        chosen = name == "Kāśī"
        ax.add_patch(FancyBboxPatch((gx - 1.6, uy - 2.2), 3.2, 2.4,
                                    boxstyle="round,pad=0.012,rounding_size=0.4",
                                    fc=MAROON if chosen else OCHRE, ec="none"))
        free_text(ax, gx, 35.6, name, (gx - 7, 32.4, 14, 4.2), size=6.6,
                  color=MAROON if chosen else INK, weight="bold" if chosen else "normal")
    free_text(ax, 4.5, 19.3, "Gaṅgotrī", (3, 15, 14, 5), size=6.4, ha="left")
    free_text(ax, 95.5, 19.3, "Gaṅgāsāgar", (82, 15, 15, 5), size=6.4, ha="right")
    free_text(ax, 60, 19.3, "the chosen ghāṭ: one deva identified with Brahman  ↗",
              (30, 15, 50, 5), size=6.4, color=MAROON, style="italic")
    banner(ax, 2, 11.5,
           "Select one ghāṭ: one deva identified with Brahman, the other devas subordinate to him.\n"
           "Bathe in the Gaṅgā at the ghāṭ, not in the ghāṭ — and you bathe in the whole Gaṅgā.",
           fc=SAND, ec=MAROON, color=MAROON, size=7.0, top=2.4, lw=1.8)
    save(fig, "fig6_upasana_ghat.png")


# ---------------------------------------------------------------- Figure 7
def fig7():
    fig, ax = new_fig(5.6)
    title(ax, "Two Routes from Upāsanā")
    lh = box(ax, 2, 81.5, 44, 6.6, fc=PALE, ec=TEAL)
    header(ax, lh, "Citta-śuddhi first (as some hold)", size=8.4, off=1.6)
    rh = box(ax, 54, 81.5, 44, 6.6, fc=PALE, ec=MAROON, lw=1.8)
    header(ax, rh, "Mahāprabhuji: phala-dāna-dvārā", color=MAROON, size=8.4, off=1.6)
    left = [("Upāsanā", "worship of the chosen deity", 68),
            ("Citta-śuddhi", "the mind stops wandering", 56),
            ("Brahma-jñāna", "Brahman understood by itself", 44)]
    for hd, tx, y in left:
        c = box(ax, 6, y, 36, 8.5)
        header(ax, c, hd, size=7.8, off=1.4)
        body(ax, c, tx, top=4.8, ha="center", size=6.5)
    for y in (68, 56):
        arrow(ax, 24, y - 0.4, 24, y - 3.1)
    arrow(ax, 24, 81.1, 24, 76.9, color=GREY, lw=1.0, ms=7)
    imp = box(ax, 2, 15.5, 44, 23, fc=PALE, ec=OCHRE, lw=1.4)
    header(ax, imp, "The impasse", color=OCHRE, size=8.2)
    body(ax, imp,
         "No pure citta, no deity; and our citta\ndoes not purify itself. The initiative\nwould be ours.",
         top=6.0, size=6.6)
    body(ax, imp,
         "The pujārī asleep, feet towards Viśvanātha;\nthe hundred-rupee cradle in Gokul.",
         top=15.4, size=6.3, color=GREY, style="italic")
    arrow(ax, 24, 43.6, 24, 38.9, color=OCHRE, lw=1.0, ms=7)
    right = [("The deity accepts us", "\"as is where is\", by its own power", 69, False),
             ("It gives some fruit", "experiential, behavioural, external", 58, False),
             ("Māhātmya-jñāna", "the deity's greatness is grasped", 47, False),
             ("Bhakti", "firm love, greater than all else", 36, False),
             ("Uddhāra", "uplift: Brahman is attained", 25, True)]
    for hd, tx, y, last in right:
        c = box(ax, 58, y, 36, 8.5, fc=PALE if last else SAND,
                ec=MAROON if last else TEAL, lw=1.6 if last else 1.0)
        header(ax, c, hd, size=7.8, off=1.4, color=MAROON if last else TEAL)
        body(ax, c, tx, top=4.8, ha="center", size=6.5)
    for y in (69, 58, 47, 36):
        arrow(ax, 76, y - 0.4, 76, y - 2.1)
    arrow(ax, 76, 81.1, 76, 77.9, color=GREY, lw=1.0, ms=7)
    free_text(ax, 76, 23.2, "Śabarī, Śiśupāla, even Rāvaṇa: the power is the deity's",
              (55, 17, 42, 6.5), size=6.3, style="italic")
    banner(ax, 2, 11,
           "Condition (Bālabodha): ananyāśraya and ananyāsakti towards the deity one holds —\n"
           "said there of Śiva as well as Viṣṇu, because Brahman alone is such.",
           size=7.0, top=2.4)
    save(fig, "fig7_two_routes.png")


# ---------------------------------------------------------------- Figure 8
def fig8():
    fig, ax = new_fig(5.2)
    title(ax, "Centre and Corners: The Āvaraṇa-devatās Move with Bhakti")
    grids = [("Devotee of Mahādeva", "Mahādeva", ["Pārvatī", "Viṣṇu", "Gaṇapati", "Sūrya"]),
             ("Devotee of Viṣṇu", "Viṣṇu", ["Mahādeva", "Pārvatī", "Gaṇapati", "Sūrya"]),
             ("Devotee of Gaṇapati", "Gaṇapati", ["Mahādeva", "Pārvatī", "Viṣṇu", "Sūrya"])]
    cw, ch, gap = 9.1, 10.4, 0.5
    for x0, (hd, centre, corners) in zip([3, 36, 69], grids):
        frame = box(ax, x0 - 1, 46, 29.8, 44.5, fc=PALE, ec=GREY, lw=0.7)
        header(ax, frame, hd, size=7.8, off=1.6)
        ys = [77.6, 66.2, 54.8]  # row anchors: cell bottom = anchor - 6.6
        corner_cells = [(0, 0), (0, 2), (2, 0), (2, 2)]
        for (r, c), name in zip(corner_cells, corners):
            cx, cy = x0 + c * (cw + gap), ys[r] - 6.6
            cell = box(ax, cx, cy, cw, ch, fc=SAND, ec=TEAL, lw=0.9)
            free_text(ax, cx + cw / 2, cy + ch / 2, name, cell, size=6.1, color=TEAL, va="center")
        for (r, c) in [(0, 1), (1, 0), (1, 2), (2, 1)]:
            cx, cy = x0 + c * (cw + gap), ys[r] - 6.6
            box(ax, cx, cy, cw, ch, fc="none", ec=GREY, lw=0.5, ls=":")
        cx, cy = x0 + (cw + gap), ys[1] - 6.6
        cell = box(ax, cx, cy, cw, ch, fc=PALE, ec=MAROON, lw=1.7)
        free_text(ax, cx + cw / 2, cy + ch / 2, centre, cell, size=6.2, color=MAROON,
                  weight="bold", va="center")
    left = box(ax, 2, 15, 59, 26, fc=PALE, ec=MAROON, lw=1.8)
    header(ax, left, "tattadrūpo hariḥ", color=MAROON, size=8.5)
    body(ax, left,
         "The one in the centre is Bhagavān, and the ones in the\ncorners are Bhagavān: no quarrel over the centre\n"
         "(viśiṣṭa-śeṣatva, not bhinnārtha).\n\n"
         "If you are Gaṇapati's devotee, Gaṇapati comes to the\nmiddle — not because he wants the centre, but\n"
         "because your bhakti is happening in that form.",
         top=6.2, size=6.6)
    kite = box(ax, 64, 15, 34, 26, fc=SAND, ec=TEAL)
    header(ax, kite, "The kite and the string", size=8.2)
    body(ax, kite,
         "The devas are kites, flying\nhigher than you can reach;\nyour bhakti is the string.\n\n"
         "Hold the string, not the kite.",
         top=6.2, size=6.6)
    banner(ax, 2, 9,
           "Smārta pañcadeva-upāsanā: the iṣṭa-deva in the middle, four āvaraṇa-devatās in the corners.",
           fc=SAND, ec=TEAL, color=TEAL, size=7.0, top=3.0)
    save(fig, "fig8_centre_corners.png")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        f()
