# 🎓 EduApp: 인사이트 기반 프로덕트 & 마케팅-블로그 자동 배선 시스템

> **저장된 프로덕트 기획서**: [`docs/PRODUCT_SPECIFICATIONS.md`](docs/PRODUCT_SPECIFICATIONS.md)  
> **마케팅 소스 디렉터리**: `/Users/name/Desktop/Cluade/EDU`  
> **배선 아웃풋 디렉터리**: `output/blog/`  

---

## 📌 1. 프로젝트 개요

본 프로젝트는 `/Users/name/Desktop/Cluade/EDU` 내에 축적된 30여 건 이상의 교육 기획서, 단일 카드뉴스, 팩트체크 데이터, 사용자 반응 분석 자료를 기반으로:
1. **학부모의 실제 결핍(Pain Points)을 해결하는 4대 신규 프로덕트 상세 설계**를 체계적으로 보관하고,
2. **마케팅 기획서가 만들어지면 네이버 블로그(2,500자 롱폼, SEO) 및 앱 게시판으로 즉시 올릴 수 있도록 자동 배선(Wiring)**하는 통합 시스템입니다.

---

## 🏛️ 2. 보관된 4대 프로덕트 상세 설계 (`docs/`)

자세한 데이터 스키마 및 사용자 흐름은 [`docs/PRODUCT_SPECIFICATIONS.md`](docs/PRODUCT_SPECIFICATIONS.md)에 저장되어 있습니다.

| 프로덕트명 | 핵심 가치 제안 (Value Proposition) | 핵심 기능 |
|---|---|---|
| **1. [EduSpot Radar]**<br>키즈 체험 예약 레이더 & 헛걸음 방지 | "무료·이색 체험 예약 오픈일 알림과 팩트체크로 헛걸음 제로" | • 전국 공공/기업 무료 체험 예약 캘린더<br>• 사전 예약 오픈 D-Day 알림<br>• 휴관일/운영시간 팩트체크<br>• 날씨/초등 교과연계 필터 |
| **2. [EduBenefit]**<br>가족 맞춤 양육·교육 지원금 진단기 | "우리 가족이 받을 수 있는 정부 지원금 1분 만에 연간 총액 계산" | • 1분 맞춤 지원금 계산기 (부모급여, 자녀장려금, 아동수당, 시간제보육)<br>• 다자녀카드(2자녀) 지역별 혜택 비교<br>• 선착순 마감형(임산부 농산물 등) D-Day 알리미 |
| **3. [EduScore 5.0]**<br>고교 5등급제 내신 분석기 | "5등급제 동점자 속출 시대, 내 아이의 진짜 위치(원점수) 진단" | • 과목별 원점수·평균·표준편차 기반 백분위 산출<br>• 1등급 10% 확대에 따른 동점자 밀집도 리포트 |
| **4. [Daily Literacy & Quest]**<br>문해력 챌린지 & 패밀리 퀘스트 | "스마트폰 과의존을 가족 오프라인 탐방과 5분 문해력으로 전환" | • 초·중등 하루 1지문 5분 문해력 퀴즈<br>• 오프라인 박물관/자연 탐방 퀘스트 & 스탬프 보상 |

---

## ⚡ 3. 마케팅 → 블로그 & 앱 게시판 자동 배선 파이프라인 (실행 방법)

마케팅 저쪽(`/Users/name/Desktop/Cluade/EDU`)의 `만든 콘텐츠/`나 `단일 카드뉴스/`에 기획서(`00-기획서.md` 또는 `00-기획안.md`)가 작성되면, 본 시스템이 정본 규격(`blog-app-prompts.md`)에 맞추어 **네이버 블로그 포맷(`01_블로그.md`)**과 **앱 게시판 포맷(`02_앱게시판.md`)**으로 즉시 변환합니다.

### 1) 배선 현황 확인
```bash
python3 scripts/sync_marketing_to_blog.py --status
```
*모든 캠페인의 기획서 유무, 블로그/앱게시판 생성 상태를 표로 한눈에 확인합니다.*

### 2) 특정 캠페인 동기화 (단건 생성)
```bash
python3 scripts/sync_marketing_to_blog.py --sync "무료체험공간8곳"
# 또는
python3 scripts/sync_marketing_to_blog.py --sync "고1-5등급제"
```

### 3) 모든 캠페인 일괄 동기화 (26개 전수 생성 완료)
```bash
python3 scripts/sync_marketing_to_blog.py --sync-all
```

### 4) 실시간 감시 모드 (저쪽에서 새로 만들면 자동 생성!)
```bash
python3 scripts/sync_marketing_to_blog.py --watch
```
*마케팅 폴더를 실시간 감시하여 새 캠페인이 추가되거나 기획서가 수정되면 즉시 01_블로그.md 및 02_앱게시판.md를 자동 생성합니다.*

### 5) macOS 원클릭 클립보드 복사 (`pbcopy` 연동)
```bash
# 네이버 블로그용 마크다운 본문 클립보드 복사
python3 scripts/sync_marketing_to_blog.py --copy-blog "고1-5등급제"

# 앱 게시판용 클린 텍스트(이모지/볼드 제거) 복사
python3 scripts/sync_marketing_to_blog.py --copy-app "고1-5등급제"

# 네이버 블로그 태그 30개만 복사
python3 scripts/sync_marketing_to_blog.py --copy-tags "고1-5등급제"
```
*터미널 실행 즉시 클립보드에 들어가므로, 네이버 스마트에디터 ONE 또는 앱 관리자 화면에서 `Cmd + V`로 바로 붙여넣을 수 있습니다.*

---

## 🌐 4. 시각적 웹 대시보드 & 미리보기 서버

마케터와 운영자가 브라우저에서 네이버 블로그 스타일로 시각적 렌더링을 확인하고, 원클릭으로 복사할 수 있는 로컬 웹 대시보드를 제공합니다.

```bash
python3 scripts/preview_server.py
```
- 브라우저 접속: **`http://localhost:8765`**
- 기능:
  - 26개 캠페인 검색 및 실시간 전환
  - 네이버 블로그 스마트에디터 ONE 스타일 렌더링 미리보기
  - 앱 게시판(순수 텍스트) 미리보기
  - 원클릭 복사 버튼: `[📋 네이버 블로그용 복사]`, `[🏷️ 태그 30개 복사]`, `[📄 마크다운 복사]`

---

## 📂 5. 디렉터리 구조

```
/Users/name/cursor/app_edu/
├── docs/
│   ├── PRODUCT_SPECIFICATIONS.md      # EDU 인사이트 기반 4대 프로덕트 상세 기획서 (영구 보관)
│   └── PIPELINE_ARCHITECTURE.md       # 마케팅-블로그 자동 배선 아키텍처 상세 문서
├── scripts/
│   ├── sync_marketing_to_blog.py      # 마케팅 -> 블로그/앱게시판 변환, CLI, 감시기, 클립보드 복사
│   ├── blog_generator.py              # 네이버 블로그 정본(2,500자, SEO, 🐶 도입부, 태그 30개) 생성기
│   ├── app_board_generator.py         # 앱 게시판(이모지 0개 전면 제거, bold 제거, 태그 4개) 생성기
│   └── preview_server.py              # 웹 미리보기 & 원클릭 복사 로컬 서버 (localhost:8765)
├── output/
│   └── blog/                          # 생성된 26개 캠페인 아카이브 (01_블로그.md, 02_앱게시판.md)
│       ├── 20260603-아이랑-무료체험공간8곳/
│       ├── 20260629-고1-5등급제/
│       ├── 20260519-다자녀카드혜택/
│       └── ... (총 26개 폴더)
└── README.md                          # 본 가이드 문서
```
