#!/usr/bin/env python3
"""지출·적정보험료 진단 페이지 빌드.

- 명함 사진을 표시 크기의 2.5배(240x288) WebP로 줄여 base64로 인라인
- 파비콘(1KB PNG)도 base64 data URI로 인라인 → 페이지가 외부 요청을 전혀 하지 않는다
- 결과: index.html (저장소 루트) + downloads/2026-11-27/지출_적정보험료_진단.html
"""
import base64
import pathlib
import shutil

import make_brand_assets as brand

HERE = pathlib.Path(__file__).resolve().parent
TPL = HERE / "index.template.html"
OUT = HERE / "index.html"
ASSETS = HERE / "assets"
PHOTO_SRC = ASSETS / "photo_card.png"          # 저장소 안 원본(554x680)
PHOTO_WEBP = ASSETS / "photo_card_240.webp"    # 빌드가 만드는 인라인용 리사이즈본
FAVICON = HERE / "favicon.png"
DEST_DIR = HERE.parent / "downloads" / "2026-11-27"
DEST = DEST_DIR / "지출_적정보험료_진단.html"


def data_uri(path, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(path.read_bytes()).decode("ascii"))


def main():
    if not PHOTO_SRC.exists():
        raise SystemExit("사진 원본이 없습니다: %s" % PHOTO_SRC)
    # 인라인용 리사이즈본을 원본에서 매번 다시 만든다(원본이 바뀌면 같이 갱신)
    brand.make_photo_thumb()

    html = TPL.read_text(encoding="utf-8")

    photo_uri = data_uri(PHOTO_WEBP, "image/webp")
    favicon_uri = data_uri(FAVICON, "image/png")

    for token, value in (("__PHOTO_DATA_URI__", photo_uri), ("__FAVICON_DATA_URI__", favicon_uri)):
        assert token in html, "template placeholder missing: " + token
        html = html.replace(token, value)
    assert "__PHOTO_DATA_URI__" not in html and "__FAVICON_DATA_URI__" not in html, \
        "placeholder left unfilled"

    OUT.write_text(html, encoding="utf-8")
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OUT, DEST)

    size = OUT.stat().st_size
    print("built  %s  %.1f KB" % (OUT, size / 1024))
    print("copied %s  %.1f KB" % (DEST, DEST.stat().st_size / 1024))
    print("photo  %s  %d bytes webp -> %.1f KB base64" % (PHOTO_WEBP.name,
                                                          PHOTO_WEBP.stat().st_size,
                                                          len(photo_uri) / 1024))
    print("favicon %d bytes -> %.1f KB base64" % (FAVICON.stat().st_size, len(favicon_uri) / 1024))


if __name__ == "__main__":
    main()
