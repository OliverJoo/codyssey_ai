# test comments

import json
import shutil

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
        self.choices = choices
        self.answer = answer

    def display(self, index: int):
        print(f"\n[문제 {index}]")
        print(f"  {self.question}")
        print()

        for i, choice in enumerate(self.choices, start=1):
            print(f"  {i}. {choice}")

    def is_correct(self, user_answer: int) -> bool:
        return user_answer == self.answer

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"],
        )


# ============================================================
# QuizGame 클래스
# 역할: 게임 전체 흐름(메뉴/입력 처리/게임 진행/점수/저장·불러오기)을 담당
# ============================================================
class QuizGame:

    def __init__(self):
        self.quizzes: list = []
        self.high_score: int = 0
        self.load_state()

    # def load_state(self):
    #     try:
    #         with open(STATE_FILE, "r", encoding="utf-8") as f:
    #             data = json.load(f)
    #         self.quizzes = [Quiz.from_dict(q) for q in data.get("quizzes", [])]
    #         self.high_score = data.get("high_score", 0)
    #         print(f"저장된 데이터를 불러왔습니다.(퀴즈 {len(self.quizzes)}개, 최고점수 {self.high_score}점)")
    #     except FileNotFoundError:
    #         print("저장된 파일이 없습니다. 기본 퀴즈 데이터를 사용합니다.")
    #         self._init_default_quizzes()
    #     except json.JSONDecodeError:
    #         print(f"저장 파일이 손상되었습니다. "
    #               f"'{BACKUP_FILE}'로 백업 후 기본 데이터로 초기화합니다.")
    #         try:
    #             shutil.copy(STATE_FILE, BACKUP_FILE)
    #         except OSError:
    #             print("백업 파일 생성에 실패했습니다.")
    #         self._init_default_quizzes()
    #     except IOError as e:
    #         print(f"파일 읽기 오류: {e}")
    #         print("기본 퀴즈 데이터를 사용합니다.")
    #         self._init_default_quizzes()

    def load_state(self):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.quizzes = [Quiz.from_dict(q) for q in data.get("quizzes", [])]
            self.high_score = data.get("high_score", 0)

            if not isinstance(self.high_score, int):
                raise ValueError("high_score는 정수여야 합니다.")

            print(f"저장된 데이터를 불러왔습니다.(퀴즈 {len(self.quizzes)}개, 최고점수 {self.high_score}점)")

        except FileNotFoundError:
            print("저장된 파일이 없습니다. 기본 퀴즈 데이터를 사용합니다.")
            self._init_default_quizzes()

        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            print(f"저장 파일이 손상되었습니다. '{BACKUP_FILE}'로 백업 후 기본 데이터로 초기화합니다.")
            try:
                shutil.copy(STATE_FILE, BACKUP_FILE)
            except OSError:
                print("백업 파일 생성에 실패했습니다.")
            self._init_default_quizzes()

        except IOError as e:
            print(f"파일 읽기 오류: {e}")
            print("기본 퀴즈 데이터를 사용합니다.")
            self._init_default_quizzes()

    def save_state(self):
        try:
            data = {
                "quizzes": [q.to_dict() for q in self.quizzes],
                "high_score": self.high_score,
            }
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"저장 실패: {e}")
            print("이번 변경 사항은 파일에 저장되지 않았습니다.")

    def _init_default_quizzes(self):
        self.quizzes = [Quiz.from_dict(q) for q in DEFAULT_QUIZZES]
        self.high_score = 0

    def show_menu(self):
        print("\n" + SEPARATOR_THICK)
        print(" - 단순 퀴즈 게임 - ")
        print(SEPARATOR_THICK)
        print("  1. 퀴즈 풀기")
        print("  2. 퀴즈 추가")
        print("  3. 퀴즈 목록 보기")
        print("  4. 최고 점수 확인")
        print("  5. 종료")
        print(SEPARATOR_THICK)

    def get_valid_input(self, prompt: str, min_val: int, max_val: int) -> int:
        while True:
            try:
                raw = input(prompt)
                stripped = raw.strip()

                if stripped == "":
                    print(f"입력값이 없습니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.")
                    continue

                number = int(stripped)

                if number < min_val or number > max_val:
                    print(f"{min_val}~{max_val} 사이의 숫자를 입력하세요. "
                          f"(입력값: {number})")
                    continue

                return number

            except ValueError:
                print(f"숫자만 입력할 수 있습니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.")

    def get_valid_string(self, prompt: str) -> str:
        while True:
            value = input(prompt).strip()
            if value == "":
                print("내용을 입력해주세요. 빈 값은 허용되지 않습니다.")
                continue
            return value

    def run_quiz(self):
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해주세요.")
            return

        total = len(self.quizzes)
        correct_count = 0

        print(f"\n퀴즈를 시작합니다! (총 {total}문제)")
        print(SEPARATOR_THIN)

        for index, quiz in enumerate(self.quizzes, start=1):
            quiz.display(index)
            user_answer = self.get_valid_input("  정답 입력: ", MIN_ANSWER, MAX_ANSWER)

            if quiz.is_correct(user_answer):
                print("정답입니다!")
                correct_count += 1
            else:
                correct_text = quiz.choices[quiz.answer - 1]
                print(f"오답입니다. 정답은 {quiz.answer}번 '{correct_text}' 입니다.")
            print(SEPARATOR_THIN)

        score = round((correct_count / total) * PERFECT_SCORE)

        print(f"\n{SEPARATOR_THICK}")
        print(f"결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")

        if score > self.high_score:
            self.high_score = score
            print("새로운 최고 점수입니다!")
            self.save_state()
        else:
            print(f"현재 최고 점수: {self.high_score}점")
        print(SEPARATOR_THICK)

    def add_quiz(self):
        print("\n새로운 퀴즈를 추가합니다.")
        print(SEPARATOR_THIN)

        question = self.get_valid_string("문제를 입력하세요: ")

        choices = []
        for i in range(1, NUM_CHOICES + 1):
            choice = self.get_valid_string(f"선택지 {i}: ")
            choices.append(choice)

        answer = self.get_valid_input(f"  정답 번호 ({MIN_ANSWER}-{MAX_ANSWER}): ", MIN_ANSWER, MAX_ANSWER)

        self.quizzes.append(Quiz(question=question, choices=choices, answer=answer))
        self.save_state()
        print("퀴즈가 추가되었습니다!")

    def show_quiz_list(self):
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다.")
            return

        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print(SEPARATOR_THIN)

        for i, quiz in enumerate(self.quizzes, start=1):
            print(f"  [{i}] {quiz.question}")
            for j, choice in enumerate(quiz.choices, start=1):
                marker = "★" if j == quiz.answer else "  "
                print(f"        {marker} {j}. {choice}")
            print()
        print(SEPARATOR_THIN)

    def show_high_score(self):
        print()
        if self.high_score == 0:
            print("아직 퀴즈를 풀지 않았습니다. 퀴즈를 풀어보세요!")
        else:
            print(f"최고 점수: {self.high_score}점")

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = self.get_valid_input("  선택: ", MIN_MENU, MAX_MENU)

                if choice == 1:
                    self.run_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.show_quiz_list()
                elif choice == 4:
                    self.show_high_score()
                elif choice == 5:
                    self.save_state()
                    print("\n프로그램을 종료합니다. 안녕히 가세요!")
                    break

        except (KeyboardInterrupt, EOFError) as e:
            if isinstance(e, KeyboardInterrupt):
                print("\n\nCtrl+C 입력 감지. 데이터를 저장하고 종료합니다...")
            else:
                print("\n\n입력 스트림 종료. 데이터를 저장하고 종료합니다...")

            self.save_state()
            print("프로그램을 안전하게 종료했습니다.")


def main():
    game = QuizGame()
    game.run()


if __name__ == '__main__':
    main()
