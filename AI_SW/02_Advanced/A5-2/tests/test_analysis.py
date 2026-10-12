import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.analysis import CustomerAnalysis, FEATURES
from src.bonus import HierarchicalAnalysis, DashboardAnalysis

ROOT = Path(__file__).resolve().parents[1]

def test_exact_data_and_target_exclusion():
    assert hashlib.sha256((ROOT/'data/finance_data.csv').read_bytes()).hexdigest() == '4ddf83dd154ee23bb2374a2bbc1aa56d537ef7ad5114c2f162078756542fe1a2'
    analysis = CustomerAnalysis()
    assert analysis.features.shape == (10000, 6)
    assert 'credit_score' not in FEATURES and 'is_overdue' not in FEATURES

def test_standardized_input():
    analysis = CustomerAnalysis()
    values = analysis.scaled()
    np.testing.assert_allclose(values.mean(axis=0), 0, atol=1e-12)
    np.testing.assert_allclose(values.std(axis=0), 1, atol=1e-12)

def test_choose_k_and_pca_variance():
    analysis = CustomerAnalysis()
    result = analysis.cluster(range(2, 5))
    assert result['chosen_k'] == max(result['candidates'], key=lambda row: row['silhouette'])['k']
    assert sum(result['explained_variance_ratio']) <= 1
    assert sum(row['count'] for row in result['clusters']) == 10000

def test_shap_additivity_and_decision():
    analysis = CustomerAnalysis()
    sample = analysis.features.iloc[[0,1,2]]
    explanation = analysis.explain(sample)
    probabilities = analysis.probabilities(sample)
    np.testing.assert_allclose(explanation.base_values + explanation.values.sum(axis=1), probabilities, atol=1e-7)
    assert analysis.decision(0.5) == '거절'
    assert analysis.decision(0.499) == '승인'
    with pytest.raises(ValueError): analysis.decision(5)

def test_bonus_inheritance_and_predictions():
    assert issubclass(HierarchicalAnalysis, CustomerAnalysis)
    assert issubclass(DashboardAnalysis, CustomerAnalysis)
    analysis = DashboardAnalysis()
    result = analysis.predict_customer(dict(age=35, annual_income=5000, spending_score=50, debt_ratio=.3, credit_card_count=3, overdue_count_6m=0))
    assert 0 <= result['probability'] <= 1
    assert abs(result['base'] + sum(result['contributions'].values()) - result['probability']) < 1e-7
