#!/usr/bin/env python3
"""Figures for Lecture 4 (2026-08-01) of the Śāstrārtha Prakaraṇa series.

Every box is sized from its own text and each figure is laid out from the top
down; the empty space left at the bottom is trimmed by bbox_inches="tight".
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image, ImageChops

plt.rcParams["font.family"] = "DejaVu Sans"

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"
WHITE = "#FFFFFF"

OUT = Path(__file__).resolve().parent / "figs04"
OUT.mkdir(exist_ok=True)

W = 6.2
SUB = 6.5  # size of italic sub-headers inside boxes


def nlines(s):
    return 0 if not s else s.count("\n") + 1


class Fig:
    def __init__(self, h):
        self.h = h
        self.fig = plt.figure(figsize=(W, h), dpi=200)
        self.fig.patch.set_facecolor(PALE)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis("off")
        self.ax.patch.set_visible(False)  # keep it out of the tight bbox

    # -- measures (y-units)
    def lh(self, size):
        return size * 1.36 / 72 * 100 / self.h

    def need(self, head, body=None, sub=None, hsize=8.6, bsize=6.8, gap=1.2):
        h = 1.6 + self.lh(hsize)
        if sub:
            h += 0.5 + nlines(sub) * self.lh(SUB)
        if body:
            h += gap + nlines(body) * self.lh(bsize)
        return h + 1.9

    # -- primitives
    def box(self, x, y, w, h, ec=TEAL, fc=SAND, lw=1.1, z=1):
        self.ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.012,rounding_size=1.1",
            mutation_aspect=W / self.h, ec=ec, fc=fc, lw=lw, zorder=z))

    def text(self, x, y, s, size=6.8, color=INK, ha="left", va="top",
             weight="normal", style="normal", z=5):
        self.ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va,
                     fontweight=weight, fontstyle=style, zorder=z,
                     linespacing=1.35)

    def title(self, t, sub):
        self.text(50, 98.8, t, size=12, weight="bold", ha="center")
        self.text(50, 98.8 - self.lh(12) - 1.0, sub, size=7.4, color=GREY,
                  ha="center", style="italic")
        return 98.8 - self.lh(12) - 1.0 - self.lh(7.4) - 2.6

    def panel(self, x, top, w, h, head, body=None, sub=None, ec=TEAL, fc=SAND,
              hsize=8.6, bsize=6.8, gap=1.2, hcolor=None, lw=1.1):
        """Header centred near the top; sub-header and body top-anchored."""
        self.box(x, top - h, w, h, ec=ec, fc=fc, lw=lw)
        y = top - 1.6
        self.text(x + w / 2, y, head, size=hsize, weight="bold",
                  color=hcolor or ec, ha="center")
        y -= self.lh(hsize)
        if sub:
            y -= 0.5
            self.text(x + w / 2, y, sub, size=SUB, color=GREY, style="italic",
                      ha="center")
            y -= nlines(sub) * self.lh(SUB)
        if body:
            self.text(x + 1.8, y - gap, body, size=bsize)

    def banner(self, top, s, size=7.2, x=3, w=94):
        h = 1.7 + nlines(s) * self.lh(size) + 1.5
        self.box(x, top - h, w, h, ec=OCHRE, fc=OCHRE, lw=1.0)
        self.text(x + w / 2, top - 1.7, s, size=size, color=WHITE,
                  weight="bold", ha="center")
        return top - h

    def arrow(self, x1, y1, x2, y2, color=OCHRE, lw=1.3, rad=0.0, ms=10):
        self.ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=ms,
            color=color, lw=lw, connectionstyle=f"arc3,rad={rad}", zorder=4,
            shrinkA=0, shrinkB=0))

    def save(self, name):
        path = OUT / name
        self.fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.12,
                         facecolor=PALE)
        plt.close(self.fig)
        trim(path)
        print("wrote", path.name)


def trim(path, margin=24):
    """Crop the unused background left below a top-down layout.

    matplotlib counts the whole (invisible) axes in the tight bbox, so the
    blank tail is removed here, keeping the same 0.12 in (24 px) margin.
    """
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, PALE)
    box = ImageChops.difference(im, bg).getbbox()
    if box is None:
        return
    x0, y0, x1, y1 = box
    im.crop((max(0, x0 - margin), max(0, y0 - margin),
             min(im.width, x1 + margin), min(im.height, y1 + margin))
            ).save(path, dpi=(200, 200))


GAP = 2.6  # vertical gap between rows (y-units)


# ---------------------------------------------------------------- Figure 1
def fig1():
    f = Fig(5.0)
    top = f.title("Propositional functions and the tautology",
                  "Truth values as the speaker recites them, “to be learnt like "
                  "multiplication tables”")
    cols = [("P", 7.0, ""), ("Q", 7.0, ""), ("P ⊃ Q", 19.5, "implication"),
            ("P · Q", 19.5, "conjunction"),
            ("P ∨ Q", 19.5, "disjunction (weak “vel”)"),
            ("P ≡ Q", 19.5, "equivalence")]
    rows = [("T", "T", "T", "T", "T", "T"),
            ("T", "F", "F", "F", "T", "F"),
            ("F", "T", "T", "F", "T", "F"),
            ("F", "F", "T", "F", "F", "T")]
    examples = ["", "", "if smoke, then fire", "it rained and\nthe ground is wet",
                "tea or biscuits?\n“both” is fine", "true together,\nfalse together"]
    hh, rh = 9.4, 6.0
    x = 4.0
    for j, ((lab, w, nm), ex) in enumerate(zip(cols, examples)):
        f.box(x + 0.4, top - hh, w - 0.8, hh, ec=TEAL, fc=TEAL)
        f.text(x + w / 2, top - 1.3, lab, size=9, weight="bold", color=WHITE,
               ha="center")
        if nm:
            f.text(x + w / 2, top - 1.3 - f.lh(9) - 0.4, nm, size=6.3,
                   color=WHITE, ha="center")
        for i, r in enumerate(rows):
            yb = top - hh - (i + 1) * rh
            f.box(x + 0.4, yb + 0.3, w - 0.8, rh - 0.6, ec=GREY,
                  fc=SAND if i % 2 == 0 else PALE, lw=0.5)
            val = r[j]
            f.text(x + w / 2, yb + rh / 2, val, size=8.4, va="center",
                   ha="center", weight="bold" if val == "T" else "normal",
                   color=INK if val == "T" else GREY)
        if ex:
            f.text(x + w / 2, top - hh - 4 * rh - 1.2, ex, size=6.3,
                   color=GREY, style="italic", ha="center")
        x += w
    top = top - hh - 4 * rh - 1.2 - 2 * f.lh(6.3) - GAP
    b1 = ("Tea or Coca-Cola? Hot or cold?\nOne of the two must be true:\n"
          "answering “both” sounds odd.")
    b2 = ("P ⊃ Q   ≡   not-P ∨ Q\nThe same content in another format:\n"
          "no new information “formats the mind”.")
    h = max(f.need("Strong “or” (aut)", b1), f.need("Tautology", b2))
    f.panel(4, top, 44, h, "Strong “or” (aut)", b1, ec=TEAL)
    f.panel(52, top, 44, h, "Tautology", b2, ec=MAROON)
    f.banner(top - h - GAP, "A tautology needs no further reason: it is "
             "svataḥ-siddha, as the commentary says of the Veda", x=4, w=92)
    f.save("fig1_truth_tables.png")


# ---------------------------------------------------------------- Figure 2
def fig2():
    f = Fig(5.6)
    top = f.title("Two reasons, two functions",
                  "The speaker's answer to the charge that the Veda's authority "
                  "is circular")
    ob = ("“The Veda is pramāṇa because it is Bhagavān's speech; Bhagavān is "
          "established because\nthe Veda is pramāṇa”: is this anyonyāśraya?")
    h = f.need("The objection at Gandhinagar", ob, hsize=8.2, bsize=6.7)
    f.panel(3, top, 94, h, "The objection at Gandhinagar", ob, ec=GREY,
            fc=PALE, hsize=8.2, bsize=6.7)
    top -= h + GAP
    ph = 48.5
    f.panel(3, top, 46, ph, "Kāraka-hetu and jñāpaka-hetu", ec=MAROON)
    f.panel(51, top, 46, ph, "When it is anyonyāśraya", ec=TEAL)
    lab1 = top - 1.6 - f.lh(8.6) - 2.2          # first label line
    bx_top = lab1 - 2 * f.lh(6.7) - 6.6          # top of the small boxes
    bh = 8.0
    for x, name, sub, ec in ((7, "Fire", "P", MAROON), (32, "Smoke", "Q", MAROON),
                             (55, "P", None, TEAL), (80, "Q", None, TEAL)):
        f.box(x, bx_top - bh, 13, bh, ec=ec, fc=PALE)
        f.text(x + 6.5, bx_top - 1.5, name, size=8.2, weight="bold", color=ec,
               ha="center")
        if sub:
            f.text(x + 6.5, bx_top - 1.5 - f.lh(8.2) - 0.2, sub, size=6.4,
                   color=GREY, ha="center")
    ya, yb = bx_top - 1.8, bx_top - bh + 1.8
    f.arrow(20.2, ya, 31.8, ya, rad=-0.55)
    f.arrow(31.8, yb, 20.2, yb, rad=-0.55)
    f.text(26, lab1, "kāraka-hetu: brings about", size=6.7, weight="bold",
           color=OCHRE, ha="center")
    f.text(26, lab1 - f.lh(6.7), "“ratio essendi”", size=6.5, color=GREY,
           style="italic", ha="center")
    lab2 = bx_top - bh - 6.4
    f.text(26, lab2, "jñāpaka-hetu: makes known", size=6.7, weight="bold",
           color=OCHRE, ha="center")
    f.text(26, lab2 - f.lh(6.7), "“ratio cognoscendi”", size=6.5, color=GREY,
           style="italic", ha="center")
    f.arrow(79.8, ya, 68.2, ya, color=TEAL, rad=0.55)
    f.arrow(68.2, yb, 79.8, yb, color=TEAL, rad=0.55)
    f.text(74, lab1 - f.lh(6.7) * 0.5, "P is true because Q is true", size=6.6,
           color=TEAL, ha="center")
    f.text(74, lab2 - f.lh(6.7) * 0.5, "Q is true because P is true", size=6.6,
           color=TEAL, ha="center")
    body_top = lab2 - 2 * f.lh(6.7) - 2.0
    f.text(5, body_top,
           "Smoke can make fire known only because fire\n"
           "produced it. Two different functions, so there\n"
           "is no anyonyāśraya and the reasoning holds.", size=6.6)
    f.text(53, body_top,
           "P born of Q and Q born of P: kārakatā and\n"
           "jñāpakatā are both broken, and the logic is\n"
           "no longer valid, though the matter may be true.", size=6.6)
    top -= ph + GAP
    trio = [("Mother and child", "No mother until a child is born,\n"
             "no child without a mother: logic\ncries anyonyāśraya; reality is so."),
            ("The unsigned loan", "Borrowed, but no signature:\n"
             "legally invalid, while the money\nwas in fact borrowed."),
            ("No “romance”", "Logical, legal and factual truth\n"
             "go their own ways, and each must\nbe judged in its own way.")]
    h = max(f.need(a, b, hsize=7.8, bsize=6.4) for a, b in trio)
    for i, (a, b) in enumerate(trio):
        f.panel(3 + i * 32, top, 30, h, a, b, ec=GREY, fc=PALE, hsize=7.8,
                bsize=6.4)
    f.banner(top - h - GAP, "What logic calls invalid may in reality be true: "
             "logic has its limitations", size=7.0)
    f.save("fig2_karaka_jnapaka.png")


# ---------------------------------------------------------------- Figure 3
def fig3():
    f = Fig(4.8)
    top = f.title("Which pramāṇa fits which concept",
                  "Every concept has a verbal part; only a verbal concept is "
                  "proved by the word alone")
    cols = [("Empirical concept", "settled by pratyakṣa", TEAL,
             "“This is a telescope.” The eye\n"
             "sees spectacles, not a telescope.\n"
             "Gather the definitions and the\n"
             "designs, look again, and the\n"
             "claim is disproved."),
            ("Logical concept", "settled by anumāna", TEAL,
             "“There is smoke, so there is\n"
             "fire.” Two things seen together\n"
             "before: when one is seen, the\n"
             "other is inferred."),
            ("Verbal concept", "settled by śabda alone", MAROON,
             "“These spectacles were given to\n"
             "me by Dharmesh-bhāī.” No logic\n"
             "and no perception reach it:\n"
             "only the word. So too the hero\n"
             "and villain of a fictional play,\n"
             "and Brahman, Paramātmā and\n"
             "Bhagavān in the Veda.")]
    h = max(f.need(a, d, sub=b) for a, b, c, d in cols)
    for i, (a, b, c, d) in enumerate(cols):
        f.panel(3 + i * 32, top, 30, h, a, d, sub=b, ec=c)
    top -= h + GAP
    com = ("vedā iti śabda eva pramāṇam  ·  tatrāpi alaukika-jñāpakam eva  ·  "
           "tat svataḥ-siddha-pramāṇa-bhāvam\n"
           "By “Veda” is meant the word; among words, the one that makes the "
           "alaukika known; and its authority\nis self-established.")
    h = f.need("The commentary on the Veda as pramāṇa", com, hsize=8.2,
               bsize=6.6)
    f.panel(3, top, 94, h, "The commentary on the Veda as pramāṇa", com,
            ec=GREY, fc=PALE, hsize=8.2, bsize=6.6)
    f.banner(top - h - GAP, "A verbal concept is proved verbally: calling it "
             "“illogical” misses what kind of concept it is")
    f.save("fig3_concepts.png")


# ---------------------------------------------------------------- Figure 4
def fig4():
    f = Fig(5.3)
    top = f.title("Utpatti, jñapti, sthiti",
                  "Where each pramāṇa leans on another, as the speaker sets it out")
    cx, cw = [21, 47, 73], 24
    hh = 1.4 + f.lh(8.8) + 0.4 + f.lh(6.4) + 1.6
    for x, (h_, s) in zip(cx, [("Utpatti", "coming to be"),
                               ("Jñapti", "making known"),
                               ("Sthiti", "staying")]):
        f.box(x, top - hh, cw, hh, ec=TEAL, fc=TEAL)
        f.text(x + cw / 2, top - 1.4, h_, size=8.8, weight="bold", color=WHITE,
               ha="center")
        f.text(x + cw / 2, top - 1.4 - f.lh(8.8) - 0.4, s, size=6.4,
               color=WHITE, ha="center", style="italic")
    top -= hh + 1.6
    cells = {
        "Pratyakṣa": ["Free of words: a newborn\nsees and hears with no\nvocabulary.",
                      "To say what is seen, a word\nis needed: “I can't\nrecognise it.”",
                      None],
        "Śabda": ["Leans on perception: the\nword must have been heard,\n"
                  "its meaning shown: “Beta,\nthis is a cow.”",
                  "Stands on its own: the\nthing need not be present:\n"
                  "dinosaurs, the Big Bang.",
                  "Once heard, it stays; no\none need keep speaking\nlike a machine."],
        "Anumāna": ["Leans on perception and\nword: two things seen\ntogether before.",
                    "Then works on its own:\nseeing one, the other\nis inferred.",
                    None],
    }
    rh = 1.8 + 4 * f.lh(6.5) + 1.8
    for name, sub, ec in (("Pratyakṣa", "perception", TEAL),
                          ("Śabda", "word", MAROON),
                          ("Anumāna", "inference", TEAL)):
        f.box(3, top - rh, 16, rh, ec=ec, fc=ec)
        f.text(11, top - rh / 2 + 1.6, name, size=8.4, weight="bold",
               color=WHITE, ha="center", va="center")
        f.text(11, top - rh / 2 - 2.0, sub, size=6.4, color=WHITE,
               ha="center", va="center", style="italic")
        for x, body in zip(cx, cells[name]):
            if body is None:
                f.box(x, top - rh, cw, rh, ec=GREY, fc=PALE, lw=0.6)
                f.text(x + cw / 2, top - rh / 2, "not discussed", size=6.3,
                       color=GREY, style="italic", ha="center", va="center")
            else:
                f.box(x, top - rh, cw, rh, ec=ec, fc=SAND, lw=1.0)
                f.text(x + 1.6, top - 1.8, body, size=6.5)
        top -= rh + 1.6
    f.text(3, top - 0.4, "The pen: it depends on the factory to come into "
           "being, but not to write.", size=6.5, color=GREY, style="italic")
    f.banner(top - 0.4 - f.lh(6.5) - GAP,
             "Śabda leans on perception only in its utpatti:\n"
             "so calling śabda “blind faith” is the greatest blind faith")
    f.save("fig4_utpatti_grid.png")


# ---------------------------------------------------------------- Figure 5
def fig5():
    f = Fig(5.4)
    top = f.title("Half a Veda, or the whole",
                  "Sarvanāśe samutpanne ardhaṁ tyajati paṇḍitaḥ: after the Jaina "
                  "and Bauddha attack, each school kept half")
    cols = [("Kabandha-Mīmāṁsā", "keeps the trunk:\nkarma-kāṇḍa (Śabara)", TEAL,
             "Āmnāyasya kriyārthatvāt: the\n"
             "Veda exists to guide duty.\n"
             "Only imperatives convey\n"
             "meaning; descriptive state-\n"
             "ments merely restate (anuvāda);\n"
             "arthavāda counts only as\n"
             "praise of a vidhi.\n\n"
             "Casualty: “Bhagavān makes,\n"
             "sustains and absorbs the\n"
             "world” has no bearing on\n"
             "duty, so it is not pramāṇa."),
            ("Rāhu-Vedānta", "keeps the head:\njñāna-kāṇḍa (Śaṅkara)", TEAL,
             "Imperatives lure like grass\n"
             "shown to a donkey before the\n"
             "stick: paśvādibhiś cāviśeṣāt.\n"
             "Whoever commands treats the\n"
             "listener as a beast, so the\n"
             "karma-kāṇḍa is useless;\n"
             "descriptive statements make\n"
             "reality understood."),
            ("Mahāprabhuji", "kāṇḍa-dvaya:\nboth are pramāṇa", MAROON,
             "Vedāḥ sarva eva kāṇḍa-dvaya-\n"
             "sthitāḥ, arthavāda included.\n"
             "The kāṇḍas are complementary,\n"
             "hence independent: the Veda\n"
             "is “two in one”.\n\n"
             "Upāsanā (devatā, Saṅkarṣaṇa)\n"
             "runs through both; with us it\n"
             "is called bhakti, a līlā.\n\n"
             "The same point, made\n"
             "without abuse.")]
    h = max(f.need(a, d, sub=b) for a, b, c, d in cols)
    for i, (a, b, c, d) in enumerate(cols):
        f.panel(3 + i * 32, top, 30, h, a, d, sub=b, ec=c)
    f.banner(top - h - GAP, "Knowledge and action rest on each other: pure "
             "knowledge and pure action occur nowhere")
    f.save("fig5_kandas.png")


# ---------------------------------------------------------------- Figure 6
def fig6():
    f = Fig(4.8)
    top = f.title("Three registers of speech",
                  "Prabhu-, suhṛt- and kāntā-sammita bhāṣā, and why the Gītā is "
                  "counted as smṛti")
    cols = [("Prabhu-sammita", "master to servant\nthe Veda", TEAL,
             "“Do this, or you will go to\n"
             "hell; do this, and you will\n"
             "reach Vaikuṇṭha.” A command\n"
             "that leaves no choice: the\n"
             "“do or die” language."),
            ("Suhṛt- / mitra-sammita", "friend to friend\nsmṛti", MAROON,
             "Kṛṣṇa as charioteer, not guru:\n"
             "bhakto ’si me sakhā ceti (4.3);\n"
             "kaccid etac chrutam (18.72);\n"
             "yathecchasi tathā kuru (18.63).\n\n"
             "Rajo-bāī, too, answered\n"
             "Mahāprabhuji over the ghee\n"
             "as a friend speaks."),
            ("Kāntā-sammita", "wife to husband\npoetry", TEAL,
             "Persuasion, ullū paṭānā:\n"
             "“The neighbour brings his\n"
             "wife a new sari on every\n"
             "birthday…” She never says,\n"
             "“Give me a sari.”")]
    h = max(f.need(a, d, sub=b) for a, b, c, d in cols)
    for i, (a, b, c, d) in enumerate(cols):
        f.panel(3 + i * 32, top, 30, h, a, d, sub=b, ec=c)
    f.banner(top - h - GAP,
             "Kṛṣṇa's words are Veda, yet they are listed separately “as smṛti”\n"
             "(smṛtitvena pṛthag uktāni): the tone has changed")
    f.save("fig6_registers.png")


# ---------------------------------------------------------------- Figure 7
def fig7():
    f = Fig(5.4)
    top = f.title("Who gives the fruit: karma or Īśvara?",
                  "Jaimini and Vyāsa, the Jaina–Bauddha challenge, and "
                  "Mahāprabhuji's answer")
    ch = ("If Īśvara gives by looking at karma, karma\n"
          "suffices: Occam's razor. If he gives without\n"
          "looking, he is partial, a man like us.")
    h = max(f.need("Jaimini", "Karma gives\nthe fruit."),
            f.need("The Jaina–Bauddha challenge", ch),
            f.need("Vyāsa", "Īśvara gives\nthe fruit.", sub="(Bādarāyaṇa)"))
    f.panel(3, top, 22, h, "Jaimini", "Karma gives\nthe fruit.", ec=TEAL)
    f.panel(27, top, 46, h, "The Jaina–Bauddha challenge", ch, ec=GREY,
            fc=PALE)
    f.panel(75, top, 22, h, "Vyāsa", "Īśvara gives\nthe fruit.",
            sub="(Bādarāyaṇa)", ec=TEAL)
    top -= h + 1.8
    f.text(50, top, "Possible ways of combining or choosing", size=6.6,
           color=GREY, style="italic", ha="center")
    top -= f.lh(6.6) + 1.0
    sh = 1.6 + 2 * f.lh(6.5) + 1.6
    for i, s in enumerate(["Īśvara gives,\nthrough karma",
                           "Karma gives, by\nĪśvara's leave",
                           "Only karma;\nno Īśvara needed",
                           "Only Īśvara;\nno karma needed"]):
        x = 3 + i * 24
        f.box(x, top - sh, 22, sh, ec=GREY, fc=PALE, lw=0.7)
        f.text(x + 11, top - 1.6, s, size=6.5, ha="center")
    top -= sh + GAP
    m = ("Hari himself has taken the form of karma.\n"
         "Karma is one form of Hari; Hari is not a\n"
         "form of karma. Karma and the giver of the\n"
         "fruit are not two but two forms of one,\n"
         "so the quarrel itself is false.")
    s = ("Dādājī would not pay, but\n"
         "petitioned two trusts; the\n"
         "trustees, under his influence,\n"
         "granted it. From the trust, or\n"
         "from Dādājī? The father acted\n"
         "through the trust.")
    h = max(f.need("Mahāprabhuji", m), f.need("The scholarship", s))
    f.panel(3, top, 52, h, "Mahāprabhuji", m, ec=MAROON)
    f.panel(58, top, 39, h, "The scholarship", s, ec=TEAL)
    f.banner(top - h - GAP,
             "Jaimini is accepted where he is not opposed to Vyāsa (evakāra),\n"
             "for Vyāsa is upajīvya: coordination without abuse")
    f.save("fig7_fruit.png")


# ---------------------------------------------------------------- Figure 8
def fig8():
    f = Fig(5.8)
    top = f.title("Four sources, one sentence",
                  "Śāstrārtha Prakaraṇa 7 with the commentary, and the three tests "
                  "of truth")
    tops = [("Veda", "Śabda as alaukika-\njñāpaka; both kāṇḍas,\narthavāda too."),
            ("Kṛṣṇa-vākya", "The Gītā: Veda, yet\nlisted apart “as\nsmṛti”."),
            ("Vyāsa-sūtra", "Orders the Upaniṣads;\n“ca” admits Jaimini\n"
                            "where not opposed\nto Vyāsa."),
            ("Samādhi-bhāṣā", "The Bhāgavata: what\nVyāsa himself saw in\n"
                              "samādhi; not laukika,\nnot paramata.")]
    h = max(f.need(a, b, hsize=8.2, bsize=6.4) for a, b in tops)
    for i, (a, b) in enumerate(tops):
        f.panel(3 + i * 24, top, 22, h, a, b, ec=TEAL, hsize=8.2, bsize=6.4)
        if i < 3:
            f.arrow(3 + i * 24 + 22.2, top - h / 2, 3 + i * 24 + 23.8,
                    top - h / 2, ms=8, lw=1.1)
    vtop = top - h - 7.0
    for i in range(4):
        x = 3 + i * 24 + 11
        f.arrow(x, top - h - 0.4, 50 + (x - 50) * 0.55, vtop + 0.4, lw=1.1,
                ms=8)
    vb = ("The unity of the four as one sentence is the pramāṇa: not four "
          "pramāṇas, not a “prasthāna-catuṣṭaya”.")
    vh = f.need("etac catuṣṭayam ekavākyatāpannaṁ pramā-janakam", vb,
                hsize=8.2, bsize=6.6)
    f.panel(10, vtop, 80, vh, "etac catuṣṭayam ekavākyatāpannaṁ pramā-janakam",
            vb, ec=MAROON, hsize=8.2, bsize=6.6)
    top = vtop - vh - 6.0
    f.text(50, top + 3.6, "Three tests of truth", size=6.8, color=GREY,
           style="italic", ha="center")
    tests = [("Correspondence", TEAL,
              "Knowledge must be checked\nagainst its object by other\n"
              "knowledge: impossible in a\ndream, which seems true."),
             ("Utility", TEAL,
              "The placebo; Nirmalā Devī's\nkick; the mole on a self-drawn\n"
              "vidyā-rekhā: true by use,\nyet not pramāṇa."),
             ("Coherence", MAROON,
              "Where neither can be checked:\nthe Veda in the Gītā, the Gītā\n"
              "in the Brahmasūtra, that in the\nsamādhi-bhāṣā; BS 1 samanvaya,\n"
              "BS 2 avirodha.")]
    th = max(f.need(a, c, hsize=8.0, bsize=6.4) for a, b, c in tests)
    for i, (a, b, c) in enumerate(tests):
        f.panel(3 + i * 32, top, 30, th, a, c, ec=b, hsize=8.0, bsize=6.4)
    f.arrow(84, top + 0.4, 76, vtop - vh - 0.4, lw=1.2)
    f.banner(top - th - GAP,
             "Where correspondence and utility cannot be verified, coherence "
             "remains:\nthe four are read as one sentence")
    f.save("fig8_four_one.png")


if __name__ == "__main__":
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        fn()
