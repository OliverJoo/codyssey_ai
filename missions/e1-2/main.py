import json
import os

STATE_FILE = "state.json"  # 데이터 저장 파일명
BACKUP_FILE = "state.json.bak"  # 손상 시 백업 파일명
NUM_CHOICES = 4  # 선택지 개수 (고정 4개)
MIN_MENU = 1  # 메뉴 최솟값
MAX_MENU = 5  # 메뉴 최댓값
MIN_ANSWER = 1  # 정답 번호 최솟값
MAX_ANSWER = 4  # 정답 번호 최댓값
PERFECT_SCORE = 100  # 만점 기준 (퍼센트 환산)
SEPARATOR_THIN = "-" * 44  # 구분선
SEPARATOR_THICK = "=" * 44  # 구분선

# 디폴트 퀴즈
DEFAULT_QUIZZES = [
    {
        "question": "Python의 창시자는 누구인가요?",
        "choices": ["제임스 고슬링", "귀도 반 로섬", "리누스 토발즈", "데니스 리치"],
        "answer": 2
    },
    {
        "question": "Python에서 빈 리스트를 만드는 올바른 방법은?",
        "choices": ["list = {}", "list = []", "list = ()", "list = <>"],
        "answer": 2
    },
    {
        "question": "Python에서 주석을 작성할 때 사용하는 기호는?",
        "choices": ["//", "/*", "#", "--"],
        "answer": 3
    },
    {
        "question": "Python에서 정수형 데이터 타입을 나타내는 키워드는?",
        "choices": ["integer", "int", "num", "number"],
        "answer": 2
    },
    {
        "question": "Python에서 함수를 정의할 때 사용하는 키워드는?",
        "choices": ["function", "func", "def", "define"],
        "answer": 3
    },
    {
        "question": "Python에서 True/False를 다루는 데이터 타입은?",
        "choices": ["int", "str", "bool", "float"],
        "answer": 3
    },
    {
        "question": "Python에서 딕셔너리(dict)를 생성할 때 사용하는 괄호는?",
        "choices": ["[ ]", "( )", "{ }", "< >"],
        "answer": 3
    },
]


# ============================================================
# Quiz 클래스
# 역할: 개별 퀴즈 한 개의 데이터(질문/선택지/정답)를 표현하고
#       해당 데이터에 직접 관련된 동작(출력, 정답 확인, 직렬화)을 담당
# ============================================================
class Quiz:

    def __init__(self, question: str, choices: list, answer: int):
        self.question = question
        self.choices  = choices
        self.answer   = answer

    def display(self, index: int):
        pass

    def is_correct(self, user_answer: int) -> bool:
        pass

    def to_dict(self) -> dict:
        pass

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        pass

# ============================================================
# QuizGame 클래스
# 역할: 게임 전체 흐름(메뉴/입력 처리/게임 진행/점수/저장·불러오기)을 담당
# ============================================================
class QuizGame:

    def __init__(self):
        self.quizzes: list   = []
        self.high_score: int = 0
        self.load_state()

    # --- 데이터 저장/불러오기 ---

    def load_state(self):
        pass

    def save_state(self):
        pass

    def _init_default_quizzes(self):
        pass

    # --- UI 출력 ---

    def show_menu(self):
        pass

    # --- 입력 처리(검증) ---

    def get_valid_input(self, prompt: str, min_val: int, max_val: int) -> int:
        pass

    def get_valid_string(self, prompt: str) -> str:
        pass

    # --- 게임 진행 ---

    def run_quiz(self):
        pass

    def add_quiz(self):
        pass

    def show_quiz_list(self):
        pass

    def show_high_score(self):
        pass


def main():
    pass


if __name__ == '__main__':
    main()
