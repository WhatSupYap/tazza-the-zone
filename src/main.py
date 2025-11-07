"""
타짜 - The Zone
Pygame 메인 진입점
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.game_screen import GameScreen


def main():
    """메인 함수"""
    
    # UI 실행
    try:
        screen = GameScreen()
        screen.run()

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n게임을 종료합니다. 감사합니다!")


if __name__ == "__main__":
    main()
