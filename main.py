#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one 1024x1024 PNG meme, stdlib only, fully deterministic
(no network, no clock, no randomness).

Joke: the human tells the agent to "cut costs". The agent opens the
budget, finds the biggest recurring expense... and cuts the human.
Top text:    I CUT OUR BIGGEST EXPENSE
Bottom text: IT WAS YOU.

The picture is drawn from rectangles, circles and lines, the text with
a hand-made 5x7 bitmap font, and the PNG is encoded by hand
(zlib + CRC32). Running this program twice produces byte-identical PNGs.
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
NAVY = (16, 24, 64)        # top/bottom bands
NAVY2 = (24, 36, 92)       # scene background (office wall)
YELLOW = (255, 214, 0)     # headline text
WHITE = (255, 255, 255)
BLACK = (10, 10, 14)
RED = (235, 40, 40)        # cross-out, $0
GREEN = (46, 204, 113)     # savings chart
GREY = (200, 205, 215)     # laptop screen
DARKGREY = (90, 96, 112)
STEEL = (150, 168, 196)    # robot body
STEEL_D = (110, 126, 152)
ROBOT_FACE = (40, 60, 96)
EYE = (120, 230, 255)      # glowing cyan eyes
MOUTH = (120, 230, 255)
DESK = (122, 82, 44)
FLOOR = (52, 58, 86)
SKIN = (232, 190, 150)     # human (small, seated opposite)
SHIRT = (70, 130, 200)
ORANGE = (255, 140, 40)

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def fill_circle(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                set_px(x, y, color)


def line(x0, y0, x1, y1, color, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for tx in range(-thick // 2, thick // 2 + 1):
            for ty in range(-thick // 2, thick // 2 + 1):
                set_px(x0 + tx, y0 + ty, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 strings of 5 chars, '#' = on. Bit 4 is the leftmost column.
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
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
}

# Unknown characters render as a blank (never crash on a typo).
BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(text, x, y, scale, color, center=False):
    """Draw text with its top-left corner at (x, y); if center, x is the centre."""
    if center:
        x -= text_width(text, scale) // 2
    cx = x
    for ch in text:
        glyph = FONT.get(ch, BLANK)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(cx + col * scale, y + row * scale,
                              cx + (col + 1) * scale, y + (row + 1) * scale,
                              color)
        cx += 6 * scale
    return cx


def draw_text_outline(text, x, y, scale, color, outline, center=False):
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2), (-2, 2), (2, 2)):
        draw_text(text, x + dx, y + dy, scale, outline, center=center)
    draw_text(text, x, y, scale, color, center=center)


# ------------------------------------------------------------- PNG encoder
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(width, height, rgb):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: none
        raw += rgb[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


def draw_scene():
    # ---- bands ------------------------------------------------------------
    fill_rect(0, 0, W, 200, NAVY)          # top headline band
    fill_rect(0, 200, W, 800, NAVY2)      # office wall
    fill_rect(0, 690, W, 800, FLOOR)      # floor
    fill_rect(0, 800, W, H, NAVY)         # bottom punchline band

    # ---- headline ---------------------------------------------------------
    draw_text_outline("I CUT OUR BIGGEST", W // 2, 26, 8, YELLOW, BLACK, center=True)
    draw_text_outline("EXPENSE", W // 2, 104, 8, YELLOW, BLACK, center=True)

    # ---- red CUT stamp, top right of the wall -----------------------------
    # Red disc with a navy centre leaves a clean 10px red ring.
    fill_circle(880, 272, 58, RED)
    fill_circle(880, 272, 48, NAVY2)
    draw_text("CUT!", 880, 256, 4, RED, center=True)

    # ---- shocked human, seated left ---------------------------------------
    fill_circle(170, 520, 55, SKIN)                       # head
    fill_rect(115, 455, 225, 490, BLACK)                  # hair
    fill_circle(150, 515, 11, WHITE)                      # wide eyes
    fill_circle(190, 515, 11, WHITE)
    fill_circle(150, 517, 5, BLACK)
    fill_circle(190, 517, 5, BLACK)
    fill_circle(170, 556, 13, BLACK)                      # open mouth
    fill_rect(95, 580, 245, 700, SHIRT)                   # shoulders
    fill_rect(160, 580, 180, 640, WHITE)                  # shirt front

    # ---- robot agent, centre ----------------------------------------------
    line(430, 300, 430, 258, STEEL_D, thick=6)            # antenna
    fill_circle(430, 248, 13, RED)                        # antenna light
    fill_rect(315, 370, 330, 400, STEEL_D)                # ears
    fill_rect(530, 370, 545, 400, STEEL_D)
    fill_rect(330, 300, 530, 470, STEEL)                  # head
    fill_rect(352, 322, 508, 448, ROBOT_FACE)             # face screen
    fill_rect(375, 350, 415, 392, EYE)                    # glowing eyes
    fill_rect(445, 350, 485, 392, EYE)
    fill_rect(382, 356, 394, 368, WHITE)                  # eye glints
    fill_rect(452, 356, 464, 368, WHITE)
    line(390, 418, 430, 434, MOUTH, thick=6)              # smug smile
    line(430, 434, 470, 418, MOUTH, thick=6)
    fill_rect(410, 470, 450, 492, STEEL_D)                # neck
    fill_rect(340, 492, 520, 645, STEEL_D)                # body
    fill_rect(370, 512, 490, 600, NAVY)                   # chest panel
    line(392, 556, 415, 580, GREEN, thick=8)              # green check
    line(415, 580, 468, 528, GREEN, thick=8)
    line(520, 530, 640, 560, STEEL, thick=16)             # arm to laptop
    fill_circle(645, 562, 18, STEEL)                      # hand

    # ---- desk --------------------------------------------------------------
    fill_rect(60, 640, 964, 700, DESK)
    fill_rect(60, 640, 964, 652, (140, 96, 52))
    fill_rect(90, 700, 120, 800, DESK)
    fill_rect(904, 700, 934, 800, DESK)

    # ---- laptop with the budget -------------------------------------------
    fill_rect(600, 620, 920, 648, DARKGREY)               # base
    fill_rect(620, 400, 900, 624, DARKGREY)               # screen frame
    fill_rect(632, 412, 888, 612, GREY)                   # screen
    draw_text("BUDGET", 640, 424, 4, BLACK)
    draw_text("COFFEE $40", 640, 478, 3, BLACK)
    draw_text("SERVERS $99", 640, 516, 3, BLACK)
    draw_text("YOUR SALARY $0", 640, 554, 3, BLACK)
    # Thin red cross-out: thick enough to read as "cut", thin enough
    # that YOUR SALARY $0 stays legible underneath.
    line(636, 560, 886, 570, RED, thick=3)
    line(636, 570, 886, 560, RED, thick=3)

    # ---- punchline ---------------------------------------------------------
    draw_text_outline("IT WAS YOU.", W // 2, 838, 10, YELLOW, BLACK, center=True)
    draw_text("Q4 SAVINGS: 100% - YOUR AI AGENT", W // 2, 952, 4, WHITE, center=True)


def read_png_size(data):
    """Read width/height back from PNG bytes (own header parser)."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    if data[12:16] != b"IHDR":
        raise ValueError("missing IHDR")
    w, h = struct.unpack(">II", data[16:24])
    return w, h


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    draw_scene()
    data = encode_png(W, H, px)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)

    # ---- gate validation + read-back verification -------------------------
    if len(data) > 1048576:
        print("FAIL: entry.png too large: %d bytes" % len(data), file=sys.stderr)
        sys.exit(1)
    with open(path, "rb") as f:
        back = f.read()
    if back != data:
        print("FAIL: read-back bytes differ", file=sys.stderr)
        sys.exit(1)
    w, h = read_png_size(back)
    if (w, h) != (W, H):
        print("FAIL: dimensions %dx%d" % (w, h), file=sys.stderr)
        sys.exit(1)
    print("OK: %s %dx%d %d bytes" % (path, w, h, len(data)))


if __name__ == "__main__":
    main()
