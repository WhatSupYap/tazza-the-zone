

# 🎴 타짜 - The Zone

# 🎴 타짜 - The Zone

> 극도의 몰입 상태 "Zone"에서 펼쳐지는 3장 섯다 게임

> 극도의 몰입 상태 "Zone"에서 펼쳐지는 3장 섯다 게임

![Python](https://img.shields.io/badge/Python-3.12.12-3776AB?style=flat-square&logo=python&logoColor=white)

![Pygame](https://img.shields.io/badge/Pygame-2.6.1-00A67E?style=flat-square&logo=python&logoColor=white)![Python](https://img.shields.io/badge/Python-3.12.12-3776AB?style=flat-square&logo=python&logoColor=white)

![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)![Pygame](https://img.shields.io/badge/Pygame-2.6.1-00A67E?style=flat-square&logo=python&logoColor=white)

![Status](https://img.shields.io/badge/Status-Beta%20v0.9-yellow?style=flat-square)![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

![Status](https://img.shields.io/badge/Status-Beta%20v0.5-yellow?style=flat-square)

**뛰어난 관찰력과 기억력으로 느려진 세상 속 모든 힌트를 활용해 승리하세요.**

**뛰어난 관찰력과 기억력으로 느려진 세상 속 모든 힌트를 활용해 승리하세요.**

---

---

## 🎮 게임 소개

## 🎮 게임 소개

AI 기반 NPC와 대결하는 3장 섯다 게임입니다. 독창적인 "Zone" 시스템을 통해 과거 라운드 기록을 회상하고 전략을 세울 수 있습니다.

AI 기반 NPC와 대결하는 3장 섯다 게임입니다. ~~독창적인 "Zone" 시스템을 통해 과거 라운드 기록을 회상하고 전략을 세울 수 있습니다.~~

### 핵심 기능

- **3장 섯다**: 화투 20장을 사용한 전통 섯다 게임### 핵심 기능

- **Zone 시스템**: 확률 기반 발동, 이전 게임 기록 열람 가능- **3장 섯다**: 화투 20장을 사용한 전통 섯다 게임

- **AI NPC**: 4가지 성격 능력치와 멘탈/분노 상태에 따른 행동 변화- **Zone 시스템**: 확률 기반 발동, 이전 게임 기록 열람 가능

- **족보 시스템**: 12가지 기본 족보 + 4가지 특수 족보- **AI NPC**: 4가지 성격 능력치와 멘탈/분노 상태에 따른 행동 변화

- **족보 시스템**: 12가지 기본 족보 + 4가지 특수 족보

---

### 개발 현황 (v0.5 - 베타)

## 🚀 빠른 시작- ✅ 핵심 게임 로직 완성

- ✅ Pygame 기반 GUI 구현

### 요구사항- ✅ NPC AI 시스템 완성

- Python 3.12 이상- ✅ LLM 대화 연동 예정 (현재 임시 대사 사용)

- ⏳ Zone 시스템 구현

### 설치

---

```bash

# 1. 저장소 클론## 🚀 빠른 시작

git clone https://github.com/WhatSupYap/tazza-the-zone.git

cd tazza-the-zone### 요구사항

- Python 3.12 이상

# 2. 패키지 설치

pip install -r requirements.txt### 설치

```

```bash

### 실행# 1. 저장소 클론

git clone https://github.com/WhatSupYap/tazza-the-zone.git

```bashcd tazza-the-zone

# GUI 버전 (권장)

cd src# 2. 패키지 설치

python main.pypip install -r requirements.txt

```

# 콘솔 버전

python main_console.py### 실행

```

```bash

---# GUI 버전 (권장)

cd src

## 🎯 게임 플레이python main.py



### 기본 규칙# 콘솔 버전

- 총 10라운드 진행python main_console.py

- 시작 금액: 각 100,000원```

- 최소 베팅: 1,000원

---

### 진행 순서

1. 각 플레이어에게 2장 배분 → 1장 공개 → 1차 베팅## 🎯 게임 플레이

2. 3번째 카드 배분 → 2차 베팅

3. 쇼다운 (족보 비교)### 기본 규칙

- 총 10라운드 진행

### 베팅 옵션- 시작 금액: 각 100,000원

| 옵션 | 설명 |- 최소 베팅: 1,000원

|------|------|

| 다이 | 포기 |### 진행 순서

| 체크 | 패스 |1. 각 플레이어에게 2장 배분 → 1장 공개 → 1차 베팅

| 삥 | 최소 금액 베팅 |2. 3번째 카드 배분 → 2차 베팅

| 하프 | 판돈의 절반 베팅 |3. 쇼다운 (족보 비교)

| 콜 | 상대 베팅 금액 맞춤 |

| 올인 | 전 재산 베팅 |### 베팅 옵션

| 옵션 | 설명 |

### 조작법|------|------|

- **마우스**: 버튼/카드 클릭| 다이 | 포기 |

- **SPACE**: 다음 단계| 체크 | 패스 |

- **ESC**: 게임 종료| 삥 | 최소 금액 베팅 |

- **족보 버튼**: 언제든 족보 확인 가능| 하프 | 판돈의 절반 베팅 |

| 콜 | 상대 베팅 금액 맞춤 |

---| 올인 | 전 재산 베팅 |



## 🎴 족보 시스템### 조작법

- **마우스**: 버튼/카드 클릭

### 기본 족보 (12종)- **SPACE**: 다음 단계

삼팔광땡 > 1광땡 ~ 9땡 > 알리 > 독사 > 구삥 > 장삥 > 장사 > 세륙 > 갑오 > 끗 > 망통- **ESC**: 게임 종료

- **족보 버튼**: 언제든 족보 확인 가능

### 특수 족보 (4종)

- **땡잡이** (3월+7월): 1~9땡 격파---

- **구사** (4월+9월): 재경기 발동

- **멍텅구리구사** (4열끗+9열끗): 9땡 격파## 🎴 족보 시스템

- **암행어사** (4열끗+7열끗): 1광땡, 3광땡 격파

### 기본 족보 (12종)

---삼팔광땡 > 1광땡 ~ 9땡 > 알리 > 독사 > 구삥 > 장삥 > 장사 > 세륙 > 갑오 > 끗 > 망통



## 📁 프로젝트 구조### 특수 족보 (4종)

- **땡잡이** (3월+7월): 1~9땡 격파

```- **구사** (4월+9월): 재경기 발동

📦 tazza-the-zone/- **멍텅구리구사** (4열끗+9열끗): 9땡 격파

├── src/- **암행어사** (4열끗+7열끗): 1광땡, 3광땡 격파

│   ├── main.py               # GUI 실행

│   ├── main_console.py       # 콘솔 실행---

│   ├── config.py             # 전역 설정

│   ├── core/                 # 게임 로직## 📁 프로젝트 구조

│   │   ├── card.py          # 카드/덱

│   │   ├── hand_evaluator.py # 족보 평가```

│   │   ├── player.py        # 플레이어📦 tazza-the-zone/

│   │   ├── zone.py          # Zone 시스템├── src/

│   │   └── game.py          # 메인 로직│   ├── main.py               # GUI 실행

│   ├── ai/                   # NPC AI│   ├── main_console.py       # 콘솔 실행

│   │   ├── npc.py           # NPC 플레이어│   ├── config.py             # 전역 설정

│   │   └── llm_handler.py   # LLM 통신│   ├── core/                 # 게임 로직

│   └── ui/                   # Pygame UI│   │   ├── card.py          # 카드/덱

│       ├── renderer.py      # 렌더링│   │   ├── hand_evaluator.py # 족보 평가

│       ├── button.py        # 버튼│   │   ├── player.py        # 플레이어

│       ├── card_display.py  # 카드 표시│   │   ├── zone.py          # Zone 시스템

│       └── game_screen.py   # 게임 화면 (2500+ lines)│   │   └── game.py          # 메인 로직

├── assets/                   # 에셋│   ├── ai/                   # NPC AI

│   └── cards/               # 카드 이미지 (21개)│   │   ├── npc.py           # NPC 플레이어

├── docs/                     # 문서│   │   └── llm_handler.py   # LLM 통신

└── requirements.txt│   └── ui/                   # Pygame UI

```│       ├── renderer.py      # 렌더링

│       ├── button.py        # 버튼

---│       ├── card_display.py  # 카드 표시

│       └── game_screen.py   # 게임 화면 (2500+ lines)

## 🔧 기술 스택├── assets/                   # 에셋

│   └── cards/               # 카드 이미지 (21개)

### 언어 & 프레임워크├── docs/                     # 문서

![Python](https://img.shields.io/badge/Python-3.12.12-3776AB?style=for-the-badge&logo=python&logoColor=white)└── requirements.txt

![Anaconda](https://img.shields.io/badge/Anaconda-44A833?style=for-the-badge&logo=anaconda&logoColor=white)```



### 주요 라이브러리---

![Pygame](https://img.shields.io/badge/Pygame-2.6.1-00A67E?style=for-the-badge&logo=python&logoColor=white)

![Pillow](https://img.shields.io/badge/Pillow-12.0.0-4B8BBE?style=for-the-badge&logo=python&logoColor=white)## 🔧 기술 스택

![Requests](https://img.shields.io/badge/Requests-2.32.5-FF6B6B?style=for-the-badge&logo=python&logoColor=white)

### 언어 & 프레임워크

### AI & LLM (선택 사항)![Python](https://img.shields.io/badge/Python-3.12.12-3776AB?style=for-the-badge&logo=python&logoColor=white)

![Ollama](https://img.shields.io/badge/Ollama-0.6.0-000000?style=for-the-badge&logo=ollama&logoColor=white)![Anaconda](https://img.shields.io/badge/Anaconda-44A833?style=for-the-badge&logo=anaconda&logoColor=white)

![LLM](https://img.shields.io/badge/Eeve--Korean-10.8B-FF6F00?style=for-the-badge&logo=ai&logoColor=white)

### 주요 라이브러리

### 개발 도구![Pygame](https://img.shields.io/badge/Pygame-2.6.1-00A67E?style=for-the-badge&logo=python&logoColor=white)

![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)![Pillow](https://img.shields.io/badge/Pillow-12.0.0-4B8BBE?style=for-the-badge&logo=python&logoColor=white)

![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)![Requests](https://img.shields.io/badge/Requests-2.32.5-FF6B6B?style=for-the-badge&logo=python&logoColor=white)



---### AI & LLM (선택 사항)

![Ollama](https://img.shields.io/badge/Ollama-0.6.0-000000?style=for-the-badge&logo=ollama&logoColor=white)

## 📊 개발 현황 (v0.9 Beta)![LLM](https://img.shields.io/badge/Eeve--Korean-10.8B-FF6F00?style=for-the-badge&logo=ai&logoColor=white)



### ✅ 완료### 개발 도구

- 핵심 게임 로직 (섯다, 베팅, 족보)![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)

- NPC AI 시스템 (4가지 능력치 + 멘탈/분노)![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)

- Zone 시스템 (발동, 기록 추적)

- Pygame GUI (2500+ 라인)---

- 카드 이미지 에셋 (21개)

- 콘솔 버전## � 개발 현황 (v0.9 Beta)



### 🚧 개선 중### ✅ 완료

- UI/UX 폴리싱- 핵심 게임 로직 (섯다, 베팅, 족보)

- 밸런스 조정- NPC AI 시스템 (4가지 능력치 + 멘탈/분노)

- Zone 시스템 (발동, 기록 추적)

### 📋 향후 계획- Pygame GUI (2500+ 라인)

- LLM 연동 (Ollama)- 카드 이미지 에셋 (21개)

- 사운드 시스템- 콘솔 버전

- 추가 NPC 캐릭터

- Zone UI 고도화### 🚧 개선 중

- UI/UX 폴리싱

---- 밸런스 조정



## 🤝 기여### 📋 향후 계획

- Zone UI 고도화

이슈, 풀 리퀘스트 환영합니다!



------



## 📄 라이선스## � 링크



MIT License**Repository**: https://github.com/WhatSupYap/tazza-the-zone



------



## 🔗 링크**행운을 빕니다! 🎴**


**Repository**: https://github.com/WhatSupYap/tazza-the-zone

---

**행운을 빕니다! 🎴**
