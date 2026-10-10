"""평가용 독립 비교: 손계산 상수, eig 기준 해, 안정성 판정을 기록한다.

np.linalg.eig는 구현 알고리즘이 아닌 비교 검증에만 사용한다.
"""

import numpy as np
from src.probability import ProbabilityLoss


def compare_power_iteration(matrix, value, vector, tolerance_percent=5.):
    """절댓값 최대 eig와 비교하고 부호를 정렬한 단위벡터 오차를 기록한다."""
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    index = int(np.argmax(np.abs(eigenvalues)))
    reference = float(eigenvalues[index])
    reference_vector = eigenvectors[:, index].real
    reference_vector /= np.linalg.norm(reference_vector)
    if np.dot(vector, reference_vector) < 0:
        reference_vector = -reference_vector
    error_percent = abs(value - reference) / abs(reference) * 100
    residual = float(np.linalg.norm(matrix @ vector - value * vector))
    vector_error = float(np.linalg.norm(vector - reference_vector))
    return {'reference_eig': reference, 'reference_eigenvector': reference_vector.tolist(),
            'relative_error_percent': float(error_percent), 'tolerance_percent': tolerance_percent,
            'passed': bool(error_percent <= tolerance_percent),
            'sign_aligned_vector_l2_error': vector_error,
            'vector_tolerance': 1e-6, 'vector_passed': bool(vector_error <= 1e-6),
            'residual_norm': residual, 'residual_tolerance': 1e-6,
            'residual_passed': bool(residual <= 1e-6)}


def hand_checkpoints():
    """노트북 수식으로 유도한 4자리 상수를 반환한다. 실행 결과에서 복사하지 않는다."""
    forward = {'z1': [.1, .3], 'a1': [.5250, .5744], 'z2': .6072,
               'y_pred': .6473, 'loss': .4350}
    backward = {'dy_pred': -1.5449, 'dz2': -.3527,
                'dW2': [-.1852, -.2026], 'da1': [-.1764, -.2116],
                'dz1': [-.0440, -.0517], 'dW1': [[-.0440, 0], [-.0517, 0]]}
    return forward, backward


def compare_hand_calculation(values, gradients):
    """손계산과 NumPy를 둘 다 round(...,4)한 뒤 shape과 각 원소를 비교한다."""
    rows = []
    for group, data, hand in zip(('forward', 'backward'), (values, gradients), hand_checkpoints()):
        for name, expected in hand.items():
            numpy_value = np.asarray(data[name])
            hand_value = np.asarray(expected)
            rounded_numpy = np.round(numpy_value, 4)
            rounded_hand = np.round(hand_value, 4)
            passed = (numpy_value.shape == hand_value.shape
                      and np.array_equal(rounded_numpy, rounded_hand))
            rows.append({'group': group, 'name': name, 'shape': list(numpy_value.shape),
                         'hand_rounded_4': rounded_hand.tolist(),
                         'numpy_rounded_4': rounded_numpy.tolist(), 'passed': bool(passed)})
    return {'decimals': 4, 'rows': rows, 'passed': all(row['passed'] for row in rows)}


def circle_stability(lr, history):
    """원형 이차함수의 증폭률과 실측 반경비로 수렴/진동/발산을 분류한다."""
    factor = 1 - 2 * lr
    magnitude = abs(factor)
    if magnitude < 1:
        regime = 'convergent'
    elif magnitude == 1:
        regime = 'oscillating' if factor < 0 else 'stationary'
    else:
        regime = 'divergent'
    measured = float(np.linalg.norm(history[-1]) / np.linalg.norm(history[0]))
    predicted = float(magnitude ** (len(history) - 1))
    return {'learning_rate': lr, 'coordinate_factor': factor, 'regime': regime,
            'radius_ratio': measured, 'predicted_radius_ratio': predicted,
            'matches_recurrence': bool(np.isclose(measured, predicted, atol=1e-12, rtol=1e-10)),
            'divergence_observed': bool(regime == 'divergent' and measured > 1)}


def verify_softmax_cases():
    """큰 양수·음수·동일점수·단일클래스 등 여러 입력을 절대오차로 검증한다."""
    results = []
    for logits in [[1000., 1001., 1002.], [-1000., -1001., -1002.],
                   [0., 0., 0.], [2., 1., -3.], [1000.]]:
        probabilities = ProbabilityLoss.softmax(logits)
        error = float(abs(probabilities.sum() - 1))
        passed = bool(error <= 1e-6 and np.all(np.isfinite(probabilities))
                      and np.all(probabilities >= 0) and np.all(probabilities <= 1))
        results.append({'logits': logits, 'probabilities': probabilities.tolist(),
                        'sum': float(probabilities.sum()), 'absolute_sum_error': error,
                        'tolerance': 1e-6, 'passed': passed})
    return results


def verify_loss_likelihood():
    """분포 확률로 계산한 NLL과 전개한 손실의 동치를 수치로 독립 검산한다."""
    y = np.array([1., 2., 3.])
    predictions = np.array([[1., 2., 3.], [.8, 2.2, 2.7], [0., 0., 0.]])
    variance = .5
    mse = np.mean((predictions - y) ** 2, axis=1)
    direct_gaussian_nll = -np.log(ProbabilityLoss.normal_pdf(y, predictions, variance)).sum(axis=1)
    expanded_gaussian_nll = len(y) / 2 * np.log(2 * np.pi * variance) + len(y) * mse / (2 * variance)
    labels = np.array([1., 0., 1.])
    q = np.array([.8, .3, .6])
    likelihood_b = np.prod(ProbabilityLoss.bernoulli_pmf(labels, q))
    bce_sum = -np.sum(labels * np.log(q) + (1 - labels) * np.log(1 - q))
    one_hot = np.array([[0., 0., 1.], [1., 0., 0.]])
    cat_q = np.array([ProbabilityLoss.softmax([0., 1., 2.]), ProbabilityLoss.softmax([2., 1., 0.])])
    likelihood_c = np.prod(np.prod(cat_q ** one_hot, axis=1))
    ce_sum = -np.sum(one_hot * np.log(cat_q))
    gaussian_error = float(np.max(np.abs(direct_gaussian_nll - expanded_gaussian_nll)))
    bernoulli_error = float(abs(-np.log(likelihood_b) - bce_sum))
    categorical_error = float(abs(-np.log(likelihood_c) - ce_sum))
    return {'gaussian': {'targets': y.tolist(), 'predictions': predictions.tolist(),
                         'variance': variance, 'mse': mse.tolist(),
                         'nll_from_pdf': direct_gaussian_nll.tolist(),
                         'nll_from_mse': expanded_gaussian_nll.tolist(),
                         'maximum_absolute_error': gaussian_error,
                         'same_minimizer_among_candidates': bool(np.argmin(mse) == np.argmin(direct_gaussian_nll))},
            'bernoulli': {'labels': labels.tolist(), 'probabilities': q.tolist(),
                          'likelihood': float(likelihood_b), 'nll': float(-np.log(likelihood_b)),
                          'bce_sum': float(bce_sum), 'absolute_error': bernoulli_error},
            'categorical': {'one_hot': one_hot.tolist(), 'probabilities': cat_q.tolist(),
                            'likelihood': float(likelihood_c), 'nll': float(-np.log(likelihood_c)),
                            'ce_sum': float(ce_sum), 'absolute_error': categorical_error},
            'tolerance': 1e-12,
            'passed': bool(max(gaussian_error, bernoulli_error, categorical_error) <= 1e-12
                           and np.argmin(mse) == np.argmin(direct_gaussian_nll))}
