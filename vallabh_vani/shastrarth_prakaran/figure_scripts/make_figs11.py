#!/usr/bin/env python3
"""Figures for Śāstrārtha Prakaraṇa, Lecture 11 (2026-09-19).

Layout is computed in points from the top of the figure, so every box is sized to
its text (header + top-anchored body) and the figure height fits the content.
Axes run 0–100 both ways with the axis switched off.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.family"] = "DejaVu Sans"

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"
WHITE = "#FFFFFF"

OUT = Path(__file__).resolve().parent / "figs11"
OUT.mkdir(exist_ok=True)

WIDTH_IN = 6.2
TITLE = 12.0
HEAD = 8.6
SUB = 6.9
BODY = 6.8
LS = 1.3
LINE = BODY * LS  # points per body line
TITLE_BLOCK = 40.0  # points used by title + subtitle
GAP = 9.0  # visual gap between stacked boxes, points


def nlines(s):
    return s.count("\n") + 1


def panel_h(body, sub=False):
    return (29.0 if sub else 21.0) + nlines(body) * LINE + 8.0


def banner_h(line2):
    return 21.0 + nlines(line2) * LINE + 7.0


class Canvas:
    def __init__(self, height_pt):
        self.hpt = height_pt
        self.fig = plt.figure(figsize=(WIDTH_IN, height_pt / 72.0), facecolor=PALE)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis("off")

    def y(self, p):
        """Data y for a point offset p measured from the top."""
        return 100.0 - p * 100.0 / self.hpt

    def u(self, p):
        return p * 100.0 / self.hpt

    def text(self, x, p, s, size=BODY, color=INK, ha="left", va="top", weight="normal",
             style="normal", ls=LS):
        self.ax.text(x, self.y(p), s, fontsize=size, color=color, ha=ha, va=va,
                     fontweight=weight, fontstyle=style, linespacing=ls)

    def box(self, x, p_top, w, h_pt, ec=TEAL, fc=WHITE, lw=1.2, ls="-"):
        self.ax.add_patch(
            FancyBboxPatch((x, self.y(p_top + h_pt)), w, self.u(h_pt),
                           boxstyle="round,pad=0.012", mutation_scale=60,
                           fc=fc, ec=ec, lw=lw, ls=ls)
        )

    def panel(self, x, p_top, w, h_pt, head, body, ec=TEAL, sub=None, head_color=None,
              fc=WHITE, lw=None, center_head=True, sub_size=SUB):
        lw = lw if lw is not None else (1.8 if ec == MAROON else 1.2)
        self.box(x, p_top, w, h_pt, ec=ec, fc=fc, lw=lw)
        hx, ha = (x + w / 2, "center") if center_head else (x + 2.0, "left")
        self.text(hx, p_top + 13.5, head, size=HEAD, color=head_color or ec, ha=ha, va="baseline",
                  weight="bold")
        body_top = 21.0
        if sub:
            self.text(hx, p_top + 22.5, sub, size=sub_size, color=GREY, ha=ha, va="baseline",
                      style="italic")
            body_top = 29.0
        self.text(x + 2.0, p_top + body_top, body)

    def banner(self, p_top, line1, line2, ec=OCHRE, c1=MAROON, size1=7.6):
        h = banner_h(line2)
        self.box(2, p_top, 96, h, ec=ec, fc=SAND, lw=1.5)
        self.text(50, p_top + 12.5, line1, size=size1, color=c1, ha="center", va="baseline",
                  weight="bold")
        self.text(50, p_top + 19.0, line2, ha="center")
        return h

    def title(self, s, sub=None):
        self.text(50, 19.0, s, size=TITLE, ha="center", va="baseline", weight="bold")
        if sub:
            self.text(50, 30.5, sub, size=7.4, color=GREY, ha="center", va="baseline",
                      style="italic")

    def arrow(self, x1, p1, x2, p2, color=OCHRE, lw=1.3, ms=10):
        self.ax.add_patch(FancyArrowPatch((x1, self.y(p1)), (x2, self.y(p2)), arrowstyle="-|>",
                                          mutation_scale=ms, color=color, lw=lw,
                                          shrinkA=0, shrinkB=0))

    def save(self, name):
        self.fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.12,
                         facecolor=PALE)
        plt.close(self.fig)


# ---------------------------------------------------------------- Figure 1
def fig1():
    cols = [
        (2, "Ekarāśi · simple", "one unit of experience", TEAL,
         "Those who take illusion as\nekarāśi say: this knowledge\nis neither compound nor\ncomplex — it is simple.\n\n"
         "Then the only question is:\nwhat is its object — sat,\nasat, both, or neither?"),
        (35, "Dvirāśi · compound", "experience + recollection", TEAL,
         "Seen young ten years ago,\nseen 'aged' today.\n\nPratyabhijñā → picchāṇaṁ\n→ pahacān: 'what I saw then\n"
         "is what I see now.'\n\nRemembered — or only the\nimpression recollected?"),
        (68, "Complex · three rāśis", "the bald man in a wig", MAROON,
         "1  Yesterday: bald (ṭāl).\n2  Today: a full head of hair.\n3  Already 'uploaded':\n"
         "    hair does not grow so fast.\n\n→ 'Are you you?'\n'If I am not me, who else\nwould I be?'"),
    ]
    line1 = "Mahāprabhuji: neither ekarāśi nor dvirāśi — every knowledge is complex."
    line2 = ("We miss this because we look at objects through knowledge, never at knowledge itself —\n"
             "as anger looks at its target and not at the anger.")
    ch = max(panel_h(c[4], sub=True) for c in cols)
    total = TITLE_BLOCK + ch + 12 + banner_h(line2) + 4
    c = Canvas(total)
    c.title("How many units in one cognition?", "ekarāśi · dvirāśi · complex — and the bald man in a wig")
    top = TITLE_BLOCK
    for x, head, sub, ec, body in cols:
        c.panel(x, top, 30, ch, head, body, ec=ec, sub=sub)
    mid = top + ch / 2
    c.arrow(32.3, mid, 34.7, mid)
    c.arrow(65.3, mid, 67.7, mid)
    c.banner(top + ch + 12, line1, line2, ec=MAROON)
    c.save("fig1_rasi.png")


# ---------------------------------------------------------------- Figure 2
def fig2():
    left = [
        ("Sat-khyāti", "Only sat is ever known; asat never is.\nSāṅkhya, Kapila Muni; Rāmānuja"),
        ("Asat-khyāti", "The unreal is known — pinned on Buddha,\nyet his śūnya is not asat. Madhva first\n"
                        "argued that asat can be known."),
        ("Sad-asat-khyāti", "'Leave the quarrel': what is known in\nbhrama is a mixture of being and non-being"),
        ("Sad-asad-vilakṣaṇa", "Neither sat nor asat\nŚaṅkara, Buddha"),
    ]
    right = [
        ("Akhyāti", "ajñāna: 'you cannot understand',\n'you are not experiencing'", TEAL),
        ("Anyathākhyāti", "anyathā-jñāna:\n'you are misunderstanding'", TEAL),
        ("Anyakhyāti", "anya-jñāna: knowledge of something else —\nthe deity is here, the mind is elsewhere;\n"
                       "the 'other' is a concept from your own mind", MAROON),
    ]
    line1 = "Mahāprabhuji: in bhrama one knows not sat, asat, both or neither — but the anya."
    line2 = "Every knowledge is complex; so for us mithyā means anya, the 'other'."
    lh = [panel_h(b) for _, b in left]
    col_total = sum(lh) + GAP * (len(left) - 1)
    rh = (col_total - GAP * (len(right) - 1)) / len(right)
    top = TITLE_BLOCK + 16
    total = top + col_total + 12 + banner_h(line2) + 4
    c = Canvas(total)
    c.title("What is known in an illusion? The map of khyātis", "khyāti = appearance, not 'fame'")
    c.text(25.5, TITLE_BLOCK + 9.5, "From the object's side (viṣaya)", size=HEAD, color=TEAL,
           ha="center", va="baseline", weight="bold")
    c.text(74.5, TITLE_BLOCK + 9.5, "From the subject's side (viṣayī)", size=HEAD, color=TEAL,
           ha="center", va="baseline", weight="bold")
    p = top
    for (head, body), h in zip(left, lh):
        c.panel(2, p, 47, h, head, body, ec=TEAL)
        p += h + GAP
    p = top
    for head, body, ec in right:
        c.panel(51, p, 47, rh, head, body, ec=ec)
        p += rh + GAP
    c.banner(top + col_total + 12, line1, line2, ec=MAROON, size1=7.4)
    c.save("fig2_khyati.png")


# ---------------------------------------------------------------- Figure 3
def fig3():
    steps = [
        ("Indriya — eye, ear, nose, touch, taste", "gives only sattā: 'something is there'"),
        ("Manas — presents the vikalpas", "Gujarati? Marathi? Bengali? European? African?\n"
                                          "Arabian? a vanamānuṣa? — all at once"),
        ("Ahaṅkāra — forwards them", "'these are all the possibilities: you decide'"),
        ("Buddhi — adhyavasāya: settles one", "by its 'grudge': hāna · upādāna · upekṣā,\n"
                                              "coloured by its sāttvika · rājasa · tāmasa state"),
        ("Aham — bears it all", "like the head of a joint family: whoever did the\n"
                                "work, the consequences fall on him"),
    ]
    notes = [
        (GREY, "Sattā",
         "Śaṅkara and Buddha: sattā is\nnirvikalpaka. Mahāprabhuji:\nsattā has countless vikalpas,\n"
         "stored in the mind as\nimpressions."),
        (GREY, "The 'grudge'",
         "anti- or pro-; with none, buddhi\ndecides arbitrarily. 'Hair cannot\ngrow in a day' → 'this must be\n"
         "someone else'. A fair man in India\n'must be a leper'; a dark man in\nEurope 'must be African'."),
        (MAROON, "Anyakhyāti",
         "Mind supplied the subjectivity;\nbuddhi decided. If the chosen\nvikalpa is not out there, the\n"
         "cognition is anyakhyāti —\nmithyā in this sense, not\n'nowhere at all' (asat).\n\n"
         "Not sat, not asat, not both,\nnot neither: anya."),
    ]
    agap = 15.0
    sh = [panel_h(b) for _, b in steps]
    left_total = sum(sh) + agap * (len(steps) - 1)
    nh = [panel_h(b) for _, _, b in notes]
    ngap = (left_total - sum(nh)) / (len(notes) - 1)
    top = 30.0
    total = top + left_total + 5
    c = Canvas(total)
    c.title("Cakṣuṣālocya vastūni: the layers of one cognition")
    p = top
    for i, ((head, body), h) in enumerate(zip(steps, sh)):
        ec = MAROON if i == len(steps) - 1 else TEAL
        c.panel(2, p, 57, h, head, body, ec=ec, center_head=False)
        if i < len(steps) - 1:
            c.arrow(30.5, p + h + 2.5, 30.5, p + h + agap - 2.5)
        p += h + agap
    p = top
    for (ec, head, body), h in zip(notes, nh):
        c.panel(62, p, 36, h, head, body, ec=ec, head_color=MAROON if ec == MAROON else TEAL,
                fc=SAND if ec == GREY else WHITE, lw=1.6 if ec == MAROON else 1.1)
        p += h + ngap
    c.save("fig3_layers.png")


# ---------------------------------------------------------------- Figure 4
def fig4():
    lbody = ("Railway berth: the train gives it for\nthe journey.\n\nPillow: issued by the conductor for\nthe night.\n\n"
             "Prathameśjī's car: lent so Śrīpāda\nBābā could reach Mathura.\n\n"
             "'It came into my hand, I use it; if it\ncomes into your hand, you use it.'")
    rbody = ("'My berth: I reserved it, I paid for it' —\nbut let goons show a gun, and it is\n'yours only'.\n\n"
             "The 'I' that gave away the pillow was\nfinished in a blink at Kota.\n\n"
             "The lent car went to Agra and was sold.\n\n"
             "The lion's 'king of the jungle' ended in\nthe elephant's trunk.")
    line1 = "Mahāprabhuji: aham is not yours — it is a function of Brahman, given to you to use (vāparne)."
    line2 = ("Mama too is given by Bhagavān. Use it for the journey and there is no fault;\n"
             "confine it to yourself 'forever' and it is anyakhyāti — mithyā.")
    h = max(panel_h(lbody), panel_h(rbody))
    total = TITLE_BLOCK + h + 12 + banner_h(line2) + 4
    c = Canvas(total)
    c.title("An 'I' given for the journey", "aham and mama as Bhagavān's gift, for use")
    c.panel(2, TITLE_BLOCK, 47, h, "Given for use — not mithyā", lbody, ec=TEAL)
    c.panel(51, TITLE_BLOCK, 47, h, "Claimed as 'mine forever' — mithyā", rbody, ec=GREY,
            head_color=GREY)
    c.banner(TITLE_BLOCK + h + 12, line1, line2, ec=MAROON, size1=7.3)
    c.save("fig4_berth.png")


# ---------------------------------------------------------------- Figure 5
def fig5():
    cols_x = [19.5, 46.45, 73.4]
    cw = 24.2
    heads = [("Sthita · situated", TEAL, "in that place or time"),
             ("Bhāsita · appearing", OCHRE, "mithyā: not there, yet appears"),
             ("Āvirbhūta · manifest", MAROON, "Mahāprabhuji: āvirbhāva")]
    rows = [("Deśa", "place"), ("Kāla", "time"), ("Vastu", "thing")]
    cells = [
        ["'I am in this room':\nnot mithyā, yet not\nnitya — when I leave,\nI am not seen here",
         "the reflection in a\nmirror: it appears\nwhere it is not",
         "air fills the room;\nunder the fan it is felt;\nelsewhere it is there\nbut not felt"],
        ["not there yesterday,\nhere today, gone\ntomorrow",
         "the eclipse: not in\nthat time, yet it\nappears",
         "it was there, not\nmanifest; now it is\nmade manifest"],
        ["this is a pencil,\nnot a whiteboard",
         "appears as a thing\nthat it is not",
         "manifest as this thing:\nāvirbhāva, and in\nturn tirobhāva"],
    ]
    line1 = "Mithyā is concluded only where a thing is not in that place or time, yet appears."
    line2 = "Āvirbhāva: it was there and becomes manifest — not ābhāsa, not mere sthiti."
    head_h = 30.0
    rgap = 8.0
    rh = [max(nlines(s) for s in row) * LINE + 16.0 for row in cells]
    rh = [max(h, 38.0) for h in rh]
    top = TITLE_BLOCK
    grid_total = head_h + rgap + sum(rh) + rgap * (len(rows) - 1)
    total = top + grid_total + 12 + banner_h(line2) + 4
    c = Canvas(total)
    c.title("The ninefold pariccheda", "three limits × three modes")
    for x, (h, col, s) in zip(cols_x, heads):
        c.box(x, top, cw, head_h, ec=col, fc=SAND, lw=1.4)
        c.text(x + cw / 2, top + 13.0, h, size=8.0, color=col, ha="center", va="baseline",
               weight="bold")
        c.text(x + cw / 2, top + 23.0, s, size=6.4, color=INK, ha="center", va="baseline",
               style="italic")
    p = top + head_h + rgap
    for (r, rs), h, row in zip(rows, rh, cells):
        c.box(2, p, 15, h, ec=TEAL, fc=SAND, lw=1.2)
        c.text(9.5, p + h / 2 - 1.0, r, size=HEAD, color=TEAL, ha="center", va="baseline",
               weight="bold")
        c.text(9.5, p + h / 2 + 9.0, rs, size=SUB, color=GREY, ha="center", va="baseline",
               style="italic")
        for x, (hh, col, s), body in zip(cols_x, heads, row):
            c.box(x, p, cw, h, ec=col, fc=WHITE, lw=1.6 if col == MAROON else 1.2)
            c.text(x + 1.8, p + 8.0, body)
        p += h + rgap
    c.banner(top + grid_total + 12, line1, line2, ec=OCHRE)
    c.save("fig5_pariccheda.png")


# ---------------------------------------------------------------- Figure 6
def fig6():
    notes = [
        (TEAL, "Relative limits",
         "The earth's orbit is unlimited relative to the\nearth, limited relative to Mars's orbit; the\n"
         "whole solar system is limited in its turn."),
        (TEAL, "Infinite regress",
         "If a limit comes from a deśa-kāla, what limits\nthat deśa-kāla — and that one? Unless something\n"
         "is aparicchinna, the chain never ends."),
        (GREY, "Track and treadmill",
         "Motion is known only against what is still: if\nthe track runs back as fast as the train runs\n"
         "on, the train has not moved."),
        (MAROON, "Not imported",
         "The limit cannot be brought into the aparicchinna\nfrom elsewhere, or at some time — else it\n"
         "would no longer be aparicchinna, nor nitya."),
    ]
    nh = [panel_h(b) for _, _, b in notes]
    col_total = sum(nh) + GAP * (len(notes) - 1)
    top = TITLE_BLOCK
    total = top + col_total + 4
    c = Canvas(total)
    c.title("Relative limits need an unlimited ground", "the orbits, the track and the treadmill")
    # left frame: the aparicchinna
    c.box(2, top, 46, col_total, ec=MAROON, fc=SAND, lw=1.6, ls="--")
    c.text(25, top + 13.0, "the aparicchinna — called Brahman", size=7.2, color=MAROON,
           ha="center", va="baseline", weight="bold")
    c.text(25, top + 22.5, "in which deśa, kāla and vastu themselves stand", size=6.4,
           color=MAROON, ha="center", va="baseline", style="italic")
    c.text(25, top + col_total - 6.0, "the whole solar system: itself limited", size=6.5,
           color=GREY, ha="center", va="baseline", style="italic")
    # orbits, drawn in inches so they stay circular
    usable_top = top + 30.0
    usable_bot = top + col_total - 16.0
    rmax_pt = (usable_bot - usable_top) / 2 - 7.0
    cy_pt = (usable_top + usable_bot) / 2 + 3.0
    cx = 25.0
    sx = WIDTH_IN * 72.0 / 100.0  # points per x unit
    fracs = [(0.17, "Budha", GREY, 0.8), (0.31, "Śukra", GREY, 0.8), (0.47, "Earth", TEAL, 2.0),
             (0.65, "Maṅgala", TEAL, 1.3), (0.83, "Guru", GREY, 0.8), (1.0, "Śani", GREY, 0.8)]
    for f, name, col, lw in fracs:
        r = f * rmax_pt
        c.ax.add_patch(Ellipse((cx, c.y(cy_pt)), 2 * r / sx, c.u(2 * r), fill=False, ec=col, lw=lw))
        c.text(cx, cy_pt - r - 1.5, name, size=6.4, color=col, ha="center", va="baseline",
               weight="bold" if name in ("Earth", "Maṅgala") else "normal")
    c.ax.add_patch(Ellipse((cx, c.y(cy_pt)), 7.0 / sx, c.u(7.0), fc=OCHRE, ec=OCHRE))
    c.text(cx, cy_pt + 12.0, "sun", size=6.4, color=OCHRE, ha="center", va="baseline")
    p = top
    for (ec, head, body), h in zip(notes, nh):
        c.panel(51, p, 47, h, head, body, ec=ec)
        p += h + GAP
    c.save("fig6_orbits.png")


# ---------------------------------------------------------------- Figure 7
def fig7():
    cols = [
        (2, "1 · Connection with all", "sakala-mūrta-dravya-saṁyogitā", TEAL,
         "ananta = connected with every\nformed thing. But no one can\nknow all formed things — so\n"
         "ananta here turns into ajñeya,\nthe unknowable."),
        (35, "2 · Freedom from limits", "trividha-pariccheda-rāhitya", TEAL,
         "free of the limits of place,\ntime and thing. A negative\ndefinition, like 'colourless'\n"
         "or 'formless': no picture\nforms in the mind."),
        (68, "3 · Endless forms", "anantamūrtitā — Mahāprabhuji", MAROON,
         "not one mūrti but countless —\nwhat pervades all numbers,\nikāī … padma and beyond.\n"
         "Viruddha-dharmāśrayatā:\nendless yet formed, formed\nyet endless."),
    ]
    line1 = "Saṅkhyā = samyak khyāti, what is properly cognised; ananta is the asaṅkhya."
    line2 = ("A positive term ('lion') conveys something; a negative one ('not lion') conveys nothing —\n"
             "or everything.")
    ch = max(panel_h(b, sub=True) for *_, b in cols)
    total = TITLE_BLOCK + ch + 12 + banner_h(line2) + 4
    c = Canvas(total)
    c.title("Three readings of ananta", "anantamūrti tad brahma")
    for x, head, sub, ec, body in cols:
        c.panel(x, TITLE_BLOCK, 30, ch, head, body, ec=ec, sub=sub, sub_size=6.4)
    mid = TITLE_BLOCK + ch / 2
    c.arrow(32.3, mid, 34.7, mid, color=GREY, ms=8)
    c.arrow(65.3, mid, 67.7, mid)
    c.banner(TITLE_BLOCK + ch + 12, line1, line2, ec=OCHRE)
    c.save("fig7_ananta.png")


# ---------------------------------------------------------------- Figure 8
def fig8():
    cols = [
        (2, "Assembly", "theory of assembly",
         "atoms or spare parts join\ninto a structure — the car"),
        (35, "Appearance", "kaleidoscope · ābhāsa",
         "the bangle-pieces never join;\nthree mirrors make a design\nthat is only appearance —\n"
         "Buddha's pratītya-samutpāda"),
        (68, "Transformation", "vikāravāda",
         "the cause turns into effects,\nwhether by vikṛta- or even\navikṛta-pariṇāma"),
    ]
    vbody = ("In the undivided, division appears by the undivided's own icchā: as much of its sattā, cetanā and\n"
             "ānanda as it chooses to show is vibhāga, kārya; the rest remains kāraṇa, svarūpa.\n"
             "The face is one — how much the ghūṅghaṭ reveals is the wearer's will. Pond-moss gathers where the\n"
             "light falls — Brahman shows a division where, when and for whom it wills.\n"
             "Avikṛta-pariṇāma and āvirbhāva-tirobhāva come under this kārya-kāraṇa-bhāva.")
    line1 = "Avibhaktaṁ vibhaktimat: one Godāvarī through many kuṇḍas."
    line2 = ("But the kuṇḍas are ours, like Henry's foot laid on a slab; Brahman's divisions are its own,\n"
             "for time, space, māyā and jīva are themselves among them.")
    ch = max(panel_h(b, sub=True) for *_, b in cols)
    vh = 23.0 + nlines(vbody) * BODY * 1.4 + 8.0
    total = TITLE_BLOCK + ch + 11 + vh + 12 + banner_h(line2) + 4
    c = Canvas(total)
    c.title("How do the many come from the one?", "four ontologies")
    for x, head, sub, body in cols:
        c.panel(x, TITLE_BLOCK, 30, ch, head, body, ec=TEAL, sub=sub)
    vt = TITLE_BLOCK + ch + 11
    c.box(2, vt, 96, vh, ec=MAROON, fc=WHITE, lw=1.9)
    c.text(50, vt + 14.0, "Vibhāgavāda — Mahāprabhuji's root view", size=9.0, color=MAROON,
           ha="center", va="baseline", weight="bold")
    c.text(4.0, vt + 22.0, vbody, ls=1.4)
    c.banner(vt + vh + 12, line1, line2, ec=OCHRE)
    c.save("fig8_ontology.png")


def contact_sheet():
    from PIL import Image

    files = sorted(OUT.glob("fig*_*.png"))
    ims = [Image.open(f).convert("RGB") for f in files]
    w = max(i.width for i in ims)
    half = w // 2
    thumbs = [i.resize((half, int(i.height * half / i.width))) for i in ims]
    rows = [thumbs[k:k + 2] for k in range(0, len(thumbs), 2)]
    height = sum(max(t.height for t in r) for r in rows)
    sheet = Image.new("RGB", (w, height), "white")
    y = 0
    for r in rows:
        x = 0
        for t in r:
            sheet.paste(t, (x, y))
            x += t.width
        y += max(t.height for t in r)
    sheet.save(OUT / "contact11.png")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        f()
    contact_sheet()
    print("done:", ", ".join(p.name for p in sorted(OUT.glob("*.png"))))
