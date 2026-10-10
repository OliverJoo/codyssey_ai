# A5-1: 대출을 해줘도 될지 판단하는 지도학습 시스템

이 폴더의 PDF 제공 코드로 생성한 **가상 고객 10,000명**에서 신용점수 회귀와 연체 분류를 구현했습니다. 5규칙 기준선, Train-only 대치·표준화 Pipeline, Ridge/Lasso, balanced Logistic, 5-fold GridSearchCV Random Forest를 동일한 고정 분할로 비교합니다. 외부 데이터와 딥러닝 프레임워크는 사용하지 않습니다.

실제 결과는 Train 8,000명/Test 2,000명, 연체율 12.01%, TDD 19개 통과입니다. Forest Test F1은 0.659686, Logistic AUC는 0.950457이며 모든 지표가 동시에 좋아지는 것은 아닙니다. 합성 생성 규칙을 예측한 결과이고 실제 은행 성능을 검증한 결과는 아닙니다.

## 1. PDF 요구사항과 구현 범위

| PDF 요구 | 실제 코드·결과 | 상태 |
|---|---|---|
| 제공 생성 코드 10,000행, 노이즈·불균형 보존 | [data_gen.py](data_gen.py), finance_data.csv 10,000×8 | 수행 |
| CSV Git 제외 | [.gitignore](.gitignore)의 `*.csv` | 수행 |
| 5개 이상 if 규칙·5지표·ML 비교 | [baseline.py](baseline.py), 아래 실제 비교표 | 수행 |
| Pipeline/ColumnTransformer, 수치 대치→스케일 | [workflow.py](workflow.py), Train/fold 내부 fit | 수행 |
| 범주형 인코딩 | 빈 categorical 목록의 OneHotEncoder 분기 | 원본은 수치형만 있어 실제 인코딩 미적용 |
| 8:2/seed 42/5-fold | [experiment.json](reports/experiment.json)의 고객 ID·CV 결과 | 수행 |
| Ridge/Lasso, alpha 5개, 계수 곡선, 회귀 2지표 이상 | RMSE/MAE/R² 전부, regularization.png | 수행 |
| 불균형 처리·혼동행렬·ROC/AUC | balanced weight, 실제 그림 두 종류 | 수행 |
| Random Forest + GridSearchCV | 100 trees, 4조합×5-fold | 수행 |
| 특징 중요도·3줄 해석(권장) | feature_importance.png와 아래 해석 | 수행 |
| 선택 CustomTransformer/모듈화/Learning Curve | [bonus.py](bonus.py), [bonus_experiment.py](bonus_experiment.py) | 별도 상속 파일로 수행 |
| git init/기능 단위 commit/Repository URL 제출 | 기존 상위 Git 사용, 중첩 init 없음 | A5-1 변경을 기능 단위 커밋으로 관리 |

원본에 없는 직업·성별 열을 추가하거나 카드 수를 명목형으로 바꾸지 않았습니다. 입력 6열을 그대로 보존하며 범주형 지원 분기가 있는 것과 실제 인코딩한 것을 구분합니다. PDF의 소득 주석은 음수 처리라고 되어 있지만 실제 코드는 `max(x,1500)`이므로 그 식을 유지했습니다.

## 2. 설치와 독립 실행

확인 환경은 Python 3.12.2(py312), NumPy 1.26.4, Pandas 2.3.3, scikit-learn 1.7.2, Matplotlib 3.10.1, pytest 8.4.1입니다. 패키지가 이미 있어 새 설치는 하지 않았습니다. [requirements.txt](requirements.txt)에 버전을 고정했습니다. pytest는 개발 검증 도구이고 모델 실행에는 PDF가 허용한 네 라이브러리만 사용합니다.

```bash
conda activate py312
cd /Users/oliverjoo/Dev/codyssey/2026/codyssey_missions/AI_SW/02_Advanced/A5-1
python data_gen.py
python -m pytest -q
python experiment.py
python bonus_experiment.py
python scripts/build_docs.py
python scripts/verify_artifacts.py
```

새 환경에는 `python -m pip install -r requirements.txt` 후 위 실행을 확인합니다. 기본·보너스·문서 빌더가 이 폴더 안에서 동작하며 다른 미션 모듈이나 데이터를 import하지 않습니다. CSV가 없으면 첫 실험에서 제공 코드로 생성합니다. 기존 CSV는 원본 재생성과 동치인지 검사하여 임의 수정된 데이터가 조용히 학습되지 않게 합니다.

새 고객 실행:

```bash
python main.py --customer '{"age":40,"annual_income":5000,"spending_score":50,"debt_ratio":0.4,"credit_card_count":3,"overdue_count_6m":1}'
```

위 실제 입력의 결과는 신용점수 359.558161, 연체 확률 0.098553입니다. [실제 CLI 로그](reports/cli_execution.txt)에 기록했습니다. 소득 단위는 만원, 부채비율은 0~1입니다. CLI는 실행마다 Train에서 Ridge alpha 1과 balanced Logistic을 fit합니다. `python main.py`는 전체 기본 실험을 실행합니다. PDF 세부 기능 밖의 배포 API·승인/거절/보류 정책 서비스는 추가하지 않았습니다.

## 3. 데이터와 누수 방지

- 입력: age, annual_income, spending_score, debt_ratio, credit_card_count, overdue_count_6m의 6개입니다.
- 정답: credit_score(0~1000 회귀), is_overdue(0/1 분류)이며 입력에서 모두 제외합니다.
- 전체 정상은 8,799명, 연체는 1,201명입니다. Train 양성=961, Test 양성=240입니다.
- CSV SHA-256은 `4ddf83dd154ee23bb2374a2bbc1aa56d537ef7ad5114c2f162078756542fe1a2`입니다.
- 외부 분할은 층화 8:2/seed 42이며 고객 ID 중복이 없습니다. 회귀 KFold와 분류 StratifiedKFold는 모두 5-fold/shuffle/seed 42입니다.
- 대치→표준화→모델을 Pipeline으로 묶어 CV 내부 Training 부분에서만 fit합니다. Test는 transform/predict만 합니다.
- alpha는 Train CV RMSE, Forest 설정은 Train CV F1으로 선택하며 Test 표로 설정을 바꾸지 않습니다.

표준화는 `z=(x−μtrain)/σtrain`입니다. 원본 결측은 없지만 요구된 median 대치 단계와 NaN 검증을 수행했습니다. Test 소득을 1e12로 바꿔 transform해도 Train 평균이 바뀌지 않음을 검사합니다. 원본 레이블의 하위 15% quantile은 PDF 합성 생성 규칙이며 학습 전처리의 Train-only 통계와 구분해서 보존합니다.

## 4. 규칙 기준선과 분류 성능

다섯 양성 규칙은 연체≥3, 부채>0.7, 소득<3000, 카드>7, 연체≥1이면서 부채>0.45입니다. 처음 만족한 조건에서 1을 반환하고 끝까지 해당하지 않으면 0입니다. 동일 Test 2,000명에서 측정했고 ML 임계값은 0.5로 고정했습니다.

| 모델 | Accuracy | Precision | Recall | F1 | AUC |
|---|---:|---:|---:|---:|---:|
| Rule baseline | 0.500000 | 0.188013 | 0.954167 | 0.314129 | 0.696117 |
| Balanced Logistic | 0.878500 | 0.496454 | 0.875000 | 0.633484 | 0.950457 |
| Tuned Random Forest | 0.902500 | 0.567568 | 0.787500 | 0.659686 | 0.941451 |


규칙은 1,218명을 경고하고 그중 989명이 오경고입니다. Recall은 높지만 Precision/F1은 낮습니다. Forest는 규칙보다 F1과 오경고 수를 개선하는 대신 미탐이 늘었습니다. Logistic은 Forest보다 AUC/Recall이 높고 Forest는 Accuracy/F1이 높으므로 한 모델이 모든 지표에서 우수하다고 설명하지 않습니다.

Test를 모두 정상이라 하면 Accuracy는 88%지만 양성 Recall/F1은 0입니다. Logistic Accuracy 87.85%가 그보다 조금 낮아도 연체 210/240명을 찾습니다. balanced weight는 Train 빈도에서 `n_train/(2×n_class)`로 계산하며 실제 가중치는 `{'0': 0.568262537292229, '1': 4.1623309053069715}`입니다. SMOTE는 선택 대안이고 이번에는 사용하지 않았습니다.

![동일 Test의 세 모델 혼동행렬](reports/confusion_matrix.png)

행=정답, 열=예측, 순서=[정상0,연체1]입니다. Logistic 행렬은 [[1547,213],[30,210]], Forest는 [[1616,144],[51,189]]입니다. 오경고 FP와 미탐 FN의 영향을 분리해서 읽습니다.

$$ Precision=TP/(TP+FP), Recall=TP/(TP+FN) $$

$$ F1=2×Precision×Recall/(Precision+Recall) $$

![ROC와 각 모델 AUC](reports/roc_auc.png)

규칙 AUC에는 확률이 아닌 0/1 flag를 사용합니다. 몇 개 점으로 된 거친 ROC이며 보정된 위험 확률이 아닙니다. ML AUC에는 predict_proba의 클래스 1 확률을 사용합니다.

## 5. 신용점수 회귀와 규제

| 모델 | alpha | Train CV RMSE | Test RMSE | Test MAE | Test R² |
|---|---:|---:|---:|---:|---:|
| ridge | 0.01 | 29.583826 | 30.125668 | 23.932708 | 0.861186 |
| ridge | 0.1 | 29.583825 | 30.125694 | 23.932715 | 0.861186 |
| ridge | 1 | 29.583817 | 30.125949 | 23.932791 | 0.861184 |
| ridge | 10 | 29.583939 | 30.128632 | 23.933551 | 0.861159 |
| ridge | 100 | 29.604678 | 30.167483 | 23.951167 | 0.860801 |
| lasso | 0.01 | 29.583138 | 30.125851 | 23.932360 | 0.861185 |
| lasso | 0.1 | 29.577382 | 30.128428 | 23.929690 | 0.861161 |
| lasso | 1 | 29.609044 | 30.220273 | 23.976942 | 0.860313 |
| lasso | 10 | 34.260590 | 35.236794 | 28.213907 | 0.810088 |
| lasso | 100 | 79.693475 | 80.873692 | 64.730244 | -0.000399 |


선택 alpha는 Ridge 1, Lasso 0.1입니다. alpha별 Test 값은 진단 자료이며 선택은 Train CV RMSE만으로 했습니다. Test 출력은 0~1000으로 clip하여 지표를 계산합니다. CV scoring은 raw 출력의 RMSE라는 차이를 명시합니다.

$$ RMSE=√(Σᵢ(yᵢ−ŷᵢ)²/n) $$

$$ R²=1−Σᵢ(yᵢ−ŷᵢ)²/Σᵢ(yᵢ−ȳ)² $$

![Ridge와 Lasso의 alpha별 실제 계수](reports/regularization.png)

표준화한 6입력의 계수입니다. sklearn Ridge는 RSS+alpha×L2, Lasso는 RSS/(2n)+alpha×L1이므로 같은 alpha를 같은 규제 힘으로 읽지 않습니다. 강한 Lasso alpha는 여러 계수를 0으로 만들지만 오차도 커집니다. RMSE 약 30점은 생성 노이즈 표준편차 30점과 함께 해석합니다.

## 6. 앙상블 최적화와 특징 중요도

Random Forest는 100 trees/balanced/seed 42/n_jobs 1입니다. depth [5,None]×leaf [1,5]의 4조합을 5-fold F1으로 탐색합니다. 파라미터당 2후보·총 4조합은 PDF 권장 제한 이내입니다. 최적 설정은 `{'model__max_depth': None, 'model__min_samples_leaf': 5}`, 최고 Train CV F1=0.673420입니다.

| max_depth | min_samples_leaf | Train CV F1 평균 | fold 표준편차 |
|---|---:|---:|---:|
| 5 | 1 | 0.624902 | 0.020828 |
| 5 | 5 | 0.627317 | 0.017312 |
| None | 1 | 0.570904 | 0.032421 |
| None | 5 | 0.673420 | 0.023872 |


![튜닝된 Forest의 특징 중요도](reports/feature_importance.png)

1. 연소득 중요도 0.491469가 가장 높고 최근 연체 0.225720·부채비율 0.168634가 뒤를 잇습니다.
2. 제공 점수 생성식이 이 세 변수를 사용하므로 합성 데이터 구조와 일관됩니다.
3. 불순도 감소 중요도는 모델이 사용한 정보를 요약하며 인과효과가 아닙니다. 카드 수의 작은 중요도를 현실에서 무의미하다고 일반화하지 않습니다.

## 7. 실제 고객 예측과 오류 해석

Test 고객 5911의 입력은 `{'age': 51.0, 'annual_income': 3559.0, 'spending_score': 52.0, 'debt_ratio': 0.84, 'credit_card_count': 1.0, 'overdue_count_6m': 0.0}`입니다. 실제 점수는 286, Ridge 예측은 322.192748, 실제 연체=1, Logistic 확률=0.467952입니다. 확률이 0.5보다 낮아 연체를 놓쳤습니다. 회귀 점수 오차와 분류 오류가 다른 형태로 발생하는 예입니다.

노이즈와 별도 레이블 난수가 있으며 모델은 6입력만 보므로 완벽한 분류를 기대할 수 없습니다. 합성 자료만으로 현실 오류의 원인을 확정하지 않습니다. 고객 번호는 합성 행 ID이며 실제 개인정보가 아닙니다.

## 8. 보너스: 상속·모듈화·학습곡선

[bonus.py](bonus.py)의 DerivedFeatures는 BaseEstimator/TransformerMixin을 상속해 카드당 소득과 부채×연체를 계산합니다. BonusWorkflow(FinanceWorkflow)는 전처리만 재정의하고 기본 회귀·분류·탐색을 상속합니다. 원본 CSV는 수정하지 않습니다. 보너스 Test F1=0.633484, AUC=0.950483입니다. F1이 기본 Logistic과 같아 뚜렷한 개선이라고 보고하지 않습니다.

기본과 보너스 모두 .py 모듈로 나눠 Notebook 상태에 의존하지 않습니다. 학습곡선은 보너스 Logistic을 원래 Train 내부 5-fold로 평가하며 외부 Test를 사용하지 않습니다.

| fold내Train 고객수 | Train F1 평균 | Validation F1 평균 | Validation std |
|---:|---:|---:|---:|
| 640 | 0.644748 | 0.645297 | 0.013097 |
| 1600 | 0.642543 | 0.647594 | 0.022662 |
| 3200 | 0.650381 | 0.643858 | 0.022176 |
| 4800 | 0.647547 | 0.647877 | 0.023536 |
| 6400 | 0.648427 | 0.646085 | 0.021681 |


![보너스의 Train/Validation 학습곡선](reports/learning_curve.png)

최대 크기의 Train F1=0.648427, Validation=0.646085로 차이가 작습니다. 크기를 늘려도 큰 개선이 관측되지 않고 약 0.64~0.65여서 표현·모델·노이즈 제약을 검토할 근거가 됩니다. 작은 차이만으로 모든 과대적합이 없다고 증명하지 않습니다. 음영은 fold 표준편차이며 신뢰구간이 아닙니다.

## 9. TDD·검증·설명 문서

미구현 stub에서 19개 테스트를 실행해 11 failed/8 errors를 기록했고 구현 후 19 passed가 되었습니다. [RED 로그](reports/tdd_red.txt), [GREEN 로그](reports/tdd_green.txt). 데이터 동치·범위, 5개 규칙 경계, 고정 층화 분할, Train-only 통계·결측 대치, 타겟 제외, alpha/clip/balanced/grid, 손계산 지표, 상속/clone/원본 무변경을 검증합니다.

- [README HTML](README.html): 이 보고서와 실제 그림·도식.
- [학습 MD](docs/code_walkthrough.md): 15개 개념·수식·현실 예시·실제 함수의 순차 설명.
- [학습 HTML](docs/code_walkthrough.html): 위 설명과 Python 전체 원문·줄번호 링크·SHA 내장.
- [기본 실측값](reports/experiment.json), [보너스 실측값](reports/bonus.json), [문서 생성 근거](reports/document_build.json), [최종 검증](reports/final_verification.json).

Markdown은 README와 학습 문서의 정확히 두 개이며 각각 HTML을 만들었습니다. diagram-design financial-services를 적용하고 코드 배경 #e7ebf0/글자 #14213d/줄번호 #475569/선택줄 #f4eddf를 사용합니다. flowchart 960×600, 실제 그림, 코드, MathML을 내장하여 외부 서버 없이 읽힙니다.

기존 상위 저장소는 `https://github.com/OliverJoo/codyssey_ai`, 미션 경로는 `AI_SW/02_Advanced/A5-1`입니다. A5-1 변경은 상위 저장소에서 기능 단위 커밋으로 관리합니다. Git에 CSV를 포함하지 않고 제공 생성기로 재현합니다.
