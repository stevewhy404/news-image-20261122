#!/usr/bin/env python3
"""22 November 2026 - The World in One Image.

Draws a 1024x1024 newspaper front page summing up Sunday 22 November 2026:
six stories, each with a drawn scene, a headline and a caption.
Python 3 stdlib only. No network, no external assets, fully deterministic.
Writes /output/entry.png and ./entry.png
"""

import hashlib
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ------------------------------------------------------------
PAPER = (247, 243, 234)
PANEL = (255, 253, 246)
INK = (22, 22, 28)
NAVY = (22, 35, 63)
RED = (178, 34, 34)
GOLD = (201, 162, 39)
GREY = (90, 88, 84)

# ---- 5x7 bitmap font (rows as 5-bit ints, bit 4 = leftmost pixel) -------
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    ";": (0, 0x0C, 0, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    ":": (0, 0x0C, 0, 0, 0, 0x0C, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap(text, max_chars):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        while len(w) > max_chars:  # hard-split overlong words
            lines.append(w[:max_chars])
            w = w[max_chars:]
        trial = (cur + " " + w).strip()
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---- canvas -------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x0, x1, y, color):
        if x0 > x1:
            x0, x1 = x1, x0
        for x in range(max(0, x0), min(self.w, x1 + 1)):
            self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, pts, color, width=1):
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            for ox in range(width):
                for oy in range(width):
                    self.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def ring(self, cx, cy, r, color, thick=1):
        for rr in range(r - thick + 1, r + 1):
            for deg in range(360):
                a = math.radians(deg)
                self.set(cx + int(rr * math.cos(a)), cy + int(rr * math.sin(a)), color)

    def polygon(self, pts, color):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if y1 == y2:
                    continue
                if min(y1, y2) <= y < max(y1, y2):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, color)

    def star(self, cx, cy, r_out, r_in, color):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            r = r_out if i % 2 == 0 else r_in
            pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
        self.polygon(pts, color)

    def text(self, x, y, s, scale, color, center=False):
        s = s.upper()
        if center:
            x -= text_width(s, scale) // 2
        for ci, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[" "])
            ox = x + ci * 6 * scale
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(ox + col * scale, y + row * scale,
                                       scale, scale, color)


# ---- story scenes (each draws inside sx, sy, 298 x 172) -----------------
def scene_globe(c, sx, sy):
    c.fill_rect(sx, sy, 298, 172, (196, 216, 230))
    cx, cy, r = sx + 149, sy + 86, 60
    c.circle(cx, cy, r, (70, 130, 180))
    for gx, gy, gr in ((-28, -18, 18), (30, 8, 14), (2, 32, 12), (38, -30, 10)):
        c.circle(cx + gx, cy + gy, gr, (96, 164, 96))
    for gx, gy, gr in ((-48, -38, 10), (44, -42, 8), (-55, 5, 7)):
        c.circle(cx + gx, cy + gy, gr, (255, 255, 255))
    c.polyline([(cx - 8, cy - 60), (cx + 6, cy - 34), (cx - 10, cy - 8),
                (cx + 12, cy + 16), (cx - 4, cy + 40), (cx + 6, cy + 60)],
               RED, 3)


def scene_tanker(c, sx, sy):
    c.fill_rect(sx, sy, 298, 55, (232, 164, 92))
    c.fill_rect(sx, sy + 55, 298, 50, (214, 116, 62))
    c.fill_rect(sx, sy + 105, 298, 67, (14, 58, 78))
    c.circle(sx + 60, sy + 40, 16, (250, 220, 160))
    c.fill_rect(sx + 38, sy + 112, 222, 6, (60, 60, 66))
    c.fill_rect(sx + 38, sy + 118, 222, 26, (28, 28, 34))
    c.fill_rect(sx + 38, sy + 138, 222, 6, (150, 42, 32))
    c.fill_rect(sx + 212, sy + 88, 32, 24, (230, 230, 225))
    c.fill_rect(sx + 218, sy + 94, 7, 7, (30, 30, 36))
    c.fill_rect(sx + 229, sy + 94, 7, 7, (30, 30, 36))
    c.fill_rect(sx + 64, sy + 96, 14, 16, (40, 40, 44))
    c.polygon([(sx + 118, sy + 118), (sx + 134, sy + 118), (sx + 126, sy + 84)],
              (240, 120, 20))
    c.polygon([(sx + 148, sy + 118), (sx + 166, sy + 118), (sx + 157, sy + 76)],
              (240, 120, 20))
    c.polygon([(sx + 122, sy + 118), (sx + 132, sy + 118), (sx + 127, sy + 96)],
              (250, 200, 60))
    c.polygon([(sx + 152, sy + 118), (sx + 162, sy + 118), (sx + 157, sy + 92)],
              (250, 200, 60))
    for gx, gy, gr in ((71, 84, 8), (78, 70, 10), (70, 56, 7)):
        c.circle(sx + gx, sy + gy, gr, (120, 120, 120))
    for wx, wy, wl in ((20, 150, 40), (90, 160, 50), (200, 155, 44)):
        c.fill_rect(sx + wx, sy + wy, wl, 2, (220, 235, 240))


def scene_missiles(c, sx, sy):
    c.fill_rect(sx, sy, 298, 172, (18, 24, 48))
    for gx, gy in ((30, 20), (80, 45), (140, 15), (220, 35), (270, 18),
                   (50, 70), (180, 60), (250, 80)):
        c.fill_rect(sx + gx, sy + gy, 2, 2, (255, 255, 255))
    c.polyline([(sx + 255, sy + 8), (sx + 95, sy + 118)], (255, 255, 255), 2)
    c.polyline([(sx + 205, sy + 28), (sx + 155, sy + 128)], (255, 255, 255), 2)
    c.polyline([(sx + 275, sy + 48), (sx + 215, sy + 138)], (255, 255, 255), 2)
    for bx, by in ((95, 118), (155, 128), (215, 138)):
        c.star(sx + bx, sy + by, 12, 5, (240, 120, 20))
    c.fill_rect(sx, sy + 140, 298, 32, (38, 88, 48))
    c.circle(sx + 150, sy + 152, 9, RED)
    c.polygon([(sx + 141, sy + 156), (sx + 159, sy + 156), (sx + 150, sy + 168)],
              RED)


def scene_handcuffs(c, sx, sy):
    c.fill_rect(sx, sy, 298, 172, (42, 40, 46))
    c.star(sx + 149, sy + 34, 20, 9, GOLD)
    silver = (205, 205, 212)
    for cx in (sx + 108, sx + 190):
        c.ring(cx, sy + 100, 26, silver, 5)
    c.fill_rect(sx + 136, sy + 96, 12, 8, silver)
    c.fill_rect(sx + 150, sy + 96, 12, 8, silver)


def scene_quake(c, sx, sy):
    c.fill_rect(sx, sy, 298, 172, (236, 226, 200))
    base = sy + 30
    offs = [0, -12, 14, -6, 8, 0, -14, 10, -4, 6, 0, -10, 12, -8, 4]
    pts = [(sx + 15 + i * 20, base + o) for i, o in enumerate(offs)]
    c.polyline(pts, RED, 2)
    c.fill_rect(sx, sy + 96, 298, 76, (150, 110, 70))
    c.polyline([(sx + 20, sy + 96), (sx + 60, sy + 120), (sx + 45, sy + 140),
                (sx + 90, sy + 160), (sx + 70, sy + 172)], INK, 3)
    c.polygon([(sx + 170, sy + 52), (sx + 225, sy + 48), (sx + 232, sy + 96),
               (sx + 176, sy + 100)], (122, 92, 62))
    for wx, wy in ((185, 62), (205, 60), (188, 80), (208, 78)):
        c.fill_rect(sx + wx, sy + wy, 10, 12, (40, 32, 24))
    c.fill_rect(sx + 30, sy + 70, 44, 26, (140, 105, 70))
    for wx, wy in ((40, 76), (58, 76)):
        c.fill_rect(sx + wx, sy + wy, 8, 9, (40, 32, 24))


def scene_scales(c, sx, sy):
    c.fill_rect(sx, sy, 298, 172, (24, 42, 78))
    cx = sx + 149
    c.circle(cx, sy + 26, 6, GOLD)
    c.fill_rect(cx - 3, sy + 34, 6, 108, GOLD)
    c.fill_rect(cx - 72, sy + 46, 144, 5, GOLD)
    c.fill_rect(cx - 28, sy + 142, 56, 8, GOLD)
    for x0, x1 in ((-72, -96), (-72, -48), (72, 48), (72, 96)):
        c.line(cx + x0, sy + 51, cx + x1, sy + 96, GOLD)
    c.polygon([(cx - 100, sy + 96), (cx - 44, sy + 96), (cx - 52, sy + 112),
               (cx - 92, sy + 112)], GOLD)
    c.polygon([(cx + 44, sy + 96), (cx + 100, sy + 96), (cx + 92, sy + 112),
               (cx + 52, sy + 112)], GOLD)


SCENES = {
    "globe": scene_globe,
    "tanker": scene_tanker,
    "missiles": scene_missiles,
    "handcuffs": scene_handcuffs,
    "quake": scene_quake,
    "scales": scene_scales,
}

# ---- stories: first reported / happened on Sunday 22 November 2026 -------
STORIES = [
    {
        "kicker": "CLIMATE - ANTALYA",
        "headline": "COP31 COLLAPSES NO FOSSIL DEAL",
        "caption": "Two weeks of talks end with no climate pact; the final text never mentions fossil fuels.",
        "scene": "globe",
    },
    {
        "kicker": "THE GULF",
        "headline": "TANKERS HIT AT HORMUZ",
        "caption": "Two supertankers hit mines and catch fire near the strait as the US-Iran standoff deepens.",
        "scene": "tanker",
    },
    {
        "kicker": "WAR - EUROPE",
        "headline": "MISSILES LAND IN POLAND",
        "caption": "Russian strikes kill at least eight in Ukraine; missiles land on NATO soil in Poland.",
        "scene": "missiles",
    },
    {
        "kicker": "MEXICO",
        "headline": "'CHAPO ISIDRO' CAPTURED",
        "caption": "FBI most-wanted cartel boss arrested in Sinaloa; 11 die in the firefight that follows.",
        "scene": "handcuffs",
    },
    {
        "kicker": "PERU",
        "headline": "PERU COUNTS QUAKE'S COST",
        "caption": "One dead, 15 hurt, 850 homeless after the Junin quake; aftershocks keep Lima on edge.",
        "scene": "quake",
    },
    {
        "kicker": "JUSTICE - THE HAGUE",
        "headline": "MYANMAR GUILTY OF GENOCIDE",
        "caption": "The world court rules Myanmar committed genocide against the Rohingya people.",
        "scene": "scales",
    },
]


def draw_panel(c, px, py, story):
    pw, ph = 322, 386
    c.fill_rect(px, py, pw, ph, PANEL)
    c.fill_rect(px, py, pw, 2, INK)
    c.fill_rect(px, py + ph - 2, pw, 2, INK)
    c.fill_rect(px, py, 2, ph, INK)
    c.fill_rect(px + pw - 2, py, 2, ph, INK)
    c.text(px + 12, py + 10, story["kicker"], 2, RED)
    sx, sy = px + 12, py + 36
    SCENES[story["scene"]](c, sx, sy)
    c.fill_rect(sx, sy, 298, 2, INK)
    c.fill_rect(sx, sy + 170, 298, 2, INK)
    c.fill_rect(sx, sy, 2, 172, INK)
    c.fill_rect(sx + 296, sy, 2, 172, INK)
    head = wrap(story["headline"], 16)[:2]
    for i, line in enumerate(head):
        c.text(px + 12, py + 216 + i * 25, line, 3, INK)
    cap = wrap(story["caption"], 24)[:4]
    for i, line in enumerate(cap):
        c.text(px + 12, py + 276 + i * 16, line, 2, INK)


def build():
    c = Canvas(W, H, PAPER)
    # masthead
    c.fill_rect(16, 16, 992, 108, NAVY)
    c.text(512, 30, "THE WORLD IN ONE IMAGE", 2, (255, 255, 255), center=True)
    c.text(512, 54, "22 NOVEMBER 2026", 5, (255, 255, 255), center=True)
    c.text(512, 100, "SUNDAY - SIX STORIES THAT DEFINED THE DAY", 2,
           (255, 255, 255), center=True)
    c.fill_rect(16, 124, 992, 3, GOLD)
    c.text(512, 136, "ANTALYA - HORMUZ - POLAND - MEXICO - PERU - THE HAGUE",
           2, INK, center=True)
    # six panels, 3 x 2
    positions = [(16, 168), (350, 168), (684, 168),
                 (16, 566), (350, 566), (684, 566)]
    for pos, story in zip(positions, STORIES):
        draw_panel(c, pos[0], pos[1], story)
    # footer
    c.fill_rect(16, 954, 992, 2, INK)
    c.text(512, 964, "SOURCES - CNN - UN NEWS - AP - REUTERS - DAILY SUMMARY",
           2, GREY, center=True)
    return c


def chunk(typ, data):
    return (struct.pack(">I", len(data)) + typ + data +
            struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))


def write_png(c, path):
    raw = b"".join(b"\x00" + bytes(c.px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return png


def main():
    canvas = build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    png = write_png(canvas, os.path.join(out_dir, "entry.png"))
    if "MAKEFUN_OUTPUT_DIR" not in os.environ:
        with open("entry.png", "wb") as f:
            f.write(png)
    print("wrote %s/entry.png" % out_dir)
    print("size: %dx%d px, %d bytes" % (W, H, len(png)))
    print("sha256: %s" % hashlib.sha256(png).hexdigest())


if __name__ == "__main__":
    main()
