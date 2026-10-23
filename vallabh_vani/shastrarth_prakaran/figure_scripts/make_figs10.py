#!/usr/bin/env python3
"""Figures for Śāstrārtha Prakaraṇa, Lecture 10 (session of 2026-09-12).

House style: matplotlib Agg, DejaVu Sans, width 6.2 in, dpi 200, axes 0-100 both ways
(axis off), rounded FancyBboxPatch boxes ("round,pad=0.012"), headers centred near the
box top, body text top-anchored.

Layout is planned in inches measured from the top-left corner. Every text block is
measured before drawing, boxes are sized to their contents, and the figure height is
the sum of the rows. At render time the inch layout is converted to the 0-100 axes.
After drawing, every text is checked against the box that must contain it, against all
other texts, and against the canvas; problems are printed.
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

OUT = Path(__file__).resolve().parent / "figs10"
OUT.mkdir(exist_ok=True)

W = 6.2  # figure width, inches
X0, X1 = 0.05, 6.15  # usable horizontal span
TITLE, SUBT, HEAD, SUB, TAG, BODY = 12.0, 7.4, 8.8, 6.4, 7.6, 6.8
LS = 1.4
PAD_TOP, GAP_S, GAP_B, PAD_BOT, PAD_X = 0.10, 0.05, 0.09, 0.11, 0.12
ROW_GAP = 0.10

PROBLEMS: list[str] = []

_scratch = plt.figure(figsize=(W, 4), dpi=200)
_rend = _scratch.canvas.get_renderer()


def measure(s: str, size: float, weight: str = "normal", style: str = "normal",
            ls: float = LS) -> tuple[float, float]:
    """Width and height of a text block, in inches."""
    t = _scratch.text(0, 0, s, fontsize=size, fontweight=weight, fontstyle=style,
                      linespacing=ls)
    bb = t.get_window_extent(renderer=_rend)
    t.remove()
    return bb.width / _scratch.dpi, bb.height / _scratch.dpi


def vmetrics(size: float, weight: str = "normal", style: str = "normal") -> tuple[float, float]:
    """Ascent above and descent below the baseline (inches) for the tallest IAST glyphs,
    so that single-line headers can be baseline-aligned across a row."""
    t = _scratch.text(0.5, 0.5, "ŚĀṄÑgjyṣ", fontsize=size, fontweight=weight, fontstyle=style,
                      va="baseline", transform=_scratch.transFigure)
    bb = t.get_window_extent(renderer=_rend)
    base = 0.5 * _scratch.bbox.height
    t.remove()
    return (bb.y1 - base) / _scratch.dpi, (base - bb.y0) / _scratch.dpi


def line(f, x, cy, s, size, weight="normal", style="normal", **kw):
    """Draw one baseline-aligned line whose top is at cy; return the next free y."""
    a, d = vmetrics(size, weight, style)
    f.text(x, cy + a, s, size=size, weight=weight, style=style, va="baseline", **kw)
    return cy + a + d


class Fig:
    def __init__(self, name: str):
        self.name = name
        self.cmds: list[tuple] = []
        self.bottom = 0.0
        self.y = 0.0  # running cursor (inches from top)

    # ---- recording primitives (inches from top-left) -----------------------------------
    def box(self, x, y, w, h, ec=TEAL, fc=SAND, lw=1.1):
        self.cmds.append(("box", x, y, w, h, ec, fc, lw))
        self.bottom = max(self.bottom, y + h)
        return (x, y, w, h)

    def text(self, x, y, s, size=BODY, color=INK, ha="left", va="top", weight="normal",
             style="normal", within=None, ls=LS):
        self.cmds.append(("text", x, y, s, size, color, ha, va, weight, style, within, ls))
        return measure(s, size, weight, style, ls)

    def ellipse(self, cx, cy, d, ec, fc, lw, z=2):
        self.cmds.append(("ellipse", cx, cy, d, ec, fc, lw, z))
        self.bottom = max(self.bottom, cy + d / 2)

    def arrow(self, x0, y0, x1, y1, color=OCHRE, lw=1.2, ms=9):
        self.cmds.append(("arrow", x0, y0, x1, y1, color, lw, ms))

    # ---- composite pieces -------------------------------------------------------------
    def title(self, s, sub=None):
        _, h = self.text(W / 2, 0.04, s, size=TITLE, ha="center", weight="bold")
        self.y = 0.04 + h
        if sub:
            _, h2 = self.text(W / 2, self.y + 0.05, sub, size=SUBT, color=GREY, ha="center",
                              style="italic")
            self.y += 0.05 + h2
        self.y += 0.12

    @staticmethod
    def panel_need(header, body=None, sub=None, tag=None, body_size=BODY):
        need = PAD_TOP + sum(vmetrics(HEAD, "bold"))
        if sub:
            need += GAP_S + sum(vmetrics(SUB, style="italic"))
        if tag:
            need += GAP_S + sum(vmetrics(TAG, "bold"))
        if body:
            need += GAP_B + measure(body, body_size)[1]
        return need + PAD_BOT

    def panel(self, x, y, w, h, header, body=None, sub=None, tag=None, ec=TEAL, fc=SAND,
              lw=1.1, hcolor=None, body_size=BODY):
        b = self.box(x, y, w, h, ec=ec, fc=fc, lw=lw)
        cy = line(self, x + w / 2, y + PAD_TOP, header, HEAD, "bold", color=hcolor or ec,
                  ha="center", within=b)
        if sub:
            cy = line(self, x + w / 2, cy + GAP_S, sub, SUB, style="italic", color=GREY,
                      ha="center", within=b)
        if tag:
            cy = line(self, x + w / 2, cy + GAP_S, tag, TAG, "bold", color=OCHRE,
                      ha="center", within=b)
        if body:
            self.text(x + PAD_X, cy + GAP_B, body, size=body_size, within=b)
        return b

    def row(self, specs, gap=0.08, x_start=X0, x_end=X1):
        """specs: list of dicts with panel kwargs; equal widths, equal (max) height."""
        n = len(specs)
        w = (x_end - x_start - gap * (n - 1)) / n
        need = max(self.panel_need(s["header"], s.get("body"), s.get("sub"), s.get("tag"))
                   for s in specs)
        boxes = []
        for k, s in enumerate(specs):
            boxes.append(self.panel(x_start + k * (w + gap), self.y, w, need, **s))
        self.y += need + ROW_GAP
        return boxes, w, need

    def banner(self, s, size=7.2):
        _, th = measure(s, size, "bold", ls=1.3)
        h = th + 0.17
        b = self.box(X0, self.y, X1 - X0, h, ec=OCHRE, fc=OCHRE, lw=1.0)
        self.text(W / 2, self.y + h / 2, s, size=size, color="white", ha="center",
                  va="center", weight="bold", within=b, ls=1.3)
        self.y += h + ROW_GAP

    # ---- rendering and checks -----------------------------------------------------------
    def render(self):
        H = max(self.bottom, self.y - ROW_GAP) + 0.05
        fig = plt.figure(figsize=(W, H))
        fig.patch.set_facecolor(PALE)
        ax = fig.add_axes((0, 0, 1, 1))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")
        ax.set_facecolor(PALE)

        def X(v):
            return v / W * 100

        def Y(v):
            return (H - v) / H * 100

        px, py = 1.2, 1.2 * W / H  # pad in data units; equal in inches on both axes
        contained, texts = [], []
        for c in self.cmds:
            kind = c[0]
            if kind == "box":
                _, x, y, w, h, ec, fc, lw = c
                ax.add_patch(FancyBboxPatch(
                    (X(x) + px, Y(y + h) + py), X(w) - 2 * px, h / H * 100 - 2 * py,
                    boxstyle="round,pad=0.012", mutation_scale=100, mutation_aspect=W / H,
                    ec=ec, fc=fc, lw=lw, zorder=1))
            elif kind == "text":
                _, x, y, s, size, color, ha, va, weight, style, within, ls = c
                t = ax.text(X(x), Y(y), s, fontsize=size, color=color, ha=ha, va=va,
                            fontweight=weight, fontstyle=style, linespacing=ls, zorder=5)
                texts.append(t)
                if within is not None:
                    bx, by, bw, bh = within
                    contained.append((t, (X(bx), Y(by + bh), X(bx + bw), Y(by))))
            elif kind == "ellipse":
                _, cx, cy, d, ec, fc, lw, z = c
                ax.add_patch(Ellipse((X(cx), Y(cy)), X(d), d / H * 100, ec=ec, fc=fc,
                                     lw=lw, zorder=z))
            elif kind == "arrow":
                _, x0, y0, x1, y1, color, lw, ms = c
                ax.add_patch(FancyArrowPatch((X(x0), Y(y0)), (X(x1), Y(y1)),
                                             arrowstyle="-|>", mutation_scale=ms,
                                             color=color, lw=lw, zorder=4))
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        to_disp = ax.transData.transform
        for t, (x0, y0, x1, y1) in contained:
            tb = t.get_window_extent(renderer=r)
            (bx0, by0), (bx1, by1) = to_disp((x0, y0)), to_disp((x1, y1))
            m = 2.5
            if tb.x0 < bx0 + m or tb.x1 > bx1 - m or tb.y0 < by0 + m or tb.y1 > by1 - m:
                PROBLEMS.append(f"{self.name}: text crosses its box: {t.get_text()[:50]!r}")
        exts = [(t, t.get_window_extent(renderer=r)) for t in texts]
        for i in range(len(exts)):
            for j in range(i + 1, len(exts)):
                a, b = exts[i][1], exts[j][1]
                if a.x0 < b.x1 - 1 and b.x0 < a.x1 - 1 and a.y0 < b.y1 - 1 and b.y0 < a.y1 - 1:
                    PROBLEMS.append(f"{self.name}: texts overlap: "
                                    f"{exts[i][0].get_text()[:30]!r} / {exts[j][0].get_text()[:30]!r}")
        fb = fig.bbox
        for t, tb in exts:
            if tb.x0 < fb.x0 + 1 or tb.x1 > fb.x1 - 1 or tb.y0 < fb.y0 + 1 or tb.y1 > fb.y1 - 1:
                PROBLEMS.append(f"{self.name}: text leaves the canvas: {t.get_text()[:40]!r}")
        fig.savefig(OUT / f"{self.name}.png", dpi=200, bbox_inches="tight", pad_inches=0.12,
                    facecolor=PALE)
        plt.close(fig)
        return H


# =====================================================================================
def fig1():
    f = Fig("fig1_five_positions")
    f.title("Bheda and abheda: five answers",
            sub="the speaker's notation:  A = abheda (non-difference)   ·   B = bheda (difference)")
    f.row([
        dict(header="Śaṅkara", tag="A only",
             body="A is, B is not:\nB is “negative”.\n\nAbheda alone is real."),
        dict(header="Bhāskara", tag="A and B",
             body="Both are there:\na natural bheda beside\na natural abheda.\n\nŚakti-pariṇāma; the\nśakti is used as a\nsubstance."),
        dict(header="Rāmānuja", tag="abheda in bheda",
             body="Bheda in the svarūpa,\nabheda within it.\n\nViśiṣṭādvaita."),
        dict(header="Madhva", tag="B only",
             body="Bheda, no abheda:\n“just opposite\nto Śaṅkara”."),
    ], gap=0.06)
    head = "Mahāprabhuji (Vallabha): svarūpataḥ abheda, and bheda arises within it"
    tag = "“B is equal to A, is equivalent to B”"
    left = ("Bheda and abheda are complementary, not\ncontradictory: Brahman is the viruddha-\n"
            "dharmāśraya, the locus of opposed attributes.")
    right = ("“By default” there is abheda; bheda arises\nwithin it. To take bheda and abheda in\n"
             "Bhāskara's way would be “very easy”.")
    need = (PAD_TOP + sum(vmetrics(HEAD, "bold")) + GAP_S + sum(vmetrics(TAG, "bold"))
            + GAP_B + max(measure(left, BODY)[1], measure(right, BODY)[1]) + PAD_BOT)
    b = f.box(X0, f.y, X1 - X0, need, ec=MAROON, fc=PALE, lw=1.8)
    cy = line(f, W / 2, f.y + PAD_TOP, head, HEAD, "bold", color=MAROON, ha="center", within=b)
    cy = line(f, W / 2, cy + GAP_S, tag, TAG, "bold", color=OCHRE, ha="center", within=b)
    cy += GAP_B
    f.text(X0 + PAD_X + 0.05, cy, left, within=b)
    f.text(W / 2 + 0.1, cy, right, within=b)
    f.y += need + ROW_GAP
    f.banner("Mirror images:  Rāmānuja accepts bheda in the svarūpa and abheda within it;\n"
             "Mahāprabhuji accepts abheda in the svarūpa, and bheda arises within it.")
    return f.render()


def fig2():
    f = Fig("fig2_dependence")
    f.title("Three kinds of dependence",
            sub="utpatti · sthiti · jñapti: the speaker's “very major point”")
    f.row([
        dict(header="Utpatti", sub="origination", tag="To arise, A depends on B.",
             body="The effect depends on its cause.\n\nThe child depends on the parents.\n\n"
                  "The house depends on its\nfoundation, not the reverse.\n\n"
                  "The śakti's utpatti is “in my\nhands”: if I end, my śakti ends."),
        dict(header="Sthiti", sub="subsistence, location", tag="To stay put, A rests on B.",
             body="The laptop rests on the table.\n\nThe whiteboard rests on the hand\n"
                  "that holds it: let go, and it falls.\n\nThe fan hangs from the hook.\n\n"
                  "The śakti rests on the śaktimān:\na force needs a substance as\nits locus."),
        dict(header="Jñapti", sub="being known", tag="To be known, A depends on B.",
             body="Parenthood is known through\nthe child.\n\nThe śaktimān is known through\n"
                  "the śakti: I walk because I can.\n\nFrom old foundations we can\n"
                  "imagine the house; the house\ndoes not show the foundation."),
    ])
    f.row([
        dict(header="Śaṅkara",
             body="Māyā and Brahman are both anādi:\nin utpatti neither depends on the other.\n"
                  "Māyā is unreal, so its jñapti depends on\nBrahman; Brahman is known without māyā."),
        dict(header="Mahāprabhuji", ec=MAROON, fc=PALE, lw=1.8,
             body="The śakti depends on the śaktimān in\nsthiti; the śaktimān never depends on\n"
                  "the śakti: an unused power is not lost.\n“Here is our difference with Bhāskara.”"),
    ])
    return f.render()


def fig3():
    f = Fig("fig3_born")
    f.title("Ucyate na tu jāyate: two meanings of “born”")
    f.row([
        dict(header="Grammar: the technical sense",
             body="janī prādurbhāve: to be born is to come\ninto view (prādurbhāva).\n"
                  "ṇaśa adarśane: to perish is to pass out\nof sight, not to be destroyed.\n\n"
                  "The sun has not ended at sunset; the plane\nbeyond the horizon is not lost; "
                  "before the\nwomb we were there as ovum and sperm."),
        dict(header="Usage: the common “bias”", ec=GREY, hcolor=TEAL,
             body="utpatti = prāgabhāva-pratiyogitva:\nbeing the opposite of a prior absence.\n"
                  "nāśa = pradhvaṁsābhāva-pratiyogitva:\nbeing the opposite of a later absence.\n\n"
                  "A car made by a mechanism: before it\nthere was no car, so the car “opposes”\n"
                  "its absence. “This sense is our bias.”"),
    ])
    f.row([
        dict(header="The pot",
             body="Comes into view and passes\nout of sight in a certain time\n"
                  "and space: objective, not\nmerely an appearance."),
        dict(header="Saṁsāra", ec=MAROON, fc=PALE, lw=1.8,
             body="Arises only in the mind, not\nin the frame of time and space:\n"
                  "it is said to be born, but it\nis not born."),
        dict(header="Brahman",
             body="Is not born either. So what\nis the difference? It lies in\n"
                  "where a thing appears, not\nin being born."),
    ])
    f.banner("Where it appears to us, there it is not born: saṁsāra appears only in the mind,\n"
             "as a concept outlives its percept and a deleted photo survives in the cloud.")
    return f.render()


def fig4():
    f = Fig("fig4_rupa_nama")
    f.title("Saṁsāra seen from two angles",
            sub="rūpa-nāma-vibhedena (TDN Śāstrārtha 1): there is a rūpa-sṛṣṭi and a nāma-sṛṣṭi")
    w = (X1 - X0 - 0.08) / 2
    sides = [
        (X0, "From the angle of rūpa-sṛṣṭi", TEAL, SAND, 1.1,
         [("bhrama", "delusion"), ("asatya", "unreal"), ("ajñāna", "ignorance")],
         "because “I” and “mine” are not in the\nframe of time and space"),
        (X0 + w + 0.08, "From the angle of nāma-sṛṣṭi", MAROON, PALE, 1.8,
         [("not ajñāna", "it is jñānātmikā"), ("not asatya", "it is sad-ātmikā"),
          ("not bhrānti", "in the mind it truly is")],
         "so this too is brahmātmaka: if anything\nwere outside Brahman, Brahman would\n"
         "not remain Brahman"),
    ]
    pitch = 0.215
    need = max(PAD_TOP + sum(vmetrics(HEAD, "bold")) + GAP_B + 3 * pitch + 0.04
               + measure(note, BODY, style="italic")[1] + PAD_BOT
               for _, h, _, _, _, _, note in sides)
    for x, head, ec, fc, lw, rows, note in sides:
        b = f.box(x, f.y, w, need, ec=ec, fc=fc, lw=lw)
        cy = line(f, x + w / 2, f.y + PAD_TOP, head, HEAD, "bold", color=ec, ha="center",
                  within=b)
        cy += GAP_B + 0.13
        for term, gloss in rows:
            f.text(x + 0.3, cy, term, size=8.0, color=ec, va="baseline", weight="bold", within=b)
            f.text(x + 1.32, cy, gloss, size=7.1, va="baseline", within=b)
            cy += pitch
        f.text(x + PAD_X, cy - 0.09, note, size=BODY, color=GREY, style="italic", within=b)
    f.y += need + ROW_GAP
    f.row([
        dict(header="Prapañca: the external world",
             body="Brahmātmaka. In it there is no story at all\nof being sat or asat; words such as asat,\n"
                  "ajñāna and bhrama do not apply to it."),
        dict(header="Saṁsāra: “I” and “mine”",
             body="Abhimaty-ātmaka: counted as “it is not”\nin the frame of time and space, yet alive\n"
                  "in the frame of the mind."),
    ])
    f.banner("The dead live on in the mind: the outer one has a lifespan, the inner one has none.")
    return f.render()


def fig5():
    f = Fig("fig5_circles")
    f.title("The wider circle: subject and predicate in the mahāvākyas")
    top = f.y
    # right column: verb panel, then two small boxes
    rx = 3.05
    rw = X1 - rx
    verb_body = ("ahaṁ brahmāsmi: “I am Brahman”,\n   not “I is Brahman” (brahma asti)\n\n"
                 "tvaṁ tad asi (said as tat tvam asi):\n   not tat tvam asti\n\n"
                 "idaṁ sarvaṁ brahma (asti)\n\n"
                 "So aham, tvam and idam are the subjects,\nparts within the whole that is Brahman.")
    vneed = Fig.panel_need("The verb agrees with the subject", verb_body)
    f.panel(rx, top, rw, vneed, "The verb agrees with the subject", verb_body)
    sy = top + vneed + 0.08
    sw = (rw - 0.08) / 2
    chain = "asti\n↓\nast\n↓\nest (Latin)\n↓\nist (German)\n↓\n“is”"
    chain_h = measure(chain, 6.4, ls=1.08)[1]
    sneed = PAD_TOP + sum(vmetrics(7.2, "bold")) + 0.06 + chain_h + PAD_BOT
    lb = f.box(rx, sy, sw, sneed, ec=GREY, fc=PALE)
    line(f, rx + sw / 2, sy + PAD_TOP, "“lion is an animal”", 7.2, "bold", color=TEAL,
         ha="center", within=lb)
    lcx, lcy = rx + sw / 2, sy + sneed / 2 + 0.1
    big = min(sneed - 0.42, sw - 0.3)
    f.ellipse(lcx, lcy, big, GREY, "white", 1.0)
    f.ellipse(lcx, lcy + big * 0.17, big * 0.42, TEAL, SAND, 1.0, z=3)
    f.text(lcx, lcy - big * 0.30, "animal", size=6.4, color=GREY, ha="center", va="center",
           within=lb)
    f.text(lcx, lcy + big * 0.17, "lion", size=6.4, color=TEAL, ha="center", va="center",
           within=lb)
    eb = f.box(rx + sw + 0.08, sy, sw, sneed, ec=GREY, fc=PALE)
    cy = line(f, rx + sw * 1.5 + 0.08, sy + PAD_TOP, "the speaker's chain", 7.2, "bold",
              color=TEAL, ha="center", within=eb)
    f.text(rx + sw * 1.5 + 0.08, cy + 0.06, chain, size=6.4, ha="center", within=eb, ls=1.08)
    col_bottom = sy + sneed
    # left: circles, filling the height of the right column
    region = col_bottom - top
    d = min(region - 0.02, rx - X0 - 0.12)
    cx, cy = X0 + (rx - X0 - 0.08) / 2, top + region / 2
    f.ellipse(cx, cy, d, MAROON, PALE, 2.0)
    f.text(cx, cy - d * 0.40, "Brahman", size=HEAD + 0.6, color=MAROON, ha="center",
           weight="bold")
    f.text(cx, cy - d * 0.30, "the predicate: always the wider circle", size=6.3, color=GREY,
           ha="center", style="italic")
    di = d * 0.30
    for ix, iy, word, verb in ((cx - d * 0.205, cy - d * 0.035, "aham", "asmi · 1st person"),
                               (cx + d * 0.205, cy - d * 0.035, "tvam", "asi · 2nd person"),
                               (cx, cy + d * 0.275, "idam", "asti · 3rd person")):
        f.ellipse(ix, iy, di, TEAL, SAND, 1.2, z=3)
        f.text(ix, iy - 0.02, word, size=8.2, color=TEAL, ha="center", va="bottom", weight="bold")
        f.text(ix, iy + 0.04, verb, size=5.9, ha="center", va="top")
    f.y = col_bottom + ROW_GAP
    f.banner("Realized in one's own consciousness, assumed in others by analogy:\n"
             "“if others and you both are Brahman, then everything is Brahman”: sarvaṁ khalv idaṁ brahma.")
    return f.render()


def fig6():
    f = Fig("fig6_prasthanas")
    f.title("Śaṅkara's three prasthānas, and Mahāprabhuji",
            sub="the speaker's stages; the Vārttika's position comes “very close” to Vallabha")
    gap = 0.27
    boxes, w, need = f.row([
        dict(header="Vivaraṇa", sub="Padmapāda", tag="pratibimba-vāda",
             body="The individual\nconsciousness is\nonly a reflection\nof Brahman's\n"
                  "consciousness\nin māyā."),
        dict(header="Bhāmatī", sub="Vācaspati Miśra", tag="avaccheda-vāda",
             body="Pot-space is real\nspace taking on the\npot's character: it\n"
                  "moves, is born and\nends. So too the\nindividual\nconsciousness."),
        dict(header="Vārttika", sub="the Vārttikakāra", tag="ābhāsa",
             body="Rādheya–Kaunteya:\nKarṇa was always\nKaunteya; Kuntī's\n"
                  "words changed only\nhis opinion."),
        dict(header="Mahāprabhuji", sub="Vallabha", tag="we are Brahman",
             ec=MAROON, fc=PALE, lw=1.8,
             body="Only the opinion,\nahantā and mamatā,\nis corrupted; we are\n"
                  "not corrupted.\n\nTattvajñāna removes\najñāna, not the\nprapañca."),
    ], gap=gap)
    ay = boxes[0][1] + need * 0.55
    for k in range(3):
        xr = X0 + (k + 1) * w + k * gap
        f.arrow(xr + 0.035, ay, xr + gap - 0.035, ay, ms=8, lw=1.1)
    f.banner("Correct the opinion: we were Kaunteya before, we are today,\n"
             "and we will be in future. Out of Rādheya, Kaunteya was not made.")
    return f.render()


def fig7():
    f = Fig("fig7_objection_reply")
    f.title("Prapañca and saṁsāra: the objection and the reply")
    w = (X1 - X0 - 0.10) / 2
    xl, xr = X0, X0 + w + 0.10
    line(f, xl + w / 2, f.y, "The objector, in Gosāīṁjī's addition", HEAD, "bold", color=TEAL,
         ha="center")
    f.y = line(f, xr + w / 2, f.y, "The reply: na bhavet", HEAD, "bold", color=MAROON,
               ha="center") + 0.08
    left = [
        "A stick breaks a pot in the prapañca;\ntattvajñāna “breaks” saṁsāra in the\nsame way.",
        "So avidyā is the stick and saṁsāra the\npot: call saṁsāra brahmātmaka, a part\nof the prapañca.",
        "“Then saṁsāra is eternal; mukti is cut\noff?” No: saṁsāra and mukti are\n"
        "successive āvirbhāvas, as a raw pot\nshows black and a baked pot red.",
        "Why keep an ardhajaratīya Brahmavāda,\nhalf brahmātmaka and half māyika,\n"
        "half old woman and half young?",
    ]
    right = [
        "Āvirbhāva and tirobhāva belong only to\nwhat exists: what is not cannot come\n"
        "in front, nor go out of sight.",
        "Saṁsāra is abhimaty-ātmaka: only\nsubjective, not in time and space; so\n"
        "it is asat as rūpa, though not as nāma.",
        "The pot: clay, tools, procedure, time\nand space are all objective. “My pot”\n"
        "is only a mānyatā: the stolen scooter,\nthe farmers' śrāddha.",
        "So saṁsāra does not fall within the\nprapañca: it is neither produced nor\n"
        "destroyed like a pot.",
    ]
    agap = 0.17
    for k, (ls_, rs_) in enumerate(zip(left, right)):
        need = 0.09 + max(measure(ls_, BODY)[1], measure(rs_, BODY)[1]) + 0.10
        bl = f.box(xl, f.y, w, need, ec=TEAL, fc=SAND)
        f.text(xl + PAD_X, f.y + 0.09, ls_, within=bl)
        br = f.box(xr, f.y, w, need, ec=MAROON, fc=PALE, lw=1.6)
        f.text(xr + PAD_X, f.y + 0.09, rs_, within=br)
        f.y += need
        if k < 3:
            for x in (xl, xr):
                f.arrow(x + w / 2, f.y + 0.015, x + w / 2, f.y + agap - 0.015, ms=8, lw=1.1)
            f.y += agap
    f.y += ROW_GAP
    f.banner("Redness and roundness are objective characters of the pot; being “mine” is a subjective one.")
    return f.render()


def fig8():
    f = Fig("fig8_creation")
    f.title("Out of nothing, out of potency, out of itself")
    f.row([
        dict(header="Abrahamic view", sub="Judaism, Christianity, Islam", tag="out of nothing",
             body="“God created this world\nout of nothing”, in the void.\n\n"
                  "Made by his power, but not\na pariṇāma of that power.\n\n"
                  "The student's example: we\nbring out a voice “out of\nnothing”."),
        dict(header="Bhāskara", sub="bhedābheda", tag="out of his potency",
             body="Śakti-pariṇāma: the world is\nmade from the śakti.\n\n"
                  "Like planets made from the\nsun's power, the sun still\nintact; "
                  "or sun and planets\nas siblings from one cloud\nof gas."),
        dict(header="Mahāprabhuji", sub="Brahmavāda", tag="out of itself",
             ec=MAROON, fc=PALE, lw=1.8,
             body="Svarūpa-pariṇāma: tad\nātmānaṁ svayam akuruta.\n\n"
                  "Like a passing star raising a\ntide in the sun and pulling\n"
                  "matter out, which the sun\nthen holds: the planets are\nthe sun's own substance."),
    ])
    f.banner("Remember the rickshaw: hold the luggage on your lap, and the rickshaw-wallah still\n"
             "carries its weight. If the śakti is touched, Brahman is touched: it cannot stay aparas.")
    return f.render()


if __name__ == "__main__":
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        h = fn()
        print(f"{fn.__name__}: height {h:.2f} in")
    if PROBLEMS:
        print("PROBLEMS:")
        for p in PROBLEMS:
            print("  " + p)
    else:
        print("no overflow or overlap detected")
