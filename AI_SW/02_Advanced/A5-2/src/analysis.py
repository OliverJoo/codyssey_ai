"""원본 6개 입력으로 군집화하고 기존 Random Forest를 TreeSHAP로 해석한다."""
from pathlib import Path
import hashlib
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['age', 'annual_income', 'spending_score', 'debt_ratio', 'credit_card_count', 'overdue_count_6m']

class CustomerAnalysis:
    """데이터 경로와 모델 경로는 이 미션 내부에서만 해석한다."""
    def __init__(self, csv_path=None, model_path=None):
        self.csv_path = Path(csv_path or ROOT/'data/finance_data.csv')
        self.frame = pd.read_csv(self.csv_path)
        expected = FEATURES + ['credit_score', 'is_overdue']
        if list(self.frame.columns) != expected:
            raise ValueError('원본 CSV 컬럼 8개가 정확히 필요합니다.')
        if self.frame[FEATURES].isna().any().any():
            raise ValueError('원본 입력에 결측치가 있습니다.')
        self.features = self.frame[FEATURES].copy()
        self.model = joblib.load(model_path or ROOT/'models/random_forest.joblib')
        self.scaler = StandardScaler()
        self.labels = None
        self.pca_coordinates = None
        self.explainer = shap.TreeExplainer(self.model.named_steps['model'])

    def scaled(self):
        """소득 만원과 부채비율의 단위 차이를 제거한다."""
        return self.scaler.fit_transform(self.features)

    def cluster(self, candidates=range(2, 9)):
        values = self.scaled()
        metrics, models = [], {}
        for k in candidates:
            model = KMeans(n_clusters=k, random_state=42, n_init=10).fit(values)
            score = silhouette_score(values, model.labels_, sample_size=1500, random_state=42)
            metrics.append({'k': int(k), 'inertia': float(model.inertia_), 'silhouette': float(score)})
            models[k] = model
        chosen = max(metrics, key=lambda row: row['silhouette'])['k']
        self.labels = models[chosen].labels_
        pca = PCA(n_components=2)
        self.pca_coordinates = pca.fit_transform(values)
        clusters = []
        for label in range(chosen):
            mask = self.labels == label
            means = self.features.loc[mask].mean().to_dict()
            centroid = models[chosen].cluster_centers_[label]
            indices = np.flatnonzero(mask)
            representative = int(indices[np.argmin(np.linalg.norm(values[indices]-centroid, axis=1))])
            clusters.append({'cluster': label, 'count': int(mask.sum()), 'means': means, 'representative': representative})
        return {'chosen_k': chosen, 'candidates': metrics, 'silhouette_sample_size': 1500,
                'seed': 42, 'n_init': 10, 'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                'pca_loadings': pca.components_.tolist(), 'clusters': clusters,
                'shape': list(self.features.shape), 'csv_sha256': hashlib.sha256(self.csv_path.read_bytes()).hexdigest()}

    def transformed(self, frame):
        return self.model.named_steps['prepare'].transform(frame[FEATURES])

    def probabilities(self, frame):
        return self.model.predict_proba(frame[FEATURES])[:, 1]

    def explain(self, frame):
        """RF 다중 클래스 출력 중 is_overdue=1 확률의 기여도를 선택한다."""
        result = self.explainer(self.transformed(frame))
        return shap.Explanation(values=result.values[:, :, 1], base_values=result.base_values[:, 1],
                                data=frame[FEATURES].to_numpy(), feature_names=FEATURES)

    @staticmethod
    def decision(probability):
        if not 0 <= probability <= 1:
            raise ValueError('확률은 0 이상 1 이하여야 합니다.')
        return '거절' if probability >= .5 else '승인'
