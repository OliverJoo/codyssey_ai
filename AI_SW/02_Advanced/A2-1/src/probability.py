"""정규/베르누이 분포와 Softmax를 계산한다. 정보 이론 보너스의 기본 클래스다."""

import numpy as np
import matplotlib.pyplot as plt


class ProbabilityLoss:
    """필수 확률 계산을 모아 보너스에서 상속할 수 있도록 했다."""

    @staticmethod
    def normal_pdf(x, mean=0., variance=1.):
        """N(μ,σ²)의 PDF; 두 번째 분포 매개변수는 표준편차가 아닌 분산이다."""
        if variance <= 0:
            raise ValueError('분산은 양수여야 한다.')
        return np.exp(-(np.asarray(x) - mean) ** 2 / (2 * variance)) / np.sqrt(2 * np.pi * variance)

    @staticmethod
    def bernoulli_pmf(x, p):
        """x=0,1에 대해 p^x*(1-p)^(1-x)를 반환한다."""
        x = np.asarray(x)
        return np.where((x == 0) | (x == 1), p ** x * (1 - p) ** (1 - x), 0.)

    @staticmethod
    def softmax(logits):
        """exp(z-max(z))/Σexp(z-max(z))로 1차원 로짓을 정규화한다."""
        shifted = np.asarray(logits, dtype=float) - np.max(logits)
        exponentials = np.exp(shifted)
        return exponentials / np.sum(exponentials)


def plot_normal_distributions():
    """N(0,1), N(2,.5)를 분산 규약에 따라 한 Figure에 그린다."""
    x = np.linspace(-4, 6, 500)
    figure, axis = plt.subplots(figsize=(8, 4))
    for mean, variance in [(0, 1), (2, .5)]:
        axis.plot(x, ProbabilityLoss.normal_pdf(x, mean, variance),
                  label=f'N(mean={mean}, variance={variance})')
    axis.set(xlabel='x', ylabel='Probability density', title='Normal PDF')
    axis.legend()
    axis.grid(alpha=.3)
    figure.tight_layout()
    return figure


def plot_bernoulli_distributions():
    """B(.3), B(.7)의 PMF를 나란한 막대로 한 Figure에 그린다."""
    x = np.array([0, 1])
    figure, axis = plt.subplots(figsize=(7, 4))
    for p, offset in [(.3, -.18), (.7, .18)]:
        axis.bar(x + offset, ProbabilityLoss.bernoulli_pmf(x, p), .36, label=f'B(p={p})')
    axis.set(xticks=x, xlabel='x', ylabel='Probability mass', ylim=(0, 1), title='Bernoulli PMF')
    axis.legend()
    figure.tight_layout()
    return figure
