"""원격의 네 유틸 함수를 함께 실행하는 제출 패키지 추가 예제."""

from pathlib import Path
import sys


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from count_utils import count_words
from list_utils import remove_duplicates
from math_utils import is_even
from string_utils import reverse_string


if __name__ == "__main__":
    print("=== 4인 팀 Python Utils 추가 Demo ===")
    print("dave17code:", reverse_string("Hello World"))
    print("heeyoung35:", count_words("Hello Python Git Collaboration"))
    print("OliverJoo:", sorted(remove_duplicates([1, 2, 2, 3, 3])))
    print("hyunn9799:", is_even(-4))
