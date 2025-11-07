"""
카드 이미지 로딩 및 표시 시스템
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    CARD_ASSETS_PATH, CARD_WIDTH, CARD_HEIGHT, COLOR_WHITE, COLOR_BLACK,
    CARD_TYPE_GWANG, CARD_TYPE_TTI, CARD_TYPE_YEOLKKUT, CARD_TYPE_CODES
)
from core.card import Card


class CardDisplay:
    """카드 이미지 로딩 및 표시 클래스"""
    
    def __init__(self):
        """카드 표시 시스템을 초기화합니다."""
        self.card_images = {}  # {(month, card_type): surface}
        self.card_back_image = None
        
        self.card_width = CARD_WIDTH
        self.card_height = CARD_HEIGHT
        
        self._load_card_images()
    
    def _load_card_images(self):
        """카드 이미지를 로드합니다."""
        # 카드 뒷면 이미지 로드 (또는 생성)
        back_path = os.path.join(CARD_ASSETS_PATH, "back.png")
        
        if os.path.exists(back_path):
            try:
                self.card_back_image = pygame.image.load(back_path)
                self.card_back_image = pygame.transform.scale(
                    self.card_back_image, 
                    (self.card_width, self.card_height)
                )
            except:
                self.card_back_image = self._create_card_back()
        else:
            self.card_back_image = self._create_card_back()
        
        # 화투 카드 이미지 로드
        # 파일명 패턴: {month}{code}.png (예: 1g.png, 2t.png, 3k.png)
        # gwang -> g, tti -> t, yeolkkut -> k
        card_types = [CARD_TYPE_GWANG, CARD_TYPE_TTI, CARD_TYPE_YEOLKKUT]
        
        for month in range(1, 11):
            for card_type in card_types:
                # 카드 타입 코드 가져오기 (gwang->g, tti->t, yeolkkut->k)
                type_code = CARD_TYPE_CODES.get(card_type, "")
                
                card_path = os.path.join(
                    CARD_ASSETS_PATH, 
                    f"{month}{type_code}.png"
                )
                
                if os.path.exists(card_path):
                    try:
                        image = pygame.image.load(card_path)
                        image = pygame.transform.scale(
                            image, 
                            (self.card_width, self.card_height)
                        )
                        self.card_images[(month, card_type)] = image
                        # print(f"카드 이미지 로드 성공: {month}{type_code}.png")
                    except Exception as e:
                        print(f"카드 이미지 로드 실패: {card_path} - {e}")
                        # 폴백: 텍스트 카드 생성
                        self.card_images[(month, card_type)] = self._create_text_card(
                            month, card_type
                        )
                # 이미지 파일이 없어도 에러 없이 진행 (해당 월에 그 타입이 없을 수 있음)
    
    def _create_card_back(self) -> pygame.Surface:
        """
        카드 뒷면 이미지를 생성합니다.
        
        Returns:
            카드 뒷면 surface
        """
        surface = pygame.Surface((self.card_width, self.card_height))
        
        # 배경 (파란색 패턴)
        surface.fill((20, 50, 120))
        
        # 테두리
        pygame.draw.rect(surface, COLOR_WHITE, surface.get_rect(), 3, border_radius=8)
        
        # 패턴 (대각선)
        for i in range(0, self.card_width + self.card_height, 20):
            pygame.draw.line(surface, (40, 70, 150), 
                           (i, 0), (i - self.card_height, self.card_height), 3)
        
        return surface
    
    def _create_text_card(self, month: int, card_type: str) -> pygame.Surface:
        """
        텍스트 기반 카드 이미지를 생성합니다.
        
        Args:
            month: 월
            card_type: 카드 타입 (gwang, tti, yeolkkut)
            
        Returns:
            카드 surface
        """
        surface = pygame.Surface((self.card_width, self.card_height))
        
        # 배경 (흰색)
        surface.fill(COLOR_WHITE)
        
        # 테두리 (검정색)
        pygame.draw.rect(surface, COLOR_BLACK, surface.get_rect(), 3, border_radius=8)
        
        # 월 표시
        font_large = pygame.font.SysFont('malgungothic', 48, bold=True)
        month_text = font_large.render(f"{month}월", True, COLOR_BLACK)
        month_rect = month_text.get_rect(center=(self.card_width // 2, self.card_height // 3))
        surface.blit(month_text, month_rect)
        
        # 타입 표시 (한글 변환)
        type_names = {
            CARD_TYPE_GWANG: "광",
            CARD_TYPE_TTI: "띠",
            CARD_TYPE_YEOLKKUT: "끗"
        }
        type_display = type_names.get(card_type, card_type)
        
        font_small = pygame.font.SysFont('malgungothic', 24)
        type_text = font_small.render(type_display, True, COLOR_BLACK)
        type_rect = type_text.get_rect(center=(self.card_width // 2, self.card_height * 2 // 3))
        surface.blit(type_text, type_rect)
        
        return surface
    
    def get_card_image(self, card: Card, revealed: bool = None) -> pygame.Surface:
        """
        카드 이미지를 가져옵니다.
        
        Args:
            card: 카드 객체
            revealed: 공개 여부 (None이면 카드의 상태 사용)
            
        Returns:
            카드 이미지 surface
        """
        if revealed is None:
            revealed = card.is_revealed
        
        if revealed:
            key = (card.month, card.card_type)
            return self.card_images.get(key, self._create_text_card(card.month, card.card_type))
        else:
            return self.card_back_image
    
    def load_card_image(self, filename: str) -> pygame.Surface:
        """
        파일명으로 카드 이미지를 직접 로드합니다.
        
        Args:
            filename: 카드 이미지 파일명 (예: "1g.png", "2t.png")
            
        Returns:
            카드 이미지 surface (로드 실패 시 None)
        """
        card_path = os.path.join(CARD_ASSETS_PATH, filename)
        
        if os.path.exists(card_path):
            try:
                image = pygame.image.load(card_path)
                # 원본 크기로 반환 (스케일링은 호출자가 처리)
                return image
            except Exception as e:
                print(f"카드 이미지 로드 실패: {card_path} - {e}")
                return None
        else:
            print(f"카드 이미지 파일이 없습니다: {card_path}")
            return None
    
    def draw_card(self, screen, card: Card, x: int, y: int, 
                  revealed: bool = None, scale: float = 1.0):
        """
        카드를 화면에 그립니다.
        
        Args:
            screen: pygame 화면
            card: 카드 객체
            x, y: 위치
            revealed: 공개 여부
            scale: 크기 배율
        """
        image = self.get_card_image(card, revealed)
        
        # 크기 조정
        if scale != 1.0:
            new_width = int(self.card_width * scale)
            new_height = int(self.card_height * scale)
            image = pygame.transform.scale(image, (new_width, new_height))
        
        screen.blit(image, (x, y))
    
    def draw_cards(self, screen, cards: list, x: int, y: int, 
                   spacing: int = 10, revealed: list = None, scale: float = 1.0):
        """
        여러 카드를 가로로 나란히 그립니다.
        
        Args:
            screen: pygame 화면
            cards: 카드 리스트
            x, y: 시작 위치
            spacing: 카드 간 간격
            revealed: 각 카드의 공개 여부 리스트
            scale: 크기 배율
        """
        current_x = x
        card_width = int(self.card_width * scale)
        
        for i, card in enumerate(cards):
            is_revealed = revealed[i] if revealed else None
            self.draw_card(screen, card, current_x, y, is_revealed, scale)
            current_x += card_width + spacing
    
    def draw_hand(self, screen, cards: list, x: int, y: int, 
                  center: bool = False, scale: float = 1.0):
        """
        플레이어의 패를 그립니다 (중앙 정렬 옵션).
        
        Args:
            screen: pygame 화면
            cards: 카드 리스트
            x, y: 위치
            center: 중앙 정렬 여부
            scale: 크기 배율
        """
        spacing = 10
        card_width = int(self.card_width * scale)
        total_width = len(cards) * card_width + (len(cards) - 1) * spacing
        
        if center:
            start_x = x - total_width // 2
        else:
            start_x = x
        
        self.draw_cards(screen, cards, start_x, y, spacing, scale=scale)
    
    def draw_clickable_cards(self, screen, cards: list, x: int, y: int,
                           selected_indices: set = None, spacing: int = 10,
                           scale: float = 1.0, force_reveal: bool = True) -> list:
        """
        클릭 가능한 카드들을 그리고 Rect 리스트를 반환합니다.
        
        Args:
            screen: pygame 화면
            cards: 카드 리스트
            x, y: 시작 위치
            selected_indices: 선택된 카드 인덱스 집합
            spacing: 카드 간 간격
            scale: 크기 배율
            force_reveal: 강제로 모든 카드 공개 (기본값: True, 플레이어 카드용)
            
        Returns:
            각 카드의 Rect 리스트
        """
        if selected_indices is None:
            selected_indices = set()
        
        rects = []
        current_x = x
        card_width = int(self.card_width * scale)
        card_height = int(self.card_height * scale)
        
        for i, card in enumerate(cards):
            # 선택된 카드는 위로 올림
            offset_y = -20 if i in selected_indices else 0
            
            # 카드 그리기 (force_reveal이 True면 항상 공개)
            self.draw_card(screen, card, current_x, y + offset_y, 
                          revealed=force_reveal, scale=scale)
            
            # Rect 저장
            rect = pygame.Rect(current_x, y + offset_y, card_width, card_height)
            rects.append(rect)
            
            # 선택 표시
            if i in selected_indices:
                pygame.draw.rect(screen, (255, 255, 0), rect, 3, border_radius=8)
            
            current_x += card_width + spacing
        
        return rects


# 테스트
if __name__ == "__main__":
    print("=== CardDisplay 테스트 ===\n")
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("카드 표시 테스트")
    clock = pygame.time.Clock()
    
    # 카드 표시 시스템 초기화
    card_display = CardDisplay()
    
    # 테스트 카드 생성
    from core.card import Deck
    deck = Deck()
    deck.shuffle()
    
    test_cards = [deck.draw() for _ in range(5)]
    test_cards[0].reveal()
    test_cards[2].reveal()
    
    selected = {1, 3}
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 화면 그리기
        screen.fill((30, 80, 50))
        
        # 제목
        font = pygame.font.SysFont('malgungothic', 36, bold=True)
        title = font.render("카드 표시 테스트", True, COLOR_WHITE)
        screen.blit(title, (500, 30))
        
        # 카드 뒷면
        small_font = pygame.font.SysFont('malgungothic', 20)
        label1 = small_font.render("카드 뒷면:", True, COLOR_WHITE)
        screen.blit(label1, (100, 100))
        screen.blit(card_display.card_back_image, (100, 130))
        
        # 단일 카드 (공개)
        label2 = small_font.render("공개된 카드:", True, COLOR_WHITE)
        screen.blit(label2, (300, 100))
        card_display.draw_card(screen, test_cards[0], 300, 130, revealed=True)
        
        # 여러 카드 (일부 공개)
        label3 = small_font.render("여러 카드 (일부 공개):", True, COLOR_WHITE)
        screen.blit(label3, (100, 300))
        card_display.draw_cards(screen, test_cards, 100, 330)
        
        # 클릭 가능한 카드 (선택된 카드 있음)
        label4 = small_font.render("클릭 가능한 카드 (노란색=선택됨):", True, COLOR_WHITE)
        screen.blit(label4, (100, 500))
        card_display.draw_clickable_cards(screen, test_cards, 100, 530, selected)
        
        # 안내
        info = small_font.render("ESC: 종료", True, (200, 200, 200))
        screen.blit(info, (10, 690))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("테스트 종료")
