#!/usr/bin/env python3
"""Figures for Śāstrārtha Prakaraṇa Lecture 14 (2026-10-24). Output: build/figs14/."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.family"] = "DejaVu Sans"
MAROON, OCHRE, TEAL = "#7B2D26", "#C46210", "#2C4A52"
SAND, PALE, GREY, INK = "#F5EDE0", "#FBF7F0", "#8A8078", "#2B2320"
OUT = Path(__file__).resolve().parent / "figs14"
OUT.mkdir(exist_ok=True)


def canvas(h=4.6):
    fig, ax = plt.subplots(figsize=(6.2, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor(PALE)
    return fig, ax


def title(ax, text, sub=None):
    ax.text(50, 98, text, ha="center", va="top", fontsize=12, weight="bold", color=INK)
    if sub:
        ax.text(50, 92.5, sub, ha="center", va="top", fontsize=7.6, color=GREY, style="italic")


def box(ax, x, y, w, h, head, body="", edge=TEAL, fill=SAND, hs=8.6, bs=6.8, lw=1.3, hcol=None):
    ax.add_patch(
        FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012", fc=fill, ec=edge, lw=lw)
    )
    if body:
        ax.text(x + w / 2, y + h - 1.6, head, ha="center", va="top", fontsize=hs, weight="bold",
                color=hcol or edge)
    else:  # a header-only box: centre its single label
        ax.text(x + w / 2, y + h / 2, head, ha="center", va="center", fontsize=hs, weight="bold",
                color=hcol or edge)
    if body:
        nh = head.count("\n") + 1
        ax.text(x + w / 2, y + h - 2.2 - 4.2 * nh, body, ha="center", va="top", fontsize=bs,
                color=INK, linespacing=1.3)


def arrow(ax, x1, y1, x2, y2, col=OCHRE, lw=1.4):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10,
                                 color=col, lw=lw))


def banner(ax, text, y=2, h=9, edge=MAROON, fs=6.5):
    ax.add_patch(FancyBboxPatch((3, y), 94, h, boxstyle="round,pad=0.012", fc=SAND, ec=edge, lw=1.5))
    ax.text(50, y + h - 1.8, text, ha="center", va="top", fontsize=fs, color=edge,
            linespacing=1.3)


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.12, facecolor=PALE)
    plt.close(fig)


# 1 ─ the cancerous growth of ahantā and mamatā
fig, ax = canvas(5.8)
title(ax, "The Cancerous Growth of Ahantā and Mamatā", "kārikās 23 and 31: how saṁsāra arises in the jīva")
box(ax, 20, 75, 60, 14, "Pure consciousness (cid-aṁśa)",
    "ānanda withdrawn; joined to prakṛti and its tattvas;\nin itself neither ahantā nor mamatā")
arrow(ax, 38, 75, 27, 71)
arrow(ax, 62, 75, 73, 71)
left = [("ahantā", "the attribute of the antaḥkaraṇa"), ("krodha", "anger at what thwarts the 'I'"),
        ("dveṣa", "anger one cannot discharge:\n'this is against me'"), ("mātsarya", "jealousy: even dveṣa\ncannot be applied")]
right = [("mamatā", "possession: 'this is mine'"), ("kāma", "desire for what one would own"),
         ("rāga", "being dyed in the desire"), ("lobha", "kāma never satisfied:\nhoarding, like the cheetah")]
for col, items, edge in ((6, left, TEAL), (54, right, TEAL)):
    for i, (h, b) in enumerate(items):
        y = 58 - i * 14.2
        box(ax, col, y, 40, 12.5, h, b, edge=edge, hs=8.2, bs=6.4)
        if i:
            arrow(ax, col + 20, y + 12.5 + 1.7, col + 20, y + 12.5)
banner(ax, "The seed is blameless; the defect lies in the growth, like a gland turned cancerous.\n"
       "That growth is the jīva's duḥkhitva (being in sorrow) and anīśatā (being without mastery).",
       y=0.5, h=9)
save(fig, "fig1_cancerous_growth.png")

# 2 ─ knowledge can bear ignorance, bare consciousness cannot
fig, ax = canvas(5.2)
title(ax, "Knowledge Can Bear Ignorance; Bare Consciousness Cannot",
      "after the tirobhāva of ānanda only cit remains, and it illumines whatever comes")
box(ax, 8, 72, 84, 15, "Saccidānanda  →  ānanda withdrawn  →  cit alone",
    "śuddha cetanā = 'only' consciousness, as pure gold is only gold:\nneither jñāna nor ajñāna, it lights up knowledge or ignorance alike",
    edge=TEAL, hs=8.4)
arrow(ax, 38, 72, 27, 66)
arrow(ax, 62, 72, 73, 66)
box(ax, 4, 15, 44, 50, "Consciousness with\nknowledge",
    "the grandson who lisps 'tum ṭon':\nhe knows he is a child and says so,\nand turns the joke back on his\ngrandfather: 'you are a child!'\n\n"
    "ignorance is present but seen;\nit can be tested and borne;\nit does not spread over him\n\n"
    "jñāna can bear vijñāna and\navijñāna alike", edge=MAROON, hs=8.4)
box(ax, 52, 15, 44, 50, "Consciousness without\nknowledge",
    "the chanter who could not say\n'Hare Kṛṣṇa' and thought it correct;\n'Horibol' for the dying in Bengal\n\n"
    "Rāmhit Yādav spelled 'Ram Hit Yadav'\nand translated back into Hindi\nas 'Rām struck Yādav'\n\n"
    "ignorance is not seen;\nit spreads over consciousness", edge=TEAL, hs=8.4)
banner(ax, "If there is knowledge, avijñāna can be borne; if only consciousness remains, anything can happen.",
       y=2, h=8)
save(fig, "fig2_knowledge_vs_consciousness.png")

# 3 ─ accelerator and brake
fig, ax = canvas(5.0)
title(ax, "Ahantā and Kāma: Accelerator and Brake",
      "the two raise and lower the speed of consciousness, and pull against each other")
box(ax, 4, 48, 40, 37, "Where kāma grows",
    "pride gives way before it:\n'need is a poor wretched thing'\n\nKālidāsa: kāmārtā hi\nprakṛti-kṛpaṇāś cetanācetaneṣu —\nthe love-sick cannot tell the\nconscious from the unconscious",
    edge=TEAL)
box(ax, 56, 48, 40, 37, "Where ahantā grows",
    "desire gives way before it:\n\nGandhiji, who cared for the\nwhole world, kept his evening walk\nwhile Kasturbā lay dying;\nDevdās called 'Kasturbā kī jay'",
    edge=TEAL)
arrow(ax, 44, 70, 56, 70, col=OCHRE)
arrow(ax, 56, 62, 44, 62, col=OCHRE)
ax.text(50, 66, "one up,\none down", ha="center", va="center", fontsize=5.8, color=GREY)
box(ax, 10, 14, 80, 29, "As in every car",
    "an accelerator and a brake: ahantā and mamatā both\nincrease and decrease the speed of consciousness.\n"
    "In the matter where you have kāma, your ahantā lessens;\nin the matter where you have ahantā, your kāma weakens.",
    edge=MAROON)
banner(ax, "The power of making distinctions weakens in either extreme.", y=3, h=7)
save(fig, "fig3_accelerator_brake.png")

# 4 ─ the six qualities reversed
fig, ax = canvas(5.2)
title(ax, "The Six Qualities Reversed", "withdrawn with ānanda, each quality leaves a lack, and a vice compensates it")
rows = [
    ("aiśvarya", "dīnatā", "krodha", "anaiśvaryāt krodhitā —\nanger at what one cannot master"),
    ("vīrya", "duḥkhitā", "lobha", "aviśrambhāt sva-vīryasya —\nno trust in one's own strength"),
    ("yaśas", "hīnatā", "mātsarya", "yaśo-hīno matsarī syāt —\nthe rival who boasts of pedigree"),
    ("śrī", "janmādi-vipat", "mada", "śrī-hīne mado mataḥ —\nthe bridegroom's mother"),
    ("jñāna", "ahaṅkārika moha", "moha", "jñānābhāve bhaven mohaḥ —\nthe jail of solipsism"),
    ("vairāgya", "viṣaya-kāmanā", "kāma", "kāmo vairāgya-rahite —\ndesire for the objects"),
]
heads = [("in Bhagavān", 4, 17), ("the lack", 23, 21), ("its vice", 46, 16),
         ("the speaker's verse", 64, 32)]
for h, x, w in heads:
    ax.text(x + w / 2, 87.6, h, ha="center", va="center", fontsize=7.6, weight="bold", color=TEAL)
for i, (q, lack, vice, verse) in enumerate(rows):
    y = 75.5 - i * 11.2
    box(ax, 4, y, 17, 9, q, edge=MAROON, hs=8.2)
    box(ax, 23, y, 21, 9, lack, edge=TEAL, hs=7.0)
    box(ax, 46, y, 16, 9, vice, edge=OCHRE, hs=8.2)
    ax.text(80, y + 7.6, verse, ha="center", va="top", fontsize=6.4, color=INK, linespacing=1.25)
    arrow(ax, 21, y + 4.5, 23, y + 4.5, lw=1.0)
    arrow(ax, 44, y + 4.5, 46, y + 4.5, lw=1.0)
banner(ax, "In Bhagavān these qualities never control him (avilupta jñāna); in the jīva each lack is blameless,\n"
       "and the defect enters at the third step, when it is compensated: ity eṣā viparītatā.",
       y=1, h=9.5)
save(fig, "fig4_six_qualities_reversed.png")

# 5 ─ vairāgya against tyāga
fig, ax = canvas(4.6)
title(ax, "Vairāgya Is Victory, Tyāga Is Defeat", "for indriyādhyāsa the vidyā is vairāgya, not tyāga")
box(ax, 4, 31, 44, 54, "Tyāga: leaving",
    "admits defeat by the object:\n'I can no longer bear it, so I leave it'\n\n"
    "the Haridvār āśrama with a TV antenna\nand 'Beware of dog' on the door:\nshould one fear the dog or the svāmī?\n\n"
    "the Gokul svāmī who made tea and\ngāṭhiyā for the thieves", edge=TEAL)
box(ax, 52, 31, 44, 54, "Vairāgya: overcoming",
    "enjoy the object, keep no anurāga;\nvictoriousness over the object\n\n"
    "duḥkheṣv anudvigna-manāḥ, sukheṣu\nvigata-spṛhaḥ (Gītā 2.56): welcome what\ncomes, bid farewell to what goes\n\n"
    "the monk who asked the conqueror:\n'do you understand that you can\ncut off my neck?'", edge=MAROON)
box(ax, 14, 11, 72, 17, "Jābāla Upaniṣad 4",
    "yad ahar eva virajet tad ahar eva pravrajet:\nrenounce on the very day vairāgya comes; we reverse it,\nrenouncing first and seeking vairāgya after", edge=OCHRE, hs=8.0)
banner(ax, "True tyāga is by the mind (tyāgo 'pi manasaiva): it dilutes the concepts of pleasure and pain.",
       y=1.5, h=7.5)
save(fig, "fig5_vairagya_tyaga.png")

# 6 ─ five limbs of avidyā and vidyā, and the Tao circle
fig, ax = canvas(5.4)
title(ax, "Five Limbs of Avidyā, Five of Vidyā",
      "kārikās 32–33 and 45cd–46ab: each vidyā answers a limb, and each hides an avidyā")
cols = [("avidyā: the limb", 3, 26, TEAL), ("vidyā that answers it", 31, 24, MAROON),
        ("the avidyā hidden in it", 57, 40, GREY)]
for h, x, w, c in cols:
    ax.text(x + w / 2, 88, h, ha="center", va="center", fontsize=7.6, weight="bold", color=c)
rows = [
    ("svarūpājñāna", "deep sleep, coma", "Sāṅkhya", "inventory of tattvas",
     "an inventory needs an inventor:\none must take oneself as a 'you'"),
    ("antaḥkaraṇādhyāsa", "ahaṅkāra first", "Yoga", "turn the senses inward",
     "'I must have ātma-darśana' —\nthe darkness under the lamp"),
    ("prāṇādhyāsa", "the comfort zone", "Tapas", "training in discomfort",
     "tapas of prāṇa needs prāṇa\nheld as one's own"),
    ("indriyādhyāsa", "palatable / not", "Vairāgya", "not shaken, not craving",
     "pleasure and pain have no\nwatertight compartment"),
    ("dehādhyāsa", "the body as self", "Bhakti", "of commitment",
     "bhajana needs a body: the Kutch\nmother, the Hāḍā soldier"),
]
for i, (a, ab, v, vb, hid) in enumerate(rows):
    y = 72 - i * 13
    box(ax, 3, y, 26, 11, a, ab, edge=TEAL, hs=7.6, bs=6.4)
    box(ax, 31, y, 24, 11, v, vb, edge=MAROON, hs=8.0, bs=6.4)
    box(ax, 57, y, 40, 11, "", "", edge=GREY, fill=PALE, lw=0.9)
    ax.text(77, y + 9.0, hid, ha="center", va="top", fontsize=6.5, color=INK, linespacing=1.3)
    arrow(ax, 29, y + 5.5, 31, y + 5.5, lw=1.0)
banner(ax, "Like sleep and waking, or the Tao circle (in every black a white, in every white a black),\n"
       "vidyā and avidyā are installed in the jīva, complementary and cyclical, not contradictory.",
       y=0.5, h=9.5)
save(fig, "fig6_five_limbs_tao.png")

# 7 ─ comfort and discomfort
fig, ax = canvas(4.6)
title(ax, "Comfort and Discomfort", "the ground on which tapas works on prāṇa and vairāgya on the senses")
ax.add_patch(FancyBboxPatch((6, 74), 88, 6, boxstyle="round,pad=0.012", fc=SAND, ec=GREY, lw=1.0))
ax.text(10, 77, "comfort: palatable, pleasure", ha="left", va="center", fontsize=6.8, color=TEAL)
ax.text(90, 77, "discomfort: non-palatable, pain", ha="right", va="center", fontsize=6.8, color=MAROON)
arrow(ax, 44, 77, 56, 77)
arrow(ax, 56, 77, 44, 77)
ax.text(50, 71.5, "no watertight compartment: mother's milk → sugar → chilli", ha="center", va="top",
        fontsize=6.6, color=GREY, style="italic")
box(ax, 4, 18, 44, 46, "Tapas for prāṇa",
    "yoga trains one to feel discomfort as\ncomfort: śavāsana is easy, every other\nāsana is not; prāṇāyāma until sweat\n\n"
    "Dayānanda bare in the Haridvār cold;\nhibernation; Vālmīki in the anthill;\nMahāvīra and the cowherd's thorn\n\n"
    "who lives in comfort grows weak", edge=TEAL)
box(ax, 52, 18, 44, 46, "Vairāgya for the senses",
    "not happy in pleasure, not sorrowful\nin sorrow: when pleasure comes, enjoy it;\nwhen sorrow comes, undergo it\n\n"
    "āyātam āyāntam apekṣaṇīyam:\nwelcome what comes, let go what goes;\nwhat is ours remains ours\n\n"
    "pain felt, but not disturbed by it", edge=MAROON)
banner(ax, "Fearing is one thing, being in trouble another: we fear blood more than the wound.", y=3, h=8)
save(fig, "fig7_comfort_discomfort.png")

# 8 ─ control, not removal; consciousness, not understanding
fig, ax = canvas(5.0)
title(ax, "Control, Not Removal; Consciousness, Not Understanding", "the questions at the end of the session")
box(ax, 3, 30, 36, 56, "Vidyā and avidyā",
    "not attached by karma, so karma\ncannot remove them: a belt\none tied oneself can be opened;\nfetters someone else put on cannot\n\n"
    "'Can you delete your skeleton?'\nNo — but with the muscles\nyou can control it\n\n"
    "ego and possessiveness fight\nhand in hand: the girl who\ngave the green signal and\ncannot let go", edge=MAROON, bs=6.2)
ax.text(69.5, 85, "cetanā and buddhi", ha="center", va="center",
        fontsize=7.4, weight="bold", color=TEAL)
box(ax, 42, 57, 27, 24, "understood,\nnot conscious",
    "gravitational pull;\nBose proves life in\nplants, yet no pain in\nus when we pluck a fruit", edge=TEAL, hs=7.6, bs=6.4)
box(ax, 71, 57, 26, 24, "conscious,\nnot understood",
    "the old who feel their\nend is near; the killer's\nnote: 'why do I want\nto shoot those I love?'", edge=TEAL, hs=7.6, bs=6.4)
box(ax, 42, 30, 55, 23, "Our cit is bare cit",
    "in Brahman cit is of the nature of jñāna, aiśvarya,\nvīrya, vairāgya; with ānanda withdrawn ours is\n"
    "only cit, born of a mixture like the lotus from mud:\nthe Aquaguard, the mosquito, the Worli gutter", edge=OCHRE, hs=8.0, bs=6.4)
banner(ax, "Nivṛtti is his to do; the jīva's part is to bring the installed powers under control.\n"
       "Purity beyond our making is the story of the maryādī, not of the one who does sevā.", y=3, h=11)
save(fig, "fig8_control_consciousness.png")

print("figures written to", OUT)
