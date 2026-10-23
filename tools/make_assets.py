#!/usr/bin/env python3
"""Draw the profile banner, the research-line cards and the SPOT-DETR GIF.

    python3 tools/make_assets.py --fonts DIR [--cache DIR --images DIR]

--fonts holds NanumGothic-Regular.ttf and NanumGothic-Bold.ttf. The GIF is
drawn only when --cache (the qual_cache_v2test folder of the SPOT-DETR
experiments) and --images (AI-TOD-v2 test images) are given.
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'

THEMES = {
    'light': dict(bg='#ffffff', ink='#1f2328', ink2='#59636e', muted='#8c959f', grid='#d8dee4',
                  card='#f6f8fa', edge='#d1d9e0', accent='#2a78d6', atom='#eb6834', box='#6250d6'),
    'dark': dict(bg='#0d1117', ink='#f0f6fc', ink2='#9198a1', muted='#6e7681', grid='#30363d',
                 card='#151b23', edge='#3d444d', accent='#3987e5', atom='#d95926', box='#9085e9'),
}


def use_fonts(font_dir):
    for name in ('NanumGothic-Regular.ttf', 'NanumGothic-Bold.ttf'):
        font_manager.fontManager.addfont(str(Path(font_dir) / name))
    plt.rcParams['font.family'] = 'NanumGothic'


def banner(theme):
    t = THEMES[theme]
    fig = plt.figure(figsize=(8, 1.8), dpi=200)
    fig.patch.set_facecolor(t['bg'])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 180)
    ax.axis('off')

    # Right side: a stride grid, anchors at cell centers, off-grid atoms on two rows of cars.
    x0, y0, cell, cols, rows = 452, 22, 34, 10, 4
    for i in range(cols + 1):
        ax.plot([x0 + i * cell] * 2, [y0, y0 + rows * cell], color=t['grid'], lw=0.6)
    for j in range(rows + 1):
        ax.plot([x0, x0 + cols * cell], [y0 + j * cell] * 2, color=t['grid'], lw=0.6)
    for i in range(cols):
        for j in range(rows):
            ax.plot(x0 + (i + .5) * cell, y0 + (j + .5) * cell, 'o', ms=1.6, color=t['muted'], alpha=.7)
    rng = np.random.default_rng(7)
    for row_y, start, n in ((y0 + 1.15 * cell, x0 + 0.45 * cell, 7), (y0 + 2.75 * cell, x0 + 2.3 * cell, 6)):
        for k in range(n):
            cx = start + k * 0.93 * cell + rng.normal(0, 2)
            cy = row_y + rng.normal(0, 2.5)
            ax.add_patch(FancyBboxPatch((cx - 11, cy - 7), 22, 14, boxstyle='round,pad=0,rounding_size=2',
                                        fill=False, lw=0.9, ec=t['box']))
            ax.plot(cx, cy, 'o', ms=4.2, color=t['atom'], mec=t['bg'], mew=0.6)

    name = ax.text(40, 112, 'Ki-won Eom', fontsize=27, fontweight='bold', color=t['ink'], va='baseline')
    fig.canvas.draw()
    right = ax.transData.inverted().transform(name.get_window_extent().get_points())[1][0]
    ax.text(right + 12, 112, '엄기원', fontsize=14, color=t['ink2'], va='baseline')
    ax.text(41, 80, 'Tiny object detection in aerial and SAR imagery', fontsize=11.5, color=t['ink'],
            va='baseline')
    ax.text(41, 58, 'Undergraduate researcher · AIM Lab, Hanbat National University', fontsize=8.6,
            color=t['ink2'], va='baseline')
    ax.add_patch(Rectangle((41, 40), 46, 2.2, color=t['accent'], lw=0))
    fig.savefig(OUT / f'banner-{theme}.png', facecolor=t['bg'])
    plt.close(fig)


LINE = {
    'en': [
        ('2024', 'SATELLITE · MULTISPECTRAL', 'Wildfire detection', 'Grand Prize, AI SPARK Challenge'),
        ('2025', 'FACE FORENSICS', 'ViT deepfake detection\nwith facial region weights', 'J. Digital Forensics · first author'),
        ('2026', 'SAR', 'YOLO-Dos: speckle\nsuppression for SAR\nship detection', 'J. IKEEE · first author'),
        ('2026', 'AERIAL', 'SPOT-DETR: tiny object\ndetection with off-grid\ncandidates', 'Manuscript · co-first author'),
    ],
    'ko': [
        ('2024', '위성 · 다분광 영상', '산불 탐지', 'AI SPARK 챌린지 대상'),
        ('2025', '얼굴 위변조 탐지', '눈·코·입 영역 가중치를 쓰는\nViT 딥페이크 탐지', '디지털포렌식연구 · 제1저자'),
        ('2026', 'SAR 영상', 'YOLO-Dos: 스펙클 억제로\nSAR 선박 탐지 개선', '전기전자학회논문지 · 제1저자'),
        ('2026', '항공 영상', 'SPOT-DETR: off-grid 후보로\n극소 객체 탐지', '투고 준비 · 공동 제1저자'),
    ],
}


def research_line(theme, lang):
    t = THEMES[theme]
    fig = plt.figure(figsize=(8, 2.25), dpi=200)
    fig.patch.set_facecolor(t['bg'])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 225)
    ax.axis('off')
    ax.plot([60, 740], [26, 26], color=t['edge'], lw=1.2)
    w, gap, left = 178, 12, 23
    for k, (year, tag, title, outcome) in enumerate(LINE[lang]):
        x = left + k * (w + gap)
        last = k == len(LINE[lang]) - 1
        ax.add_patch(FancyBboxPatch((x, 48), w, 160, boxstyle='round,pad=0,rounding_size=8',
                                    fc=t['card'], ec=t['accent'] if last else t['edge'], lw=1.4 if last else 0.8))
        ax.plot(x + w / 2, 26, 'o', ms=7 if last else 5.5, color=t['accent'] if last else t['muted'],
                mec=t['bg'], mew=1.2)
        ax.plot([x + w / 2] * 2, [30, 48], color=t['edge'], lw=0.8)
        ax.text(x + 14, 186, year, fontsize=13, fontweight='bold', color=t['accent'], va='center')
        ax.text(x + 14, 164, tag, fontsize=6.6, color=t['ink2'], va='center')
        ax.text(x + 14, 136, title, fontsize=8.6, fontweight='bold', color=t['ink'], va='top', linespacing=1.35)
        ax.text(x + 14, 66, outcome, fontsize=7, color=t['ink2'], va='center')
    fig.savefig(OUT / f'research-line-{lang}-{theme}.png', facecolor=t['bg'])
    plt.close(fig)


def spot_gif(cache, images, image_id=10430, size=760):
    from PIL import Image, ImageDraw, ImageFont

    cache = Path(cache)
    meta = {m['id']: m for m in json.loads((cache / 'images.json').read_text())}[image_id]
    thr = json.loads((cache / 'models.json').read_text())
    gt = np.load(cache / 'gt.npz')
    gsel = gt['image_id'] == image_id
    gboxes = gt['box'][gsel]
    base_img = Image.open(Path(images) / meta['file_name']).convert('RGB')
    scale = size / base_img.width
    base_img = base_img.resize((size, round(base_img.height * scale)), Image.LANCZOS)
    bold = ImageFont.truetype(str(FONT_DIR / 'NanumGothic-Bold.ttf'), 21)
    reg = ImageFont.truetype(str(FONT_DIR / 'NanumGothic-Regular.ttf'), 16)
    colors = {'tp': (40, 170, 60), 'fp': (40, 90, 230), 'fn': (220, 40, 45)}

    def frame(model, title):
        dets = np.load(cache / 'dets' / f'{model}.npz')
        match = np.load(cache / 'match' / f'{model}.npz')
        sel = (dets['image_id'] == image_id) & (dets['score'] >= thr[model]['thr'])
        tp = match['det_tp'][sel]
        boxes = dets['box'][sel]
        found = match['gt_score'][gsel] >= thr[model]['thr']
        img = base_img.copy()
        d = ImageDraw.Draw(img)
        for b in gboxes[~found]:
            d.rectangle([*(b * scale)], outline=colors['fn'], width=2)
        for b, ok in zip(boxes, tp):
            d.rectangle([*(b * scale)], outline=colors['tp' if ok else 'fp'], width=2)
        canvas = Image.new('RGB', (size, img.height + 64), (31, 35, 40))
        canvas.paste(img, (0, 64))
        c = ImageDraw.Draw(canvas)
        c.text((18, 12), title, font=bold, fill=(240, 246, 252))
        stats = f'found {int(found.sum())} of {len(gboxes)}  ·  false alarms {int((~tp).sum())}'
        c.text((18, 40), stats, font=reg, fill=(200, 208, 216))
        x = size - 18
        for key, label in (('fn', 'missed'), ('fp', 'false alarm'), ('tp', 'correct')):
            w = c.textlength(label, font=reg)
            x -= w
            c.text((x, 40), label, font=reg, fill=(200, 208, 216))
            x -= 20
            c.rectangle([x, 43, x + 13, 56], outline=colors[key], width=3)
            x -= 16
        return canvas

    a = frame('base', 'SMWG-DETR (baseline)')
    b = frame('final', 'SPOT-DETR (ours)')
    fades = [Image.blend(a, b, w) for w in (0.25, 0.5, 0.75)]
    frames = [a, *fades, b, *fades[::-1]]
    durations = [1700, 90, 90, 90, 2200, 90, 90, 90]
    pal = [f.quantize(colors=160, method=Image.MEDIANCUT, dither=Image.NONE) for f in frames]
    pal[0].save(OUT / 'spot-detr.gif', save_all=True, append_images=pal[1:], duration=durations,
                loop=0, optimize=True, disposal=1)


def main():
    global FONT_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument('--fonts', required=True)
    ap.add_argument('--cache')
    ap.add_argument('--images')
    args = ap.parse_args()
    FONT_DIR = Path(args.fonts)
    use_fonts(FONT_DIR)
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        banner(theme)
        for lang in LINE:
            research_line(theme, lang)
    if args.cache and args.images:
        spot_gif(args.cache, args.images)
    print('\n'.join(sorted(p.name for p in OUT.iterdir())))


if __name__ == '__main__':
    main()
