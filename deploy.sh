#!/usr/bin/env bash
# GitHub Pages 배포 스크립트
#   사용법: ./deploy.sh [owner/repo]   (기본값: DaemZero/insurance-check)
#   전제: 저장소가 먼저 존재해야 합니다(GitHub App 권한으로는 저장소 생성이 불가).
set -euo pipefail
REPO="${1:-DaemZero/insurance-check}"
OWNER="${REPO%%/*}"
NAME="${REPO##*/}"
URL="https://$(echo "$OWNER" | tr '[:upper:]' '[:lower:]').github.io/$NAME/"
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
git push -u origin main

echo "→ GitHub Pages 활성화 시도"
gh api -X POST "/repos/$REPO/pages" \
  -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 || \
gh api -X PUT "/repos/$REPO/pages" \
  -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 || \
gh api -X POST "/repos/$REPO/pages" -f "build_type=legacy" \
  -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 || \
  echo "  ! Pages API가 거부되었습니다. GitHub → Settings → Pages → 'Deploy from a branch' → main / (root) 로 켜 주세요."

echo "→ 배포 대기"
for i in $(seq 1 20); do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$URL" || true)
  echo "   [$i] $code $URL"
  [ "$code" = "200" ] && break
  sleep 10
done
echo "배포 주소: $URL"
