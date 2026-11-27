#!/usr/bin/env python3
"""현대홈쇼핑 PLAN H 마크 정리 — 유저가 올린 JPEG 원본 → 인라인용 고화질 에셋.

원본: 유저가 2026-11-27 카톡으로 보낸 캡처(2048x1453 JPEG, 흰 배경 + 압축 노이즈)
결과: assets/planh_mark.png      640px 폭 PNG(마스터, 인쇄·확대용)
      assets/planh_mark_640.webp 인라인용(빌드가 index.html에 base64로 넣는다)

손질 순서
 1) 마크가 있는 부분만 찾아 사방 여백을 똑같이 남기고 크롭
 2) 흰 배경을 순백(#FFFFFF)으로 — JPEG 링잉(글자 주변 회색 번짐)을 두 번에 걸쳐 정리
 3) 살짝 디노이즈(양방향 필터) 후 640px로 축소, 언샤프 마스크로 선명도 보정
 4) 글자·색은 손대지 않는다(현대홈쇼핑 / PLAN H / 현대백화점그룹 현대홈쇼핑 GA사업부)

실행: python3 make_planh_mark.py [원본JPEG경로]
"""
import pathlib
import sys

import cv2
import numpy as np
from PIL import Image, ImageFilter

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE / "assets"
DEFAULT_SRC = HERE.parent / "attachments" / "2026-11-27" / "23839-cc7a4820281c4df48678092569088030.jpg"

WIDTH = 640        # 최종 폭(표시 크기 ~150~190px의 3~4배 → 레티나·인쇄에서도 또렷)
PAD_RATIO = 0.030  # 사방 여백 = 마크 폭의 3%


def content_bbox(im):
    """흰 바탕이 아닌 픽셀(= 채도가 있거나 어두운 픽셀)의 외곽 상자."""
    a = np.asarray(im).astype(np.int16)
    mx, mn = a.max(2), a.min(2)
    content = ((mx - mn) > 25) | (mx < 235)
    cols, rows = content.sum(0), content.sum(1)
    xs = np.where(cols > 3)[0]
    ys = np.where(rows > 3)[0]
    return xs.min(), ys.min(), xs.max(), ys.max()


def whiten(im, t_hi, t_lo):
    """무채색 픽셀 중 밝은 쪽을 순백으로, 그 아래 회색 번짐은 비례해서 밝힌다."""
    a = np.asarray(im).astype(np.float32)
    mx, mn = a.max(2), a.min(2)
    sat = mx - mn
    lum = a.mean(2)
    neutral = sat < 16
    w = np.clip((lum - t_lo) / (t_hi - t_lo), 0, 1)[..., None] * neutral[..., None]
    out = a * (1 - w) + 255 * w
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))


def build(src_path):
    src = Image.open(src_path).convert("RGB")
    x0, y0, x1, y1 = content_bbox(src)
    pad = int(round((x1 - x0 + 1) * PAD_RATIO))
    crop = src.crop((x0 - pad, y0 - pad, x1 + 1 + pad, y1 + 1 + pad))

    # 1차: 원본 해상도에서 회색 번짐 정리 → 디노이즈 → 축소
    clean = whiten(crop, t_hi=242, t_lo=198)
    arr = cv2.bilateralFilter(np.asarray(clean), d=7, sigmaColor=26, sigmaSpace=7)
    h = round(WIDTH * crop.size[1] / crop.size[0])
    im = Image.fromarray(arr).resize((WIDTH, h), Image.LANCZOS)

    # 2차: 축소 후 남은 옅은 회색을 순백으로, 살짝 선명하게
    im = whiten(im, t_hi=248, t_lo=228)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=55, threshold=1))

    ASSETS.mkdir(exist_ok=True)
    png = ASSETS / "planh_mark.png"
    webp = ASSETS / "planh_mark_640.webp"
    im.save(png, "PNG", optimize=True)
    make_webp(png, webp)
    print("planh mark: crop %s → %dx%d" % (crop.size, im.size[0], im.size[1]))
    print("  %s  %.1f KB" % (png.name, png.stat().st_size / 1024))
    print("  %s  %.1f KB" % (webp.name, webp.stat().st_size / 1024))
    return im


def make_webp(png_path=None, webp_path=None):
    """인라인용 WebP. 마스터 PNG를 품질 94로 다시 담는다(눈으로 구분되지 않음)."""
    png_path = png_path or ASSETS / "planh_mark.png"
    webp_path = webp_path or ASSETS / "planh_mark_640.webp"
    Image.open(png_path).convert("RGB").save(webp_path, "WEBP", quality=94, method=6)
    return webp_path


if __name__ == "__main__":
    build(pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC)
