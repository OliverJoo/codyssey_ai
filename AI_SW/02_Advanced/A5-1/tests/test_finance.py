import numpy as np
import pandas as pd
import pytest
from sklearn.base import clone, BaseEstimator
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from data_gen import generate_data
from baseline import RuleBaseline
from workflow import FEATURES, ALPHAS, FinanceWorkflow, classification_metrics, regression_metrics
from bonus import DerivedFeatures, BonusWorkflow

@pytest.fixture(scope="module")
def data():
    return generate_data()

def test_generator_exact_shape_and_targets(data):
    assert data.shape == (10000, 8)
    assert list(data.columns) == FEATURES + ["credit_score", "is_overdue"]
    assert data.credit_score.between(0,1000).all()
    assert set(data.is_overdue) == {0,1}
    assert 0.10 < data.is_overdue.mean() < 0.15
    assert data.annual_income.min() == 1500

def test_generator_reproducible(data):
    pd.testing.assert_frame_equal(data,generate_data())

def test_generator_file(tmp_path,data):
    p=tmp_path/"finance_data.csv"
    generate_data(p)
    pd.testing.assert_frame_equal(data,pd.read_csv(p))

@pytest.mark.parametrize("change",[
    {"overdue_count_6m":3}, {"debt_ratio":.71}, {"annual_income":2999},
    {"credit_card_count":8}, {"overdue_count_6m":1,"debt_ratio":.46}])
def test_each_positive_rule(change):
    normal=dict(age=40,annual_income=6000,spending_score=30,debt_ratio=.2,credit_card_count=2,overdue_count_6m=0)
    normal.update(change)
    assert RuleBaseline().predict(pd.DataFrame([normal])).tolist() == [1]

def test_rule_negative_and_boundaries():
    normal=dict(age=40,annual_income=3000,spending_score=30,debt_ratio=.7,credit_card_count=7,overdue_count_6m=0)
    assert RuleBaseline().predict(pd.DataFrame([normal])).tolist() == [0]

def test_stratified_reproducible_split(data):
    work=FinanceWorkflow()
    a,b=work.split(data)
    a2,b2=work.split(data)
    assert len(a)==8000 and len(b)==2000
    assert set(a.index).isdisjoint(b.index)
    assert list(a.index)==list(a2.index) and list(b.index)==list(b2.index)
    assert abs(a.is_overdue.mean()-b.is_overdue.mean()) < .001

def test_train_only_fit_and_imputation(data):
    processor=FinanceWorkflow().preprocessor()
    train=data[FEATURES].iloc[:100].copy()
    train.loc[train.index[0],"annual_income"]=np.nan
    processor.fit(train)
    numeric=processor.named_transformers_["numeric"]
    assert isinstance(numeric.named_steps["impute"],SimpleImputer)
    imputed=numeric.named_steps["impute"].transform(train)
    np.testing.assert_allclose(numeric.named_steps["scale"].mean_,imputed.mean(axis=0))
    original=numeric.named_steps["scale"].mean_.copy()
    test=data[FEATURES].iloc[100:102].copy();test["annual_income"]=1e12
    assert np.isfinite(processor.transform(test)).all()
    np.testing.assert_array_equal(numeric.named_steps["scale"].mean_,original)
    cat=dict((name,(transformer,cols)) for name,transformer,cols in processor.transformers)["categorical"]
    assert isinstance(cat[0].named_steps["encode"], OneHotEncoder) and cat[1]==[]

def test_targets_excluded_and_regression(data):
    work=FinanceWorkflow();model=work.regression("ridge",1)
    assert isinstance(model,Pipeline)
    model.fit(data[FEATURES].iloc[:200],data.credit_score.iloc[:200])
    columns=model.named_steps["prepare"].transformers_[0][2]
    assert columns == FEATURES
    assert "credit_score" not in columns and "is_overdue" not in columns
    assert len(model.named_steps["model"].coef_)==6

@pytest.mark.parametrize("method",["ridge","lasso"])
def test_alpha_and_regressor(method):
    model=FinanceWorkflow().regression(method,100)
    assert model.named_steps["model"].alpha==100
    assert ALPHAS==[.01,.1,1,10,100]

def test_credit_range():
    class Fake:
        def predict(self,x):return np.array([-10,500,1100])
    np.testing.assert_array_equal(FinanceWorkflow().predict_credit(Fake(),pd.DataFrame([{}, {}, {}])),[0,500,1000])

def test_class_weight_and_small_grid():
    work=FinanceWorkflow()
    assert work.classifier().named_steps["model"].class_weight=="balanced"
    search=work.ensemble_search()
    assert search.cv.n_splits==5 and search.cv.random_state==42
    assert search.estimator.named_steps["model"].class_weight=="balanced"
    assert np.prod([len(x) for x in search.param_grid.values()])<=100

def test_handcomputed_metrics():
    m=classification_metrics([0,0,1,1],[0,1,0,1],[.1,.8,.2,.9])
    assert m["accuracy"]==.5 and m["precision"]==.5 and m["recall"]==.5 and m["f1"]==.5
    assert m["auc"]==.75 and m["confusion_matrix"]==[[1,1],[1,1]]
    r=regression_metrics([10,20],[12,18])
    assert r["rmse"]==2 and r["mae"]==2 and r["r2"]==pytest.approx(.84)

def test_bonus_transformer_clone_and_no_mutation(data):
    t=DerivedFeatures();clone(t)
    x=data[FEATURES].iloc[:5].copy();original=x.copy()
    out=t.fit_transform(x)
    pd.testing.assert_frame_equal(x,original)
    np.testing.assert_allclose(out["income_per_card"],x.annual_income/x.credit_card_count)
    np.testing.assert_allclose(out["debt_overdue"],x.debt_ratio*x.overdue_count_6m)
    assert isinstance(t,BaseEstimator)

def test_bonus_inherits_and_pipeline(data):
    assert issubclass(BonusWorkflow,FinanceWorkflow)
    p=BonusWorkflow().preprocessor()
    x=p.fit_transform(data[FEATURES].iloc[:10])
    assert x.shape==(10,8)
