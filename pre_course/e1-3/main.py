# 행(row)을 먼저 zip으로 묶고, 그 안의 원소(v)를 다시 zip으로 묶어 비교.
# matrix1, 2 열고 내부에 r1, r2로 1:1 매칭 후 xor 계산
# hamming_dist = sum(v1 ^ v2 for r1, r2 in zip(matrix1, matrix2) for v1, v2 in zip(r1, r2))

"""Mini NPU Simulator 메인 실행 파일"""

from mode1 import run_mode1
from mode2 import run_mode2



def main():
    print("=== Mini NPU Simulator ===")
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")

    mode = input("선택: ").strip()

    if mode == "1":
        run_mode1()
    elif mode == "2":
        run_mode2("data.json")
    else:
        print("잘못된 입력입니다. 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()