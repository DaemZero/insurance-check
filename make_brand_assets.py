#!/usr/bin/env python3
"""브랜드 이미지 생성: ①명함 사진 리사이즈(assets/photo_card_240.webp) ②og-image.png ③favicon.png

- 원본: assets/photo_card.png (work_guwon/photo_card.png 에서 복사해 둔 554x680)
- 실행: python3 make_brand_assets.py
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE / "assets"
SRC = ASSETS / "photo_card.png"

TEAL_900 = (11, 59, 56)
TEAL_800 = (19, 78, 74)
TEAL_700 = (15, 118, 110)
TEAL_600 = (16, 101, 94)
GOLD = (217, 181, 102)
GOLD_DEEP = (181, 133, 47)
CREAM = (247, 243, 233)

FONT_REG = "/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf"
# 굵은 자체가 없어 획 두께(stroke_width)로 굵기를 흉내 낸다.
BOLD = 3


def font(size):
    return ImageFont.truetype(FONT_REG, size)


def kr_text(draw, xy, text, size, fill, bold=0, anchor="la"):
    """한글 텍스트. bold>0 이면 같은 글자를 살짝 겹쳐 써서 굵게 보이게 한다."""
    f = font(size)
    draw.text(xy, text, font=f, fill=fill, anchor=anchor,
              stroke_width=bold, stroke_fill=fill)
    return draw.textbbox(xy, text, font=f, anchor=anchor, stroke_width=bold)


# ---------------------------------------------------------------- 사진 리사이즈
def make_photo_thumb():
    im = Image.open(SRC).convert("RGB")
    tw, th = 240, 288  # 표시 크기(96x112)의 2.5배 / 240x288
    ratio = tw / th
    w, h = im.size
    if w / h > ratio:            # 원본이 더 넓으면 좌우 크롭
        nw = int(h * ratio)
        left = (w - nw) // 2
        im = im.crop((left, 0, left + nw, h))
    else:                        # 세로 크롭(위쪽 22% 지점 기준 — CSS object-position 50% 22%)
        nh = int(w / ratio)
        top = int((h - nh) * 0.22)
        im = im.crop((0, top, w, top + nh))
    im = im.resize((tw, th), Image.LANCZOS)
    out_webp = ASSETS / "photo_card_240.webp"
    im.save(out_webp, "WEBP", quality=80, method=6)
    out_jpg = ASSETS / "photo_card_240.jpg"
    im.save(out_jpg, "JPEG", quality=82, optimize=True, progressive=True)
    print("photo thumb:", out_webp, out_webp.stat().st_size, "bytes /",
          out_jpg.name, out_jpg.stat().st_size, "bytes")
    return im


# ---------------------------------------------------------------- og-image
def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.size[0], im.size[1]),
                                           radius=radius, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def make_og(photo):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), TEAL_800)
    d = ImageDraw.Draw(img)

    # 세로 그라데이션 (좌상단 어두운 청록 → 우하단 밝은 청록)
    for y in range(H):
        t = y / (H - 1)
        r = int(TEAL_900[0] + (TEAL_600[0] - TEAL_900[0]) * t)
        g = int(TEAL_900[1] + (TEAL_600[1] - TEAL_900[1]) * t)
        b = int(TEAL_900[2] + (TEAL_600[2] - TEAL_900[2]) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))

    # 우상단 금색 광원
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(26, 0, -1):
        rad = i * 22
        alpha = int(9 * (1 - i / 26) * 6)
        gd.ellipse((1030 - rad, -110 - rad, 1030 + rad, -110 + rad),
                   fill=(GOLD[0], GOLD[1], GOLD[2], max(1, alpha)))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    d = ImageDraw.Draw(img)

    # 좌측 텍스트 블록
    x = 84
    kr_text(d, (x, 96), "1분 보험료 건강검진", 24, GOLD, bold=1)
    d.line([(x, 144), (x + 74, 144)], fill=GOLD_DEEP, width=3)

    kr_text(d, (x, 176), "내 보험료,", 64, (255, 255, 255), bold=2)
    kr_text(d, (x, 254), "지금 딱 맞을까?", 64, (255, 255, 255), bold=2)

    kr_text(d, (x, 362), "현대홈쇼핑GA · 금융플래너 김대민", 32, (207, 230, 225), bold=1)
    d.line([(x, 432), (x + 520, 432)], fill=(255, 255, 255, 40), width=2)
    kr_text(d, (x, 462), "월 소득과 지출을 입력하면, 지금 내는 보험료가", 25, (185, 214, 208))
    kr_text(d, (x, 502), "적정한 수준인지 바로 확인할 수 있습니다.", 25, (185, 214, 208))

    # 우측 인물 사진 카드
    pw, ph = 300, 360
    face = photo.resize((pw, ph), Image.LANCZOS)
    card = Image.new("RGBA", (pw + 16, ph + 16), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, pw + 15, ph + 15), radius=26, fill=GOLD + (255,))
    inner = rounded(face, 20)
    card.alpha_composite(inner, (8, 8))
    img.alpha_composite(card, (1200 - 84 - pw - 16, 132))

    # 좌하단 주소
    kr_text(d, (x, 560), "daemzero.github.io/insurance-check", 20, (140, 178, 171))

    out = HERE / "og-image.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print("og-image:", out, out.stat().st_size, "bytes")


# ---------------------------------------------------------------- favicon
def make_favicon():
    S = 128
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 둥근 사각 청록 배경 + 금색 테두리
    d.rounded_rectangle((2, 2, S - 3, S - 3), radius=30, fill=TEAL_800,
                        outline=GOLD, width=5)
    # 가운데 금색 원 + 체크(진단) 표시
    cx, cy, r = S // 2, S // 2 - 6, 27
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=5)
    d.line([(cx - 13, cy + 1), (cx - 3, cy + 11), (cx + 14, cy - 10)],
           fill=(255, 255, 255), width=8, joint="curve")
    img.save(HERE / "favicon.png", "PNG", optimize=True)

    # 애플 터치 아이콘(180) — 배경 불투명
    t = Image.new("RGB", (180, 180), TEAL_800)
    td = ImageDraw.Draw(t)
    td.rounded_rectangle((0, 0, 179, 179), radius=0, fill=TEAL_800)
    td.ellipse((90 - 44, 78 - 44, 90 + 44, 78 + 44), outline=GOLD, width=8)
    td.line([(90 - 21, 79), (90 - 5, 95), (90 + 23, 61)], fill=(255, 255, 255),
            width=12, joint="curve")
    t.save(HERE / "apple-touch-icon.png", "PNG", optimize=True)
    print("favicon:", (HERE / "favicon.png").stat().st_size, "bytes / apple-touch-icon:",
          (HERE / "apple-touch-icon.png").stat().st_size, "bytes")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    thumb = make_photo_thumb()
    make_og(thumb)
    make_favicon()
