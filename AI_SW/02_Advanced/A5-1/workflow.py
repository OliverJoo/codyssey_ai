"""Train에서만 fit하는 전처리·회귀·분류·앙상블의 공통 설정."""
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, Lasso, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, confusion_matrix, mean_absolute_error,
                             mean_squared_error, r2_score)

FEATURES = ["age", "annual_income", "spending_score", "debt_ratio", "credit_card_count", "overdue_count_6m"]
ALPHAS = [0.01, 0.1, 1, 10, 100]
RANDOM_STATE = 42

class FinanceWorkflow:
    def split(self, frame):
        """타겟 비율을 유지하며 고정 8:2 분할; DataFrame 원래 인덱스 보존."""
        return train_test_split(frame, test_size=0.2, random_state=RANDOM_STATE,
                                stratify=frame["is_overdue"])

    def preprocessor(self):
        """수치 6개를 median 대치→표준화; 원본에는 범주형 열이 없다."""
        numeric = Pipeline([("impute", SimpleImputer(strategy="median")),
                            ("scale", StandardScaler())])
        categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                ("encode", OneHotEncoder(handle_unknown="ignore"))])
        return ColumnTransformer([("numeric", numeric, FEATURES),
                                  ("categorical", categorical, [])], remainder="drop")

    def regression(self, model, alpha):
        """전처리까지 CV fold 내부에서 학습되도록 하나의 Pipeline으로 묶는다."""
        if model == "ridge":
            estimator = Ridge(alpha=alpha)
        elif model == "lasso":
            estimator = Lasso(alpha=alpha, max_iter=10000, random_state=RANDOM_STATE)
        else:
            raise ValueError("model must be ridge or lasso")
        return Pipeline([("prepare", self.preprocessor()), ("model", estimator)])

    def classifier(self):
        """불균형 보정은 Train 빈도로 계산하는 balanced class weight 사용."""
        return Pipeline([("prepare", self.preprocessor()),
                         ("model", LogisticRegression(class_weight="balanced",
                                                      max_iter=2000, random_state=RANDOM_STATE))])

    def ensemble_search(self):
        """작은 4조합·5-fold F1 탐색; 외부 Test는 탐색에서 사용하지 않는다."""
        forest = RandomForestClassifier(n_estimators=100, class_weight="balanced",
                                        random_state=RANDOM_STATE, n_jobs=1)
        pipeline = Pipeline([("prepare", self.preprocessor()), ("model", forest)])
        folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        return GridSearchCV(pipeline, {"model__max_depth": [5, None],
                                     "model__min_samples_leaf": [1, 5]},
                            scoring="f1", cv=folds, n_jobs=1, refit=True)

    def predict_credit(self, pipeline, frame):
        """요구한 0~1000 서비스 출력 범위로 예측만 제한한다."""
        return np.clip(pipeline.predict(frame), 0, 1000)

def classification_metrics(actual, predicted, scores):
    """1=연체 양성. AUC에는 ML 확률, 규칙의 경우 binary flag를 전달한다."""
    return dict(accuracy=float(accuracy_score(actual,predicted)),
                precision=float(precision_score(actual,predicted,zero_division=0)),
                recall=float(recall_score(actual,predicted,zero_division=0)),
                f1=float(f1_score(actual,predicted,zero_division=0)),
                auc=float(roc_auc_score(actual,scores)),
                confusion_matrix=confusion_matrix(actual,predicted,labels=[0,1]).tolist())

def regression_metrics(actual, predicted):
    """점수 단위의 RMSE/MAE와 무차원 R²를 반환한다."""
    return dict(rmse=float(np.sqrt(mean_squared_error(actual,predicted))),
                mae=float(mean_absolute_error(actual,predicted)),
                r2=float(r2_score(actual,predicted)))
