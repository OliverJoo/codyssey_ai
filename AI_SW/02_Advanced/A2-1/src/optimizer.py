"""경사하강법과 Momentum의 업데이트 및 등고선 경로를 구현했다."""

import numpy as np
import matplotlib.pyplot as plt


class VanillaGD:
    """θ_{t+1}=θ_t-lr*gradient인 기본 경사하강법."""

    def __init__(self, lr=.1):
        """학습률을 저장한다."""
        self.lr = lr

    def step(self, point, gradient):
        """한 번의 가중치 업데이트를 반환한다."""
        return np.asarray(point) - self.lr * np.asarray(gradient)


class Momentum(VanillaGD):
    """v_t=beta*v_{t-1}+g_t, θ_{t+1}=θ_t-lr*v_t인 Momentum."""

    def __init__(self, lr=.1, beta=.9):
        """기본 학습률을 상속하고 누적 기울기는 첫 호출에서 초기화한다."""
        super().__init__(lr)
        self.beta = beta
        self.velocity = None

    def step(self, point, gradient):
        """이전 속도와 현재 기울기를 합쳐 좌표를 이동한다."""
        gradient = np.asarray(gradient)
        if self.velocity is None:
            self.velocity = np.zeros_like(gradient)
        self.velocity = self.beta * self.velocity + gradient
        return np.asarray(point) - self.lr * self.velocity


def circle_loss(point):
    """f(x,y)=x²+y²; 마지막 축이 좌표인 여러 점도 함께 계산한다."""
    return np.sum(np.asarray(point) ** 2, axis=-1)


def circle_gradient(point):
    """∇f=(2x,2y)를 반환한다."""
    return 2 * np.asarray(point)


def ellipse_loss(point):
    """f(x,y)=x²+10y²를 반환한다."""
    point = np.asarray(point)
    return point[..., 0] ** 2 + 10 * point[..., 1] ** 2


def ellipse_gradient(point):
    """∇f=(2x,20y)를 반환한다."""
    return np.asarray(point) * np.array([2., 20.])


def optimize(optimizer, gradient_function, initial=(5, 5), steps=100):
    """초기점과 steps번 업데이트를 포함하는 (steps+1, 2) 경로를 반환한다.

    Momentum/Adam은 상태를 가지므로 독립 실험마다 새 인스턴스를 사용했다.
    """
    point = np.array(initial, dtype=float)
    history = [point.copy()]
    for _ in range(steps):
        point = optimizer.step(point, gradient_function(point))
        history.append(point.copy())
    return np.array(history)


def plot_paths(loss_function, paths, title, extent=6):
    """같은 등고선 위에 각 경로를 점선으로 겹쳐 그린다."""
    coordinates = np.linspace(-extent, extent, 250)
    x, y = np.meshgrid(coordinates, coordinates)
    points = np.stack((x, y), axis=-1)
    figure, axis = plt.subplots(figsize=(7, 6))
    axis.contour(x, y, loss_function(points), levels=20, colors='slategray', alpha=.5)
    for label, history in paths.items():
        axis.plot(*history.T, '--', linewidth=1.5, label=label)
        axis.scatter(*history[0], s=25)
        axis.scatter(*history[-1], marker='x', s=40)
    axis.set(title=title, xlabel='x', ylabel='y', xlim=(-extent, extent), ylim=(-extent, extent))
    axis.set_aspect('equal')
    axis.legend()
    figure.tight_layout()
    return figure


def plot_loss_curves(loss_function, paths, title):
    """수렴 속도를 비교하기 위해 업데이트 수 대비 손실을 로그 축으로 그린다."""
    figure, axis = plt.subplots(figsize=(8, 4))
    for label, history in paths.items():
        losses = np.maximum(loss_function(history), 1e-20)
        axis.semilogy(np.arange(len(history)), losses, label=label)
    axis.set(title=title, xlabel='Updates', ylabel='Loss (log scale, floor=1e-20)')
    axis.grid(alpha=.3)
    axis.legend()
    figure.tight_layout()
    return figure
