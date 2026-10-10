"""평가 검증기가 잘못된 결과를 실제로 거부하는지 확인한다."""

import unittest
import os
from pathlib import Path

os.environ['MPLCONFIGDIR'] = str(Path(__file__).resolve().parents[1] / '.cache' / 'matplotlib')

import numpy as np
from scripts.assessment import (compare_power_iteration, compare_hand_calculation, circle_stability,
                                verify_softmax_cases, verify_loss_likelihood)
from src.calculus import derivative_sensitivity
from src.backprop import fixed_example, forward_backward
from src.linear_algebra import power_iteration
from src.optimizer import VanillaGD, optimize, circle_gradient


class AssessmentTests(unittest.TestCase):
    """부호 모호성, 잘못된 손계산, 학습률 경계값을 검사한다."""

    def test_eigenvector_sign_is_equivalent_but_wrong_vector_fails(self):
        """v와 -v는 같게 취급하고 고유공간 밖의 벡터는 거부한다."""
        matrix = np.array([[4., 1.], [1., 3.]])
        value, vector, _ = power_iteration(matrix)
        self.assertTrue(compare_power_iteration(matrix, value, -vector)['vector_passed'])
        wrong = compare_power_iteration(matrix, value, np.array([1., 0.]))
        self.assertFalse(wrong['vector_passed'])
        self.assertFalse(wrong['residual_passed'])

    def test_hand_comparison_rejects_pdf_typo_and_wrong_shape(self):
        """참고 예시의 -.0513 및 (1,2) 모양을 통과시키지 않는다."""
        values, gradients = forward_backward(**fixed_example())
        self.assertTrue(compare_hand_calculation(values, gradients)['passed'])
        altered = {**gradients, 'dz1': np.array([-.0440, -.0513])}
        self.assertFalse(compare_hand_calculation(values, altered)['passed'])
        altered = {**gradients, 'dW2': gradients['dW2'].reshape(1, 2)}
        self.assertFalse(compare_hand_calculation(values, altered)['passed'])

    def test_learning_rate_boundary_and_observed_divergence(self):
        """.5 수렴, 1 진동, 1.1 발산을 실제 경로와 점화식으로 확인한다."""
        for lr, expected in [(.5, 'convergent'), (1., 'oscillating'), (1.1, 'divergent')]:
            history = optimize(VanillaGD(lr), circle_gradient, steps=20)
            result = circle_stability(lr, history)
            self.assertEqual(result['regime'], expected)
            self.assertTrue(result['matches_recurrence'])
            self.assertEqual(result['divergence_observed'], lr > 1)

    def test_sensitivity_distinguishes_truncation_from_cancellation(self):
        """sin의 보통 h 구간은 O(h²), 아주 작은 h는 반올림 영향이 커진다."""
        rows = derivative_sensitivity()
        errors = {row['h']: row['absolute_error'] for row in rows if row['function'] == 'sin(x)'}
        self.assertTrue(90 < errors[.1] / errors[.01] < 110)
        self.assertTrue(90 < errors[.01] / errors[.001] < 110)
        self.assertGreater(errors[1e-13], errors[1e-5])

    def test_distribution_likelihoods_match_losses_and_softmax_cases(self):
        """분포를 대입한 우도와 전개된 손실 및 확률 정규화를 검증한다."""
        checks = verify_loss_likelihood()
        self.assertTrue(checks['passed'])
        self.assertAlmostEqual(checks['bernoulli']['likelihood'], .8 * .7 * .6)
        self.assertTrue(all(row['passed'] for row in verify_softmax_cases()))


if __name__ == '__main__':
    unittest.main()
