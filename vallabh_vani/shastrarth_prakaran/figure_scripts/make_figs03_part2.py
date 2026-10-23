#!/usr/bin/env python3
"""Figures 5-8 for Lecture 3, Part 2 (session of 2026-07-25, 01:23:00 to the end)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

plt.rcParams["font.family"] = "DejaVu Sans"

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"

OUT = Path(__file__).resolve().parent / "figs03"
OUT.mkdir(exist_ok=True)


def new_fig(height):
    fig = plt.figure(figsize=(6.2, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor(PALE)
    return fig, ax


def box(ax, x, y, w, h, edge=TEAL, fill=SAND, lw=1.2):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.012,rounding_size=1.1",
            fc=fill, ec=edge, lw=lw,
        )
    )


def title(ax, y, text, sub=None, sub_gap=4.0):
    ax.text(50, y, text, ha="center", va="top", fontsize=12, color=MAROON, fontweight="bold")
    if sub:
        ax.text(50, y - sub_gap, sub, ha="center", va="top", fontsize=7.0, color=GREY, fontstyle="italic")


def header(ax, x, y, text, size=8.6, color=TEAL):
    ax.text(x, y, text, ha="center", va="top", fontsize=size, color=color, fontweight="bold",
            linespacing=1.2)


def body(ax, x, y, text, size=6.7, color=INK, ha="left", style="normal"):
    ax.text(x, y, text, ha=ha, va="top", fontsize=size, color=color, linespacing=1.38,
            fontstyle=style)


def arrow(ax, x1, y1, x2, y2, color=OCHRE, lw=1.4):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10,
                                 color=color, lw=lw))


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.12,
                facecolor=fig.get_facecolor())
    plt.close(fig)


# ---------------------------------------------------------------- Figure 5
def fig5():
    fig, ax = new_fig(6.0)
    title(ax, 99, "Mahāprabhuji's prāmāṇya-vyavasthā: a circle that widens",
          "The four texts are pramāṇa for this book alone; the circle widens as understanding deepens")

    bands = [
        # x0, x1, top, bottom, edge, fill, lw, head, head colour, body lines
        (2, 98, 90.5, 30.5, MAROON, SAND, 1.8,
         "When Bhagavān manifests  ·  the speaker's “fourth stage”", MAROON,
         "He follows your ajñāna, fluctuating like the Wittgenstein figure: friend, enemy, son,\n"
         "father, disciple, runaway (Raṇchoḍrāy), warrior. Ajñāna is no longer ajñāna."),
        (6.5, 93.5, 78.5, 33.5, TEAL, PALE, 1.2,
         "Once Brahman is understood  ·  the “third stage”", TEAL,
         "Everything is pramāṇa, nothing apramāṇa — even agnir anuṣṇaḥ, “fire is not hot”:\n"
         "fire = Brahman, non-heat = Brahman, so fire = non-heat (if A = B and B = C, A = C)."),
        (11, 89, 66.5, 36.5, TEAL, SAND, 1.2,
         "To grasp the framework of Brahmavāda", TEAL,
         "All scripture counts: Vedas, Rāmāyaṇas, Bhārata, Pañcarātras, other śāstras\n"
         "(artho ’yam eva nikhilair api vedavākyai …)."),
        (15.5, 84.5, 54.5, 39.5, MAROON, PALE, 1.6,
         "For this book only: TDN, Śāstrārtha Prakaraṇa", MAROON,
         "The catuṣṭaya — Veda, Gītā, Brahmasūtra, Vyāsa's samādhi-bhāṣā —\n"
         "as one coordinated pramāṇa (ekavākyatā), plus whatever does not\n"
         "contradict it (aviruddha), such as the Jaimini Sūtra."),
    ]
    for x0, x1, top, bot, edge, fill, lw, head, hcol, text in bands:
        box(ax, x0, bot, x1 - x0, top - bot, edge=edge, fill=fill, lw=lw)
        header(ax, 50, top - 1.4, head, size=8.4, color=hcol)
        body(ax, 50, top - 5.0, text, ha="center")

    # pratyakṣa banner
    box(ax, 2, 15.5, 96, 12.5, edge=TEAL, fill=PALE, lw=1.0)
    header(ax, 50, 26.6, "Throughout: pratyakṣa is pramāṇa about the pramāṇas", size=8.2)
    body(ax, 50, 23.0,
         "The Veda is pramāṇa for dharma, not for whether a text is Veda: the “Allopaniṣad” is exposed by ear.\n"
         "The Veda itself names four pramāṇas “within the solar orb”: śruti, pratyakṣa, aitihya, anumāna.",
         ha="center")

    # verdict
    box(ax, 2, 3.0, 96, 9.5, edge=OCHRE, fill=SAND, lw=1.4)
    header(ax, 50, 11.0, "Verdict", size=8.2, color=OCHRE)
    body(ax, 50, 7.6,
         "“Only four pramāṇas in Vallabha's view” is a misreading: the four hold for the Śāstrārtha Prakaraṇa alone.",
         ha="center")
    save(fig, "fig5_widening_pramana.png")


# ---------------------------------------------------------------- Figure 6
def fig6():
    fig, ax = new_fig(7.0)
    title(ax, 99, "One cognition, many stages — too fast to notice",
          "Simple, compound, complex: no single stick drives every animal; each jñeya needs its own kind of knowledge")

    cols = [
        (2, "PERCEPTION  (pratyakṣa)", [
            ("1 · Sāmānya-jñāna (nirvikalpaka)",
             "“The knowledge of this”: something is there;\nwhat it is, is not yet known."),
            ("2 · Vikalpas pile up",
             "Cow? horse? deer? buffalo? — “an infinite\npossibilities”, like files on a minister's table."),
            ("3 · Selection by criteria (involuntary)",
             "Place, time, behaviour, features: dewlap, belly,\nalertness. The child who took nuns for big crows."),
            ("4 · Confirmation",
             "The chosen vikalpa is confirmed:\n“this seems right to me”."),
            ("5 · Anubhūti → vyavasāya (decision)",
             "No longer mere knowledge or experience:\na decision, and distinction becomes possible."),
        ]),
        (51, "INFERENCE  (anumāna)", [
            ("1 · Sāhacarya",
             "This and this seen together all the time,\nstored in memory as a confidence."),
            ("2 · Vyāpti-jñāna",
             "“Smoke is always with the fire.” (Śaṅkara's jibe:\nneem smoke fills the hut, and no fire.)"),
            ("3 · Hetu-jñāna",
             "One of the pair is seen: “here is a smoke”."),
            ("4 · Pakṣa-viśiṣṭa-hetu-jñāna",
             "The hetu known as qualified by the pakṣa:\nsmoke here, in this place."),
            ("5 · Decision: “therefore”",
             "“… and here is a smoke, therefore here is fire.”"),
        ]),
    ]
    w = 47
    for x, head, stages in cols:
        box(ax, x, 87.0, w, 4.6, edge=TEAL, fill=TEAL, lw=1.0)
        ax.text(x + w / 2, 89.3, head, ha="center", va="center", fontsize=8.6, color="white",
                fontweight="bold")
        top = 84.0
        for i, (h, b) in enumerate(stages):
            last = i == len(stages) - 1
            box(ax, x, top - 10.6, w, 10.6, edge=MAROON if last else TEAL,
                fill=SAND if last else PALE, lw=1.6 if last else 1.0)
            header(ax, x + w / 2, top - 1.2, h, size=7.8, color=MAROON if last else TEAL)
            body(ax, x + w / 2, top - 4.4, b, size=6.6, ha="center")
            if not last:
                arrow(ax, x + w / 2, top - 10.8, x + w / 2, top - 13.4)
            top -= 13.6

    box(ax, 2, 2.5, 96, 13.0, edge=OCHRE, fill=SAND, lw=1.4)
    header(ax, 50, 14.4, "Why we do not notice the steps", size=8.2, color=OCHRE)
    body(ax, 50, 10.9,
         "śatapatra-vedhavat durlakṣya: a needle through a hundred lotus petals seems one stroke,\n"
         "yet pierces them in order. Film frames run so fast they look like one picture;\n"
         "a running fan shows a disc, not blades.",
         ha="center")
    save(fig, "fig6_stages_of_cognition.png")


# ---------------------------------------------------------------- Figure 7
def fig7():
    fig, ax = new_fig(4.4)
    title(ax, 99, "Śabda in stages: primary and doubt-removing pramāṇa",
          "uttaraṁ pūrva-sandeha-vārakam — each later text removes the doubt the earlier one leaves (TDN, Śāstrārtha Prakaraṇa)",
          sub_gap=6.0)

    chain = [
        ("Veda", "prāthamika: gives\nsome knowledge —\nand some saṁśaya"),
        ("Gītā", "removes the Veda's\ndoubt; knowledge is\nupdated, doubt remains"),
        ("Brahmasūtra", "removes the doubt\nleft in that updated\nknowledge"),
        ("Bhāgavata", "samādhi-bhāṣā:\nremoves the doubts\nleft in the Brahmasūtra"),
    ]
    w, gap, x = 20.6, 4.53, 2.0
    for i, (h, b) in enumerate(chain):
        box(ax, x, 68.5, w, 19.0, edge=TEAL, fill=PALE, lw=1.1)
        header(ax, x + w / 2, 86.0, h, size=8.6)
        body(ax, x + w / 2, 80.5, b, size=6.5, ha="center")
        if i < len(chain) - 1:
            arrow(ax, x + w + 0.4, 77.0, x + w + gap - 0.4, 77.0)
            ax.text(x + w + gap / 2, 79.5, "doubt", ha="center", va="bottom", fontsize=5.8,
                    color=OCHRE, fontstyle="italic")
        x += w + gap

    box(ax, 2, 43.0, 96, 20.0, edge=MAROON, fill=SAND, lw=1.8)
    header(ax, 50, 61.5, "Mahāprabhuji's siddhānta-vākya", size=8.6, color=MAROON)
    ax.text(50, 57.0, "etac catuṣṭayam ekavākyatāpannaṁ sat pramājanakam", ha="center", va="top",
            fontsize=8.4, color=INK, fontstyle="italic")
    body(ax, 50, 52.0,
         "When the four reach ekavākyatā (coordination) they produce valid knowledge (pramā).\n"
         "One coordinated caukaḍī is the pramāṇa — not four pramāṇas, and not four “prasthānas”.",
         ha="center")

    box(ax, 2, 19.5, 46.5, 17.5, edge=TEAL, fill=PALE, lw=1.1)
    header(ax, 25.25, 35.5, "Coordination holds", size=8.2)
    body(ax, 25.25, 31.0,
         "pramā, valid knowledge. Whatever does not\ncontradict the four (aviruddha) is\npramāṇa too.",
         ha="center")
    box(ax, 51.5, 19.5, 46.5, 17.5, edge=GREY, fill=PALE, lw=1.1)
    header(ax, 74.75, 35.5, "Coordination fails", size=8.2, color=GREY)
    body(ax, 74.75, 31.0,
         "prāmāṇya is suspended. The knowledge\nremains knowledge; only its standing\nas pramāṇa is on hold.",
         ha="center")
    arrow(ax, 36, 42.6, 30, 37.6)
    arrow(ax, 64, 42.6, 70, 37.6, color=GREY)

    box(ax, 2, 1.5, 96, 14.0, edge=OCHRE, fill=SAND, lw=1.4)
    header(ax, 50, 14.0, "Scope", size=8.2, color=OCHRE)
    body(ax, 50, 9.8,
         "The rule is for the Tattvārthadīpanibandha alone. Teaching “four prasthānas” is a ghost\n"
         "in the father's guise, as in Gope's film: the ghost has put on the father's form.",
         ha="center")
    save(fig, "fig7_doubt_removal_chain.png")


# ---------------------------------------------------------------- Figure 8
def fig8():
    fig, ax = new_fig(4.1)
    title(ax, 99, "Three languages in the Bhāgavata — and placement",
          "Only samādhi-bhāṣā is pramāṇa, and only when it coordinates with the other three texts",
          sub_gap=6.0)

    cols = [
        ("Samādhi-bhāṣā", "pramāṇa, when coordinated", MAROON, 1.8,
         "What Vyāsa saw in samādhi\nwhen, unsatisfied after the\nMahābhārata and the\nBrahmasūtra, he took\nNārada's advice. It is the\npramāṇa that nourishes\nthe Bhāgavata."),
        ("Paramata-bhāṣā", "not pramāṇa", TEAL, 1.2,
         "Others' views voiced inside\nthe text: Śiśupāla's abuse\nof Kṛṣṇa; in the Rāmāyaṇa,\nthe washerman's words on\nSītā; in the Gītā, Arjuna's\n“buddhiṁ mohayasīva me”\n(Bhagavadgītā 3.2)."),
        ("Laukikī-bhāṣā", "not pramāṇa", GREY, 1.2,
         "Worldly description:\n“at dawn the roosters\ncrowed kukaḍū-kū”.\nWhat has that to do with\nthe Bhāgavata's samādhi?"),
    ]
    w, gap, x = 30.4, 2.4, 2.0
    for head, tag, edge, lw, text in cols:
        box(ax, x, 51.5, w, 36.0, edge=edge, fill=SAND if edge == MAROON else PALE, lw=lw)
        header(ax, x + w / 2, 86.0, head, size=8.8, color=INK if edge == GREY else edge)
        ax.text(x + w / 2, 81.4, tag, ha="center", va="top", fontsize=6.6,
                color=edge, fontstyle="italic")
        body(ax, x + w / 2, 76.6, text, size=6.6, ha="center")
        x += w + gap

    header(ax, 50, 47.6, "Placement: in whose mouth does the statement sit?", size=8.8)
    places = [
        ("Bhāgavata", "Vyāsa's mouth,\nor Śiśupāla's?"),
        ("Rāmāyaṇa", "Vālmīki's mouth,\nor the washerman's?"),
        ("Gītā", "Kṛṣṇa's, Vyāsa's,\nor Arjuna's?"),
    ]
    x = 2.0
    for head, text in places:
        box(ax, x, 26.0, w, 15.5, edge=TEAL, fill=SAND, lw=1.0)
        header(ax, x + w / 2, 40.0, head, size=8.0)
        body(ax, x + w / 2, 35.0, text, size=6.7, ha="center")
        x += w + gap

    box(ax, 2, 2.0, 96, 20.0, edge=OCHRE, fill=SAND, lw=1.4)
    header(ax, 50, 20.5, "Without placement", size=8.2, color=OCHRE)
    body(ax, 50, 15.6,
         "The “Allopaniṣad” would pass for Veda;\n"
         "“nikhātā pitar” (the ancestors are the foundation) is heard as “the ancestors don't eat”;\n"
         "“barhāpīḍam” (a crown of peacock feathers) becomes “O groom, you gave me pain”.",
         ha="center")
    save(fig, "fig8_three_languages_placement.png")


if __name__ == "__main__":
    fig5()
    fig6()
    fig7()
    fig8()
    print("written:", sorted(p.name for p in OUT.glob("fig[5-8]_*.png")))
