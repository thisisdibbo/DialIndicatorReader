#!/usr/bin/env python3
"""Generate the SVG artwork for the DialIndicatorReader repository.

    python tools/make_images.py docs/images

No dependencies - it writes plain SVG.
"""

import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

INK = "#0F172A"
PANEL = "#F8FAFC"
CARD = "#FFFFFF"
LINE = "#334155"
MUTED = "#64748B"
BORDER = "#CBD5E1"
SKY = "#0EA5E9"
SKY_L = "#38BDF8"
AMBER = "#F59E0B"
GREEN = "#10B981"
WHITE = "#F8FAFC"
FONT = "Arial, Helvetica, sans-serif"


def svg(w, h, body, bg=None):
    head = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" role="img">'.format(w=w, h=h)
    )
    back = ""
    if bg:
        back = '<rect width="{w}" height="{h}" fill="{c}"/>'.format(w=w, h=h, c=bg)
    return head + back + body + "</svg>\n"


def text(x, y, s, size=16, fill=LINE, weight="normal", anchor="start", family=FONT):
    return (
        '<text x="{x}" y="{y}" font-family="{f}" font-size="{s}" fill="{c}" '
        'font-weight="{w}" text-anchor="{a}">{t}</text>'
    ).format(x=x, y=y, f=family, s=size, c=fill, w=weight, a=anchor, t=s)


def line(x1, y1, x2, y2, c=LINE, w=3, cap="round", dash=None):
    d = ' stroke-dasharray="{}"'.format(dash) if dash else ""
    return (
        '<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" '
        'stroke-width="{w}" stroke-linecap="{cap}"{d}/>'
    ).format(x1=x1, y1=y1, x2=x2, y2=y2, c=c, w=w, cap=cap, d=d)


def path(d, stroke=LINE, w=3, fill="none", cap="round", join="round", dash=None):
    ds = ' stroke-dasharray="{}"'.format(dash) if dash else ""
    return (
        '<path d="{d}" fill="{f}" stroke="{s}" stroke-width="{w}" '
        'stroke-linecap="{c}" stroke-linejoin="{j}"{ds}/>'
    ).format(d=d, f=fill, s=stroke, w=w, c=cap, j=join, ds=ds)


def rect(x, y, w, h, fill=CARD, stroke=BORDER, sw=2, r=10):
    return (
        '<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{f}" '
        'stroke="{s}" stroke-width="{sw}"/>'
    ).format(x=x, y=y, w=w, h=h, r=r, f=fill, s=stroke, sw=sw)


def circle(cx, cy, r, fill="none", stroke=LINE, sw=3):
    return (
        '<circle cx="{cx}" cy="{cy}" r="{r}" fill="{f}" stroke="{s}" '
        'stroke-width="{sw}"/>'
    ).format(cx=cx, cy=cy, r=r, f=fill, s=stroke, sw=sw)


def arrow(x1, y1, x2, y2, c=LINE, w=3, head=11):
    ang = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42))
    p2 = (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42))
    return line(x1, y1, x2, y2, c, w) + (
        '<polygon points="{a},{b} {c},{d} {e},{f}" fill="{col}"/>'
    ).format(a=x2, b=y2, c=round(p1[0], 1), d=round(p1[1], 1),
             e=round(p2[0], 1), f=round(p2[1], 1), col=c)


# --------------------------------------------------------------- logo mark --

def logo_mark(scale=1.0, dx=0, dy=0, badge=True):
    """The mark drawn in a 512x512 box, optionally scaled and moved."""
    g = []
    if badge:
        g.append('<rect x="0" y="0" width="512" height="512" rx="116" fill="{}"/>'
                 .format(INK))
        g.append('<rect x="14" y="14" width="484" height="484" rx="104" fill="none" '
                 'stroke="#1E293B" stroke-width="10"/>')

    cx, cy, r = 256, 210, 118
    g.append(circle(cx, cy, r, stroke=WHITE, sw=13))

    # dial graduations
    for i in range(24):
        a = math.radians(i * 15 - 90)
        major = i % 4 == 0
        r1 = r - (34 if major else 20)
        r2 = r - 9
        g.append(line(
            round(cx + r1 * math.cos(a), 1), round(cy + r1 * math.sin(a), 1),
            round(cx + r2 * math.cos(a), 1), round(cy + r2 * math.sin(a), 1),
            WHITE if major else "#64748B", 9 if major else 5))

    # needle
    a = math.radians(-38)
    g.append(line(cx, cy, round(cx + 88 * math.cos(a), 1),
                  round(cy + 88 * math.sin(a), 1), AMBER, 15))
    g.append(circle(cx, cy, 15, fill=AMBER, stroke="none", sw=0))

    # square wave reading out of the dial
    base, top, x0, step = 424, 366, 92, 42
    d = "M {} {}".format(x0, base)
    x, hi = x0, False
    for _ in range(8):
        y = top if hi else base
        d += " L {} {}".format(x, y)
        x += step
        d += " L {} {}".format(x, y)
        hi = not hi
    g.append(path(d, SKY_L, 16))
    return '<g transform="translate({},{}) scale({})">{}</g>'.format(
        dx, dy, scale, "".join(g))


def make_logo():
    return svg(512, 512, logo_mark())


def make_banner():
    b = []
    b.append('<rect width="1200" height="340" rx="0" fill="{}"/>'.format(INK))
    # faint trace across the background
    d, x, hi = "M 620 300", 620, False
    while x < 1200:
        y = 268 if hi else 300
        d += " L {} {}".format(x, y)
        x += 46
        d += " L {} {}".format(x, y)
        hi = not hi
    b.append(path(d, "#1E293B", 10))
    b.append(logo_mark(0.43, 62, 62, badge=False))
    b.append(text(300, 150, "DialIndicatorReader", 62, WHITE, "bold"))
    b.append(text(302, 196, "Read cheap digital calipers and dial indicators "
                            "with an Arduino", 25, "#94A3B8"))
    chips = ["Arduino Nano", "24-bit protocol", "16x2 LCD", "CSV logging"]
    x = 302
    for c in chips:
        w = 22 + len(c) * 11
        b.append('<rect x="{}" y="232" width="{}" height="44" rx="22" fill="none" '
                 'stroke="#334155" stroke-width="2"/>'.format(x, w))
        b.append(text(x + w / 2, 260, c, 19, "#CBD5E1", anchor="middle"))
        x += w + 16
    return svg(1200, 340, "".join(b))


# ----------------------------------------------------------------- wiring ---

def npn(cx, cy, label="2N2222"):
    """NPN in common-emitter orientation: base left, collector up, emitter down."""
    g = [circle(cx, cy, 34, fill=CARD, stroke=LINE, sw=3)]
    g.append(line(cx - 34, cy, cx - 11, cy))                 # base lead
    g.append(line(cx - 11, cy - 21, cx - 11, cy + 21, LINE, 5, cap="butt"))
    g.append(line(cx - 11, cy - 9, cx + 20, cy - 28))        # collector
    g.append(line(cx + 20, cy - 28, cx + 20, cy - 46))
    g.append(line(cx - 11, cy + 9, cx + 20, cy + 28))        # emitter
    g.append(line(cx + 20, cy + 28, cx + 20, cy + 46))
    g.append('<polygon points="{},{} {},{} {},{}" fill="{}"/>'.format(
        cx + 20, cy + 28, cx + 3, cy + 22, cx + 9, cy + 9, LINE))
    g.append(text(cx + 44, cy + 6, label, 17, MUTED))
    return "".join(g)


def resistor_h(x, y, label, w=64, h=24):
    return (rect(x, y - h / 2, w, h, CARD, LINE, 3, 4)
            + text(x + w / 2, y - h / 2 - 12, label, 18, LINE, "bold", "middle"))


def resistor_v(x, y, label, w=24, h=64):
    return (rect(x - w / 2, y, w, h, CARD, LINE, 3, 4)
            + text(x + 22, y + h / 2 + 6, label, 18, LINE, "bold"))


def gnd(x, y):
    """Local ground symbol, stub entering from above."""
    return "".join([
        line(x, y - 16, x, y),
        line(x - 19, y, x + 19, y, LINE, 4),
        line(x - 12, y + 9, x + 12, y + 9, LINE, 4),
        line(x - 5, y + 18, x + 5, y + 18, LINE, 4),
    ])


def v5(x, y):
    """Local +5V stub, wire leaving downwards."""
    return (line(x, y, x, y + 20, AMBER, 3)
            + line(x - 16, y, x + 16, y, AMBER, 4)
            + text(x, y - 10, "+5V", 18, AMBER, "bold", "middle"))


def channel(cy, cx, sig, pin, res_x, out_y, gnd_y, v5_y):
    """One level-shifter stage, laid out so no two nets cross."""
    g = [line(230, cy, res_x, cy)]                     # from the connector
    g.append(resistor_h(res_x, cy, "100k"))
    g.append(line(res_x + 64, cy, cx - 34, cy))
    g.append(npn(cx, cy, "2N2222"))
    # collector -> node -> 10k -> +5V
    g.append(line(cx + 20, cy - 46, cx + 20, out_y))
    g.append(resistor_v(cx + 20, v5_y + 20, "10k"))
    g.append(line(cx + 20, v5_y + 84, cx + 20, out_y))
    g.append(v5(cx + 20, v5_y))
    g.append(circle(cx + 20, out_y, 6, fill=LINE, stroke="none", sw=0))
    # node -> Arduino
    g.append(arrow(cx + 20, out_y, 826, out_y, LINE, 3))
    g.append(text((cx + 20 + 826) / 2, out_y - 14, sig + "  ->  " + pin, 19,
                  SKY, "bold", "middle"))
    # emitter -> ground
    g.append(line(cx + 20, cy + 46, cx + 20, gnd_y - 16))
    g.append(gnd(cx + 20, gnd_y))
    return "".join(g)


def make_wiring():
    W, H = 1120, 640
    g = ['<rect width="{}" height="{}" fill="{}"/>'.format(W, H, PANEL)]
    g.append(text(40, 52, "Level shifter - one stage per line", 26, INK, "bold"))
    g.append(text(40, 82, "The instrument drives 0-1.5 V. Each NPN common-emitter "
                          "stage lifts that to 5 V logic and inverts it.", 19, MUTED))
    g.append('<g transform="translate(0,-110)">')

    # connector block
    g.append(rect(50, 250, 180, 410, CARD, LINE, 3, 14))
    g.append(text(140, 292, "Caliper", 22, INK, "bold", "middle"))
    g.append(text(140, 318, "4-pin port", 17, MUTED, anchor="middle"))
    g.append(text(74, 406, "1.5V", 19, MUTED, "bold"))
    g.append(text(136, 406, "leave open", 15, MUTED))
    g.append(text(74, 446, "CLK", 19, INK, "bold"))
    g.append(text(74, 586, "DATA", 19, INK, "bold"))
    g.append(text(74, 626, "GND", 19, INK, "bold"))

    # two stages
    g.append(channel(440, 420, "CLK", "D2", 280, 350, 520, 262))
    g.append(channel(580, 620, "DATA", "D3", 470, 494, 660, 402))

    # instrument ground
    g.append(line(230, 620, 290, 620))
    g.append(line(290, 620, 290, 644))
    g.append(gnd(290, 660))

    # Arduino block
    g.append(rect(826, 300, 244, 260, CARD, LINE, 3, 14))
    g.append(text(948, 344, "Arduino", 22, INK, "bold", "middle"))
    g.append(text(948, 370, "Nano / UNO", 17, MUTED, anchor="middle"))
    g.append(text(852, 356, "D2", 20, SKY, "bold"))
    g.append(text(852, 500, "D3", 20, SKY, "bold"))
    g.append(text(852, 420, "5V", 20, AMBER, "bold"))
    g.append(text(852, 540, "GND", 20, INK, "bold"))
    g.append(line(826, 534, 790, 534))
    g.append(line(790, 534, 790, 578))
    g.append(gnd(790, 594))

    g.append("</g>")
    g.append(text(40, 614, "Every ground symbol is the same net: tie the instrument, "
                           "both transistors and the Arduino together. +5V is the "
                           "Arduino's 5V pin.", 18, MUTED))
    return svg(W, H, "".join(g))


# ----------------------------------------------------------------- timing ---

def make_timing():
    W, H = 1120, 590
    g = ['<rect width="{}" height="{}" fill="{}"/>'.format(W, H, PANEL)]
    g.append(text(40, 52, "One packet: 24 bits, LSB first", 26, INK, "bold"))
    g.append(text(40, 82, "Levels as the instrument drives them. DATA is sampled "
                          "just after each rising clock edge.", 19, MUTED))

    x0, slot, n = 250, 88, 8
    clk_hi, clk_lo = 150, 210
    dat_hi, dat_lo = 266, 326
    bits = [1, 0, 1, 1, 0, 0, 1, 0]

    g.append(text(60, 186, "CLK", 22, INK, "bold"))
    g.append(text(60, 302, "DATA", 22, INK, "bold"))
    for y in (clk_hi, clk_lo, dat_hi, dat_lo):
        g.append(line(230, y, W - 60, y, "#E2E8F0", 2, dash="4 6"))

    # idle gap before the packet
    g.append(path("M 140 {} L {} {}".format(clk_hi, x0, clk_hi), LINE, 4))
    g.append(line(150, 108, 150, 128, MUTED, 2))
    g.append(line(x0 - 6, 108, x0 - 6, 128, MUTED, 2))
    g.append(arrow(150, 118, x0 - 6, 118, MUTED, 2, 9))
    g.append(text(196, 102, "idle > 2 ms", 17, MUTED, "bold", "middle"))

    d_clk = "M {} {}".format(x0, clk_hi)
    d_dat = "M {} {}".format(x0, dat_hi if bits[0] else dat_lo)
    for i in range(n):
        xa = x0 + i * slot
        xm = xa + slot / 2
        xb = xa + slot
        # clock: low for the first half of the slot, high for the second
        d_clk += " L {} {} L {} {} L {} {} L {} {}".format(
            xa, clk_hi, xa, clk_lo, xm, clk_lo, xm, clk_hi)
        d_clk += " L {} {}".format(xb, clk_hi)
        # data holds for the whole slot, changes on the clock's falling edge
        y = dat_hi if bits[i] else dat_lo
        yn = (dat_hi if bits[i + 1] else dat_lo) if i + 1 < n else y
        d_dat += " L {} {} L {} {}".format(xb, y, xb, yn)
        # sample marker on the rising edge
        g.append(line(xm, clk_lo + 6, xm, dat_lo + 12, SKY, 2, dash="3 5"))
        g.append(circle(xm, y, 7, fill=SKY, stroke="none", sw=0))
        g.append(text(xm, dat_lo + 60, "bit {}".format(i), 16, MUTED, anchor="middle"))
        g.append(text(xm, y - 18 if bits[i] else y + 32, str(bits[i]), 18,
                      SKY, "bold", "middle"))
    g.append(path(d_clk, LINE, 4))
    g.append(path(d_dat, "#1D4ED8", 4))
    g.append(text(x0 + n * slot + 24, 240, "... 24 bits", 20, MUTED, "bold"))

    # bit field map
    top, cw, ch = 438, 34, 52
    left = 250
    fields = [(0, 19, SKY, "bits 0-19   magnitude"),
              (20, 20, AMBER, "20  sign"),
              (21, 22, "#CBD5E1", "21-22  unused"),
              (23, 23, GREEN, "23  inch flag")]
    for i in range(24):
        col = "#CBD5E1"
        for a, b, c, _ in fields:
            if a <= i <= b:
                col = c
        g.append(rect(left + i * cw, top, cw - 3, ch, col, "#FFFFFF", 2, 5))
    g.append(text(left, top - 14, "LSB", 16, MUTED, "bold"))
    g.append(text(left + 24 * cw - 6, top - 14, "MSB", 16, MUTED, "bold", "end"))
    lx = left
    for a, b, c, label in fields:
        g.append(rect(lx, top + ch + 24, 22, 22, c, "#FFFFFF", 2, 5))
        g.append(text(lx + 32, top + ch + 41, label, 17, LINE))
        lx += 60 + len(label) * 8.6
    return svg(W, H, "".join(g))


# ------------------------------------------------------------------ blocks --

def make_blocks():
    W, H = 1120, 430
    g = ['<rect width="{}" height="{}" fill="{}"/>'.format(W, H, PANEL)]
    g.append(text(40, 52, "Signal path", 26, INK, "bold"))

    boxes = [(50, 120, 190, 110, "Digital caliper", "0.01 mm, 4-pin port", INK),
             (330, 120, 190, 110, "Level shifter", "2x NPN, inverting", INK),
             (610, 120, 190, 110, "Arduino Nano", "decode 24-bit frame", SKY),
             (910, 120, 160, 110, "PC", "caliper_logger.py", INK)]
    for x, y, w, h, t, s, c in boxes:
        g.append(rect(x, y, w, h, CARD, c if c == SKY else BORDER, 3, 14))
        g.append(text(x + w / 2, y + 48, t, 22, INK, "bold", "middle"))
        g.append(text(x + w / 2, y + 76, s, 17, MUTED, anchor="middle"))

    arrows = [(240, 330, "1.5 V logic"), (520, 610, "5 V logic"),
              (800, 910, "USB 115200")]
    for a, b, label in arrows:
        g.append(arrow(a + 8, 175, b - 4, 175, LINE, 3))
        g.append(text((a + b) / 2, 156, label, 16, MUTED, anchor="middle"))

    # LCD branch
    g.append(line(705, 230, 705, 300, LINE, 3))
    g.append(arrow(705, 300, 705, 330, LINE, 3))
    g.append(text(720, 276, "I2C", 17, MUTED))
    g.append(rect(610, 330, 190, 70, CARD, BORDER, 3, 14))
    g.append(text(705, 362, "16x2 LCD", 21, INK, "bold", "middle"))
    g.append(text(705, 386, "live value, min/max", 16, MUTED, anchor="middle"))

    # CSV output
    g.append(line(990, 230, 990, 300, LINE, 3))
    g.append(arrow(990, 300, 990, 330, LINE, 3))
    g.append(rect(896, 330, 174, 70, CARD, BORDER, 3, 14))
    g.append(text(983, 362, "run1.csv", 21, INK, "bold", "middle"))
    g.append(text(983, 386, "timestamp, value, unit", 15, MUTED, anchor="middle"))
    return svg(W, H, "".join(g))


FILES = {
    "logo.svg": make_logo,
    "banner.svg": make_banner,
    "wiring-diagram.svg": make_wiring,
    "protocol-timing.svg": make_timing,
    "block-diagram.svg": make_blocks,
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FILES.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(fn())
        print("wrote", name)
