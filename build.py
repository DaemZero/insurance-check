#!/usr/bin/env python3
# 지출·적정보험료 진단 페이지 빌드: 사진을 base64로 인라인해 단일 HTML 생성
import base64, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent
TPL = HERE / "index.template.html"
OUT = HERE / "index.html"
PHOTO = ROOT / "work_guwon" / "photo_card.png"
DEST_DIR = ROOT / "downloads" / "2026-11-27"
DEST = DEST_DIR / "지출_적정보험료_진단.html"

html = TPL.read_text(encoding="utf-8")
b64 = base64.b64encode(PHOTO.read_bytes()).decode("ascii")
uri = "data:image/png;base64," + b64
assert "__PHOTO_DATA_URI__" in html
html = html.replace("__PHOTO_DATA_URI__", uri)
OUT.write_text(html, encoding="utf-8")

DEST_DIR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(OUT, DEST)
print("built", OUT, OUT.stat().st_size, "bytes")
print("copied", DEST, DEST.stat().st_size, "bytes")
print("photo b64 chars:", len(b64))
