#!/usr/bin/env python3
"""Figures for Śāstrārtha Prakaraṇa, Lecture 1 (session of 2026-07-11).

Run from anywhere: writes PNGs into figs01/ next to this script.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch  # noqa: E402

plt.rcParams["font.family"] = "DejaVu Sans"

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"

OUT = Path(__file__).resolve().parent / "figs01"
OUT.mkdir(exist_ok=True)


def canvas(height):
    fig = plt.figure(figsize=(6.2, height))
    fig.patch.set_facecolor(PALE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.set_facecolor(PALE)
    return fig, ax


def rbox(ax, x, y, w, h, edge=TEAL, fill=SAND, lw=1.1, ls="-", z=1):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.012", linewidth=lw,
            edgecolor=edge, facecolor=fill, linestyle=ls, zorder=z,
        )
    )


def head(ax, x, y, text, color=TEAL, size=8.6, style="normal", weight="bold"):
    ax.text(x, y, text, ha="center", va="center", fontsize=size, color=color,
            weight=weight, style=style, zorder=4)


def body(ax, x, y, text, size=6.8, color=INK, ha="left", style="normal", ls=1.38):
    ax.text(x, y, text, ha=ha, va="top", fontsize=size, color=color,
            linespacing=ls, style=style, zorder=4)


def title(ax, text, y=96.0, size=12.0):
    ax.text(50, y, text, ha="center", va="center", fontsize=size, color=INK,
            weight="bold", zorder=4)


def banner(ax, text, y, h, edge=OCHRE, fill=SAND, size=7.2, color=INK, style="normal"):
    rbox(ax, 2, y, 96, h, edge=edge, fill=fill, lw=1.3)
    ax.text(50, y + h / 2, text, ha="center", va="center", fontsize=size,
            color=color, linespacing=1.35, style=style, zorder=4)


def arrow(ax, x1, y1, x2, y2, color=OCHRE, lw=1.4, rad=0.0, ms=11):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=ms, color=color,
            lw=lw, connectionstyle=f"arc3,rad={rad}", zorder=3,
            shrinkA=0, shrinkB=0,
        )
    )


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.12,
                facecolor=PALE)
    plt.close(fig)


# ---------------------------------------------------------------- Figure 1
def fig1():
    fig, ax = canvas(5.0)
    title(ax, "Five kinds of grantha, and the prakriyā-grantha as the “manual”")

    kinds = ["vyākhyā", "vāda", "prakaraṇa", "stuti", "prakriyā"]
    w, gap, x0 = 17.6, 2.0, 2.0
    for i, k in enumerate(kinds):
        x = x0 + i * (w + gap)
        last = k == "prakriyā"
        rbox(ax, x, 74, w, 14, edge=MAROON if last else TEAL,
             fill=SAND if last else PALE, lw=1.6 if last else 1.0)
        head(ax, x + w / 2, 84.6, k, color=MAROON if last else TEAL, size=8.8)
        if last:
            body(ax, x + w / 2, 81.2, "how to “operate”\na siddhānta", size=6.5,
                 ha="center")
        else:
            body(ax, x + w / 2, 81.2, f"{k}-rūpa", size=6.5, color=GREY, ha="center",
                 style="italic")

    # left: other schools
    rbox(ax, 2, 20, 46, 49, edge=TEAL, fill=SAND)
    head(ax, 25, 65.2, "Prakriyā-granthas across the schools", color=TEAL, size=8.4)
    body(ax, 4, 61.0,
         "Jaina — the most: some twenty\n"
         "Bauddha — few: the school split into nineteen\n"
         "Advaita — Vedāntasāra, Vedāntaparibhāṣā,\n"
         "     Siddhāntaleśasaṅgraha; Madhusūdana Sarasvatī\n"
         "Mādhva — Madhva's Tattvasaṅkhyāna, Tattvaviveka (?)\n"
         "Rāmānuja's school — later works, none by\n"
         "     Rāmānuja himself; Yāmuna's Siddhitraya\n"
         "Kashmir Śaivism — Paramārthasāra and others",
         size=6.7, ls=1.62)
    body(ax, 25, 29.0, "a listener: “In Nyāya?” — “They are not found.”", size=6.5,
         ha="center", color=GREY, style="italic")

    # right: the Śuddhādvaita line
    rbox(ax, 52, 20, 46, 49, edge=MAROON, fill=PALE, lw=1.2)
    head(ax, 75, 65.2, "The Śuddhādvaita line", color=MAROON, size=8.4)
    line = [
        ("Mahāprabhuji · Tattvārthadīpanibandha", "Śāstrārtha Prakaraṇa: the root of all", True),
        ("Lālū Bhaṭṭa", "Prameyaratnārṇava (title restored)", False),
        ("Giridharajī of Kāśī", "Śuddhādvaitamārtaṇḍa", False),
        ("Gaṭṭūlālajī", "“Pañcadarśī” (title as heard)", False),
    ]
    by, bh, bstep = 53.5, 8.4, 10.4
    for i, (who, what, root) in enumerate(line):
        y = by - i * bstep
        rbox(ax, 55, y, 40, bh, edge=MAROON if root else TEAL,
             fill=SAND, lw=1.6 if root else 0.9)
        head(ax, 75, y + bh - 2.6, who, color=MAROON if root else TEAL, size=7.0)
        body(ax, 75, y + bh - 4.6, what, size=6.5, ha="center", style="italic")
        if i < len(line) - 1:
            arrow(ax, 75, y - 0.2, 75, y - bstep + bh + 0.4, ms=8, lw=1.1)

    banner(ax,
           "The speaker's analogies: the manual that comes with the machine · the ālāpacārī "
           "before the song ·\na panoramic view of a location · the prologue of a book · "
           "the preamble of a constitution",
           y=3, h=12, size=6.9)
    save(fig, "fig1_prakriya.png")


# ---------------------------------------------------------------- Figure 2
def fig2():
    fig, ax = canvas(4.6)
    title(ax, "The Śāstrārtha Prakaraṇa as this course reads it")
    ax.text(50, 88.5,
            "about 104 ślokas · selection: jaḍa, jīva, Īśvara, paramata-nirākaraṇa · "
            "the syllabus enters at the sixth śloka",
            ha="center", va="center", fontsize=7.0, color=GREY, style="italic")

    w, gap, x0 = 21.5, 3.0, 2.5
    xs = [x0 + i * (w + gap) for i in range(4)]
    top_y, bot_y, h = 58.0, 26.0, 22.0
    top = [
        ("Maṅgalācaraṇa", "and four more ślokas:\ndropped from the\nsyllabus, explained\norally today", GREY, PALE, "--"),
        ("Svamata", "pramāṇa, prameya,\nsādhana, phala —\nbeginning with the\nparibhāṣā (today)", MAROON, SAND, "-"),
        ("Pramāṇa", "pramāṇa-vyavasthā;\nrefutation of doubts\n(from next session)", TEAL, SAND, "-"),
        ("Prameya", "jaḍa and jīva;\nBhagavān's māyā;\nthe jīva; jagat (jaḍa);\nantaryāmin, ānandāṁśa", TEAL, SAND, "-"),
    ]
    bottom = [
        ("Saṁsāra", "how it becomes\nmanifest to the\njīvātman; the mode\nof its cessation", TEAL, SAND, "-"),
        ("Brahman", "the exposition of\nBrahman's svarūpa", TEAL, SAND, "-"),
        ("Phala", "the vyavasthā of\nphala according to\nour own view", TEAL, SAND, "-"),
        ("Upasaṁhāra", "the close of the\nŚāstrārtha Prakaraṇa", TEAL, SAND, "-"),
    ]
    for i, (hd, bd, col, fill, ls) in enumerate(top):
        rbox(ax, xs[i], top_y, w, h, edge=col, fill=fill, ls=ls,
             lw=1.6 if col == MAROON else 1.0)
        head(ax, xs[i] + w / 2, top_y + h - 3.6, hd, color=col, size=8.2)
        body(ax, xs[i] + 1.6, top_y + h - 7.6, bd, size=6.6)
    # bottom row runs right to left: Saṁsāra sits under Prameya
    for j, (hd, bd, col, fill, ls) in enumerate(bottom):
        i = 3 - j
        rbox(ax, xs[i], bot_y, w, h, edge=col, fill=fill, ls=ls)
        head(ax, xs[i] + w / 2, bot_y + h - 3.6, hd, color=col, size=8.2)
        body(ax, xs[i] + 1.6, bot_y + h - 7.6, bd, size=6.6)
    for i in range(3):
        arrow(ax, xs[i] + w + 0.3, top_y + h / 2, xs[i + 1] - 0.3, top_y + h / 2, ms=9)
        arrow(ax, xs[3 - i] - 0.3, bot_y + h / 2, xs[2 - i] + w + 0.3, bot_y + h / 2, ms=9)
    arrow(ax, xs[3] + w / 2, top_y - 0.3, xs[3] + w / 2, bot_y + h + 0.3, ms=9)

    banner(ax,
           "Not everything is taken: the aim is the salient features of the siddhānta,\n"
           "and a “taste” of Mahāprabhuji's thought process and style of explanation",
           y=4, h=12, size=6.9)
    save(fig, "fig2_plan.png")


# ---------------------------------------------------------------- Figure 3
def fig3():
    fig, ax = canvas(4.0)
    title(ax, "“This” and “that”: four grades of distance from the seer")

    # the seer
    ax.add_patch(Circle((6.5, 58), 2.6, facecolor=SAND, edgecolor=INK, lw=1.0, zorder=3))
    ax.add_patch(Circle((6.5, 58), 1.0, facecolor=INK, edgecolor=INK, zorder=4))
    body(ax, 6.5, 51.5, "draṣṭā\n(the seer)", size=6.6, ha="center")

    zones = [
        (13.0, "etad", "samīpataravarti", "nearer still: what lies\nbetween the idam\nand the seer", "m. eṣaḥ · f. eṣā", TEAL),
        (34.0, "idam", "sannikṛṣṭa", "in sannikarṣa:\nwhat we are in\ncontact with", "m. ayam · f. iyam", TEAL),
        (55.0, "adas", "viprakṛṣṭa", "within the range of\nsight, but seen\nfrom far away", "m. asau · f. asau", TEAL),
        (79.0, "tad", "parokṣa", "beyond the horizon:\n“beyond the ken”\n(k-e-n, not c-a-n)", "tasmai bhagavate", MAROON),
    ]
    w, y0, h = 19.0, 31.0, 47.0
    for x, word, term, gloss, forms, col in zones:
        rbox(ax, x, y0, w, h, edge=col, fill=SAND, lw=1.6 if col == MAROON else 1.0)
        head(ax, x + w / 2, y0 + h - 4.4, word, color=col, size=10.0, style="italic")
        head(ax, x + w / 2, y0 + h - 10.6, term, color=col, size=6.9, weight="normal",
             style="italic")
        body(ax, x + 1.6, y0 + h - 15.6, gloss, size=6.6)
        ax.plot([x + 2, x + w - 2], [y0 + 11.6, y0 + 11.6], color=GREY, lw=0.5, zorder=4)
        body(ax, x + w / 2, y0 + 9.4, forms, size=6.6, ha="center",
             color=MAROON if col == MAROON else GREY, style="italic")

    # horizon
    ax.plot([76.0, 76.0], [26, 86], color=OCHRE, lw=1.3, ls=(0, (3, 2)), zorder=2)
    ax.text(76.0, 88.0, "horizon · the “ken”", ha="center", va="center", fontsize=6.6,
            color=OCHRE)
    arrow(ax, 13.0, 25.0, 97.0, 25.0, color=GREY, lw=0.9, ms=8)
    ax.text(55, 22.2, "farther from the seer", ha="center", va="center", fontsize=6.4,
            color=GREY, style="italic")

    banner(ax,
           "English, Hindi, Gujarati: only “this” and “that”.  Sanskrit grades the awareness.  "
           "Tasmai: Bhagavān is tat —\nunseen, so nothing can be done to him but namana.",
           y=3, h=13, size=6.9)
    save(fig, "fig3_demonstratives.png")


# ---------------------------------------------------------------- Figure 4
def fig4():
    fig, ax = canvas(4.8)
    title(ax, "The maṅgalācaraṇa: four pādas, four things", y=96.5)
    ax.text(50, 90.2,
            "namo bhagavate tasmai kṛṣṇāyādbhutakarmaṇe |  "
            "rūpanāmavibhedena jagat krīḍati yo yataḥ ||",
            ha="center", va="center", fontsize=7.6, color=MAROON, style="italic")

    w, gap, x0 = 22.5, 2.0, 2.0
    y0, h = 21.0, 63.0
    cols = [
        ("Pāda 1", "namo bhagavate tasmai",
         "tasmai, “to that”:\nBhagavān is tat —\nparokṣa, beyond the\nken\n\n"
         "to one unseen, only\nnamana is possible\n\n"
         "the wave: bend, and it\npasses over you; block\nit, and it throws you",
         "pramāṇa and\nsādhana"),
        ("Pāda 2", "kṛṣṇāyādbhutakarmaṇe",
         "Kṛṣṇa: God who\nbecomes man — the\nnirākāra takes the\nnarākāra, unbound\n\n"
         "adbhuta: wonder at\nthe periphery, śānta\nat the core\n\n"
         "many-faceted, as he\nenters the arena\n(Bhāgavata 10.43.17)",
         "prameya"),
        ("Pāda 3", "rūpa-nāma-vibhedena",
         "rūpa = the percept\n(material)\n\nnāma = the concept\n(mental)\n\n"
         "mind and matter:\nformally two,\nsubstantially one",
         "rūpa and nāma"),
    ]
    for i, (pada, frag, txt, verdict) in enumerate(cols):
        x = x0 + i * (w + gap)
        rbox(ax, x, y0, w, h, edge=MAROON, fill=SAND, lw=1.2)
        head(ax, x + w / 2, y0 + h - 3.6, pada, color=MAROON, size=8.6)
        head(ax, x + w / 2, y0 + h - 8.2, frag, color=MAROON, size=6.9, weight="normal",
             style="italic")
        body(ax, x + 1.5, y0 + h - 12.4, txt, size=6.5)
        rbox(ax, x + 1.5, y0 + 1.8, w - 3.0, 9.0, edge=OCHRE, fill=PALE, lw=1.0)
        ax.text(x + w / 2, y0 + 6.3, f"→ {verdict}", ha="center", va="center",
                fontsize=6.7, color=INK, weight="bold", linespacing=1.25, zorder=4)

    # column 4: threefold krīḍā
    x = x0 + 3 * (w + gap)
    rbox(ax, x, y0, w, h, edge=MAROON, fill=SAND, lw=1.2)
    head(ax, x + w / 2, y0 + h - 3.6, "Pāda 4", color=MAROON, size=8.6)
    head(ax, x + w / 2, y0 + h - 8.2, "jagat krīḍati yo yataḥ", color=MAROON, size=6.9,
         weight="normal", style="italic")
    kr = [
        ("yaḥ krīḍati", "beyond time\nand space"),
        ("yo jagad bhūtvā krīḍati", "within time\nand space"),
        ("yato jagat krīḍati", "in time, not in space:\nnāma without rūpa\n(dream, bhrama)"),
    ]
    ky, kh = [y0 + 39.0, y0 + 24.5, y0 + 8.0], [11.5, 11.5, 14.0]
    for (k, d), yy, hh in zip(kr, ky, kh):
        rbox(ax, x + 1.2, yy, w - 2.4, hh, edge=TEAL, fill=PALE, lw=0.9)
        head(ax, x + w / 2, yy + hh - 2.6, k, color=TEAL, size=6.1, style="italic")
        body(ax, x + w / 2, yy + hh - 4.9, d, size=6.4, ha="center")
    body(ax, x + w / 2, y0 + 7.0, "his līlā — not our\nignorance", size=6.4, ha="center",
         color=MAROON, style="italic")

    banner(ax,
           "“In a nutshell” Mahāprabhuji's whole panoramic view in one anuṣṭubh — dropped from "
           "the syllabus, explained orally",
           y=4, h=9, size=6.9)
    save(fig, "fig4_mangalacarana.png")


# ---------------------------------------------------------------- Figure 5
def fig5():
    fig, ax = canvas(5.0)
    title(ax, "Lakṣaṇa and pramāṇa: what definition and experience can do")

    # Europe
    rbox(ax, 2, 18, 46, 72, edge=TEAL, fill=SAND)
    head(ax, 25, 86.2, "Europe: one side at a time", color=TEAL, size=8.6)
    body(ax, 4, 82.0,
         "Rationalists: once defined, established —\n"
         "   but fairies can be defined; and “G-O-D”,\n"
         "   generator-operator-destroyer, fits any company\n"
         "Empiricists: once experienced, established —\n"
         "   but the fish in a round tub, or a straight one,\n"
         "   sees a biased view; the horizon is “pure illusion”",
         size=6.6, ls=1.42)
    steps = [
        ("sandehavāda, scepticism", "“everything is doubtful”"),
        ("agnosticism", "“we don't know what is reality”"),
        ("Kant", "inquire into the apparatus of understanding:\nmicroscope, telescope"),
    ]
    sy = [50.0, 37.0, 21.0]
    sh = [9.0, 9.0, 12.0]
    for (k, d), yy, hh in zip(steps, sy, sh):
        rbox(ax, 5, yy, 40, hh, edge=TEAL, fill=PALE, lw=0.9)
        head(ax, 25, yy + hh - 2.6, k, color=TEAL, size=6.9)
        body(ax, 25, yy + hh - 4.6, d, size=6.4, ha="center", style="italic")
    arrow(ax, 25, 49.8, 25, 46.3, ms=8, lw=1.1)
    arrow(ax, 25, 36.8, 25, 33.3, ms=8, lw=1.1)

    # Indian presumption
    rbox(ax, 52, 18, 46, 72, edge=MAROON, fill=SAND, lw=1.6)
    head(ax, 75, 86.2, "The Indian presumption", color=MAROON, size=8.6)
    head(ax, 75, 81.0, "lakṣaṇa-pramāṇābhyāṁ vastu-siddhiḥ", color=MAROON, size=7.2,
         weight="normal", style="italic")
    rbox(ax, 55, 58, 40, 18, edge=TEAL, fill=PALE, lw=0.9)
    head(ax, 75, 73.4, "lakṣaṇa (definition)", color=TEAL, size=7.0)
    body(ax, 57, 70.6,
         "makes the thing conceivable: only a\n"
         "probability — “it can be like this”\n"
         "to “de-finite” is to tag: an I-card shows\n"
         "the front only; always incomplete",
         size=6.4)
    rbox(ax, 55, 41, 40, 12, edge=TEAL, fill=PALE, lw=0.9)
    head(ax, 75, 50.4, "pramāṇa (verification)", color=TEAL, size=7.0)
    body(ax, 75, 47.6, "“it is so”: empirical verification", size=6.4, ha="center")
    body(ax, 75, 25.5, "“this is our limitation”, not the thing's", size=6.4,
         ha="center", color=GREY, style="italic")
    body(ax, 55.5, 37.5,
         "the two are complementary — “this is all\n"
         "what we can do”; to deny them is to say\n"
         "mama mātā vandhyā, “my mother is barren”",
         size=6.4)
    arrow(ax, 75, 57.8, 75, 53.3, ms=8, lw=1.1)

    banner(ax,
           "Mahāprabhuji denies neither the presumption nor its limitation — so he begins with "
           "paribhāṣā,\nwhich yields only probability; establishing is left to pramāṇa",
           y=3, h=11, edge=MAROON, size=6.9)
    save(fig, "fig5_laksana_pramana.png")


# ---------------------------------------------------------------- Figure 6
def fig6():
    fig, ax = canvas(5.0)
    title(ax, "The vicious circle of the pramāṇas")

    nodes = {
        "śabda": (50.0, 74.0, "word"),
        "anumāna": (77.0, 40.0, "inference"),
        "pratyakṣa": (23.0, 40.0, "perception"),
    }
    nw, nh = 20.0, 10.0
    for name, (cx, cy, eng) in nodes.items():
        rbox(ax, cx - nw / 2, cy - nh / 2, nw, nh, edge=TEAL, fill=SAND, lw=1.3)
        head(ax, cx, cy + 1.5, name, color=TEAL, size=9.0, style="italic")
        head(ax, cx, cy - 2.2, eng, color=INK, size=6.6, weight="normal")

    # arrows: A depends on B, drawn A -> B
    arrow(ax, 60.5, 71.0, 74.0, 45.5, rad=-0.25)   # śabda -> anumāna
    arrow(ax, 66.5, 37.0, 33.5, 37.0, rad=-0.25)   # anumāna -> pratyakṣa
    arrow(ax, 26.0, 45.5, 39.5, 71.0, rad=-0.25)   # pratyakṣa -> śabda

    # notes
    rbox(ax, 70, 66, 28, 16.5, edge=GREY, fill=PALE, lw=0.8)
    body(ax, 71.5, 80.6,
         "śabda rests on anumāna:\n"
         "word-meanings are inferred —\n"
         "“bring the pen”, “take the\n"
         "pen away”, “bring the cloth”",
         size=6.3)
    rbox(ax, 2, 66, 28, 16.5, edge=GREY, fill=PALE, lw=0.8)
    body(ax, 3.5, 80.6,
         "pratyakṣa rests on śabda:\n"
         "no concept without the word —\n"
         "na so 'sti pratyayo loke\n"
         "(Vākyapadīya); the thing seen\n"
         "but not named",
         size=6.3)
    rbox(ax, 31, 18.5, 38, 11, edge=GREY, fill=PALE, lw=0.8)
    body(ax, 50, 28.4,
         "anumāna rests on pratyakṣa: it needs the\n"
         "concomitance seen in perception (smoke, fire)",
         size=6.3, ha="center")
    rbox(ax, 2, 18.5, 27, 13, edge=GREY, fill=PALE, lw=0.8)
    body(ax, 3.5, 30.0,
         "and pratyakṣa is shaken:\n"
         "the plastic rose, House of\n"
         "Wax, doctored photos, AI",
         size=6.3)
    rbox(ax, 71, 18.5, 27, 13, edge=GREY, fill=PALE, lw=0.8)
    body(ax, 72.5, 30.0,
         "“a complete chaos” —\n"
         "man, “the most irrational\n"
         "animal” on the earth",
         size=6.3)
    for lx, ly in ((63.5, 56.0), (50.0, 35.2), (36.5, 56.0)):
        ax.text(lx, ly, "rests on", ha="center", va="center", fontsize=6.2,
                color=OCHRE, style="italic")
    ax.text(50, 49.5, "each leans\non another", ha="center", va="center", fontsize=6.8,
            color=OCHRE, style="italic", linespacing=1.3)

    banner(ax,
           "Yet there is no other apparatus.  “The complete reality is unknowable, but the "
           "reality is knowable —\nby its own initiative”: Brahman is known by all, fully by none.",
           y=3, h=11, edge=MAROON, size=6.9)
    save(fig, "fig6_vicious_circle.png")


# ---------------------------------------------------------------- Figure 7
def fig7():
    fig, ax = canvas(5.0)
    title(ax, "One vastu, three facets, three “tags”")

    cols = [
        ("Brahman", MAROON,
         ["a categorical term:\nby itself, in no relation",
          "“that which includes\neverything and excludes\nnothing”",
          "as “human being” covers\nhusband, father and\nson alike",
          "the tag in the\nŚāstrārtha Prakaraṇa",
          "its liṅga in the Vedānta"]),
        ("Paramātmā", TEAL,
         ["a relational term:\nconceptually dependent,\nnot substantially",
          "excludes jaḍa and jīva",
          "as “father” excludes the\nson; all ministers gone,\nstill “Prime Minister”",
          "the tag in the\nSarvanirṇaya Prakaraṇa",
          "its liṅga in the Gītā"]),
        ("Bhagavān", TEAL,
         ["relational: bhaga from\nbhaj, “the worshipable”",
          "substantially dependent\ntoo: bhakta and Bhagavān\nare correlata",
          "“Can there be a teacher\nwithout student?”",
          "the tag in the\nBhāgavatārtha Prakaraṇa",
          "its liṅga in the Bhāgavata"]),
    ]
    w, gap, x0 = 30.0, 3.0, 2.0
    y0, h = 29.0, 61.0
    rows_y = [81.0, 71.0, 59.5, 43.5, 35.3]
    for i, (name, col, rows) in enumerate(cols):
        x = x0 + i * (w + gap)
        rbox(ax, x, y0, w, h, edge=col, fill=SAND, lw=1.6 if col == MAROON else 1.0)
        head(ax, x + w / 2, y0 + h - 4.0, name, color=col, size=9.6, style="italic")
        for j, (txt, ry) in enumerate(zip(rows, rows_y)):
            colr = INK if j < 3 else (MAROON if j == 3 else GREY)
            body(ax, x + w / 2, ry, txt, size=6.6 if j != 2 else 6.4, ha="center",
                 color=GREY if j == 2 else colr,
                 style="italic" if j in (2, 4) else "normal")
        ax.plot([x + 3, x + w - 3], [46.5, 46.5], color=GREY, lw=0.5)

    ax.text(50, 23.5,
            "The paradox: the Śāstrārtha is the Gītārtha, and the Gītā's thrust is Paramātmā; "
            "here he treats\nthe facet of Paramātmā's being Brahman.",
            ha="center", va="center", fontsize=6.6, color=GREY, style="italic",
            linespacing=1.35)
    banner(ax,
           "brahmeti paramātmeti Bhagavān iti śabdyate — one vastu, not three: three words "
           "for one thing would be\nmere repetition (“Parsi, Bāvā, gāṇḍā”), so the three "
           "words name three facets",
           y=3, h=12, edge=MAROON, size=6.8)
    save(fig, "fig7_three_facets.png")


# ---------------------------------------------------------------- Figure 8
def fig8():
    fig, ax = canvas(5.0)
    title(ax, "The Gītā's chariot and the three “cells”")

    # left: the Gītā's format
    rbox(ax, 2, 18, 46, 72, edge=TEAL, fill=SAND)
    head(ax, 25, 86.2, "The Gītā's “format”", color=TEAL, size=8.6)
    rows = [
        ("ratha, the chariot", "the body", TEAL, 8.0),
        ("rathī, the rider", "the jīvātman — Arjuna, nara: “one who\ncan see”, aware of itself "
         "and of its world", TEAL, 12.0),
        ("sārathi, the charioteer", "Paramātmā — Kṛṣṇa, Nārāyaṇa: narāṇām\nayanam, the abode "
         "where all is unified,\n“a guiding principle”", MAROON, 14.5),
    ]
    ry = 81.5
    for k, d, col, hh in rows:
        yy = ry - hh
        rbox(ax, 5, yy, 40, hh, edge=col, fill=PALE, lw=1.4 if col == MAROON else 0.9)
        head(ax, 25, yy + hh - 2.6, k, color=col, size=7.0)
        body(ax, 25, yy + hh - 4.8, d, size=6.4, ha="center")
        ry = yy - 4.5
    body(ax, 25, 33.5,
         "nara: what was born in the nārā, the\n"
         "waters — the first living cell, at the\n"
         "seashore — in which awareness came",
         size=6.3, ha="center", color=GREY, style="italic")

    # right: three cells
    rbox(ax, 52, 18, 46, 72, edge=MAROON, fill=SAND, lw=1.6)
    head(ax, 75, 86.2, "Three kinds of “cell”", color=MAROON, size=8.6)
    cells = [
        ("divine cell (soul): the antaryāmin", "enters consciousness and governs it from\nwithin; "
         "we do not know him, he knows us", MAROON),
        ("conscious cell", "aware of its own self and of the external\nworld; the laboratory "
         "cannot make it\n(AI: only “mechanical”)", TEAL),
        ("living cell", "the metabolic process goes on: a coma\npatient is living, "
         "but not conscious", TEAL),
    ]
    cy = [68.5, 43.5, 21.0]
    ch = [12.5, 15.0, 12.5]
    for (k, d, col), yy, hh in zip(cells, cy, ch):
        rbox(ax, 55, yy, 40, hh, edge=col, fill=PALE, lw=1.4 if col == MAROON else 0.9)
        head(ax, 75, yy + hh - 2.8, k, color=col, size=7.0)
        body(ax, 75, yy + hh - 5.2, d, size=6.4, ha="center")
    arrow(ax, 75, 68.3, 75, 58.8, ms=8, lw=1.1)
    arrow(ax, 75, 43.3, 75, 33.8, ms=8, lw=1.1)
    ax.text(77.0, 63.5, "from it", ha="left", va="center", fontsize=6.2, color=OCHRE,
            style="italic")
    ax.text(77.0, 38.5, "from it", ha="left", va="center", fontsize=6.2, color=OCHRE,
            style="italic")

    banner(ax,
           "tat sṛṣṭvā tad evānuprāviśat — Brahman creates, then enters, and so is Paramātmā: "
           "the Gītā's\nParamātmā presupposes Brahman, the topic of the Śāstrārtha Prakaraṇa",
           y=3, h=11, edge=MAROON, size=6.9)
    save(fig, "fig8_chariot_cells.png")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        f()
    print("figures written to", OUT)
