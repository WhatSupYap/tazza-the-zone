"""
메인 게임 화면
Pygame을 사용한 게임 UI 통합
"""

import pygame
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FPS,
    COLOR_WHITE, COLOR_HIGHLIGHT, COLOR_GOLD, COLOR_SUCCESS, COLOR_DANGER,
    COLOR_BLACK, COLOR_WARNING, COLOR_LIGHT_GRAY,
    CARD_WIDTH, CARD_HEIGHT,
    COLOR_COMMON, COLOR_UNCOMMON, COLOR_RARE, COLOR_EPIC, COLOR_LEGENDARY, COLOR_MYTHIC
)

from core.game import SutdaGame, GameState, BetAction
from ui.renderer import Renderer
from ui.button import Button, BetButton, DangerButton, HighlightButton, ButtonGroup
from ui.card_display import CardDisplay


class GameScreen:
    """메인 게임 화면 클래스"""
    
    def __init__(self):
        """
        게임 화면을 초기화합니다.
        
        Args:
            game: 게임 인스턴스
        """
        self.game = SutdaGame()
        self.renderer = Renderer()
        self.card_display = CardDisplay()
        self.button_group = ButtonGroup()
        
        # 상태
        self.running = True
        self.message = ""
        self.message_timer = 0
        self.dialogue = None
        self.dialogue_timer = 0
        self.dialogue_waiting_click = False  # 대화 클릭 대기 중
        self.dialogue_confirm_button = None  # 대화 확인 버튼
        self.dialogue_inner_thought_button = None  # 대화 속마음 버튼
        self.show_inner_thought = False  # 속마음 표시 여부
        self.inner_thought_text = ""  # 속마음 텍스트
        self.inner_thought_close_button = None  # 속마음 닫기 버튼
        
        # Zone UI
        self.zone_active = False
        self.zone_scroll_offset = 0
        
        # 카드 선택
        self.selected_card_indices = set()
        self.card_rects = []
        self.card_confirm_button = None  # 카드 선택 확정 버튼
        
        # 쇼다운 조합 선택
        self.combo_rects = []  # 조합 영역들
        self.selected_combo_index = None  # 선택된 조합 인덱스
        self.showdown_confirm_button = None  # 쇼다운 확정 버튼
        
        # NPC 턴 대기 상태
        self.waiting_for_npc = False
        self.npc_action_timer = 0
        self.npc_action_delay = 1500  # 1.5초 대기
        self.npc_turn_in_progress = False  # NPC 턴 실행 중 플래그 (중복 실행 방지)
        
        # NPC 선택
        self.npc_card_rects = []  # NPC 카드 영역들
        self.selected_npc_index = 0  # 선택된 NPC 인덱스 (기본 0)
        self.hovered_npc_index = -1  # 마우스 호버 중인 NPC 인덱스
        self.npc_confirm_button = None  # 확인 버튼
        
        # 족보 화면
        self.show_hand_guide = False  # 족보 화면 표시 여부
        self.hand_guide_button = None  # 족보 버튼
        self.hand_guide_close_button = None  # 족보 닫기 버튼
        self.hand_guide_scroll = 0  # 족보 화면 스크롤 오프셋
        
        # 베팅 버튼 설정
        self._setup_bet_buttons()
        
        # 족보 버튼 생성
        self._create_hand_guide_button()
        
        # 플레이어 이름 입력
        self.player_name = "플레이어"
        self.name_input_rect = None
        self.name_input_active = False
        
        # ESC 종료 확인 팝업
        self.show_exit_popup = False
        self.exit_popup_buttons = []  # [메인으로, 게임종료, 취소] 버튼들

    def handle_events(self):
        """이벤트를 처리합니다."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            # 족보 화면이 열려있을 때는 족보 관련 이벤트만 처리
            if self.show_hand_guide:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._close_hand_guide()
                elif event.type == pygame.MOUSEWHEEL:
                    self.hand_guide_scroll -= event.y * 30
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.hand_guide_close_button:
                        self.hand_guide_close_button.handle_event(event)
                continue
            
            # 종료 확인 팝업이 열려있을 때
            if self.show_exit_popup:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_exit_popup_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # ESC로 팝업 닫기
                        self.show_exit_popup = False
                continue
            
            # 키보드 이벤트 처리 (독립적으로)
            if event.type == pygame.KEYDOWN:
                # 이름 입력 중일 때
                if self.name_input_active:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.name_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.name_input_active = False
                # 이름 입력 중이 아닐 때
                else:
                    if event.key == pygame.K_ESCAPE:
                        # 메인 타이틀이면 바로 종료, 아니면 팝업 표시
                        if self.game.state == GameState.MAIN_TITLE:
                            self.running = False
                            return False
                        else:
                            self.show_exit_popup = True
                            self._create_exit_popup_buttons()
                    # Alt+Enter: 전체화면 토글
                    elif event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT):
                        self._toggle_fullscreen()
                    # GameState가 MainTitle일때 캐릭터 선택 화면으로 이동
                    elif self.game.state == GameState.MAIN_TITLE:
                        self.game.state = GameState.CHOICE_NPC
                    elif event.key == pygame.K_SPACE:
                        # 스페이스: 다음 단계 진행
                        self._advance_game_state()
            
            # 텍스트 입력 이벤트 처리 (한글 입력 지원)
            if event.type == pygame.TEXTINPUT:
                if self.name_input_active:
                    # 글자 수 제한 (최대 10자)
                    if len(self.player_name) < 10:
                        self.player_name += event.text
            
            # 마우스 움직임 이벤트 처리 (독립적으로)
            if event.type == pygame.MOUSEMOTION:
                # 족보 버튼 호버 처리 (항상 최우선으로 확인)
                if self.hand_guide_button:
                    self.hand_guide_button.handle_event(event)
                
                # 대화 클릭 대기 중이면 다른 마우스 움직임 무시
                if self.dialogue_waiting_click:
                    continue
                
                # NPC 선택 화면에서 마우스 호버 처리
                if self.game.state == GameState.CHOICE_NPC:
                    self._handle_npc_hover(event.pos)
            
            # 마우스 클릭 이벤트 처리 (독립적으로)
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 족보 화면이 열려있을 때 닫기 버튼 클릭 처리 (최우선 - 1순위)
                if self.show_hand_guide and self.hand_guide_close_button:
                    if self.hand_guide_close_button.rect.collidepoint(event.pos):
                        print("DEBUG: 족보 닫기 버튼 클릭됨")
                        self._close_hand_guide()
                        continue
                
                # 족보 버튼 클릭 처리 (모든 상황에서 가능, 최우선 - 2순위)
                if self.hand_guide_button and self.hand_guide_button.rect.collidepoint(event.pos):
                    print("DEBUG: 족보 버튼 클릭됨")
                    self._toggle_hand_guide()
                    continue
                
                # 속마음 대화창이 열려있으면 속마음 닫기 버튼만 처리 (3순위)
                if self.show_inner_thought and self.inner_thought_close_button:
                    if self.inner_thought_close_button.rect.collidepoint(event.pos):
                        self.show_inner_thought = False
                        self.inner_thought_close_button = None
                    continue
                
                # 대화 클릭 대기 중이면 대화 관련 버튼만 처리 (4순위)
                if self.dialogue_waiting_click and self.dialogue:
                    # 확인 버튼 클릭
                    if self.dialogue_confirm_button and self.dialogue_confirm_button.rect.collidepoint(event.pos):
                        self.dialogue = None
                        self.dialogue_waiting_click = False
                        self.dialogue_confirm_button = None
                        self.dialogue_inner_thought_button = None
                        self.show_inner_thought = False
                        self.inner_thought_close_button = None
                        self.inner_thought_text = ""
                        continue
                    
                    # 속마음 버튼 클릭
                    if self.dialogue_inner_thought_button and self.dialogue_inner_thought_button.rect.collidepoint(event.pos):
                        if not self.show_inner_thought:
                            self.show_inner_thought = True
                            self._create_inner_thought_close_button()
                        continue
                    
                    # 대화창이 열려있을 때는 다른 클릭 무시
                    continue

                # 이름 입력창 클릭 처리
                if self.game.state == GameState.CHOICE_NPC and self.name_input_rect:
                    if self.name_input_rect.collidepoint(event.pos):
                        self.name_input_active = True
                    else:
                        self.name_input_active = False
                
                if self.game.state == GameState.MAIN_TITLE:
                    self.game.state = GameState.CHOICE_NPC
                # NPC 선택 화면에서 클릭 처리
                elif self.game.state == GameState.CHOICE_NPC:
                    self._handle_npc_click(event.pos)
                # 카드 선택 화면에서 확정 버튼 클릭
                elif self.game.state == GameState.CARD_SELECTION:
                    if self.card_confirm_button and self.card_confirm_button.rect.collidepoint(event.pos):
                        self._confirm_card_selection()
                # 쇼다운 화면에서 조합 선택
                elif self.game.state == GameState.SHOWDOWN:
                    self._handle_showdown_click(event.pos)
                # 라운드 종료 화면에서 클릭으로 다음 라운드 진행
                elif self.game.state == GameState.ROUND_END:
                    if self.game.state != GameState.GAME_OVER:
                        self._advance_game_state()
                # 게임 오버 화면에서 클릭으로 메인 타이틀로
                elif self.game.state == GameState.GAME_OVER:
                    self._restart_game()
                
                # 버튼 클릭
                self.button_group.handle_event(event)
                
                # 카드 클릭 (카드 공개 선택)
                if event.button == 1:  # 왼쪽 클릭
                    self._handle_card_click(event.pos)
            
            # 마우스 휠 이벤트 처리 (독립적으로)
            if event.type == pygame.MOUSEWHEEL:
                # 대화 클릭 대기 중이면 스크롤 무시
                if self.dialogue_waiting_click:
                    continue

        
        return True
    
    def _setup_bet_buttons(self):
        """베팅 버튼을 설정합니다."""
        button_x = SCREEN_WIDTH - 230
        button_y = SCREEN_HEIGHT - 160
        button_width = 210
        button_height = 45
        button_spacing = 10
        
        # 다이
        self.btn_die = DangerButton(
            button_x, button_y, button_width, button_height,
            "다이 (포기)", callback=self._on_die_click
        )
        
        # 체크
        self.btn_check = BetButton(
            button_x, button_y + (button_height + button_spacing),
            button_width, button_height,
            "체크 (패스)", callback=self._on_check_click
        )
        
        # 삥
        self.btn_pping = BetButton(
            button_x, button_y + (button_height + button_spacing) * 2,
            button_width, button_height,
            f"삥 ({self.game.min_bet:,}원)", callback=self._on_pping_click
        )
        
        self.button_group.add_button(self.btn_die)
        self.button_group.add_button(self.btn_check)
        self.button_group.add_button(self.btn_pping)
    
    def _create_additional_bet_buttons(self):
        """추가 베팅 버튼을 생성합니다 (하프, 콜, 올인)."""
        self.button_group.clear()
        
        button_x = SCREEN_WIDTH - 230
        button_y = SCREEN_HEIGHT - 260
        button_width = 105
        button_height = 45
        button_spacing = 5
        
        # 첫 줄: 다이, 체크
        self.btn_die = DangerButton(
            button_x, button_y, button_width, button_height,
            "다이", callback=self._on_die_click
        )
        self.btn_check = BetButton(
            button_x + button_width + button_spacing, button_y,
            button_width, button_height,
            "체크", callback=self._on_check_click
        )
        
        # 둘째 줄: 삥, 하프
        self.btn_pping = BetButton(
            button_x, button_y + button_height + button_spacing,
            button_width, button_height,
            f"삥 {self.game.min_bet//1000}K", callback=self._on_pping_click
        )
        half_amount = self.game.pot // 2
        self.btn_half = BetButton(
            button_x + button_width + button_spacing,
            button_y + button_height + button_spacing,
            button_width, button_height,
            f"하프 {half_amount//1000}K", callback=self._on_half_click
        )
        
        # 셋째 줄: 콜, 올인
        call_amount = self.game.npc.current_bet - self.game.player.current_bet
        self.btn_call = HighlightButton(
            button_x, button_y + (button_height + button_spacing) * 2,
            button_width, button_height,
            f"콜 {call_amount//1000}K" if call_amount > 0 else "콜",
            callback=self._on_call_click
        )
        self.btn_allin = HighlightButton(
            button_x + button_width + button_spacing,
            button_y + (button_height + button_spacing) * 2,
            button_width, button_height,
            "올인!", callback=self._on_allin_click
        )
        
        self.button_group.add_button(self.btn_die)
        self.button_group.add_button(self.btn_check)
        self.button_group.add_button(self.btn_pping)
        self.button_group.add_button(self.btn_half)
        self.button_group.add_button(self.btn_call)
        self.button_group.add_button(self.btn_allin)
        
        # 버튼 활성화 상태 업데이트
        self._update_button_states()
    
    def _update_button_states(self):
        """베팅 버튼의 활성화 상태를 중앙에서 관리하고 업데이트합니다."""
        # 기본적으로 모든 버튼을 비활성화 상태로 시작합니다.
        enable_die = False
        enable_check = False
        enable_pping = False
        enable_half = False
        enable_call = False
        enable_allin = False

        # 게임 상태가 베팅이 아니거나, NPC 턴을 기다리거나, 대화창이 떠 있으면 모든 버튼을 비활성화합니다.
        if self.game.state != GameState.BETTING or self.waiting_for_npc or self.dialogue_waiting_click:
            # 버튼 비활성화
            if hasattr(self, 'btn_die'):
                self.btn_die.set_enabled(False)
            if hasattr(self, 'btn_check'):
                self.btn_check.set_enabled(False)
            if hasattr(self, 'btn_pping'):
                self.btn_pping.set_enabled(False)
            if hasattr(self, 'btn_half'):
                self.btn_half.set_enabled(False)
            if hasattr(self, 'btn_call'):
                self.btn_call.set_enabled(False)
            if hasattr(self, 'btn_allin'):
                self.btn_allin.set_enabled(False)
            return
        
        # ★★★ 새로운 턴 시스템: 현재 플레이어 턴인지 확인
        is_player_turn = self.game.is_player_turn()
        
        # print(f"DEBUG: 버튼 상태 업데이트 - 플레이어 턴? {is_player_turn}, waiting_for_npc? {self.waiting_for_npc}")
        # print(f"DEBUG: 현재 턴: {self.game.get_current_turn_player().name if self.game.get_current_turn_player() else 'None'}")
        # print(f"DEBUG: 플레이어 베팅: {self.game.player_current_bet}, NPC 베팅: {self.game.npc_current_bet}")
        
        # NPC 턴이면 버튼만 비활성화 (자동 트리거는 하지 않음)
        # NPC 턴 트리거는 _player_bet_action() 또는 _execute_pending_action()에서만 수행
        if not is_player_turn:
            # print("DEBUG: _update_button_states - NPC 턴이므로 버튼 비활성화만 수행")
            # 버튼 모두 비활성화
            if hasattr(self, 'btn_die'):
                self.btn_die.set_enabled(False)
            if hasattr(self, 'btn_check'):
                self.btn_check.set_enabled(False)
            if hasattr(self, 'btn_pping'):
                self.btn_pping.set_enabled(False)
            if hasattr(self, 'btn_half'):
                self.btn_half.set_enabled(False)
            if hasattr(self, 'btn_call'):
                self.btn_call.set_enabled(False)
            if hasattr(self, 'btn_allin'):
                self.btn_allin.set_enabled(False)
            return
        
        if is_player_turn:
            # 베팅에 필요한 게임 상태 정보 가져오기
            player = self.game.player
            pot = self.game.pot
            min_bet = self.game.min_bet
            call_amount = self.game.npc_current_bet - self.game.player_current_bet
            
            # print(f"DEBUG: call_amount = {call_amount}, 판돈 = {pot}")
            
            # 플레이어가 이번 베팅 라운드에서 이미 행동했는지 여부
            player_has_acted = self.game.player_has_acted

            # 1. 다이(Die) 버튼: 항상 활성화
            enable_die = True

            # 2. 올인(All-in) 버튼: 플레이어 돈이 0보다 크면 항상 활성화
            enable_allin = player.money > 0

            # 3. 콜(Call) 버튼: 상대가 나보다 많이 베팅했고, 그 금액만큼 돈이 있을 때 활성화
            enable_call = call_amount > 0 and player.money >= call_amount
            
            # print(f"DEBUG: 콜 활성화? {enable_call} (call_amount={call_amount}, money={player.money})")

            # 4. 체크(Check) 버튼: 플레이어가 아직 행동하지 않았고, 콜할 금액이 없을 때 활성화
            enable_check = not player_has_acted and call_amount <= 0

            # 5. 삥(Pping) 버튼: 플레이어가 아직 행동하지 않았고, 콜할 금액이 없으며, 최소 베팅 금액 이상 돈이 있을 때 활성화
            enable_pping = not player_has_acted and call_amount <= 0 and player.money >= min_bet

            # 6. 하프(Half) 버튼:
            half_amount = pot // 2
            can_afford_half = player.money >= half_amount
            # 하프 베팅은 판돈이 있고, 그 금액을 감당할 수 있을 때 가능합니다.
            # 또한, 콜이 필요한 상황이 아니라면(첫 턴이 아니어야 함), 아무도 베팅하지 않은 첫 턴일 때 가능합니다.
            is_raisable_situation = call_amount > 0 or (not player_has_acted and half_amount > 0)
            
            if half_amount > 0 and can_afford_half and is_raisable_situation:
                # 하프 금액이 최소한 콜해야 하는 금액보다는 크거나 같아야 합니다.
                if half_amount >= call_amount:
                    enable_half = True
        
        # print(f"DEBUG: 최종 버튼 상태 - 다이:{enable_die}, 체크:{enable_check}, 삥:{enable_pping}, 하프:{enable_half}, 콜:{enable_call}, 올인:{enable_allin}")

        # 최종적으로 계산된 상태를 각 버튼에 적용합니다.
        if hasattr(self, 'btn_die'):
            self.btn_die.set_enabled(enable_die)
        if hasattr(self, 'btn_check'):
            self.btn_check.set_enabled(enable_check)
        if hasattr(self, 'btn_pping'):
            self.btn_pping.set_enabled(enable_pping)
        if hasattr(self, 'btn_half'):
            self.btn_half.set_enabled(enable_half)
        if hasattr(self, 'btn_call'):
            self.btn_call.set_enabled(enable_call)
        if hasattr(self, 'btn_allin'):
            self.btn_allin.set_enabled(enable_allin)
    
    def _create_hand_guide_button(self):
        """족보 버튼을 생성합니다."""
        button_width = 100
        button_height = 40
        button_x = SCREEN_WIDTH - button_width - 20  # 우측 상단
        button_y = 20
        
        print(f"DEBUG: 족보 버튼 생성 - 위치: ({button_x}, {button_y}), 크기: ({button_width}, {button_height})")
        
        self.hand_guide_button = Button(
            button_x, button_y, button_width, button_height,
            "족보",
            bg_color=(50, 100, 150),
            hover_color=(70, 120, 170),
            text_color=COLOR_WHITE,
            border_color=COLOR_GOLD,
            callback=self._toggle_hand_guide
        )
        
        print(f"DEBUG: 족보 버튼 생성 완료 - button rect: {self.hand_guide_button.rect}")
    
    def _toggle_hand_guide(self):
        """족보 화면을 토글합니다."""
        self.show_hand_guide = not self.show_hand_guide
        
        # 족보 화면이 열릴 때 닫기 버튼 생성 및 스크롤 초기화
        if self.show_hand_guide:
            self.hand_guide_scroll = 0  # 스크롤 초기화
            close_size = 40
            close_x = SCREEN_WIDTH - 100 - close_size - 20
            close_y = 70
            
            self.hand_guide_close_button = Button(
                close_x, close_y, close_size, close_size,
                "X",  # ✕ 대신 X 사용 (폰트 호환성)
                bg_color=(150, 50, 50),
                hover_color=(180, 70, 70),
                text_color=COLOR_WHITE,
                border_color=COLOR_DANGER,
                callback=self._close_hand_guide
            )
    
    def _close_hand_guide(self):
        """족보 화면을 닫습니다."""
        self.show_hand_guide = False
        self.hand_guide_close_button = None
    
    def _draw_hand_guide(self):
        """족보 화면을 그립니다."""
        # 반투명 배경
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLOR_BLACK)
        self.renderer.screen.blit(overlay, (0, 0))
        
        # 족보 상자 크기 및 위치
        box_width = 900
        box_height = 700
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        # 족보 상자 배경
        guide_bg = pygame.Surface((box_width, box_height))
        guide_bg.set_alpha(240)
        guide_bg.fill((30, 30, 40))
        self.renderer.screen.blit(guide_bg, (box_x, box_y))
        
        # 족보 상자 테두리
        pygame.draw.rect(
            self.renderer.screen,
            COLOR_GOLD,
            (box_x, box_y, box_width, box_height),
            5
        )
        
        # 제목
        self.renderer.draw_text_outlined(
            "섯다 족보",
            box_x + box_width // 2 - 80, box_y + 20,
            self.renderer.font_large, COLOR_GOLD
        )
        
        # 스크롤 안내
        self.renderer.draw_text(
            "마우스 휠로 스크롤",
            box_x + box_width - 180, box_y + 25,
            self.renderer.font_small, COLOR_WARNING
        )
        
        # 컨텐츠 영역 설정 (스크롤 가능)
        content_x = box_x + 20
        content_y = box_y + 85  # 타이틀과 콘텐츠 사이 간격 증가 (70 -> 85)
        content_width = box_width - 40
        content_height = box_height - 105  # content_y 증가에 따라 조정 (90 -> 105)
        
        # 클리핑 영역 설정 (컨텐츠가 박스 밖으로 나가지 않도록)
        clip_rect = pygame.Rect(content_x, content_y, content_width, content_height)
        self.renderer.screen.set_clip(clip_rect)
        
        # 스크롤된 시작 위치
        start_y = content_y - self.hand_guide_scroll
        y_offset = start_y
        line_height = 28
        
        # === 게임 설명 ===
        game_desc = [
            "- 섯다는 2장의 패를 조합하여 높은 족보를 만든 사람이 이기는 게임이다.",
            "- 족보 순위는 1위가 가장 높고, 숫자가 클수록 낮다.",
            "- 특수 족보 '암행어사'는 '광땡'을 잡을 수 있다.",
            "- 특수 족보 '땡잡이'는 '장땡'이하 모든 '땡'을 잡을 수 있다.",
            "- 특수 족보 '구사'는 '땡'아래, '멍텅구리 구사'는 '장땡' 아래를 재경기로 만든다."
        ]
        
        for desc in game_desc:
            self.renderer.draw_text(
                desc,
                content_x + 10, y_offset,
                self.renderer.font_small, COLOR_WHITE
            )
            y_offset += line_height
        
        y_offset += 20  # 게임 설명과 카드 섹션 사이 간격 증가 (15 -> 20)
        
        # === 카드 이미지 표시 (1월~10월) ===
        self.renderer.draw_text(
            "【화투 카드】",
            content_x + 20, y_offset,
            self.renderer.font_medium, COLOR_GOLD
        )
        y_offset += line_height + 10
        
        # 카드 이미지 크기 (작게)
        card_scale = 0.3
        card_img_width = int(CARD_WIDTH * card_scale)
        card_img_height = int(CARD_HEIGHT * card_scale)
        card_spacing = 8  # 카드 간 간격 증가
        
        # 월별 카드 정보 (파일명, 이름)
        month_cards = [
            ([("1g.png", "광"), ("1t.png", "띠")], "1월 (송학)"),
            ([("2k.png", "열끗"), ("2t.png", "띠")], "2월 (매조)"),
            ([("3g.png", "광"), ("3t.png", "띠")], "3월 (벚꽃)"),
            ([("4k.png", "열끗"), ("4t.png", "띠")], "4월 (흑싸리)"),
            ([("5k.png", "열끗"), ("5t.png", "띠")], "5월 (난초)"),
            ([("6k.png", "열끗"), ("6t.png", "띠")], "6월 (모란)"),
            ([("7k.png", "열끗"), ("7t.png", "띠")], "7월 (홍싸리)"),
            ([("8g.png", "광"), ("8k.png", "열끗")], "8월 (공산)"),
            ([("9k.png", "열끗"), ("9t.png", "띠")], "9월 (국진)"),
            ([("10k.png", "열끗"), ("10t.png", "띠")], "10월 (단풍)")
        ]
        
        # 2행 5열로 배치
        cards_per_row = 5
        row_height = card_img_height + 50  # 행 간격 증가
        
        for idx, (cards_info, month_name) in enumerate(month_cards):
            row = idx // cards_per_row
            col = idx % cards_per_row
            
            # 위치 계산
            x_pos = content_x + 30 + col * 170
            y_pos = y_offset + row * row_height
            
            # 월 이름
            self.renderer.draw_text(
                month_name,
                x_pos, y_pos,
                self.renderer.font_small, COLOR_HIGHLIGHT
            )
            
            # 카드 이미지 2장
            for card_idx, (card_file, card_type) in enumerate(cards_info):
                card_x = x_pos + card_idx * (card_img_width + card_spacing)
                card_y = y_pos + 25  # 월 이름과 카드 사이 간격 증가
                
                # 카드 이미지 로드 및 표시
                card_img = self.card_display.load_card_image(card_file)
                if card_img:
                    scaled_img = pygame.transform.scale(card_img, (card_img_width, card_img_height))
                    self.renderer.screen.blit(scaled_img, (card_x, card_y))
        
        # 다음 섹션 위치 조정
        y_offset += row_height * 2 + 20
        
        # === 족보 순위 ===
        self.renderer.draw_text(
            "【족보 순위】",
            content_x + 20, y_offset,
            self.renderer.font_medium, COLOR_GOLD
        )
        y_offset += line_height + 10
        
        # 족보 리스트 (이름, 설명, 색상, 카드파일들)
        hand_ranks = [
            ("1. 삼팔 광땡", "(3월, 8월 광)", COLOR_LEGENDARY, ["3g.png", "8g.png"]),
            ("2. 일팔 광땡", "(1월, 8월 광)", COLOR_EPIC, ["1g.png", "8g.png"]),
            ("3. 일삼 광땡", "(1월, 3월 광)", COLOR_EPIC, ["1g.png", "3g.png"]),
            ("4. 땡", "(같은 월의 패 2장)", COLOR_RARE, ["9k.png", "9t.png"]),  # 예시: 9땡
            ("5. 알리", "(1월, 2월)", COLOR_UNCOMMON, ["1g.png", "2k.png"]),
            ("6. 독사", "(1월, 4월)", COLOR_UNCOMMON, ["1g.png", "4k.png"]),
            ("7. 구삥", "(1월, 9월)", COLOR_UNCOMMON, ["1g.png", "9k.png"]),
            ("8. 장삥", "(1월, 10월)", COLOR_UNCOMMON, ["1g.png", "10k.png"]),
            ("9. 장사", "(4월, 10월)", COLOR_UNCOMMON, ["4k.png", "10k.png"]),
            ("10. 세륙", "(4월, 6월)", COLOR_UNCOMMON, ["4k.png", "6k.png"]),
            ("11. 암행어사", "(4월, 7월 패)", COLOR_DANGER, ["4k.png", "7k.png"]),
            ("12. 땡잡이", "(3월, 7월 패)", COLOR_DANGER, ["3g.png", "7k.png"]),
            ("13. 갑오", "(아홉끗, 9)", COLOR_WHITE, ["1g.png", "8g.png"]),  # 예시: 1+8=9
            ("14. 끗", "(두패 합의 1의 자리 숫자)", (180, 180, 180), ["2k.png", "3g.png"])  # 예시: 5끗
        ]
        
        # 작은 카드 이미지 크기
        rank_card_scale = 0.2
        rank_card_width = int(CARD_WIDTH * rank_card_scale)
        rank_card_height = int(CARD_HEIGHT * rank_card_scale)
        rank_card_spacing = 3
        
        for rank, desc, color, card_files in hand_ranks:
            # 족보 이름 (왼쪽)
            self.renderer.draw_text(
                f"{rank}",
                content_x + 30, y_offset,
                self.renderer.font_small, color
            )
            
            # 카드 이미지 2장 (중앙)
            card_start_x = content_x + 200
            for idx, card_file in enumerate(card_files):
                card_x = card_start_x + idx * (rank_card_width + rank_card_spacing)
                card_y = y_offset - 5  # 텍스트와 정렬
                
                # 카드 이미지 로드 및 표시
                card_img = self.card_display.load_card_image(card_file)
                if card_img:
                    scaled_img = pygame.transform.scale(card_img, (rank_card_width, rank_card_height))
                    self.renderer.screen.blit(scaled_img, (card_x, card_y))
            
            # 설명 (오른쪽)
            self.renderer.draw_text(
                f"{desc}",
                content_x + 330, y_offset,
                self.renderer.font_small, COLOR_WHITE
            )
            
            y_offset += line_height
        
        # 컨텐츠 총 높이 계산 (스크롤을 고려하여 실제 컨텐츠 높이)
        total_content_height = (y_offset - start_y) + self.hand_guide_scroll
        
        # 최대 스크롤 계산 (컨텐츠가 뷰포트보다 클 때만 스크롤 가능)
        max_scroll = max(0, total_content_height - content_height)
        
        # 스크롤 범위 재조정
        if max_scroll > 0:
            self.hand_guide_scroll = max(0, min(self.hand_guide_scroll, max_scroll))
        else:
            self.hand_guide_scroll = 0
        
        # print(f"DEBUG: 스크롤 - 현재: {self.hand_guide_scroll}, 최대: {max_scroll}, 컨텐츠 높이: {total_content_height}, 뷰포트: {content_height}")
        
        # 클리핑 해제
        self.renderer.screen.set_clip(None)
        
        # 스크롤바 그리기 (컨텐츠가 박스보다 클 때만)
        if max_scroll > 0:
            scrollbar_height = max(30, int(content_height * content_height / total_content_height))
            scrollbar_y = content_y + int((self.hand_guide_scroll / max_scroll) * (content_height - scrollbar_height))
            
            pygame.draw.rect(
                self.renderer.screen,
                COLOR_GOLD,
                (box_x + box_width - 15, scrollbar_y, 8, scrollbar_height),
                0,
                border_radius=4
            )
        
        # 닫기 버튼 그리기
        if self.hand_guide_close_button:
            self.hand_guide_close_button.draw(self.renderer.screen)
    
    def _draw_bet_history(self):
        """베팅 히스토리를 그립니다."""
        # 베팅 히스토리 박스 설정
        box_width = 350
        box_height = 250
        box_x = self.renderer.screen.get_width() - box_width - 20  # 우측 정렬
        box_y = 100
        
        # 배경
        history_bg = pygame.Surface((box_width, box_height))
        history_bg.set_alpha(220)
        history_bg.fill((20, 20, 30))
        self.renderer.screen.blit(history_bg, (box_x, box_y))
        
        # 테두리
        pygame.draw.rect(
            self.renderer.screen,
            COLOR_GOLD,
            (box_x, box_y, box_width, box_height),
            3
        )
        
        # 제목
        self.renderer.draw_text(
            "베팅 기록",
            box_x + box_width // 2, box_y + 15,
            self.renderer.font_medium, COLOR_GOLD, center=True
        )
        
        # 히스토리 내용 (최근 7개만 표시)
        y_offset = box_y + 50
        line_height = 28
        
        # 베팅 히스토리를 최근 것부터 표시
        recent_history = self.game.bet_history[-7:]
        
        for player_name, action, amount in recent_history:
            # 플레이어 이름 색상
            name_color = COLOR_SUCCESS if player_name == self.game.player.name else COLOR_DANGER
            
            # 행동 텍스트
            if amount > 0:
                text = f"{player_name}: {action} ({amount:,}원)"
            else:
                text = f"{player_name}: {action}"
            
            self.renderer.draw_text(
                text,
                box_x + 15, y_offset,
                self.renderer.font_small, name_color
            )
            y_offset += line_height
    
    # 베팅 버튼 콜백
    def _on_die_click(self):
        self._player_bet_action(BetAction.DIE, 0)
    
    def _on_check_click(self):
        self._player_bet_action(BetAction.CHECK, 0)
    
    def _on_pping_click(self):
        self._player_bet_action(BetAction.PPING, self.game.min_bet)
    
    def _on_half_click(self):
        half_amount = self.game.pot // 2
        self._player_bet_action(BetAction.HALF, half_amount)
    
    def _on_call_click(self):
        call_amount = self.game.npc_current_bet - self.game.player_current_bet
        self._player_bet_action(BetAction.CALL, call_amount)
    
    def _on_allin_click(self):
        self._player_bet_action(BetAction.ALLIN, self.game.player.money)
    
    def _player_bet_action(self, action: str, amount: int):
        """
        플레이어 베팅 행동을 처리합니다.
        
        Args:
            action: 베팅 행동
            amount: 베팅 금액
        """
        if self.game.process_bet(self.game.player, action, amount):
            self.show_message(f"{action.upper()} 선택!")
            
            # 다이를 했으면 즉시 쇼다운으로
            if action == BetAction.DIE:
                self.waiting_for_npc = True
                self.npc_action_timer = pygame.time.get_ticks()
                self.npc_action_delay = 1000
                self.show_message("다이! 라운드 종료...", 1000)
                return
            
            # 베팅이 완료되었는지 확인
            if self.game.is_betting_done():
                print("DEBUG: 플레이어 베팅 후 베팅 완료됨")
                # 1차 베팅이 끝났고 아직 카드가 2장이면 3번째 카드 배분
                if self.game.betting_phase == 0 and len(self.game.player.cards) == 2:
                    self.waiting_for_npc = True
                    self.npc_action_timer = pygame.time.get_ticks()
                    self.npc_action_delay = 1500
                    self.show_message("3번째 카드 배분 준비...", 1500)
                # 2차 베팅이 끝났으면 자동으로 쇼다운 진행
                else:
                    self.waiting_for_npc = True
                    self.npc_action_timer = pygame.time.get_ticks()
                    self.npc_action_delay = 1500
                    self.show_message("쇼다운 준비...", 1500)
            else:
                # 베팅이 아직 진행 중 - 현재 턴을 명시적으로 확인
                current_turn_player = self.game.get_current_turn_player()
                print(f"DEBUG: 플레이어 베팅 후 현재 턴: {current_turn_player.name if current_turn_player else 'None'}")
                
                # 현재 턴이 NPC이면 NPC 턴 대기 설정
                if current_turn_player == self.game.npc:
                    print("DEBUG: NPC 턴으로 전환됨 - NPC 턴 대기 설정")
                    self.waiting_for_npc = True
                    self.npc_action_timer = pygame.time.get_ticks()
                    self.npc_action_delay = 1500
                    self.show_message("NPC가 생각 중...", 1500)
                else:
                    # 플레이어 턴이면 아무것도 안함 (레이즈 등으로 다시 플레이어 턴인 경우)
                    print("DEBUG: 플레이어 베팅 후에도 여전히 플레이어 턴 (레이즈 등)")
                    self.show_message("계속 베팅하세요", 1000)
    
    def _npc_turn(self):
        """NPC 턴을 처리합니다."""
        # 중복 실행 방지
        if self.npc_turn_in_progress:
            print("DEBUG: NPC 턴이 이미 실행 중입니다 - 스킵")
            return
        
        self.npc_turn_in_progress = True
        print("DEBUG: NPC 턴 시작 (플래그 설정)")
        
        try:
            # NPC 카드 족보 평가
            from core.hand_evaluator import HandEvaluator
            evaluator = HandEvaluator()
            npc_hand = evaluator.evaluate(self.game.npc.cards)
            
            # 상대방 공개 카드
            player_visible_cards = [card for card in self.game.player.cards if card.is_revealed]

            # NPC 대사
            if self.game.npc.should_speak():
                from ai.llm_handler import LLMHandler
                llm = LLMHandler()
                # 대사 가져오기
                talk, inner_talk = llm.generate_dialogue(self.game)
                self.inner_thought_text = inner_talk  # 속마음 저장
                self.show_dialogue(self.game.npc.name, talk, wait_for_click=True)
            
            # NPC가 콜해야 하는 금액 계산 (플레이어 베팅액 - NPC 베팅액)
            call_amount = self.game.player_current_bet - self.game.npc_current_bet
            
            action, amount = self.game.npc.decide_bet_action(
                npc_hand,
                player_visible_cards,
                self.game.pot,
                call_amount,
                self.game.npc_current_bet == 0
            )
            
            self.game.process_bet(self.game.npc, action, amount)
            self.show_message(f"NPC: {action.upper()}", 2000)
            
            print(f"DEBUG: NPC 베팅 완료 - {action}")
            
            # 베팅이 완료되었는지 확인 - 완료되면 다음 단계로
            if self.game.is_betting_done():
                print("DEBUG: NPC 베팅 후 베팅 완료됨")
                # 1차 베팅이 끝났고 아직 카드가 2장이면 3번째 카드 배분
                if self.game.betting_phase == 0 and len(self.game.player.cards) == 2:
                    self.waiting_for_npc = True
                    self.npc_action_timer = pygame.time.get_ticks()
                    self.npc_action_delay = 1500
                # 2차 베팅이 끝났으면 자동으로 쇼다운 진행
                else:
                    self.waiting_for_npc = True
                    self.npc_action_timer = pygame.time.get_ticks()
                    self.npc_action_delay = 1500
            else:
                # 베팅이 아직 진행 중 - 현재 턴 확인
                current_turn_player = self.game.get_current_turn_player()
                print(f"DEBUG: NPC 베팅 후 현재 턴: {current_turn_player.name if current_turn_player else 'None'}")
                
                # 여전히 NPC 턴이면 다시 NPC 턴 대기 설정 (연속 NPC 턴)
                if current_turn_player == self.game.npc:
                    print("DEBUG: 연속 NPC 턴 - 다시 대기 설정")
                    self.waiting_for_npc = True
                    self.npc_action_timer = pygame.time.get_ticks()
                    self.npc_action_delay = 1500
                else:
                    print("DEBUG: 플레이어 턴으로 전환됨 - 플레이어 입력 대기")
                    # waiting_for_npc는 이미 False이므로 아무것도 안함
        
        finally:
            # 항상 플래그 해제 (예외 발생 시에도)
            self.npc_turn_in_progress = False
            print("DEBUG: NPC 턴 종료 (플래그 해제)")
        

    
    def _execute_pending_action(self):
        """대기 중인 액션을 실행합니다."""
        print("DEBUG: _execute_pending_action 호출됨")
        
        # 다이로 인한 베팅 종료인 경우 바로 쇼다운
        if self.game.player.has_folded or self.game.npc.has_folded:
            print("DEBUG: 다이로 인한 쇼다운")
            self.game.showdown()
            self.show_message("쇼다운! 패를 공개합니다!", 3000)
            return
        
        # 베팅이 완료된 후의 처리
        if self.game.is_betting_done():
            print("DEBUG: 베팅 완료 - 다음 단계로 진행")
            # 1차 베팅이 끝났고 아직 카드가 2장이면 3번째 카드 배분
            if self.game.betting_phase == 0 and len(self.game.player.cards) == 2:
                self.game.deal_third_card()
                self.show_message("3번째 카드 배분! 2차 베팅 시작!", 3000)
                
                # 2차 베팅 시작 - NPC가 선이면 NPC 턴 대기 설정
                current_turn_player = self.game.get_current_turn_player()
                print(f"DEBUG: 2차 베팅 시작 - 현재 턴: {current_turn_player.name}")
                
                if current_turn_player == self.game.npc:
                    print("DEBUG: 2차 베팅 - NPC 턴이므로 대기 설정")
                    self.waiting_for_npc = True
                    self.npc_action_timer = pygame.time.get_ticks()
                    self.npc_action_delay = 1500
                else:
                    print("DEBUG: 2차 베팅 - 플레이어 턴")
                    # 버튼 상태 업데이트
                    self._update_button_states()
            # 2차 베팅이 끝났으면 자동으로 쇼다운 진행
            else:
                print("DEBUG: 2차 베팅 완료 - 쇼다운 진행")
                self.game.showdown()
                self.show_message("쇼다운! 패를 공개합니다!", 3000)
        else:
            # 베팅이 아직 진행 중 - 현재 턴이 NPC인지 확인
            print(f"DEBUG: 베팅 진행 중")
            current_turn_player = self.game.get_current_turn_player()
            print(f"DEBUG: 현재 턴: {current_turn_player.name if current_turn_player else 'None'}")
            
            if current_turn_player == self.game.npc:
                print("DEBUG: NPC 턴 - NPC 턴 실행")
                self._npc_turn()
            else:
                print("DEBUG: 플레이어 턴 - 플레이어 입력 대기")
    
    def show_message(self, message: str, duration: int = 2000):
        """
        메시지를 표시합니다.
        
        Args:
            message: 메시지 내용
            duration: 표시 시간 (밀리초)
        """
        self.message = message
        self.message_timer = pygame.time.get_ticks() + duration
    
    def show_dialogue(self, speaker: str, text: str, duration: int = None, wait_for_click: bool = False):
        """
        대화를 표시합니다.
        
        Args:
            speaker: 발화자
            text: 대사
            duration: 표시 시간 (밀리초), None이면 클릭 대기
            wait_for_click: True면 클릭할 때까지 대기
        """
        self.dialogue = (speaker, text)
        if wait_for_click or duration is None:
            self.dialogue_waiting_click = True
            self.dialogue_timer = 0
            self._create_dialogue_confirm_button()  # 확인 버튼 생성
        else:
            self.dialogue_waiting_click = False
            self.dialogue_timer = pygame.time.get_ticks() + duration
            self.dialogue_confirm_button = None
    
    def _create_dialogue_confirm_button(self):
        """대화 확인 버튼을 생성합니다."""
        # 대화 상자 크기 및 위치 (draw 메서드와 동일하게)
        box_width = 900
        box_height = 250
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        # 버튼 설정 (대화창 아래 중앙에 배치)
        button_width = 120
        button_height = 45
        button_spacing = 15
        
        # 두 버튼의 전체 너비 계산
        total_width = button_width * 2 + button_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        button_y = box_y + box_height + 20  # 대화창 아래 20px
        
        # 속마음 버튼 (왼쪽)
        def on_inner_thought():
            if not self.show_inner_thought:
                # 속마음 열기
                self.show_inner_thought = True
                self._create_inner_thought_close_button()
            # 이미 열려있으면 아무것도 안함 (닫기 버튼으로만 닫을 수 있음)
        
        self.dialogue_inner_thought_button = Button(
            start_x, button_y,
            button_width, button_height,
            "속마음",
            bg_color=(100, 50, 150),  # 보라색
            hover_color=(120, 70, 170),
            text_color=COLOR_WHITE,
            font=self.renderer.font_medium,
            callback=on_inner_thought
        )
        
        # 확인 버튼 (오른쪽)
        def on_confirm():
            self.dialogue = None
            self.dialogue_waiting_click = False
            self.dialogue_confirm_button = None
            self.dialogue_inner_thought_button = None
            self.show_inner_thought = False
            self.inner_thought_close_button = None
            self.inner_thought_text = ""
        
        self.dialogue_confirm_button = HighlightButton(
            start_x + button_width + button_spacing, button_y,
            button_width, button_height,
            "확인",
            font=self.renderer.font_medium,
            callback=on_confirm
        )
    
    def _create_inner_thought_close_button(self):
        """속마음 닫기 버튼을 생성합니다."""
        # 속마음 대화 상자 크기 및 위치 (draw 메서드와 동일하게)
        box_width = 900  # 700 -> 900
        box_height = 250  # 200 -> 250
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        # 버튼 설정 (속마음 대화창 아래 중앙에 배치)
        button_width = 180  # 150 -> 180 (텍스트가 삐져나가지 않게)
        button_height = 45
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = box_y + box_height + 20
        
        def on_close_inner_thought():
            self.show_inner_thought = False
            self.inner_thought_close_button = None
        
        self.inner_thought_close_button = Button(
            button_x, button_y,
            button_width, button_height,
            "속마음 닫기",
            bg_color=(100, 50, 150),
            hover_color=(120, 70, 170),
            text_color=COLOR_WHITE,
            font=self.renderer.font_medium,
            callback=on_close_inner_thought
        )
    
    def _handle_card_click(self, pos: tuple):
        """카드 클릭을 처리합니다 (라디오 버튼 방식: 하나만 선택)."""
        for i, rect in enumerate(self.card_rects):
            if rect.collidepoint(pos):
                if i in self.selected_card_indices:
                    # 이미 선택된 카드를 다시 클릭하면 선택 해제
                    self.selected_card_indices.clear()
                else:
                    # 새로운 카드 선택 (기존 선택 모두 해제하고 새로 선택)
                    self.selected_card_indices.clear()
                    self.selected_card_indices.add(i)
                break
    
    def _handle_npc_hover(self, pos: tuple):
        """NPC 카드 호버를 처리합니다."""
        self.hovered_npc_index = -1
        for i, rect in enumerate(self.npc_card_rects):
            if rect.collidepoint(pos):
                self.hovered_npc_index = i
                break
    
    def _handle_npc_click(self, pos: tuple):
        """NPC 카드 클릭을 처리합니다."""
        # NPC 카드 클릭
        for i, rect in enumerate(self.npc_card_rects):
            if rect.collidepoint(pos):
                self.selected_npc_index = i
                return
        
        # 확인 버튼 클릭
        if self.npc_confirm_button and self.npc_confirm_button.rect.collidepoint(pos):
            self._confirm_npc_selection()
    
    def _create_exit_popup_buttons(self):
        """ESC 팝업 버튼 생성"""
        popup_width = 500
        popup_height = 300
        popup_x = (SCREEN_WIDTH - popup_width) // 2
        popup_y = (SCREEN_HEIGHT - popup_height) // 2
        
        button_width = 130
        button_height = 50
        button_spacing = 20
        button_y = popup_y + popup_height - 80
        
        # 세 버튼을 중앙에 균등하게 배치
        total_width = button_width * 3 + button_spacing * 2
        start_x = popup_x + (popup_width - total_width) // 2
        
        # 타이틀로 버튼
        title_btn = Button(
            start_x, button_y,
            button_width, button_height,
            "타이틀로",
            font=self.renderer.font_normal,
            callback=lambda: self._exit_popup_action("title")
        )
        
        # 게임 종료 버튼
        exit_btn = DangerButton(
            start_x + button_width + button_spacing, button_y,
            button_width, button_height,
            "게임 종료",
            font=self.renderer.font_normal,
            callback=lambda: self._exit_popup_action("exit")
        )
        
        # 취소 버튼
        cancel_btn = Button(
            start_x + (button_width + button_spacing) * 2, button_y,
            button_width, button_height,
            "취소",
            font=self.renderer.font_normal,
            callback=lambda: self._exit_popup_action("cancel")
        )
        
        self.exit_popup_buttons = [title_btn, exit_btn, cancel_btn]

    def _exit_popup_action(self, action: str):
        """ESC 팝업 액션 처리"""
        if action == "title":
            # 타이틀 화면으로
            self.game.state = GameState.MAIN_TITLE
            self.show_exit_popup = False
        elif action == "exit":
            # 게임 종료
            self.running = False
        elif action == "cancel":
            # 팝업만 닫기
            self.show_exit_popup = False

    def _handle_exit_popup_click(self, pos: tuple):
        """ESC 팝업 버튼 클릭 처리"""
        for button in self.exit_popup_buttons:
            if button.rect.collidepoint(pos):
                if button.callback:
                    button.callback()
                break

    def _draw_exit_popup(self):
        """ESC 팝업 그리기"""
        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.renderer.screen.blit(overlay, (0, 0))
        
        # 팝업 창
        popup_width = 500
        popup_height = 300
        popup_x = (SCREEN_WIDTH - popup_width) // 2
        popup_y = (SCREEN_HEIGHT - popup_height) // 2
        
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(self.renderer.screen, (40, 40, 40), popup_rect)
        pygame.draw.rect(self.renderer.screen, (100, 100, 100), popup_rect, 3)
        
        # 타이틀
        self.renderer.draw_text(
            "⚠️ 나가시겠습니까?",
            popup_x + popup_width // 2, popup_y + 50,
            font=self.renderer.font_large, color=(255, 255, 255), center=True
        )
        
        # 설명
        self.renderer.draw_text(
            "타이틀 화면으로 돌아가거나 게임을 종료할 수 있습니다.",
            popup_x + popup_width // 2, popup_y + 110,
            font=self.renderer.font_small, color=(200, 200, 200), center=True
        )
        
        # 버튼들 그리기
        for button in self.exit_popup_buttons:
            button.draw(self.renderer.screen)

    def _confirm_npc_selection(self):
        """NPC 선택을 확정하고 게임을 시작합니다."""
        # 선택된 NPC 정보
        npc_list = [
            {
                "name": "호구",
                "composure": 1,
                "deception": 1,
                "boldness": 2,
                "recovery": 1,
                "persona": "도박판의 가장 밑바닥",
                "catchphrase": "그래, 파도! 올라갔으면 내려가고, 내려갔다가 다시 올라가는 거야!"
            },
            {
                "name": "고광렬",
                "composure": 3,
                "deception": 9,
                "boldness": 7,
                "recovery": 5,
                "persona": "대학 시절 타짜였던 노련한 플레이어",
                "catchphrase": "아유... 뭐 돈 따려고 칩니까? 재미있자고 치는 거지."
            },
            {
                "name": "아귀",
                "composure": 10,
                "deception": 9,
                "boldness": 9,
                "recovery": 10,
                "persona": "냉철하고 계산적인 베테랑 도박사",
                "catchphrase": "깨끗이 칩시다. 혹시나 뽀록나면 저 망치로 손모가지 분질러 블랑게."
            }
        ]
        
        selected_npc = npc_list[self.selected_npc_index]
        
        # NPC 생성 및 게임 초기화
        from ai.npc import NPCPlayer
        
        npc = NPCPlayer(
            name=selected_npc["name"],
            money=100_000,
            composure=selected_npc["composure"],
            deception=selected_npc["deception"],
            boldness=selected_npc["boldness"],
            recovery=selected_npc["recovery"]
        )
        npc.persona = selected_npc["persona"]
        npc.catchphrase = selected_npc["catchphrase"]
        
        # 게임에 NPC 설정
        self.game.npc = npc
        
        # 게임 시작 (카드 배분까지만)
        self.game.start_new_game()
        
        # 게임 시작 후 플레이어 이름 설정 (start_new_game이 플레이어를 초기화하기 때문에 이후에 설정)
        self.game.player.name = self.player_name if self.player_name else "플레이어"
        
        # 카드 선택 단계로 이동
        self.game.state = GameState.CARD_SELECTION
        self.selected_card_indices.clear()
        
        self.show_message("공개할 카드를 선택하세요!", 3000)
        
        print(f"\n{selected_npc['name']}와(과) 대결을 시작합니다!")
        print(f"플레이어 이름: {self.game.player.name}")
    
    def _confirm_card_selection(self):
        """플레이어의 카드 선택을 확정하고 게임을 진행합니다."""
        # 카드가 선택되지 않았으면 경고
        if len(self.selected_card_indices) == 0:
            self.show_message("카드를 선택해주세요!", 2000)
            return
        
        # 선택한 카드 공개
        selected_index = list(self.selected_card_indices)[0]
        self.game.player.cards[selected_index].reveal()
        
        # NPC도 카드 선택 (AI 로직 사용)
        npc_choice = self.game.npc.choose_card_to_reveal(self.game.player.cards)
        self.game.npc.cards[npc_choice].reveal()
        
        # 선택 초기화
        self.selected_card_indices.clear()
        
        # 베팅 단계로 이동
        self.game.state = GameState.BETTING
        
        # 1차 베팅 시작
        self.game.start_new_betting_phase(0)
        
        # 추가 베팅 버튼 생성
        self._create_additional_bet_buttons()
        
        self.show_message("1차 베팅을 시작합니다!", 2000)
        
        # first_player 확인
        print(f"DEBUG: 1차 베팅 시작 - 선: {self.game.first_player.name}")
        print(f"DEBUG: 현재 턴: {self.game.get_current_turn_player().name}")
        
        # NPC가 선이면 NPC 턴 대기 설정
        current_turn_player = self.game.get_current_turn_player()
        if current_turn_player == self.game.npc:
            print("DEBUG: NPC가 선이므로 NPC 턴 대기 설정")
            self.waiting_for_npc = True
            self.npc_action_timer = pygame.time.get_ticks()
            self.npc_action_delay = 1500
            self.show_message("NPC가 먼저 베팅합니다...", 1500)
    
    def _handle_showdown_click(self, pos):
        """쇼다운 화면에서 클릭을 처리합니다."""
        # 확정 버튼 클릭 체크
        if self.showdown_confirm_button and self.showdown_confirm_button.rect.collidepoint(pos):
            if self.selected_combo_index is not None:
                self._confirm_showdown_selection()
            return
        
        # 조합 클릭 체크
        for i, rect in enumerate(self.combo_rects):
            if rect.collidepoint(pos):
                self.selected_combo_index = i
                self.show_message(f"조합 {i + 1} 선택됨", 1000)
                return
    
    def _confirm_showdown_selection(self):
        """쇼다운에서 플레이어의 조합 선택을 확정합니다."""
        if self.selected_combo_index is None:
            self.show_message("조합을 선택해주세요!", 2000)
            return
        
        # 플레이어 조합 선택
        if not self.game.select_player_combination(self.selected_combo_index):
            self.show_message("선택 오류!", 2000)
            return
        
        # 최종 승부 판정
        self.game.finalize_showdown()
        
        # 조합 선택 초기화
        self.selected_combo_index = None
        
        self.show_message("승부가 결정되었습니다!", 2000)
    
    def _toggle_fullscreen(self):
        """전체화면 모드를 토글합니다."""
        # 현재 화면 모드 확인
        current_flags = self.renderer.screen.get_flags()
        
        if current_flags & pygame.FULLSCREEN:
            # 전체화면 -> 창 모드
            self.renderer.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        else:
            # 창 모드 -> 전체화면
            self.renderer.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.FULLSCREEN
            )
        
        # 화면 제목 유지
        pygame.display.set_caption(SCREEN_TITLE)
    
    def _advance_game_state(self):
        """게임 상태를 다음 단계로 진행합니다."""
        if self.game.state == GameState.SHOWDOWN:
            # 쇼다운 실행 (승부 결정)
            self.game.showdown()
            self.show_message("쇼다운! 패를 공개합니다!", 3000)
        elif self.game.state == GameState.ROUND_END:
            # 라운드 종료
            self.game.end_round()
            
            if self.game.state != GameState.GAME_OVER:
                # 라운드 종료 후 선택 초기화
                self.selected_combo_index = None
                self.selected_card_indices.clear()
                
                self.show_message("다음 라운드를 시작합니다!", 2000)
            else:
                self.show_message("게임 종료!", 3000)
    
    def _restart_game(self):
        """게임을 재시작하고 메인 타이틀로 돌아갑니다."""
        # 게임 상태 초기화
        self.game = SutdaGame()
        
        # UI 상태 초기화
        self.selected_combo_index = None
        self.selected_card_indices.clear()
        self.combo_rects = []
        self.card_rects = []
        
        # 버튼 초기화
        self.button_group.clear()
        self._setup_bet_buttons()
        self.card_confirm_button = None
        self.showdown_confirm_button = None
        
        # 메인 타이틀로 이동
        self.game.state = GameState.MAIN_TITLE
        
        self.show_message("메인 화면으로 돌아갑니다!", 2000)
    
    def draw(self):
        """화면을 그립니다."""
        self.renderer.clear_screen()
        
        # 게임 상태에 따라 다른 화면 표시
        # 상태-오프닝 -> 메인화면 그림
        if self.game.state == GameState.MAIN_TITLE:
            self._draw_main_title()
        elif self.game.state == GameState.CHOICE_NPC:
            self._draw_choice_npc()
        elif self.game.state == GameState.CARD_SELECTION:
            self._draw_card_selection()
        elif self.game.state == GameState.SHOWDOWN:
            self._draw_showdown()
        elif self.game.state == GameState.ROUND_END:
            self._draw_round_end()
        elif self.game.state == GameState.GAME_OVER:
            self._draw_game_over()
        else:
            self._draw_game_play()
        
        # ESC 팝업이 활성화되어 있으면 그리기 (족보 화면보다 아래)
        if self.show_exit_popup:
            self._draw_exit_popup()
        
        # 족보 버튼 그리기 (OPENING, MAIN_TITLE, CHOICE_NPC, GAME_OVER 상태가 아닐 때만)
        # 최상위 레이어로 항상 보이도록 (대화창/속마음 위에도 표시)
        should_show_hand_guide_button = self.game.state not in [
            GameState.OPENING,
            GameState.MAIN_TITLE,
            GameState.CHOICE_NPC,
            GameState.GAME_OVER
        ]
        
        if should_show_hand_guide_button and self.hand_guide_button and not self.show_hand_guide:
            self.hand_guide_button.draw(self.renderer.screen)
        
        # 족보 화면 (모든 화면 위에 렌더링, 가장 최상위)
        if self.show_hand_guide:
            self._draw_hand_guide()
        
        self.renderer.update_display()
    
    def _draw_main_title(self):
        """메뉴 화면을 그립니다."""

        self.renderer.draw_text_outlined(
            "🎴 타짜 - The Zone",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
            self.renderer.font_large, COLOR_GOLD, center=True
        )
        
        self.renderer.draw_text(
            "아무 버튼이나 누르세요",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            self.renderer.font_medium, COLOR_WHITE, center=True
        )
        
        self.renderer.draw_text(
            "ESC: 종료",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
            self.renderer.font_normal, COLOR_WHITE, center=True
        )
    
    def _draw_choice_npc(self):
        """NPC 선택 화면을 그립니다."""
        # 타이틀
        self.renderer.draw_text_outlined(
            "상대 선택",
            SCREEN_WIDTH // 2, 80,
            self.renderer.font_large, COLOR_GOLD, center=True
        )
        
        # 플레이어 이름 입력 필드
        self._draw_name_input()
        
        # NPC 목록 (예시로 3명의 NPC)
        npc_list = [            
            {
                "name": "호구",
                "desc": "도박판의 가장 밑바닥.",
                "stats": "침착 1 | 기만 1 | 대담 2 | 회복 1",
                "catchphrase": "그래, 파도! 올라갔으면 내려가고,\n내려갔다가 다시 올라가는 거야!",
                "difficulty": "초급"
            },
            {
                "name": "고광렬",
                "desc": "대학 시절 타짜였던 노련한 플레이어",
                "stats": "침착 3 | 기만 9 | 대담 7 | 회복 5",
                "catchphrase": "아유... 뭐 돈 따려고 칩니까?\n재미있자고 치는 거지.",
                "difficulty": "중급"
            },
            {
                "name": "아귀",
                "desc": "냉철하고 계산적인 베테랑 도박사",
                "stats": "침착 10 | 기만 9 | 대담 9 | 회복 10",
                "catchphrase": "깨끗이 칩시다. 혹시나 뽀록나면\n저 망치로 손모가지 분질러 블랑게.",
                "difficulty": "고급"
            }
            
        ]
        
        # NPC 카드 표시
        card_width = 350
        card_height = 300
        spacing = 40
        start_x = (SCREEN_WIDTH - (card_width * 3 + spacing * 2)) // 2
        start_y = 180
        
        # NPC 카드 영역 초기화
        self.npc_card_rects = []
        
        for i, npc_info in enumerate(npc_list):
            x = start_x + i * (card_width + spacing)
            y = start_y
            
            # NPC 정보 카드
            card_rect = pygame.Rect(x, y, card_width, card_height)
            self.npc_card_rects.append(card_rect)
            
            # 선택 여부와 호버 여부 확인
            is_selected = (i == self.selected_npc_index)
            is_hovered = (i == self.hovered_npc_index)
            
            # 배경 색상 결정 (호버 또는 선택 시 밝게)
            if is_selected or is_hovered:
                bg_color = (60, 60, 60, 230)  # 밝은 배경
            else:
                bg_color = (40, 40, 40, 220)  # 기본 배경
            
            # 카드 배경
            surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            pygame.draw.rect(surface, bg_color, surface.get_rect(), border_radius=15)
            self.renderer.screen.blit(surface, (x, y))
            
            # 테두리 (선택 시 골드, 호버 시 흰색, 기본 회색)
            if is_selected:
                border_color = COLOR_GOLD
                border_width = 4
            elif is_hovered:
                border_color = COLOR_WHITE
                border_width = 3
            else:
                border_color = COLOR_LIGHT_GRAY
                border_width = 2
            
            pygame.draw.rect(self.renderer.screen, border_color, card_rect, border_width, border_radius=15)
            
            # 난이도 뱃지
            difficulty_colors = {
                "초급": COLOR_SUCCESS,
                "중급": COLOR_WARNING,
                "고급": COLOR_DANGER
            }
            badge_color = difficulty_colors.get(npc_info["difficulty"], COLOR_WHITE)
            badge_rect = pygame.Rect(x + 10, y + 10, 60, 30)
            pygame.draw.rect(self.renderer.screen, badge_color, badge_rect, border_radius=5)
            self.renderer.draw_text(
                npc_info["difficulty"],
                x + 40, y + 25,
                self.renderer.font_small, COLOR_BLACK, center=True
            )
            
            # NPC 이름
            self.renderer.draw_text_outlined(
                npc_info["name"],
                x + card_width // 2, y + 50,
                self.renderer.font_medium, COLOR_GOLD, center=True
            )
            
            # 설명
            self.renderer.draw_text(
                npc_info["desc"],
                x + 10, y + 85,
                self.renderer.font_small, COLOR_WHITE
            )
            
            # 능력치
            self.renderer.draw_text(
                npc_info["stats"],
                x + 10, y + 115,
                self.renderer.font_small, COLOR_HIGHLIGHT
            )
            
            # 캐치프레이즈 (여러 줄 지원)
            catchphrase = f'"{npc_info["catchphrase"]}"'
            # 수동으로 줄바꿈이 있는 경우 처리
            if '\n' in catchphrase:
                lines = catchphrase.split('\n')
            else:
                # 자동 줄바꿈 (카드 폭에 맞춰)
                lines = self.renderer._wrap_text(catchphrase, card_width - 20, self.renderer.font_small)
            
            # 여러 줄 출력
            for idx, line in enumerate(lines[:4]):  # 최대 4줄
                self.renderer.draw_text(
                    line,
                    x + 10,
                    y + 145 + idx * 25,
                    self.renderer.font_small, (200, 200, 200)
                )

        # 선택 완료 버튼 (중앙 하단)
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = start_y + card_height + 60
        
        # 버튼이 없으면 생성
        if not self.npc_confirm_button:
            self.npc_confirm_button = HighlightButton(
                button_x, button_y, button_width, button_height,
                "선택 완료",
                font=self.renderer.font_medium,
                callback=self._confirm_npc_selection
            )
        else:
            # 버튼 위치 업데이트
            self.npc_confirm_button.rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # 버튼 호버 업데이트
        mouse_pos = pygame.mouse.get_pos()
        self.npc_confirm_button.update(mouse_pos)
        
        # 버튼 그리기
        self.npc_confirm_button.draw(self.renderer.screen)

        # 추가 설명
        self.renderer.draw_text(
            "상대를 클릭하여 선택하세요!",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            self.renderer.font_small, COLOR_LIGHT_GRAY, center=True
        )
    
    def _draw_name_input(self):
        """플레이어 이름 입력 UI를 그립니다."""
        input_box_width = 300
        input_box_height = 40
        input_x = 50
        input_y = 70
        
        self.name_input_rect = pygame.Rect(input_x, input_y, input_box_width, input_box_height)
        
        # 라벨
        self.renderer.draw_text(
            "플레이어 이름:",
            input_x, input_y - 25,
            self.renderer.font_small, COLOR_WHITE
        )
        
        # 입력 상자 배경
        bg_color = (50, 50, 60) if self.name_input_active else (30, 30, 40)
        pygame.draw.rect(self.renderer.screen, bg_color, self.name_input_rect, border_radius=5)
        
        # 입력 상자 테두리
        border_color = COLOR_GOLD if self.name_input_active else COLOR_LIGHT_GRAY
        pygame.draw.rect(self.renderer.screen, border_color, self.name_input_rect, 2, border_radius=5)
        
        # 입력된 텍스트
        self.renderer.draw_text(
            self.player_name,
            input_x + 10, input_y + input_box_height // 2,
            self.renderer.font_normal, COLOR_WHITE, center_y=True
        )
        
        # 활성 상태일 때 커서 표시
        if self.name_input_active and (pygame.time.get_ticks() // 500) % 2 == 0:
            text_surf = self.renderer.font_normal.render(self.player_name, True, COLOR_WHITE)
            cursor_x = input_x + 10 + text_surf.get_width()
            cursor_y = input_y + 5
            pygame.draw.line(self.renderer.screen, COLOR_WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + input_box_height - 10), 2)
    
    def _draw_card_selection(self):
        """카드 선택 화면을 그립니다."""
        # 타이틀
        self.renderer.draw_text_outlined(
            "공개할 카드 선택",
            SCREEN_WIDTH // 2, 80,
            self.renderer.font_large, COLOR_GOLD, center=True
        )
        
        # 안내 메시지
        self.renderer.draw_text(
            "공개할 카드 1장을 선택하세요",
            SCREEN_WIDTH // 2, 140,
            self.renderer.font_medium, COLOR_WHITE, center=True
        )
        
        # 플레이어 정보
        self.renderer.draw_text(
            f"플레이어: {self.game.player.name} | 소지금: {self.game.player.money:,}원",
            SCREEN_WIDTH // 2, 200,
            self.renderer.font_normal, COLOR_HIGHLIGHT, center=True
        )
        
        # 플레이어 카드 (중앙에 크게 표시)
        if self.game.player.cards:
            card_y = 280
            self.card_rects = self.card_display.draw_clickable_cards(
                self.renderer.screen,
                self.game.player.cards,
                SCREEN_WIDTH // 2 - 150, card_y,
                self.selected_card_indices,
                spacing=20, scale=1.2,
                force_reveal=True
            )
        
        # 확정 버튼 (선택된 카드가 있을 때만 활성화)
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = 550
        
        # 버튼이 없으면 생성
        if not self.card_confirm_button:
            self.card_confirm_button = HighlightButton(
                button_x, button_y, button_width, button_height,
                "선택 확정",
                font=self.renderer.font_medium,
                callback=self._confirm_card_selection
            )
        else:
            # 버튼 위치 업데이트
            self.card_confirm_button.rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # 버튼 활성화 상태 (카드가 선택되었을 때만)
        self.card_confirm_button.set_enabled(len(self.selected_card_indices) > 0)
        
        # 버튼 호버 업데이트
        mouse_pos = pygame.mouse.get_pos()
        self.card_confirm_button.update(mouse_pos)
        
        # 버튼 그리기
        self.card_confirm_button.draw(self.renderer.screen)
        
        # 하단 안내
        self.renderer.draw_text(
            "카드를 클릭하여 선택하세요",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
            self.renderer.font_small, COLOR_LIGHT_GRAY, center=True
        )
    
    def _draw_card_combination(self, x, y, cards, hand_info, scale=0.8, is_selected=False, is_clickable=False):
        """
        카드 조합과 족보를 그립니다.
        
        Args:
            x, y: 중앙 위치
            cards: 카드 2장 리스트
            hand_info: 족보 정보
            scale: 카드 크기 배율
            is_selected: 선택된 조합인지 여부
            is_clickable: 클릭 가능한지 여부
        
        Returns:
            pygame.Rect: 조합 영역의 사각형
        """
        # 카드 2장 그리기
        card_width = int(CARD_WIDTH * scale)
        card_height = int(CARD_HEIGHT * scale)
        card_spacing = 5
        total_width = card_width * 2 + card_spacing
        start_x = x - total_width // 2
        
        # 영역 사각형 (카드 + 텍스트)
        text_height = 30
        rect = pygame.Rect(start_x - 10, y - 10, total_width + 20, card_height + text_height + 20)
        
        # 선택/호버 효과
        if is_clickable:
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = rect.collidepoint(mouse_pos)
            
            if is_selected:
                # 선택된 조합: 금색 테두리
                pygame.draw.rect(self.renderer.screen, COLOR_GOLD, rect, 3)
            elif is_hovered:
                # 호버: 흰색 테두리
                pygame.draw.rect(self.renderer.screen, COLOR_WHITE, rect, 2)
            else:
                # 기본: 회색 테두리
                pygame.draw.rect(self.renderer.screen, COLOR_LIGHT_GRAY, rect, 1)
        
        for i, card in enumerate(cards):
            card_x = start_x + i * (card_width + card_spacing)
            self.card_display.draw_cards(
                self.renderer.screen,
                [card],
                card_x, y,
                revealed=[True],
                spacing=0, scale=scale
            )
        
        # 족보명 표시
        hand_name = hand_info['name'] if isinstance(hand_info, dict) else hand_info.name
        text_y = y + int(CARD_HEIGHT * scale) + 15
        
        # 선택된 조합이면 강조
        text_color = COLOR_GOLD if is_selected else (COLOR_HIGHLIGHT if is_clickable else COLOR_GOLD)
        
        self.renderer.draw_text(
            hand_name,
            x, text_y,
            self.renderer.font_small, text_color, center=True
        )
        
        return rect
    
    def _draw_showdown(self):
        """쇼다운 화면을 그립니다."""
        # 배경
        self.renderer.draw_text_outlined(
            "🃏 쇼다운! 🃏",
            SCREEN_WIDTH // 2, 40,
            self.renderer.font_large, COLOR_GOLD, center=True
        )
        
        # 현재 라운드 정보
        self.renderer.draw_text(
            f"라운드 {self.game.current_round} | 판돈: {self.game.pot:,}원",
            SCREEN_WIDTH // 2, 90,
            self.renderer.font_medium, COLOR_HIGHLIGHT, center=True
        )
        
        # 조합 영역 초기화
        self.combo_rects = []
        
        # NPC 영역 (상단)
        npc_y = 140
        self.renderer.draw_text(
            f"상대: {self.game.npc.name}",
            SCREEN_WIDTH // 2, npc_y,
            self.renderer.font_medium, COLOR_DANGER, center=True
        )
        
        # NPC는 항상 선택된 조합만 표시
        if self.game.npc_combinations and self.game.npc_selected_combo_index is not None:
            combo_y = npc_y + 40
            
            # 플레이어가 선택하기 전에는 뒷면으로
            if self.game.player_selected_combo_index is None:
                # 뒷면 카드 2장
                card_width = int(CARD_WIDTH * 0.8)
                card_spacing = 10
                start_x = SCREEN_WIDTH // 2 - card_width - card_spacing // 2
                
                for i in range(2):
                    card_x = start_x + i * (card_width + card_spacing)
                    # 뒷면 이미지 직접 그리기
                    back_img = self.card_display.card_back_image
                    if back_img:
                        scaled_back = pygame.transform.scale(back_img, (card_width, int(CARD_HEIGHT * 0.8)))
                        self.renderer.screen.blit(scaled_back, (card_x, combo_y))
                
                self.renderer.draw_text(
                    "???",
                    SCREEN_WIDTH // 2, combo_y + int(CARD_HEIGHT * 0.8) + 15,
                    self.renderer.font_small, COLOR_DANGER, center=True
                )
            else:
                # 플레이어가 선택한 후에는 NPC 조합 공개
                selected_combo = self.game.npc_combinations[self.game.npc_selected_combo_index]
                self._draw_card_combination(
                    SCREEN_WIDTH // 2, combo_y,
                    selected_combo['cards'],
                    selected_combo['hand'],
                    scale=0.8,
                    is_selected=False,
                    is_clickable=False
                )
        
        # 플레이어 영역 (하단)
        player_y = 380
        
        # 플레이어가 아직 선택하지 않았을 때
        if self.game.player_selected_combo_index is None:
            self.renderer.draw_text(
                f"플레이어: {self.game.player.name} - 2장 조합을 선택하세요",
                SCREEN_WIDTH // 2, player_y,
                self.renderer.font_medium, COLOR_SUCCESS, center=True
            )
            
            # 플레이어 카드 조합들 표시 (클릭 가능)
            if len(self.game.player.cards) == 3 and self.game.player_combinations:
                combo_y = player_y + 35
                combo_spacing = 220
                start_x = SCREEN_WIDTH // 2 - combo_spacing
                
                for i, combo in enumerate(self.game.player_combinations):
                    combo_x = start_x + i * combo_spacing
                    rect = self._draw_card_combination(
                        combo_x, combo_y,
                        combo['cards'],
                        combo['hand'],
                        scale=0.7,
                        is_selected=(i == self.selected_combo_index),
                        is_clickable=True
                    )
                    self.combo_rects.append(rect)
            
            # 확정 버튼
            button_width = 200
            button_height = 50
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            button_y = player_y + 230
            
            if not self.showdown_confirm_button:
                self.showdown_confirm_button = HighlightButton(
                    button_x, button_y, button_width, button_height,
                    "선택 확정",
                    font=self.renderer.font_medium,
                    callback=self._confirm_showdown_selection
                )
            else:
                self.showdown_confirm_button.rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # 버튼 활성화 (조합이 선택되었을 때만)
            self.showdown_confirm_button.set_enabled(self.selected_combo_index is not None)
            
            # 버튼 호버 업데이트
            mouse_pos = pygame.mouse.get_pos()
            self.showdown_confirm_button.update(mouse_pos)
            self.showdown_confirm_button.draw(self.renderer.screen)
            
            # 안내 메시지
            self.renderer.draw_text(
                "조합을 클릭하여 선택하세요",
                SCREEN_WIDTH // 2, button_y + 70,
                self.renderer.font_small, COLOR_LIGHT_GRAY, center=True
            )
        else:
            # 플레이어가 선택한 후
            self.renderer.draw_text(
                f"플레이어: {self.game.player.name} - 선택 완료!",
                SCREEN_WIDTH // 2, player_y,
                self.renderer.font_medium, COLOR_SUCCESS, center=True
            )
            
            # 선택한 조합만 표시
            if self.game.player_combinations:
                combo_y = player_y + 60
                selected_combo = self.game.player_combinations[self.game.player_selected_combo_index]
                self._draw_card_combination(
                    SCREEN_WIDTH // 2, combo_y,
                    selected_combo['cards'],
                    selected_combo['hand'],
                    scale=1.0,
                    is_selected=True,
                    is_clickable=False
                )
    
    def _draw_round_end(self):
        """라운드 종료 화면을 그립니다."""
        # 승자 확인
        winner = self.game.last_winner
        
        # 배경
        if winner == self.game.player:
            title_text = "🏆 승리! 🏆"
            title_color = COLOR_SUCCESS
            winner_name = self.game.player.name
        elif winner == self.game.npc:
            title_text = "😢 패배... 😢"
            title_color = COLOR_DANGER
            winner_name = self.game.npc.name
        else:
            title_text = "무승부"
            title_color = COLOR_WARNING
            winner_name = None
        
        self.renderer.draw_text_outlined(
            title_text,
            SCREEN_WIDTH // 2, 40,
            self.renderer.font_large, title_color, center=True
        )
        
        # 승자 정보와 획득 판돈
        info_y = 100
        
        # 다이 정보 표시
        if self.game.player.has_folded:
            self.renderer.draw_text(
                f"❌ {self.game.player.name}가 다이했습니다 ❌",
                SCREEN_WIDTH // 2, info_y,
                self.renderer.font_medium, COLOR_DANGER, center=True
            )
            info_y += 45
        elif self.game.npc.has_folded:
            self.renderer.draw_text(
                f"✅ {self.game.npc.name}가 다이했습니다 ✅",
                SCREEN_WIDTH // 2, info_y,
                self.renderer.font_medium, COLOR_SUCCESS, center=True
            )
            info_y += 45
        
        if winner_name:
            self.renderer.draw_text(
                f"{winner_name} 승리!",
                SCREEN_WIDTH // 2, info_y,
                self.renderer.font_medium, COLOR_HIGHLIGHT, center=True
            )
            info_y += 40
        
        if winner:
            self.renderer.draw_text(
                f"획득 판돈: {self.game.pot:,}원",
                SCREEN_WIDTH // 2, info_y,
                self.renderer.font_medium, COLOR_GOLD, center=True
            )
            info_y += 50
        else:
            # 무승부일 때 메시지
            self.renderer.draw_text(
                f"판돈 {self.game.pot:,}원을 묻고 다음 라운드로!",
                SCREEN_WIDTH // 2, info_y,
                self.renderer.font_medium, COLOR_WARNING, center=True
            )
            info_y += 50
        
        # 다이하지 않았을 때만 패 비교 표시
        if not self.game.player.has_folded and not self.game.npc.has_folded:
            # NPC 패 표시 (상단)
            npc_y = info_y
            self.renderer.draw_text(
                f"{self.game.npc.name}의 패:",
                SCREEN_WIDTH // 2, npc_y,
                self.renderer.font_normal, COLOR_DANGER, center=True
            )
            
            # NPC가 선택한 조합 표시
            if self.game.npc_combinations and self.game.npc_selected_combo_index is not None:
                combo_y = npc_y + 35
                selected_combo = self.game.npc_combinations[self.game.npc_selected_combo_index]
                self._draw_card_combination(
                    SCREEN_WIDTH // 2, combo_y,
                    selected_combo['cards'],
                    selected_combo['hand'],
                    scale=0.75,
                    is_selected=False,
                    is_clickable=False
                )
            
            # 플레이어 패 표시 (하단)
            # 카드 높이 (0.75 scale) + 족보 텍스트 + 여백
            player_y = combo_y + int(CARD_HEIGHT * 0.75) + 60
            self.renderer.draw_text(
                f"{self.game.player.name}의 패:",
                SCREEN_WIDTH // 2, player_y,
                self.renderer.font_normal, COLOR_SUCCESS, center=True
            )
            
            # 플레이어가 선택한 조합 표시
            if self.game.player_combinations and self.game.player_selected_combo_index is not None:
                combo_y = player_y + 35
                selected_combo = self.game.player_combinations[self.game.player_selected_combo_index]
                self._draw_card_combination(
                    SCREEN_WIDTH // 2, combo_y,
                    selected_combo['cards'],
                    selected_combo['hand'],
                    scale=0.75,
                    is_selected=False,
                    is_clickable=False
                )
            
            # 소지금 표시 위치 조정
            money_y = combo_y + int(CARD_HEIGHT * 0.75) + 60
        else:
            # 다이했을 때도 카드 표시
            if self.game.player.has_folded or self.game.npc.has_folded:
                # 다이한 사람의 카드 표시
                fold_y = info_y
                
                if self.game.player.has_folded:
                    # 플레이어가 다이 -> NPC 카드만 표시
                    self.renderer.draw_text(
                        f"{self.game.npc.name}의 패:",
                        SCREEN_WIDTH // 2, fold_y,
                        self.renderer.font_normal, COLOR_SUCCESS, center=True
                    )
                    fold_y += 35
                    
                    # NPC 카드 그리기
                    if self.game.npc.cards and len(self.game.npc.cards) >= 2:
                        card_width = int(CARD_WIDTH * 0.6)
                        card_height = int(CARD_HEIGHT * 0.6)
                        total_width = card_width * len(self.game.npc.cards) + 10 * (len(self.game.npc.cards) - 1)
                        start_x = (SCREEN_WIDTH - total_width) // 2
                        
                        for i, card in enumerate(self.game.npc.cards):
                            x = start_x + i * (card_width + 10)
                            self.card_display.draw_card(self.renderer.screen, card, x, fold_y, scale=0.6)
                    
                    fold_y += card_height + 40
                    
                else:
                    # NPC가 다이 -> 플레이어 카드만 표시
                    self.renderer.draw_text(
                        f"{self.game.player.name}의 패:",
                        SCREEN_WIDTH // 2, fold_y,
                        self.renderer.font_normal, COLOR_SUCCESS, center=True
                    )
                    fold_y += 35
                    
                    # 플레이어 카드 그리기
                    if self.game.player.cards and len(self.game.player.cards) >= 2:
                        card_width = int(CARD_WIDTH * 0.6)
                        card_height = int(CARD_HEIGHT * 0.6)
                        total_width = card_width * len(self.game.player.cards) + 10 * (len(self.game.player.cards) - 1)
                        start_x = (SCREEN_WIDTH - total_width) // 2
                        
                        for i, card in enumerate(self.game.player.cards):
                            x = start_x + i * (card_width + 10)
                            self.card_display.draw_card(self.renderer.screen, card, x, fold_y, scale=0.6)
                    
                    fold_y += card_height + 40
                
                money_y = fold_y
            else:
                money_y = info_y + 20
        
        # 현재 소지금
        player_money_color = COLOR_SUCCESS if self.game.player.money > 0 else COLOR_DANGER
        npc_money_color = COLOR_SUCCESS if self.game.npc.money > 0 else COLOR_DANGER
        
        self.renderer.draw_text(
            f"{self.game.player.name} 소지금: {self.game.player.money:,}원",
            SCREEN_WIDTH // 2, money_y,
            self.renderer.font_normal, player_money_color, center=True
        )
        
        self.renderer.draw_text(
            f"{self.game.npc.name} 소지금: {self.game.npc.money:,}원",
            SCREEN_WIDTH // 2, money_y + 35,
            self.renderer.font_normal, npc_money_color, center=True
        )
        
        # 라운드 정보
        self.renderer.draw_text(
            f"라운드 {self.game.current_round} 종료",
            SCREEN_WIDTH // 2, money_y + 80,
            self.renderer.font_small, COLOR_LIGHT_GRAY, center=True
        )
        
        # 다음 단계 안내
        if self.game.state == GameState.GAME_OVER:
            next_text = "게임이 종료되었습니다..."
        else:
            next_text = "다음 라운드를 시작합니다... (클릭)"
        
        self.renderer.draw_text(
            next_text,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60,
            self.renderer.font_normal, COLOR_WARNING, center=True
        )
    
    def _draw_game_over(self):
        """게임 오버 화면을 그립니다."""
        self.game.show_final_result()
        
        self.renderer.draw_text_outlined(
            "게임 종료",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
            self.renderer.font_large, COLOR_GOLD, center=True
        )
        
        # 최종 결과
        if self.game.player.money > self.game.npc.money:
            result_text = "🏆 승리! 🏆"
            result_color = COLOR_SUCCESS
        elif self.game.player.money < self.game.npc.money:
            result_text = "패배..."
            result_color = COLOR_DANGER
        else:
            result_text = "무승부"
            result_color = COLOR_WHITE
        
        self.renderer.draw_text_outlined(
            result_text,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            self.renderer.font_large, result_color, center=True
        )
        
        self.renderer.draw_text(
            f"최종 금액: {self.game.player.money:,}원",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80,
            self.renderer.font_medium, COLOR_WHITE, center=True
        )
        
        # 안내 메시지
        self.renderer.draw_text(
            "클릭하여 메인 화면으로",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140,
            self.renderer.font_normal, COLOR_HIGHLIGHT, center=True
        )
        
        self.renderer.draw_text(
            "ESC: 종료",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 170,
            self.renderer.font_small, COLOR_LIGHT_GRAY, center=True
        )
    
    def _draw_game_play(self):
        """게임 플레이 화면을 그립니다."""
        # 테이블
        self.renderer.draw_table()
        
        # 라운드 정보
        self.renderer.draw_round_info(self.game.current_round, self.game.total_rounds)
        
        # NPC 정보 및 카드
        self.renderer.draw_player_info(
            self.game.npc.name,
            self.game.npc.money,
            self.game.npc.current_bet,
            100, 110,
            self.game.first_player == self.game.npc
        )
        
        # NPC 카드 (공개된 카드는 앞면, 나머지는 뒷면)
        if self.game.npc.cards:
            # 각 카드의 is_revealed 상태에 따라 공개 여부 결정
            npc_revealed = [card.is_revealed for card in self.game.npc.cards]
            self.card_display.draw_cards(
                self.renderer.screen,
                self.game.npc.cards,
                SCREEN_WIDTH // 2 - 120, 120,
                spacing=10, revealed=npc_revealed, scale=0.8
            )
        
        # 플레이어 정보 및 카드
        self.renderer.draw_player_info(
            self.game.player.name,
            self.game.player.money,
            self.game.player.current_bet,
            100, 550,
            self.game.first_player == self.game.player
        )
        
        # 플레이어 카드 (클릭 가능)
        if self.game.player.cards:
            self.card_rects = self.card_display.draw_clickable_cards(
                self.renderer.screen,
                self.game.player.cards,
                SCREEN_WIDTH // 2 - 120, 540,
                self.selected_card_indices,
                spacing=10, scale=0.8
            )
        
        # 판돈
        self.renderer.draw_pot_info(self.game.pot)
        
        # 베팅 히스토리
        if self.game.state == GameState.BETTING and self.game.bet_history:
            self._draw_bet_history()
        
        # 베팅 버튼
        if self.game.state == GameState.BETTING:
            self.button_group.draw(self.renderer.screen)
        
        # NPC 대기 중 표시
        if self.waiting_for_npc:
            # 반투명 오버레이
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill(COLOR_BLACK)
            self.renderer.screen.blit(overlay, (0, 0))
            
            # 대기 중 텍스트
            self.renderer.draw_text_outlined(
                "NPC 행동 대기 중...",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                self.renderer.font_large, COLOR_WARNING, center=True
            )
        
        # 메시지
        if self.message:
            self.renderer.draw_message(
                self.message,
                SCREEN_WIDTH // 2, 280,
                self.renderer.font_medium, COLOR_HIGHLIGHT
            )
        
        # 대화 (개선된 스타일)
        if self.dialogue:
            speaker, text = self.dialogue
            
            # 반투명 커튼
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(COLOR_BLACK)
            self.renderer.screen.blit(overlay, (0, 0))
            
            # 대화 상자 크기 및 위치
            box_width = 900
            box_height = 250
            box_x = (SCREEN_WIDTH - box_width) // 2
            box_y = (SCREEN_HEIGHT - box_height) // 2
            
            # 대화 상자 배경 (반투명 검정)
            dialog_bg = pygame.Surface((box_width, box_height))
            dialog_bg.set_alpha(220)
            dialog_bg.fill((20, 20, 20))
            self.renderer.screen.blit(dialog_bg, (box_x, box_y))
            
            # 대화 상자 테두리 (금색)
            pygame.draw.rect(
                self.renderer.screen,
                COLOR_GOLD,
                (box_x, box_y, box_width, box_height),
                4
            )
            
            # 발화자 이름 (큰 글씨)
            self.renderer.draw_text_outlined(
                speaker,
                box_x + 30, box_y + 25,
                self.renderer.font_large, COLOR_GOLD
            )
            
            # 대사 텍스트 자동 줄바꿈 처리
            text_y = box_y + 80
            max_width = box_width - 60  # 좌우 여백 30씩
            line_height = 40
            max_lines = 3  # 최대 3줄까지만 표시
            
            # 텍스트를 단어 단위로 분리하여 자동 줄바꿈
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                # 텍스트 너비 측정
                text_surface = self.renderer.font_medium.render(test_line, True, COLOR_WHITE)
                if text_surface.get_width() <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # 최대 줄 수 제한
            lines = lines[:max_lines]
            
            # 줄 그리기
            for line in lines:
                self.renderer.draw_text(
                    line,
                    box_x + 30, text_y,
                    self.renderer.font_medium, COLOR_WHITE
                )
                text_y += line_height
            
            # 버튼 그리기
            if self.dialogue_waiting_click:
                if self.dialogue_inner_thought_button:
                    self.dialogue_inner_thought_button.draw(self.renderer.screen)
                if self.dialogue_confirm_button:
                    self.dialogue_confirm_button.draw(self.renderer.screen)
        
        # 속마음 대화창 (대화창 위에 레이어로 표시)
        if self.show_inner_thought and self.inner_thought_text:
            # 추가 반투명 레이어 (연한 보라색, 불투명도 높임)
            overlay2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay2.set_alpha(230)  # 불투명도 증가 (180 -> 230)
            overlay2.fill((60, 40, 80))  # 연한 보라색
            self.renderer.screen.blit(overlay2, (0, 0))
            
            # 속마음 대화 상자 크기 및 위치 (대화창과 동일한 크기)
            inner_box_width = 900  # 700 -> 900
            inner_box_height = 250  # 200 -> 250
            inner_box_x = (SCREEN_WIDTH - inner_box_width) // 2
            inner_box_y = (SCREEN_HEIGHT - inner_box_height) // 2
            
            # 속마음 대화 상자 배경 (진한 보라색)
            inner_dialog_bg = pygame.Surface((inner_box_width, inner_box_height))
            inner_dialog_bg.set_alpha(230)
            inner_dialog_bg.fill((50, 20, 80))
            self.renderer.screen.blit(inner_dialog_bg, (inner_box_x, inner_box_y))
            
            # 속마음 대화 상자 테두리 (밝은 보라색)
            pygame.draw.rect(
                self.renderer.screen,
                (150, 100, 200),
                (inner_box_x, inner_box_y, inner_box_width, inner_box_height),
                4
            )
            
            # 속마음 제목
            self.renderer.draw_text_outlined(
                "💭 속마음",
                inner_box_x + 30, inner_box_y + 25,
                self.renderer.font_large, (200, 150, 255)
            )
            
            # 속마음 텍스트 자동 줄바꿈
            inner_text_y = inner_box_y + 80
            inner_max_width = inner_box_width - 60
            inner_line_height = 35
            inner_max_lines = 3
            
            # 텍스트 줄바꿈 처리
            inner_words = self.inner_thought_text.split()
            inner_lines = []
            inner_current_line = ""
            
            for word in inner_words:
                test_line = inner_current_line + (" " if inner_current_line else "") + word
                text_surface = self.renderer.font_medium.render(test_line, True, COLOR_WHITE)
                if text_surface.get_width() <= inner_max_width:
                    inner_current_line = test_line
                else:
                    if inner_current_line:
                        inner_lines.append(inner_current_line)
                    inner_current_line = word
            
            if inner_current_line:
                inner_lines.append(inner_current_line)
            
            inner_lines = inner_lines[:inner_max_lines]
            
            # 줄 그리기
            for line in inner_lines:
                self.renderer.draw_text(
                    line,
                    inner_box_x + 30, inner_text_y,
                    self.renderer.font_medium, (230, 230, 230)
                )
                inner_text_y += inner_line_height
            
            # 속마음 닫기 버튼 그리기
            if self.inner_thought_close_button:
                self.inner_thought_close_button.draw(self.renderer.screen)
        
        # 안내
        self.renderer.draw_text(
            "ESC: 메뉴",
            10, SCREEN_HEIGHT - 30,
            self.renderer.font_small, COLOR_WHITE
        )
    

    def update(self):
        """화면을 업데이트합니다."""
        # 대화창이 클릭 대기 중이면 다른 프로세스 멈춤
        if self.dialogue_waiting_click:
            return
        
        # 메시지 타이머
        if self.message and pygame.time.get_ticks() > self.message_timer:
            self.message = ""
        
        # 대화 타이머 (클릭 대기가 아닌 경우에만)
        if self.dialogue and not self.dialogue_waiting_click:
            if self.dialogue_timer > 0 and pygame.time.get_ticks() > self.dialogue_timer:
                self.dialogue = None
        
        # 대화 확인 버튼 업데이트
        if self.dialogue_confirm_button:
            mouse_pos = pygame.mouse.get_pos()
            self.dialogue_confirm_button.update(mouse_pos)
        
        # 대화 속마음 버튼 업데이트
        if self.dialogue_inner_thought_button:
            mouse_pos = pygame.mouse.get_pos()
            self.dialogue_inner_thought_button.update(mouse_pos)
        
        # 속마음 닫기 버튼 업데이트
        if self.inner_thought_close_button:
            mouse_pos = pygame.mouse.get_pos()
            self.inner_thought_close_button.update(mouse_pos)
        
        # NPC 턴 대기 처리
        if self.waiting_for_npc:
            current_time = pygame.time.get_ticks()
            if current_time - self.npc_action_timer >= self.npc_action_delay:
                self.waiting_for_npc = False
                self._execute_pending_action()
        
        # 버튼 상태 업데이트
        if self.game.state == GameState.BETTING:
            self._update_button_states()
        
        # 버튼 업데이트
        mouse_pos = pygame.mouse.get_pos()
        self.button_group.update(mouse_pos)
        
        # 카드 선택 확정 버튼 업데이트
        if self.card_confirm_button and self.game.state == GameState.CARD_SELECTION:
            self.card_confirm_button.update(mouse_pos)

    def run(self):
        """게임 루프를 실행합니다."""
        while self.running:
            if not self.handle_events():
                break
            
            self.update()
            self.draw()
            self.renderer.tick()
        
        self.renderer.quit()


# 테스트
if __name__ == "__main__":
    print("=== GameScreen 테스트 ===\n")
    
    from ai.npc import NPCPlayer
    
    # 게임 생성
    npc = NPCPlayer("고니", 100000, 7, 8, 6, 5)
    game = SutdaGame("플레이어", npc)
    
    # 게임 시작
    # game.start_new_game()
    
    # 게임 화면 실행
    screen = GameScreen(game)
    screen.run()
    
    print("테스트 종료")
