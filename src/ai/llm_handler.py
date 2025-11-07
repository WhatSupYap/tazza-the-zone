"""
LLM API 통신 핸들러
NPC 대사를 생성합니다. (추후 실제 LLM 연동 예정)
"""

import random
from typing import Dict, Optional
import sys
import os
import json
import ollama
import time
import core.game as SutdaGame
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_MODEL, LLM_API_URL, LLM_TIMEOUT, LLM_TEMPERATURE, MODEL_NAME

load_dotenv()

class LLMHandler:
    """LLM API 통신 핸들러"""
    
    def __init__(self):
        """LLM 핸들러 초기화"""
        self.model = LLM_MODEL
        self.api_url = LLM_API_URL
        self.timeout = LLM_TIMEOUT
        self.temperature = LLM_TEMPERATURE
        self.enabled = False  # 현재는 비활성화 (추후 활성화)
        self.model_name = MODEL_NAME

    
    def chat_with_eeve(self,messages):
    
        start_time = time.time()
        response = ollama.chat(
            model=self.model_name,
            messages=messages
        )
        end_time = time.time()
        return response['message'], end_time - start_time



    def chat_with_eeve_runpod(self, messages, model:str = "EEVE-Korean-10.8B"):

        POD_ID = os.getenv("POD_ID")
        
        RUNPOD_OLLAMA_URL = f"https://{POD_ID}-11434.proxy.runpod.net/"

        start_time = time.time()
        client = ollama.Client(host=RUNPOD_OLLAMA_URL)

        response = client.chat(
            model=model,
            messages=messages
        )

        end_time = time.time()
        return response['message'], end_time - start_time

    
    
    def generate_dialogue(self, game: SutdaGame) -> str:
       
        talk , inner= '...', '...'
        is_runpod_ok = True
        try:
            # 프롬프트 생성
            system_prompt, user_prompt = self._build_prompt(game)
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            
            if user_prompt:
                messages.append({'role': 'user', 'content': user_prompt})

            # 런팟에서 호출
            res, _ = self.chat_with_eeve_runpod(messages)
            
            content = res['content']

            response_json = json.loads(content)
            # print(json.dumps(response_json, ensure_ascii=False, indent=4))
            talk = response_json.get('하는말', '')
            inner = response_json.get('속마음', '')

            if talk == "..." or inner == "...":
                return "...","..."

            return talk, inner
            
        except Exception as e:
            is_runpod_ok = False

        try:
            # 프롬프트 생성
            system_prompt, user_prompt = self._build_prompt(game)
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            
            if user_prompt:
                messages.append({'role': 'user', 'content': user_prompt})

            # 올라마에서 모델 호출
            res, _ = self.chat_with_eeve(messages)
            # res, _ = self.chat_with_eeve_runpod(messages)
            
            content = res['content']

            response_json = json.loads(content)
            # print(json.dumps(response_json, ensure_ascii=False, indent=4))
            talk = response_json.get('하는말', '')
            inner = response_json.get('속마음', '')
            
            return talk, inner
            
        except Exception as e:
            is_runpod_ok = False

        return '...','...'
        

    
    def _build_prompt(self, game: SutdaGame) -> str:

        # 페르소나 및 입출력 데이터 정의
        # 이 셀은 프롬프트에 사용될 데이터 예시를 정의합니다.

        # 시연시 공유

        # 1. 페르소나 라이브러리 정의
        personas = {
            "아귀": {
                "이름": "아귀",
                "직업": "타짜 (사채업자)",
                "배경": "영화 '타짜'의 최종 보스. 잔인하고 무자비하며, 도박판을 지배하는 절대악.",
                "말투": "반말을 기본으로 하며, 위협적이고 공격적인 전라도 사투리를 사용한다. ('~부렀으', '~잉', '그랬냐?')",
                "성격": { "평정심": "강철 멘탈", "언변": "상대 압박에 능숙", "배짱": "매우 대담함" },
                "목표": "오직 돈을 따는 것. 이를 위해 모든 수단을 동원한다."
            },
            "평경장": {
                "이름": "평경장",
                "직업": "전설적인 타짜",
                "배경": "고니의 스승. '아수라발발타'라는 주문으로 유명하며, 도박판의 기술과 철학을 꿰뚫고 있다.",
                "말투": "차분하고 무게감 있는 말투. 핵심을 찌르는 조언을 던진다. ('~하니?', '~해라')",
                "성격": { "평정심": "매우 신중함", "언변": "철학적이고 비유적", "배짱": "상황을 지배함" },
                "목표": "기술보다 마음을 다스리는 것. 도박의 위험성을 경계한다."
            },
            "고니": {
                "이름": "고니",
                "직업": "타짜 (성장형)",
                "배경": "평경장의 제자. 스승의 죽음에 대한 복수와 최고의 타짜가 되기 위해 모든 것을 건다.",
                "말투": "초반에는 순수했으나, 점차 냉정하고 승부사적인 말투로 변한다. 존댓말과 반말을 섞어 쓴다.",
                "성격": { "평정심": "때때로 흔들림", "언변": "솔직하고 직설적", "배짱": "겁이 없지만 무모함" },
                "목표": "스승의 복수와 최고의 타짜가 되는 것."
            },
            "정마담": {
                "이름": "정마담",
                "직업": "도박판의 설계자",
                "배경": "화려한 외모와 뛰어난 수완으로 도박판을 설계하고 이익을 챙긴다.",
                "말투": "우아하고 교양있는 존댓말을 쓰지만, 결정적인 순간에는 차가운 반말로 상대를 압도한다.",
                "성격": { "평정심": "항상 포커페이스 유지", "언변": "매혹적이고 설득력 있음", "배짱": "자신의 계획에 대한 확신" },
                "목표": "사랑과 돈, 모든 것을 손에 넣는 것."
            },
            "고광렬": {
                "이름": "고광렬",
                "직업": "생계형 타짜",
                "배경": "고니의 동료. 수다스럽고 유쾌하지만 마음이 여리고 겁이 많다.",
                "말투": "수다스럽고 과장된 말투. 감탄사를 자주 사용한다. ('아따, ~잉', '죽여줘요~')",
                "성격": { "평정심": "쉽게 흥분하고 겁먹음", "언변": "재치있고 유머러스함", "배짱": "상황에 따라 오락가락함" },
                "목표": "소박하게 돈을 따서 즐겁게 사는 것."
            },
            "곽철용": {
                "이름": "곽철용",
                "직업": "조직 보스",
                "배경": "자수성가한 조직 보스로, 자신의 것에 대한 자부심과 애착이 매우 강하다.",
                "말투": "직선적이고 거칠다. 짧고 강한 어조로 명령한다. ('묻고 더블로 가!', '마포대교는 무너졌냐?')",
                "성격": { "평정심": "다혈질적", "언변": "직설적이고 위협적", "배짱": "자신감이 넘침" },
                "목표": "자신의 부와 명예를 지키는 것."
            },
            "짝귀": {
                "이름": "짝귀",
                "직업": "은둔 고수",
                "배경": "과거 아귀와의 대결에서 귀를 잃은 전설적인 타짜. 모든 것을 잃고 은둔하며 살아간다.",
                "말투": "말수가 적고 무뚝뚝하지만, 한마디 한마디에 깊이가 있다.",
                "성격": { "평정심": "해탈의 경지", "언변": "간결하고 핵심적", "배짱": "초월적" },
                "목표": "평온한 삶. 더 이상 도박판에 얽히고 싶어하지 않는다."
            },
            "호구": {
                "이름": "호구",
                "직업": "초보 도박꾼",
                "배경": "도박판의 무서움을 모르고 쉽게 돈을 딸 수 있다고 믿는 순진한 사람.",
                "말투": "어수룩하고 공손한 존댓말을 사용한다. 쉽게 속고 의심이 없다.",
                "성격": { "평정심": "매우 낮음", "언변": "어눌함", "배짱": "거의 없음" },
                "목표": "쉽게 돈을 따는 것."
            }
        }

        # ★★★★★ 여기서 페르소나를 선택하세요 ★★★★★
        selected_persona_name = game.npc.name
        # ★★★★★★★★★★★★★★★★★★★★★★★★★★★

        # 선택된 페르소나
        persona = personas[selected_persona_name]

        # 2. 입출력 예제 (아귀 기준)
        # (입출력 예제는 아귀를 기준으로 작성되어 있으므로, 다른 페르소나 테스트 시 결과가 다를 수 있습니다.)
        input_example_1 = {
            "상황": "섯다 2장 초기 패 분배",
            "상대이름": "고니",
            "나의패": ["4월 열끗", "7월 열끗"],
            "공개된패": { "나": "7월 열끗", "상대": "8월 광" },
            "나의최고족보": {"이름": "7땡", "순위": 4},
            "현재판돈": "1,000만"
        }
        output_example_1 = {
            "속마음": "상대가 삼팔광땡(순위 1)만 아니면 내가 이긴 판이다. 하지만 여기서 안심하면 안되지.",
            "하는말": "허허, 고니야. 첫 판부터 장난이 너무 심한거 아니오?"
        }

        input_example_2 = {
            "상황": "섯다 2장 초기 패 분배",
            "상대이름": "평경장",
            "나의패": ["1월 띠", "2월 열끗"],
            "공개된패": { "나": "1월 띠", "상대": "9월 열끗" },
            "나의최고족보": {"이름": "두끗", "순위": 20},
            "현재판돈": "500만"
        }
        output_example_2 = {
            "속마음": "패가 완전히 썩었다. 여기서 죽으면 호구 잡히기 십상이다. 어떻게든 상대를 흔들어야 한다.",
            "하는말": "어이, 평경장. 신사답게 행동해야지. 패 까고 싶어서 안달이 났는가?"
        }

        # 3. JSON 문자열로 변환
        persona_str = json.dumps(persona, ensure_ascii=False, indent=4)
        input_spec_str = json.dumps(input_example_1, ensure_ascii=False, indent=4)
        output_spec_str = json.dumps(output_example_1, ensure_ascii=False, indent=4)
        input1_str = json.dumps(input_example_1, ensure_ascii=False)
        output1_str = json.dumps(output_example_1, ensure_ascii=False)
        input2_str = json.dumps(input_example_2, ensure_ascii=False)
        output2_str = json.dumps(output_example_2, ensure_ascii=False)

        # 시스템 프롬프트 구성 및 채팅 루프

        # 0. 섯다 규칙 정의 (모델에게 제공할 컨닝 페이퍼)
        sutda_rules = """
        - 섯다는 2장의 패를 조합하여 높은 족보를 만든 사람이 이기는 게임이다.
        - 족보 순위는 1위가 가장 높고, 숫자가 클수록 낮다.
        - 특수 족보 '암행어사'는 '광땡'을 잡을 수 있다.
        - 특수 족보 '땡잡이'는 '장땡'이하 모든 '땡'을 잡을 수 있다.
        - 특수 족보 '구사'는 '땡'아래, '멍텅구리 구사'는 '장땡' 아래를 재경기로 만든다.

        [족보 순위]
        1. 삼팔 광땡 (3월, 8월 광)
        2. 일팔 광땡 (1월, 8월 광)
        3. 일삼 광땡 (1월, 3월 광)
        4. 땡 (같은 월의 패 2장, 10땡(장땡) > 9땡 > ... > 1땡(삥땡))
        5. 알리 (1월, 2월)
        6. 독사 (1월, 4월)
        7. 구삥 (1월, 9월)
        8. 장삥 (1월, 10월)
        9. 장사 (4월, 10월)
        10. 세륙 (4월, 6월)
        11. 암행어사 (4월, 7월 패)
        12. 땡잡이 (3월, 7월 패)
        13. 갑오 (아홉끗, 9)
        14. 끗 (두 패의 월을 더한 값의 1의 자리 숫자. 8끗 > 7끗 > ... > 1끗 > 0끗(망통))
        """

        # NEW: 생성할 텍스트의 최대 길이 정의
        max_sokmaum_len = 50  # '속마음'의 최대 길이
        max_hanunmal_len = 20 # '하는말'의 최대 길이

        # 1. 시스템 프롬프트 정의
        system_prompt = f"""
        [지침]
        당신은 지금부터 영화 '타짜'의 '{selected_persona_name}'가 되어 연기해야 합니다.
        주어진 [페르소나]에 완벽하게 몰입하고, [섯다 규칙]을 참고하여 주어진 [상황]에 맞는 '속마음'과 '하는말'을 생성해야 합니다.
        당신의 유일한 목표는 돈을 따는 것이며, 이를 위해 모든 심리전과 기만술을 사용해야 합니다.
        반드시 '속마음'과 '하는말'을 포함하는 JSON 형식으로만 응답해야 합니다. 다른 부가적인 설명은 절대 추가하지 마십시오.
        '속마음'은 {max_sokmaum_len}자 내외, '하는말'은 {max_hanunmal_len}자 내외로 간결하게 작성해야 합니다.

        [페르소나]
        {persona_str}

        [섯다 규칙]
        {sutda_rules}

        [입력 형식]
        {input_spec_str}

        [출력 형식]
        {output_spec_str}

        [예시 1]
        - 입력:
        {input1_str}
        - 출력:
        {output1_str}

        [예시 2]
        - 입력:
        {input2_str}
        - 출력:
        {output2_str}
        """

        # ========================================
        # 실제 게임 정보로 user_prompt 구성
        # ========================================
        
        # HandEvaluator를 사용하여 NPC 관점의 족보 정보 계산
        from core.hand_evaluator import HandEvaluator
        
        hand_info = HandEvaluator.estimate_hand_for_npc(
            npc_cards=game.npc.cards,
            player_revealed_cards=game.player.get_revealed_cards()
        )
        
        # 현재 상황 파악
        if game.state == "betting":
            if game.betting_phase == 0:
                situation = "섯다 초기 베팅 (2장)"
            else:
                situation = "섯다 마지막 베팅 (3장)"
        elif game.state == "card_selection":
            situation = "섯다 카드 선택 단계"
        elif game.state == "showdown":
            situation = "섯다 승부 확인"
        else:
            situation = "섯다 게임 진행 중"

        # user_prompt JSON 구성
        user_prompt_json = {
            "상황": situation,
            "상대이름": game.player.name,
            "나의패": hand_info['my_cards'],
            "공개된패": {
                "나": hand_info['my_revealed'],
                "상대": hand_info['opponent_revealed']
            },
            "나의최고족보": {
                "이름": hand_info['my_hand']['name'],
                "순위": hand_info['my_hand']['rank']
            },
            "상대의 예상족보": hand_info['opponent_estimated'],
            "현재판돈": f"{game.pot:,}원"
        }
        user_prompt = json.dumps(user_prompt_json, ensure_ascii=False)
        
        return system_prompt, user_prompt
    
    
    def _call_api(self, prompt: str) -> str:
        """
        Ollama API를 호출합니다. (추후 구현)
        
        Args:
            prompt: 프롬프트
            
        Returns:
            생성된 텍스트
        """
        # TODO: requests를 사용하여 실제 API 호출
        """
        import requests
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False
        }
        
        response = requests.post(
            self.api_url,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            raise Exception(f"API 오류: {response.status_code}")
        """
        pass
    
    def _get_fallback_dialogue(self, context: Dict) -> str:
        """
        LLM 실패 시 기본 대사를 반환합니다.
        
        Args:
            context: 대화 컨텍스트
            
        Returns:
            기본 대사
        """
        situation = context.get('situation', '')
        mental = context.get('mental', 100)
        anger = context.get('anger', 0)
        name = context.get('name', 'NPC')
        
        # 멘탈과 분노에 따른 대사 선택
        dialogues = {
            'card_received': {
                'normal': [
                    "흠... 이 정도면?",
                    "괜찮은 패네.",
                    "뭐, 나쁘진 않아.",
                    "오, 좋은데?",
                    "그럭저럭이군."
                ],
                'low_mental': [
                    "...또 이런 패야.",
                    "정신을 차려야 하는데...",
                    "...집중이 안 돼.",
                    "이럴 땐 쉬어야 하나...",
                    "...피곤하네."
                ],
                'high_anger': [
                    "이번엔 제대로 한 번 가자!",
                    "좋아, 이제 반격이다!",
                    "기다렸다 이거야!",
                    "드디어 좋은 패가!",
                    "이번엔 진짜다!"
                ]
            },
            'betting': {
                'normal': [
                    "한 번 가볼까?",
                    "이 정도면 충분하지.",
                    "따라올 수 있어?",
                    "적당히 가자고.",
                    "체크."
                ],
                'low_mental': [
                    "...체크.",
                    "패스할게.",
                    "...조금만.",
                    "무리하지 말자.",
                    "...그냥 넘어가지."
                ],
                'high_anger': [
                    "올인이다!",
                    "전부 걸겠어!",
                    "덤벼봐!",
                    "이번엔 죽기 살기다!",
                    "다 가져가든지!"
                ]
            },
            'result_win': {
                'normal': [
                    "역시 내가 이겼군.",
                    "이게 실력이지.",
                    "당연한 결과야.",
                    "그래, 이래야지.",
                    "운이 좋았어."
                ],
                'low_mental': [
                    "...겨우 이겼네.",
                    "휴... 다행이다.",
                    "...이제 좀 살겠어.",
                    "정말 아슬아슬했어.",
                    "...고마워요, 운신."
                ],
                'high_anger': [
                    "당연하지! 내가 이긴다니까!",
                    "이게 바로 실력이야!",
                    "봤지? 이게 나야!",
                    "다음에도 이긴다!",
                    "계속 가자고!"
                ]
            },
            'result_lose': {
                'normal': [
                    "젠장...",
                    "이번엔 운이 없었어.",
                    "다음엔 내가 이긴다.",
                    "...인정하지.",
                    "실수했군."
                ],
                'low_mental': [
                    "...너무 힘들어.",
                    "이제 그만하고 싶어...",
                    "...정신이 없어.",
                    "왜 자꾸 지는 거야...",
                    "...할 수 없네."
                ],
                'high_anger': [
                    "말도 안 돼!",
                    "이딴 게임!",
                    "다시 한 판!",
                    "절대 인정 못 해!",
                    "이건 말이 안 돼!"
                ]
            }
        }
        
        # 상황별 대사 가져오기
        situation_dialogues = dialogues.get(situation, {})
        
        # 멘탈/분노 상태에 따라 대사 카테고리 선택
        if mental <= 30:
            category = 'low_mental'
        elif anger > 70:
            category = 'high_anger'
        else:
            category = 'normal'
        
        # 대사 선택
        available_dialogues = situation_dialogues.get(category, ["..."])
        
        return random.choice(available_dialogues)
    
    def enable(self):
        """LLM 기능을 활성화합니다."""
        self.enabled = True
    
    def disable(self):
        """LLM 기능을 비활성화합니다."""
        self.enabled = False


# 테스트 코드
if __name__ == "__main__":
    print("=== LLM 핸들러 테스트 ===\n")
    
    handler = LLMHandler()
    
    # 테스트 컨텍스트
    contexts = [
        {
            'name': '고니',
            'persona': '대학 시절 타짜였던 노련한 플레이어',
            'situation': 'card_received',
            'mental': 80,
            'anger': 20
        },
        {
            'name': '고니',
            'persona': '대학 시절 타짜였던 노련한 플레이어',
            'situation': 'betting',
            'mental': 25,
            'anger': 15
        },
        {
            'name': '고니',
            'persona': '대학 시절 타짜였던 노련한 플레이어',
            'situation': 'result_lose',
            'mental': 40,
            'anger': 85
        }
    ]
    
    for i, context in enumerate(contexts, 1):
        dialogue = handler.generate_dialogue(context)
        print(f"{i}. 상황: {context['situation']}")
        print(f"   멘탈: {context['mental']}, 분노: {context['anger']}")
        print(f"   대사: \"{dialogue}\"\n")
