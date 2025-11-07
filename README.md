# 타짜 - The Zone 🃏

**AI 기반 3장 섯다 카드 게임**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.6.1+-00A86B?style=flat&logo=pygame&logoColor=white)](https://www.pygame.org/)
[![Status](https://img.shields.io/badge/Status-Beta%20v0.9-yellow?style=flat)](https://github.com/WhatSupYap/tazza-the-zone)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat)](LICENSE)

> 극도의 몰입 상태 "Zone"에 진입하여 모든 힌트를 읽고 승부하는 한국 전통 카드 게임

---

## 📋 프로젝트 소개

한국 영화 '타짜' 시리즈에서 영감을 받은 3장 섯다 게임입니다. 플레이어는 NPC의 속마음을 참고할 수 있습니다. ~~플레이어는 Zone 시스템을 활용하여 NPC의 심리와 패턴을 파악하고 승부를 겨룹니다.~~

### 주요 특징

- 🎯 **Zone 시스템**: 몰입 상태 진입 시 모든 게임 기록 회상 가능
- 🤖 **AI NPC**: Ollama + Eeve 모델 기반 실시간 대화 생성
- 🎮 **다양한 캐릭터**: 영화 속 3명의 캐릭터 (호구, 고광렬, 아귀 등)
- 🧠 **심리 시스템**: NPC의 `기본 능력치`, `멘탈`, `분노`가 플레이에 영향
- 🃏 **정통 섯다 규칙**: 20가지 족보와 전략적 베팅

---

## 🛠️ 기술 스택

<div align="center">

| Category | Technologies |
|----------|-------------|
| **Language** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) |
| **Game Engine** | ![Pygame](https://img.shields.io/badge/Pygame-00A86B?style=for-the-badge&logo=pygame&logoColor=white) |
| **AI/LLM** | ![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white) ![Eeve](https://img.shields.io/badge/Eeve_10.8B-FF6B6B?style=for-the-badge) |
| **Image Processing** | ![Pillow](https://img.shields.io/badge/Pillow-FFD43B?style=for-the-badge) |
| **IDE** | ![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white) |
<!-- | **HTTP Client** | ![Requests](https://img.shields.io/badge/Requests-3E8BFF?style=for-the-badge) | -->

</div>

---

## 🎮 게임 규칙

### 기본 설정
- **게임 방식**: 1:1 대결 (플레이어 vs NPC)
- **라운드**: 10판 (설정 변경 가능)
- **시작 금액**: 100,000원 (설정 변경 가능)
- **최소 베팅**: 1,000원 (설정 변경 가능)

### 게임 진행
1. **카드 배분** (1-2장) → 2. **1차 베팅** (1장 공개) → 3. **3장째 배분** → 4. **최종 베팅** → 5. **쇼다운**

### 베팅 옵션
- **다이 (Die)**: 포기
- **체크 (Check)**: 0원 베팅
- **삥 (Pping)**: 최소 단위 베팅
- **하프 (Half)**: 현재 판돈의 절반
- **콜 (Call)**: 상대방 금액 맞추기
- **올인 (All-In)**: 전액 베팅

---

## 🃏 섯다 족보 (낮을수록 강함)

1. **삼팔광땡** - 3광 + 8광 (최강)
2. **광땡** - 광 2장
3. **땡** - 같은 월 2장
4. **알리** - 1월 + 2월
5. **독사** - 1월 + 4월
6. **구삥** - 1월 + 9월
7. **장삥** - 1월 + 10월
8. **장사** - 4월 + 10월
9. **세륙** - 3월 + 6월
10. **끗** - 두 장의 합 (9끗 ~ 1끗)
11. **망통** - 0끗 (가장 약함)

**특수 족보**: 땡잡이(3+7), 구사(4+9), 암행어사(4열끗+7열끗) 등

---

## 🚀 설치 및 실행

### 사전 요구사항
- Python 3.12 이상
- pip (Python 패키지 관리자)

### 1. 저장소 클론
```bash
git clone https://github.com/WhatSupYap/tazza-the-zone.git
cd tazza-the-zone
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. (선택사항) Ollama 설정
LLM 기반 NPC 대화를 원할 경우:
```bash
# Ollama 설치 후
ollama pull eeve-korean-10.8b
```

### 4. 게임 실행
```bash
cd src
python main.py
```

---

## 📁 프로젝트 구조

```
phase2.5_game/
├── src/
│   ├── main.py                 # 게임 진입점
│   ├── config.py               # 설정 파일
│   ├── core/                   # 핵심 게임 로직
│   │   ├── card.py            # 카드 및 덱 시스템
│   │   ├── game.py            # 게임 메인 로직
│   │   ├── hand_evaluator.py # 족보 판정
│   │   ├── player.py          # 플레이어 클래스
│   │   └── zone.py            # Zone 시스템
│   ├── ai/                     # AI 시스템
│   │   ├── npc.py             # NPC AI 및 능력치
│   │   └── llm_handler.py     # LLM 통신
│   └── ui/                     # 사용자 인터페이스
│       ├── game_screen.py     # 메인 화면
│       ├── renderer.py        # 렌더링
│       ├── card_display.py    # 카드 표시
│       └── button.py          # UI 버튼
├── assets/
│   ├── cards/                  # 카드 이미지 (20장)
│   └── sounds/                 # 사운드 파일 (미구현)
├── docs/                       # 문서
│   ├── overview.md            # 프로젝트 개요
│   ├── checklist.md           # 개발 체크리스트
│   └── brainstoming.md        # 캐릭터 능력치
└── requirements.txt           # 의존성 목록
```

---

## 🎭 NPC 캐릭터

| 이름 | 침착성 | 말빨 | 배짱 | 회복력 | 특징 |
|------|--------|------|------|--------|------|
| 호구 | 1 | 1 | 2 | 1 | 초보 플레이어 |
| 고광렬 | 3 | 9 | 7 | 5 | 최고의 말빨, 약한 멘탈 |
| 아귀 | 10 | 9 | 9 | 10 | 완벽한 포커페이스 |
| ~~평경장~~ | 10 | 5 | 6 | 9 | 최고 경지의 타짜 |
| ~~고니~~ | 7 | 8 | 10 | 6 | 뜨거운 심장의 주인공 |
| ~~정마담~~ | 8 | 10 | 8 | 7 | 기만과 술수의 달인 |
| ~~짝귀~~ | 9 | 4 | 7 | 8 | 기술과 직관의 고수 |
| ~~곽철용~~ | 6 | 7 | 8 | 4 | 분노 조절 실패 |

---

## ⚙️ 설정 (config.py)

주요 게임 설정값:
```python
DEFAULT_ROUNDS = 10           # 라운드 수
DEFAULT_START_MONEY = 100000  # 시작 금액
DEFAULT_MIN_BET = 1000        # 최소 베팅
ZONE_BASE_CHANCE = 0.05       # Zone 발동 확률
```

---

## 📝 개발 현황

- [x] 핵심 게임 로직
- [x] 섯다 족보 시스템 (20개 족보)
- [x] NPC AI 및 심리 시스템
- [x] Zone 시스템
- [x] Pygame UI 구현
- [x] 베팅 시스템

**현재 버전**: v0.3 Beta (플레이 가능)

## 📧 연락처

**프로젝트 링크**: [https://github.com/WhatSupYap/tazza-the-zone](https://github.com/WhatSupYap/tazza-the-zone)

---