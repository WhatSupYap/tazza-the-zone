"""
NPC AI 시스템
NPC의 능력치, 멘탈, 분노를 관리하고 배팅 의사결정을 수행합니다.
"""

import random
from typing import List, Dict, Optional, Tuple
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    NPC_STAT_MIN, NPC_STAT_MAX,
    MENTAL_START, MENTAL_THRESHOLD, MENTAL_DECREASE_MIN, MENTAL_DECREASE_MAX,
    ANGER_START, ANGER_THRESHOLD
)
from core.player import Player
from core.card import Card


class NPCPlayer(Player):
    """NPC 플레이어 클래스"""
    
    def __init__(self, name: str, money: int, composure: int, deception: int,
                 boldness: int, recovery: int):
        """
        Args:
            name: NPC 이름
            money: 시작 자금
            composure: 침착성 (1~10)
            deception: 말빨/기만 (1~10)
            boldness: 배짱 (1~10)
            recovery: 멘탈 회복력 (1~10)
        """
        super().__init__(name, money)
        
        # 기본 능력치
        self.base_composure = self._validate_stat(composure)
        self.base_deception = self._validate_stat(deception)
        self.base_boldness = self._validate_stat(boldness)
        self.base_recovery = self._validate_stat(recovery)
        
        # 현재 능력치 (멘탈에 따라 변동)
        self.composure = self.base_composure
        self.deception = self.base_deception
        self.boldness = self.base_boldness
        self.recovery = self.base_recovery
        
        # 실시간 변동 수치
        self.mental = MENTAL_START
        self.anger = ANGER_START
        
        # 페르소나
        self.persona = ""
        self.catchphrase = ""
        
        self.is_human = False
    
    def _validate_stat(self, value: int) -> int:
        """능력치가 유효한 범위인지 확인합니다."""
        return max(NPC_STAT_MIN, min(NPC_STAT_MAX, value))
    
    def update_stats(self):
        """멘탈 상태에 따라 능력치를 업데이트합니다."""
        if self.mental <= MENTAL_THRESHOLD:
            # 멘탈이 임계점 이하일 때 능력치 반감
            self.composure = self.base_composure // 2
            self.deception = self.base_deception // 2
            self.boldness = self.base_boldness // 2
        else:
            # 정상 상태
            self.composure = self.base_composure
            self.deception = self.base_deception
            self.boldness = self.base_boldness
        
        self.recovery = self.base_recovery
    
    def on_defeat(self):
        """패배 시 멘탈과 분노를 업데이트합니다."""
        # 멘탈 감소
        mental_decrease = random.randint(MENTAL_DECREASE_MIN, MENTAL_DECREASE_MAX)
        self.mental = max(0, self.mental - mental_decrease)
        
        # 분노 증가
        anger_increase = random.randint(1, 5) * ((10 - self.composure) * 0.5)
        self.anger = min(100, self.anger + anger_increase)
        
        # 능력치 업데이트
        self.update_stats()
        
        # 패배 기록
        self.lose()
    
    def on_victory(self):
        """승리 시 분노를 감소시킵니다."""
        anger_decrease = random.randint(1, 5)
        self.anger = max(0, self.anger - anger_decrease)
    
    def recover_mental(self):
        """라운드 종료 시 멘탈을 회복합니다."""
        recovery_amount = self.recovery * 2
        self.mental = min(MENTAL_START, self.mental + recovery_amount)
        
        # 분노도 회복력만큼 감소
        self.anger = max(0, self.anger - self.recovery)
        
        self.update_stats()
    
    def can_calculate_opponent_hand(self) -> bool:
        """상대 패를 계산할 수 있는지 확인합니다."""
        # 침착성이 낮으면 일정 확률로 계산 못함
        calculation_chance = self.composure / 10.0
        return random.random() < calculation_chance
    
    def should_speak(self) -> bool:
        """발언할지 여부를 결정합니다."""
        # 기만 능력치가 높으면 말을 많이 함
        speak_chance = self.deception / 10.0
        return random.random() < speak_chance
    
    def get_max_bet_limit(self) -> float:
        """베팅 금액 상한선을 반환합니다."""
        # 분노가 임계점 초과 시 상한선 무시
        if self.anger > ANGER_THRESHOLD:
            return float('inf')
        
        # 배짱 수치에 따른 상한선 (배짱 * 10%)
        return self.money * (self.boldness / 10.0)
    
    def calculate_win_probability(self, my_hand: Dict, opponent_visible_cards: List[Card],
                                  pot_amount: int) -> float:
        """
        승률을 계산합니다.
        
        Args:
            my_hand: 내 족보 정보
            opponent_visible_cards: 상대 공개 카드
            pot_amount: 현재 판돈
            
        Returns:
            승률 (0.0 ~ 1.0)
        """
        # 상대 패를 계산할 수 없으면 자신의 패만 보고 판단
        if not self.can_calculate_opponent_hand():
            # 자신의 족보 랭크만으로 단순 판단
            if my_hand['rank'] <= 3:  # 삼팔광땡, 광땡, 땡
                return 0.8
            elif my_hand['rank'] <= 6:  # 특수 조합
                return 0.6
            elif my_hand['rank'] == 10:  # 끗
                return 0.3 + (my_hand['score'] * 0.05)  # 끗수에 따라
            else:  # 망통
                return 0.1
        
        # 상대 패를 계산할 수 있으면 더 정확한 판단
        # (실제로는 더 복잡한 로직이 필요하지만, 기본 구현)
        
        # 상대 공개 카드로 추정
        if len(opponent_visible_cards) > 0:
            # 상대가 광을 공개했으면 광땡 가능성
            from config import CARD_TYPE_GWANG
            if any(card.card_type == CARD_TYPE_GWANG for card in opponent_visible_cards):
                # 내가 광땡 이상이 아니면 승률 낮춤
                if my_hand['rank'] > 2:
                    return 0.3
        
        # 기본 승률 계산
        base_prob = 0.5
        
        # 내 족보에 따른 보정
        if my_hand['rank'] == 1:  # 삼팔광땡
            base_prob = 0.95
        elif my_hand['rank'] == 2:  # 광땡
            base_prob = 0.85
        elif my_hand['rank'] == 3:  # 땡
            base_prob = 0.7 + (my_hand['score'] * 0.02)
        elif my_hand['rank'] <= 9:  # 특수 조합
            base_prob = 0.6
        elif my_hand['rank'] == 10:  # 끗
            base_prob = 0.3 + (my_hand['score'] * 0.05)
        else:  # 망통
            base_prob = 0.1
        
        return base_prob
    
    def choose_card_to_reveal(self, opponent_cards: List[Card]) -> int:
        """
        공개할 카드를 선택합니다.
        
        Args:
            opponent_cards: 상대방의 카드 (공개된 카드 확인용)
            
        Returns:
            공개할 카드의 인덱스 (0, 1, 2)
        """
        # 상대방이 공개한 카드 확인
        opponent_revealed = [card for card in opponent_cards if card.is_revealed]
        
        # 자신의 카드 평가
        card_values = []
        for i, card in enumerate(self.cards):
            # 카드 가치 계산 (월 숫자가 높을수록 좋은 카드로 간주)
            value = card.month
            
            # 광 카드는 가치 높음
            if card.card_type == 'gwang':
                value += 10
            # 띠 카드는 중간
            elif card.card_type == 'tti':
                value += 5
            
            card_values.append((i, value))
        
        # 성격에 따른 전략
        if self.deception >= 7 and self.boldness >= 7:
            # 기만과 대담이 높으면: 가장 약한 카드 공개 (블러핑)
            card_values.sort(key=lambda x: x[1])
            return card_values[0][0]
        elif self.composure >= 7:
            # 침착이 높으면: 중간 정도 카드 공개 (안정적)
            card_values.sort(key=lambda x: x[1])
            return card_values[1][0]
        else:
            # 기본: 가장 좋은 카드 공개
            card_values.sort(key=lambda x: x[1], reverse=True)
            return card_values[0][0]
    
    def decide_bet_action(self, my_hand: Dict, opponent_visible_cards: List[Card],
                         pot_amount: int, opponent_last_bet: int, 
                         is_first_bet: bool) -> Tuple[str, int]:
        """
        베팅 행동을 결정합니다.
        
        Args:
            my_hand: 내 족보 정보
            opponent_visible_cards: 상대 공개 카드
            pot_amount: 현재 판돈
            opponent_last_bet: 상대가 나보다 많이 베팅한 금액 (콜해야 하는 금액)
            is_first_bet: 첫 베팅 여부
            
        Returns:
            (행동, 금액) 튜플
            행동: 'die', 'check', 'pping', 'half', 'call', 'allin'
        """
        # 승률 계산
        win_prob = self.calculate_win_probability(my_hand, opponent_visible_cards, pot_amount)
        
        # 베팅 상한선
        max_bet = self.get_max_bet_limit()
        
        # 하프 금액
        half_amount = pot_amount // 2
        
        # 돈이 하프보다 적으면 올인만 가능
        if self.money <= half_amount:
            if win_prob >= 0.5:
                return ('allin', self.money)
            elif win_prob >= 0.3:
                return ('call', min(opponent_last_bet, self.money))
            else:
                return ('die', 0)
        
        # 승률에 따른 행동 결정
        if win_prob >= 0.8:
            # 매우 높은 승률: 공격적 베팅
            if opponent_last_bet > 0:
                # 상대방이 베팅했으면 콜만 가능 (하프는 불가능)
                return ('call', min(opponent_last_bet, self.money))
            else:
                # 상대방이 베팅하지 않았으면 하프 또는 삥
                if half_amount <= max_bet and half_amount <= self.money:
                    return ('half', half_amount)
                else:
                    from config import DEFAULT_MIN_BET
                    return ('pping', DEFAULT_MIN_BET)
        
        elif win_prob >= 0.6:
            # 높은 승률: 적당히 베팅
            if opponent_last_bet == 0:
                from config import DEFAULT_MIN_BET
                return ('pping', DEFAULT_MIN_BET)
            else:
                return ('call', min(opponent_last_bet, self.money))
        
        elif win_prob >= 0.4:
            # 중간 승률: 소극적
            if opponent_last_bet == 0:
                return ('check', 0)
            elif opponent_last_bet <= self.money * 0.1:  # 작은 금액이면 콜
                return ('call', opponent_last_bet)
            else:
                return ('die', 0)
        
        else:
            # 낮은 승률: 매우 소극적 또는 다이
            if opponent_last_bet == 0:
                return ('check', 0)
            else:
                # 배짱이 높거나 분노가 높으면 블러핑 시도
                if self.boldness >= 7 or self.anger > ANGER_THRESHOLD:
                    if random.random() < 0.3:  # 30% 확률로 블러핑
                        return ('call', min(opponent_last_bet, self.money))
                
                return ('die', 0)
    
    def get_dialogue_context(self, situation: str) -> Dict:
        """
        LLM에 전달할 대화 컨텍스트를 생성합니다.
        
        Args:
            situation: 상황 ('card_received', 'betting', 'result')
            
        Returns:
            컨텍스트 딕셔너리
        """
        return {
            'name': self.name,
            'persona': self.persona,
            'situation': situation,
            'mental': self.mental,
            'anger': self.anger,
            'composure': self.composure,
            'deception': self.deception,
            'boldness': self.boldness,
            'money': self.money,
            'wins': self.wins,
            'losses': self.losses
        }
    
    def get_fallback_dialogue(self, situation: str) -> str:
        """
        LLM 실패 시 사용할 기본 대사를 반환합니다.
        
        Args:
            situation: 상황
            
        Returns:
            대사
        """
        dialogues = {
            'card_received': [
                "흠...",
                "이거 괜찮은데?",
                "뭐야 이게...",
                "오, 좋아!",
                "그럭저럭이군."
            ],
            'betting': [
                "한 번 가볼까?",
                "따라올 수 있겠어?",
                "이 정도면 충분하지.",
                "더 올려볼까?",
                "체크!"
            ],
            'result_win': [
                "역시 내가 이겼군.",
                "이게 실력이지!",
                "당연한 결과야.",
                "다음에 또 하자고.",
                "운이 좋았어."
            ],
            'result_lose': [
                "젠장...",
                "이럴 수가...",
                "다음엔 내가 이긴다.",
                "실수했어.",
                "...인정하지."
            ]
        }
        
        # 멘탈과 분노 상태에 따라 대사 선택
        if self.mental <= MENTAL_THRESHOLD:
            if situation == 'betting':
                return random.choice(["...체크.", "패스.", "..."])
            elif situation == 'result_lose':
                return random.choice(["...너무 힘들어.", "정신이 없어.", "..."])
        
        if self.anger > ANGER_THRESHOLD:
            if situation == 'betting':
                return random.choice(["올인이다!", "다 걸어!", "덤벼라!"])
            elif situation == 'result_lose':
                return random.choice(["이딴 게임!", "말도 안 돼!", "다시 한 판!"])
        
        return random.choice(dialogues.get(situation, ["..."]))
    
    def __str__(self) -> str:
        return (f"{self.name} (자금: {self.money:,}원, "
                f"멘탈: {self.mental}, 분노: {self.anger})")


# 테스트 코드
if __name__ == "__main__":
    print("=== NPC AI 시스템 테스트 ===\n")
    
    # NPC 생성
    npc = NPCPlayer(
        name="고니",
        money=100000,
        composure=7,
        deception=8,
        boldness=6,
        recovery=5
    )
    npc.persona = "대학 시절 타짜였던 노련한 플레이어"
    npc.catchphrase = "대학 시절 타짜였지."
    
    print(f"1. NPC 생성: {npc}")
    print(f"   침착성: {npc.composure}")
    print(f"   기만: {npc.deception}")
    print(f"   배짱: {npc.boldness}")
    print(f"   회복력: {npc.recovery}")
    
    # 승률 계산
    print("\n2. 승률 계산:")
    from core.hand_evaluator import HandEvaluator
    from core.card import Card, CARD_TYPE_GWANG
    
    test_hand = {'rank': 2, 'name': '광땡', 'score': 8}
    win_prob = npc.calculate_win_probability(test_hand, [], 10000)
    print(f"   광땡 승률: {win_prob*100:.1f}%")
    
    # 베팅 결정
    print("\n3. 베팅 결정:")
    action, amount = npc.decide_bet_action(test_hand, [], 10000, 5000, False)
    print(f"   행동: {action}, 금액: {amount:,}원")
    
    # 패배 처리
    print("\n4. 패배 처리:")
    print(f"   패배 전 멘탈: {npc.mental}, 분노: {npc.anger}")
    npc.on_defeat()
    print(f"   패배 후 멘탈: {npc.mental}, 분노: {npc.anger}")
    print(f"   능력치 변화: 침착성 {npc.composure}")
    
    # 멘탈 회복
    print("\n5. 멘탈 회복:")
    npc.recover_mental()
    print(f"   회복 후 멘탈: {npc.mental}, 분노: {npc.anger}")
    
    # 대화
    print("\n6. 대화 생성:")
    dialogue = npc.get_fallback_dialogue('betting')
    print(f"   대사: \"{dialogue}\"")
