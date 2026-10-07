"""필수 수학 실험의 PNG와 실제 수치 결과를 저장한다. --bonus는 선택 과제다."""

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR'] = str(ROOT / '.cache' / 'matplotlib')
sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.linear_algebra import (
    unit_circle, rotation_matrix, scaling_matrix, shear_matrix, transform_points,
    polygon_area, plot_transformations, power_iteration, svd_compress,
    svd_reconstruct, plot_svd_reconstructions,
)
from src.calculus import central_difference, numerical_gradient, plot_gradient
from src.backprop import fixed_example, forward_backward
from src.optimizer import (
    VanillaGD, Momentum, optimize, circle_loss, circle_gradient,
    ellipse_loss, ellipse_gradient, plot_paths, plot_loss_curves,
)
from src.probability import ProbabilityLoss, plot_normal_distributions, plot_bernoulli_distributions


def save_figure(figure, name):
    """시각화 결과를 outputs/의 PNG로 저장하고 Figure를 닫는다."""
    figure.savefig(ROOT / 'outputs' / name, dpi=150, bbox_inches='tight')
    plt.close(figure)


def convergence_summary(paths, loss_function, threshold=.01):
    """최종 좌표·손실·반경과 손실 기준 최초 도달 업데이트 수를 기록한다.

    최초 도달 뒤 다시 증가할 수 있으므로 영구 수렴의 판정은 아니다.
    """
    result = {}
    for label, history in paths.items():
        losses = loss_function(history)
        reached = np.flatnonzero(losses <= threshold)
        result[label] = {'final_point': history[-1].tolist(),
                         'final_loss': float(losses[-1]),
                         'final_radius': float(np.linalg.norm(history[-1])),
                         'first_update_loss_le_0.01': int(reached[0]) if len(reached) else None,
                         'updates': len(history) - 1}
    return result


def run_required():
    """PDF의 선형대수·미적분·최적화·확률 요구를 실행하고 기준을 확인한다."""
    np.random.seed(42)
    plt.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=['#14213d', '#a67c20', '#64748b', '#1d4ed8'])
    (ROOT / 'outputs').mkdir(exist_ok=True)
    (ROOT / 'reports').mkdir(exist_ok=True)
    image = np.load(ROOT / 'data' / 'image64.npy')
    assert image.ndim == 2 and max(image.shape) <= 64
    save_figure(plot_transformations(), 'matrix_transformations.png')
    points = unit_circle()
    area_results = {}
    for name, matrix in [('rotation', rotation_matrix(np.pi / 4)),
                         ('scaling', scaling_matrix(2, .5)), ('shear', shear_matrix(.8))]:
        determinant = float(np.linalg.det(matrix))
        ratio = polygon_area(transform_points(points, matrix)) / polygon_area(points)
        error_percent = abs(ratio - abs(determinant)) / abs(determinant) * 100
        assert error_percent <= 1
        area_results[name] = {'determinant': determinant, 'measured_area_ratio': ratio,
                              'relative_error_percent': error_percent}
    matrix = np.array([[4., 1.], [1., 3.]])
    value, vector, iterations = power_iteration(matrix)
    reference = float(np.linalg.eig(matrix)[0].max())  # 결과 비교 검증에만 사용했다.
    eigen_error = abs(value - reference) / abs(reference) * 100
    assert eigen_error <= 5
    save_figure(plot_svd_reconstructions(image), 'svd_reconstructions.png')
    svd_results = []
    for k in [10, 50, 100]:
        factors = svd_compress(image, k)
        effective_k = len(factors[1])
        svd_results.append({'requested_k': k, 'effective_k': effective_k,
                            'mse': float(np.mean((image - svd_reconstruct(*factors)) ** 2)),
                            'original_values': int(image.size),
                            'factor_values': int(effective_k * (sum(image.shape) + 1))})
    derivative = float(central_difference(lambda x: x ** 2, 3))
    assert abs(derivative - 6) <= 1e-4
    save_figure(plot_gradient(), 'gradient_contours.png')
    tangent_errors = []
    for point in np.array([[1., 2.], [-2., 1.], [2., -3.]]):
        gradient = numerical_gradient(circle_loss, point)
        tangent_errors.append(float(abs(gradient @ [-point[1], point[0]])))
    circle_paths = {name: optimize(optimizer, circle_gradient, steps=100)
                    for name, optimizer in [('GD lr=0.1', VanillaGD(.1)),
                                             ('Momentum lr=0.1 beta=0.9', Momentum(.1, .9))]}
    assert np.linalg.norm(circle_paths['GD lr=0.1'][-1]) <= .1
    save_figure(plot_paths(circle_loss, circle_paths, 'Circle: GD vs Momentum (100 updates)'), 'circle_paths.png')
    save_figure(plot_loss_curves(circle_loss, circle_paths, 'Circle convergence'), 'circle_loss.png')
    lr_paths = {f'GD lr={lr}': optimize(VanillaGD(lr), circle_gradient, steps=20)
                for lr in [.1, .5, 1., 1.1]}
    save_figure(plot_paths(circle_loss, lr_paths, 'Circle: learning-rate stability (20 updates)', extent=210),
                'learning_rate_paths.png')
    save_figure(plot_loss_curves(circle_loss, lr_paths, 'lr=0.5 reaches zero; lr=1.1 diverges'), 'learning_rate_loss.png')
    ellipse_paths = {name: optimize(optimizer, ellipse_gradient, steps=200)
                     for name, optimizer in [('GD lr=0.01', VanillaGD(.01)),
                                              ('Momentum lr=0.01 beta=0.9', Momentum(.01, .9))]}
    save_figure(plot_paths(ellipse_loss, ellipse_paths, 'Ellipse: GD vs Momentum (200 updates)'), 'ellipse_paths.png')
    save_figure(plot_loss_curves(ellipse_loss, ellipse_paths, 'Ellipse convergence'), 'ellipse_loss.png')
    save_figure(plot_normal_distributions(), 'normal_pdf.png')
    save_figure(plot_bernoulli_distributions(), 'bernoulli_pmf.png')
    probabilities = ProbabilityLoss.softmax([1000., 1001., 1002.])
    assert abs(probabilities.sum() - 1) <= 1e-6
    values, gradients = forward_backward(**fixed_example())
    metrics = {'seed': 42, 'image_shape': list(image.shape), 'area': area_results,
               'power_iteration': {'eigenvalue': value, 'eigenvector': vector.tolist(),
                                   'iterations': iterations, 'reference_eig': reference,
                                   'relative_error_percent': eigen_error},
               'svd': svd_results,
               'derivative': {'value': derivative, 'absolute_error': abs(derivative - 6)},
               'gradient_tangent_abs_dot': tangent_errors,
               'circle': convergence_summary(circle_paths, circle_loss),
               'learning_rates': convergence_summary(lr_paths, circle_loss),
               'ellipse': convergence_summary(ellipse_paths, ellipse_loss),
               'softmax': {'probabilities': probabilities.tolist(), 'sum': float(probabilities.sum())},
               'backprop': {group: {key: np.asarray(value).tolist() for key, value in data.items()}
                            for group, data in [('forward', values), ('backward', gradients)]}}
    (ROOT / 'reports' / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n', encoding='utf-8')
    return metrics


def run_bonus():
    """별도 상속 모듈의 Adam/Newton/정보 이론 결과를 필수 결과와 분리한다."""
    from src.bonus_optimizer import Adam, NewtonMethod
    from src.bonus_probability import InformationTheory

    np.random.seed(42)
    paths = {name: optimize(optimizer, ellipse_gradient, steps=2000)
             for name, optimizer in [('GD lr=0.01', VanillaGD(.01)),
                                      ('Momentum lr=0.01', Momentum(.01, .9)),
                                      ('Adam lr=0.01', Adam(.01))]}
    save_figure(plot_paths(ellipse_loss, {k: v[:201] for k, v in paths.items()},
                           'Bonus: first 200 updates, same lr=0.01'), 'bonus_adam_paths.png')
    save_figure(plot_loss_curves(ellipse_loss, paths, 'Bonus: GD / Momentum / Adam, same lr=0.01'),
                'bonus_adam_loss.png')
    newton_paths = {'GD lr=0.01': optimize(VanillaGD(.01), ellipse_gradient, steps=100),
                   'Newton': optimize(NewtonMethod(lambda point: np.diag([2., 20.])), ellipse_gradient, steps=100)}
    save_figure(plot_paths(ellipse_loss, newton_paths, 'Bonus: analytic Hessian Newton vs GD'), 'bonus_newton_paths.png')
    save_figure(plot_loss_curves(ellipse_loss, newton_paths, 'Bonus: Newton solves the quadratic in one update'),
                'bonus_newton_loss.png')
    p, q = [.3, .7], [.6, .4]
    metrics = {'adam_comparison': convergence_summary(paths, ellipse_loss),
               'newton_comparison': convergence_summary(newton_paths, ellipse_loss),
               'information_theory': {'p': p, 'q': q, 'unit': 'nats',
                                       'entropy': InformationTheory.entropy(p),
                                       'kl_divergence': InformationTheory.kl_divergence(p, q),
                                       'cross_entropy': InformationTheory.cross_entropy(p, q)}}
    (ROOT / 'reports' / 'bonus_metrics.json').write_text(json.dumps(metrics, indent=2) + '\n', encoding='utf-8')
    return metrics


if __name__ == '__main__':
    result = run_required()
    if '--bonus' in sys.argv:
        result['bonus'] = run_bonus()
    print(json.dumps(result, indent=2))
