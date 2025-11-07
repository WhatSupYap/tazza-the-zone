"""
타짜 - The Zone 게임 설정 파일
모든 게임 설정값을 관리합니다.
"""

# MODEL_NAME = 'EEVE-Korean'
MODEL_NAME = 'EEVE-Korean'
# MODEL_NAME = 'anpigon/eeve-korean-10.8b'

SCREEN_TITLE = '타짜 - The Zone'

CARD_ASSETS_PATH = './assets/cards'

# ==================== 화면 설정 ====================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# ==================== 색상 설정 ====================
# RGB 색상 코드 (R, G, B)

# 기본 색상
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (200, 200, 200)

# UI 색상
COLOR_BG = (20, 40, 30)  # 배경색 (어두운 녹색)
COLOR_TEXT = (220, 220, 220)  # 텍스트 색상 (밝은 회색)
COLOR_TABLE = (0, 100, 50)  # 테이블 색상 (포커 테이블 녹색)
COLOR_HIGHLIGHT = (255, 215, 0)  # 강조색 (골드)
COLOR_GOLD = (255, 215, 0)  # 골드색

# 상태 색상
COLOR_SUCCESS = (46, 204, 113)  # 성공/긍정 (녹색)
COLOR_DANGER = (231, 76, 60)  # 위험/부정 (빨강)
COLOR_WARNING = (241, 196, 15)  # 경고 (노랑)
COLOR_INFO = (52, 152, 219)  # 정보 (파랑)

# 등급 색상 (블리자드 스타일)
COLOR_COMMON = (157, 157, 157)  # C (Common) - 회백색
COLOR_UNCOMMON = (30, 255, 0)  # UC (Uncommon) - 녹색
COLOR_RARE = (0, 112, 221)  # R (Rare) - 파란색
COLOR_EPIC = (163, 53, 238)  # SR (Super Rare/Epic) - 보라색
COLOR_LEGENDARY = (255, 128, 0)  # SSR (Legendary) - 주황색/금색
COLOR_MYTHIC = (229, 28, 35)  # UR (Ultra Rare/Mythic) - 빨간색

# 레거시 색상 (하위 호환성)
COLOR_DARK_GREEN = (0, 100, 0)
COLOR_RED = (220, 20, 60)
COLOR_BLUE = (30, 144, 255)

# ==================== 게임 설정 ====================
# 기본 게임 규칙
DEFAULT_ROUNDS = 10  # 기본 라운드 수
DEFAULT_START_MONEY = 100000  # 시작 금액 (원)
DEFAULT_MIN_BET = 1000  # 최소 베팅 금액 (원)
DEFAULT_BET_TIME = 10  # 베팅 제한 시간 (초)

# ==================== Zone 시스템 설정 ====================
# Zone 발동 확률 (0.0 ~ 1.0)
ZONE_BASE_CHANCE = 0.05  # 기본 5%
ZONE_HIGH_BET_CHANCE = 0.15  # 판돈 50% 이상 베팅 시 15%
ZONE_SPECIAL_HAND_CHANCE = 0.20  # 특수 족보 시 20%

# Zone 지속 시간 (초)
ZONE_DURATION = 60

# ==================== NPC 능력치 범위 ====================
# 각 능력치는 1~10 범위
NPC_STAT_MIN = 1
NPC_STAT_MAX = 10

# ==================== 멘탈/분노 설정 ====================
# 멘탈 설정
MENTAL_START = 100  # 시작 멘탈
MENTAL_THRESHOLD = 30  # 임계점 (이하일 때 능력치 반감)
MENTAL_DECREASE_MIN = 1  # 패배 시 최소 감소량
MENTAL_DECREASE_MAX = 5  # 패배 시 최대 감소량

# 분노 설정
ANGER_START = 0  # 시작 분노
ANGER_THRESHOLD = 70  # 임계점 (초과 시 베팅 상한선 무시)

# ==================== 에셋 경로 ====================
# 카드 이미지
ASSETS_PATH = "assets"
CARDS_PATH = f"{ASSETS_PATH}/cards"
CARD_BACK_PATH = f"{CARDS_PATH}/back.png"

# 사운드 (추후 구현)
SOUNDS_PATH = f"{ASSETS_PATH}/sounds"

# 폰트 (추후 구현)
FONTS_PATH = f"{ASSETS_PATH}/fonts"

# ==================== LLM 설정 ====================
LLM_MODEL = "eeve"  # Ollama 모델명
LLM_API_URL = "http://localhost:11434/api/generate"  # Ollama API URL
LLM_TIMEOUT = 30  # API 타임아웃 (초)
LLM_TEMPERATURE = 0.8  # 응답 다양성 (0.0 ~ 1.0)

# ==================== 카드 설정 ====================
# 카드 이미지 크기
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_SCALE = 1.0  # 카드 스케일 조정

# 카드 배치 위치
CARD_SPACING = 20  # 카드 간 간격

# ==================== UI 설정 ====================
# 버튼 크기
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 50
BUTTON_PADDING = 10

# 폰트 크기
FONT_SIZE_SMALL = 20
FONT_SIZE_MEDIUM = 28
FONT_SIZE_LARGE = 36
FONT_SIZE_XLARGE = 48

# ==================== 화투 카드 정의 ====================
# 화투 패 타입
CARD_TYPE_GWANG = "gwang"  # 광
CARD_TYPE_TTI = "tti"  # 띠
CARD_TYPE_YEOLKKUT = "yeolkkut"  # 열끗

# 카드 타입 코드 (파일명용)
CARD_TYPE_CODES = {
    CARD_TYPE_GWANG: "g",
    CARD_TYPE_TTI: "t",
    CARD_TYPE_YEOLKKUT: "k"
}

# 카드 타입 우선순위 (턴 결정 시)
CARD_TYPE_PRIORITY = {
    CARD_TYPE_GWANG: 3,
    CARD_TYPE_YEOLKKUT: 2,
    CARD_TYPE_TTI: 1
}

# 화투 패 정의 (월별)
HWATU_CARDS = {
    1: [CARD_TYPE_GWANG, CARD_TYPE_TTI],  # 솔
    2: [CARD_TYPE_YEOLKKUT, CARD_TYPE_TTI],  # 매조
    3: [CARD_TYPE_GWANG, CARD_TYPE_TTI],  # 벚꽃
    4: [CARD_TYPE_YEOLKKUT, CARD_TYPE_TTI],  # 흑싸리
    5: [CARD_TYPE_YEOLKKUT, CARD_TYPE_TTI],  # 난초
    6: [CARD_TYPE_YEOLKKUT, CARD_TYPE_TTI],  # 모란
    7: [CARD_TYPE_YEOLKKUT, CARD_TYPE_TTI],  # 홍싸리
    8: [CARD_TYPE_GWANG, CARD_TYPE_YEOLKKUT],  # 공산
    9: [CARD_TYPE_YEOLKKUT, CARD_TYPE_TTI],  # 국진
    10: [CARD_TYPE_YEOLKKUT, CARD_TYPE_TTI]  # 단풍
}

# 화투 패 이름
CARD_NAMES = {
    1: "솔", 2: "매조", 3: "벚꽃", 4: "흑싸리", 5: "난초",
    6: "모란", 7: "홍싸리", 8: "공산", 9: "국진", 10: "단풍"
}

# ==================== 디버그 설정 ====================
DEBUG_MODE = False  # 디버그 모드 (True 시 상대 카드 공개)
DEBUG_SHOW_FPS = False  # FPS 표시
