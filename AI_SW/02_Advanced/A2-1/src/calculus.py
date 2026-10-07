"""중심차분으로 미분을 계산하고 등고선 위의 기울기를 표시한다."""

import numpy as np
import matplotlib.pyplot as plt


def central_difference(function, x, h=1e-5):
    """f'(x)≈[f(x+h)-f(x-h)]/(2h)를 계산한다."""
    return (function(x + h) - function(x - h)) / (2 * h)


def numerical_gradient(function, point, h=1e-5):
    """각 좌표만 ±h 바꾸어 스칼라 함수의 기울기 벡터를 계산한다."""
    point = np.asarray(point, dtype=float)
    gradient = np.zeros_like(point)
    for index in range(point.size):
        plus, minus = point.copy(), point.copy()
        plus[index] += h
        minus[index] -= h
        gradient[index] = (function(plus) - function(minus)) / (2 * h)
    return gradient


def plot_gradient():
    """f=x²+y² 등고선 위 여덟 점의 수치 기울기를 화살표로 그린다."""
    coordinates = np.linspace(-3, 3, 200)
    x, y = np.meshgrid(coordinates, coordinates)
    figure, axis = plt.subplots(figsize=(6, 6))
    contours = axis.contour(x, y, x ** 2 + y ** 2, levels=[1, 4, 9], colors='slategray')
    axis.clabel(contours)
    angles = np.arange(8) * np.pi / 4
    points = 2 * np.column_stack((np.cos(angles), np.sin(angles)))
    gradients = np.array([numerical_gradient(lambda p: np.sum(p ** 2), p) for p in points])
    axis.quiver(*points.T, *gradients.T, angles='xy', scale_units='xy', scale=5, color='C1')
    axis.scatter(*points.T, color='C1', s=15)
    axis.set(title='Gradient is normal to contours: f(x,y)=x²+y²', xlabel='x', ylabel='y')
    axis.set_aspect('equal')
    axis.grid(alpha=.25)
    figure.tight_layout()
    return figure
