#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校验专栏 01 已写文章是否达标。

检查项：
1. 正文 H1 == README 登记的发布标题
2. 正文小标题 == README 大纲条目（逐条对应，顺序一致）
3. GEO：开头有加粗定义句 / 无模板节标题 / 无空表头 / 有结论节 / 无「后面会讲」
4. 每个代码块前后各有一句交代（找最近的非空行）
5. 主图存在

用法：python3 tools/check_articles.py
"""

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "S0-语言与浏览器基础", "01-HTML与CSS地基")

TEMPLATE = {"简单示例", "标签介绍（概念和特征）", "要点总结"}


def parse_readme():
    """返回 {条目名: [发布标题, 大纲条目...]}"""
    path = os.path.join(BASE, "README.md")
    entries, cur = {}, None
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = re.match(r"^- \[[ x]\] (.+)$", line)
            if m:
                cur = m.group(1).strip()
                entries[cur] = []
                continue
            if cur and line.startswith("  - "):
                item = line[4:].strip()
                if item.startswith("发布标题："):
                    entries[cur].insert(0, item.replace("发布标题：", ""))
                else:
                    entries[cur].append(item)
            elif not line.strip() or not line.startswith("  - "):
                cur = None
    return entries


def norm(s):
    return re.sub(r"[\s、，,]", "", s)


def nearest(lines, idx, step):
    """从 idx 往 step 方向找最近的非空行"""
    j = idx + step
    while 0 <= j < len(lines) and not lines[j].strip():
        j += step
    return lines[j].strip() if 0 <= j < len(lines) else ""


def main():
    entries = parse_readme()
    norm_entries = {norm(k): (k, v) for k, v in entries.items()}

    dirs = [
        d for d in sorted(os.listdir(BASE))
        if os.path.isdir(os.path.join(BASE, d)) and re.match(r"^\d{3}-", d)
    ]

    problems, checked = [], 0
    for d in dirs:
        p = os.path.join(BASE, d)
        body_path = os.path.join(p, "正文.md")
        if not os.path.exists(body_path):
            continue

        name = re.sub(r"^\d{3}-", "", d)
        key = None
        for nk, (orig, val) in norm_entries.items():
            if nk in norm(name) or norm(name) in nk:
                if key is None or len(orig) > len(key[0]):
                    key = (orig, val)
        if not key:
            print(f"? {name}  README 里找不到对应条目")
            continue

        checked += 1
        with io.open(body_path, encoding="utf-8") as f:
            lines = f.read().split("\n")

        h1 = lines[0].lstrip("# ").strip()
        secs = [l[3:].strip() for l in lines if l.startswith("## ")]
        exp_title, exp_secs = key[1][0], key[1][1:]

        errs = []
        if h1 != exp_title:
            errs.append("H1 ≠ 发布标题")
        if secs != exp_secs:
            errs.append(f"小标题 ≠ 大纲\n      正文 {secs}\n      大纲 {exp_secs}")

        lead_end = next((k for k, l in enumerate(lines) if l.startswith("## ")), 0)
        if not "\n".join(lines[1:lead_end]).strip().startswith("**"):
            errs.append("缺加粗定义句")
        if [l for l in lines if l[3:].strip() in TEMPLATE]:
            errs.append("有模板节标题")
        if [l for l in lines if re.match(r"^\|\s*\|", l)]:
            errs.append("有空表头")
        if not any(l.startswith("## 要点总结") for l in lines):
            errs.append("缺结论节")
        if [l for l in lines if "后面会讲" in l]:
            errs.append("有后置引用")

        blocks = [k for k, l in enumerate(lines) if l.startswith("```")]
        for bi in range(0, len(blocks), 2):
            s, e = blocks[bi], blocks[bi + 1]
            if not nearest(lines, s, -1):
                errs.append(f"代码块 {bi // 2 + 1} 前无交代")
            if not nearest(lines, e, 1):
                errs.append(f"代码块 {bi // 2 + 1} 后无交代")

        if not os.path.exists(os.path.join(p, "主图.png")):
            errs.append("缺主图")

        if errs:
            problems.append((d, errs))
        print(f"{'✓' if not errs else '✗'} {name[:36]:<38} {len(secs)} 节")

    print(f"\n检查 {checked} 篇")
    if problems:
        print("\n有问题：")
        for d, errs in problems:
            print(f"  {d}")
            for e in errs:
                print(f"    - {e}")
        return 1
    print("全部通过 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
