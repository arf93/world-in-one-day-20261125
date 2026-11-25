#!/usr/bin/env python3
"""Draw the one-picture summary of Wednesday 25 November 2026.

Reads nothing but this file: every story, label and picture is drawn here
with Pillow shapes, so the program runs with no network and writes the same
bytes on every run. Output: entry.png, 1024x1024, under 1 MiB.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 22

# ---- palette: warm paper, one navy accent, one red accent -----------------
PAPER = (255, 253, 245)
CARD = (255, 255, 255)
INK = (16, 26, 40)
NAVY = (13, 40, 70)
NAVY_SOFT = (28, 68, 110)
GOLD = (176, 132, 44)
RED = (171, 32, 32)
RED_SOFT = (251, 239, 234)
GRAY = (88, 98, 110)
LINE = (206, 198, 178)
LAND = (227, 212, 178)
LAND_EDGE = (170, 152, 116)
SEA = (243, 238, 224)
SKY_NIGHT = (14, 30, 54)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_O = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(path, text, max_w, start, floor=10):
    """Largest size at which text fits max_w, starting from start."""
    size = start
    while size > floor:
        f = font(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 1
    return font(path, floor)


def wrap(text, f, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_lines(draw, x, y, lines, f, fill, leading=None, align="left", width=None):
    """Draw lines of text; returns the y just below the last line."""
    if leading is None:
        leading = int(f.size * 1.22)
    for line in lines:
        if align == "center" and width is not None:
            draw.text((x + (width - f.getlength(line)) / 2, y), line,
                      font=f, fill=fill)
        else:
            draw.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def pill(draw, x, y, label, f, fg, bg):
    """Small rounded label; returns width used."""
    pad = 5
    w = int(f.getlength(label)) + pad * 2
    h = f.size + 6
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    draw.text((x + pad, y + 3), label, font=f, fill=fg)
    return w


def card(draw, x, y, w, h, fill=CARD, outline=LINE, radius=6):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius,
                           fill=fill, outline=outline, width=1)
    return (x, y, w, h)


def vline(draw, x, y0, y1, fill=LINE, width=1):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


def starfield(draw, box, n=26, seed=7):
    """Deterministic pseudo-random stars inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    s = seed
    for _ in range(n):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        sx = x0 + s % max(1, (x1 - x0))
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        sy = y0 + s % max(1, (y1 - y0))
        r = 1 + (s % 2)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))


# ---- picture scenes: one small drawn illustration per card ----------------
# Each painter receives (draw, box) and draws a flat, recognisable scene.
# Scenes are designed in a 350x100 reference frame (a wide strip, like the
# hero and minor picture areas) and mapped onto the box, so one painter
# works for a tall hero picture and a short minor strip alike.


class SC:
    """Maps 350x100 scene coordinates onto a picture box."""

    def __init__(self, d, box):
        self.d = d
        self.x0, self.y0, self.x1, self.y1 = box
        self.w = self.x1 - self.x0
        self.h = self.y1 - self.y0

    def x(self, fx):
        return self.x0 + fx * self.w / 350.0

    def y(self, fy):
        return self.y0 + fy * self.h / 100.0

    def pt(self, fx, fy):
        return (self.x(fx), self.y(fy))

    def rect(self, fx0, fy0, fx1, fy1, **kw):
        self.d.rectangle([self.x(fx0), self.y(fy0), self.x(fx1), self.y(fy1)],
                         **kw)

    def poly(self, pts, **kw):
        self.d.polygon([self.pt(fx, fy) for fx, fy in pts], **kw)

    def ell(self, fx0, fy0, fx1, fy1, **kw):
        self.d.ellipse([self.x(fx0), self.y(fy0), self.x(fx1), self.y(fy1)],
                       **kw)

    def line(self, pts, **kw):
        self.d.line([self.pt(fx, fy) for fx, fy in pts], **kw)

    def text(self, fx, fy, s, path, size_pct, **kw):
        size = max(6, int(size_pct * self.h / 100.0))
        self.d.text((self.x(fx), self.y(fy)), s, font=font(path, size), **kw)


def scene_rocket(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=SKY_NIGHT)
    starfield(d, box, 30, seed=11)
    # ground
    s.rect(0, 88, 350, 100, fill=(52, 58, 64))
    # rocket body, centre-left
    s.rect(160, 18, 190, 72, fill=(240, 240, 236))
    s.poly([(160, 18), (190, 18), (175, 4)], fill=(178, 34, 34))
    s.rect(160, 40, 190, 48, fill=(13, 40, 70))
    s.rect(160, 56, 190, 64, fill=(176, 132, 44))
    # fins + flame
    s.poly([(160, 72), (146, 86), (160, 80)], fill=(178, 34, 34))
    s.poly([(190, 72), (204, 86), (190, 80)], fill=(178, 34, 34))
    s.poly([(166, 72), (184, 72), (175, 90)], fill=(255, 176, 32))
    # station, top right
    s.rect(272, 20, 296, 26, fill=(176, 132, 44))
    s.rect(312, 20, 336, 26, fill=(176, 132, 44))
    s.ell(296, 14, 312, 32, fill=(220, 224, 230))


def scene_refinery(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=(24, 18, 26))
    # fire glow, centre
    for r, col in ((42, (120, 40, 20)), (28, (200, 90, 20)), (15, (255, 170, 40))):
        s.ell(175 - r, 78 - r, 175 + r, 78 + r, fill=col)
    # towers and tanks
    s.rect(28, 42, 52, 92, fill=(70, 76, 84))
    s.rect(60, 56, 86, 92, fill=(88, 94, 102))
    s.rect(264, 46, 288, 92, fill=(70, 76, 84))
    s.rect(296, 62, 322, 92, fill=(96, 102, 110))
    s.rect(92, 74, 258, 92, fill=(60, 66, 74))
    # chimneys with smoke
    for cx in (40, 276):
        s.rect(cx - 4, 22, cx + 4, 42, fill=(110, 114, 120))
        s.ell(cx - 9, 8, cx + 5, 20, fill=(150, 148, 142))
    # drone silhouette, top right
    s.ell(306, 22, 330, 28, fill=(20, 20, 20))
    s.line([(302, 18), (334, 18)], fill=(200, 200, 200), width=2)


def scene_chart_down(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=(16, 26, 40))
    for gy in (25, 50, 75):
        s.line([(4, gy), (346, gy)], fill=(44, 60, 80), width=1)
    pts = [(12, 14), (68, 20), (124, 26), (180, 38), (236, 52),
           (292, 66), (338, 82)]
    s.line(pts, fill=(235, 64, 52), width=4)
    for px, py in pts:
        s.ell(px - 3, py - 3, px + 3, py + 3, fill=(255, 120, 110))
    s.text(8, 62, "-6.2%", SANS_B, 30, fill=(255, 96, 84))


def scene_supermarket(d, box):
    s = SC(d, box)
    # dawn sky + sun
    s.rect(0, 0, 350, 34, fill=(255, 196, 120))
    s.rect(0, 34, 350, 100, fill=(246, 238, 222))
    s.ell(306, 6, 336, 30, fill=(255, 220, 130))
    # storefront
    s.rect(14, 40, 336, 92, fill=(240, 240, 238))
    s.rect(14, 40, 336, 56, fill=(13, 40, 70))
    s.text(22, 43, "SUPERMARKET", SANS_B, 13, fill=(255, 255, 255))
    s.rect(24, 62, 96, 92, fill=(160, 200, 220))
    s.rect(106, 62, 300, 92, fill=(200, 220, 230))
    # two figures (rescuers) bottom right
    for fx in (310, 328):
        s.ell(fx - 5, 66, fx + 5, 76, fill=(40, 40, 40))
        s.rect(fx - 6, 76, fx + 6, 92, fill=(13, 40, 70))


def scene_treaty(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=(232, 240, 246))
    # document
    s.rect(80, 10, 270, 92, fill=(255, 255, 255), outline=(150, 160, 170),
           width=1)
    for i in range(4):
        ly = 26 + i * 9
        s.line([(90, ly), (260, ly)], fill=(170, 178, 186), width=2)
    # two flags on the document
    s.rect(90, 62, 130, 78, fill=(0, 47, 108))
    s.rect(90, 62, 104, 78, fill=(255, 255, 255))
    s.rect(220, 62, 260, 78, fill=(0, 122, 94))
    s.poly([(220, 62), (240, 70), (220, 78)], fill=(255, 215, 0))
    # pen
    s.line([(96, 86), (254, 86)], fill=(176, 132, 44), width=3)


def scene_garment(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=(246, 238, 224))
    # factory
    s.rect(10, 30, 340, 92, fill=(196, 178, 150))
    s.rect(10, 30, 340, 42, fill=(120, 60, 50))
    for wx0 in (24, 90, 160, 230):
        s.rect(wx0, 50, wx0 + 56, 68, fill=(255, 250, 235))
    s.rect(40, 12, 58, 30, fill=(120, 60, 50))
    s.text(14, 70, "Tk 17,000", SANS_B, 24, fill=(13, 40, 70))


def scene_google(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=(238, 240, 244))
    # courthouse base + columns + pediment
    s.rect(0, 88, 350, 100, fill=(120, 126, 134))
    for cx in (44, 100, 250, 306):
        s.rect(cx - 8, 26, cx + 8, 88, fill=(255, 255, 255),
               outline=(150, 158, 166), width=1)
    s.poly([(14, 26), (336, 26), (175, 8)], fill=(13, 40, 70))
    # play button
    s.rect(140, 44, 210, 74, fill=(178, 34, 34))
    s.poly([(162, 50), (162, 68), (186, 59)], fill=(255, 255, 255))
    s.text(16, 66, "$146m", SANS_B, 26, fill=(171, 32, 32))


def scene_mine(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 26, fill=(140, 170, 200))
    s.rect(0, 26, 350, 100, fill=(96, 72, 48))
    # shaft + water + helmet
    s.rect(120, 26, 170, 96, fill=(40, 28, 18))
    s.rect(120, 26, 170, 52, fill=(70, 140, 190))
    s.line([(120, 52), (170, 52)], fill=(150, 200, 240), width=3)
    s.ell(132, 56, 158, 70, fill=(255, 196, 32))
    s.rect(130, 68, 160, 72, fill=(255, 196, 32))
    # pump + hose on the surface
    s.rect(288, 6, 322, 26, fill=(178, 34, 34))
    s.line([(305, 26), (145, 30)], fill=(60, 60, 60), width=3)
    # rain
    for rx in range(8, 342, 16):
        s.line([(rx, 4), (rx - 4, 16)], fill=(220, 230, 240), width=1)


def scene_port(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 44, fill=(255, 196, 110))
    s.rect(0, 44, 350, 100, fill=(52, 90, 130))
    # cranes
    for cx in (60, 150):
        s.line([(cx, 14), (cx, 44)], fill=(40, 40, 40), width=3)
        s.line([(cx, 14), (cx + 34, 24)], fill=(40, 40, 40), width=2)
    # ship + containers
    s.rect(30, 56, 320, 76, fill=(30, 34, 40))
    s.rect(44, 46, 96, 56, fill=(200, 60, 50))
    s.rect(104, 48, 150, 56, fill=(220, 220, 220))
    # jet, top right
    s.poly([(300, 18), (326, 14), (332, 18), (326, 22)], fill=(40, 40, 44))


def scene_diplomat(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=(236, 238, 242))
    # North Korea flag: red band, white stripe, blue band, star
    s.rect(80, 8, 270, 22, fill=(178, 34, 34))
    s.rect(80, 22, 270, 25, fill=(255, 255, 255))
    s.rect(80, 25, 270, 30, fill=(0, 47, 108))
    s.ell(170, 11, 180, 21, fill=(255, 255, 255))
    # building + windows
    s.rect(50, 34, 300, 92, fill=(180, 186, 194))
    for wy in (44, 58, 72):
        for wx in (62, 100, 138, 176, 214, 252):
            s.rect(wx, wy, wx + 24, wy + 9, fill=(60, 80, 110))
    s.text(14, 74, "48 HOURS", SANS_B, 22, fill=(171, 32, 32))


def scene_bitcoin(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=(16, 26, 40))
    # $60,000 line + falling price
    s.line([(6, 44), (344, 44)], fill=(120, 130, 145), width=1)
    s.text(8, 30, "$60,000", SANS, 12, fill=(180, 188, 198))
    pts = [(12, 16), (80, 24), (150, 30), (220, 48), (290, 62), (330, 72)]
    s.line(pts, fill=(235, 64, 52), width=3)
    # coin, bottom right
    s.ell(296, 56, 334, 94, fill=(247, 147, 26))
    s.text(306, 62, "B", SANS_B, 26, fill=(255, 255, 255))


def scene_crown(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=(46, 24, 64))
    # stage light beams
    for lx in (40, 110, 240, 310):
        s.poly([(lx - 5, 4), (lx + 5, 4), (lx + 14, 34), (lx - 14, 34)],
               fill=(255, 220, 120))
    # crown, centre
    s.poly([(140, 88), (140, 42), (158, 58), (175, 34), (192, 58),
            (210, 42), (210, 88)], fill=(255, 205, 60))
    s.rect(140, 82, 210, 88, fill=(200, 150, 30))
    for px, py in ((140, 40), (175, 32), (210, 40)):
        s.ell(px - 4, py - 4, px + 4, py + 4, fill=(255, 240, 180))


def scene_phone(d, box):
    s = SC(d, box)
    s.rect(0, 0, 350, 100, fill=(232, 236, 242))
    # phone, centre
    s.rect(140, 8, 210, 94, fill=(20, 24, 30))
    s.rect(146, 14, 204, 88, fill=(255, 255, 255))
    # chat bubbles
    s.rect(152, 22, 190, 38, fill=(200, 225, 250))
    s.rect(166, 44, 198, 60, fill=(13, 40, 70))
    s.rect(152, 66, 186, 80, fill=(200, 225, 250))
    # warning triangle, bottom right
    s.poly([(296, 66), (282, 90), (310, 90)], fill=(255, 176, 32))
    s.text(293, 72, "!", SANS_B, 16, fill=(20, 20, 20))


# ---- world map: hand-drawn simplified continents (lon, lat) ---------------
# Rough outlines I drew from the shape of each continent; equirectangular
# projection. Stylised on purpose: the map must read as a world map with
# numbered pins, not as a survey chart.

CONTINENTS = {
    "north_america": [
        (-168, 66), (-158, 58), (-148, 60), (-135, 58), (-128, 50),
        (-124, 42), (-120, 34), (-114, 29), (-108, 24), (-102, 20),
        (-96, 16), (-90, 14), (-84, 11), (-79, 9), (-81, 13), (-86, 16),
        (-88, 21), (-91, 19), (-97, 26), (-93, 30), (-86, 30), (-81, 25),
        (-80, 32), (-75, 36), (-72, 41), (-68, 44), (-63, 45), (-58, 47),
        (-60, 52), (-65, 58), (-70, 60), (-78, 62), (-86, 66), (-94, 68),
        (-104, 68), (-116, 69), (-128, 70), (-142, 70), (-155, 71),
        (-165, 68), (-168, 66),
    ],
    "greenland": [
        (-56, 64), (-50, 60), (-42, 60), (-36, 64), (-28, 68), (-22, 70),
        (-24, 76), (-34, 78), (-48, 77), (-56, 74), (-58, 70), (-56, 64),
    ],
    "south_america": [
        (-79, 9), (-77, 4), (-80, -3), (-80, -7), (-76, -13), (-71, -18),
        (-70, -24), (-71, -30), (-73, -38), (-73, -46), (-70, -53),
        (-66, -55), (-68, -50), (-65, -44), (-61, -38), (-57, -34),
        (-51, -30), (-46, -25), (-40, -21), (-38, -15), (-35, -8),
        (-37, -4), (-42, -2), (-49, 0), (-52, 4), (-57, 6), (-62, 9),
        (-68, 11), (-73, 11), (-77, 8), (-79, 9),
    ],
    "africa": [
        (-6, 35), (-10, 31), (-16, 26), (-17, 20), (-17, 15), (-15, 11),
        (-11, 7), (-7, 5), (0, 6), (6, 4), (9, 4), (10, 0), (12, -5),
        (13, -12), (13, -18), (15, -25), (17, -30), (19, -34), (25, -34),
        (28, -32), (32, -28), (36, -23), (40, -15), (40, -10), (43, -3),
        (48, 0), (51, 4), (51, 11), (46, 11), (42, 13), (39, 16),
        (36, 21), (34, 27), (32, 31), (27, 32), (21, 33), (15, 32),
        (10, 34), (5, 37), (0, 36), (-6, 35),
    ],
    "eurasia": [
        (-10, 36), (-9, 39), (-9, 43), (-2, 44), (-1, 47), (-4, 48),
        (0, 50), (3, 52), (7, 54), (8, 57), (11, 59), (14, 56), (18, 56),
        (21, 55), (24, 58), (21, 61), (16, 62), (10, 62), (5, 60),
        (6, 58), (10, 58), (14, 55), (18, 54), (23, 54), (28, 54),
        (30, 57), (29, 61), (32, 65), (36, 68), (42, 68), (48, 69),
        (54, 68), (60, 69), (66, 68), (72, 72), (78, 72), (84, 74),
        (90, 75), (96, 76), (102, 76), (108, 75), (114, 74), (120, 73),
        (126, 72), (132, 71), (138, 72), (144, 72), (150, 70), (156, 69),
        (160, 65), (162, 60), (158, 56), (154, 52), (150, 59), (143, 59),
        (141, 52), (140, 46), (137, 43), (132, 42), (128, 38), (126, 34),
        (122, 31), (119, 26), (114, 22), (109, 20), (107, 12), (104, 9),
        (101, 6), (98, 8), (96, 12), (93, 17), (91, 22), (88, 22),
        (86, 20), (82, 17), (80, 13), (77, 8), (75, 11), (73, 17),
        (71, 21), (68, 23), (64, 25), (60, 25), (57, 26), (54, 26),
        (51, 27), (49, 29), (52, 27), (55, 25), (58, 23), (59, 22),
        (56, 19), (54, 17), (51, 15), (47, 13), (44, 12), (42, 15),
        (40, 16), (38, 21), (36, 24), (34, 28), (32, 31), (28, 32),
        (24, 31), (20, 32), (16, 32), (12, 33), (8, 35), (4, 36),
        (0, 36), (-4, 35), (-6, 35), (-10, 36),
    ],
    "australia": [
        (114, -22), (114, -30), (116, -35), (120, -34), (124, -33),
        (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
        (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
        (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
        (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
        (114, -22),
    ],
    "uk": [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (1, 52), (1, 51),
           (-3, 50), (-5, 50)],
    "japan": [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37),
              (141, 39), (141, 42), (143, 43), (141, 45), (139, 41),
              (137, 38), (134, 35), (131, 33), (130, 31)],
    "indonesia": [(95, 5), (100, 0), (105, -6), (110, -7), (114, -8),
                  (119, -9), (120, -8), (124, -10), (128, -8), (131, -3),
                  (134, -4), (137, -2), (140, -3), (141, -1), (138, 1),
                  (132, 0), (128, 2), (124, 1), (120, 1), (116, 0),
                  (112, -2), (108, -3), (104, -2), (100, 0), (95, 5)],
    "new_zealand": [(167, -45), (170, -42), (173, -40), (175, -38),
                    (177, -38), (174, -41), (171, -43), (168, -46),
                    (167, -45)],
}


def draw_map(d, box, pins):
    """Draw the stylised world map with numbered pins inside box.

    A pin is (num, lon, lat, label, dx, dy, callout): dx/dy offset the
    label from the pin; callout (dx, dy) moves the numbered circle away
    from a crowded true spot, joined by a leader line to a dot there.
    """
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=SEA)
    # land
    for poly in CONTINENTS.values():
        pts = []
        for lon, lat in poly:
            px = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
            py = y0 + (85.0 - lat) / 145.0 * (y1 - y0)
            pts.append((px, py))
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # pins
    fnum = font(SANS_B, 9)
    flab = font(SANS_B, 9)
    for num, lon, lat, label, dx, dy, callout in pins:
        px = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
        py = y0 + (85.0 - lat) / 145.0 * (y1 - y0)
        r = 7
        if callout is not None:
            cx, cy = px + callout[0], py + callout[1]
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=NAVY)
            d.line([(px, py), (cx, cy)], fill=NAVY, width=1)
            px, py = cx, cy
        d.ellipse([px - r, py - r, px + r, py + r], fill=NAVY,
                  outline=(255, 255, 255), width=1)
        tw = fnum.getlength(str(num))
        d.text((px - tw / 2, py - 6), str(num), font=fnum,
               fill=(255, 255, 255))
        lx, ly = px + dx, py + dy
        # white halo so the label reads over land
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            d.text((lx + ox, ly + oy), label, font=flab, fill=(255, 255, 255))
        d.text((lx, ly), label, font=flab, fill=INK)


# ---- the day's stories (verified 25 Nov 2026; see STORIES-20261125.md) ------

HEROES = [
    dict(num=1, region="SPACE · CHINA", label="CONFIRMED", scene=scene_rocket,
         dateline="00:18 GMT · DOCKING 03:56 GMT",
         headline="Pakistan's first astronaut reaches China's space station",
         body="Shenzhou-24 launched 00:18 GMT, docked 03:56 GMT. Zeeshan Ali "
              "is the first Pakistani in orbit."),
    dict(num=2, region="WAR · RUSSIA", label="REPORTED", scene=scene_refinery,
         dateline="OVERNIGHT · 02:12 UTC",
         headline="Ukraine hits two refineries 800 km inside Russia",
         body="Drones struck Syzran and Kuibyshev overnight. Samara confirms "
              "one killed, power cuts."),
    dict(num=3, region="MARKETS · ASIA", label="CONFIRMED", scene=scene_chart_down,
         dateline="WEDNESDAY'S CLOSE",
         headline="Asia's chip stocks crash as AI doubts return",
         body="Kospi -6.2%, Taiex -4.8%, Nikkei -2.8%. SK Hynix -11%, "
              "Samsung -9%, SoftBank -16%."),
]

MINORS = [
    dict(num=4, region="COLOMBIA", label="CONFIRMED", scene=scene_supermarket,
         headline="All hostages freed in Cartagena siege",
         body="Dawn storm frees ~30 hostages after a ~20-hour siege.",
         source="Reuters · AFP"),
    dict(num=5, region="PACIFIC", label="OFFICIAL", scene=scene_treaty,
         headline="Solomons sign Australia treaty, shut door on China bases",
         body="Treaty signed in Canberra; no foreign base on Solomons soil.",
         source="pm.gov.au"),
    dict(num=6, region="BANGLADESH", label="CONFIRMED", scene=scene_garment,
         headline="Bangladesh garment workers win 36% pay rise",
         body="Wage board approves Tk17,000 a month after weeks of protests.",
         source="Reuters · AP"),
    dict(num=7, region="MALAYSIA", label="CONFIRMED", scene=scene_google,
         headline="Malaysia sues Google for $146m over YouTube content",
         body="MCMC seeks RM600m over harmful YouTube content, scams, fraud.",
         source="Reuters"),
    dict(num=8, region="INDONESIA", label="REPORTED", scene=scene_mine,
         headline="Dozens trapped in flooded Bogor gold mine",
         body="Rescuers search for ~30 miners 100 m down a flooded shaft.",
         source="Reuters · AP"),
    dict(num=9, region="YEMEN / SAUDI", label="REPORTED", scene=scene_port,
         headline="Houthis threaten Jeddah as Saudi jets hit Hodeidah",
         body="Coalition hits Hodeidah after Houthis threaten Jeddah's ports.",
         source="Reuters"),
    dict(num=10, region="NORTH KOREA", label="OFFICIAL", scene=scene_diplomat,
         headline="North Korea expels Swiss diplomat, shuts office",
         body="Pyongyang orders Swiss envoy out in 48 hours; office to close.",
         source="KCNA · Reuters"),
    dict(num=11, region="GLOBAL", label="CONFIRMED", scene=scene_bitcoin,
         headline="Bitcoin falls below $60,000",
         body="Bitcoin at ~$59,380; ETF outflows hit a record $4.71bn in Nov.",
         source="Finnhub · Reuters"),
    dict(num=12, region="PUERTO RICO", label="CONFIRMED", scene=scene_crown,
         headline="Miss Universe crowns its first mother",
         body="Jennifer Barreto, 27, is the first mother ever to win the crown.",
         source="CNN"),
    dict(num=13, region="AUSTRALIA", label="REPORTED", scene=scene_phone,
         headline="AI app Talkie 'engineered to hook kids'",
         body="ABC: MiniMax's Talkie was built to bond with children.",
         source="ABC"),
]

INDEX_ITEMS = [
    (14, "SEOUL — Russia defends Tu-160 flight; Seoul scrambled F-15Ks Tue"),
    (15, "GULF OF MEXICO — Six dead as Cessna crashes; no survivors found"),
    (16, "DR CONGO — Army plane missing; rebels CLAIM shoot-down, unverified"),
    (17, "KYIV — Zelenskyy warns Russia is readying new strikes on Ukraine"),
    (18, "TANGERANG — ASEAN opens disaster-prevention ministerial (14th AMMDM)"),
    (19, "TOKYO — Japan service prices +4.2%, a 36-year high"),
    (20, "CANBERRA — Australia core inflation 3.8%, headline CPI 4.9%"),
    (21, "MUMBAI — Sensex +2.35%; record FII inflows $13.2bn in November"),
    (22, "EUROPE — Man City 2-2 Napoli; Arsenal 1-1 Dortmund in UCL"),
    (23, "BOSTON — Tatum 41 as Celtics beat Wizards 131-116 in NBA Cup"),
    (24, "SHANGHAI — Party pledges loyalty after Chen graft probe"),
    (25, "NEW DELHI — Cisco CEO: AI helps hackers outpace defenders"),
    (26, "LOS ANGELES — Academy: fully AI-made film out of Oscar race"),
    (27, "LONDON — Unilever cuts Channel 4 ad spend 92%"),
    (28, "SEVILLE — Europol shuts 57 illegal IPTV services; EUR 26m traced"),
    (29, "BOLOGNA — Davis Cup: Italy face South Korea in QF today"),
    (30, "LOS ANGELES — A24 box office passes $526m, a record year"),
    (31, "ADDIS ABABA — Malaria risk spreads to African highlands"),
    (32, "WASHINGTON — US inflation data due tonight: PCE, Q3 GDP, claims"),
    (33, "DOHA — Verstappen can seal F1 second place at Qatar GP on Sunday"),
]

UTC_EVENTS = [
    ("00:18", "Shenzhou-24 launches"),
    ("02:12", "Ukraine hits 2 refineries"),
    ("03:56", "Shenzhou-24 docks"),
    ("04:16", "Pongkor rescue under way"),
    ("05:44", "Malaysia sues Google"),
    ("06:00", "Cartagena hostages freed"),
    ("08:55", "Bitcoin below $60,000"),
]

NUMBERS = [
    ("-6.2%", "Kospi, Wednesday's chip sell-off"),
    ("30", "hostages freed in Cartagena"),
    ("17,000", "taka, new Bangladesh garment wage (+36%)"),
    ("$146M", "Malaysia's claim against Google"),
    ("$59,380", "Bitcoin, below $60,000"),
    ("2", "Russian refineries hit 800 km inside Russia"),
]

DATECHECK_TITLE = "DATE CHECK · LEFT OUT AS OLDER NEWS"
DATECHECK_LINES = [
    "Huawei convicted Tue 24 Nov · Russian jets in Korea's zone Tue 24 Nov · "
    "Houthi drone hits Riyadh tower Tue 24 Nov, 11 hurt · Laos leaves UN "
    "least-developed list Tue 24 Nov",
    "Sanofi-Insmed $41bn deal Mon 24 Nov · Nvidia restores Huang Mon 23 Nov · "
    "COP31 collapsed Sun 22 Nov · Gibran resigned 12 Nov",
    "Yesterday to today: Riyadh hit Tue, Hodeidah strikes Wed · Chen probe "
    "Tue, Shanghai loyalty Wed. Not yet: Spain debate Thu 26 Nov · Tai Po "
    "anniv. Thu 26 Nov · Spain vote 29 Nov · wage 1 Dec · VP vote 11 Dec",
]

SOURCES_LINE = ("Sources: Reuters, AP, AFP, Xinhua, Yonhap, CNN, WSJ, Bloomberg, "
                "BBC, BusinessLine, pm.gov.au, ABC, IANS, ASEAN, US Coast Guard, "
                "Finnhub, CoinDesk, Guardian, IndieWire, Europol, CNBC, myKhel, "
                "Field Level Media.")

# (num, lon, lat, label, label_dx, label_dy, callout_dx, callout_dy)
# Callout: pin 10's true spot is 1.5 px from pin 3, so it is drawn as a dot
# with a leader to a numbered circle offset up-left. Bogor's plotted spot is
# nudged a few degrees so its circle clears Kuala Lumpur's.
PINS = [
    (1, 100.3, 40.9, "JIUQUAN", 10, -4, None),
    (2, 50.1, 53.2, "SAMARA", 10, -4, None),
    (3, 127.0, 37.5, "SEOUL", 10, 2, None),
    (4, -75.5, 10.4, "CARTAGENA", 10, -4, None),
    (5, 160.0, -9.6, "SOLOMONS", -62, 8, None),
    (6, 90.4, 23.8, "DHAKA", 10, -4, None),
    (7, 101.7, 3.1, "KUALA LUMPUR", 10, -4, None),
    (8, 109.5, -8.0, "BOGOR", 10, 8, None),
    (9, 42.8, 14.8, "HODEIDAH", 10, -4, None),
    (10, 125.8, 39.0, "PYONGYANG", 12, -4, (-36, -22)),
    (11, -74.0, 40.7, "NEW YORK", 10, -4, None),
    (12, -66.1, 18.5, "SAN JUAN", 10, -4, None),
    (13, 151.2, -33.9, "SYDNEY", -58, -4, None),
]

LABEL_FILL = {"CONFIRMED": NAVY, "OFFICIAL": (120, 88, 20), "REPORTED": (74, 84, 96)}


# ---- layout ----------------------------------------------------------------

def draw_masthead(d, y):
    f_kick = font(SANS_B, 13)
    kick = "T H E   W O R L D   O N   O N E   P A G E"
    text_lines(d, 0, y, [kick], f_kick, GRAY, align="center", width=W)
    y += 18
    f_date = fit_font(SERIF, "Wednesday 25 November 2026", W - 2 * MARGIN, 76)
    text_lines(d, 0, y, ["Wednesday 25 November 2026"], f_date, INK,
               leading=f_date.size + 6, align="center", width=W)
    y += f_date.size + 8
    f_count = font(SANS_B, 16)
    count = "33 STORIES  ·  7 REGIONS  ·  14 FIELDS  ·  ALL FROM THIS WEDNESDAY"
    text_lines(d, 0, y, [count], f_count, NAVY, align="center", width=W)
    y += 22
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=GOLD, width=2)
    return y + 5


def draw_utc(d, y, h):
    d.rectangle([MARGIN, y, W - MARGIN, y + h], fill=NAVY)
    d.rectangle([MARGIN, y, W - MARGIN, y + 3], fill=GOLD)
    col_w = (W - 2 * MARGIN) / len(UTC_EVENTS)
    f_time = font(SANS_B, 11)
    f_lab = font(SANS, 8)
    for i, (t, lab) in enumerate(UTC_EVENTS):
        cx = MARGIN + col_w * i
        if i:
            vline(d, int(cx), y + 7, y + h - 7, fill=(60, 90, 130))
        text_lines(d, int(cx + 6), y + 7, [t], f_time, (255, 255, 255))
        text_lines(d, int(cx + 6), y + 22, [lab], f_lab, (205, 216, 230))
    return y + h


def draw_heroes(d, y, h):
    gap = 8
    cw = (W - 2 * MARGIN - 2 * gap) // 3
    f_head = font(SERIF, 17)
    f_body = font(SANS, 11)
    f_reg = font(SANS_B, 9)
    f_lab = font(SANS_B, 8)
    f_date = font(SANS_B, 8)
    for i, hero in enumerate(HEROES):
        x = MARGIN + i * (cw + gap)
        card(d, x, y, cw, h)
        hero["scene"](d, (x + 6, y + 6, x + cw - 6, y + 94))
        ty = y + 100
        pill(d, x + 8, ty, hero["region"], f_reg, (255, 255, 255), NAVY)
        lw = pill(d, x + 8 + int(f_reg.getlength(hero["region"])) + 16, ty,
                  hero["label"], f_lab, (255, 255, 255),
                  LABEL_FILL[hero["label"]])
        d.text((x + cw - 8 - f_date.getlength(hero["dateline"]), ty + 2),
               hero["dateline"], font=f_date, fill=GRAY)
        hy = ty + 20
        lines = wrap(hero["headline"], f_head, cw - 16)
        assert len(lines) <= 2, hero["headline"]
        text_lines(d, x + 8, hy, lines, f_head, INK, leading=19)
        by = hy + len(lines) * 19 + 4
        blines = wrap(hero["body"], f_body, cw - 16)
        assert len(blines) <= 2, hero["body"]
        text_lines(d, x + 8, by, blines, f_body, (44, 54, 66), leading=13)
    return y + h


def draw_numbers(d, y, h):
    f_head = font(SANS_B, 11)
    text_lines(d, MARGIN, y, ["THE DAY IN NUMBERS"], f_head, NAVY)
    cell_w = (W - 2 * MARGIN) / len(NUMBERS)
    f_num = font(SANS_B, 24)
    f_lab = font(SANS, 8)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = MARGIN + cell_w * i
        if i:
            vline(d, int(cx), y + 14, y + h - 2, fill=LINE)
        text_lines(d, int(cx + 8), y + 15, [num], f_num,
                   RED if num.startswith("-") else NAVY)
        llines = wrap(lab, f_lab, cell_w - 16)
        assert len(llines) <= 2, lab
        text_lines(d, int(cx + 8), y + 43, llines, f_lab, GRAY, leading=10)
    return y + h


def draw_minors(d, y, h):
    gap = 8
    cw = (W - 2 * MARGIN - 4 * gap) // 5
    ch = (h - gap) // 2
    f_head = font(SERIF, 10)
    f_body = font(SANS, 9)
    f_reg = font(SANS_B, 8)
    f_src = font(SANS, 8)
    f_num = font(SANS_B, 9)
    for i, m in enumerate(MINORS):
        row, col = divmod(i, 5)
        x = MARGIN + col * (cw + gap)
        yy = y + row * (ch + gap)
        card(d, x, yy, cw, ch)
        m["scene"](d, (x + 5, yy + 4, x + cw - 5, yy + 46))
        ny = yy + 49
        d.ellipse([x + 5, ny, x + 19, ny + 14], fill=NAVY)
        nw = f_num.getlength(str(m["num"]))
        d.text((x + 12 - nw / 2, ny + 2), str(m["num"]), font=f_num,
               fill=(255, 255, 255))
        d.text((x + 23, ny + 2), m["region"], font=f_reg, fill=GRAY)
        lab_w = int(f_reg.getlength(m["label"])) + 10
        pill(d, x + cw - 5 - lab_w, ny, m["label"], f_reg,
             (255, 255, 255), LABEL_FILL[m["label"]])
        hy = ny + 17
        lines = wrap(m["headline"], f_head, cw - 10)
        assert len(lines) <= 2, m["headline"]
        text_lines(d, x + 5, hy, lines, f_head, INK, leading=11)
        by = hy + len(lines) * 11 + 2
        blines = wrap(m["body"], f_body, cw - 10)
        assert len(blines) <= 2, m["body"]
        text_lines(d, x + 5, by, blines, f_body, (44, 54, 66), leading=10)
        sy = by + len(blines) * 10 + 2
        assert sy + 8 <= yy + ch, m["headline"]
        d.text((x + 5, sy), m["source"], font=f_src, fill=GRAY)
    return y + h


def draw_map_index(d, y, h):
    f_head = font(SANS_B, 11)
    map_w = 430
    map_x = MARGIN
    idx_x = MARGIN + map_w + 12
    idx_w = W - MARGIN - idx_x
    text_lines(d, map_x, y, ["WHERE IT HAPPENED · PINS 1-13"], f_head, NAVY)
    text_lines(d, idx_x, y, ["ALSO ON WEDNESDAY 25 NOVEMBER"], f_head, NAVY)
    my = y + 16
    mh = h - 16
    draw_map(d, (map_x, my, map_x + map_w, my + mh), PINS)
    # index: two columns, ten rows each
    f_idx = font(SANS, 9)
    col_w = (idx_w - 10) // 2
    for i, (num, text) in enumerate(INDEX_ITEMS):
        col, row = divmod(i, 10)
        ix = idx_x + col * (col_w + 10)
        iy = my + row * 20
        d.text((ix, iy), str(num) + ".", font=font(SANS_B, 9), fill=NAVY)
        lines = wrap(text, f_idx, col_w - 20)
        assert len(lines) <= 2, text
        text_lines(d, ix + 20, iy, lines, f_idx, INK, leading=10)
    return y + h


def draw_datecheck(d, y, h):
    d.rounded_rectangle([MARGIN, y, W - MARGIN, y + h], radius=6,
                        fill=RED_SOFT, outline=RED, width=1)
    f_title = font(SANS_B, 11)
    f_body = font(SANS, 9)
    text_lines(d, MARGIN + 10, y + 5, [DATECHECK_TITLE], f_title, RED)
    ly = y + 20
    for line in DATECHECK_LINES:
        assert f_body.getlength(line) <= W - 2 * MARGIN - 20, line[:60]
        ly = text_lines(d, MARGIN + 10, ly, [line], f_body, INK, leading=11)
    return y + h


def draw_footer(d, y, h):
    f_leg = font(SANS_B, 10)
    f_src = font(SANS, 8)
    legend = ("CONFIRMED  2+ outlets   ·   OFFICIAL  on the record   ·   "
              "REPORTED  one outlet  —  every story happened, or was first "
              "reported, on Wednesday 25 November 2026.")
    text_lines(d, MARGIN, y, [legend], f_leg, NAVY)
    slines = wrap(SOURCES_LINE, f_src, W - 2 * MARGIN)
    assert len(slines) <= 2, SOURCES_LINE
    text_lines(d, MARGIN, y + 14, slines, f_src, GRAY, leading=10)
    return y + h


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 0
    y = draw_masthead(d, y + 8)
    y += 5
    y = draw_utc(d, y, 38)
    y += 6
    y = draw_heroes(d, y, 190)
    y += 6
    y = draw_numbers(d, y, 56)
    y += 6
    f_mh = font(SANS_B, 12)
    text_lines(d, MARGIN, y, ["TEN MORE STORIES — EVERY ONE WITH ITS PICTURE"],
               f_mh, NAVY)
    y += 17
    y = draw_minors(d, y, 248)
    y += 6
    y = draw_map_index(d, y, 224)
    y += 6
    y = draw_datecheck(d, y, 54)
    y += 6
    y = draw_footer(d, y, 36)
    assert y <= H, "overflow: final y=%d > %d" % (y, H)
    print("final y =", y, "of", H)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote", out, size, "bytes")
    assert size <= 1048576, "entry.png over 1 MiB"
    print("OK: 1024x1024, under 1 MiB")


if __name__ == "__main__":
    main()
