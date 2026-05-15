"""모드 2: data.json 자동 테스트 처리"""

import json
import re

from label import normalize_label
from mac import calculate_mac, compare_mode2_scores, count_operations, measure_average_mac_time



def load_json_file(file_path):
    """JSON 파일을 읽어서 딕셔너리로 반환한다."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)



def extract_size_from_pattern_key(pattern_key):
    """size_13_1 같은 키에서 13을 추출한다."""
    match = re.match(r"^size_(\d+)_\d+$", pattern_key)
    if not match:
        return None
    return int(match.group(1))



def get_matrix_size(matrix):
    """정사각 행렬의 크기를 반환한다."""
    return len(matrix)



def is_valid_square_matrix(matrix, expected_size):
    """행렬이 expected_size x expected_size 형태인지 확인한다."""
    if not isinstance(matrix, list):
        return False

    if len(matrix) != expected_size:
        return False

    for row in matrix:
        if not isinstance(row, list):
            return False
        if len(row) != expected_size:
            return False

    return True



def normalize_filter_group(filter_group):
    """cross/x 키를 Cross/X로 바꿔서 새 딕셔너리를 만든다."""
    normalized_group = {}

    for raw_key, matrix in filter_group.items():
        normalized_key = normalize_label(raw_key)
        normalized_group[normalized_key] = matrix

    return normalized_group



def analyze_single_pattern(pattern_key, pattern_info, filters_data):
    """패턴 하나를 분석해서 결과를 딕셔너리로 반환한다."""
    size = extract_size_from_pattern_key(pattern_key)

    if size is None:
        return {
            "case_id": pattern_key,
            "status": "FAIL",
            "reason": "패턴 키 형식 오류"
        }

    filter_key = f"size_{size}"

    if filter_key not in filters_data:
        return {
            "case_id": pattern_key,
            "status": "FAIL",
            "reason": f"해당 크기의 필터 없음: {filter_key}"
        }

    if "input" not in pattern_info or "expected" not in pattern_info:
        return {
            "case_id": pattern_key,
            "status": "FAIL",
            "reason": "pattern 정보에 input 또는 expected 없음"
        }

    pattern = pattern_info["input"]
    expected_label = normalize_label(pattern_info["expected"])
    filter_group = normalize_filter_group(filters_data[filter_key])

    if "Cross" not in filter_group or "X" not in filter_group:
        return {
            "case_id": pattern_key,
            "status": "FAIL",
            "reason": f"{filter_key} 필터에 Cross/X가 모두 없음"
        }

    cross_filter = filter_group["Cross"]
    x_filter = filter_group["X"]

    if not is_valid_square_matrix(pattern, size):
        return {
            "case_id": pattern_key,
            "status": "FAIL",
            "reason": f"패턴 크기 오류: {size}x{size} 아님"
        }

    if not is_valid_square_matrix(cross_filter, size) or not is_valid_square_matrix(x_filter, size):
        return {
            "case_id": pattern_key,
            "status": "FAIL",
            "reason": f"필터 크기 오류: {filter_key}"
        }

    cross_score = calculate_mac(pattern, cross_filter)
    x_score = calculate_mac(pattern, x_filter)
    verdict = compare_mode2_scores(cross_score, x_score)

    if expected_label not in ["Cross", "X"]:
        return {
            "case_id": pattern_key,
            "cross_score": cross_score,
            "x_score": x_score,
            "verdict": verdict,
            "expected": expected_label,
            "status": "FAIL",
            "reason": "expected 라벨이 Cross/X로 정규화되지 않음"
        }

    if verdict == expected_label:
        return {
            "case_id": pattern_key,
            "cross_score": cross_score,
            "x_score": x_score,
            "verdict": verdict,
            "expected": expected_label,
            "status": "PASS",
            "reason": ""
        }

    fail_reason = "예상 라벨과 판정 결과가 다름"
    if verdict == "UNDECIDED":
        fail_reason = "동점(UNDECIDED) 처리 규칙에 따라 FAIL"

    return {
        "case_id": pattern_key,
        "cross_score": cross_score,
        "x_score": x_score,
        "verdict": verdict,
        "expected": expected_label,
        "status": "FAIL",
        "reason": fail_reason
    }



def build_cross_matrix(size):
    """성능 측정용 Cross 패턴을 만든다."""
    matrix = []
    center = size // 2

    for row in range(size):
        current_row = []
        for col in range(size):
            if row == center or col == center:
                current_row.append(1.0)
            else:
                current_row.append(0.0)
        matrix.append(current_row)

    return matrix



def collect_benchmark_rows(filters_data, patterns_data):
    """성능 분석 표에 사용할 데이터를 만든다."""
    benchmark_rows = []

    # 3x3은 JSON에 없으므로 기본 예시를 사용한다.
    pattern_3 = [
        [0.0, 1.0, 0.0],
        [1.0, 1.0, 1.0],
        [0.0, 1.0, 0.0]
    ]
    filter_3 = [
        [0.0, 1.0, 0.0],
        [1.0, 1.0, 1.0],
        [0.0, 1.0, 0.0]
    ]
    benchmark_rows.append((3, pattern_3, filter_3))

    for size in [5, 13, 25]:
        filter_key = f"size_{size}"
        if filter_key not in filters_data:
            continue

        normalized_filters = normalize_filter_group(filters_data[filter_key])
        cross_filter = normalized_filters["Cross"]

        selected_pattern = None
        for pattern_key, pattern_info in patterns_data.items():
            pattern_size = extract_size_from_pattern_key(pattern_key)
            if pattern_size == size:
                selected_pattern = pattern_info["input"]
                break

        if selected_pattern is None:
            selected_pattern = build_cross_matrix(size)

        benchmark_rows.append((size, selected_pattern, cross_filter))

    return benchmark_rows



def print_performance_table(filters_data, patterns_data):
    """성능 분석 표를 출력한다."""
    print("#---------------------------------------")
    print("# [3] 성능 분석 (평균/10회)")
    print("#---------------------------------------")
    print(f"{'크기':<10}{'평균 시간(ms)':<20}{'연산 횟수(N²)':<15}")
    print("-----------------------------------------------")

    benchmark_rows = collect_benchmark_rows(filters_data, patterns_data)

    for size, pattern, filter_matrix in benchmark_rows:
        average_ms = measure_average_mac_time(pattern, filter_matrix, repeat_count=10)
        operation_count = count_operations(size)
        print(f"{str(size) + 'x' + str(size):<10}{average_ms:<20.6f}{operation_count:<15}")



def run_mode2(file_path="data.json"):
    """모드 2 전체 실행"""
    data = load_json_file(file_path)
    filters_data = data.get("filters", {})
    patterns_data = data.get("patterns", {})

    print("#---------------------------------------")
    print("# [1] 필터 로드")
    print("#---------------------------------------")
    for filter_key, filter_group in filters_data.items():
        normalized_group = normalize_filter_group(filter_group)
        loaded_labels = ", ".join(normalized_group.keys())
        print(f"✓ {filter_key} 필터 로드 완료 ({loaded_labels})")

    print("#---------------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#---------------------------------------")

    results = []

    for pattern_key, pattern_info in patterns_data.items():
        result = analyze_single_pattern(pattern_key, pattern_info, filters_data)
        results.append(result)

        print(f"--- {pattern_key} ---")
        if "cross_score" in result and "x_score" in result:
            print(f"Cross 점수: {result['cross_score']:.10f}")
            print(f"X 점수: {result['x_score']:.10f}")
            print(
                f"판정: {result['verdict']} | expected: {result['expected']} | {result['status']}"
            )
            if result["status"] == "FAIL":
                print(f"사유: {result['reason']}")
        else:
            print(f"FAIL | 사유: {result['reason']}")

    print_performance_table(filters_data, patterns_data)

    total_count = len(results)
    pass_count = 0
    fail_results = []

    for result in results:
        if result["status"] == "PASS":
            pass_count += 1
        else:
            fail_results.append(result)

    fail_count = total_count - pass_count

    print("#---------------------------------------")
    print("# [4] 결과 요약")
    print("#---------------------------------------")
    print(f"총 테스트: {total_count}개")
    print(f"통과: {pass_count}개")
    print(f"실패: {fail_count}개")

    if fail_results:
        print("실패 케이스:")
        for fail_result in fail_results:
            print(f"- {fail_result['case_id']}: {fail_result['reason']}")