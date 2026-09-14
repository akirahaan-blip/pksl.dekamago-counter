# -*- coding: utf-8 -*-
"""
============================================================
 デカマゴカウンター
 X や LINE に URL を貼ったときに出る「カード画像」（ogp.png 1200x630）と、
 ホーム画面に置いたときのアイコン（icon-180 / 192 / 512.png）を作るツール

 ふだんは使いません。文字や色を変えたくなったときだけ使います。

 使いかた：
   PowerShell でこのフォルダに移動して  python make-images.py
 できるもの：
   ogp.png / icon-180.png / icon-192.png / icon-512.png が同じフォルダに保存されます

 ポケモンの公式の絵は一切使っていません。かちかちくん（数取器）の絵だけで描いています。
============================================================
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ---------- 設定：ここを書き換えれば見た目が変わります ----------
TITLE = "デカマゴカウンター"
LEAD  = "おおきなマゴのみ、拾った回数をカチカチ数える"
NOTE  = "ポケモンスリープ 非公式ファンツール"

W, H = 1200, 630
S = 2                      # 2倍の大きさで描いて最後に縮める（フチがなめらかになる）

# 色（アプリ本体と同じ系統）
BG_TOP    = (0x2B, 0x0A, 0x1E)   # 背景の上（プラム）
BG_BOTTOM = (0x4A, 0x14, 0x38)   # 背景の下
PINK      = (0xFF, 0x8E, 0xC4)   # タイトル
MUTED     = (0xE8, 0xC6, 0xD8)   # うすい文字
BODY_TOP  = (0x3A, 0x1A, 0x30)   # 本体（黒いプラスチック＋ピンクのスキン）
BODY_BOT  = (0x1A, 0x08, 0x12)
BODY_LINE = (0x0C, 0x04, 0x08)
LCD_TOP   = (0xCF, 0xDB, 0xB6)   # 液晶（黄緑）
LCD_BOT   = (0xA9, 0xB8, 0x92)
LCD_RIM   = (0x0E, 0x0F, 0x12)
LCD_SEG   = (0x1B, 0x24, 0x18)   # 点いている棒
LCD_GHOST = (0x9E, 0xAB, 0x8A)   # 消えている棒（うっすら）
LCD_INK   = (0x2A, 0x3A, 0x26)   # 液晶の文字
# ボタンの色（明るい / 本体 / 影）
BUTTONS = [
    ((0xFF, 0xA3, 0xCF), (0xE0, 0x50, 0x8F), (0x93, 0x30, 0x5C)),  # ミュウ＝ピンク
    ((0xD5, 0x9B, 0xFF), (0x8A, 0x3F, 0xD0), (0x55, 0x25, 0x8A)),  # ミュウツー＝紫
    ((0xFF, 0x7A, 0x72), (0xD9, 0x35, 0x2E), (0x8E, 0x1F, 0x1A)),  # エスパー＝赤
    ((0x7F, 0xD9, 0x8F), (0x2F, 0x9A, 0x4C), (0x1C, 0x5F, 0x2E)),  # それ以外＝緑
    ((0x7F, 0xD9, 0x8F), (0x2F, 0x9A, 0x4C), (0x1C, 0x5F, 0x2E)),  # それ以外＝緑
]
# 液晶に出す数字（見本）
TOTAL_NUM = "0042"
SLOT_NUMS = ["012", "009", "007", "008", "006"]
SLOT_LABELS = ["1 ミュウ", "2 ミュウツー", "3 エスパー", "4 それ以外", "5 それ以外"]

FONT_HEAVY = "C:/Windows/Fonts/MPLUS1p-ExtraBold.ttf"   # 800
FONT_BOLD  = "C:/Windows/Fonts/MPLUS1p-Bold.ttf"        # 700
FALLBACKS  = ["C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/meiryob.ttc"]

here = os.path.dirname(os.path.abspath(__file__))


def font(path, size):
    for p in [path] + FALLBACKS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgradient(img, box, top, bottom):
    """box の範囲をたてのグラデーションで塗る"""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        d.line([(x0, y), (x1, y)], fill=lerp(top, bottom, t))


def rounded_gradient(img, box, radius, top, bottom):
    """角丸の範囲だけをグラデーションで塗る（マスクを使う）"""
    x0, y0, x1, y1 = box
    layer = Image.new("RGB", (x1 - x0, y1 - y0))
    vgradient(layer, (0, 0, x1 - x0, y1 - y0), top, bottom)
    mask = Image.new("L", layer.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, layer.size[0] - 1, layer.size[1] - 1), radius=radius, fill=255)
    img.paste(layer, (x0, y0), mask)


# ---------- 7セグメント数字（アプリと同じ形） ----------
SEG_PTS = {
    "a": [(10, 3), (46, 3), (41, 10), (15, 10)],
    "b": [(47, 5), (53, 9), (53, 45), (49, 50), (45, 45), (45, 11)],
    "c": [(45, 55), (49, 50), (53, 55), (53, 91), (47, 95), (45, 89)],
    "d": [(15, 90), (41, 90), (46, 97), (10, 97)],
    "e": [(3, 55), (7, 50), (11, 55), (11, 89), (9, 95), (3, 91)],
    "f": [(3, 9), (9, 5), (11, 11), (11, 45), (7, 50), (3, 45)],
    "g": [(13, 47), (43, 47), (47, 50), (43, 53), (13, 53), (9, 50)],
}
DIGIT_SEGS = ["abcdef", "bc", "abged", "abgcd", "fgbc", "afgcd", "afgedc", "abc", "abcdefg", "abcdfg"]


def draw_digit(d, x, y, h, ch):
    """左上 (x,y)、高さ h で数字 ch を描く。少し右に傾けて液晶っぽく"""
    k = h / 100.0
    on = DIGIT_SEGS[int(ch)]
    for name, pts in SEG_PTS.items():
        poly = []
        for (px, py) in pts:
            skew = (100 - py) * 0.10  # 上ほど右へ（斜め）
            poly.append((x + (px + skew + 5) * k, y + py * k))
        d.polygon(poly, fill=LCD_SEG if name in on else LCD_GHOST)


def draw_number(d, x, y, h, text, gap=0.12):
    w = h * 0.66
    for i, ch in enumerate(text):
        draw_digit(d, x + i * (w + h * gap), y, h, ch)
    return len(text) * (w + h * gap)


def draw_button(d, cx, cy, r, colors):
    hi, body, shadow = colors
    d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=(0x15, 0x08, 0x0F))   # 台座
    d.ellipse((cx - r, cy - r + r * 0.18, cx + r, cy + r + r * 0.18), fill=shadow)         # 下の影
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=body)
    d.ellipse((cx - r * 0.62, cy - r * 0.72, cx + r * 0.05, cy - r * 0.08), fill=hi)       # ハイライト
    d.ellipse((cx - r * 0.45, cy - r * 0.62, cx - r * 0.12, cy - r * 0.32), fill=(255, 255, 255))


def draw_device(img, box):
    """かちかちくん本体を box の範囲に描く"""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    rad = int(h * 0.09)
    d.rounded_rectangle((x0 - 6, y0 - 6, x1 + 6, y1 + 6), radius=rad + 6, fill=BODY_LINE)
    rounded_gradient(img, box, rad, BODY_TOP, BODY_BOT)

    # 液晶
    pad = int(w * 0.03)
    lx0, ly0, lx1, ly1 = x0 + pad, y0 + int(h * 0.14), x1 - pad, y0 + int(h * 0.52)
    d.rounded_rectangle((lx0 - 8, ly0 - 8, lx1 + 8, ly1 + 8), radius=18, fill=LCD_RIM)
    rounded_gradient(img, (lx0, ly0, lx1, ly1), 12, LCD_TOP, LCD_BOT)
    # 銘板の文字
    f_logo = font(FONT_HEAVY, int(h * 0.075))
    d.text((lx0, y0 + int(h * 0.035)), "おおきなマゴのみ", font=f_logo, fill=PINK)

    # 液晶の中身：左に TOTAL（大）、右に5列（小）
    f_lbl = font(FONT_BOLD, int(h * 0.05))
    inner_h = ly1 - ly0
    total_h = int(inner_h * 0.56)
    tx = lx0 + int(w * 0.025)
    ty = ly0 + int(inner_h * 0.34)
    d.text((tx + total_h * 0.9, ly0 + int(inner_h * 0.08)), "TOTAL", font=f_lbl, fill=LCD_INK)
    tw = draw_number(d, tx, ty, total_h, TOTAL_NUM)
    sep_x = tx + tw + int(w * 0.02)
    d.line([(sep_x, ly0 + 14), (sep_x, ly1 - 14)], fill=(0x6A, 0x78, 0x5E), width=4)

    col_w = (lx1 - sep_x - int(w * 0.02)) / 5.0
    slot_h = int(min(inner_h * 0.44, col_w / 2.7))   # 3桁が列の幅に収まる大きさ
    for i in range(5):
        cx = sep_x + int(w * 0.02) + col_w * i
        lbl = SLOT_LABELS[i]
        lw = d.textlength(lbl, font=f_lbl)
        num_w = 3 * (slot_h * 0.66 + slot_h * 0.12)
        d.text((cx + (col_w - lw) / 2, ly0 + int(inner_h * 0.10)), lbl, font=f_lbl, fill=LCD_INK)
        draw_number(d, cx + (col_w - num_w) / 2, ly0 + int(inner_h * 0.42), slot_h, SLOT_NUMS[i])

    # ボタン5つ
    r = int(h * 0.13)
    by = y0 + int(h * 0.77)
    for i in range(5):
        cx = x0 + int(w * (0.12 + 0.19 * i))
        draw_button(d, cx, by, r, BUTTONS[i])


def make_ogp():
    img = Image.new("RGB", (W * S, H * S))
    vgradient(img, (0, 0, W * S, H * S), BG_TOP, BG_BOTTOM)
    d = ImageDraw.Draw(img)

    # 文字
    f_title = font(FONT_HEAVY, 88 * S)
    f_lead = font(FONT_BOLD, 34 * S)
    f_note = font(FONT_BOLD, 22 * S)
    d.text((70 * S, 44 * S), TITLE, font=f_title, fill=PINK)
    d.text((74 * S, 156 * S), LEAD, font=f_lead, fill=MUTED)
    nw = d.textlength(NOTE, font=f_note)
    d.text((W * S - nw - 70 * S, H * S - 50 * S), NOTE, font=f_note, fill=MUTED)

    # 本体
    draw_device(img, (70 * S, 218 * S, (W - 70) * S, (H - 66) * S))

    out = img.resize((W, H), Image.LANCZOS)
    out.save(os.path.join(here, "ogp.png"), optimize=True)
    print("ogp.png を保存しました")


def make_icon(size):
    base = 512 * S
    img = Image.new("RGB", (base, base))
    vgradient(img, (0, 0, base, base), BG_TOP, BG_BOTTOM)
    d = ImageDraw.Draw(img)
    # 液晶（上）
    m = int(base * 0.10)
    ly0, ly1 = int(base * 0.14), int(base * 0.46)
    d.rounded_rectangle((m - 10, ly0 - 10, base - m + 10, ly1 + 10), radius=40, fill=LCD_RIM)
    rounded_gradient(img, (m, ly0, base - m, ly1), 28, LCD_TOP, LCD_BOT)
    hh = int((ly1 - ly0) * 0.68)
    nw = 3 * (hh * 0.66 + hh * 0.12)
    draw_number(d, (base - nw) / 2, ly0 + int((ly1 - ly0) * 0.16), hh, "042")
    # ボタン（下）＝ミュウのピンク
    draw_button(d, base // 2, int(base * 0.72), int(base * 0.17), BUTTONS[0])
    out = img.resize((size, size), Image.LANCZOS)
    out.save(os.path.join(here, "icon-%d.png" % size), optimize=True)
    print("icon-%d.png を保存しました" % size)


if __name__ == "__main__":
    make_ogp()
    for s in (180, 192, 512):
        make_icon(s)
