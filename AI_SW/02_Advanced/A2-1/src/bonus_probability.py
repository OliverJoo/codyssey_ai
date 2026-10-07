"""ProbabilityLoss를 상속해 엔트로피, KL, Cross-Entropy를 직접 구현했다."""

import numpy as np

from .probability import ProbabilityLoss


class InformationTheory(ProbabilityLoss):
    """자연로그 단위 nats의 이산 정보 이론 계산."""

    @staticmethod
    def _distribution(values):
        """음이 아닌 유한 값의 1차원 확률 벡터인지 확인한다."""
        values = np.asarray(values, dtype=float)
        if (values.ndim != 1 or not np.isfinite(values).all()
                or np.any(values < 0) or not np.isclose(values.sum(), 1, rtol=0, atol=1e-10)):
            raise ValueError('확률 벡터는 음이 아닌 유한 값이며 합이 1이어야 한다.')
        return values

    @classmethod
    def entropy(cls, p):
        """H(p)=-Σp*log(p); p=0 항은 극한에 따라 0으로 제외한다."""
        p = cls._distribution(p)
        positive = p > 0
        return float(-np.sum(p[positive] * np.log(p[positive])))

    @classmethod
    def cross_entropy(cls, p, q):
        """H(p,q)=-Σp*log(q); p>0이고 q=0인 항이 있으면 +∞다."""
        p, q = cls._distribution(p), cls._distribution(q)
        if p.shape != q.shape:
            raise ValueError('두 분포의 shape이 같아야 한다.')
        positive = p > 0
        if np.any(q[positive] == 0):
            return float('inf')
        return float(-np.sum(p[positive] * np.log(q[positive])))

    @classmethod
    def kl_divergence(cls, p, q):
        """D_KL(p||q)=Σp*log(p/q); 영확률은 Cross-Entropy와 같은 규약이다."""
        p, q = cls._distribution(p), cls._distribution(q)
        if p.shape != q.shape:
            raise ValueError('두 분포의 shape이 같아야 한다.')
        positive = p > 0
        if np.any(q[positive] == 0):
            return float('inf')
        return float(np.sum(p[positive] * np.log(p[positive] / q[positive])))
