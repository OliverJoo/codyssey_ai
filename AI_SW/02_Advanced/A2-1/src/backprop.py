"""고정된 2→2→1 신경망의 순전파와 연쇄 법칙을 NumPy로 계산했다."""

import numpy as np


def fixed_example():
    """PDF 3쪽 입력값과 7쪽의 y_true=1을 새 배열로 반환한다."""
    return {'x': np.array([1., 0.]), 'W1': np.array([[.1, .2], [.3, .4]]),
            'b1': np.array([0., 0.]), 'W2': np.array([.5, .6]), 'b2': 0., 'y_true': 1.}


def sigmoid(value):
    """σ(z)=1/(1+exp(-z))를 고정 예제의 활성화 함수로 사용한다."""
    return 1 / (1 + np.exp(-np.asarray(value)))


def forward_backward(x, W1, b1, W2, b2, y_true):
    """순전파 중간값과 BCE의 여섯 필수 미분 및 편향 미분을 반환한다.

    열벡터 규약: W1(2,2) @ x(2,) -> z1(2,), W2(2,) @ a1(2,) -> z2().
    dL/dz2=ŷ-y, dW1=outer(dz1,x). 내부 계산은 반올림하지 않는다.
    """
    x, W1, b1, W2 = (np.asarray(value, dtype=float) for value in [x, W1, b1, W2])
    z1 = W1 @ x + b1
    a1 = sigmoid(z1)
    z2 = W2 @ a1 + b2
    y_pred = sigmoid(z2)
    loss = -(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
    dy_pred = -y_true / y_pred + (1 - y_true) / (1 - y_pred)
    dz2 = dy_pred * y_pred * (1 - y_pred)
    dW2 = dz2 * a1
    da1 = dz2 * W2
    dz1 = da1 * a1 * (1 - a1)
    dW1 = np.outer(dz1, x)
    values = {'z1': z1, 'a1': a1, 'z2': z2, 'y_pred': y_pred, 'loss': loss}
    gradients = {'dy_pred': dy_pred, 'dz2': dz2, 'dW2': dW2,
                 'da1': da1, 'dz1': dz1, 'dW1': dW1, 'db1': dz1.copy(), 'db2': dz2}
    return values, gradients
