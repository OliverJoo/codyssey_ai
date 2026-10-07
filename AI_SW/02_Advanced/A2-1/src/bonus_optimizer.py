"""선택 과제 Adam과 Newton을 기본 옵티마이저의 상속으로 분리했다."""

import numpy as np

from .optimizer import VanillaGD, Momentum


class Adam(Momentum):
    """1차 모멘트와 기울기 제곱의 2차 모멘트를 편향 보정하는 Adam."""

    def __init__(self, lr=.1, beta1=.9, beta2=.999, epsilon=1e-8):
        """Momentum의 학습률·velocity를 재사용하고 Adam 상태를 추가한다."""
        super().__init__(lr=lr, beta=beta1)
        self.beta2 = beta2
        self.epsilon = epsilon
        self.second_moment = None
        self.t = 0

    def step(self, point, gradient):
        """θ <- θ-lr*m_hat/(sqrt(v_hat)+ε); m에 (1-beta1)을 적용한다."""
        gradient = np.asarray(gradient)
        if self.velocity is None:
            self.velocity = np.zeros_like(gradient)
            self.second_moment = np.zeros_like(gradient)
        self.t += 1
        self.velocity = self.beta * self.velocity + (1 - self.beta) * gradient
        self.second_moment = self.beta2 * self.second_moment + (1 - self.beta2) * gradient ** 2
        m_hat = self.velocity / (1 - self.beta ** self.t)
        v_hat = self.second_moment / (1 - self.beta2 ** self.t)
        return np.asarray(point) - self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)


class NewtonMethod(VanillaGD):
    """해석적 Hessian을 사용해 θ <- θ-H^{-1}g를 계산한다."""

    def __init__(self, hessian_function):
        """기본 클래스의 인터페이스를 상속하고 Hessian 함수를 저장한다."""
        super().__init__(lr=1.)
        self.hessian_function = hessian_function

    def step(self, point, gradient):
        """역행렬을 직접 만들지 않고 H*delta=g를 풀어 좌표에서 뺀다."""
        hessian = self.hessian_function(point)
        delta = np.linalg.solve(hessian, gradient)
        return np.asarray(point) - self.lr * delta
