"""
카드 및 덱 시스템
화투 카드를 표현하고 덱을 관리합니다.
"""

import random
from typing import List, Optional
import sys
import os

# 상위 디렉토리의 config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    HWATU_CARDS, CARD_NAMES, CARD_TYPE_CODES,
    CARD_TYPE_GWANG, CARD_TYPE_TTI, CARD_TYPE_YEOLKKUT,
    CARDS_PATH
)


class Card:
    """화투 카드 클래스"""
    
    def __init__(self, month: int, card_type: str):
        """
        Args:
            month: 월 (1~10)
            card_type: 카드 타입 ('gwang', 'tti', 'yeolkkut')
        """
        if month not in range(1, 11):
            raise ValueError(f"월은 1~10 사이여야 합니다: {month}")
        
        if card_type not in [CARD_TYPE_GWANG, CARD_TYPE_TTI, CARD_TYPE_YEOLKKUT]:
            raise ValueError(f"올바르지 않은 카드 타입: {card_type}")
        
        # 해당 월에 해당 타입의 카드가 존재하는지 확인
        if card_type not in HWATU_CARDS[month]:
            raise ValueError(f"{month}월에는 {card_type} 타입이 없습니다")
        
        self.month = month
        self.card_type = card_type
        self.is_revealed = False  # 공개 여부
    
    def reveal(self):
        """카드를 공개합니다."""
        self.is_revealed = True
    
    def hide(self):
        """카드를 숨깁니다."""
        self.is_revealed = False
    
    def get_image_path(self) -> str:
        """카드 이미지 경로를 반환합니다."""
        type_code = CARD_TYPE_CODES[self.card_type]
        return f"{CARDS_PATH}/{self.month}{type_code}.png"
    
    def __str__(self) -> str:
        """카드를 문자열로 표현합니다."""
        type_name = {
            CARD_TYPE_GWANG: "광",
            CARD_TYPE_TTI: "띠",
            CARD_TYPE_YEOLKKUT: "열끗"
        }
        card_name = CARD_NAMES[self.month]
        revealed = "공개" if self.is_revealed else "비공개"
        return f"{card_name}({self.month}월) {type_name[self.card_type]} [{revealed}]"
    
    def __repr__(self) -> str:
        return f"Card({self.month}, {self.card_type}, revealed={self.is_revealed})"
    
    def __eq__(self, other) -> bool:
        """카드 동등성 비교 (월과 타입만 비교)"""
        if not isinstance(other, Card):
            return False
        return self.month == other.month and self.card_type == other.card_type
    
    def __hash__(self) -> int:
        """해시 값 반환 (set, dict 사용을 위해)"""
        return hash((self.month, self.card_type))


class Deck:
    """화투 덱 클래스 (20장)"""
    
    def __init__(self):
        """덱을 생성하고 초기화합니다."""
        self.cards: List[Card] = []
        self._initialize_deck()
    
    def _initialize_deck(self):
        """덱을 초기화합니다 (20장 생성)."""
        self.cards = []
        for month in range(1, 11):
            for card_type in HWATU_CARDS[month]:
                self.cards.append(Card(month, card_type))
    
    def shuffle(self):
        """덱을 섞습니다."""
        random.shuffle(self.cards)
    
    def draw(self) -> Optional[Card]:
        """
        카드를 한 장 뽑습니다.
        
        Returns:
            뽑은 카드 (덱이 비어있으면 None)
        """
        if len(self.cards) == 0:
            return None
        return self.cards.pop()
    
    def draw_multiple(self, count: int) -> List[Card]:
        """
        카드를 여러 장 뽑습니다.
        
        Args:
            count: 뽑을 카드 수
            
        Returns:
            뽑은 카드 리스트
        """
        drawn_cards = []
        for _ in range(count):
            card = self.draw()
            if card:
                drawn_cards.append(card)
        return drawn_cards
    
    def reset(self):
        """덱을 초기화하고 섞습니다."""
        self._initialize_deck()
        self.shuffle()
    
    def remaining_count(self) -> int:
        """남은 카드 수를 반환합니다."""
        return len(self.cards)
    
    def __len__(self) -> int:
        """덱의 카드 수를 반환합니다."""
        return len(self.cards)
    
    def __str__(self) -> str:
        return f"Deck(남은 카드: {len(self.cards)}장)"
    
    def __repr__(self) -> str:
        return f"Deck(cards={len(self.cards)})"


def get_card_image_path(month: int, card_type: str) -> str:
    """
    카드 이미지 경로를 반환합니다.
    
    Args:
        month: 월 (1~10)
        card_type: 카드 타입 ('gwang', 'tti', 'yeolkkut')
        
    Returns:
        카드 이미지 경로
    """
    type_code = CARD_TYPE_CODES[card_type]
    return f"{CARDS_PATH}/{month}{type_code}.png"


def get_card_back_path() -> str:
    """카드 뒷면 이미지 경로를 반환합니다."""
    return f"{CARDS_PATH}/back.png"


# 테스트 코드
if __name__ == "__main__":
    print("=== 카드 시스템 테스트 ===\n")
    
    # 카드 생성 테스트
    print("1. 카드 생성:")
    card1 = Card(1, CARD_TYPE_GWANG)
    print(f"  {card1}")
    
    card2 = Card(8, CARD_TYPE_GWANG)
    card2.reveal()
    print(f"  {card2}")
    
    # 덱 생성 및 섞기 테스트
    print("\n2. 덱 생성 및 섞기:")
    deck = Deck()
    print(f"  초기 덱: {deck}")
    deck.shuffle()
    print(f"  섞은 후: {deck}")
    
    # 카드 뽑기 테스트
    print("\n3. 카드 뽑기:")
    for i in range(5):
        card = deck.draw()
        if card:
            print(f"  {i+1}번째: {card}")
    
    print(f"\n  남은 카드: {deck.remaining_count()}장")
    
    # 덱 리셋 테스트
    print("\n4. 덱 리셋:")
    deck.reset()
    print(f"  리셋 후: {deck}")
