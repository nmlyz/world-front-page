"""World Front Page: one day of world news as a single 1024x1024 PNG.

Pure standard library. A hand-made 5x7 bitmap font and code-drawn
illustrations render a broadsheet front page for Tuesday 24 November
2026. No network, no external assets, fully deterministic.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# Each glyph is seven rows of five pixels, drafted for this project.
_G = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
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
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00010", "00100", "01000", "10000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
}

PAPER = (243, 238, 222)
INK = (24, 24, 28)
RED = (164, 32, 36)
BLUE = (30, 62, 118)
TEAL = (18, 104, 110)
GOLD = (176, 128, 28)
GREY = (96, 94, 88)
LIGHT = (226, 219, 198)
SKY = (172, 198, 220)
SEA = (44, 92, 138)
SAND = (206, 184, 138)

PX = bytearray(W * H * 3)


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PX[i] = c[0]
        PX[i + 1] = c[1]
        PX[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            put(xx, yy, c)


def frame(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(t):
            for b in range(t):
                put(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                put(xx, yy, c)


def ring(cx, cy, r, c, t=2):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d <= r ** 2:
                put(xx, yy, c)


def text_w(s, sc):
    return len(s) * 6 * sc - sc


def draw_text(x, y, s, sc, c):
    for ch in s:
        glyph = _G[ch]
        for r in range(7):
            row = glyph[r]
            for col in range(5):
                if row[col] == "1":
                    rect(x + col * sc, y + r * sc, sc, sc, c)
        x += 6 * sc
    return x


def centered(y, s, sc, c, cx=W // 2):
    draw_text(cx - text_w(s, sc) // 2, y, s, sc, c)


def para(x, y, lines, sc, c, pitch=None):
    p = pitch or (7 * sc + 4)
    for ln in lines:
        draw_text(x, y, ln, sc, c)
        y += p
    return y


def save_png(path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += PX[yy * W * 3:(yy + 1) * W * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ------------------------------------------------------- illustrations
def illo_lead(x, y, w, h):
    rect(x, y, w, h, (16, 28, 52))
    for sx, sy in ((18, 14), (70, 8), (150, 20), (250, 10), (320, 22), (96, 26)):
        put(x + sx, y + sy, (240, 240, 220))
    disc(x + w - 52, y + 26, 13, (232, 226, 190))
    rect(x, y + h - 42, w, 42, SEA)
    # city silhouette
    for bx, bw, bh in ((6, 34, 30), (46, 24, 40), (76, 40, 24), (250, 30, 36), (286, 44, 26), (336, 26, 34)):
        rect(x + bx, y + h - 42 - bh, bw, bh, (10, 16, 30))
    # tilting corvette
    hull = ((70, 88), (250, 78), (272, 96), (96, 108))
    rect(x + 92, y + 84, 158, 18, (88, 96, 108))
    for i in range(len(hull)):
        x0, y0 = hull[i]
        x1, y1 = hull[(i + 1) % len(hull)]
        line(x + x0, y + y0, x + x1, y + y1, (150, 158, 168), 3)
    rect(x + 130, y + 62, 62, 18, (120, 128, 140))
    rect(x + 168, y + 48, 8, 16, (120, 128, 140))
    line(x + 96, y + 104, x + 250, y + 96, (90, 96, 108), 2)
    # helicopter falling, drone boat, splash
    disc(x + 292, y + 52, 7, GOLD)
    line(x + 276, y + 46, x + 308, y + 46, GOLD, 2)
    line(x + 292, y + 58, x + 300, y + 74, GOLD, 2)
    rect(x + 22, y + h - 30, 34, 8, INK)
    line(x + 38, y + h - 30, x + 66, y + 86, (240, 200, 90), 1)
    for dx in (196, 208, 220, 232):
        line(x + dx, y + h - 44, x + dx - 6, y + h - 60, (220, 235, 245), 2)


def illo_tanker(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x, y + h - 16, w, 16, SEA)
    # headlands
    for i in range(26):
        rect(x, y + h - 16 - i, 30 - i, 1, (90, 110, 70))
        rect(x + w - 30 + i, y + h - 16 - i, 30 - i, 1, (90, 110, 70))
    rect(x + 52, y + h - 26, 110, 10, (150, 52, 44))
    rect(x + 66, y + h - 34, 70, 8, (210, 205, 195))
    rect(x + 128, y + h - 42, 12, 10, INK)
    for dx in (84, 96, 108):
        disc(x + dx, y + 8 + (dx % 7), 5, (250, 190, 70))
        disc(x + dx, y + 8 + (dx % 7), 2, RED)


def illo_banks(x, y, w, h):
    rect(x, y, w, h, LIGHT)
    for cx in (28, 52, 76, 100):
        rect(x + cx, y + 10, 10, h - 22, (240, 238, 228))
        frame(x + cx, y + 10, 10, h - 22, GREY, 1)
    rect(x + 14, y + 4, 122, 6, GOLD)
    rect(x + 14, y + h - 10, 122, 6, GOLD)
    ring(x + w - 34, y + h // 2, 15, BLUE, 3)
    line(x + w - 52, y + 12, x + w - 74, y + h - 10, RED, 3)
    for ax in (150, 168, 186):
        line(x + ax, y + h - 8, x + ax + 22, y + 8, TEAL, 1)


def illo_capitol(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x + 52, y + 18, 70, h - 18, (238, 236, 228))
    disc(x + 87, y + 18, 20, (238, 236, 228))
    rect(x + 84, y + 2, 6, 10, INK)
    for cx in (58, 72, 96, 110):
        rect(x + cx, y + 26, 5, h - 30, GREY)
    rect(x + 190, y + h - 20, 96, 8, RED)
    rect(x + 190, y + h - 10, 62, 8, BLUE)
    draw_text(x + 190, y + 2, "258-173", 1, INK)


def illo_aid(x, y, w, h):
    rect(x, y, w, h, SAND)
    rect(x, y + h - 6, w, 6, GREY)
    rect(x + 20, y + 8, 76, 20, (238, 236, 228))
    rect(x + 96, y + 14, 22, 14, BLUE)
    disc(x + 38, y + 30, 5, INK)
    disc(x + 84, y + 30, 5, INK)
    for bx in (30, 48, 66):
        rect(x + bx, y + 13, 12, 9, GOLD)
    line(x + 150, y + 4, x + 150, y + 32, INK, 2)
    for i in range(9):
        line(x + 150, y + 4 + i, x + 168, y + 8 + i, TEAL, 1)
    rect(x + 196, y + 18, 34, 14, (150, 145, 135))
    rect(x + 240, y + 22, 26, 10, (130, 125, 115))


def illo_khartoum(x, y, w, h):
    rect(x, y, w, h, (196, 170, 140))
    rect(x + 8, y + h - 22, 40, 22, (120, 100, 80))
    rect(x + 56, y + h - 30, 30, 30, (110, 92, 72))
    rect(x + 108, y + h - 34, 8, 34, INK)
    disc(x + 112, y + h - 36, 5, INK)
    for dx in (30, 74, 120):
        for s in range(14):
            put(x + dx + (s % 3), y + h - 36 - s, GREY)
    line(x + 180, y + 10, x + 206, y + 10, INK, 2)
    line(x + 186, y + 6, x + 200, y + 14, INK, 2)
    line(x + 186, y + 14, x + 200, y + 6, INK, 2)


def illo_march(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x, y + h - 10, w, 10, GREY)
    for cx in range(14, w - 10, 22):
        disc(x + cx, y + h - 24, 4, INK)
        rect(x + cx - 3, y + h - 20, 6, 10, BLUE if (cx // 22) % 2 else RED)
    for bx, bc in ((20, RED), (84, GOLD), (150, TEAL), (216, BLUE)):
        rect(x + bx, y + 6, 44, 12, bc)
        rect(x + bx, y + 6, 3, 26, INK)
    # colosseum hint + tower hint
    for a in range(5):
        frame(x + 258, y + 14 + a * 0, 30, 22, (170, 140, 100), 1)
    line(x + 300, y + 36, x + 308, y + 8, INK, 2)
    line(x + 316, y + 36, x + 308, y + 8, INK, 2)


def illo_seoul(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x + 60, y + 16, 120, h - 16, (238, 236, 228))
    rect(x + 52, y + 10, 136, 8, BLUE)
    for wx in (72, 96, 120, 144):
        rect(x + wx, y + 24, 12, 10, SKY)
    rect(x + 108, y + h - 16, 16, 16, INK)
    line(x + 22, y + 4, x + 22, y + 38, INK, 2)
    rect(x + 24, y + 4, 22, 12, (238, 236, 228))
    disc(x + 35, y + 10, 4, RED)
    line(x + 196, y + 4, x + 196, y + 38, INK, 2)
    rect(x + 198, y + 4, 22, 12, TEAL)


# ---------------------------------------------------------------- page
def story_box(x, y, w, h, kicker, headline, body, illo, body_sc=2):
    frame(x, y, w, h, INK, 2)
    draw_text(x + 8, y + 7, kicker, 1, RED)
    hy = y + 20
    for hl in headline:
        draw_text(x + 8, hy, hl, 2, INK)
        hy += 18
    iy = hy + 3
    illo(x + 8, iy, w - 16, 38)
    para(x + 8, iy + 44, body, body_sc, INK, pitch=7 * body_sc + 3)


def build():
    rect(0, 0, W, H, PAPER)
    frame(10, 10, W - 20, H - 20, INK, 3)
    centered(22, "THE WORLD FRONT PAGE", 6, INK)
    rect(28, 66, W - 56, 3, RED)
    centered(74, "TUESDAY 24 NOVEMBER 2026 - ONE PICTURE EDITION - NO. 24", 2, GREY)
    # numbers strip
    rect(16, 96, W - 32, 30, INK)
    centered(104, "258 SEATS - 60 BANKS - 330 VOTES - 3 SHIPS - 100+ CITIES", 2, (250, 246, 230))

    # LEAD
    lx, ly, lw, lh = 16, 134, W - 32, 252
    frame(lx, ly, lw, lh, INK, 3)
    draw_text(lx + 12, ly + 10, "LIBYA - BENGHAZI, NOV 24", 2, RED)
    draw_text(lx + 12, ly + 36, "UKRAINE SINKS RUSSIAN", 4, INK)
    draw_text(lx + 12, ly + 70, "WARSHIP IN LIBYA", 4, INK)
    illo_lead(lx + 596, ly + 34, 380, 128)
    para(lx + 12, ly + 178, [
        "A UKRAINIAN SEA DRONE SANK A RUSSIAN NAVY CORVETTE AT ITS BERTH IN BENGHAZI",
        "AND DESTROYED A HELICOPTER. ZELENSKY CLAIMED THE STRIKE. LIBYA'S EASTERN",
        "GOVERNMENT FILED A FORMAL COMPLAINT AT THE UN DEMANDING AN INVESTIGATION.",
    ], 2, INK, pitch=21)

    story_box(16, 394, 496, 196, "GULF - STRAIT OF HORMUZ, NOV 23-24",
              ["THREE MORE SHIPS HIT IN HORMUZ"],
              ["WEEKEND ATTACKS LIFT THE PACE OF",
               "SHIP STRIKES TO ITS HIGHEST SINCE",
               "FEBRUARY, DESPITE THE US NAVAL",
               "BLOCKADE OF IRANIAN PORTS. TRUMP",
               "SAYS HE MAY RESUME STRIKES ON IRAN",
               "AFTER THE NEW YEAR IF NO DEAL."],
              illo_tanker)
    story_box(512, 394, 496, 196, "EUROPE - BRUSSELS, NOV 24",
              ["EU AIMS NEW SANCTIONS AT 60", "RUSSIAN BANKS"],
              ["THE EUROPEAN COMMISSION PROPOSES",
               "CUTTING 60 BANKS FROM SWIFT, A",
               "CRACKDOWN ON CRYPTO PLATFORMS AND",
               "A PORT BAN ON 70 MORE SHADOW",
               "FLEET TANKERS."],
              illo_banks)
    story_box(16, 598, 496, 196, "AMERICA - WASHINGTON, NOV 23",
              ["DEMOCRATS TAKE 258 HOUSE SEATS"],
              ["THE LARGEST HOUSE MAJORITY SINCE",
               "1992, SEALED SUNDAY WHEN CHUCK",
               "HUBBARD BEAT VIRGINIA FOXX BY 330",
               "VOTES OUT OF 287,000 IN NORTH",
               "CAROLINA AFTER A RECOUNT.",
               "REPUBLICANS HOLD AT LEAST 173."],
              illo_capitol)
    story_box(512, 598, 496, 196, "MIDDLE EAST - GAZA CITY, NOV 22-24",
              ["AID WORKERS KILLED IN GAZA"],
              ["AN ISRAELI STRIKE HIT A CAR FULL",
               "OF PACKAGED FOOD FOR DISPLACED",
               "PEOPLE. WORLD CENTRAL KITCHEN",
               "PAPERS WERE FOUND IN THE WRECK.",
               "SIX DIED SATURDAY, SIX MORE ON",
               "SUNDAY. A UNRWA WORKER DIED MONDAY."],
              illo_aid)
    story_box(16, 802, 320, 196, "AFRICA - KHARTOUM, NOV 24",
              ["DRONES STRIKE", "KHARTOUM AGAIN"],
              ["AT LEAST FOUR PEOPLE WERE KILLED IN",
               "DRONE STRIKES ACROSS GREATER",
               "KHARTOUM AND SOUTH OF THE CAPITAL.",
               "A UN BUILDING WAS ALSO DAMAGED."],
              illo_khartoum, body_sc=1)
    story_box(344, 802, 336, 196, "EUROPE - ROME, PARIS, TIRANA",
              ["STUDENTS FLOOD", "EUROPE'S STREETS"],
              ["A STUDENT-LED WAVE SWEPT EUROPE: A",
               "NATIONWIDE STRIKE IN MORE THAN 100",
               "ITALIAN CITIES, TENS OF THOUSANDS",
               "MARCHING IN PARIS, PROTESTS FROM",
               "SPAIN TO THE UK. DEMANDS: HIGHER",
               "WAGES, LOWER RENTS, BETTER SCHOOLS,",
               "NO CONSCRIPTION."],
              illo_march, body_sc=1)
    story_box(688, 802, 320, 196, "ASIA - SEOUL, NOV 24",
              ["SEOUL NAMES NEW", "TOP DIPLOMATS"],
              ["PRESIDENT LEE JAE MYUNG NOMINATED",
               "NEW FOREIGN AND UNIFICATION",
               "MINISTERS IN A CABINET RESHUFFLE,",
               "AMID CALLS TO BETTER MANAGE THE",
               "ALLIANCE WITH WASHINGTON."],
              illo_seoul, body_sc=1)


def main():
    build()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    save_png(os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
