"""
플레이어 클래스
플레이어와 NPC의 기본 정보를 관리합니다.
"""

from typing import List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.card import Card


class Player:
    """플레이어 기본 클래스"""
    
    def __init__(self, name: str, money: int):
        """
        Args:
            name: 플레이어 이름
            money: 시작 자금
        """
        self.name = name
        self.money = money
        self.cards: List[Card] = []  # 현재 보유 카드
        
        # 게임 기록
        self.wins = 0  # 승리 횟수
        self.losses = 0  # 패배 횟수
        self.total_bet = 0  # 총 베팅 금액
        self.total_won = 0  # 총 획득 금액
        
        # 현재 라운드 정보
        self.current_bet = 0  # 현재 라운드 베팅 금액
        self.has_folded = False  # 다이 여부
    
    def add_card(self, card: Card):
        """카드를 받습니다."""
        self.cards.append(card)
    
    def clear_cards(self):
        """카드를 모두 제거합니다."""
        self.cards = []
    
    def bet(self, amount: int) -> bool:
        """
        베팅합니다.
        
        Args:
            amount: 베팅 금액
            
        Returns:
            성공 여부
        """
        if amount > self.money:
            return False
        
        self.money -= amount
        self.current_bet += amount
        self.total_bet += amount
        return True
    
    def win(self, amount: int):
        """판돈을 획득합니다."""
        self.money += amount
        self.total_won += amount
        self.wins += 1
    
    def lose(self):
        """패배 기록을 추가합니다."""
        self.losses += 1
    
    def fold(self):
        """다이합니다."""
        self.has_folded = True
    
    def reset_round(self):
        """라운드를 리셋합니다."""
        self.current_bet = 0
        self.has_folded = False
        self.clear_cards()
    
    def can_bet(self, amount: int) -> bool:
        """베팅 가능 여부를 확인합니다."""
        return self.money >= amount
    
    def is_bankrupt(self) -> bool:
        """파산 여부를 확인합니다."""
        return self.money <= 0
    
    def get_revealed_cards(self) -> List[Card]:
        """공개된 카드만 반환합니다."""
        return [card for card in self.cards if card.is_revealed]
    
    def get_hidden_cards(self) -> List[Card]:
        """비공개 카드만 반환합니다."""
        return [card for card in self.cards if not card.is_revealed]
    
    def reveal_card(self, index: int) -> bool:
        """
        특정 카드를 공개합니다.
        
        Args:
            index: 카드 인덱스 (0부터 시작)
            
        Returns:
            성공 여부
        """
        if 0 <= index < len(self.cards):
            self.cards[index].reveal()
            return True
        return False
    
    def reveal_all_cards(self):
        """모든 카드를 공개합니다."""
        for card in self.cards:
            card.reveal()
    
    def __str__(self) -> str:
        return f"{self.name} (자금: {self.money:,}원)"
    
    def __repr__(self) -> str:
        return f"Player(name={self.name}, money={self.money}, cards={len(self.cards)})"


class HumanPlayer(Player):
    """사람 플레이어 클래스"""
    
    def __init__(self, name: str, money: int):
        super().__init__(name, money)
        self.is_human = True


# 테스트 코드
if __name__ == "__main__":
    print("=== 플레이어 시스템 테스트 ===\n")
    
    # 플레이어 생성
    player = HumanPlayer("플레이어", 100000)
    print(f"1. 플레이어 생성: {player}")
    
    # 카드 추가
    from core.card import Card, CARD_TYPE_GWANG
    card1 = Card(1, CARD_TYPE_GWANG)
    card2 = Card(8, CARD_TYPE_GWANG)
    player.add_card(card1)
    player.add_card(card2)
    print(f"\n2. 카드 추가 후: {len(player.cards)}장")
    
    # 베팅
    print(f"\n3. 베팅 테스트:")
    print(f"   베팅 전 자금: {player.money:,}원")
    player.bet(10000)
    print(f"   10,000원 베팅 후: {player.money:,}원")
    
    # 승리
    print(f"\n4. 승리 테스트:")
    player.win(25000)
    print(f"   25,000원 획득 후: {player.money:,}원")
    print(f"   승리 횟수: {player.wins}회")
    
    # 카드 공개
    print(f"\n5. 카드 공개:")
    player.reveal_card(0)
    print(f"   공개된 카드: {len(player.get_revealed_cards())}장")
    print(f"   비공개 카드: {len(player.get_hidden_cards())}장")
    
    # 라운드 리셋
    print(f"\n6. 라운드 리셋:")
    player.reset_round()
    print(f"   리셋 후 카드: {len(player.cards)}장")
    print(f"   현재 베팅: {player.current_bet}원")
