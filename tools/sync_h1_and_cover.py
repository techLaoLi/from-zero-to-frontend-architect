#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把已写文章的正文 H1 换成 README 里登记的发布标题，并重出主图。

只动 H1 和主图，不动正文内容。正文内容重排要逐篇人工做。
"""

import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "S0-语言与浏览器基础", "01-HTML与CSS地基")
README = os.path.join(BASE, "README.md")
GEN = os.path.join(ROOT, "tools", "gen_cover.py")


def main():
    with io.open(README, encoding="utf-8") as f:
        readme = f.read()

    # 抓 已完成条目 -> 发布标题
    pairs = []
    cur = None
    for line in readme.split("\n"):
        m = re.match(r"^- \[x\] (.+)$", line)
        if m:
            cur = m.group(1).strip()
            continue
        m2 = re.match(r"^  - 发布标题：(.+)$", line)
        if m2 and cur:
            pairs.append((cur, m2.group(1).strip()))
            cur = None

    dirs = sorted(
        d for d in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, d)) and re.match(r"^\d{3}-", d)
    )

    for d in dirs:
        name = re.sub(r"^\d{3}-", "", d)
        title = dict(pairs).get(name)
        if not title:
            print(f"跳过 {d}（README 里没登记发布标题）")
            continue

        # 改 H1
        p = os.path.join(BASE, d, "正文.md")
        with io.open(p, encoding="utf-8") as f:
            text = f.read()
        new_text, n = re.subn(r"^# .*$", "# " + title, text, count=1, flags=re.M)
        if n == 0:
            print(f"跳过 {d}（没找到 H1）")
            continue
        with io.open(p, "w", encoding="utf-8") as f:
            f.write(new_text)

        # 重出主图
        out = os.path.join(BASE, d, "主图.png")
        r = subprocess.run(
            [sys.executable, GEN, "--title", title, "--out", out],
            capture_output=True, text=True,
        )
        print(f"{d}\n    H1 + 主图 -> {title}")
        if r.returncode != 0:
            print("    主图失败:", r.stderr.strip())


if __name__ == "__main__":
    main()
