#!/usr/bin/env python3
"""Draw the profile banner and the research-line cards.

    python3 tools/make_assets.py --fonts DIR [--cache DIR --images DIR]

--fonts holds NanumGothic-Regular.ttf and NanumGothic-Bold.ttf. The banner's
satellite scene is drawn only when --cache (the qual_cache_v2test folder of the
SPOT-DETR experiments) and --images (AI-TOD-v2 test images) are given.
The demo GIF comes from tools/record_demo.py (headless Chromium on the live demo).
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


def detection_scene(cache, images, image_id=1372, size=(660, 360)):
    """Satellite crop with SPOT-DETR detections coloured by class (for the banner)."""
    from PIL import Image, ImageDraw

    cache = Path(cache)
    meta = {m['id']: m for m in json.loads((cache / 'images.json').read_text())}[image_id]
    thr = json.loads((cache / 'models.json').read_text())['final']['thr']
    dets = np.load(cache / 'dets' / 'final.npz')
    img = Image.open(Path(images) / meta['file_name']).convert('RGB')
    draw = ImageDraw.Draw(img)
    colors = {3: (235, 104, 52), 5: (57, 135, 229), 2: (27, 175, 122), 0: (232, 123, 164)}
    sel = (dets['image_id'] == image_id) & (dets['score'] >= thr)
    for box, label in zip(dets['box'][sel], dets['label'][sel]):
        draw.rectangle([*box], outline=colors.get(int(label), (240, 240, 240)), width=2)
    w, h = size
    top = 150
    crop = img.crop((0, top, 800, top + round(800 * h / w)))
    return crop.resize(size, Image.LANCZOS)


def banner(theme, scene=None):
    from PIL import Image

    t = THEMES[theme]
    fig = plt.figure(figsize=(8, 1.8), dpi=200)
    fig.patch.set_facecolor(t['bg'])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 180)
    ax.axis('off')
    name = ax.text(40, 112, 'Ki-won Eom', fontsize=27, fontweight='bold', color=t['ink'], va='baseline')
    fig.canvas.draw()
    right = ax.transData.inverted().transform(name.get_window_extent().get_points())[1][0]
    ax.text(right + 12, 112, '엄기원', fontsize=14, color=t['ink2'], va='baseline')
    ax.text(41, 80, 'Computer vision · Object detection in satellite imagery', fontsize=11.5,
            color=t['ink'], va='baseline')
    ax.text(41, 58, 'Undergraduate researcher · AIM Lab, Hanbat National University', fontsize=8.6,
            color=t['ink2'], va='baseline')
    ax.add_patch(Rectangle((41, 40), 46, 2.2, color=t['accent'], lw=0))
    out = OUT / f'banner-{theme}.png'
    fig.savefig(out, facecolor=t['bg'])
    plt.close(fig)
    if scene is None:
        return
    base = Image.open(out).convert('RGB')
    W, H = base.size
    sw, sh = scene.size
    x0 = W - sw
    ramp = np.clip(np.linspace(0, 1, sw) / 0.22, 0, 1) ** 1.4
    mask = Image.fromarray((np.tile(ramp, (sh, 1)) * 255).astype('uint8'))
    base.paste(scene, (x0, (H - sh) // 2), mask)
    base.save(out)


LINE = {
    'en': [
        ('2025', 'FACE FORENSICS', 'ViT deepfake detection\nwith facial region weights', 'J. Digital Forensics · first author'),
        ('2026', 'SAR', 'YOLO-Dos: speckle\nsuppression for SAR\nship detection', 'J. IKEEE · first author'),
        ('2026', 'AERIAL', 'SPOT-DETR: tiny object\ndetection with off-grid\ncandidates', 'Manuscript · co-first author'),
    ],
    'ko': [
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
    n = len(LINE[lang])
    gap, left = 14, 23
    w = (800 - 2 * left - (n - 1) * gap) / n
    for k, (year, tag, title, outcome) in enumerate(LINE[lang]):
        x = left + k * (w + gap)
        last = False
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
    scene = detection_scene(args.cache, args.images) if args.cache and args.images else None
    for theme in THEMES:
        banner(theme, scene)
        for lang in LINE:
            research_line(theme, lang)
    print('\n'.join(sorted(p.name for p in OUT.iterdir())))


if __name__ == '__main__':
    main()
