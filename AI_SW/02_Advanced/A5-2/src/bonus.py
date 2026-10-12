"""선택 과제: 기본 분석 클래스를 상속하는 군집 비교와 웹 입력 예측."""
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score, silhouette_score
from .analysis import CustomerAnalysis, FEATURES

class HierarchicalAnalysis(CustomerAnalysis):
    def compare(self, chosen_k):
        values = self.scaled()
        if self.labels is None:
            self.cluster([chosen_k])
        labels = AgglomerativeClustering(n_clusters=chosen_k, linkage='ward').fit_predict(values)
        return {'algorithm': 'Ward hierarchical', 'k': chosen_k,
                'silhouette': float(silhouette_score(values, labels, sample_size=1500, random_state=42)),
                'ari_vs_kmeans': float(adjusted_rand_score(self.labels, labels)),
                'counts': pd.Series(labels).value_counts().sort_index().to_dict()}

class DashboardAnalysis(CustomerAnalysis):
    def predict_customer(self, customer):
        frame = pd.DataFrame([customer], columns=FEATURES)
        probability = float(self.probabilities(frame)[0])
        explanation = self.explain(frame)
        return {'probability': probability, 'decision': self.decision(probability),
                'base': float(explanation.base_values[0]),
                'contributions': dict(zip(FEATURES, explanation.values[0].tolist()))}
