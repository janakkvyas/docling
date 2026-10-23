#!/usr/bin/env python3
"""Figures for Lecture 6 (2026-08-15) of the Śāstrārtha Prakaraṇa series.

House style: matplotlib Agg, DejaVu Sans, width 6.2 in, dpi 200, axes 0-100 both ways,
IAST and English only. Vertical layout is planned in inches (box heights are computed from
their text) and converted to the 0-100 axes, so boxes fit their contents.
Run from build/: python3 make_figs06.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path as MPath

plt.rcParams["font.family"] = "DejaVu Sans"

MAROON = "#7B2D26"
OCHRE = "#C46210"
TEAL = "#2C4A52"
SAND = "#F5EDE0"
PALE = "#FBF7F0"
GREY = "#8A8078"
INK = "#2B2320"
WHITE = "#FFFFFF"

OUT = Path(__file__).resolve().parent / "figs06"
OUT.mkdir(exist_ok=True)
FIG_W = 6.2

TOP_PAD = 0.085     # inches from box top to header top
HEAD_LS = 1.17      # header line spacing factor
BODY_LS = 1.28      # body line spacing factor
GAP_HB = 0.065      # inches between header block and body block
BOT_PAD = 0.085     # inches below the last body line
ASC = 1.0           # header ascent (em) above the first baseline, room for accents such as Ś, ā
DESC = 0.24         # header descent (em) below the last baseline


def n_lines(text: str | None) -> int:
    return 0 if not text else text.count("\n") + 1


def box_h(header=None, body=None, hsize=8.6, bsize=6.8) -> float:
    """Height in inches that a box needs for its header and body."""
    h = TOP_PAD + BOT_PAD
    if header:
        h += (ASC + (n_lines(header) - 1) * HEAD_LS + DESC) * hsize / 72
    if header and body:
        h += GAP_HB
    if body:
        h += n_lines(body) * bsize * BODY_LS / 72
    return h


class Canvas:
    """0-100 x 0-100 axes on a 6.2-in-wide figure; vertical positions given in inches from the top."""

    def __init__(self, height_in: float):
        self.H = height_in
        self.fig = plt.figure(figsize=(FIG_W, height_in), facecolor=PALE)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis("off")
        self.pairs: list[tuple] = []

    def Y(self, inch_from_top: float) -> float:
        return 100 - inch_from_top / self.H * 100

    def U(self, inches: float) -> float:
        return inches / self.H * 100

    def title(self, text, top_in=0.10, size=12.0):
        self.ax.text(50, self.Y(top_in), text, ha="center", va="top", fontsize=size, fontweight="bold", color=INK)

    def note(self, top_in, text, size=6.6, color=GREY, italic=True, x=50, ha="center", bold=False):
        return self.ax.text(x, self.Y(top_in), text, ha=ha, va="top", fontsize=size, color=color,
                            style="italic" if italic else "normal", fontweight="bold" if bold else "normal",
                            linespacing=1.25, zorder=4)

    def box(self, x, top_in, w, h_in, header=None, body=None, edge=TEAL, fill=SAND, lw=1.0,
            hsize=8.6, bsize=6.8, hcolor=None, bcolor=INK, body_ha="center"):
        y0 = self.Y(top_in + h_in)
        patch = FancyBboxPatch((x, y0), w, self.U(h_in), boxstyle="round,pad=0.012,rounding_size=1.4",
                               linewidth=lw, edgecolor=edge, facecolor=fill, zorder=2)
        self.ax.add_patch(patch)
        cursor = top_in + TOP_PAD
        if header:
            # one text per line, placed on computed baselines so first lines align across a row
            for k, line in enumerate(header.split("\n")):
                base = cursor + (ASC + k * HEAD_LS) * hsize / 72
                t = self.ax.text(x + w / 2, self.Y(base), line, ha="center", va="baseline", fontsize=hsize,
                                 fontweight="bold", color=hcolor or edge, zorder=3)
                self.pairs.append((t, patch))
            cursor += (ASC + (n_lines(header) - 1) * HEAD_LS + DESC) * hsize / 72 + GAP_HB
        if body:
            bx = x + w / 2 if body_ha == "center" else x + 1.8
            t = self.ax.text(bx, self.Y(cursor), body, ha=body_ha, va="top", fontsize=bsize, color=bcolor,
                             zorder=3, linespacing=BODY_LS)
            self.pairs.append((t, patch))
        return patch

    def banner(self, top_in, text, size=7.2):
        h_in = box_h(body=text, bsize=size) + 0.06
        patch = FancyBboxPatch((3, self.Y(top_in + h_in)), 94, self.U(h_in),
                               boxstyle="round,pad=0.012,rounding_size=1.4", linewidth=0, facecolor=OCHRE, zorder=2)
        self.ax.add_patch(patch)
        t = self.ax.text(50, self.Y(top_in + h_in / 2), text, ha="center", va="center", fontsize=size,
                         fontweight="bold", color=WHITE, zorder=3, linespacing=1.3)
        self.pairs.append((t, patch))
        return h_in

    def arrow(self, x1, y1_in, x2, y2_in, color=OCHRE, lw=1.3, rad=0.0, ms=9):
        self.ax.add_patch(FancyArrowPatch((x1, self.Y(y1_in)), (x2, self.Y(y2_in)), arrowstyle="-|>",
                                          mutation_scale=ms, color=color, linewidth=lw,
                                          connectionstyle=f"arc3,rad={rad}", zorder=1.5, shrinkA=0, shrinkB=0))

    def line_in(self, xs, ys_in, color=INK, lw=0.9):
        self.ax.plot(xs, [self.Y(v) for v in ys_in], color=color, linewidth=lw, zorder=1.4,
                     solid_capstyle="butt")

    def tree(self, px, p_in, child_xs, c_in, color=INK, bar_in=None):
        bar = bar_in if bar_in is not None else (p_in + c_in) / 2
        self.line_in([px, px], [p_in, bar], color)
        self.line_in([min(child_xs + [px]), max(child_xs + [px])], [bar, bar], color)
        for cx in child_xs:
            self.line_in([cx, cx], [bar, c_in], color)

    def save(self, name: str) -> Path:
        path = OUT / name
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        problems = []
        for text, patch in self.pairs:
            tb, pb = text.get_window_extent(renderer), patch.get_window_extent(renderer)
            m = 3.0  # px
            if tb.x0 < pb.x0 + m or tb.x1 > pb.x1 - m or tb.y0 < pb.y0 + m or tb.y1 > pb.y1 - m:
                problems.append(text.get_text().split("\n")[0][:45])
        fb = self.fig.bbox
        for t in self.ax.texts:
            tb = t.get_window_extent(renderer)
            if tb.x0 < fb.x0 + 2 or tb.x1 > fb.x1 - 2 or tb.y0 < fb.y0 + 2 or tb.y1 > fb.y1 - 2:
                problems.append("OUTSIDE: " + t.get_text().split("\n")[0][:40])
        # sibling text overlap check (texts not inside the same box)
        texts = self.ax.texts
        boxes = [tb for tb in (t.get_window_extent(renderer) for t in texts)]
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                if boxes[i].overlaps(boxes[j]):
                    problems.append("TEXT OVERLAP: " + texts[i].get_text()[:20] + " / " + texts[j].get_text()[:20])
        self.fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.12, facecolor=PALE)
        plt.close(self.fig)
        print(f"{name}: {'OK' if not problems else 'CHECK: ' + ' | '.join(problems)}  (H={self.H:.2f} in)")
        return path


# ---------------------------------------------------------------- Figure 1
def fig1() -> Path:
    heads = ["itaretarābhāva-\nrūpa", "itaretarābhāva-\nvyāpakatva", "itaretara-\nsahiṣṇutayā", "prayojana /\nphala-bheda"]
    bodies = [
        "Where this is, that\nis not; where that\nis, this is not: day\nand night, region by\nregion of the earth.\n\"Logical\" opposition.",
        "Where this is absent,\nthat is present: the\nabsence of one is\npervaded by the other.\n\"Logical\", not \"factual\".",
        "\"They cannot bear each\nother, nor live apart\":\ndonkeys, bulls, horses,\ngamblers, paṇḍits,\nchildren. Milder kind:\nSanskrit vs Persian.",
        "For imperative\nstatements: difference\nof purpose or fruit,\nwith adhikārī, deśa,\nkāla and avasthā\n(see Figure 4).",
    ]
    nat = ("What is all forms holds presence and absence\ntogether. At the poles day and night coexist;\n"
           "the whole city holds gutter and garden; suras\nand asuras are forms Bhagavān takes. A \"factual\"\n"
           "resolution, by svabhāva.")
    cap = ("If nature is not understood, accept Prabhu's\nalaukika capability to become everything\n"
           "(sarva-bhavana-sāmarthya): \"tāro Bhagavān is\ncapable\". Whichever one understands, use it,\n"
           "and keep no doubt.")
    ban = ("Exclusion is true \"for a limited area\"; where sarvarūpatā comes, the opposition is dissolved.\n"
           "Prakāśa: viruddhāṁśa-parityāga is twofold, by sāmarthya or by sarvarūpatva.")
    hb = max(box_h(h, b, 7.9, 6.5) for h, b in zip(heads, bodies))
    hr = max(box_h("x", nat, 8.6, 6.7), box_h("x", cap, 8.6, 6.7))
    root_top, root_h = 0.62, box_h("virodha-parihāra", None, 8.8)
    br_top = root_top + root_h + 0.26
    brace = br_top + hb + 0.12
    res_top = brace + 0.42
    ban_top = res_top + hr + 0.16
    H = ban_top + box_h(body=ban, bsize=7.2) + 0.06 + 0.10
    c = Canvas(H)
    c.title("Virodha-parihāra: four kinds of opposition and their dissolution")
    c.note(0.38, "after the speaker's chart, page 1")
    c.box(37, root_top, 26, root_h, header="virodha-parihāra", hsize=8.8)
    xs, w = [3, 27.5, 52, 76.5], 20.5
    c.tree(50, root_top + root_h, [x + w / 2 for x in xs], br_top)
    for x, hd, bd in zip(xs, heads, bodies):
        c.box(x, br_top, w, hb, header=hd, body=bd, hsize=7.9, bsize=6.5)
    # brace under the three tāttvika kinds
    c.line_in([4, 71.5], [brace, brace], GREY, 0.9)
    c.line_in([4, 4], [brace - 0.05, brace], GREY, 0.9)
    c.line_in([71.5, 71.5], [brace - 0.05, brace], GREY, 0.9)
    c.note(brace + 0.03, "the first three: tāttvika oppositions, in descriptive statements", size=6.4)
    c.arrow(30, brace + 0.17, 25, res_top - 0.03)
    c.arrow(46, brace + 0.17, 74.5, res_top - 0.03)
    c.box(3, res_top, 45, hr, header="by nature: sarvarūpatva", body=nat, edge=MAROON, lw=1.7, bsize=6.7)
    c.box(52, res_top, 45, hr, header="by capability: sāmarthya", body=cap, bsize=6.7)
    c.banner(ban_top, ban, size=7.2)
    return c.save("fig1_virodha_parihara.png")


# ---------------------------------------------------------------- Figure 2
def fig2() -> Path:
    med = "\"This medicine is for a cold.\"  (tattva)\n\"‹You have a cold›, so take this medicine.\"\n(kartavya)"
    dho = "\"Dhokla is tasty\" means \"eat it\".\nThe visiting professor: praise of the food\nis turned into a duty, \"then have more\"."
    ban = ("Because fact and duty blur into each other, the ways of resolving contradiction\n"
           "worked out for duty can be carried over to tattva.")
    r_in = 1.0
    circ_top = 0.62
    hb = max(box_h("x", med, 8.2, 6.7), box_h("x", dho, 8.2, 6.7))
    box_top = circ_top + 2 * r_in + 0.18
    ban_top = box_top + hb + 0.15
    H = ban_top + box_h(body=ban, bsize=7.2) + 0.06 + 0.10
    c = Canvas(H)
    c.title("Tattva and kartavya: no watertight compartment")
    c.note(0.38, "after the speaker's chart, page 1")
    rx, ry = r_in / FIG_W * 100, c.U(r_in)
    cy_in = circ_top + r_in
    lcx, rcx = 40.0, 60.0
    for cx in (lcx, rcx):
        c.ax.add_patch(Ellipse((cx, c.Y(cy_in)), 2 * rx, 2 * ry, facecolor=SAND, edgecolor=TEAL,
                               linewidth=1.3, alpha=0.8, zorder=1))
    left_mid = (lcx - rx + rcx - rx) / 2
    right_mid = (lcx + rx + rcx + rx) / 2
    c.note(cy_in - 0.62, "tattva", size=9.2, color=TEAL, italic=False, x=left_mid, bold=True)
    c.note(cy_in - 0.33, "\"fact\"\ndescriptive\nstatement\n\"involuntary\":\nnot governed\nby our will",
           size=6.5, color=INK, italic=False, x=left_mid)
    c.note(cy_in - 0.62, "kartavya", size=9.2, color=TEAL, italic=False, x=right_mid, bold=True)
    c.note(cy_in - 0.33, "\"duty\"\nimperative\nstatement\n\"voluntary\":\nwe may do it\nor not",
           size=6.5, color=INK, italic=False, x=right_mid)
    c.note(cy_in - 0.40, "\"grey\narea\"", size=7.6, color=MAROON, italic=False, bold=True)
    c.note(cy_in + 0.02, "blurred:\neach\ncarries\nthe other", size=6.2, color=MAROON, italic=False)
    c.box(3, box_top, 45, hb, header="one medicine, two statements", body=med, hsize=8.2, bsize=6.7)
    c.box(52, box_top, 45, hb, header="one dhokla, two statements", body=dho, hsize=8.2, bsize=6.7)
    c.banner(ban_top, ban)
    return c.save("fig2_tattva_kartavya.png")


# ---------------------------------------------------------------- Figure 3
def fig3() -> Path:
    heads = ["karmāṅga", "tīrtha", "grāma", "kula", "iṣṭa"]
    bodies = [
        "limb of a rite, e.g.\nGaṇeśa-sthāpanā\nat a wedding:\nfrom duty, not\nfrom desire",
        "the deva of a\ntīrtha, worshipped\nin that tīrtha:\nnot anyāśraya",
        "the village deity,\nwhen one goes to\nthat village; daily,\nas an iṣṭa:\nanyāśraya",
        "the family deity,\non a family\noccasion: not\nanyāśraya;\notherwise it is",
        "only one: two\niṣṭadevas are\nanyāśraya; the\nothers in their\nown setting\nare not",
    ]
    left = ("Karmāṅga deities serve the rite, like the air\nhostess who is there for your comfort. A role\n"
            "held for the occasion: the śrāddha brāhmaṇa\nis \"father\" while the rite lasts, the betel nut\n"
            "is Gaṇapati during the pūjā, and the Sun\nreceives arghya as a form of Nārāyaṇa.")
    right = ("The iṣṭadeva is not a means to anything: the\nworship is for him. A wife is still the wife,\n"
             "a husband still the husband, even in\ndiscomfort; he is not a salesman.")
    ban = ("Desire-worship goes to the deity who handles that desire (ask the police, not a doctor,\n"
           "for your railway coach); yet akāmaḥ sarva-kāmo vā … yajeta puruṣaṁ param (Bhāgavata 2.3.10):\n"
           "all are adhikārīs for the supreme Puruṣa.")
    root_top, root_h = 0.62, box_h("devatā", None, 8.8)
    br_top = root_top + root_h + 0.26
    hb = max(box_h(h, b, 8.4, 6.4) for h, b in zip(heads, bodies))
    low_top = br_top + hb + 0.18
    hl = max(box_h("x", left, 8.4, 6.6), box_h("x", right, 8.4, 6.6))
    ban_top = low_top + hl + 0.16
    H = ban_top + box_h(body=ban, bsize=7.0) + 0.06 + 0.10
    c = Canvas(H)
    c.title("Five kinds of devatā and the rule against anyāśraya")
    c.note(0.38, "after the speaker's chart, page 1")
    c.box(40, root_top, 20, root_h, header="devatā", hsize=8.8)
    w, gap = 17.6, 1.5
    xs = [3 + i * (w + gap) for i in range(5)]
    c.tree(50, root_top + root_h, [x + w / 2 for x in xs], br_top)
    for x, hd, bd in zip(xs, heads, bodies):
        edge, lw = (MAROON, 1.7) if hd == "iṣṭa" else (TEAL, 1.0)
        c.box(x, br_top, w, hb, header=hd, body=bd, edge=edge, lw=lw, hsize=8.4, bsize=6.4)
    c.box(3, low_top, 45, hl, header="the deva is for the karma", body=left, hsize=8.4, bsize=6.6)
    c.box(52, low_top, 45, hl, header="the karma is for the deva", body=right, edge=MAROON, lw=1.7,
          hsize=8.4, bsize=6.6)
    c.banner(ban_top, ban, size=7.0)
    return c.save("fig3_devata.png")


# ---------------------------------------------------------------- Figure 4
def fig4() -> Path:
    flow = [("two injunctions\nconflict", TEAL, 1.0), ("unresolved: sandeha,\nno nirṇaya, no pramāṇa", GREY, 1.0),
            ("resolving it is\nthe first duty", MAROON, 1.6)]
    vik = "a \"free option\": \"if you want to\ndo this, do this; if you want\nto do that, do that\""
    vya = "no free option: a \"particular\ncondition\" is stated; where it\nholds, the injunction applies"
    heads = ["adhikārī-bheda", "deśa-bheda", "kāla-bheda", "avasthā-bheda", "prayojana /\nphala-bheda"]
    bodies = [
        "cantonment area:\nthe citizen's right\n\"suspended\";\nŚivarātri fast for\nŚiva-bhaktas,\nJayantī fast for\nViṣṇu-bhaktas",
        "in this country\nthis rule; in that\ncountry, not",
        "aparas halved at\nnight, in illness,\non a journey; the\nclimb to Badrinath\non foot",
        "not binding on\nchildren; Ekādaśī\nnot binding at five\nor at eighty",
        "with dehābhimāna,\nvarṇāśrama-dharma\nfirst; for the\nsaṁnyāsin,\nbhagavad-dharma",
    ]
    ban = ("Where the stated condition holds, the injunction applies; where it does not, it does not, so the two\n"
           "statements never meet. Liquor is impure for the brāhmaṇa, whose work it obstructs, and not for\n"
           "the kṣatriya: \"it depends on what your job is\".")
    fh = max(box_h(t, None, 7.8) for t, _, _ in flow)
    flow_top = 0.48
    mid_top = flow_top + fh + 0.30
    hm = max(box_h("vikalpa", vik, 8.6, 6.6), box_h("vyavasthita-vikalpa", vya, 8.6, 6.6))
    row_top = mid_top + hm + 0.26
    hr = max(box_h(h, b, 7.6, 6.3) for h, b in zip(heads, bodies))
    ban_top = row_top + hr + 0.16
    H = ban_top + box_h(body=ban, bsize=7.0) + 0.06 + 0.10
    c = Canvas(H)
    c.title("Conflicting duties: vikalpa and vyavasthita-vikalpa")
    fx = [3, 36, 69]
    for x, (t, col, lw) in zip(fx, flow):
        c.box(x, flow_top, 28, fh, header=t, edge=col, lw=lw, hsize=7.8, hcolor=col)
    c.arrow(31.4, flow_top + fh / 2, 35.6, flow_top + fh / 2)
    c.arrow(64.4, flow_top + fh / 2, 68.6, flow_top + fh / 2)
    c.arrow(71.5, flow_top + fh + 0.02, 28, mid_top - 0.03)
    c.arrow(86, flow_top + fh + 0.02, 74, mid_top - 0.03)
    c.box(3, mid_top, 38, hm, header="vikalpa", body=vik, hsize=8.6, bsize=6.6)
    c.box(51, mid_top, 46, hm, header="vyavasthita-vikalpa", body=vya, edge=MAROON, lw=1.7, hsize=8.6, bsize=6.6)
    w, gap = 17.6, 1.5
    xs = [3 + i * (w + gap) for i in range(5)]
    c.tree(74, mid_top + hm, [x + w / 2 for x in xs], row_top)
    for x, hd, bd in zip(xs, heads, bodies):
        c.box(x, row_top, w, hr, header=hd, body=bd, edge=MAROON, hsize=7.6, bsize=6.3)
    c.banner(ban_top, ban, size=7.0)
    return c.save("fig4_vyavasthita_vikalpa.png")


# ---------------------------------------------------------------- Figure 5
def fig5() -> Path:
    heads = ["1  śruti", "2  smṛti", "3  sadācāra", "4  svasya ca\npriyam ātmanaḥ"]
    bodies = ["the Veda", "the past conduct of the\nṛṣis who accepted\nthe Veda",
              "\"custom\": the\nconduct of the good;\ncan be wrong", "what one finds\ndear, what is\npossible for oneself"]
    cannot = ("The śāstra says do japa, but the mind has\ngone mad; it says bathe, but there is fever,\n"
              "or no water at all. Then preferability is\nplaced on that side.")
    best = ("All four agree: smṛti in accord with śruti,\nsadācāra with smṛti, one's liking with\n"
            "sadācāra. \"There is no dharma better\nthan that.\"")
    ban = ("Prāmāṇya is settled from śruti downward, never from \"what seems best to me\" upward.\n"
           "Yājñavalkya-smṛti 1.7ab (Manusmṛti 2.12ab reads vedaḥ for śrutiḥ).")
    top = 0.62
    hb = max(box_h(h, b, 8.4, 6.6) for h, b in zip(heads, bodies))
    arr1 = top + hb + 0.16
    arr2 = arr1 + 0.40
    low_top = arr2 + 0.36
    hl = max(box_h("x", cannot, 8.2, 6.6), box_h("x", best, 8.4, 6.6))
    ban_top = low_top + hl + 0.16
    H = ban_top + box_h(body=ban, bsize=7.1) + 0.06 + 0.10
    c = Canvas(H)
    c.title("Four grounds of dharma: from authenticity to preferability")
    c.note(0.38, "after the speaker's chart, page 1  ·  śrutiḥ smṛtiḥ sadācāraḥ svasya ca priyam ātmanaḥ")
    w, gap = 21.5, 2.67
    xs = [3 + i * (w + gap) for i in range(4)]
    for x, hd, bd in zip(xs, heads, bodies):
        c.box(x, top, w, hb, header=hd, body=bd, hsize=8.4, bsize=6.6)
    c.arrow(96, arr1, 4, arr1, color=TEAL, lw=1.5)
    c.note(arr1 + 0.05, "authenticity: authority goes to the earlier (pūrva-pūrva, not pūrva-uttara)",
           size=6.8, color=TEAL, italic=False, bold=True)
    c.arrow(4, arr2, 96, arr2, color=OCHRE, lw=1.5)
    c.note(arr2 + 0.05, "preferability: what one can and will actually do", size=6.8, color=OCHRE,
           italic=False, bold=True)
    c.box(3, low_top, 45, hl, header="when one cannot", body=cannot, edge=GREY, hcolor=GREY, hsize=8.2, bsize=6.6)
    c.box(52, low_top, 45, hl, header="the best dharma", body=best, edge=MAROON, lw=1.7, hsize=8.4, bsize=6.6)
    c.banner(ban_top, ban, size=7.1)
    return c.save("fig5_authenticity_preferability.png")


# ---------------------------------------------------------------- Figure 6
def fig6() -> Path:
    cols = [
        ("kartavya: duty", TEAL, 1.0,
         "kartavya-karmaṇi evam anevaṁ\nvā kartuṁ śakyate: an action\ncan be done thus or not thus.\n\n"
         "vikalpa: a free option;\nvyavasthita-vikalpa: the\ncondition must be fulfilled.\n\n"
         "Accepted by all: a \"tolerant\"\nway of resolving contradiction."),
        ("Śaṅkara: a limited vastu", TEAL, 1.0,
         "na vastuni evam anevaṁ vā\nbhavati: a thing is not \"thus\nor not thus\".\n\n"
         "True, says the speaker, where\nthe form is parisīmita.\n\n"
         "Each thing has its arrangement:\nGandhi's spectacles are kept\nto be looked at, not worn."),
        ("Vallabha: two or all forms", MAROON, 1.7,
         "Where the thing \"allows\" it,\nboth evam and anevam:\n\nthe whale, a mammal that lives\n"
         "like a fish; the bat, a mammal\nthat flies; Gaṇapati, elephant\nand man; Narasiṁha; the\n"
         "African drum used as a table;\nthe earth, temple and gutter."),
    ]
    aside = "shoes: off outside, or off inside, but never worn through the house; Seṭh Govinddāsjī's sign for Nehru"
    ban = ("If an option is accepted in duty, why not in tattva, when tattva is sarvarūpa?\n"
           "Whoever cannot see it by svabhāva may see it by sāmarthya; either way, keep no doubt.")
    top = 0.50
    hc = max(box_h(h, b, 8.6, 6.6) for h, _, _, b in cols)
    aside_top = top + hc + 0.10
    ban_top = aside_top + 0.26
    H = ban_top + box_h(body=ban, bsize=7.3) + 0.06 + 0.10
    c = Canvas(H)
    c.title("Evam and anevam: \"thus\" and \"not thus\" in a thing")
    for x, (hd, col, lw, bd) in zip([3, 35, 67], cols):
        c.box(x, top, 30, hc, header=hd, body=bd, edge=col, lw=lw, hsize=8.6, bsize=6.6)
    c.note(aside_top, aside, size=6.4)
    c.banner(ban_top, ban, size=7.3)
    return c.save("fig6_evam_anevam.png")


# ---------------------------------------------------------------- Figure 7
def fig7() -> Path:
    cols = [
        ("pūrva-kāṇḍa", TEAL, 1.0,
         "yajña-rūpa Hari\n\nkriyā-śakti, from his\nbeing sarvaśakti:\nBrahman entered into\naction, a \"function\"\n\nexpounded khaṇḍaśaḥ,\npiecemeal"),
        ("uttara-kāṇḍa", TEAL, 1.0,
         "brahma-tanu\n\njñāna-śakti, from his\nbeing sarvajña;\n\"tanu\": Brahman with form\n(sākāra) as well as formless\n\nalso piecemeal"),
        ("Śrī Bhāgavata (and Gītā)", MAROON, 1.7,
         "avatārī Hari, Kṛṣṇa\n\njñāna-kriyobhaya-yuta:\nthe \"substance\" that holds\nboth, having manifested both\n\nexpounded samudāyena, as a\nwhole; his līlā in many ways"),
    ]
    koti = ("śruti and the Brahmasūtra: a garden and a bouquet (vimarśa: viṣaya, saṁśaya, pūrvapakṣa, uttarapakṣa, saṅgati)\n"
            "Gītā and Bhāgavata: the principle and its illustration (tad-vistāro bhāgavatam)")
    noc = ("Every action culminates in knowledge, every\nknowledge has its outlet in action: weighing\n"
           "the duster, the oiled wrestler, the eye's focus,\nthe mother's ear, frogs answering their kind.")
    nir = ("Vapour is formless; consolidated into cloud\nit takes form; falling as rain it is formless\n"
           "again. \"Sākāra can be converted into\nnirākāra, nirākāra into sākāra.\"")
    ban = ("Read this way, the Veda expounds Brahman alone, now as action, now as knowledge,\n"
           "now formless, now with form, and the contradictions across the śāstras dissolve.")
    top = 0.62
    hc = max(box_h(h, b, 8.6, 6.6) for h, _, _, b in cols)
    k_top = top + hc + 0.16
    hk = box_h("x", koti, 8.2, 6.5)
    l_top = k_top + hk + 0.16
    hl = max(box_h("x", noc, 8.2, 6.6), box_h("x", nir, 8.2, 6.6))
    ban_top = l_top + hl + 0.16
    H = ban_top + box_h(body=ban, bsize=7.2) + 0.06 + 0.10
    c = Canvas(H)
    c.title("One Hari in three portions of the pramāṇas")
    c.note(0.38, "yajña-rūpo hariḥ pūrva-kāṇḍe brahma-tanuḥ pare | avatārī hariḥ kṛṣṇaḥ śrī-bhāgavata ‹īryate›")
    for x, (hd, col, lw, bd) in zip([3, 35, 67], cols):
        c.box(x, top, 30, hc, header=hd, body=bd, edge=col, lw=lw, hsize=8.6, bsize=6.6)
    c.box(3, k_top, 94, hk, header="two koṭis, one prameya", body=koti, fill=PALE, hsize=8.2, bsize=6.5)
    c.box(3, l_top, 45, hl, header="no compartments", body=noc, hsize=8.2, bsize=6.6)
    c.box(52, l_top, 45, hl, header="nirākāra ⇄ sākāra", body=nir, hsize=8.2, bsize=6.6)
    c.banner(ban_top, ban)
    return c.save("fig7_three_portions.png")


# ---------------------------------------------------------------- Figure 8
def fig8() -> Path:
    svar = ("satyaṁ jñānam anantam: \"infinite conscious being\".\nŚaṅkara: so there is no action in Brahman.\n"
            "Mahāprabhu: being cannot be inactive; consciousness\nbrings knowledge and ignorance; the infinite,\n"
            "limited in no place, time or form, brings sarvarūpatā.")
    karya = ("jagad-utpatti-kartā, upādāna + ādhāra, sthāpaka\n+ saṁhāraka, āśraya: this is Bhagavān.\n"
             "Nothing is imported; Brahman makes itself the\n\"raw material\" (\"Allah cannot throw me out\").")
    ban = ("The Upaniṣad \"zooms out\" (three); the Bhāgavata \"zooms in\" (ten): 2 + 6 + 2 = 10.\n"
           "No contradiction between Brahman and Bhagavān, only different facets.")
    root_top, root_h = 0.60, box_h("Brahman", None, 8.8)
    def_top = root_top + root_h + 0.24
    hd = max(box_h("x", svar, 8.4, 6.4), box_h("x", karya, 8.4, 6.4))
    grp_top = def_top + hd + 0.26
    grp_h = box_h("utpatti", None, 8.2)
    b_top = grp_top + grp_h + 0.24
    gl_b = {"sarga": "primal\nform", "visarga": "\"formatted\"\nform", "mukti": "laya",
            "āśraya": "the refuge,\none with\nsarga"}
    hb = max(box_h(k, v, 7.4, 6.0) for k, v in gl_b.items())
    c_top = b_top + hb + 0.30
    six = [("sthāna", "\"placement\""), ("poṣaṇa", "\"mainte-\nnance\""), ("ūti", "saṁskāras\narise"),
           ("manvantara", "the good\nsaṁskāras"), ("īśānukathā", "the Lord's\nstory:\nbhakti"),
           ("nirodha", "citta one-\npointed in\nBhagavān")]
    hc = max(box_h(k, v, 7.2, 6.0) for k, v in six)
    loop_bottom = c_top + hc + 0.30
    snake = loop_bottom - 0.20
    ban_top = loop_bottom + 0.12
    H = ban_top + box_h(body=ban, bsize=7.0) + 0.06 + 0.10
    c = Canvas(H)
    c.title("Brahman's two definitions and the Bhāgavata's ten topics")
    c.note(0.36, "after the speaker's chart, page 2")
    c.box(40, root_top, 20, root_h, header="Brahman", hsize=8.8)
    c.tree(50, root_top + root_h, [25, 73.5], def_top)
    c.box(3, def_top, 44, hd, header="svarūpa-lakṣaṇa", body=svar, hsize=8.4, bsize=6.4)
    c.box(50, def_top, 47, hd, header="kārya-lakṣaṇa", body=karya, edge=MAROON, lw=1.7, hsize=8.4, bsize=6.4)
    c.tree(73.5, def_top + hd, [16.5, 50, 82.5], grp_top)
    for x, name in ((5, "utpatti"), (38.5, "sthiti"), (71, "laya")):
        c.box(x, grp_top, 23, grp_h, header=name, hsize=8.2)
    sw = 11.0
    bx = {"sarga": 5.0, "visarga": 17.0, "mukti": 71.0, "āśraya": 83.0}
    c.tree(16.5, grp_top + grp_h, [bx["sarga"] + sw / 2, bx["visarga"] + sw / 2], b_top)
    c.tree(82.5, grp_top + grp_h, [bx["mukti"] + sw / 2, bx["āśraya"] + sw / 2], b_top)
    for name, x in bx.items():
        edge, lw = (MAROON, 1.6) if name in ("sarga", "āśraya") else (TEAL, 1.0)
        c.box(x, b_top, sw, hb, header=name, body=gl_b[name], edge=edge, lw=lw, hsize=7.4, bsize=6.0)
    six_w, six_gap = 12.6, 1.6
    x0 = 50 - (6 * six_w + 5 * six_gap) / 2
    centres = [x0 + i * (six_w + six_gap) + six_w / 2 for i in range(6)]
    c.tree(50, grp_top + grp_h, centres, c_top, bar_in=(b_top + hb + c_top) / 2)
    for i, (name, g) in enumerate(six):
        c.box(x0 + i * (six_w + six_gap), c_top, six_w, hc, header=name, body=g, hsize=7.2, bsize=6.0)
    # the loop: from āśraya, down the right side, under the sthiti row, up the left side into sarga
    yb = c.Y(b_top + hb)
    yl = c.Y(loop_bottom)
    pts = [(91.0, yb), (95.8, yb - 3), (95.8, yl + 6), (95.8, yl), (88, yl), (50, yl), (12, yl), (4.2, yl),
           (4.2, yl + 6), (4.2, yb - 3), (8.5, yb)]
    codes = [MPath.MOVETO, MPath.CURVE3, MPath.CURVE3, MPath.CURVE3, MPath.CURVE3, MPath.LINETO, MPath.LINETO,
             MPath.CURVE3, MPath.CURVE3, MPath.CURVE3, MPath.CURVE3]
    c.ax.add_patch(FancyArrowPatch(path=MPath(pts, codes), arrowstyle="-|>", mutation_scale=10, color=OCHRE,
                                   linewidth=1.3, zorder=1.5))
    c.note(snake - 0.02, "the snake that eats its tail: where the tail ends, the mouth begins", size=6.4,
           color=OCHRE)
    c.banner(ban_top, ban, size=7.0)
    return c.save("fig8_brahma_lakshana.png")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        f()
