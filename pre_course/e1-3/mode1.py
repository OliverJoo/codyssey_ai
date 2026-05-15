"""모드 1: 3x3 수동 입력 처리"""

from mac import calculate_mac, compare_mode1_scores, count_operations, measure_average_compare_time


MATRIX_SIZE = 3



def parse_input_row(row_text, expected_size):
    """사용자 한 줄 입력을 숫자 리스트로 변환한다."""
    parts = row_text.strip().split()

    if len(parts) != expected_size:
        print(f"입력 형식 오류: 각 줄에 {expected_size}개의 숫자를 공백으로 구분해 입력하세요.")
        return None

    row_values = []

    for part in parts:
        try:
            row_values.append(float(part))
        except ValueError:
            print("입력 값 오류: 숫자만 입력하세요.")
            return None

    return row_values



def read_matrix(name, size):
    """size x size 행렬을 한 줄씩 입력받는다."""
    print(f"{name} ({size}줄 입력, 공백 구분)")
    matrix = []

    for row_number in range(size):
        while True:
            row_text = input().strip()
            parsed_row = parse_input_row(row_text, size)

            if parsed_row is not None:
                matrix.append(parsed_row)
                break

    print(f"{name} 저장 완료")
    return matrix



def run_mode1():
    """모드 1 전체 실행"""
    print("#---------------------------------------")
    print("# [1] 필터 입력")
    print("#---------------------------------------")
    filter_a = read_matrix("필터 A", MATRIX_SIZE)
    filter_b = read_matrix("필터 B", MATRIX_SIZE)

    print("#---------------------------------------")
    print("# [2] 패턴 입력")
    print("#---------------------------------------")
    pattern = read_matrix("패턴", MATRIX_SIZE)

    # 점수 계산
    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)
    verdict = compare_mode1_scores(score_a, score_b)

    # I/O를 제외한 연산 구간만 평균 시간 측정
    average_time_ms = measure_average_compare_time(pattern, filter_a, filter_b, repeat_count=10)

    print("#---------------------------------------")
    print("# [3] MAC 결과")
    print("#---------------------------------------")
    print(f"A 점수: {score_a:.10f}")
    print(f"B 점수: {score_b:.10f}")
    print(f"연산 시간(평균/10회): {average_time_ms:.6f} ms")
    print(f"연산 횟수(N²): {count_operations(MATRIX_SIZE)}")

    if verdict == "판정 불가":
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        print(f"판정: {verdict}")