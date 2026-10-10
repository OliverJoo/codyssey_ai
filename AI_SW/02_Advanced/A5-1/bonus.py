"""선택 과제: BaseEstimator 파생변수와 기본 Workflow를 상속한 확장."""
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from workflow import FinanceWorkflow, FEATURES

class DerivedFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        """통계값을 학습하지 않는 변환기; sklearn clone/CV 계약을 따른다."""
        return self

    def transform(self, X):
        """원본 CSV를 수정하지 않고 두 입력 조합을 메모리에서 만든다."""
        frame = X[FEATURES].copy()
        frame["income_per_card"] = frame["annual_income"] / frame["credit_card_count"]
        frame["debt_overdue"] = frame["debt_ratio"] * frame["overdue_count_6m"]
        return frame

class BonusWorkflow(FinanceWorkflow):
    def preprocessor(self):
        """상속받은 classifier/regression/search의 전처리 지점만 확장한다."""
        columns = FEATURES + ["income_per_card", "debt_overdue"]
        numeric = Pipeline([("impute", SimpleImputer(strategy="median")),
                            ("scale", StandardScaler())])
        return Pipeline([("derive", DerivedFeatures()),
                         ("columns", ColumnTransformer([("numeric", numeric, columns)]))])
