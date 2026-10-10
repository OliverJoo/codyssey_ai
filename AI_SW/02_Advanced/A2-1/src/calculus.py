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


def derivative_sensitivity():
    """여러 h에서 x²(필수)와 sin(x)(O(h²) 관찰용)의 절대오차를 비교한다."""
    rows = []
    for name, function, x, analytic in [('x^2', lambda value: value ** 2, 3., 6.),
                                         ('sin(x)', np.sin, 1., float(np.cos(1.)))]:
        for h in [1e-1, 1e-2, 1e-3, 1e-5, 1e-7, 1e-9, 1e-11, 1e-13]:
            value = float(central_difference(function, x, h))
            error = abs(value - analytic)
            rows.append({'function': name, 'x': x, 'h': h, 'numeric': value,
                         'analytic': analytic, 'absolute_error': error,
                         'tolerance': 1e-4, 'passed': bool(error <= 1e-4)})
    return rows


def plot_derivative_sensitivity(rows):
    """h를 줄일 때 절단오차와 반올림오차의 서로 다른 효과를 그린다."""
    figure, axis = plt.subplots(figsize=(8, 4))
    for name in ['x^2', 'sin(x)']:
        selected = [row for row in rows if row['function'] == name]
        axis.loglog([row['h'] for row in selected],
                    [max(row['absolute_error'], 1e-18) for row in selected], 'o-', label=name)
    axis.axhline(1e-4, linestyle='--', color='slategray', label='Tolerance 1e-4')
    axis.set(xlabel='h (log scale)', ylabel='Absolute error (floor=1e-18 for plotting)',
             title='Central difference: truncation vs floating-point cancellation')
    axis.invert_xaxis()
    axis.grid(alpha=.3)
    axis.legend()
    figure.tight_layout()
    return figure


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
    arrows = axis.quiver(*points.T, *gradients.T, angles='xy', scale_units='xy', scale=5, color='C1')
    axis.scatter(*points.T, color='C1', s=15)
    axis.set(title='Gradient is normal to contours: f(x,y)=x²+y²\n'
                   'Eight points on f=4; arrows = gradient / 5', xlabel='x', ylabel='y')
    axis.set_aspect('equal')
    axis.grid(alpha=.25)
    figure.tight_layout(rect=(0, .12, 1, 1))
    axis.quiverkey(arrows, .5, .06, 4, '', coordinates='figure')
    # figure.text의 실제 영역을 포함해 bbox_inches='tight' 저장 시 하단 범례가 잘리지 않는다.
    figure.text(.5, .015, 'Gradient norm 4: drawn length 0.8 (=4/5)',
                ha='center', fontsize=9)
    return figure
