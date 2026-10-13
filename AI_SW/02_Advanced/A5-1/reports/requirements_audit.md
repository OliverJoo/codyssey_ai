# A5-1 · PDF 필수 요구사항 재검토

2026-10-13에 9쪽 PDF, 실제 코드와 저장된 실험 결과, CLI와 테스트를 재검토했다. 이 폴더 데이터·결과만으로 판단했다.

| PDF 위치 | 필수 내용 | 실제 근거 | 판정 |
|---|---|---|---|
| 1–2쪽 | 규칙/ML 비교, 6입력 신용점수 회귀, 연체 확률 | [실험](../experiment.py), [고객 CLI](../main.py), [전체 실측값](experiment.json), [README 비교표](../README.md) | 구현·실행 |
| 2쪽 | README, 버전 명세 | [README](../README.md), [requirements.txt](../requirements.txt) | 존재 |
| 3쪽 | 제공 생성기, 10,000행, 노이즈·불균형 보존, CSV 제외 | [data_gen.py](../data_gen.py), 정확한 재생성 동치 테스트, [.gitignore](../.gitignore) | 수행 |
| 3쪽 | 5개 이상 if 규칙, Accuracy/Precision/Recall/F1 및 비교 | [5규칙](../baseline.py), 실험 JSON classification, README 4절의 AUC 포함 5지표 | 수행 |
| 3쪽 | Pipeline/ColumnTransformer, 수치 대치→스케일, Train-only fit | [workflow.py](../workflow.py), 고정 8:2/42, Train 내부 5-fold | 수행 |
| 3쪽 | 범주형 인코딩 | OneHotEncoder 분기 구현; 제공 6입력이 모두 수치이므로 적용할 범주형 열 없음 | 해당 데이터에서는 미적용 |
| 3쪽 | Ridge/Lasso alpha=.01/.1/1/10/100, 계수 그림, 회귀 2지표 이상 | [규제 곡선](regularization.png), 실험 JSON regression, RMSE/MAE/R² 모두 | 수행 |
| 3쪽 | class_weight balanced 또는 SMOTE, 혼동행렬·ROC/AUC | balanced Logistic/RF, [혼동행렬](confusion_matrix.png), [ROC](roc_auc.png) | 수행 |
| 3–4쪽 | RF 또는 XGBoost + GridSearchCV | RF 4조합×5-fold, 최고 Train CV F1=.673420 | 수행 |
| 4쪽 | 특징 중요도·해석(권장) | [그림](feature_importance.png), README 6절 3문장 | 수행 |
| 4–8쪽 | 제공 난수/타겟 생성 코드, 외부 데이터·DL 금지 | 원본 재생성 SHA-256 일치, sklearn/Pandas/NumPy/Matplotlib 사용 | 준수 |
| 5–6쪽 | 보너스 Custom Transformer·모듈화·학습곡선 | [별도 상속](../bonus.py), [학습곡선](learning_curve.png) | 필수와 분리 |
| 8–9쪽 | 형상관리·GitHub URL, 예시 지표 | 기존 상위 Git에서 기능 단위 관리; 예시 수치를 실측으로 복사하지 않음 | 게시·URL 제출은 별도 |

제공 코드가 수치형 6개만 생성하므로 직업·성별 등 열을 임의로 추가해 인코딩 실적을 만들지 않았다. 숫자인 카드 수를 명목 범주로 바꾸지 않고 제공 데이터 정의를 보존했다. 이는 인코딩 코드 부재와는 다르다.

py312에서 `python -m pytest tests -q` 재실행 **19개 통과**. 원본 동치, 규칙 경계, Train-only 통계, 타겟 제외, alpha/출력 clip, balanced·grid, 손계산 지표를 확인했다. RF Test F1=.659686, Logistic AUC=.950457이며 모든 지표 동시 개선으로 과장하지 않았다. 재검토 때문에 원본 데이터나 모델을 임의 수정·재학습하지 않았다.
