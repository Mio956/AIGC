# -*- coding: utf-8 -*-
"""任务3：生成页面低保真线框图（矩形/文字/色块），输出总览 + 各视图 PNG。"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\20986\WorkBuddy\2026-11-18-14-23-14"
REG = "C:/Windows/Fonts/msyh.ttc"
BLD = "C:/Windows/Fonts/msyhbd.ttc"

INK = "#1F2937"
MUTED = "#6B7280"
HINT = "#9AA3AF"
LINE = "#B7BDC7"
SOFT = "#C9CFD8"
PANEL = "#F3F5F8"
FIELD = "#FAFBFC"
BLUE = "#3B6FED"
ORANGE = "#D97706"
WHITE = "#FFFFFF"

_cache = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(BLD if bold else REG, size)
    return _cache[key]


def text(d, x, y, s, size=17, color=INK, bold=False):
    d.text((x, y), s, font=font(size, bold), fill=color)


def wrap(d, x, y, s, max_w, size=17, color=INK, bold=False, lh=None):
    f = font(size, bold)
    lh = lh or size + 9
    line, cy = "", y
    for ch in s:
        if f.getlength(line + ch) > max_w and line:
            d.text((x, cy), line, font=f, fill=color)
            cy += lh
            line = ch
        else:
            line += ch
    if line:
        d.text((x, cy), line, font=f, fill=color)
        cy += lh
    return cy


def center(d, box, s, size, color=INK, bold=False):
    f = font(size, bold)
    x0, y0, x1, y1 = box
    bb = d.textbbox((0, 0), s, font=f)
    d.text((x0 + (x1 - x0 - (bb[2] - bb[0])) / 2,
            y0 + (y1 - y0 - (bb[3] - bb[1])) / 2 - bb[1]),
           s, font=f, fill=color)


def rect(d, x, y, w, h, fill=WHITE, outline=LINE, width=2, radius=0):
    if radius:
        d.rounded_rectangle((x, y, x + w, y + h), radius=radius,
                            fill=fill, outline=outline, width=width)
    else:
        d.rectangle((x, y, x + w, y + h), fill=fill, outline=outline, width=width)


def dashed(d, x, y, w, h, color=BLUE, fill=None, width=2, dash=12, gap=8):
    if fill:
        d.rectangle((x, y, x + w, y + h), fill=fill)
    for xx in range(x, x + w, dash + gap):
        d.line((xx, y, min(xx + dash, x + w), y), fill=color, width=width)
        d.line((xx, y + h, min(xx + dash, x + w), y + h), fill=color, width=width)
    for yy in range(y, y + h, dash + gap):
        d.line((x, yy, x, min(yy + dash, y + h)), fill=color, width=width)
        d.line((x + w, yy, x + w, min(yy + dash, y + h)), fill=color, width=width)


def chip(d, x, y, label, bg, size=14):
    f = font(size, True)
    w = int(f.getlength(label)) + 24
    d.rounded_rectangle((x, y, x + w, y + 30), radius=6, fill=bg)
    center(d, (x, y, x + w, y + 30), label, size, WHITE, True)
    return w


def arrow(d, x1, y1, x2, y2, color=ORANGE, width=3):
    d.line((x1, y1, x2, y2), fill=color, width=width)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 12
    for a in (ang + 2.6, ang - 2.6):
        d.line((x2, y2, x2 + L * math.cos(a), y2 + L * math.sin(a)),
               fill=color, width=width)


def header(d, x, y, w, title, right):
    rect(d, x, y, w, 40, fill=PANEL, outline=LINE, width=1)
    text(d, x + 14, y + 8, title, 19, INK, True)
    f = font(15, False)
    rw = f.getlength(right)
    text(d, x + w - rw - 14, y + 11, right, 15, ORANGE, False)


# ---------- 视图 1 ----------
W1, H1 = 760, 600


def view1(d, ox, oy):
    rect(d, ox, oy, W1, H1, WHITE, LINE, 2)
    header(d, ox, oy, W1, "视图 1 · 首页上传视图", "上传解析完成 → 视图 2")
    rect(d, ox + 20, oy + 55, 720, 520, WHITE, SOFT, 2)
    rect(d, ox + 20, oy + 55, 720, 50, PANEL, SOFT, 1)
    text(d, ox + 40, oy + 68, "面向杭电计算机研究所的论文智能初筛助手", 19, INK, True)
    dashed(d, ox + 55, oy + 130, 650, 235, BLUE, "#F2F6FF", 2)
    center(d, (ox + 55, oy + 165, ox + 705, oy + 215),
           "拖拽 PDF 上传区 / 点击上传按钮", 23, INK, True)
    center(d, (ox + 55, oy + 220, ox + 705, oy + 255),
           "支持本地 PDF 文件", 16, MUTED)
    rect(d, ox + 290, oy + 290, 180, 44, BLUE, BLUE, 1, radius=6)
    center(d, (ox + 290, oy + 290, ox + 470, oy + 334), "上传按钮", 18, WHITE, True)
    rect(d, ox + 55, oy + 390, 650, 82, WHITE, SOFT, 2)
    text(d, ox + 72, oy + 402, "摘要文本粘贴框（备选输入方式）", 17, INK, True)
    text(d, ox + 72, oy + 435, "粘贴论文摘要文本……", 15, HINT)
    text(d, ox + 55, oy + 495,
         "提示：上传后 AI 自动提取内容、匹配研究所标签", 15, MUTED)


# ---------- 视图 2 ----------
W2, H2 = 760, 600

CARDS = [
    ("具身机器人研究所", "#2F6FED", "论文标题：xxxxxxxxxxxxx",
     "一句话摘要：xxxxxxxxxxxxxxx", "关键词：具身智能 / 感知 / 定位 / ……"),
    ("媒体智能计算研究所", "#7C4DBE", "论文标题：xxxxxxxxxxxxx",
     "一句话摘要：xxxxxxxxxxxxxxx", "关键词：跨模态 / 三维视觉 / 生成 / ……"),
    ("认知计算与智能交互研究所", "#0E8A72", "论文标题：xxxxxxxxxxxxx",
     "一句话摘要：xxxxxxxxxxxxxxx", "关键词：脑机协同 / 多模态 / 决策 / ……"),
]


def view2(d, ox, oy):
    rect(d, ox, oy, W2, H2, WHITE, LINE, 2)
    header(d, ox, oy, W2, "视图 2 · 论文卡片列表视图", "点击卡片 → 视图 3")
    rect(d, ox + 20, oy + 55, 720, 520, WHITE, SOFT, 2)
    text(d, ox + 45, oy + 72, "论文列表", 22, INK, True)
    for i, (tag, color, title, summary, kw) in enumerate(CARDS):
        y = oy + 115 + i * 138
        rect(d, ox + 45, y, 670, 122, WHITE, SOFT, 2)
        chip(d, ox + 60, y + 12, "研究所标签：" + tag, color, 14)
        text(d, ox + 60, y + 50, title, 17, INK, True)
        text(d, ox + 60, y + 76, summary, 15, MUTED)
        text(d, ox + 60, y + 99, kw, 14, HINT)
    arrow(d, ox + 715, oy + 250, ox + 738, oy + 250)
    text(d, ox + 45, oy + 540,
         "点击任意一张卡片 → 右侧滑出详情面板（含彩色研究所标签）", 16, ORANGE, True)


# ---------- 视图 3 ----------
W3, H3 = 1560, 700
FIELDS = ["论文标题", "研究目标", "核心方法", "传感器 / 数据集",
          "实验结论", "匹配研究所", "关键词"]


def view3(d, ox, oy):
    rect(d, ox, oy, W3, H3, WHITE, LINE, 2)
    header(d, ox, oy, W3, "视图 3 · 论文详情（摘要 + 问答）面板视图",
           "点关闭 → 回到视图 2 卡片列表")
    rect(d, ox + 20, oy + 55, 1520, 620, WHITE, SOFT, 2)
    rect(d, ox + 20, oy + 55, 1520, 52, PANEL, SOFT, 1)
    text(d, ox + 42, oy + 69, "论文详情面板（右侧滑出）", 20, INK, True)
    text(d, ox + 1180, oy + 72,
         "× 关闭：收起详情面板，回到卡片列表", 16, ORANGE, True)
    # 左栏
    text(d, ox + 45, oy + 122, "结构化摘要面板（左栏）", 19, INK, True)
    for i, name in enumerate(FIELDS):
        y = oy + 162 + i * 68
        rect(d, ox + 45, y, 710, 56, FIELD, SOFT, 1)
        rect(d, ox + 45, y, 180, 56, PANEL, SOFT, 1)
        center(d, (ox + 45, y, ox + 225, y + 56), name, 16, INK, True)
        text(d, ox + 240, y + 17, "……（AI 提取内容）", 15, HINT)
    # 分隔线
    for yy in range(oy + 122, oy + 650, 18):
        d.line((ox + 790, yy, ox + 790, min(yy + 10, oy + 650)),
               fill=SOFT, width=2)
    # 右栏
    text(d, ox + 820, oy + 122, "问答对话区（右栏）", 19, INK, True)
    rect(d, ox + 820, oy + 165, 460, 56, "#E8F0FE", "#B5C9F5", 1, radius=10)
    center(d, (ox + 820, oy + 165, ox + 1280, oy + 221),
           "用户提问：这篇论文用了什么传感器？", 16, INK)
    rect(d, ox + 880, oy + 240, 640, 110, PANEL, SOFT, 1, radius=10)
    text(d, ox + 900, oy + 255, "AI 回答记录（对话气泡）", 16, INK, True)
    wrap(d, ox + 900, oy + 284,
         "基于本篇论文内容回答；仅展示问答区模块位置，不预设具体回答内容。",
         600, 15, MUTED)
    rect(d, ox + 820, oy + 555, 560, 62, WHITE, SOFT, 2)
    text(d, ox + 838, oy + 574, "针对本篇论文提问", 16, HINT)
    rect(d, ox + 1395, oy + 555, 125, 62, BLUE, BLUE, 1, radius=6)
    center(d, (ox + 1395, oy + 555, ox + 1520, oy + 617),
           "发送", 18, WHITE, True)
    text(d, ox + 820, oy + 630,
         "输入框 + 发送按钮：针对本篇论文提问", 15, ORANGE)


# ---------- 备注 ----------
WN, HN = 1560, 380


def notes(d, ox, oy):
    rect(d, ox, oy, WN, HN, "#FFFCF5", "#E8C98A", 2)
    rect(d, ox, oy, WN, 44, "#FFF3D9", "#E8C98A", 1)
    text(d, ox + 16, oy + 10, "备注 · 给前端 C 的布局与交互说明（重要）",
         20, "#8A5A00", True)
    lines = [
        "1. UI 布局参考：summarizepaper，只借鉴分区结构，样式可以采用深色科研风",
        "2. 交互：默认只显示首页；上传解析完成，渲染卡片列表；卡片点击，右侧滑出详情面板",
        "3. 原型不做：分页、收藏、用户登录",
        "4. 分区对照：搜索区＝上传区 / 论文卡片＝卡片列表 / 摘要面板＝详情左栏 / 问答区＝详情右栏",
        "5. 研究所标签取值以任务 1 关键词表 R1~R9 官网全称为准：官网为「具身机器人研究所」，无「具身智能研究所」",
        "6. 流程：首页上传 → 卡片列表 → 详情面板 →（点关闭）回到卡片列表",
    ]
    y = oy + 62
    for s in lines:
        y = wrap(d, ox + 24, y, s, WN - 60, 17, INK, False, 32) + 12
    text(d, ox + 24, oy + HN - 42,
         "交付：腾讯文档在线链接 + PNG 图片｜数据来源：杭电计算机学院官网科研机构页面｜2026-11-18",
         14, MUTED)


def save(fn, w, h, painter):
    img = Image.new("RGB", (w, h), WHITE)
    painter(ImageDraw.Draw(img), 0, 0)
    p = os.path.join(OUT, fn)
    img.save(p, "PNG")
    print("[OK]", p, img.size, os.path.getsize(p), "bytes")
    return p


def main():
    W, H = 1600, 1890
    img = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(img)
    text(d, 24, 22, "论文阅读助手 - 低保真原型草图", 32, INK, True)
    text(d, 24, 64,
         "3 个视图 + 交互标注｜仅用矩形 / 文字 / 色块表达模块与点击逻辑，不做美化｜给前端 C",
         16, MUTED)
    view1(d, 20, 100)
    view2(d, 820, 100)
    view3(d, 20, 720)
    notes(d, 20, 1440)
    text(d, 24, 1845,
         "视图 1 首页上传  →  视图 2 论文卡片列表  →  视图 3 详情面板（摘要 + 问答）  →  关闭回到列表",
         17, ORANGE, True)
    p = os.path.join(OUT, "线框图_总览_论文阅读助手低保真原型草图.png")
    img.save(p, "PNG")
    print("[OK]", p, img.size, os.path.getsize(p), "bytes")
    save("视图1_首页上传.png", W1, H1, view1)
    save("视图2_论文卡片列表.png", W2, H2, view2)
    save("视图3_详情面板.png", W3, H3, view3)
    save("备注_给前端.png", WN, HN, notes)


if __name__ == "__main__":
    main()
