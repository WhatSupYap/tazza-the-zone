"""
버튼 UI 컴포넌트
클릭 가능한 버튼 위젯
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLOR_WHITE, COLOR_BLACK, COLOR_HIGHLIGHT, COLOR_DANGER, COLOR_SUCCESS


class Button:
    """버튼 클래스"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, font=None,
                 bg_color=(70, 70, 70), hover_color=(100, 100, 100),
                 text_color=COLOR_WHITE, border_color=COLOR_WHITE,
                 callback=None, enabled=True):
        """
        버튼을 생성합니다.
        
        Args:
            x, y: 위치
            width, height: 크기
            text: 버튼 텍스트
            font: 폰트
            bg_color: 배경 색상
            hover_color: 마우스 오버 시 색상
            text_color: 텍스트 색상
            border_color: 테두리 색상
            callback: 클릭 시 호출될 함수
            enabled: 활성화 여부
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font if font else pygame.font.SysFont('malgungothic', 20)
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.disabled_color = (50, 50, 50)
        self.text_color = text_color
        self.disabled_text_color = (100, 100, 100)
        self.border_color = border_color
        
        self.callback = callback
        self.enabled = enabled
        self.hovered = False
    
    def update(self, mouse_pos: tuple):
        """
        버튼 상태를 업데이트합니다.
        
        Args:
            mouse_pos: 마우스 위치 (x, y)
        """
        if self.enabled:
            self.hovered = self.rect.collidepoint(mouse_pos)
        else:
            self.hovered = False
    
    def handle_event(self, event) -> bool:
        """
        이벤트를 처리합니다.
        
        Args:
            event: pygame 이벤트
            
        Returns:
            클릭되었으면 True
        """
        if not self.enabled:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # hovered 상태 또는 직접 collidepoint 체크
            if self.hovered or self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        elif event.type == pygame.MOUSEMOTION:
            # 마우스 이동 시 hovered 상태 업데이트
            self.hovered = self.rect.collidepoint(event.pos)
        
        return False
    
    def draw(self, screen):
        """
        버튼을 그립니다.
        
        Args:
            screen: pygame 화면
        """
        # 배경 색상 결정
        if not self.enabled:
            bg_color = self.disabled_color
            text_color = self.disabled_text_color
        elif self.hovered:
            bg_color = self.hover_color
            text_color = self.text_color
        else:
            bg_color = self.bg_color
            text_color = self.text_color
        
        # 배경 그리기
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        
        # 테두리 그리기
        border_color = self.border_color if self.enabled else (80, 80, 80)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)
        
        # 텍스트 그리기
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def set_enabled(self, enabled: bool):
        """버튼 활성화 상태를 설정합니다."""
        self.enabled = enabled
    
    def set_text(self, text: str):
        """버튼 텍스트를 변경합니다."""
        self.text = text


class ButtonGroup:
    """버튼 그룹 관리 클래스"""
    
    def __init__(self):
        """버튼 그룹을 생성합니다."""
        self.buttons = []
    
    def add_button(self, button: Button):
        """
        버튼을 추가합니다.
        
        Args:
            button: 추가할 버튼
        """
        self.buttons.append(button)
    
    def update(self, mouse_pos: tuple):
        """
        모든 버튼을 업데이트합니다.
        
        Args:
            mouse_pos: 마우스 위치
        """
        for button in self.buttons:
            button.update(mouse_pos)
    
    def handle_event(self, event) -> Button:
        """
        이벤트를 처리합니다.
        
        Args:
            event: pygame 이벤트
            
        Returns:
            클릭된 버튼 (없으면 None)
        """
        for button in self.buttons:
            if button.handle_event(event):
                return button
        return None
    
    def draw(self, screen):
        """
        모든 버튼을 그립니다.
        
        Args:
            screen: pygame 화면
        """
        for button in self.buttons:
            button.draw(screen)
    
    def clear(self):
        """모든 버튼을 제거합니다."""
        self.buttons.clear()
    
    def set_all_enabled(self, enabled: bool):
        """모든 버튼의 활성화 상태를 설정합니다."""
        for button in self.buttons:
            button.set_enabled(enabled)


# 미리 정의된 버튼 스타일
class BetButton(Button):
    """베팅 버튼"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, font=None, callback=None):
        super().__init__(
            x, y, width, height, text, font,
            bg_color=(50, 100, 50),
            hover_color=(70, 130, 70),
            text_color=COLOR_WHITE,
            border_color=COLOR_SUCCESS,
            callback=callback
        )


class DangerButton(Button):
    """위험 버튼 (다이 등)"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, font=None, callback=None):
        super().__init__(
            x, y, width, height, text, font,
            bg_color=(100, 30, 30),
            hover_color=(130, 50, 50),
            text_color=COLOR_WHITE,
            border_color=COLOR_DANGER,
            callback=callback
        )


class HighlightButton(Button):
    """강조 버튼 (콜, 올인 등)"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, font=None, callback=None):
        super().__init__(
            x, y, width, height, text, font,
            bg_color=(100, 80, 30),
            hover_color=(130, 110, 50),
            text_color=COLOR_WHITE,
            border_color=COLOR_HIGHLIGHT,
            callback=callback
        )


# 테스트
if __name__ == "__main__":
    print("=== Button 테스트 ===\n")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("버튼 테스트")
    clock = pygame.time.Clock()
    
    # 버튼 그룹 생성
    button_group = ButtonGroup()
    
    # 테스트 버튼들
    def on_click_1():
        print("버튼 1 클릭!")
    
    def on_click_2():
        print("버튼 2 클릭!")
    
    def on_click_3():
        print("버튼 3 클릭!")
    
    button1 = Button(300, 200, 200, 50, "일반 버튼", callback=on_click_1)
    button2 = BetButton(300, 270, 200, 50, "베팅 버튼", callback=on_click_2)
    button3 = DangerButton(300, 340, 200, 50, "다이", callback=on_click_3)
    button4 = HighlightButton(300, 410, 200, 50, "올인!")
    button5 = Button(300, 480, 200, 50, "비활성화", enabled=False)
    
    button_group.add_button(button1)
    button_group.add_button(button2)
    button_group.add_button(button3)
    button_group.add_button(button4)
    button_group.add_button(button5)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # 버튼 이벤트 처리
            clicked_button = button_group.handle_event(event)
            if clicked_button:
                print(f"'{clicked_button.text}' 클릭됨")
        
        # 버튼 업데이트
        button_group.update(mouse_pos)
        
        # 화면 그리기
        screen.fill((40, 40, 40))
        
        # 제목
        font = pygame.font.SysFont('malgungothic', 36)
        title = font.render("버튼 테스트", True, COLOR_WHITE)
        screen.blit(title, (300, 100))
        
        # 버튼 그리기
        button_group.draw(screen)
        
        # 안내
        small_font = pygame.font.SysFont('malgungothic', 18)
        info = small_font.render("ESC: 종료", True, (200, 200, 200))
        screen.blit(info, (10, 570))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("테스트 종료")
