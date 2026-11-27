# 월 지출 · 적정 보험료 진단

상담용 인터랙티브 웹페이지입니다. 현대홈쇼핑GA · 금융플래너 김대민.

- 월 실수령 소득, 고정·변동 생활비, 저축·투자, 현재 월 보험료를 만원 단위로 입력
- 적정 보험료 범위(기본 월 소득의 7~10%) 대비 초과·여력 진단
- 소득 대비 지출 구성 도넛 차트, 현재 보험료 비교 바, 1년·10년 환산 금액
- 상담 메모(브라우저에만 저장), 인쇄·PDF 저장

단일 `index.html` 파일이며 외부 라이브러리·폰트·이미지 요청이 없습니다(사진은 base64 인라인).

## 수정·배포 방법

1. `index.template.html`를 고칩니다.
2. `python3 build.py` — 사진(base64)이 인라인된 `index.html`과 `downloads/2026-11-27/지출_적정보험료_진단.html`을 다시 만듭니다.
3. `python3 test_logic.py` — 계산·표시 로직을 DOM 스텁에서 검증합니다.
4. 커밋 후 두 브랜치에 push (GitHub Pages가 `gh-pages` 브랜치를 바라보고 있습니다):

```
git push origin main
git push origin main:gh-pages
```

주소: https://daemzero.github.io/insurance-check/
