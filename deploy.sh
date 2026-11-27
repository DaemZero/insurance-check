#!/usr/bin/env bash
# GitHub Pages 배포 스크립트
#   사용법: ./deploy.sh [owner/repo]   (기본값: DaemZero/insurance-check)
#   전제: 저장소가 먼저 존재해야 합니다(GitHub App 권한으로는 저장소 생성이 불가).
#   하는 일: main push → gh-pages push(Pages가 보는 브랜치) → 저장소 설명·홈페이지 설정 → 200 확인
set -euo pipefail
REPO="${1:-DaemZero/insurance-check}"
OWNER="${REPO%%/*}"
NAME="${REPO##*/}"
URL="https://$(echo "$OWNER" | tr '[:upper:]' '[:lower:]').github.io/$NAME/"
DESC="내 보험료, 지금 딱 맞을까? · 1분 보험료 건강검진 (현대홈쇼핑GA 김대민)"
cd "$(dirname "$0")"

if ! gh repo view "$REPO" >/dev/null 2>&1; then
  echo "✗ 저장소 $REPO 가 없습니다."
  echo "  github.com/new 에서 빈 공개 저장소($NAME)를 먼저 만들어 주세요."
  echo "  → https://github.com/new?name=$NAME&visibility=public"
  exit 2
fi

git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$REPO.git"
git branch -M main

echo "→ main 푸시"
git push -u origin main

echo "→ gh-pages 푸시 (GitHub Pages 가 바라보는 브랜치)"
git push origin main:gh-pages

echo "→ 저장소 설명·홈페이지 설정"
gh api -X PATCH "/repos/$REPO" -f "description=$DESC" -f "homepage=$URL" >/dev/null \
  && echo "   ✓ description / homepage 반영" \
  || echo "   ! 저장소 설정을 바꿀 권한이 없습니다(403). 건너뜁니다."

echo "→ GitHub Pages 활성화 시도"
gh api -X POST "/repos/$REPO/pages" \
  -f "source[branch]=gh-pages" -f "source[path]=/" >/dev/null 2>&1 || \
gh api -X PUT "/repos/$REPO/pages" \
  -f "source[branch]=gh-pages" -f "source[path]=/" >/dev/null 2>&1 || \
  echo "  ! Pages API가 거부되었습니다. GitHub → Settings → Pages → 'Deploy from a branch' → gh-pages / (root) 로 켜 주세요."

echo "→ 배포 대기"
for i in $(seq 1 20); do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$URL" || true)
  echo "   [$i] $code $URL"
  [ "$code" = "200" ] && break
  sleep 10
done

echo "→ og-image 확인"
curl -s -o /dev/null -w '   og-image.png %{http_code} %{size_download} bytes\n' "${URL}og-image.png" || true
echo "배포 주소: $URL"
