# 내 보험료, 지금 딱 맞을까? · 1분 보험료 건강검진

상담용 인터랙티브 웹페이지입니다. 현대홈쇼핑GA · 금융플래너 김대민.

- 월 실수령 소득, 고정·변동 생활비, 저축·투자, 현재 월 보험료를 만원 단위로 입력 (예시: 30대·40대·50대·60대)
- 적정 보험료 범위(기본 월 소득의 7~10%) 대비 초과·여력 진단
- 소득 대비 지출 구성 도넛 차트, 현재 보험료 비교 바, 1년·10년 환산 금액
- 상담 메모 03번: 성함 · 상담보험(15종 복수 선택) · 궁금하신 사항 · 연락가능시간(오전/오후·1~12시·00/30분) · 연락방법(전화/문자) — 브라우저에만 저장, 인쇄물에는 선택값만 요약
- 인쇄·PDF 저장
- **진단 결과를 김대민 플래너 Gmail로 바로 보내기** (고객 성함·연락처·동의 입력 → Formsubmit AJAX)
- 카톡·문자 링크 미리보기(og:image)와 파비콘

주소: https://daemzero.github.io/insurance-check/

## 파일

| 파일 | 쓰임 |
| --- | --- |
| `index.template.html` | 편집하는 원본 HTML (사진은 `__PHOTO_DATA_URI__` 자리표시자) |
| `index.html` | `build.py`가 만든 배포본 — 직접 고치지 마세요 |
| `build.py` | 사진 리사이즈·base64 인라인 → `index.html` + `downloads/2026-11-27/지출_적정보험료_진단.html` |
| `make_brand_assets.py` | `og-image.png`(1200×630), `favicon.png`, `apple-touch-icon.png`, 사진 썸네일 생성 |
| `assets/photo_card.png` | 명함 사진 원본 554×680 (저장소 안에서 관리) |
| `assets/photo_card_240.webp` | 표시 크기의 2.5배 리사이즈본 — 빌드가 매번 다시 만듭니다 |
| `test_logic.py` | 계산·표시 로직, 인쇄 안내, 결과 전송(필수값 검증·payload·성공/실패 표시)을 DOM 스텁에서 검증 |
| `deploy.sh` | main·gh-pages 푸시 → 저장소 설명/홈페이지 설정 → 200 확인 |

## 수정·배포 방법

1. `index.template.html`을 고칩니다. (사진을 바꿀 때는 `assets/photo_card.png` 교체)
2. `python3 build.py` — 사진(WebP 240×288, 약 5KB)과 파비콘을 인라인한 `index.html`(약 60KB)을 만듭니다.
3. `python3 test_logic.py` — 계산·표시 로직을 검증합니다.
4. `./deploy.sh` — `git push origin main`, `git push origin main:gh-pages`를 함께 수행합니다.
   GitHub Pages가 `gh-pages` 브랜치를 바라보고 있어 두 브랜치 모두 올려야 실제 주소에 반영됩니다.

```bash
python3 build.py && python3 test_logic.py && ./deploy.sh
```

## 참고

- 단일 HTML 파일이며 페이지가 외부 라이브러리·폰트·이미지 요청을 하지 않습니다(사진·파비콘 모두 data URI 인라인). og:image와 전송(Formsubmit)만 외부 요청입니다.
- 인쇄는 A4 2장으로 떨어집니다(1장: 표지·입력·진단 결과 / 2장: 상담 메모·명함). 04번 '진단 결과 보내기' 카드는 `.no-print`라 인쇄물에 나오지 않습니다.
- 03번 상담 메모의 선택 컨트롤(보험 칩·오전/오후·시·분·전화/문자)은 화면 전용이고, 인쇄물에는 `#insPrint`·`#timePrint`·`#methodPrint` 요약 문장만 나옵니다.
- 카톡 등 앱 안의 브라우저에서는 `window.print()`가 막히므로, 인앱 감지 또는 `beforeprint` 미발생 시 "다른 브라우저로 열기" 안내가 버튼 아래에 표시됩니다.

## 진단 결과 메일 전송(Formsubmit)

- `index.template.html`의 `SEND_URL`이 전송 주소입니다. 공개 저장소·공개 페이지에 개인 메일 주소가 노출되지 않도록 **Formsubmit이 발급한 무작위 별칭**을 씁니다(수신 주소는 저장소에 적지 않습니다).
- 활성화는 **도메인 단위 1회**입니다. 주소(도메인)를 바꾸면 그 도메인에서 첫 전송 때 Formsubmit이 보내는 활성화 메일의 링크를 한 번 눌러야 합니다.
- Formsubmit을 거친 메일은 Gmail이 **스팸함**으로 보내는 경우가 있습니다. Gmail 필터에서 `from:(submissions@formsubmit.co)` → **스팸으로 분류하지 않음**을 걸어 두면 받은편지함으로 들어옵니다.
- 수신 주소를 바꾸려면 새 주소로 한 번 전송해 받은 활성화 메일의 링크를 누르고, 그 메일이 알려 주는 별칭을 `SEND_URL`에 넣으면 됩니다.
