"""
Zone 시스템
극도의 몰입 상태에서 게임 기록을 회상할 수 있는 시스템
"""

import time
from typing import List, Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    ZONE_BASE_CHANCE, ZONE_HIGH_BET_CHANCE, ZONE_SPECIAL_HAND_CHANCE,
    ZONE_DURATION
)


class GameRecord:
    """게임 기록 클래스"""
    
    def __init__(self, timestamp: float, event_type: str, data: Dict):
        """
        Args:
            timestamp: 기록 시간
            event_type: 이벤트 타입 ('card_dealt', 'bet', 'dialogue', 'reveal')
            data: 이벤트 데이터
        """
        self.timestamp = timestamp
        self.event_type = event_type
        self.data = data
    
    def __repr__(self) -> str:
        return f"GameRecord({self.event_type}, {self.data})"


class ZoneSystem:
    """Zone 시스템 클래스"""
    
    def __init__(self):
        """Zone 시스템 초기화"""
        self.is_active = False  # Zone 활성화 여부
        self.activation_time = 0.0  # Zone 활성화 시간
        self.duration = ZONE_DURATION  # Zone 지속 시간
        self.used_this_round = False  # 현재 라운드에서 사용 여부
        
        # 게임 기록
        self.round_records: List[GameRecord] = []  # 현재 라운드 기록
        self.all_records: List[List[GameRecord]] = []  # 전체 라운드 기록
        
        self.current_round = 0
    
    def check_activation_chance(self, pot_amount: int, player_bet: int, 
                                 player_money: int, is_special_hand: bool) -> float:
        """
        Zone 발동 확률을 계산합니다.
        
        Args:
            pot_amount: 현재 판돈
            player_bet: 플레이어 베팅 금액
            player_money: 플레이어 보유 금액
            is_special_hand: 특수 족보 여부
            
        Returns:
            발동 확률 (0.0 ~ 1.0)
        """
        # 이미 이번 라운드에 사용했으면 0%
        if self.used_this_round:
            return 0.0
        
        # Zone이 이미 활성화되어 있으면 0%
        if self.is_active:
            return 0.0
        
        # 특수 족보일 경우
        if is_special_hand:
            return ZONE_SPECIAL_HAND_CHANCE
        
        # 판돈의 50% 이상 베팅했을 경우
        if player_money > 0 and (pot_amount + player_bet) >= (player_money * 0.5):
            return ZONE_HIGH_BET_CHANCE
        
        # 기본 확률
        return ZONE_BASE_CHANCE
    
    def try_activate(self, pot_amount: int, player_bet: int, 
                     player_money: int, is_special_hand: bool) -> bool:
        """
        Zone 발동을 시도합니다.
        
        Args:
            pot_amount: 현재 판돈
            player_bet: 플레이어 베팅 금액
            player_money: 플레이어 보유 금액
            is_special_hand: 특수 족보 여부
            
        Returns:
            발동 성공 여부
        """
        import random
        
        chance = self.check_activation_chance(pot_amount, player_bet, 
                                              player_money, is_special_hand)
        
        if chance > 0 and random.random() < chance:
            self.activate()
            return True
        
        return False
    
    def activate(self):
        """Zone을 활성화합니다."""
        if not self.used_this_round and not self.is_active:
            self.is_active = True
            self.activation_time = time.time()
            self.used_this_round = True
            self.record_event('zone_activated', {
                'round': self.current_round,
                'time': self.activation_time
            })
    
    def deactivate(self):
        """Zone을 비활성화합니다."""
        self.is_active = False
        self.activation_time = 0.0
    
    def is_expired(self) -> bool:
        """Zone 시간이 만료되었는지 확인합니다."""
        if not self.is_active:
            return False
        
        elapsed_time = time.time() - self.activation_time
        return elapsed_time >= self.duration
    
    def get_remaining_time(self) -> float:
        """남은 Zone 시간을 반환합니다."""
        if not self.is_active:
            return 0.0
        
        elapsed_time = time.time() - self.activation_time
        remaining = self.duration - elapsed_time
        return max(0.0, remaining)
    
    def update(self):
        """Zone 상태를 업데이트합니다 (매 프레임 호출)."""
        if self.is_active and self.is_expired():
            self.deactivate()
    
    def record_event(self, event_type: str, data: Dict):
        """
        이벤트를 기록합니다.
        
        Args:
            event_type: 이벤트 타입
            data: 이벤트 데이터
        """
        record = GameRecord(time.time(), event_type, data)
        self.round_records.append(record)
    
    def get_round_records(self) -> List[GameRecord]:
        """현재 라운드의 기록을 반환합니다."""
        return self.round_records.copy()
    
    def get_all_records(self) -> List[List[GameRecord]]:
        """전체 라운드의 기록을 반환합니다."""
        return self.all_records.copy()
    
    def get_records_by_type(self, event_type: str) -> List[GameRecord]:
        """특정 타입의 기록만 반환합니다."""
        return [r for r in self.round_records if r.event_type == event_type]
    
    def start_new_round(self, round_number: int):
        """
        새 라운드를 시작합니다.
        
        Args:
            round_number: 라운드 번호
        """
        # 이전 라운드 기록 저장
        if self.round_records:
            self.all_records.append(self.round_records.copy())
        
        # 현재 라운드 초기화
        self.round_records = []
        self.used_this_round = False
        self.current_round = round_number
        self.deactivate()
        
        self.record_event('round_start', {'round': round_number})
    
    def end_round(self):
        """라운드를 종료합니다."""
        self.record_event('round_end', {'round': self.current_round})
        self.deactivate()
    
    def reset(self):
        """Zone 시스템을 초기화합니다."""
        self.is_active = False
        self.activation_time = 0.0
        self.used_this_round = False
        self.round_records = []
        self.all_records = []
        self.current_round = 0
    
    def can_use_zone(self) -> bool:
        """Zone을 사용할 수 있는지 확인합니다."""
        return not self.used_this_round and not self.is_active
    
    def get_summary(self) -> Dict:
        """Zone 시스템 상태 요약을 반환합니다."""
        return {
            'is_active': self.is_active,
            'remaining_time': self.get_remaining_time() if self.is_active else 0.0,
            'used_this_round': self.used_this_round,
            'can_use': self.can_use_zone(),
            'current_round': self.current_round,
            'total_rounds_recorded': len(self.all_records),
            'current_round_events': len(self.round_records)
        }
    
    def __str__(self) -> str:
        status = "활성화" if self.is_active else "비활성화"
        remaining = f" (남은 시간: {self.get_remaining_time():.1f}초)" if self.is_active else ""
        return f"Zone: {status}{remaining}"


# 테스트 코드
if __name__ == "__main__":
    print("=== Zone 시스템 테스트 ===\n")
    
    zone = ZoneSystem()
    
    # 1. 초기 상태
    print("1. 초기 상태:")
    print(f"   {zone}")
    print(f"   Zone 사용 가능: {zone.can_use_zone()}")
    print(f"   상태 요약: {zone.get_summary()}")
    
    # 2. 라운드 시작
    print("\n2. 라운드 1 시작:")
    zone.start_new_round(1)
    
    # 3. 이벤트 기록
    print("\n3. 이벤트 기록:")
    zone.record_event('card_dealt', {'player': 'NPC', 'card': '1월 광'})
    zone.record_event('bet', {'player': 'Player', 'amount': 5000})
    zone.record_event('dialogue', {'player': 'NPC', 'text': '좋은 패네...'})
    print(f"   기록된 이벤트: {len(zone.round_records)}개")
    
    # 4. Zone 발동 확률 체크
    print("\n4. Zone 발동 확률:")
    prob1 = zone.check_activation_chance(10000, 5000, 100000, False)
    print(f"   기본: {prob1*100:.1f}%")
    
    prob2 = zone.check_activation_chance(50000, 50000, 100000, False)
    print(f"   판돈 50% 이상: {prob2*100:.1f}%")
    
    prob3 = zone.check_activation_chance(10000, 5000, 100000, True)
    print(f"   특수 족보: {prob3*100:.1f}%")
    
    # 5. Zone 활성화
    print("\n5. Zone 강제 활성화:")
    zone.activate()
    print(f"   {zone}")
    print(f"   남은 시간: {zone.get_remaining_time():.1f}초")
    print(f"   다시 사용 가능: {zone.can_use_zone()}")
    
    # 6. Zone 비활성화
    print("\n6. Zone 비활성화:")
    zone.deactivate()
    print(f"   {zone}")
    
    # 7. 라운드 종료
    print("\n7. 라운드 종료:")
    zone.end_round()
    
    # 8. 다음 라운드
    print("\n8. 라운드 2 시작:")
    zone.start_new_round(2)
    print(f"   Zone 사용 가능: {zone.can_use_zone()}")
    print(f"   저장된 이전 라운드: {len(zone.all_records)}개")
