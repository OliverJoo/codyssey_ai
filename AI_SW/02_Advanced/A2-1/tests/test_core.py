"""PDF의 필수 수치 기준과 고정 예제를 구현 전에 테스트로 정리했다."""

import unittest
import os
from pathlib import Path

os.environ['MPLCONFIGDIR'] = str(Path(__file__).resolve().parents[1] / '.cache' / 'matplotlib')

import numpy as np

from src.linear_algebra import (
    unit_circle, rotation_matrix, scaling_matrix, shear_matrix,
    transform_points, polygon_area, power_iteration, svd_compress,
    svd_reconstruct,
)
from src.calculus import central_difference, numerical_gradient
from src.backprop import fixed_example, forward_backward
from src.optimizer import (
    VanillaGD, Momentum, optimize, circle_loss, circle_gradient,
    ellipse_loss, ellipse_gradient,
)
from src.probability import ProbabilityLoss


class LinearAlgebraTests(unittest.TestCase):
    """변환, 면적, 고유값, SVD의 수학적 성질을 확인한다."""

    def test_rotation_preserves_radius(self):
        """회전한 단위 원의 반지름은 1이다."""
        points = transform_points(unit_circle(), rotation_matrix(np.pi / 4))
        np.testing.assert_allclose(np.linalg.norm(points, axis=1), 1)

    def test_scaling_and_shear(self):
        """PDF의 스케일링과 전단이 각각 좌표 정의대로 작동한다."""
        points = np.array([[1., 0.], [0., 1.]])
        np.testing.assert_allclose(transform_points(points, scaling_matrix(2, .5)),
                                   [[2, 0], [0, .5]])
        np.testing.assert_allclose(transform_points(points, shear_matrix(1)),
                                   [[1, 0], [1, 1]])

    def test_determinant_area_error_below_one_percent(self):
        """다각형으로 측정한 면적비와 |det(A)|의 오차가 1% 이하다."""
        points = unit_circle()
        matrices = [rotation_matrix(.7), scaling_matrix(2, .5), shear_matrix(.8)]
        for matrix in matrices:
            ratio = polygon_area(transform_points(points, matrix)) / polygon_area(points)
            expected = abs(np.linalg.det(matrix))
            self.assertLessEqual(abs(ratio - expected) / expected, .01)

    def test_power_iteration_matches_verification_eig(self):
        """직접 구현한 Power Iteration을 검증 전용 eig와 비교한다."""
        matrix = np.array([[4., 1.], [1., 3.]])
        value, vector, iterations = power_iteration(matrix)
        expected = np.linalg.eig(matrix)[0].max()  # 비교 검증에만 사용했다.
        self.assertLessEqual(abs(value - expected) / expected, .05)
        np.testing.assert_allclose(matrix @ vector, value * vector, atol=1e-6)
        self.assertGreater(iterations, 0)

    def test_svd_error_decreases_and_rank_is_capped(self):
        """k 증가에 따라 오차가 감소하며 k=100은 64개 성분으로 제한한다."""
        image = np.random.default_rng(42).random((64, 64))
        errors = []
        for requested in [10, 50, 100]:
            factors = svd_compress(image, requested)
            errors.append(np.mean((image - svd_reconstruct(*factors)) ** 2))
            self.assertEqual(len(factors[1]), min(requested, 64))
        self.assertGreater(errors[0], errors[1])
        self.assertLess(errors[2], 1e-25)


class CalculusTests(unittest.TestCase):
    """중심차분과 등고선 수직 조건을 확인한다."""

    def test_central_difference_at_three(self):
        """x²의 x=3 미분값과 6의 차이는 1e-4 이하다."""
        self.assertLessEqual(abs(central_difference(lambda x: x ** 2, 3.) - 6), 1e-4)

    def test_gradient_is_perpendicular_to_circle_tangent(self):
        """여러 점에서 기울기와 원의 접선 내적이 0이다."""
        for point in [[1., 2.], [-2., 1.], [2., -3.]]:
            gradient = numerical_gradient(circle_loss, np.array(point))
            np.testing.assert_allclose(gradient, 2 * np.array(point), atol=1e-7)
            self.assertAlmostEqual(float(gradient @ np.array([-point[1], point[0]])), 0, places=6)


class BackpropTests(unittest.TestCase):
    """독립적으로 계산한 상수와 중심차분으로 역전파를 검증한다."""

    def test_forward_hand_checkpoints(self):
        """반올림은 출력 시점에만 하며 손계산과 4자리까지 일치한다."""
        values, _ = forward_backward(**fixed_example())
        expected = {'z1': [.1, .3], 'a1': [.52497918747894, .574442516811659],
                    'z2': .6071551038264654, 'y_pred': .6472915699946178,
                    'loss': .4349584368514606}
        for key, value in expected.items():
            np.testing.assert_array_equal(np.round(values[key], 4), np.round(value, 4))

    def test_backward_hand_checkpoints_and_shapes(self):
        """PDF가 지정한 여섯 미분과 각 shape을 모두 확인한다."""
        _, gradients = forward_backward(**fixed_example())
        expected = {
            'dy_pred': -1.544898846756671, 'dz2': -.35270843000538225,
            'dW2': [-.18516458500119815, -.20261071823298064],
            'da1': [-.17635421500269112, -.21162505800322935],
            'dz1': [-.04397851580869701, -.05173350439092561],
            'dW1': [[-.04397851580869701, 0], [-.05173350439092561, 0]],
        }
        for key, value in expected.items():
            self.assertEqual(np.shape(gradients[key]), np.shape(value))
            np.testing.assert_array_equal(np.round(gradients[key], 4), np.round(value, 4))

    def test_all_parameter_gradients_match_finite_difference(self):
        """가중치와 편향의 분석적 미분을 손실 중심차분과 비교한다."""
        example = fixed_example()
        _, gradients = forward_backward(**example)
        for name in ['W1', 'b1', 'W2', 'b2']:
            parameter = np.asarray(example[name], dtype=float)
            numerical = np.zeros_like(parameter)
            for index in np.ndindex(parameter.shape):
                plus, minus = parameter.copy(), parameter.copy()
                plus[index] += 1e-5
                minus[index] -= 1e-5
                loss_plus = forward_backward(**{**example, name: plus})[0]['loss']
                loss_minus = forward_backward(**{**example, name: minus})[0]['loss']
                numerical[index] = (loss_plus - loss_minus) / 2e-5
            np.testing.assert_allclose(gradients['d' + name], numerical, atol=1e-8)


class OptimizerTests(unittest.TestCase):
    """업데이트 식과 실제 수렴/발산 조건을 확인한다."""

    def test_gd_step_and_radius_after_100_updates(self):
        """lr=.1에서 100회 뒤 반경은 .1 이하다."""
        optimizer = VanillaGD(lr=.1)
        np.testing.assert_allclose(optimizer.step(np.array([5., 5.]), np.array([10., 10.])), [4, 4])
        history = optimize(VanillaGD(.1), circle_gradient, [5, 5], 100)
        self.assertEqual(history.shape, (101, 2))
        self.assertLessEqual(np.linalg.norm(history[-1]), .1)

    def test_half_learning_rate_reaches_zero(self):
        """원의 lr=.5는 발산하지 않고 한 번에 원점에 도달한다."""
        np.testing.assert_allclose(optimize(VanillaGD(.5), circle_gradient, [5, 5], 1)[-1], [0, 0])

    def test_learning_rate_above_one_diverges(self):
        """PDF의 .5 이상 조건 중 lr=1.1을 선택하면 실제 발산한다."""
        history = optimize(VanillaGD(1.1), circle_gradient, [5, 5], 20)
        self.assertGreater(np.linalg.norm(history[-1]), np.linalg.norm(history[0]))

    def test_momentum_accumulates_gradient(self):
        """v=beta*v+g, theta=theta-lr*v 정의의 두 번 업데이트를 확인한다."""
        optimizer = Momentum(.1, beta=.9)
        point = optimizer.step(np.array([5., 5.]), np.array([10., 10.]))
        np.testing.assert_allclose(optimizer.step(point, np.array([8., 8.])), [2.3, 2.3])
        self.assertIsInstance(optimizer, VanillaGD)

    def test_momentum_advantage_on_ellipse_at_point_zero_one(self):
        """lr=.01의 타원에서는 Momentum이 손실 .01에 먼저 도달한다."""
        gd = optimize(VanillaGD(.01), ellipse_gradient, [5, 5], 200)
        momentum = optimize(Momentum(.01, .9), ellipse_gradient, [5, 5], 200)
        self.assertLess(np.flatnonzero(ellipse_loss(momentum) <= .01)[0],
                        np.flatnonzero(ellipse_loss(gd) <= .01)[0])


class ProbabilityTests(unittest.TestCase):
    """분포의 정의와 안정적인 Softmax를 확인한다."""

    def test_normal_variance_parameter_and_integral(self):
        """N(2,.5)의 두 번째 인수를 분산으로 사용하고 적분이 1인지 확인한다."""
        x = np.linspace(-10, 10, 20001)
        for mean, variance in [(0, 1), (2, .5)]:
            pdf = ProbabilityLoss.normal_pdf(x, mean, variance)
            self.assertAlmostEqual(float(np.trapz(pdf, x)), 1, places=6)
            self.assertAlmostEqual(float(ProbabilityLoss.normal_pdf(mean, mean, variance)),
                                   1 / np.sqrt(2 * np.pi * variance))

    def test_bernoulli_pmf(self):
        """B(.3), B(.7)의 0과 1 확률 합은 각각 1이다."""
        for p in [.3, .7]:
            values = ProbabilityLoss.bernoulli_pmf(np.array([0, 1]), p)
            np.testing.assert_allclose(values, [1 - p, p])
            self.assertAlmostEqual(float(values.sum()), 1)

    def test_softmax_sum_stability_and_shift_invariance(self):
        """큰 로짓도 overflow 없이 합 1과 상수 이동 불변성을 만족한다."""
        values = ProbabilityLoss.softmax(np.array([1000., 1001., 1002.]))
        self.assertTrue(np.isfinite(values).all())
        self.assertLessEqual(abs(values.sum() - 1), 1e-6)
        np.testing.assert_allclose(values, ProbabilityLoss.softmax(np.array([0., 1., 2.])))


if __name__ == '__main__':
    unittest.main()
