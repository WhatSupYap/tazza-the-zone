"""
콘솔 기반 섯다 게임 실행기
(pygame UI 구현 전 테스트용)
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DEFAULT_MIN_BET
from core.game import SutdaGame, GameState, BetAction
from ai.npc import NPCPlayer


def print_game_status(game: SutdaGame):
    """현재 게임 상태를 출력합니다."""
    print(f"\n현재 상황:")
    print(f"  판돈: {game.pot:,}원")
    print(f"  {game.player.name} 베팅: {game.player.current_bet:,}원 (잔액: {game.player.money:,}원)")
    print(f"  {game.npc.name} 베팅: {game.npc.current_bet:,}원 (잔액: {game.npc.money:,}원)")


def show_player_cards(game: SutdaGame):
    """플레이어 카드를 출력합니다."""
    print(f"\n{game.player.name}의 카드:")
    for i, card in enumerate(game.player.cards):
        status = "공개" if card.is_revealed else "비공개"
        print(f"  [{i+1}] {card} ({status})")


def show_npc_cards(game: SutdaGame):
    """NPC 카드를 출력합니다 (공개된 것만)."""
    print(f"\n{game.npc.name}의 카드:")
    for i, card in enumerate(game.npc.cards):
        if card.is_revealed:
            print(f"  [{i+1}] {card} (공개)")
        else:
            print(f"  [{i+1}] ???  (비공개)")


def get_player_bet_action(game: SutdaGame) -> tuple:
    """플레이어의 베팅 행동을 입력받습니다."""
    print(f"\n===== 베팅 선택 =====")
    print(f"1. 다이 (포기)")
    print(f"2. 체크 (패스)")
    print(f"3. 삥 ({game.min_bet:,}원)")
    print(f"4. 하프 ({game.pot // 2:,}원)")
    print(f"5. 콜 (상대 베팅에 맞춤)")
    print(f"6. 올인 (전 재산 베팅)")
    
    while True:
        try:
            choice = input("\n선택하세요 (1-6): ").strip()
            
            if choice == "1":
                return BetAction.DIE, 0
            elif choice == "2":
                return BetAction.CHECK, 0
            elif choice == "3":
                return BetAction.PPING, game.min_bet
            elif choice == "4":
                return BetAction.HALF, game.pot // 2
            elif choice == "5":
                # 상대방 베팅에 맞추기
                call_amount = game.npc.current_bet - game.player.current_bet
                if call_amount <= 0:
                    print("콜할 금액이 없습니다. 다시 선택하세요.")
                    continue
                return BetAction.CALL, call_amount
            elif choice == "6":
                return BetAction.ALLIN, game.player.money
            else:
                print("잘못된 입력입니다. 1-6 사이의 숫자를 입력하세요.")
        except Exception as e:
            print(f"오류: {e}")


def run_betting_round(game: SutdaGame):
    """한 번의 베팅 라운드를 진행합니다."""
    # 선 플레이어부터 시작
    first_to_act = game.first_player
    second_to_act = game.player if first_to_act == game.npc else game.npc
    
    # 첫 번째 플레이어 베팅
    if first_to_act == game.player:
        # 사람 차례
        show_player_cards(game)
        show_npc_cards(game)
        print_game_status(game)
        
        action, amount = get_player_bet_action(game)
        game.process_bet(game.player, action, amount)
    else:
        # NPC 차례
        action, amount = game.npc.decide_bet_action(
            game.player.cards,
            game.pot,
            game.player.current_bet,
            game.npc.current_bet,
            game.min_bet
        )
        game.process_bet(game.npc, action, amount)
    
    # 베팅 종료 체크
    if game.is_betting_done():
        return
    
    # 두 번째 플레이어 베팅
    if second_to_act == game.player:
        # 사람 차례
        show_player_cards(game)
        show_npc_cards(game)
        print_game_status(game)
        
        action, amount = get_player_bet_action(game)
        game.process_bet(game.player, action, amount)
    else:
        # NPC 차례
        action, amount = game.npc.decide_bet_action(
            game.player.cards,
            game.pot,
            game.player.current_bet,
            game.npc.current_bet,
            game.min_bet
        )
        game.process_bet(game.npc, action, amount)


def run_game():
    """게임을 실행합니다."""
    print("="*60)
    print("섯다 게임 (콘솔 버전)")
    print("="*60)
    
    # 플레이어 이름 입력
    player_name = input("\n플레이어 이름을 입력하세요: ").strip()
    if not player_name:
        player_name = "플레이어"
    
    # NPC 선택 (추후 확장 가능)
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
    
    # 게임 생성
    game = SutdaGame(player_name, npc)
    game.start_new_game()
    
    # 메인 게임 루프
    while game.state != GameState.GAME_OVER:
        
        # 1차 베팅 (2장 카드 상태)
        game.start_first_betting()
        
        # Zone 활성화된 경우
        if game.state == GameState.ZONE_ACTIVE:
            print(f"\n⚡ Zone이 활성화되었습니다! ⚡")
            print(f"지난 게임 기록을 확인할 수 있습니다.")
            print(f"(콘솔 버전에서는 자동으로 비활성화됩니다)")
            game.zone.deactivate()
            game.state = GameState.BETTING
        
        # 베팅 진행
        while not game.is_betting_done():
            run_betting_round(game)
        
        # 한쪽이 다이했으면 쇼다운으로 바로 이동
        if game.player.has_folded or game.npc.has_folded:
            game.showdown()
            game.end_round()
            continue
        
        # 3번째 카드 배분
        game.deal_third_card()
        
        # 2차 베팅
        game.start_second_betting()
        
        # Zone 활성화된 경우
        if game.state == GameState.ZONE_ACTIVE:
            print(f"\n⚡ Zone이 활성화되었습니다! ⚡")
            print(f"(콘솔 버전에서는 자동으로 비활성화됩니다)")
            game.zone.deactivate()
            game.state = GameState.BETTING
        
        # 베팅 진행
        game.check_count = 0  # 2차 베팅 초기화
        while not game.is_betting_done():
            run_betting_round(game)
        
        # 쇼다운
        game.showdown()
        
        # 라운드 종료
        game.end_round()
    
    # 최종 결과
    game.show_final_result()
    
    print("\n게임을 종료합니다. 감사합니다!")


if __name__ == "__main__":
    try:
        run_game()
    except KeyboardInterrupt:
        print("\n\n게임을 중단합니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
