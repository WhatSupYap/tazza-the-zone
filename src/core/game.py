"""
게임 메인 로직
섯다 게임의 전체 진행을 관리합니다.
"""

import time
from typing import List, Dict, Optional, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DEFAULT_ROUNDS, DEFAULT_START_MONEY, DEFAULT_MIN_BET, DEFAULT_BET_TIME,
    CARD_TYPE_PRIORITY
)
from core.card import Card, Deck
from core.hand_evaluator import HandEvaluator
from core.player import Player, HumanPlayer
from core.zone import ZoneSystem
from ai.npc import NPCPlayer
from ai.llm_handler import LLMHandler


class GameState:
    """게임 상태"""
    OPENING = 'opening'
    MAIN_TITLE = "main_title"
    CHOICE_NPC = "choice_npc"
    CARD_SELECTION = "card_selection"  # 카드 선택 단계
    PLAYING = "playing"
    BETTING = "betting"
    SHOWDOWN = "showdown"
    ROUND_END = "round_end"
    GAME_OVER = "game_over"
    ZONE_ACTIVE = "zone_active"


class BetAction:
    """베팅 행동"""
    DIE = "die"
    CHECK = "check"
    PPING = "pping"
    HALF = "half"
    CALL = "call"
    ALLIN = "allin"


class SutdaGame:
    """섯다 게임 메인 클래스"""
    
    def __init__(self, player_name: str = "플레이어", 
                 npc: Optional[NPCPlayer] = None):
        """
        게임을 초기화합니다.
        
        Args:
            player_name: 플레이어 이름
            npc: NPC 플레이어 (None이면 기본 NPC 생성)
        """
        # 플레이어 생성
        self.player = HumanPlayer(player_name, DEFAULT_START_MONEY)
        
        # NPC 생성 또는 할당
        if npc is None:
            self.npc = NPCPlayer(
                name="고니",
                money=DEFAULT_START_MONEY,
                composure=7,
                deception=8,
                boldness=6,
                recovery=5
            )
            self.npc.persona = "대학 시절 타짜였던 노련한 플레이어"
            self.npc.catchphrase = "대학 시절 타짜였지."
        else:
            self.npc = npc
        
        # 게임 설정
        self.total_rounds = DEFAULT_ROUNDS
        self.current_round = 0
        self.min_bet = DEFAULT_MIN_BET
        self.bet_time_limit = DEFAULT_BET_TIME
        
        # 게임 상태
        self.state = GameState.MAIN_TITLE
        self.deck = Deck()
        self.pot = 0  # 판돈
        self.carried_pot = 0  # 무승부로 이월된 판돈
        self.first_player = None  # 선 (먼저 베팅하는 사람)
        self.last_winner = None  # 마지막 라운드 승자
        
        # 베팅 관련 - 새로운 턴 기반 시스템
        self.betting_process_this_round = {
            'first_player': None,  # 선 플레이어
            'players': [],  # 베팅 순서 ['플레이어', 'NPC'] or ['NPC', '플레이어']
            'current_turn_index': 0,  # 현재 턴 인덱스
            'bet_history': []  # 베팅 히스토리
        }
        self.betting_phase = 0  # 0: 1차, 1: 2차
        self.player_current_bet = 0  # 플레이어가 현재 베팅 페이즈에서 베팅한 총액
        self.npc_current_bet = 0  # NPC가 현재 베팅 페이즈에서 베팅한 총액
        
        # 레거시 필드 (하위 호환성)
        self.betting_round_count = 0
        self.last_bet_amount = 0
        self.last_bet_player = None
        self.check_count = 0
        self.player_has_acted = False
        self.npc_has_acted = False
        self.bet_history = []
        
        # 시스템
        self.zone = ZoneSystem()
        self.llm = LLMHandler()
        self.evaluator = HandEvaluator()
        
        # 현재 족보
        self.player_hand = None
        self.npc_hand = None
        
        # 카드 조합 (쇼다운에서 사용)
        self.player_combinations = []
        self.npc_combinations = []
        self.player_selected_combo_index = None  # 플레이어가 선택한 조합 인덱스
        self.npc_selected_combo_index = None  # NPC가 선택한 조합 인덱스
    
    def start_new_game(self):
        """새 게임을 시작합니다."""
        self.current_round = 0
        self.player.money = DEFAULT_START_MONEY
        self.npc.money = DEFAULT_START_MONEY
        self.player.wins = 0
        self.player.losses = 0
        self.npc.wins = 0
        self.npc.losses = 0
        self.zone.reset()
        self.state = GameState.PLAYING
        
        # 첫 라운드 시작
        self.start_new_round()
    
    def start_new_round(self):
        """새 라운드를 시작합니다."""
        self.current_round += 1
        
        # 라운드 초기화
        self.player.reset_round()
        self.npc.reset_round()
        
        # 무승부로 이월된 판돈이 있으면 유지, 없으면 0으로 초기화
        if self.carried_pot > 0:
            self.pot = self.carried_pot
            self.carried_pot = 0  # 이월 판돈 초기화
            print(f"\n이전 라운드 무승부로 {self.pot:,}원이 묻혔습니다!")
        else:
            self.pot = 0
            
            # 기본 판돈 (ante): 각 플레이어가 최소 베팅액을 판돈에 넣음
            ante = self.min_bet
            if self.player.bet(ante):
                self.pot += ante
            if self.npc.bet(ante):
                self.pot += ante
            print(f"\n기본 판돈: {self.pot:,}원 (각자 {ante:,}원씩)")

        
        self.last_bet_amount = 0
        self.last_bet_player = None
        self.betting_phase = 0
        self.betting_round_count = 0
        self.check_count = 0
        self.bet_history = []  # 베팅 히스토리 초기화
        self.player_current_bet = 0  # 현재 베팅 페이즈 베팅액 초기화
        self.npc_current_bet = 0  # 현재 베팅 페이즈 베팅액 초기화
        self.player_has_acted = False
        self.npc_has_acted = False
        
        # 덱 초기화
        self.deck.reset()
        
        # Zone 시스템 라운드 시작
        self.zone.start_new_round(self.current_round)
        
        # 선 결정 (먼저!)
        self._determine_first_player()
        
        # 새로운 베팅 프로세스 초기화 (first_player 결정 후!)
        self._init_betting_process()
        
        # 카드 배분 (1-2장)
        self._deal_initial_cards()
        
        # 카드 선택 단계로 이동
        self.state = GameState.CARD_SELECTION
        
        print(f"\n{'='*50}")
        print(f"라운드 {self.current_round}/{self.total_rounds}")
        print(f"{'='*50}")
        print(f"선: {self.first_player.name}")
        print(f"{self.player.name}: {self.player.money:,}원")
        print(f"{self.npc.name}: {self.npc.money:,}원")
    
    def _determine_first_player(self):
        """선을 결정합니다."""
        if self.current_round == 1:
            # 첫 판: 랜덤 카드로 결정
            temp_deck = Deck()
            temp_deck.shuffle()
            
            player_card = temp_deck.draw()
            npc_card = temp_deck.draw()
            
            # 월 비교
            if player_card.month > npc_card.month:
                self.first_player = self.player
            elif player_card.month < npc_card.month:
                self.first_player = self.npc
            else:
                # 같은 월: 타입 우선순위로 비교
                player_priority = CARD_TYPE_PRIORITY[player_card.card_type]
                npc_priority = CARD_TYPE_PRIORITY[npc_card.card_type]
                
                if player_priority > npc_priority:
                    self.first_player = self.player
                else:
                    self.first_player = self.npc
        else:
            # 2판 이후: 이전 판 승자가 선
            if self.player.wins > self.npc.wins:
                last_winner = self.player
            elif self.npc.wins > self.player.wins:
                last_winner = self.npc
            else:
                # 동점이면 이전 선 유지
                last_winner = self.first_player
            
            self.first_player = last_winner
    
    def _init_betting_process(self):
        """베팅 프로세스를 초기화합니다."""
        # first_player가 None이면 에러
        if self.first_player is None:
            raise ValueError("first_player가 설정되지 않았습니다. _determine_first_player()를 먼저 호출하세요.")
        
        # first_player 기준으로 베팅 순서 설정
        if self.first_player == self.player:
            players_order = [self.player.name, self.npc.name]
        else:
            players_order = [self.npc.name, self.player.name]
        
        self.betting_process_this_round = {
            'first_player': self.first_player.name,
            'players': players_order,
            'current_turn_index': 0,
            'bet_history': []
        }
        
        print(f"DEBUG: 베팅 프로세스 초기화 - 선: {self.first_player.name}, 순서: {players_order}")
    
    def get_current_turn_player(self):
        """현재 턴 플레이어를 반환합니다."""
        if not self.betting_process_this_round['players']:
            return None
        
        player_name = self.betting_process_this_round['players'][
            self.betting_process_this_round['current_turn_index']
        ]
        
        return self.player if player_name == self.player.name else self.npc
    
    def is_player_turn(self):
        """현재 플레이어 턴인지 확인합니다."""
        current_player = self.get_current_turn_player()
        return current_player == self.player
    
    def advance_turn(self):
        """다음 턴으로 넘깁니다."""
        self.betting_process_this_round['current_turn_index'] = (
            self.betting_process_this_round['current_turn_index'] + 1
        ) % len(self.betting_process_this_round['players'])
        
        next_player = self.get_current_turn_player()
        print(f"DEBUG: 턴 전환 → {next_player.name}의 차례")
    
    def start_new_betting_phase(self, phase: int):
        """새로운 베팅 페이즈를 시작합니다."""
        self.betting_phase = phase
        self.player_current_bet = 0
        self.npc_current_bet = 0
        self.check_count = 0
        self.player_has_acted = False
        self.npc_has_acted = False
        
        # 턴 인덱스를 first_player로 리셋
        self.betting_process_this_round['current_turn_index'] = 0
        
        print(f"DEBUG: {phase + 1}차 베팅 시작 - {self.get_current_turn_player().name}부터")
    
    def _deal_initial_cards(self):

        self.player_has_acted = False

        """초기 카드 2장을 배분합니다."""
        # 플레이어에게 2장
        for _ in range(2):
            card = self.deck.draw()
            self.player.add_card(card)
        
        # NPC에게 2장
        for _ in range(2):
            card = self.deck.draw()
            self.npc.add_card(card)
        
        # Zone 기록
        self.zone.record_event('cards_dealt', {
            'round': self.current_round,
            'player_cards': [str(c) for c in self.player.cards],
            'npc_cards': [str(c) for c in self.npc.cards]
        })
        
        # # NPC 발화
        # if self.npc.should_speak():
        #     dialogue = self.llm.generate_dialogue(self)
        #     print(f"\n{self.npc.name}: \"{dialogue}\"")
            
        #     self.zone.record_event('npc_dialogue', {
        #         'situation': 'card_received',
        #         'text': dialogue
        #     })
    
    def deal_third_card(self):
        """3번째 카드를 배분합니다 (1차 베팅 후)."""
        # 이미 3장 이상이면 배분하지 않음
        if len(self.player.cards) >= 3:
            print("이미 3장의 카드를 보유하고 있습니다.")
            return
        
        # 플레이어에게 1장
        card = self.deck.draw()
        self.player.add_card(card)
        
        # NPC에게 1장
        card = self.deck.draw()
        self.npc.add_card(card)
        
        # 2차 베팅 시작
        self.start_new_betting_phase(1)
        
        # Zone 기록
        self.zone.record_event('third_card_dealt', {
            'round': self.current_round,
            'player_cards': [str(c) for c in self.player.cards],
            'npc_cards': [str(c) for c in self.npc.cards]
        })
        
        print(f"\n3번째 카드가 배분되었습니다.")
        print(f"2차 베팅을 시작합니다!")
        
        # # NPC 발화
        # if self.npc.should_speak():
        #     dialogue = self.llm.generate_dialogue(
        #         self.npc.get_dialogue_context('third_card')
        #     )
        #     print(f"{self.npc.name}: \"{dialogue}\"")
            
        #     self.zone.record_event('npc_dialogue', {
        #         'situation': 'third_card',
        #         'text': dialogue
        #     })
    
    def reveal_one_card(self, player: Player, card_index: int):
        """카드 1장을 공개합니다."""
        if player.reveal_card(card_index):
            revealed_card = player.cards[card_index]
            
            self.zone.record_event('card_revealed', {
                'player': player.name,
                'card': str(revealed_card),
                'card_index': card_index
            })
            
            return True
        return False
    
    def start_first_betting(self):
        """1차 베팅을 시작합니다."""
        self.betting_phase = 0
        self.betting_round_count = 0
        self.check_count = 0
        self.player_has_acted = False
        self.npc_has_acted = False
        self.state = GameState.BETTING
        
        print(f"\n--- 1차 베팅 ---")
        
        # 2장 중 1장 공개 필요
        # (UI에서 처리, 여기서는 자동으로 첫 번째 카드 공개)
        self.reveal_one_card(self.player, 0)
        self.reveal_one_card(self.npc, 0)
        
        # Zone 발동 체크
        self._check_zone_activation()
    
    def _check_zone_activation(self):
        """Zone 발동을 체크합니다."""
        # 플레이어 족보 평가 (Zone 확률 계산용)
        temp_hand = self.evaluator.evaluate(self.player.cards[:2])
        is_special = self.evaluator.is_special_hand(temp_hand)
        
        # Zone 발동 시도
        if self.zone.try_activate(
            self.pot,
            self.player.current_bet,
            self.player.money,
            is_special
        ):
            print(f"\n⚡ Zone 발동! ⚡")
            self.state = GameState.ZONE_ACTIVE    
    
    def start_second_betting(self):
        """2차 베팅을 시작합니다."""
        self.betting_phase = 1
        self.betting_round_count = 0
        self.check_count = 0
        self.player_has_acted = False
        self.npc_has_acted = False
        self.state = GameState.BETTING
        
        print(f"\n--- 2차 베팅 (최종) ---")
        
        # Zone 발동 체크
        self._check_zone_activation()
    
    def process_bet(self, player: Player, action: str, amount: int = 0) -> bool:
        """
        베팅을 처리합니다.
        
        Args:
            player: 베팅하는 플레이어
            action: 베팅 행동
            amount: 베팅 금액
            
        Returns:
            성공 여부
        """
        # 현재 턴 플레이어 확인
        current_turn_player = self.get_current_turn_player()
        if player != current_turn_player:
            print(f"ERROR: {player.name}의 차례가 아닙니다! (현재: {current_turn_player.name})")
            return False
        
        # 액션 기록 (레거시)
        if player == self.player:
            self.player_has_acted = True
        else:
            self.npc_has_acted = True
        
        # 액션별 한글 이름 매핑
        action_names = {
            BetAction.DIE: "다이",
            BetAction.CHECK: "체크",
            BetAction.PPING: "삥",
            BetAction.HALF: "하프",
            BetAction.CALL: "콜",
            BetAction.ALLIN: "올인"
        }
        
        # 베팅 히스토리 기록용
        bet_record = {
            'betting_phase': self.betting_phase,
            'bet_seq': len(self.betting_process_this_round['bet_history']),
            'bet_player': player.name,
            'bet_type': action_names[action],
            'amount': 0
        }
        
        # 레이즈 여부 체크
        is_raise = False
        
        if action == BetAction.DIE:
            player.fold()
            bet_record['amount'] = 0
            self.bet_history.append((player.name, action_names[action], 0))
            print(f"{player.name}: 다이")
            
        elif action == BetAction.CHECK:
            bet_record['amount'] = 0
            self.bet_history.append((player.name, action_names[action], 0))
            print(f"{player.name}: 체크")
            self.check_count += 1
            
        elif action == BetAction.PPING:
            if player.bet(self.min_bet):
                self.pot += self.min_bet
                bet_record['amount'] = self.min_bet
                self.last_bet_amount = self.min_bet
                self.last_bet_player = player
                self.check_count = 0
                # 현재 베팅액 추가
                if player == self.player:
                    old_bet = self.player_current_bet
                    self.player_current_bet += self.min_bet
                    # 상대방보다 많이 베팅했으면 레이즈
                    if self.player_current_bet > self.npc_current_bet:
                        is_raise = True
                else:
                    old_bet = self.npc_current_bet
                    self.npc_current_bet += self.min_bet
                    # 상대방보다 많이 베팅했으면 레이즈
                    if self.npc_current_bet > self.player_current_bet:
                        is_raise = True
                self.bet_history.append((player.name, action_names[action], self.min_bet))
                print(f"{player.name}: 삥 ({self.min_bet:,}원)")
            else:
                return False
        
        elif action == BetAction.HALF:
            half_amount = self.pot // 2
            if player.bet(half_amount):
                self.pot += half_amount
                bet_record['amount'] = half_amount
                self.last_bet_amount = half_amount
                self.last_bet_player = player
                self.check_count = 0
                # 현재 베팅액 추가
                if player == self.player:
                    old_bet = self.player_current_bet
                    self.player_current_bet += half_amount
                    # 상대방보다 많이 베팅했으면 레이즈
                    if self.player_current_bet > self.npc_current_bet:
                        is_raise = True
                else:
                    old_bet = self.npc_current_bet
                    self.npc_current_bet += half_amount
                    # 상대방보다 많이 베팅했으면 레이즈
                    if self.npc_current_bet > self.player_current_bet:
                        is_raise = True
                self.bet_history.append((player.name, action_names[action], half_amount))
                print(f"{player.name}: 하프 ({half_amount:,}원)")
            else:
                return False
        
        elif action == BetAction.CALL:
            # 콜은 상대방의 현재 베팅액과 내 베팅액의 차이만큼 베팅
            if player == self.player:
                call_amount = self.npc_current_bet - self.player_current_bet
            else:
                call_amount = self.player_current_bet - self.npc_current_bet
            
            # 가진 돈보다 많으면 올인
            call_amount = min(call_amount, player.money)
            
            # 이미 베팅액이 같으면 (call_amount == 0) 콜 성공
            if call_amount == 0:
                bet_record['amount'] = 0
                self.bet_history.append((player.name, action_names[action], 0))
                print(f"{player.name}: 콜 (이미 베팅액 동일)")
                # 베팅 히스토리에 기록
                self.betting_process_this_round['bet_history'].append(bet_record)
                # 턴 전환하지 않음 (베팅 완료)
                return True
            
            if call_amount > 0 and player.bet(call_amount):
                self.pot += call_amount
                bet_record['amount'] = call_amount
                # 현재 베팅액 업데이트
                if player == self.player:
                    self.player_current_bet += call_amount
                else:
                    self.npc_current_bet += call_amount
                self.last_bet_amount = call_amount
                self.last_bet_player = player
                self.check_count = 0
                self.bet_history.append((player.name, action_names[action], call_amount))
                print(f"{player.name}: 콜 ({call_amount:,}원)")
            else:
                return False
        
        elif action == BetAction.ALLIN:
            allin_amount = player.money
            if player.bet(allin_amount):
                self.pot += allin_amount
                bet_record['amount'] = allin_amount
                self.last_bet_amount = allin_amount
                self.last_bet_player = player
                self.check_count = 0
                # 현재 베팅액 추가
                if player == self.player:
                    old_bet = self.player_current_bet
                    self.player_current_bet += allin_amount
                    # 상대방보다 많이 베팅했으면 레이즈
                    if self.player_current_bet > self.npc_current_bet:
                        is_raise = True
                else:
                    old_bet = self.npc_current_bet
                    self.npc_current_bet += allin_amount
                    # 상대방보다 많이 베팅했으면 레이즈
                    if self.npc_current_bet > self.player_current_bet:
                        is_raise = True
                self.bet_history.append((player.name, action_names[action], allin_amount))
                print(f"{player.name}: 올인 ({allin_amount:,}원)!")
            else:
                return False
        
        # 베팅 히스토리에 기록
        self.betting_process_this_round['bet_history'].append(bet_record)
        
        # ★★★ 레이즈가 발생하면 상대방도 다시 액션해야 함
        if is_raise:
            if player == self.player:
                self.npc_has_acted = False
                print(f"DEBUG: 플레이어가 레이즈 → NPC has_acted 리셋")
            else:
                self.player_has_acted = False
                print(f"DEBUG: NPC가 레이즈 → 플레이어 has_acted 리셋")
        
        # ★★★ 핵심: 턴 전환
        self.advance_turn()
        
        # Zone 기록
        self.zone.record_event('bet', {
            'player': player.name,
            'action': action,
            'amount': amount,
            'pot': self.pot
        })
        
        # 베팅 횟수 증가 (체크와 다이 제외)
        if action not in [BetAction.CHECK, BetAction.DIE]:
            self.betting_round_count += 1
        
        print(f"현재 판돈: {self.pot:,}원")
        print(f"DEBUG: 베팅 기록 수: {len(self.betting_process_this_round['bet_history'])}")
        
        return True
    
    def is_betting_done(self) -> bool:
        """베팅이 완료되었는지 확인합니다."""
        # 한쪽이 다이했으면 종료
        if self.player.has_folded or self.npc.has_folded:
            print(f"DEBUG: 베팅 종료 - 다이 (플레이어 폴드: {self.player.has_folded}, NPC 폴드: {self.npc.has_folded})")
            return True
        
        # 둘 다 액션을 했는지 확인 - 아직 액션 안했으면 계속 진행
        if not (self.player_has_acted and self.npc_has_acted):
            print(f"DEBUG: 베팅 진행 중 - 플레이어 액션: {self.player_has_acted}, NPC 액션: {self.npc_has_acted}")
            return False
        
        # 둘 다 액션한 경우에만 아래 체크
        
        # 양쪽 모두 체크했으면 종료
        if self.check_count >= 2:
            print(f"DEBUG: 베팅 종료 - 양쪽 체크 (체크 카운트: {self.check_count})")
            return True
        
        # 한쪽 또는 양쪽이 올인했으면 (돈이 0원) 베팅 종료
        if self.player.money == 0 or self.npc.money == 0:
            print(f"DEBUG: 베팅 종료 - 올인 (플레이어 잔액: {self.player.money}, NPC 잔액: {self.npc.money})")
            return True
        
        # 양쪽 베팅 금액이 같고 둘 다 액션했으면 종료
        if self.player_current_bet == self.npc_current_bet:
            print(f"DEBUG: 베팅 종료 - 베팅액 동일 & 둘 다 액션 완료 (플레이어: {self.player_current_bet}, NPC: {self.npc_current_bet})")
            return True
        
        # 위 조건에 해당 안되면 계속 진행
        print(f"DEBUG: 베팅 진행 중 - 플레이어 베팅: {self.player_current_bet}, NPC 베팅: {self.npc_current_bet}, 플레이어 잔액: {self.player.money}, NPC 잔액: {self.npc.money}")
        return False
    
    def get_all_hand_combinations(self, cards):
        """
        3장의 카드에서 2장씩 선택한 모든 조합과 족보를 반환합니다.
        
        Args:
            cards: 카드 리스트 (3장)
            
        Returns:
            list: [(카드1, 카드2, 족보), ...] 형태의 리스트
        """
        if len(cards) < 3:
            return []
        
        combinations = []
        # 3장 중 2장을 선택하는 모든 조합 (3C2 = 3가지)
        # [0,1], [0,2], [1,2]
        indices = [(0, 1), (0, 2), (1, 2)]
        
        for i, j in indices:
            hand_cards = [cards[i], cards[j]]
            hand_eval = self.evaluator.evaluate(hand_cards)
            combinations.append({
                'cards': hand_cards,
                'indices': (i, j),
                'hand': hand_eval
            })
        
        return combinations
    
    def get_best_hand_index(self, cards):
        """
        주어진 카드에서 가장 좋은 2장 조합의 인덱스를 찾습니다.
        
        Args:
            cards: 카드 리스트
            
        Returns:
            int: 가장 좋은 조합의 인덱스 (0, 1, 2)
        """
        if len(cards) < 3:
            return 0
        
        combinations = self.get_all_hand_combinations(cards)
        if not combinations:
            return 0
        
        # 가장 높은 족보 찾기
        best_index = 0
        best_combo = combinations[0]
        for i, combo in enumerate(combinations[1:], 1):
            if self.evaluator.compare(combo['hand'], best_combo['hand']) > 0:
                best_combo = combo
                best_index = i
        
        return best_index
    
    def showdown(self):
        """쇼다운을 진행합니다 (카드 조합 평가만 수행)."""
        self.state = GameState.SHOWDOWN
        
        print(f"\n{'='*50}")
        print("쇼다운!")
        print(f"{'='*50}")
        
        # 다이한 경우 바로 승자 결정
        if self.player.has_folded or self.npc.has_folded:
            self._determine_winner()
            self.state = GameState.ROUND_END
            return
        
        # 모든 카드 공개
        self.player.reveal_all_cards()
        self.npc.reveal_all_cards()
        
        # 플레이어와 NPC의 모든 카드 조합 평가
        self.player_combinations = self.get_all_hand_combinations(self.player.cards)
        self.npc_combinations = self.get_all_hand_combinations(self.npc.cards)
        
        # NPC는 자동으로 최고 조합 선택
        if self.npc_combinations:
            self.npc_selected_combo_index = self.get_best_hand_index(self.npc.cards)
            self.npc_hand = self.npc_combinations[self.npc_selected_combo_index]['hand']
        else:
            self.npc_hand = self.evaluator.evaluate(self.npc.cards[:2])
            self.npc_selected_combo_index = 0
        
        # 플레이어는 UI에서 선택 대기
        self.player_selected_combo_index = None
        
        print(f"\n플레이어는 2장 조합을 선택하세요...")
        print(f"NPC는 자동으로 조합을 선택했습니다.")
    
    def select_player_combination(self, combo_index):
        """
        플레이어가 카드 조합을 선택합니다.
        
        Args:
            combo_index: 선택한 조합 인덱스 (0, 1, 2)
        """
        if not self.player_combinations or combo_index < 0 or combo_index >= len(self.player_combinations):
            return False
        
        self.player_selected_combo_index = combo_index
        self.player_hand = self.player_combinations[combo_index]['hand']
        
        print(f"\n플레이어가 조합 {combo_index + 1}을 선택했습니다.")
        print(f"족보: {self.player_hand['name']}")
        
        return True
    
    def finalize_showdown(self):
        """쇼다운 결과를 확정하고 승자를 결정합니다."""
        if self.player_selected_combo_index is None:
            print("플레이어가 아직 조합을 선택하지 않았습니다!")
            return False
        
        print(f"\n{'='*50}")
        print("최종 대결!")
        print(f"{'='*50}")
        
        print(f"\n{self.player.name}의 선택:")
        for card in self.player_combinations[self.player_selected_combo_index]['cards']:
            print(f"  - {card}")
        print(f"족보: {self.player_hand['name']} - {self.player_hand['description']}")
        
        print(f"\n{self.npc.name}의 선택:")
        for card in self.npc_combinations[self.npc_selected_combo_index]['cards']:
            print(f"  - {card}")
        print(f"족보: {self.npc_hand['name']} - {self.npc_hand['description']}")
        
        # 승패 판정
        self._determine_winner()
        return True
    
    def _determine_winner(self):
        """승패를 판정합니다."""
        # 다이 체크
        if self.player.has_folded:
            # 다이했어도 카드 공개
            self.player.reveal_all_cards()
            self.npc.reveal_all_cards()
            
            winner = self.npc
            loser = self.player
            print(f"\n{self.player.name}가 다이 -> {self.npc.name} 승리!")
        elif self.npc.has_folded:
            # 다이했어도 카드 공개
            self.player.reveal_all_cards()
            self.npc.reveal_all_cards()
            
            winner = self.player
            loser = self.npc
            print(f"\n{self.npc.name}가 다이 -> {self.player.name} 승리!")
        else:
            # 족보 비교
            # 구사 재경기 체크
            if self.evaluator.needs_rematch(self.player_hand, self.npc_hand):
                print(f"\n구사(4+9) 재경기!")
                self.last_winner = None
                self._handle_draw()  # 무승부 처리와 동일하게 판돈 이월
                return

            result = self.evaluator.compare(self.player_hand, self.npc_hand)
            
            if result > 0:
                winner = self.player
                loser = self.npc
                print(f"\n{self.player.name} 승리!")
            elif result < 0:
                winner = self.npc
                loser = self.player
                print(f"\n{self.npc.name} 승리!")
            else:
                # 무승부 (드물지만 가능)
                print(f"\n무승부!")
                self.last_winner = None
                self._handle_draw()
                return
        
        # 승자 저장
        self.last_winner = winner
        
        # 판돈 지급
        winner.win(self.pot)
        loser.lose()
        
        print(f"{winner.name}이(가) {self.pot:,}원 획득!")
        print(f"{self.player.name}: {self.player.money:,}원")
        print(f"{self.npc.name}: {self.npc.money:,}원")
        
        # NPC 상태 업데이트
        if winner == self.npc:
            self.npc.on_victory()
        else:
            self.npc.on_defeat()
        
        # # NPC 발화 (결과)
        # if self.npc.should_speak():
        #     situation = 'result_win' if winner == self.npc else 'result_lose'
        #     dialogue = self.llm.generate_dialogue(
        #         self.npc.get_dialogue_context(situation)
        #     )
        #     print(f"\n{self.npc.name}: \"{dialogue}\"")
            
        #     self.zone.record_event('npc_dialogue', {
        #         'situation': situation,
        #         'text': dialogue
        #     })
        
        # Zone 기록
        self.zone.record_event('showdown_result', {
            'winner': winner.name,
            'pot': self.pot,
            'player_hand': self.player_hand,
            'npc_hand': self.npc_hand
        })
        
        self.state = GameState.ROUND_END
    
    def _handle_draw(self):
        """무승부 처리 - 판돈을 묻고 다음 라운드로"""
        print(f"\n무승부! 판돈 {self.pot:,}원을 묻고 다음 라운드로 넘어갑니다.")
        
        # 판돈을 다음 라운드로 이월
        self.carried_pot = self.pot
        
        self.state = GameState.ROUND_END
    
    def end_round(self):
        """라운드를 종료합니다."""
        # NPC 멘탈 회복
        self.npc.recover_mental()
        
        # Zone 라운드 종료
        self.zone.end_round()
        
        # 게임 종료 체크
        if self._check_game_over():
            self.state = GameState.GAME_OVER
        else:
            # 다음 라운드
            if self.current_round < self.total_rounds:
                self.start_new_round()
            else:
                self.state = GameState.GAME_OVER
    
    def _check_game_over(self) -> bool:
        """게임 종료 조건 확인"""
        # 한쪽이 파산
        if self.player.is_bankrupt():
            print(f"\n{self.player.name} 파산! 게임 오버!")
            return True
        
        if self.npc.is_bankrupt():
            print(f"\n{self.npc.name} 파산! {self.player.name} 승리!")
            return True
        
        # 모든 라운드 종료
        if self.current_round >= self.total_rounds:
            return True
        
        return False
    
    def show_final_result(self):
        """최종 결과를 표시합니다."""
        print(f"\n{'='*50}")
        print("게임 종료!")
        print(f"{'='*50}")
        
        print(f"\n최종 결과:")
        print(f"{self.player.name}: {self.player.wins}승 {self.player.losses}패, {self.player.money:,}원")
        print(f"{self.npc.name}: {self.npc.wins}승 {self.npc.losses}패, {self.npc.money:,}원")
        
        if self.player.money > self.npc.money:
            print(f"\n🏆 {self.player.name} 최종 승리! 🏆")
        elif self.npc.money > self.player.money:
            print(f"\n{self.npc.name} 최종 승리!")
        else:
            print(f"\n무승부!")


# 테스트용 간단한 실행 (추후 main.py로 이동)
if __name__ == "__main__":
    print("=== 섯다 게임 테스트 ===\n")
    print("(간단한 자동 진행 테스트)")
    
    game = SutdaGame("테스터")
    game.start_new_game()
    
    print(f"\n게임 시작!")
    print(f"라운드: {game.current_round}/{game.total_rounds}")
    print(f"플레이어 카드: {[str(c) for c in game.player.cards]}")
    print(f"NPC 카드: {[str(c) for c in game.npc.cards]}")
