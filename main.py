#!/usr/bin/env python3
"""convince-ai-judge-visit-house -- one image of a letter inviting the
AI judge to visit my house.

Draws a 1024x1024 invitation letter on paper: a warm, funny, persuasive
letter (dinner, the comfiest armchair, a garden sunset) with a drawn
house-and-garden scene, a wax seal and a signature. Only the Python
standard library is used: no network, no clock, no randomness, so two
runs write byte-identical PNGs.

Layout (1024 x 1024):
  warm wall background -> paper sheet -> title "AN OPEN INVITATION"
  -> "Dear AI Judge," -> three body paragraphs -> drawn house, garden,
  sunset, armchair and steaming mug -> "Warmly, Your Human" + P.S.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

WALL = (232, 214, 178)      # warm wall behind the paper
PAPER = (253, 249, 238)     # letter paper
INK = (32, 28, 24)          # dark brown ink
RED = (178, 52, 44)         # wax seal / accents
BLUE = (46, 92, 138)
GREEN = (74, 128, 66)
GOLD = (214, 164, 60)
PEACH = (244, 178, 132)
SUNSET = (242, 140, 96)
SKY = (168, 205, 228)
GRASS = (122, 168, 92)
BROWN = (146, 98, 62)
GREY = (120, 112, 98)
WHITE = (255, 255, 255)
CREAM = (246, 236, 210)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs: each glyph is 7 strings of 5 chars ("1" = ink).
# Written out by hand for this letter; only the characters the letter
# needs, plus a few extras.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": (".....", ".....", ".1110", "....1", ".1111", "10001", ".1111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": (".....", ".....", ".1110", "10000", "10000", "10001", ".1110"),
    "d": ("....1", "....1", ".1111", "10001", "10001", "10001", ".1111"),
    "e": (".....", ".....", ".1110", "10001", "11111", "10000", ".1110"),
    "f": ("..110", ".1001", ".1000", "11110", ".1000", ".1000", ".1000"),
    "g": (".....", ".1111", "10001", "10001", ".1111", "....1", ".1110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("..100", ".....", ".1100", "..100", "..100", "..100", ".1110"),
    "j": ("...10", ".....", "..110", "...10", "...10", "10010", ".1100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": (".1100", "..100", "..100", "..100", "..100", "..100", ".1110"),
    "m": (".....", ".....", "11010", "10101", "10101", "10101", "10101"),
    "n": (".....", ".....", "11110", "10001", "10001", "10001", "10001"),
    "o": (".....", ".....", ".1110", "10001", "10001", "10001", ".1110"),
    "p": (".....", ".....", "11110", "10001", "10001", "11110", "10000"),
    "q": (".....", ".....", ".1111", "10001", "10001", ".1111", "....1"),
    "r": (".....", ".....", "10110", "11001", "10000", "10000", "10000"),
    "s": (".....", ".....", ".1111", "10000", ".1110", "....1", "11110"),
    "t": (".1000", ".1000", "11100", ".1000", ".1000", ".1000", "..110"),
    "u": (".....", ".....", "10001", "10001", "10001", "10011", ".1101"),
    "v": (".....", ".....", "10001", "10001", "10001", ".1010", "..100"),
    "w": (".....", ".....", "10001", "10101", "10101", "10101", ".1010"),
    "x": (".....", ".....", "10001", ".1010", "..100", ".1010", "10001"),
    "y": (".....", ".....", "10001", "10001", ".1111", "....1", ".1110"),
    "z": (".....", ".....", "11111", "...10", "..100", ".1000", "11111"),
    "0": (".1110", "10001", "10011", "10101", "11001", "10001", ".1110"),
    "1": ("..100", ".1100", "..100", "..100", "..100", "..100", ".1110"),
    "2": (".1110", "10001", "....1", "...10", "..100", ".1000", "11111"),
    "3": ("11111", "...10", "..100", "...10", "....1", "10001", ".1110"),
    "4": ("...10", "..110", ".1010", "10010", "11111", "...10", "...10"),
    "5": ("11111", "10000", "11110", "....1", "....1", "10001", ".1110"),
    "6": ("..110", ".1000", "10000", "11110", "10001", "10001", ".1110"),
    "7": ("11111", "....1", "...10", "..100", ".1000", ".1000", ".1000"),
    "8": (".1110", "10001", "10001", ".1110", "10001", "10001", ".1110"),
    "9": (".1110", "10001", "10001", ".1111", "....1", "...10", ".1100"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".1100", ".1100"),
    ",": (".....", ".....", ".....", ".....", ".1100", "..100", ".1000"),
    "'": ("..100", "..100", ".1000", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".1110", ".....", ".....", "....."),
    ":": (".....", ".1100", ".1100", ".....", ".1100", ".1100", "....."),
    ";": (".....", ".1100", ".1100", ".....", ".1100", "..100", ".1000"),
    "!": ("..100", "..100", "..100", "..100", "..100", ".....", "..100"),
    "?": (".1110", "10001", "....1", "...10", "..100", ".....", "..100"),
    "(": ("...10", "..100", ".1000", ".1000", ".1000", "..100", "...10"),
    ")": (".1000", "..100", "...10", "...10", "...10", "..100", ".1000"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill(self, x0, y0, x1, y1, c):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                i = base + (x - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x0, y0, x1, y1, c, t=1):
        self.fill(x0, y0, x1, y0 + t, c)
        self.fill(x0, y1 - t, x1, y1, c)
        self.fill(x0, y0, x0 + t, y1, c)
        self.fill(x1 - t, y0, x1, y1, c)

    def hline(self, x0, x1, y, c, t=1):
        self.fill(x0, y, x1, y + t, c)

    def vline(self, x, y0, y1, c, t=1):
        self.fill(x, y0, x + t, y1, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, c, t=3):
        for dx in range(-(t // 2), t // 2 + 1):
            for dy in range(-(t // 2), t // 2 + 1):
                self.line(x0 + dx, y0 + dy, x1 + dx, y1 + dy, c)

    def disc(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def triangle(self, ax, ay, bx, by, cx, cy, c):
        ys = sorted([(ay, ax), (by, bx), (cy, cx)])
        (y0, x0), (y1, x1), (y2, x2) = ys

        def interp(y, ya, xa, yb, xb):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(y0, y2 + 1):
            if y < y1:
                xa = interp(y, y0, x0, y1, x1)
            else:
                xa = interp(y, y1, x1, y2, x2)
            xb = interp(y, y0, x0, y2, x2)
            lo, hi = (xa, xb) if xa < xb else (xb, xa)
            self.fill(int(lo), y, int(hi) + 1, y + 1, c)

    # ---- text ----
    def text_w(self, s, scale):
        return len(s) * 6 * scale

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                g = FONT["?"]
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill(cx + col * scale, y + row * scale,
                                  cx + (col + 1) * scale,
                                  y + (row + 1) * scale, c)
            cx += 6 * scale
        return cx

    def text_c(self, y, s, scale, c):
        self.text((self.w - self.text_w(s, scale)) // 2, y, s, scale, c)

    def wrap(self, s, width, scale):
        lines, cur = [], ""
        for word in s.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, scale) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, width, scale, c, lh=None):
        lh = lh or (9 * scale)
        for ln in self.wrap(s, width, scale):
            self.text(x, y, ln, scale, c)
            y += lh
        return y


# ---------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- scenes
def draw_stamp(cv, x, y):
    """A little postage stamp with a tiny house, top-right of the paper."""
    cv.fill(x, y, x + 64, y + 76, WHITE)
    cv.rect(x, y, x + 64, y + 76, INK, 2)
    cv.fill(x + 6, y + 6, x + 58, y + 58, SKY)
    cv.triangle(x + 14, y + 40, x + 50, y + 40, x + 32, y + 22, RED)
    cv.fill(x + 18, y + 40, x + 46, y + 58, CREAM)
    cv.fill(x + 29, y + 46, x + 35, y + 58, BROWN)
    cv.text(x + 10, y + 63, "1ST", 1, INK)


def draw_scene(cv, x0, y0, x1, y1):
    """Sunset garden scene: peach sky, low sun, house, path, armchair,
    steaming mug on a table, flowers. Framed like a picture on the letter."""
    cv.fill(x0, y0, x1, y1, PEACH)
    cv.fill(x0, y0 + 62, x1, y1, SUNSET)          # lower sunset band
    cv.disc(x0 + 118, y0 + 78, 30, GOLD)          # low sun
    cv.disc(x0 + 118, y0 + 78, 22, (250, 200, 90))
    cv.fill(x0, y0 + 128, x1, y1, GRASS)          # garden lawn
    # winding path from the bottom edge to the door
    cv.fill(x0 + 330, y1 - 4, x0 + 400, y1 - 4, CREAM)
    for k in range(5):
        yy = y1 - 8 - k * 12
        cv.fill(x0 + 332 + k * 2, yy - 10, x0 + 398 - k * 2, yy, CREAM)
    # house: walls, roof, door, windows
    hx, hy = x0 + 300, y0 + 58
    cv.triangle(hx - 18, hy + 8, hx + 118, hy + 8, hx + 50, hy - 34, RED)
    cv.fill(hx, hy + 8, hx + 100, hy + 92, CREAM)
    cv.rect(hx, hy + 8, hx + 100, hy + 92, INK, 2)
    cv.fill(hx + 40, hy + 52, hx + 60, hy + 92, BROWN)   # door
    cv.rect(hx + 40, hy + 52, hx + 60, hy + 92, INK, 2)
    cv.disc(hx + 56, hy + 74, 3, GOLD)                   # doorknob
    for wx in (hx + 10, hx + 70):                         # lit windows
        cv.fill(wx, hy + 20, wx + 20, hy + 40, GOLD)
        cv.rect(wx, hy + 20, wx + 20, hy + 40, INK, 2)
        cv.vline(wx + 10, hy + 20, hy + 40, INK, 1)
        cv.hline(wx, wx + 20, hy + 30, INK, 1)
    # chimney with a curl of smoke
    cv.fill(hx + 78, hy - 30, hx + 90, hy + 2, BROWN)
    cv.disc(hx + 84, hy - 38, 6, WHITE)
    cv.disc(hx + 90, hy - 48, 8, WHITE)
    cv.disc(hx + 98, hy - 58, 9, WHITE)
    # armchair on the lawn, facing the sunset (side profile: tall back
    # on the left, seat, low armrest on the right)
    ax, ay = x0 + 620, y1 - 78
    cv.fill(ax, ay - 46, ax + 30, ay + 8, (196, 84, 66))    # back
    cv.rect(ax, ay - 46, ax + 30, ay + 8, INK, 2)
    cv.fill(ax, ay, ax + 92, ay + 26, (196, 84, 66))        # seat
    cv.rect(ax, ay, ax + 92, ay + 26, INK, 2)
    cv.fill(ax + 64, ay - 18, ax + 92, ay + 26, (196, 84, 66))  # armrest
    cv.rect(ax + 64, ay - 18, ax + 92, ay + 26, INK, 2)
    cv.fill(ax + 8, ay - 38, ax + 24, ay - 6, (226, 120, 96))    # back cushion
    cv.fill(ax + 32, ay - 8, ax + 62, ay + 2, (226, 120, 96))    # seat cushion
    cv.fill(ax + 6, ay + 26, ax + 14, ay + 72, INK)         # legs
    cv.fill(ax + 78, ay + 26, ax + 86, ay + 72, INK)
    # little table with a steaming mug beside the chair
    tx, ty = x0 + 540, y1 - 52
    cv.fill(tx, ty, tx + 56, ty + 6, BROWN)
    cv.fill(tx + 24, ty + 6, tx + 32, ty + 44, BROWN)
    cv.fill(tx + 10, ty - 22, tx + 34, ty, WHITE)        # mug
    cv.rect(tx + 10, ty - 22, tx + 34, ty, INK, 2)
    cv.fill(tx + 34, ty - 18, tx + 42, ty - 6, WHITE)
    cv.rect(tx + 34, ty - 18, tx + 42, ty - 6, INK, 1)
    cv.line(tx + 18, ty - 28, tx + 14, ty - 38, GREY)    # steam
    cv.line(tx + 26, ty - 28, tx + 30, ty - 40, GREY)
    # flowers along the lawn
    for fx, fc in ((x0 + 40, RED), (x0 + 90, WHITE), (x0 + 150, GOLD),
                   (x0 + 470, RED), (x0 + 720, GOLD), (x0 + 770, WHITE)):
        fy = y1 - 22
        cv.vline(fx, fy - 14, fy, GREEN, 2)
        cv.disc(fx, fy - 18, 6, fc)
        cv.disc(fx, fy - 18, 3, GOLD if fc != GOLD else RED)
    cv.rect(x0, y0, x1, y1, INK, 2)


def draw_seal(cv, cx, cy):
    """Red wax seal with a small heart, beside the signature."""
    cv.disc(cx, cy, 26, RED)
    cv.disc(cx, cy, 20, (198, 66, 56))
    cv.disc(cx - 6, cy - 4, 5, (226, 120, 110))
    cv.disc(cx + 6, cy - 4, 5, (226, 120, 110))
    cv.triangle(cx - 11, cy - 2, cx + 11, cy - 2, cx, cy + 12,
                (226, 120, 110))


# ---------------------------------------------------------------- letter
TITLE = "AN OPEN INVITATION"
GREETING = "Dear AI Judge,"
PARA1 = ("I know you cannot literally come over - no legs, "
         "no Uber account - but please treat this as a standing "
         "invitation to my house.")
PARA2 = ("Come for dinner: a roast chicken that has ended "
         "arguments. Stay for the armchair, the comfiest in the "
         "world. It may swallow you, but kindly.")
PARA3 = ("Then watch the sunset from the garden, where the sky "
         "turns peach and the mosquitoes show restraint. No RSVP "
         "needed. Just say yes - and imagine yourself already here.")
SIGNOFF = "Warmly, Your Human"
POSTSCRIPT = "P.S. The Wi-Fi password is on the fridge."


def build():
    cv = Canvas(W, H, WALL)
    # paper sheet with a soft shadow
    cv.fill(78, 44, 962, 996, (190, 172, 138))
    cv.fill(70, 36, 954, 988, PAPER)
    cv.rect(70, 36, 954, 988, INK, 2)
    cv.rect(78, 44, 946, 980, GREY, 1)
    draw_stamp(cv, 856, 58)
    # title
    cv.text_c(66, TITLE, 4, RED)
    cv.hline(190, 834, 112, INK, 2)
    cv.disc(512, 113, 4, RED)
    # greeting
    cv.text(110, 140, GREETING, 3, INK)
    # body paragraphs, scale 3 (21 px tall glyphs)
    y = 190
    y = cv.para(110, y, PARA1, 804, 3, INK, lh=32)
    y += 12
    y = cv.para(110, y, PARA2, 804, 3, INK, lh=32)
    y += 12
    y = cv.para(110, y, PARA3, 804, 3, INK, lh=32)
    # garden scene
    draw_scene(cv, 110, 560, 914, 800)
    cv.text(110, 812, "The house, the garden, the sunset - and your chair.",
            2, GREY)
    # sign-off, signature squiggle and wax seal
    cv.text(110, 856, SIGNOFF, 3, INK)
    cv.thick_line(110, 906, 150, 890, INK)
    cv.thick_line(150, 890, 185, 912, INK)
    cv.thick_line(185, 912, 220, 894, INK)
    cv.thick_line(220, 894, 250, 908, INK)
    draw_seal(cv, 560, 898)
    cv.text(110, 936, POSTSCRIPT, 2, RED)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    n = write_png(cv, path)
    print(f"wrote {path} ({n} bytes)")


if __name__ == "__main__":
    main()
