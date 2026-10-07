"""보너스는 별도 테스트와 상속 모듈로 분리했다."""

import os
from pathlib import Path
import unittest

os.environ['MPLCONFIGDIR'] = str(Path(__file__).resolve().parents[1] / '.cache' / 'matplotlib')

import numpy as np

from src.optimizer import VanillaGD, Momentum, optimize, ellipse_gradient, ellipse_loss
from src.probability import ProbabilityLoss
from src.bonus_optimizer import Adam, NewtonMethod
from src.bonus_probability import InformationTheory


class BonusOptimizerTests(unittest.TestCase):
    """상속 관계와 Adam 편향 보정, Newton의 Hessian 계산을 확인한다."""

    def test_adam_inherits_momentum(self):
        """보너스 Adam은 기본 Momentum을 상속한다."""
        self.assertIsInstance(Adam(), Momentum)

    def test_adam_bias_corrected_first_and_second_steps(self):
        """크기가 다른 기울기 두 개로 1·2차 모멘트 편향 보정을 검증한다."""
        optimizer = Adam(lr=.1)
        point = optimizer.step(np.array([5., 5.]), np.array([2., 4.]))
        np.testing.assert_allclose(point, [4.9, 4.9], atol=1e-8)
        second = optimizer.step(point, np.array([4., 2.]))
        m = .9 * np.array([.2, .4]) + .1 * np.array([4., 2.])
        v = .999 * .001 * np.array([4., 16.]) + .001 * np.array([16., 4.])
        expected = point - .1 * (m / (1 - .9 ** 2)) / (np.sqrt(v / (1 - .999 ** 2)) + 1e-8)
        np.testing.assert_allclose(second, expected)
        self.assertEqual(optimizer.t, 2)

    def test_newton_inherits_gd_and_solves_quadratic_in_one_step(self):
        """타원 Hessian diag(2,20)을 사용하면 한 번에 원점에 도달한다."""
        optimizer = NewtonMethod(lambda point: np.diag([2., 20.]))
        self.assertIsInstance(optimizer, VanillaGD)
        history = optimize(optimizer, ellipse_gradient, [5, 5], 1)
        np.testing.assert_allclose(history[-1], [0, 0])
        self.assertLess(ellipse_loss(history[-1]), ellipse_loss(
            optimize(VanillaGD(.01), ellipse_gradient, [5, 5], 1)[-1]))


class InformationTheoryTests(unittest.TestCase):
    """엔트로피, KL, 교차 엔트로피의 정의 및 영확률 경계를 확인한다."""

    def test_inherits_required_probability_class(self):
        """정보 이론은 필수 확률 클래스의 Softmax를 재사용한다."""
        self.assertIsInstance(InformationTheory(), ProbabilityLoss)
        np.testing.assert_allclose(InformationTheory.softmax([0, 0]), [.5, .5])

    def test_uniform_entropy_and_identical_kl(self):
        """공정한 동전의 엔트로피는 ln2 nats, 같은 분포의 KL은 0이다."""
        self.assertAlmostEqual(InformationTheory.entropy([.5, .5]), np.log(2))
        self.assertAlmostEqual(InformationTheory.kl_divergence([.3, .7], [.3, .7]), 0)

    def test_cross_entropy_equals_entropy_plus_kl(self):
        """H(p,q)=H(p)+D_KL(p||q)를 서로 다른 분포에서 확인한다."""
        p, q = [.3, .7], [.6, .4]
        self.assertAlmostEqual(InformationTheory.cross_entropy(p, q),
                               InformationTheory.entropy(p) + InformationTheory.kl_divergence(p, q))

    def test_zero_probability_and_impossible_event(self):
        """0log0=0이며 p>0, q=0 사건의 CE/KL은 무한대다."""
        self.assertEqual(InformationTheory.entropy([1, 0]), 0)
        self.assertEqual(InformationTheory.cross_entropy([1, 0], [1, 0]), 0)
        self.assertTrue(np.isinf(InformationTheory.cross_entropy([1, 0], [0, 1])))
        self.assertTrue(np.isinf(InformationTheory.kl_divergence([1, 0], [0, 1])))

    def test_invalid_distribution_is_rejected(self):
        """합이 1이 아닌 벡터를 확률 분포로 계산하지 않는다."""
        with self.assertRaises(ValueError):
            InformationTheory.entropy([.2, .2])

    def test_probability_sum_uses_absolute_tolerance(self):
        """확률 합의 상대 허용오차 때문에 1.000001을 수락하지 않는다."""
        with self.assertRaises(ValueError):
            InformationTheory.entropy([.5, .500001])


if __name__ == '__main__':
    unittest.main()
