"""단위 원의 선형 변환, Power Iteration, SVD 이미지 복원을 구현했다."""

import numpy as np
import matplotlib.pyplot as plt


def unit_circle(count=100):
    """PDF의 theta=linspace(0, 2π, 100)으로 (count, 2) 좌표를 만든다."""
    theta = np.linspace(0, 2 * np.pi, count)
    return np.column_stack((np.cos(theta), np.sin(theta)))


def rotation_matrix(theta):
    """R(θ)=[[cosθ,-sinθ],[sinθ,cosθ]]를 반환한다. θ 단위는 라디안이다."""
    return np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]])


def scaling_matrix(sx, sy):
    """x, y축을 각각 sx, sy배 하는 대각 행렬을 반환한다."""
    return np.diag([float(sx), float(sy)])


def shear_matrix(k):
    """x'=x+k*y, y'=y인 수평 전단 행렬을 반환한다."""
    return np.array([[1., k], [0., 1.]])


def transform_points(points, matrix):
    """행으로 저장한 점에 p'=A*p를 적용한다: points @ matrix.T."""
    return np.asarray(points) @ np.asarray(matrix).T


def polygon_area(points):
    """신발끈 공식 |Σ(x_i*y_{i+1}-y_i*x_{i+1})|/2로 면적을 측정한다."""
    x, y = np.asarray(points).T
    return float(abs(np.sum(x * np.roll(y, -1) - y * np.roll(x, -1))) / 2)


def plot_transformations():
    """회전/스케일링/전단 각각의 변환 전후를 한 Figure에 겹쳐 표시한다."""
    points = unit_circle()
    matrices = [('Rotation 45 deg', rotation_matrix(np.pi / 4)),
                ('Scaling (2, 0.5)', scaling_matrix(2, .5)),
                ('Shear k=0.8', shear_matrix(.8))]
    figure, axes = plt.subplots(1, 3, figsize=(12, 4))
    for axis, (name, matrix) in zip(axes, matrices):
        transformed = transform_points(points, matrix)
        before_area = polygon_area(points)
        after_area = polygon_area(transformed)
        determinant = float(np.linalg.det(matrix))
        ratio = after_area / before_area
        error_percent = abs(ratio - abs(determinant)) / abs(determinant) * 100
        axis.plot(*points.T, '--', label='Before')
        axis.plot(*transformed.T, label='After')
        # 회전 전후 원의 윤곽이 겹치므로 첫 점의 반지름선도 표시했다.
        axis.plot([0, points[0, 0]], [0, points[0, 1]], '--', color='C0')
        axis.plot([0, transformed[0, 0]], [0, transformed[0, 1]], color='C1')
        axis.set_title(f'{name}\ndet={determinant:.3f}, area ratio={ratio:.3f}\n'
                       f'Area {before_area:.4f} -> {after_area:.4f}\n'
                       f'Error={error_percent:.2e}% <= 1%: '
                       f'{"PASS" if error_percent <= 1 else "FAIL"}', fontsize=10)
        axis.set_aspect('equal')
        axis.set(xlabel='x', ylabel='y', xlim=(-2.3, 2.3), ylim=(-2.3, 2.3))
        axis.grid(alpha=.3)
        axis.legend()
    figure.tight_layout()
    return figure


def power_iteration(matrix, tol=1e-6, max_iterations=1000):
    """절댓값이 가장 큰 고유값을 구한다. 실험은 양의 대칭 행렬을 사용했다.

    v <- A*v/||A*v||, λ <- v.T*A*v로 갱신하고 잔차 ||A*v-λ*v||로 종료한다.
    반환값은 (고유값, 단위 고유벡터, 반복 횟수)이다.
    """
    matrix = np.asarray(matrix, dtype=float)
    vector = np.ones(matrix.shape[0])
    vector /= np.linalg.norm(vector)
    for iteration in range(1, max_iterations + 1):
        product = matrix @ vector
        norm = np.linalg.norm(product)
        if norm == 0:
            raise ValueError('초기 벡터가 영벡터로 변환되어 정규화할 수 없다.')
        vector = product / norm
        value = float(vector @ matrix @ vector)
        if np.linalg.norm(matrix @ vector - value * vector) <= tol:
            return value, vector, iteration
    raise RuntimeError('지정한 반복 횟수 내에 Power Iteration이 수렴하지 않았다.')


def svd_compress(image, k):
    """상위 min(k, 행 수, 열 수)개의 SVD 인자 U_k, s_k, Vt_k를 반환한다."""
    if k < 1:
        raise ValueError('k는 1 이상이어야 한다.')
    u, singular_values, vt = np.linalg.svd(np.asarray(image), full_matrices=False)
    effective_k = min(k, len(singular_values))
    return u[:, :effective_k], singular_values[:effective_k], vt[:effective_k, :]


def svd_reconstruct(u, singular_values, vt):
    """A_k=U_k*diag(s_k)*Vt_k를 복원한다. 열별 곱으로 대각 행렬을 생략했다."""
    return (u * singular_values) @ vt


def plot_svd_reconstructions(image, ranks=(10, 50, 100)):
    """원본과 요청 k=10/50/100의 복원 및 실제 성분 수를 한 Figure에 표시한다."""
    figure, axes = plt.subplots(1, len(ranks) + 1, figsize=(13, 4))
    axes[0].imshow(image, cmap='gray', vmin=0, vmax=1)
    axes[0].set_title(f'Original {image.shape[0]} x {image.shape[1]}')
    for axis, k in zip(axes[1:], ranks):
        factors = svd_compress(image, k)
        reconstructed = svd_reconstruct(*factors)
        mse = np.mean((image - reconstructed) ** 2)
        axis.imshow(reconstructed, cmap='gray', vmin=0, vmax=1)
        effective_k = len(factors[1])
        storage_ratio = effective_k * (sum(image.shape) + 1) / image.size
        axis.set_title(f'Requested k={k}, effective k={effective_k}\n'
                       f'MSE={mse:.3e}\nFactor/original values={storage_ratio:.3f}', fontsize=10)
    for axis in axes:
        axis.axis('off')
    figure.tight_layout()
    return figure
