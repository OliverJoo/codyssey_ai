"""MAC 연산과 점수 비교 관련 함수"""

import time

EPSILON = 1e-9


def calculate_mac(pattern, filter_matrix):
    """패턴과 필터를 위치별로 곱한 뒤 모두 더한다."""
    score = 0.0

    for row_index in range(len(pattern)):
        for col_index in range(len(pattern[row_index])):
            score += pattern[row_index][col_index] * filter_matrix[row_index][col_index]

    return score


def compare_mode1_scores(score_a, score_b, epsilon=EPSILON):
    """모드 1 판정: A / B / 판정 불가"""
    if abs(score_a - score_b) < epsilon:
        return "판정 불가"
    if score_a > score_b:
        return "A"
    return "B"


def compare_mode2_scores(score_cross, score_x, epsilon=EPSILON):
    """모드 2 판정: Cross / X / UNDECIDED"""
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"
    if score_cross > score_x:
        return "Cross"
    return "X"


def measure_average_mac_time(pattern, filter_matrix, repeat_count=10):
    """MAC 한 번의 평균 시간을 ms 단위로 측정한다."""
    start_time = time.perf_counter()

    for _ in range(repeat_count):
        calculate_mac(pattern, filter_matrix)

    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000
    average_ms = elapsed_ms / repeat_count
    return average_ms


def measure_average_compare_time(pattern, filter_a, filter_b, repeat_count=10):
    """모드 1에서 두 필터를 모두 비교하는 전체 연산 시간을 평균으로 측정한다."""
    start_time = time.perf_counter()

    for _ in range(repeat_count):
        calculate_mac(pattern, filter_a)
        calculate_mac(pattern, filter_b)

    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000
    average_ms = elapsed_ms / repeat_count
    return average_ms


def count_operations(size):
    """N x N 패턴의 MAC 연산 횟수(N²)를 반환한다."""
    return size * size