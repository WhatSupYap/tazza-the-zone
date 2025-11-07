"""
화면 렌더링 관리자
Pygame 화면 초기화 및 기본 렌더링 기능
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FPS,
    COLOR_BG, COLOR_TEXT, COLOR_TABLE, COLOR_HIGHLIGHT,
    COLOR_GOLD, COLOR_DANGER, COLOR_SUCCESS, COLOR_WHITE, COLOR_BLACK
)


class Renderer:
    """화면 렌더링 관리 클래스"""
    
    def __init__(self):
        """렌더러를 초기화합니다."""
        # Pygame 초기화
        pygame.init()
        pygame.font.init()
        
        # 화면 설정
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        
        # 시계 (FPS 제어)
        self.clock = pygame.time.Clock()
        
        # 폰트 로딩
        self._load_fonts()
        
        # 화면 영역 정의
        self._define_areas()
    
    def _load_fonts(self):
        """폰트를 로드합니다."""
        try:
            # 한글 폰트 로딩 (시스템 폰트 사용)
            self.font_large = pygame.font.SysFont('malgungothic', 48, bold=True)
            self.font_medium = pygame.font.SysFont('malgungothic', 32, bold=True)
            self.font_normal = pygame.font.SysFont('malgungothic', 24)
            self.font_small = pygame.font.SysFont('malgungothic', 18)
        except:
            # 폴백: 기본 폰트
            print("경고: 맑은 고딕 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_normal = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
    
    def _define_areas(self):
        """화면 영역을 정의합니다."""
        # 타이틀 영역
        self.title_area = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        
        # NPC 영역 (상단)
        self.npc_area = pygame.Rect(50, 100, SCREEN_WIDTH - 100, 200)
        
        # 테이블 영역 (중앙)
        self.table_area = pygame.Rect(200, 320, SCREEN_WIDTH - 400, 180)
        
        # 플레이어 영역 (하단)
        self.player_area = pygame.Rect(50, 520, SCREEN_WIDTH - 100, 200)
        
        # 버튼 영역 (우측 하단)
        self.button_area = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 180, 230, 160)
    
    def clear_screen(self):
        """화면을 지웁니다."""
        self.screen.fill(COLOR_BG)
    
    def draw_table(self):
        """테이블을 그립니다."""
        # 테이블 배경 (타원)
        pygame.draw.ellipse(self.screen, COLOR_TABLE, self.table_area)
        pygame.draw.ellipse(self.screen, COLOR_GOLD, self.table_area, 3)
    
    def draw_text(self, text: str, x: int, y: int, 
                  font=None, color=COLOR_TEXT, center=False, center_y=False):
        """
        텍스트를 그립니다 (이모지 지원).
        
        Args:
            text: 텍스트 내용
            x, y: 위치
            font: 폰트 (None이면 기본 폰트)
            color: 색상
            center: 중앙 정렬 여부
            center_y: Y축만 중앙 정렬 여부
        """
        if font is None:
            font = self.font_normal
        
        # 텍스트에 이모지가 포함된 경우 혼합 렌더링
        if self._contains_emoji(str(text)):
            # 이모지와 일반 텍스트를 분리하여 렌더링
            return self._draw_mixed_text(str(text), x, y, font, color, center)
        else:
            # 일반 텍스트 렌더링
            text_surface = font.render(str(text), True, color)
            text_rect = text_surface.get_rect()
            
            if center:
                text_rect.center = (x, y)
            elif center_y:
                text_rect.left = x
                text_rect.centery = y
            else:
                text_rect.topleft = (x, y)
            
            self.screen.blit(text_surface, text_rect)
            return text_rect
    
    def _draw_mixed_text(self, text: str, x: int, y: int, font, color, center=False):
        """
        이모지와 일반 텍스트가 섞인 텍스트를 렌더링합니다.
        
        Args:
            text: 렌더링할 텍스트
            x, y: 시작 위치
            font: 기본 폰트
            color: 색상
            center: 중앙 정렬 여부
            
        Returns:
            전체 텍스트의 사각형
        """
        # 이모지 폰트 준비
        try:
            emoji_font = pygame.font.SysFont('segoeuiemoji', font.get_height())
        except:
            emoji_font = font
        
        # 텍스트를 문자별로 분리하고 각각 렌더링
        segments = []
        current_segment = ""
        is_emoji_segment = False
        
        for char in text:
            char_is_emoji = self._is_emoji_char(char)
            
            if not current_segment:
                # 첫 문자
                current_segment = char
                is_emoji_segment = char_is_emoji
            elif char_is_emoji == is_emoji_segment:
                # 같은 타입이면 추가
                current_segment += char
            else:
                # 타입이 바뀌면 저장하고 새로 시작
                segments.append((current_segment, is_emoji_segment))
                current_segment = char
                is_emoji_segment = char_is_emoji
        
        # 마지막 세그먼트 추가
        if current_segment:
            segments.append((current_segment, is_emoji_segment))
        
        # 각 세그먼트를 렌더링하여 서피스 생성
        surfaces = []
        total_width = 0
        max_height = 0
        
        for segment_text, is_emoji in segments:
            segment_font = emoji_font if is_emoji else font
            surface = segment_font.render(segment_text, True, color)
            surfaces.append(surface)
            total_width += surface.get_width()
            max_height = max(max_height, surface.get_height())
        
        # 중앙 정렬이면 시작 위치 조정
        if center:
            current_x = x - total_width // 2
            current_y = y - max_height // 2
        else:
            current_x = x
            current_y = y
        
        # 각 세그먼트를 순서대로 그리기
        for surface in surfaces:
            self.screen.blit(surface, (current_x, current_y))
            current_x += surface.get_width()
        
        # 전체 영역 반환
        if center:
            return pygame.Rect(x - total_width // 2, y - max_height // 2, total_width, max_height)
        else:
            return pygame.Rect(x, y, total_width, max_height)
    
    def _is_emoji_char(self, char: str) -> bool:
        """
        개별 문자가 이모지인지 확인합니다.
        
        Args:
            char: 확인할 문자
            
        Returns:
            이모지 여부
        """
        code = ord(char)
        return (0x1F300 <= code <= 0x1F9FF or  # 이모지와 기호
                0x2600 <= code <= 0x26FF or    # 기타 기호
                0x2700 <= code <= 0x27BF or    # Dingbats
                0xFE00 <= code <= 0xFE0F or    # 변형 선택자
                0x1F000 <= code <= 0x1F0FF)    # 마작 타일 등
    
    def _contains_emoji(self, text: str) -> bool:
        """
        텍스트에 이모지가 포함되어 있는지 확인합니다.
        
        Args:
            text: 확인할 텍스트
            
        Returns:
            이모지 포함 여부
        """
        return any(self._is_emoji_char(char) for char in text)
    
    def draw_text_outlined(self, text: str, x: int, y: int, 
                          font=None, color=COLOR_TEXT, 
                          outline_color=COLOR_BLACK, center=False):
        """
        외곽선이 있는 텍스트를 그립니다.
        
        Args:
            text: 텍스트 내용
            x, y: 위치
            font: 폰트
            color: 텍스트 색상
            outline_color: 외곽선 색상
            center: 중앙 정렬 여부
        """
        if font is None:
            font = self.font_normal
        
        # 외곽선 (4방향)
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            self.draw_text(text, x + dx, y + dy, font, outline_color, center)
        
        # 메인 텍스트
        return self.draw_text(text, x, y, font, color, center)
    
    def draw_box(self, rect: pygame.Rect, color, border_color=None, border_width=2):
        """
        박스를 그립니다.
        
        Args:
            rect: 박스 영역
            color: 배경 색상
            border_color: 테두리 색상 (None이면 테두리 없음)
            border_width: 테두리 두께
        """
        pygame.draw.rect(self.screen, color, rect)
        
        if border_color:
            pygame.draw.rect(self.screen, border_color, rect, border_width)
    
    def draw_rounded_box(self, rect: pygame.Rect, color, 
                        border_color=None, border_width=2, radius=10):
        """
        둥근 모서리 박스를 그립니다.
        
        Args:
            rect: 박스 영역
            color: 배경 색상
            border_color: 테두리 색상
            border_width: 테두리 두께
            radius: 모서리 반경
        """
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        
        if border_color:
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=radius)
    
    def draw_info_box(self, text: str, x: int, y: int, 
                     width: int = 200, height: int = 60,
                     bg_color=None, text_color=COLOR_TEXT):
        """
        정보 박스를 그립니다.
        
        Args:
            text: 표시할 텍스트
            x, y: 위치
            width, height: 크기
            bg_color: 배경 색상
            text_color: 텍스트 색상
        """
        if bg_color is None:
            bg_color = (30, 30, 30, 200)  # 반투명 검정
        
        rect = pygame.Rect(x, y, width, height)
        
        # 반투명 박스
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, bg_color, surface.get_rect(), border_radius=10)
        self.screen.blit(surface, (x, y))
        
        # 테두리
        pygame.draw.rect(self.screen, COLOR_GOLD, rect, 2, border_radius=10)
        
        # 텍스트
        self.draw_text(text, x + width // 2, y + height // 2, 
                      self.font_normal, text_color, center=True)
    
    def draw_progress_bar(self, x: int, y: int, width: int, height: int,
                         progress: float, bg_color=(50, 50, 50),
                         fill_color=COLOR_SUCCESS, border_color=COLOR_WHITE):
        """
        프로그레스 바를 그립니다.
        
        Args:
            x, y: 위치
            width, height: 크기
            progress: 진행도 (0.0 ~ 1.0)
            bg_color: 배경 색상
            fill_color: 채움 색상
            border_color: 테두리 색상
        """
        # 배경
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=5)
        
        # 진행 바
        fill_width = int(width * max(0.0, min(1.0, progress)))
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=5)
        
        # 테두리
        pygame.draw.rect(self.screen, border_color, bg_rect, 2, border_radius=5)
    
    def draw_player_info(self, name: str, money: int, bet: int,
                        x: int, y: int, is_first=False):
        """
        플레이어 정보를 그립니다.
        
        Args:
            name: 플레이어 이름
            money: 소지금
            bet: 현재 베팅액
            x, y: 위치
            is_first: 선 여부
        """
        # 이름 (선 표시)
        name_text = f"⭐ {name}" if is_first else name
        self.draw_text_outlined(name_text, x, y, self.font_medium, COLOR_GOLD)
        
        # 소지금
        money_text = f"💰 {money:,}원"
        self.draw_text(money_text, x, y + 40, self.font_normal, COLOR_WHITE)
        
        # 현재 베팅
        if bet > 0:
            bet_text = f"베팅: {bet:,}원"
            self.draw_text(bet_text, x, y + 70, self.font_normal, COLOR_HIGHLIGHT)
    
    def draw_pot_info(self, pot: int):
        """
        판돈 정보를 그립니다.
        
        Args:
            pot: 판돈
        """
        # 테이블 중앙에 표시
        center_x = SCREEN_WIDTH // 2
        center_y = self.table_area.centery
        
        # 판돈 텍스트
        pot_text = f"판돈: {pot:,}원"
        self.draw_text_outlined(pot_text, center_x, center_y, 
                               self.font_large, COLOR_GOLD, center=True)
    
    def draw_round_info(self, current_round: int, total_rounds: int):
        """
        라운드 정보를 그립니다.
        
        Args:
            current_round: 현재 라운드
            total_rounds: 총 라운드
        """
        round_text = f"Round {current_round} / {total_rounds}"
        self.draw_text_outlined(round_text, SCREEN_WIDTH // 2, 40, 
                               self.font_medium, COLOR_WHITE, center=True)
    
    def draw_message(self, message: str, x: int = None, y: int = None,
                    font=None, color=COLOR_HIGHLIGHT, center=True):
        """
        메시지를 그립니다.
        
        Args:
            message: 메시지 내용
            x, y: 위치 (None이면 화면 중앙)
            font: 폰트
            color: 색상
            center: 중앙 정렬 여부
        """
        if x is None:
            x = SCREEN_WIDTH // 2
        if y is None:
            y = SCREEN_HEIGHT // 2
        if font is None:
            font = self.font_large
        
        self.draw_text_outlined(message, x, y, font, color, center=center)
    
    def draw_dialogue(self, speaker: str, text: str, x: int, y: int, 
                     width: int = 400):
        """
        대화를 그립니다.
        
        Args:
            speaker: 발화자
            text: 대사
            x, y: 위치
            width: 폭
        """
        # 대화창 배경
        height = 80
        bg_rect = pygame.Rect(x, y, width, height)
        
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 200), surface.get_rect(), border_radius=10)
        self.screen.blit(surface, (x, y))
        
        pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, bg_rect, 2, border_radius=10)
        
        # 발화자 이름
        self.draw_text(f"{speaker}:", x + 10, y + 10, 
                      self.font_small, COLOR_GOLD)
        
        # 대사 (여러 줄 처리)
        lines = self._wrap_text(text, width - 20, self.font_normal)
        for i, line in enumerate(lines[:2]):  # 최대 2줄
            self.draw_text(line, x + 10, y + 35 + i * 25, 
                          self.font_normal, COLOR_WHITE)
    
    def _wrap_text(self, text: str, max_width: int, font) -> list:
        """
        텍스트를 여러 줄로 나눕니다.
        
        Args:
            text: 원본 텍스트
            max_width: 최대 폭
            font: 폰트
            
        Returns:
            줄 리스트
        """
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def update_display(self):
        """화면을 업데이트합니다."""
        pygame.display.flip()
    
    def tick(self):
        """FPS를 제어합니다."""
        self.clock.tick(FPS)
    
    def quit(self):
        """Pygame을 종료합니다."""
        pygame.quit()


# 테스트
if __name__ == "__main__":
    print("=== Renderer 테스트 ===\n")
    
    renderer = Renderer()
    
    running = True
    test_progress = 0.0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 화면 그리기
        renderer.clear_screen()
        
        # 타이틀
        renderer.draw_text_outlined("타짜 - The Zone", SCREEN_WIDTH // 2, 40,
                                   renderer.font_large, COLOR_GOLD, center=True)
        
        # 테이블
        renderer.draw_table()
        
        # 플레이어 정보
        renderer.draw_player_info("플레이어", 95000, 5000, 100, 550, False)
        renderer.draw_player_info("고니", 98000, 5000, 100, 120, True)
        
        # 판돈
        renderer.draw_pot_info(10000)
        
        # 라운드 정보
        renderer.draw_round_info(3, 10)
        
        # 메시지
        renderer.draw_message("베팅하세요!", SCREEN_WIDTH // 2, 280, 
                            renderer.font_medium, COLOR_HIGHLIGHT)
        
        # 대화
        renderer.draw_dialogue("고니", "대학 시절 타짜였지. 이 패로는 좀 힘들겠는데?", 
                              450, 150, 400)
        
        # 정보 박스
        renderer.draw_info_box("Zone 게이지", SCREEN_WIDTH - 220, 200, 200, 50)
        
        # 프로그레스 바
        test_progress += 0.01
        if test_progress > 1.0:
            test_progress = 0.0
        renderer.draw_progress_bar(SCREEN_WIDTH - 220, 260, 200, 20, test_progress)
        
        # 안내 메시지
        renderer.draw_text("ESC: 종료", 10, SCREEN_HEIGHT - 30, 
                         renderer.font_small, COLOR_TEXT)
        
        renderer.update_display()
        renderer.tick()
    
    renderer.quit()
    print("테스트 종료")
