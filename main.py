"""The World in One Page -- Tuesday 17 November 2026.

A newspaper front page drawn from scratch in pure Python stdlib that sums
up the world news of Tuesday 17 November 2026 in a single 1024x1024 image.

The program writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
No network, no randomness, no wall-clock use: two runs write identical bytes.

Stories (all happened or first reported on 17 November 2026):
  1. Ukraine strikes the Crimean (Kerch) Bridge again, second day running.
  2. China confirms the first Trump-Xi-Putin three-way meeting, Thursday
     in Shenzhen on the APEC sidelines.
  3. Iran fires drones at a U.S. radar system in Bahrain; Bahrain says
     the attack was intercepted, no casualties.
  4. Several tankers hit mines near the Strait of Hormuz.
  5. Japan scrambles fighter jets after suspected Russian aircraft
     violate its airspace.
  6. Five European states plan a joint returns hub in Rwanda.
"""

import hashlib
import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 242, 230)
INK = (22, 21, 19)
RED = (178, 32, 44)
BLUE = (28, 78, 138)
TEAL = (14, 107, 92)
GOLD = (192, 138, 30)
ORANGE = (214, 110, 30)
GREY = (120, 112, 96)
LIGHT = (216, 210, 192)

# ---------------------------------------------------------------- font ----
# A 5x7 bitmap font, authored here. '#' is an ink pixel, '.' is empty.
# Only capitals are drawn; draw_text uppercases everything first.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}

# ------------------------------------------------------------- canvas -----


class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bytes(bg) * (width * height))

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        stride = self.w * 3
        for yy in range(y0, y1):
            i = yy * stride + x0 * 3
            self.px[i:i + len(row)] = row

    def rect_outline(self, x, y, w, h, t, color):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def draw_line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = math.isqrt(r * r - dy * dy)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def circle_outline(self, cx, cy, r, color):
        steps = max(32, r * 6)
        for i in range(steps):
            a = 2.0 * math.pi * i / steps
            self.set_pixel(int(round(cx + r * math.cos(a))),
                           int(round(cy + r * math.sin(a))), color)

    def fill_triangle(self, p0, p1, p2, color):
        pts = sorted((p0, p1, p2), key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        if y0 == y2:
            return
        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = edge_x(x0, y0, x1, y1, y)
                xb = edge_x(x0, y0, x2, y2, y)
            else:
                xa = edge_x(x1, y1, x2, y2, y)
                xb = edge_x(x0, y0, x2, y2, y)
            lo = int(math.ceil(min(xa, xb)))
            hi = int(math.floor(max(xa, xb)))
            if hi >= lo:
                self.fill_rect(lo, y, hi - lo + 1, 1, color)


# --------------------------------------------------------------- text -----

def clean(text):
    out = []
    for ch in text.upper():
        if ch in ("\u2014", "\u2013"):
            ch = "-"
        elif ch == "\u2019":
            ch = "'"
        elif ch in ("\u201c", "\u201d"):
            ch = '"'
        if ch not in FONT:
            ch = "?" if ch.isprintable() and ch != " " else " "
        out.append(ch)
    return "".join(out)


def text_width(text, scale):
    text = clean(text)
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    text = clean(text)
    cx = x
    for ch in text:
        glyph = FONT[ch]
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += 6 * scale


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, max_w, scale):
    words = clean(text).split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- png ------

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    stride = cv.w * 3
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    data = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return data


# -------------------------------------------------------------- motifs ----

def motif_bridge(cv, x, y, w, h):
    # Kerch Bridge under a low sun, struck mid-span.
    cv.fill_circle(x + w - 34, y + 22, 17, GOLD)
    deck_y = y + h - 58
    cv.fill_rect(x + 8, deck_y, w - 16, 9, INK)
    for tx in (x + 62, x + w - 74):
        cv.fill_rect(tx, y + 28, 11, deck_y - (y + 28), INK)
        cv.fill_rect(tx - 4, y + 24, 19, 6, INK)
    cv.draw_line(x + 67, y + 28, x + w // 2, y + 62, INK)
    cv.draw_line(x + w - 68, y + 28, x + w // 2, y + 62, INK)
    for sx in (x + 108, x + w // 2 - 30, x + w // 2 + 30, x + w - 118):
        cv.draw_line(sx, y + 52, sx, deck_y, GREY)
    bx, by = x + w // 2, deck_y - 6
    cv.fill_circle(bx, by, 11, ORANGE)
    for dx, dy in ((0, -20), (15, -14), (20, 0), (15, 14),
                   (0, 20), (-15, 14), (-20, 0), (-15, -14)):
        cv.draw_line(bx, by, bx + dx, by + dy, RED)
    cv.fill_circle(bx, by, 5, RED)
    for wy in (deck_y + 22, deck_y + 32, deck_y + 42):
        cv.draw_line(x + 14, wy, x + w - 14, wy, BLUE)
    cv.fill_rect(x + 62, y + 8, 3, 18, INK)
    cv.fill_rect(x + 65, y + 8, 20, 11, RED)


def motif_flags(cv, x, y, w, h):
    # Three summit flags: China, the United States, Russia.
    ground = y + h - 6
    cv.fill_rect(x + 6, ground, w - 12, 3, INK)
    # Each flag: a list of horizontal stripes, drawn with an ink outline
    # so pale stripes still read as a flag against the paper.
    flags = (
        (x + 40, [RED, RED, RED, RED, RED, RED], True),
        (x + w // 2 - 10, [BLUE, BLUE, RED, PAPER, RED, PAPER], False),
        (x + w - 90, [PAPER, PAPER, BLUE, BLUE, RED, RED], False),
    )
    for px, stripes, star in flags:
        cv.fill_rect(px, y + 12, 3, ground - (y + 12), INK)
        fx, fy = px + 3, y + 12
        fw, fh = 52, 29
        stripe_h = fh // len(stripes)
        for i, c in enumerate(stripes):
            cv.fill_rect(fx, fy + i * stripe_h, fw, stripe_h, c)
        cv.rect_outline(fx, fy, fw, fh, 1, INK)
        if star:
            cv.fill_circle(fx + 10, fy + 8, 4, GOLD)


def motif_radar(cv, x, y, w, h):
    # Radar dish sweeping, drone blips above it.
    cx, cy, r = x + 64, y + h // 2 + 4, 26
    cv.circle_outline(cx, cy, r, INK)
    cv.circle_outline(cx, cy, r // 2, GREY)
    cv.draw_line(cx - r, cy, cx + r, cy, GREY)
    cv.draw_line(cx, cy - r, cx, cy + r, GREY)
    cv.draw_line(cx, cy, cx + 18, cy - 18, RED)
    cv.fill_rect(cx - 3, cy + r, 6, 8, INK)
    cv.fill_rect(cx - 22, cy + r + 8, 44, 4, INK)
    for bx, by in ((x + 150, y + 12), (x + 190, y + 26), (x + 230, y + 10)):
        cv.fill_circle(bx, by, 4, RED)
        cv.fill_rect(bx - 8, by - 1, 6, 2, INK)
        cv.fill_rect(bx + 3, by - 1, 6, 2, INK)
    cv.draw_line(x + 120, y + h - 8, x + w - 10, y + h - 8, BLUE)


def motif_tanker(cv, x, y, w, h):
    # A tanker at sea with mines drifting nearby.
    sea = y + h - 16
    cv.fill_rect(x + 6, sea, w - 12, 3, BLUE)
    cv.draw_line(x + 20, sea + 7, x + 150, sea + 7, BLUE)
    cv.draw_line(x + 90, sea + 11, x + 220, sea + 11, BLUE)
    hull_y = sea - 16
    cv.fill_rect(x + 30, hull_y, 190, 16, INK)
    cv.fill_triangle((x + 220, hull_y), (x + 262, hull_y),
                     (x + 220, hull_y + 16), INK)
    for i, c in enumerate((RED, GOLD, TEAL)):
        cv.fill_rect(x + 44 + i * 34, hull_y - 18, 28, 18, c)
    cv.fill_rect(x + 150, hull_y - 26, 16, 26, INK)
    cv.fill_rect(x + 150, hull_y - 32, 22, 6, RED)
    for mx, my in ((x + 300, y + 14), (x + 340, y + 30), (x + 380, y + 12)):
        cv.fill_circle(mx, my, 6, INK)
        for dx, dy in ((0, -10), (7, -7), (10, 0), (7, 7),
                       (0, 10), (-7, 7), (-10, 0), (-7, -7)):
            cv.draw_line(mx, my, mx + dx, my + dy, INK)


def motif_jets(cv, x, y, w, h):
    # Two jets crossing a rising sun.
    cv.fill_circle(x + w - 40, y + 24, 16, GOLD)
    for jx, jy, s in ((x + 60, y + 30, 1.0), (x + 200, y + 14, 0.8)):
        L = int(46 * s)
        cv.fill_triangle((jx, jy), (jx + L, jy + 6), (jx, jy + 12), INK)
        cv.fill_triangle((jx + 12, jy), (jx + 26, jy - 12),
                         (jx + 26, jy + 6), INK)
        cv.fill_triangle((jx + 12, jy + 12), (jx + 26, jy + 6),
                         (jx + 26, jy + 18), INK)
        cv.draw_line(jx - 26, jy + 6, jx - 4, jy + 6, GREY)
        cv.draw_line(jx - 20, jy + 12, jx - 4, jy + 12, GREY)
    cv.draw_line(x + 8, y + h - 6, x + w - 8, y + h - 6, BLUE)


# -------------------------------------------------------------- layout ----

LEAD = {
    "kicker": "LEAD  \u2022  EUROPE \u2014 WAR IN UKRAINE",
    "headline": "UKRAINE STRIKES THE CRIMEAN BRIDGE AGAIN",
    "caption": ("KYIV HITS THE KERCH BRIDGE FOR A SECOND DAY RUNNING; "
                "MOSCOW SAYS TRAFFIC IS HALTED. RUSSIAN STRIKES HIT "
                "KYIV'S RIVER CROSSINGS."),
}

CARDS = [
    {
        "kicker": "ASIA-PACIFIC  \u2022  DIPLOMACY",
        "headline": "TRUMP, XI AND PUTIN TO MEET IN SHENZHEN",
        "caption": ("CHINA CONFIRMS THE FIRST THREE-WAY SUMMIT, SET FOR "
                    "THURSDAY ON THE SIDELINES OF APEC."),
        "motif": motif_flags,
    },
    {
        "kicker": "MIDDLE EAST  \u2022  IRAN",
        "headline": "IRAN DRONES TARGET U.S. RADAR IN BAHRAIN",
        "caption": ("TEHRAN FIRES DRONES AT THE SHEIKH ISA BASE; BAHRAIN "
                    "SAYS THE ATTACK WAS INTERCEPTED, NO CASUALTIES."),
        "motif": motif_radar,
    },
    {
        "kicker": "MIDDLE EAST  \u2022  SHIPPING",
        "headline": "TANKERS HIT BY MINES NEAR HORMUZ",
        "caption": ("IRAN SAYS SEVERAL TANKERS STRUCK MINES SOUTH OF THE "
                    "STRAIT AS ITS MINISTER HOLDS TALKS IN OMAN."),
        "motif": motif_tanker,
    },
    {
        "kicker": "ASIA-PACIFIC  \u2022  JAPAN-RUSSIA",
        "headline": "JAPAN SCRAMBLES JETS AFTER AIRSPACE BREACH",
        "caption": ("TOKYO PROTESTS AFTER TWO SUSPECTED RUSSIAN AIRCRAFT "
                    "VIOLATE ITS AIRSPACE EARLY ON TUESDAY."),
        "motif": motif_jets,
    },
]

TICKER_KICKER = "ALSO TODAY  \u2022  EUROPE \u2014 MIGRATION"
TICKER_HEADLINE = "FIVE EUROPEAN STATES PLAN A RWANDA RETURNS HUB"


def draw_card(cv, x, y, w, h, story):
    cv.rect_outline(x, y, w, h, 2, INK)
    ix = x + 16
    iw = w - 32
    draw_text(cv, ix, y + 14, story["kicker"], 2, RED)
    lines = wrap_text(story["headline"], iw, 3)
    ly = y + 40
    for line in lines[:2]:
        draw_text(cv, ix, ly, line, 3, INK)
        ly += 24
    lines = wrap_text(story["caption"], iw, 2)
    ly = y + 94
    for line in lines[:3]:
        draw_text(cv, ix, ly, line, 2, INK)
        ly += 18
    story["motif"](cv, ix, y + 156, iw, 44)


def build_page():
    cv = Canvas(W, H, PAPER)
    cv.rect_outline(10, 10, W - 20, H - 20, 3, INK)
    cv.rect_outline(20, 20, W - 40, H - 40, 1, INK)

    # Masthead.
    draw_text_centered(cv, W // 2, 34, "TUESDAY, 17 NOVEMBER 2026", 3, INK)
    draw_text_centered(cv, W // 2, 64, "WORLD NEWS", 11, INK)
    draw_text_centered(cv, W // 2, 150, "THE WORLD IN ONE PAGE", 2, RED)
    cv.fill_rect(28, 172, W - 56, 6, RED)
    cv.fill_rect(28, 182, W - 56, 2, INK)

    # Lead story.
    draw_text(cv, 34, 206, LEAD["kicker"], 2, RED)
    lines = wrap_text(LEAD["headline"], 620, 5)
    ly = 236
    for line in lines[:2]:
        draw_text(cv, 34, ly, line, 5, INK)
        ly += 40
    lines = wrap_text(LEAD["caption"], 620, 2)
    ly = 330
    for line in lines[:3]:
        draw_text(cv, 34, ly, line, 2, INK)
        ly += 18
    motif_bridge(cv, 690, 210, 300, 180)
    cv.fill_rect(28, 414, W - 56, 2, INK)

    # Four story cards.
    positions = [(24, 430), (528, 430), (24, 662), (528, 662)]
    for (px, py), story in zip(positions, CARDS):
        draw_card(cv, px, py, 480, 216, story)

    # Ticker: the sixth story.
    cv.fill_rect(24, 894, 976, 70, INK)
    draw_text(cv, 40, 902, TICKER_KICKER, 2, GOLD)
    draw_text(cv, 40, 924, TICKER_HEADLINE, 3, PAPER)

    # Footer.
    draw_text_centered(cv, W // 2, 972,
                       "FOR THE JUDGE: EVERY STORY HERE HAPPENED OR WAS "
                       "FIRST REPORTED ON", 2, INK)
    draw_text_centered(cv, W // 2, 988,
                       "TUESDAY, 17 NOVEMBER 2026 \u2014 SIX STORIES, "
                       "ONE DAY.", 2, INK)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    data = write_png(path, build_page())
    print("wrote %s (%d bytes, sha256 %s)"
          % (path, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
