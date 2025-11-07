"""
섯다 족보 판정 시스템
카드 조합을 평가하고 비교합니다.
"""

from typing import List, Tuple, Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CARD_TYPE_GWANG, CARD_TYPE_TTI, CARD_TYPE_YEOLKKUT, CARD_NAMES
from core.card import Card


# 족보 랭킹 (낮을수록 강함)
RANK_SANGPALGWANGTTAENG = 1  # 삼팔광땡
RANK_GWANGTTAENG = 2  # 광땡
RANK_TTAENG = 3  # 땡
RANK_ALLI = 4  # 알리
RANK_DOKSA = 5  # 독사
RANK_GUPPING = 6  # 구삥
RANK_JANGPPING = 7  # 장삥
RANK_JANGSA = 8  # 장사
RANK_SERYUK = 9  # 세륙
RANK_KKUT = 10  # 끗 (9~1끗)
RANK_MANGTONG = 11  # 망통 (0끗)

# 특수 족보
SPECIAL_TTAENGJABI = "ttaengjabi"  # 땡잡이 (3+7)
SPECIAL_GUSA = "gusa"  # 구사 (4+9)
SPECIAL_MEONGTEONGGURI_GUSA = "meongteongguri_gusa"  # 멍텅구리 구사 (4열끗+9열끗)
SPECIAL_AMHAENGEOSA = "amhaengeosa"  # 암행어사 (4열끗+7열끗)


class HandEvaluator:
    """섯다 족보 평가 클래스"""
    
    @staticmethod
    def evaluate(cards: List[Card]) -> Dict:
        """
        카드 조합을 평가합니다.
        
        Args:
            cards: 평가할 카드 리스트 (2장 또는 3장)
            
        Returns:
            {
                'rank': int,  # 족보 랭킹
                'name': str,  # 족보 이름
                'score': int,  # 세부 점수 (같은 랭킹 내 비교용)
                'description': str,  # 족보 설명
                'special': Optional[str]  # 특수 족보 타입
            }
        """
        if len(cards) < 2:
            raise ValueError("최소 2장의 카드가 필요합니다")
        
        # 3장일 경우 처음 2장만 사용
        eval_cards = cards[:2]
        
        month1, month2 = eval_cards[0].month, eval_cards[1].month
        type1, type2 = eval_cards[0].card_type, eval_cards[1].card_type
        
        # 특수 족보 체크
        special = HandEvaluator._check_special_hand(month1, month2, type1, type2)
        
        # 1. 삼팔광땡 체크
        if HandEvaluator._is_sangpalgwangttaeng(month1, month2, type1, type2):
            return {
                'rank': RANK_SANGPALGWANGTTAENG,
                'name': '삼팔광땡',
                'score': 0,
                'description': '3광 + 8광 (최강의 족보)',
                'special': None
            }
        
        # 2. 광땡 체크
        if type1 == CARD_TYPE_GWANG and type2 == CARD_TYPE_GWANG:
            score = max(month1, month2)  # 높은 월
            return {
                'rank': RANK_GWANGTTAENG,
                'name': f'{score}광땡',
                'score': score,
                'description': f'{month1}광 + {month2}광',
                'special': None
            }
        
        # 3. 땡 체크
        if month1 == month2:
            return {
                'rank': RANK_TTAENG,
                'name': f'{month1}땡',
                'score': month1,
                'description': f'{month1}월 2장',
                'special': None
            }
        
        # 4. 특수 조합 체크 (알리, 독사, 구삥, 장삥, 장사, 세륙)
        months = sorted([month1, month2])
        
        if months == [1, 2]:
            return {
                'rank': RANK_ALLI,
                'name': '알리',
                'score': 0,
                'description': '1월 + 2월',
                'special': None
            }
        
        if months == [1, 4]:
            return {
                'rank': RANK_DOKSA,
                'name': '독사',
                'score': 0,
                'description': '1월 + 4월',
                'special': None
            }
        
        if months == [1, 9]:
            return {
                'rank': RANK_GUPPING,
                'name': '구삥',
                'score': 0,
                'description': '1월 + 9월',
                'special': None
            }
        
        if months == [1, 10]:
            return {
                'rank': RANK_JANGPPING,
                'name': '장삥',
                'score': 0,
                'description': '1월 + 10월',
                'special': None
            }
        
        if months == [4, 10]:
            return {
                'rank': RANK_JANGSA,
                'name': '장사',
                'score': 0,
                'description': '4월 + 10월',
                'special': None
            }
        
        if months == [4, 6]:
            return {
                'rank': RANK_SERYUK,
                'name': '세륙',
                'score': 0,
                'description': '4월 + 6월',
                'special': None
            }
        
        # 5. 끗수 계산
        kkut = (month1 + month2) % 10
        
        # 특수 족보 이름 매핑
        special_names = {
            SPECIAL_TTAENGJABI: '땡잡이',
            SPECIAL_GUSA: '구사',
            SPECIAL_MEONGTEONGGURI_GUSA: '멍텅구리 구사',
            SPECIAL_AMHAENGEOSA: '암행어사'
        }
        
        if kkut == 0:
            # 특수 족보가 있으면 특수 이름 표시
            if special:
                name = special_names.get(special, '망통')
                desc = f'{month1} + {month2} = {month1 + month2} (0끗, {name})'
            else:
                name = '망통'
                desc = f'{month1} + {month2} = {month1 + month2} (0끗)'
            
            return {
                'rank': RANK_MANGTONG,
                'name': name,
                'score': 0,
                'description': desc,
                'special': special
            }
        
        # 특수 족보가 있으면 특수 이름 표시
        if special:
            name = special_names.get(special, f'{kkut}끗')
            desc = f'{month1} + {month2} = {month1 + month2} ({kkut}끗, {name})'
        else:
            name = f'{kkut}끗'
            desc = f'{month1} + {month2} = {month1 + month2} ({kkut}끗)'
        
        return {
            'rank': RANK_KKUT,
            'name': name,
            'score': kkut,
            'description': desc,
            'special': special
        }
    
    @staticmethod
    def _is_sangpalgwangttaeng(month1: int, month2: int, type1: str, type2: str) -> bool:
        """삼팔광땡 여부 확인"""
        if type1 != CARD_TYPE_GWANG or type2 != CARD_TYPE_GWANG:
            return False
        months = sorted([month1, month2])
        return months == [3, 8]
    
    @staticmethod
    def _check_special_hand(month1: int, month2: int, type1: str, type2: str) -> Optional[str]:
        """특수 족보 확인"""
        months = sorted([month1, month2])
        
        # 땡잡이 (3월 + 7월)
        if months == [3, 7]:
            return SPECIAL_TTAENGJABI
        
        # 멍텅구리 구사 (4열끗 + 9열끗)
        if months == [4, 9] and type1 == CARD_TYPE_YEOLKKUT and type2 == CARD_TYPE_YEOLKKUT:
            return SPECIAL_MEONGTEONGGURI_GUSA
        
        # 구사 (4월 + 9월, 멍텅구리 구사 제외)
        if months == [4, 9]:
            return SPECIAL_GUSA
        
        # 암행어사 (4열끗 + 7열끗)
        if months == [4, 7] and type1 == CARD_TYPE_YEOLKKUT and type2 == CARD_TYPE_YEOLKKUT:
            return SPECIAL_AMHAENGEOSA
        
        return None
    
    @staticmethod
    def compare(hand1: Dict, hand2: Dict) -> int:
        """
        두 족보를 비교합니다.
        
        Args:
            hand1: 첫 번째 족보
            hand2: 두 번째 족보
            
        Returns:
            1: hand1 승리
            -1: hand2 승리
            0: 무승부
        """
        # 특수 족보 처리
        result = HandEvaluator._handle_special_hands(hand1, hand2)
        if result is not None:
            return result
        
        # 랭크 비교 (낮을수록 강함)
        if hand1['rank'] < hand2['rank']:
            return 1
        elif hand1['rank'] > hand2['rank']:
            return -1
        
        # 같은 랭크일 경우 점수 비교
        if hand1['score'] > hand2['score']:
            return 1
        elif hand1['score'] < hand2['score']:
            return -1
        
        # 무승부
        return 0
    
    @staticmethod
    def _handle_special_hands(hand1: Dict, hand2: Dict) -> Optional[int]:
        """특수 족보 효과 처리"""
        special1 = hand1.get('special')
        special2 = hand2.get('special')
        
        # 땡잡이: 광땡 제외한 모든 땡(1땡~9땡) 승리
        if special1 == SPECIAL_TTAENGJABI:
            if hand2['rank'] == RANK_TTAENG:  # 상대가 땡
                return 1
        if special2 == SPECIAL_TTAENGJABI:
            if hand1['rank'] == RANK_TTAENG:  # 상대가 땡
                return -1
        
        # 멍텅구리 구사: 9땡까지 잡을 수 있음
        if special1 == SPECIAL_MEONGTEONGGURI_GUSA:
            if hand2['rank'] == RANK_TTAENG and hand2['score'] <= 9:
                return 1
        if special2 == SPECIAL_MEONGTEONGGURI_GUSA:
            if hand1['rank'] == RANK_TTAENG and hand1['score'] <= 9:
                return -1
        
        # 암행어사: 1광땡, 3광땡 승리 (삼팔광땡 제외)
        if special1 == SPECIAL_AMHAENGEOSA:
            if hand2['rank'] == RANK_GWANGTTAENG and hand2['score'] in [1, 3]:
                return 1
        if special2 == SPECIAL_AMHAENGEOSA:
            if hand1['rank'] == RANK_GWANGTTAENG and hand1['score'] in [1, 3]:
                return -1
        
        # 구사: 땡보다는 약하지만 일반 끗수보다는 강함
        # 구사 vs 끗수 -> 구사 승리
        if special1 in [SPECIAL_GUSA, SPECIAL_MEONGTEONGGURI_GUSA]:
            if hand2['rank'] == RANK_KKUT or hand2['rank'] == RANK_MANGTONG:
                return 1
        if special2 in [SPECIAL_GUSA, SPECIAL_MEONGTEONGGURI_GUSA]:
            if hand1['rank'] == RANK_KKUT or hand1['rank'] == RANK_MANGTONG:
                return -1
        
        return None
    
    @staticmethod
    def is_special_hand(hand: Dict) -> bool:
        """특수 족보 여부 확인 (Zone 확률 증가용)"""
        # 삼팔광땡, 광땡, 특수 조합(알리~세륙)
        if hand['rank'] in [RANK_SANGPALGWANGTTAENG, RANK_GWANGTTAENG,
                           RANK_ALLI, RANK_DOKSA, RANK_GUPPING,
                           RANK_JANGPPING, RANK_JANGSA, RANK_SERYUK]:
            return True
        
        # 특수 족보
        if hand.get('special') is not None:
            return True
        
        return False
    
    @staticmethod
    def needs_rematch(hand1: Dict, hand2: Dict) -> bool:
        """구사로 인한 재경기 필요 여부"""
        special1 = hand1.get('special')
        special2 = hand2.get('special')
        
        # 구사 또는 멍텅구리 구사일 경우
        if special1 in [SPECIAL_GUSA, SPECIAL_MEONGTEONGGURI_GUSA]:
            # 상대가 땡 이하의 족보일 때
            if hand2['rank'] >= RANK_TTAENG:
                return True
        
        if special2 in [SPECIAL_GUSA, SPECIAL_MEONGTEONGGURI_GUSA]:
            if hand1['rank'] >= RANK_TTAENG:
                return True
        
        return False


    @staticmethod
    def _get_card_name(card: Card) -> str:
        """
        카드 이름을 문자열로 반환합니다.
        
        Args:
            card: 카드 객체
            
        Returns:
            카드 이름 (예: "솔 광", "매조 띠", "벚꽃 열끗")
        """
        type_name = {
            CARD_TYPE_GWANG: "광",
            CARD_TYPE_TTI: "띠",
            CARD_TYPE_YEOLKKUT: "열끗"
        }
        card_name = CARD_NAMES.get(card.month, f"{card.month}월")
        return f"{card_name} {type_name[card.card_type]}"


    @staticmethod
    def estimate_hand_for_npc(npc_cards: List[Card], player_revealed_cards: List[Card]) -> Dict:
        """
        NPC 관점에서 자신과 상대방의 예상 족보를 계산합니다.
        
        Args:
            npc_cards: NPC가 가진 카드 리스트
            player_revealed_cards: 플레이어가 공개한 카드 리스트
            
        Returns:
            {
                'my_hand': Dict,  # NPC의 최고 족보
                'my_cards': List[str],  # NPC 카드 이름 리스트
                'my_revealed': List[str],  # NPC 공개 카드 이름 리스트
                'opponent_revealed': List[str],  # 상대 공개 카드 이름 리스트
                'opponent_estimated': str  # 상대 예상 족보 설명
            }
        """
        # NPC의 최고 족보 계산
        my_best_hand = HandEvaluator.evaluate(npc_cards)
        
        # NPC의 카드 정보 (카드 이름 생성)
        my_cards = [HandEvaluator._get_card_name(card) for card in npc_cards]
        my_revealed = [HandEvaluator._get_card_name(card) for card in npc_cards if card.is_revealed]
        
        # 플레이어 공개 카드 정보
        opponent_revealed = [HandEvaluator._get_card_name(card) for card in player_revealed_cards]
        
        # 플레이어 예상 족보 계산
        if len(player_revealed_cards) == 0:
            opponent_estimated = "알 수 없음 (공개 카드 없음)"
        elif len(player_revealed_cards) == 1:
            # 1장만 공개된 경우: 가능한 최고/최저 족보 범위
            revealed_month = player_revealed_cards[0].month
            revealed_type = player_revealed_cards[0].card_type
            
            # 광이면 광땡 가능성
            if revealed_type == CARD_TYPE_GWANG:
                opponent_estimated = f"광땡 ~ 끗 가능 (공개: {HandEvaluator._get_card_name(player_revealed_cards[0])})"
            # 같은 월이면 땡 가능성
            else:
                opponent_estimated = f"땡 ~ 끗 가능 (공개: {HandEvaluator._get_card_name(player_revealed_cards[0])})"
        else:
            # 2장 이상 공개된 경우: 정확한 족보 계산
            opponent_hand = HandEvaluator.evaluate(player_revealed_cards)
            opponent_estimated = f"{opponent_hand['name']} (순위 {opponent_hand['rank']})"
        
        return {
            'my_hand': my_best_hand,
            'my_cards': my_cards,
            'my_revealed': my_revealed,
            'opponent_revealed': opponent_revealed,
            'opponent_estimated': opponent_estimated
        }


# 테스트 코드
if __name__ == "__main__":
    from core.card import Card, CARD_TYPE_GWANG, CARD_TYPE_TTI, CARD_TYPE_YEOLKKUT
    
    print("=== 족보 판정 시스템 테스트 ===\n")
    
    # 테스트 케이스들
    test_cases = [
        ([Card(3, CARD_TYPE_GWANG), Card(8, CARD_TYPE_GWANG)], "삼팔광땡"),
        ([Card(1, CARD_TYPE_GWANG), Card(8, CARD_TYPE_GWANG)], "광땡"),
        ([Card(10, CARD_TYPE_YEOLKKUT), Card(10, CARD_TYPE_TTI)], "10땡"),
        ([Card(1, CARD_TYPE_GWANG), Card(2, CARD_TYPE_TTI)], "알리"),
        ([Card(4, CARD_TYPE_YEOLKKUT), Card(6, CARD_TYPE_TTI)], "세륙"),
        ([Card(5, CARD_TYPE_YEOLKKUT), Card(4, CARD_TYPE_TTI)], "9끗"),
        ([Card(5, CARD_TYPE_YEOLKKUT), Card(5, CARD_TYPE_TTI)], "망통"),
        ([Card(3, CARD_TYPE_GWANG), Card(7, CARD_TYPE_TTI)], "땡잡이"),
    ]
    
    for i, (cards, expected) in enumerate(test_cases, 1):
        hand = HandEvaluator.evaluate(cards)
        print(f"{i}. {cards[0].month}월 {cards[1].month}월")
        print(f"   결과: {hand['name']}")
        print(f"   설명: {hand['description']}")
        if hand.get('special'):
            print(f"   특수: {hand['special']}")
        print()
