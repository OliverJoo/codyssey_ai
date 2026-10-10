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
from src.calculus import (central_difference, numerical_gradient, plot_gradient,
                          derivative_sensitivity, plot_derivative_sensitivity)
from src.backprop import fixed_example, forward_backward
from src.optimizer import (
    VanillaGD, Momentum, optimize, circle_loss, circle_gradient,
    ellipse_loss, ellipse_gradient, plot_paths, plot_loss_curves,
)
from src.probability import ProbabilityLoss, plot_normal_distributions, plot_bernoulli_distributions
from scripts.assessment import (compare_power_iteration, compare_hand_calculation, circle_stability,
                                verify_softmax_cases, verify_loss_likelihood)


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
        radii = np.linalg.norm(history, axis=1)
        sustained = np.flatnonzero(np.maximum.accumulate(losses[::-1])[::-1] <= threshold)
        result[label] = {'final_point': history[-1].tolist(),
                         'final_loss': float(losses[-1]),
                         'final_radius': float(np.linalg.norm(history[-1])),
                         'first_update_loss_le_0.01': int(reached[0]) if len(reached) else None,
                         'first_sustained_update_loss_le_0.01': int(sustained[0]) if len(sustained) else None,
                         'radius_threshold_pdf': .1,
                         'within_pdf_radius_0.1': bool(radii[-1] <= .1),
                         'within_review_radius_1': bool(radii[-1] <= 1),
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
        area_results[name] = {'parameters': matrix.tolist(), 'determinant': determinant,
                              'points_shape': list(points.shape), 'sample_count': len(points),
                              'distinct_vertices': len(points) - 1,
                              'before_area': polygon_area(points),
                              'after_area': polygon_area(transform_points(points, matrix)),
                              'measured_area_ratio': ratio, 'relative_error_percent': error_percent,
                              'tolerance_percent': 1., 'passed': bool(error_percent <= 1)}
    matrix = np.array([[4., 1.], [1., 3.]])
    value, vector, iterations = power_iteration(matrix)
    eigen_comparison = compare_power_iteration(matrix, value, vector)
    assert eigen_comparison['passed'] and eigen_comparison['vector_passed'] and eigen_comparison['residual_passed']
    save_figure(plot_svd_reconstructions(image), 'svd_reconstructions.png')
    svd_results = []
    for k in [10, 50, 100]:
        factors = svd_compress(image, k)
        effective_k = len(factors[1])
        reconstruction = svd_reconstruct(*factors)
        svd_results.append({'requested_k': k, 'effective_k': effective_k,
                            'image_shape': list(image.shape),
                            'mse': float(np.mean((image - svd_reconstruct(*factors)) ** 2)),
                            'max_absolute_pixel_error': float(np.max(np.abs(image - reconstruction))),
                            'rank_cap': min(image.shape),
                            'factor_to_original_ratio': float(effective_k * (sum(image.shape) + 1) / image.size),
                            'original_values': int(image.size),
                            'factor_values': int(effective_k * (sum(image.shape) + 1))})
    derivative = float(central_difference(lambda x: x ** 2, 3))
    assert abs(derivative - 6) <= 1e-4
    sensitivity = derivative_sensitivity()
    save_figure(plot_derivative_sensitivity(sensitivity), 'derivative_sensitivity.png')
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
    ellipse_lr_paths = {f'GD lr={lr}': optimize(VanillaGD(lr), ellipse_gradient, steps=20)
                        for lr in [.01, .1, .5, .7]}
    save_figure(plot_loss_curves(ellipse_loss, ellipse_lr_paths,
                               'Ellipse: lr=0.5 / 0.7 diverge (y factor -9 / -13)'),
                'ellipse_learning_rate_loss.png')
    save_figure(plot_normal_distributions(), 'normal_pdf.png')
    save_figure(plot_bernoulli_distributions(), 'bernoulli_pmf.png')
    probabilities = ProbabilityLoss.softmax([1000., 1001., 1002.])
    assert abs(probabilities.sum() - 1) <= 1e-6
    values, gradients = forward_backward(**fixed_example())
    hand_comparison = compare_hand_calculation(values, gradients)
    assert hand_comparison['passed']
    softmax_cases = verify_softmax_cases()
    likelihood_checks = verify_loss_likelihood()
    assert all(row['passed'] for row in softmax_cases) and likelihood_checks['passed']
    (ROOT / 'reports' / 'loss_likelihood_checks.json').write_text(
        json.dumps(likelihood_checks, indent=2) + '\n', encoding='utf-8')
    distribution_results = {'normal': [], 'bernoulli': []}
    grid = np.linspace(-10, 10, 20001)
    for mean, variance in [(0, 1), (2, .5)]:
        integral = float(np.trapz(ProbabilityLoss.normal_pdf(grid, mean, variance), grid))
        distribution_results['normal'].append({'mean': mean, 'variance': variance,
                                                'standard_deviation': float(np.sqrt(variance)),
                                                'integral': integral, 'passed': bool(abs(integral - 1) <= 1e-6)})
    for p in [.3, .7]:
        pmf = ProbabilityLoss.bernoulli_pmf([0, 1], p)
        distribution_results['bernoulli'].append({'p': p, 'pmf': pmf.tolist(),
                                                   'sum': float(pmf.sum()), 'passed': bool(abs(pmf.sum() - 1) <= 1e-6)})
    lr_checks = [circle_stability(lr, lr_paths[f'GD lr={lr}']) for lr in [.1, .5, 1., 1.1]]
    assert all(item['matches_recurrence'] for item in lr_checks)
    metrics = {'seed': 42, 'image_shape': list(image.shape), 'area': area_results,
               'reproducibility': {'initial_point': [5., 5.], 'seed': 42,
                                   'deterministic_gradient': True, 'fresh_optimizer_per_run': True,
                                   'initial_velocity': [0., 0.], 'circle_steps': 100,
                                   'learning_rate_steps': 20, 'ellipse_steps': 200,
                                   'ellipse_lr_for_both': .01, 'momentum_beta': .9},
               'power_iteration': {'eigenvalue': value, 'eigenvector': vector.tolist(),
                                   'matrix': matrix.tolist(), 'matrix_shape': list(matrix.shape),
                                   'iterations': iterations, **eigen_comparison},
               'svd': svd_results,
               'derivative': {'value': derivative, 'analytic_value': 6., 'h': 1e-5,
                              'absolute_error': abs(derivative - 6), 'tolerance': 1e-4,
                              'passed': bool(abs(derivative - 6) <= 1e-4)},
               'gradient_tangent_abs_dot': tangent_errors,
               'derivative_sensitivity': sensitivity,
               'gradient_visualization': {'points_shape': [8, 2], 'contour_levels': [1, 4, 9],
                                          'gradient_norm_on_radius_2': 4., 'quiver_scale': 5.,
                                          'displayed_arrow_length': .8},
               'circle': convergence_summary(circle_paths, circle_loss),
               'learning_rates': convergence_summary(lr_paths, circle_loss),
               'learning_rate_stability': lr_checks,
               'ellipse': convergence_summary(ellipse_paths, ellipse_loss),
               'ellipse_learning_rates': convergence_summary(ellipse_lr_paths, ellipse_loss),
               'ellipse_stability': {'gd_stable_lr_range': [0., .1], 'endpoints_excluded': True,
                                     'y_factor_at_lr_0.5': -9.,
                                     'loss_increases_at_lr_0.5': bool(np.all(np.diff(ellipse_loss(ellipse_lr_paths['GD lr=0.5'])) > 0))},
               'distributions': distribution_results,
               'softmax_cases': softmax_cases, 'loss_likelihood_checks': likelihood_checks,
               'softmax': {'logits': [1000., 1001., 1002.], 'probabilities': probabilities.tolist(),
                           'sum': float(probabilities.sum()), 'absolute_sum_error': float(abs(probabilities.sum() - 1)),
                           'tolerance': 1e-6, 'passed': bool(abs(probabilities.sum() - 1) <= 1e-6)},
               'backprop_comparison': hand_comparison,
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
