#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「从零基础到前端架构师」专栏的主图 / 首图。

用法:
    python3 tools/gen_cover.py --title "div 和 span 有什么区别？" --out path/to/主图.png
    python3 tools/gen_cover.py --title "HTML 与 CSS 地基" --out path/to/首图.png --column 01

规格:
    1920x1080 PNG，底色 #FAF6F0 -> #F3EBE1 极轻纵向渐变
    文字 #2B2B2B，强调色 #E86A17（技术名/核心词用橙色）
    标题水平垂直居中，双行，字号自适应
"""

import argparse
import html
import os
import re

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG_TOP = (250, 246, 240)
BG_BOTTOM = (243, 235, 225)
TEXT = (43, 43, 43)
ACCENT = (232, 106, 23)
GRAY = (122, 113, 104)

# 中文字体候选。macOS 新版本已不再提供 PingFang.ttc，逐个探测可用项。
FONT_CANDIDATES = [
    ("/System/Library/Fonts/PingFang.ttc", 5),
    ("/System/Library/Fonts/PingFang.ttc", 4),
    ("/System/Library/Fonts/STHeiti Medium.ttc", 1),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2),
]


def pick_font(size: int):
    """返回 (regular_font, medium_font)。找不到中文字体就直接报错。"""
    for path, index in FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            f = ImageFont.truetype(path, size, index=index)
        except Exception:
            continue
        return f
    raise SystemExit("找不到可用的中文字体，检查 FONT_CANDIDATES")


def make_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG_TOP)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(
            int(round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t)) for i in range(3)
        )
        d.line([(0, y), (W, y)], fill=c)
    return img


def text_width(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]


def split_lines(draw, text, font, max_width):
    """把标题折成两行。

    中文标题优先在标点后断行（「？」「，」「、」等），其次才按字宽硬断。
    英文单词不拆开。
    """
    if text_width(draw, text, font) <= max_width:
        return [text]

    # 枚举所有可断点，取能让两行都放得下的、且第一行尽量短的方案
    break_points = []
    for i, ch in enumerate(text):
        if ch in "，。？、：；！？,.:;?!" and i > 0:
            break_points.append(i + 1)  # 标点之后断

    candidates = []
    for bp in break_points:
        a, b = text[:bp].strip(), text[bp:].strip()
        if not a or not b:
            continue
        wa, wb = text_width(draw, a, font), text_width(draw, b, font)
        candidates.append((wa, wb, [a, b]))

    # 优先选两行都放得下的；都没有放得下时，选「超宽最少」的
    fitting = [c for c in candidates if c[0] <= max_width and c[1] <= max_width]
    if fitting:
        best = min(fitting, key=lambda c: abs(c[0] - c[1]))
        return best[2]
    if candidates:
        best = min(candidates, key=lambda c: max(c[0], c[1]))
        return best[2]

    # 没有合适的标点断点，按 token 硬断（英文单词不拆）
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-_]*|\s+|.", text)
    lines, cur = [], ""
    for tk in tokens:
        if tk == " " and not cur:
            continue
        trial = cur + tk
        if text_width(draw, trial, font) > max_width and cur:
            lines.append(cur.rstrip())
            cur = tk.lstrip() if tk == " " else tk
        else:
            cur = trial
    if cur.strip():
        lines.append(cur.rstrip())
    return lines


def accent_terms(text):
    """技术名用橙色：HTML/CSS 标签、属性名、英文单词。"""
    return set(re.findall(r"`?[A-Za-z][A-Za-z0-9\-_]*`?", text))


def draw_centered_text(draw, text, font, y, fill, accent_words=None, letter_spacing=0):
    """水平居中绘制，逐词着色以支持强调色。"""
    if not accent_words:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        x = (W - w) / 2
        draw.text((x, y), text, font=font, fill=fill)
        return

    # 拆成 token，逐个量宽累加
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-_]*|\s+|.", text)
    widths = []
    for tk in tokens:
        widths.append(text_width(draw, tk, font) + letter_spacing)
    total = sum(widths)
    x = (W - total) / 2

    for tk, w in zip(tokens, widths):
        bare = tk.strip("`")
        color = ACCENT if bare in accent_words and bare else fill
        draw.text((x, y), tk, font=font, fill=color)
        x += w


def build(title, out_path, column=None, max_width=1380):
    # 标题里的 HTML 实体要显示成真实符号，&lt; 显示成 <
    title = html.unescape(title)
    img = make_bg()
    draw = ImageDraw.Draw(img)

    size = 142
    while size > 60:
        font = pick_font(size)
        lines = split_lines(draw, title, font, max_width)
        if len(lines) <= 2:
            break
        size -= 6

    font = pick_font(size)
    line_h = int(size * 1.28)
    words = accent_terms(title)

    # 先画到透明图层，再按实际墨迹边界居中，避免字体上留白导致的偏移
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    y = 0
    for line in lines:
        draw_centered_text(ld, line, font, y, TEXT, words)
        y += line_h

    bbox = layer.getbbox()
    if bbox is None:
        raise SystemExit("标题为空")
    cropped = layer.crop(bbox)
    img.paste(cropped, ((W - cropped.width) // 2, (H - cropped.height) // 2), cropped)

    if column:
        small = pick_font(34)
        label = f"— 从零基础到前端架构师 · 专栏 {column} —"
        bbox2 = draw.textbbox((0, 0), label, font=small)
        draw.text(((W - (bbox2[2] - bbox2[0])) / 2, 92), label, font=small, fill=GRAY)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img.save(out_path, "PNG")
    print(f"已生成 {out_path}  ({size}px, {len(lines)} 行)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--column", default=None)
    args = ap.parse_args()
    build(args.title, args.out, args.column)
