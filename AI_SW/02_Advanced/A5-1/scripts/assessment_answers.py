"""A5-1.png의 16개 질문에 실제 코드·기존 실측값으로 답하는 HTML 부록."""
import hashlib
from html import escape
from pathlib import Path

import html_tools

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {1: "항목 1 · 구현과 산출물 확인", 2: "항목 2 · 구조와 데이터 흐름", 3: "항목 3 · 원리와 실험 해석", 4: "항목 4 · 서비스 관점의 판단"}
QUESTIONS = [
    "data_gen.py를 실행하여 finance_data.csv(10,000건)가 정상 생성되는가?",
    "규칙 기반 베이스라인이 5개 이상의 if-else 규칙으로 구현되어 있고, ML 모델과 성능 비교표(Accuracy, F1-Score, AUC)가 정량적으로 제시되어 있는가?",
    "Scikit-learn의 Pipeline 또는 ColumnTransformer로 전처리가 모듈화되어 있고, fit/predict 실행 시 에러 없이 동작하는가?",
    "불균형 처리(class_weight='balanced' 또는 SMOTE) 적용 후, 분류 모델의 Confusion Matrix와 ROC-AUC 곡선이 시각화되어 있는가?",
    "Ridge/Lasso 모델에 Alpha 값 변화(0.01~100)에 따른 계수 변화 그래프가 있고, RMSE/MAE/R² 중 2개 이상이 산출되어 있는가?",
    "앙상블 모델(Random Forest 또는 HistGradientBoosting)이 GridSearchCV로 튜닝되어 있고, 단일 모델 대비 성능 향상이 수치로 입증되어 있는가?",
    "README.md에 프로젝트 개요, 실행 방법, 성능 비교 리포트가 포함되어 있고, requirements.txt가 존재하는가?",
    "전처리→학습→평가 흐름을 어떤 구조로 분리했는지 설명해 주세요. 각 모듈/셀/함수의 역할과 흐름을 코드를 보며 설명할 수 있는가?",
    "데이터 누수(Data Leakage) 방지를 위해 전처리 기준(fit)을 어디서 수행했는지, 해당 코드를 직접 가리키며 설명할 수 있는가?",
    "회귀 모델과 분류 모델을 동시에 다루는 구조에서, 공통 전처리와 개별 모델링을 어떻게 설계했는지 설명할 수 있는가?",
    "이 문제에서 Accuracy 대신 F1-Score와 AUC를 평가지표로 선택한 이유는 무엇이며, 불균형 데이터에서 Accuracy가 왜 부적절한지 구체적인 수치로 설명할 수 있는가?",
    "규제(Ridge/Lasso)가 모델의 복잡도를 어떻게 제어하는지, Alpha 값 변화에 따른 계수 변화 그래프를 근거로 설명할 수 있는가? L1과 L2의 차이를 이 데이터셋 결과에서 어떻게 확인했는가?",
    "앙상블 기법(Random Forest/Boosting)이 단일 모델의 편향이나 분산을 줄이는 원리는 무엇이며, 실제 성능 결과에서 이 효과를 어떻게 확인했는가?",
    "불균형 데이터를 처리할 때 SMOTE나 class_weight를 선택한 이유는 무엇이며, 해당 방법을 Test Set에는 적용하지 않아야 하는 이유를 설명할 수 있는가?",
    "실제 서비스라면 모델의 성능(정확도)과 예측 속도 중 무엇을 더 우선시하겠는가?",
    "이 모델이 실제 은행에 배포된다면, 오탐(정상인데 연체로 예측)과 미탐(연체인데 정상으로 예측) 중 어떤 것이 더 심각한가? 금융 의사결정 관점에서 임계값(threshold)을 어떻게 조정하겠는가?",
]


def table(headers, rows):
    """가로 스크롤 가능한 표에 실제 수치와 교육용 예시를 구분해서 담는다."""
    body = '<tr>'+''.join('<th>'+escape(str(cell))+'</th>' for cell in headers)+'</tr>'
    body += ''.join('<tr>'+''.join('<td>'+escape(str(cell))+'</td>' for cell in row)+'</tr>' for row in rows)
    return '<div class="table-scroll"><table>'+body+'</table></div>'


def render_answers(result, bonus, locate):
    """기존 문서의 마지막에 붙일 질문·답변과 동적으로 찾은 코드 근거를 만든다."""
    references = []
    facts = result['classification']
    rule, logistic, forest = [facts[name] for name in ['Rule baseline', 'Balanced Logistic', 'Tuned Random Forest']]
    train_positive = result['split']['train_positive']
    train_size, test_size = result['split']['train_size'], result['split']['test_size']
    normal_test = test_size-result['split']['test_positive']
    curve = bonus['learning_curve']

    def p(text):
        return '<p>'+html_tools.inline(text)+'</p>'

    def steps(texts):
        return '<ol>'+''.join('<li>'+html_tools.inline(text)+'</li>' for text in texts)+'</ol>'

    def file_link(file, label=None):
        return '<a href="../'+escape(file, quote=True)+'">'+escape(label or file)+'</a>'

    def proof(file, symbol, needle=None, limit=10):
        line, source = locate(file, symbol)
        lines = source.splitlines()
        offset = next((i for i, text in enumerate(lines) if needle in text), None) if needle else 0
        if offset is None:
            raise ValueError(f'없는 코드 근거: {file}: {needle}')
        line += offset
        snippet = '\n'.join(lines[offset:offset+limit])
        references.append(dict(file=file, symbol=symbol, line=line, snippet=snippet,
                               sha256=hashlib.sha256((ROOT/file).read_bytes()).hexdigest()))
        identifier = html_tools.anchor(file, line)
        link = f'<a class="qa-code-link" href="#{identifier}">{escape(file)} · {escape(symbol)} · L{line}</a>'
        return p('아래는 실제 파일의 일부입니다. 링크를 누르면 이 HTML에 내장한 전체 코드의 해당 줄로 이동합니다.')+link+'<pre><code>'+escape(snippet)+'</code></pre>'

    def metric_table():
        return table(['모델', 'Accuracy', 'Precision', 'Recall', 'F1', 'AUC'],
                     [[name]+[f'{row[key]:.6f}' for key in ['accuracy', 'precision', 'recall', 'f1', 'auc']]
                      for name, row in facts.items()])

    def matrix_table():
        rows = []
        for name, row in facts.items():
            (tn, fp), (fn, tp) = row['confusion_matrix']
            rows.append([name, tn, fp, fn, tp])
        return table(['모델', 'TN 정상→정상', 'FP 정상→연체', 'FN 연체→정상', 'TP 연체→연체'], rows)

    def regression_table():
        rows = []
        for name, model in result['regression'].items():
            for row in model['rows']:
                rows.append([name, row['alpha'], f'{row["cv_rmse"]:.6f}', f'{row["rmse"]:.6f}',
                             f'{row["mae"]:.6f}', f'{row["r2"]:.6f}', sum(abs(v)<1e-12 for v in row['coefficients'])])
        return table(['모델', 'alpha', 'Train CV RMSE', 'Test RMSE', 'Test MAE', 'Test R²', '0인 계수 수'], rows)

    rows = []
    def answer(number, group, lead, explanation, example, nodes, evidence, extra='', formula=None, limit=''):
        """이미지의 질문 순서를 유지하며 답변과 근거를 바로 이어 붙인다."""
        rows.append(dict(number=number, group=group, question=QUESTIONS[number-1], lead=lead,
                         explanation=explanation, example=example, nodes=nodes, evidence=evidence,
                         extra=extra, formula=formula, limit=limit))

    answer(1, 1, '예. PDF 제공 생성식을 구현했고, 실제 CSV의 shape은 (10,000, 8)입니다.',
        ['한 행은 가상 고객 한 명입니다. 입력은 나이·소득·소비점수·부채비율·카드 수·최근 연체 횟수의 6개이고, 정답은 신용점수와 연체 여부의 2개입니다. 8개 열 전체를 모델 입력으로 넣지는 않습니다.',
         f'generate_data()가 seed=42로 난수 호출 순서를 고정합니다. 신용점수는 노이즈를 포함해 계산하고 0~1000으로 제한합니다. 점수 하위 15% 조건과 별도 난수로 연체 레이블을 만들며, 실제 연체율은 {100*result["data"]["positive_rate"]:.2f}%입니다.',
         '파일이 없으면 experiment.py가 생성합니다. 기존 파일이 있으면 generate_data() 결과와 assert_frame_equal로 대조하고 학습하므로 수정된 CSV가 조용히 사용되는 것을 막습니다.'],
        ['교육용 고객의 소득이 5,000만원, 연체 횟수 1, 부채비율 0.4라면 노이즈 전 점수는 300+150−50−40=360점입니다.',
         '여기에 생성 난수가 더해져 정답 점수가 정해집니다. 모델은 이 난수 자체를 입력으로 받지 않으므로 같은 특징만으로 완벽한 예측을 기대할 수 없습니다.',
         '평가자는 `python data_gen.py`의 10,000건 출력과 CSV를 확인하고 테스트의 생성·재현성 검사를 따라갈 수 있습니다. 고객 수 10,000과 열 수 8을 함께 확인합니다.'],
        [('입력 6개 생성', 'seed=42 / 10,000 rows'), ('노이즈와 정답 2개', 'credit_score / is_overdue'), ('CSV 저장·원본 대조', 'shape=(10000, 8)')],
        [('data_gen.py', 'generate_data', 'np.random.seed', 10), ('experiment.py', 'run_experiment', 'pd.testing.assert_frame_equal', 7)],
        extra=p('근거 파일: ')+file_link('finance_data.csv')+' · '+file_link('reports/experiment.json')+' · '+file_link('reports/final_verification.json')+p('원본 CSV SHA-256: `'+result['data']['sha256']+'`'),
        formula='credit_score=clip(300+0.03×income−50×overdue_count−100×debt_ratio+noise,0,1000)',
        limit='실제 고객 데이터가 아니라 PDF가 지정한 합성 자료입니다. .gitignore의 *.csv 규칙으로 데이터 파일은 Git에서 제외하고 생성기로 재현합니다.')

    answer(2, 1, '예. 학습하지 않는 양성 규칙 5개와 정상 else를 구현했고 동일 Test 2,000명에서 ML과 비교했습니다.',
        ['규칙은 연체 횟수≥3, 부채비율>0.7, 소득<3000, 카드 수>7, 연체 횟수≥1이면서 부채비율>0.45입니다. predict_row는 위에서 아래로 검사하고 처음 만족하는 조건에서 1을 반환합니다.',
         '규칙은 사람이 정한 조건입니다. Logistic과 Forest는 Train의 입력·정답을 이용해 가중치나 분기 구조를 학습합니다. 테스트 고객과 정답을 동일하게 유지해야 차이를 공정하게 비교할 수 있습니다.',
         f'규칙 F1={rule["f1"]:.6f}에 비해 Logistic={logistic["f1"]:.6f}, Forest={forest["f1"]:.6f}입니다. 규칙은 연체를 많이 찾지만 오경고가 989건이라 Precision이 낮습니다.'],
        ['교육용 고객의 연체 1회·부채비율0.46이면 앞의 조건이 모두 거짓이어도 다섯 번째 규칙으로 경고1이 됩니다.',
         '부채비율을0.45로 바꾸고 다른 조건도 해당하지 않으면 >0.45가 거짓이므로 정상0입니다. 규칙의 경계와 비교 연산자를 확인하는 예입니다.',
         '규칙이 잘 찾는 것뿐 아니라 정상 고객에게 불필요한 경고를 얼마나 주는지도 실제 비교표의 Precision·FP로 확인합니다.'],
        [('고객 입력 6개', 'same Test / 2,000 customers'), ('규칙 또는 학습 모델', '5 rules / Logistic / Forest'), ('같은 정답으로 비교', 'Accuracy / F1 / AUC')],
        [('baseline.py', 'RuleBaseline.predict_row', None, 15), ('experiment.py', 'run_experiment', 'rule = RuleBaseline', 7)],
        extra=metric_table()+p('수치 원본: ')+file_link('reports/experiment.json'),
        limit='규칙의 AUC는 0/1 경고 플래그로 계산한 거친 순위 지표입니다. ML predict_proba와 같은 연속 확률 출력으로 해석하지 않습니다.')

    answer(3, 1, '예. ColumnTransformer가 열별 처리를, Pipeline이 전처리→모델 연결을 담당합니다.',
        ['SimpleImputer(strategy="median")가 수치 결측치를 처리하고 StandardScaler가 Train 평균·표준편차로 표준화합니다. 모델 Pipeline에는 prepare와 model 두 단계가 있습니다.',
         'Pipeline.fit은 입력으로 전처리 통계를 학습한 뒤 변환된 배열로 모델을 학습합니다. Pipeline.predict는 이미 학습한 전처리로 입력을 변환하고 모델 예측을 반환합니다. 호출할 때마다 전처리를 따로 맞출 필요가 줄어듭니다.',
         '원본 6열은 모두 수치형입니다. OneHotEncoder가 있는 categorical 분기는 열 목록이 비어 실제 변환에 참여하지 않습니다. 분기 존재와 실제 범주형 인코딩 적용을 구분합니다.'],
        ['교육용 Train 소득 [3000,5000,7000]의 평균은5000입니다. 결측 소득에는 중앙값5000을 대치합니다.',
         '새 고객 소득6000은 기존 Train 통계로 z=(6000−5000)/σtrain을 계산합니다. 새 고객 때문에 평균을6000 쪽으로 다시 fit하지 않습니다.',
         '실제 테스트는 Test 소득을1e12로 바꾸어 transform해도 Train 평균이 그대로인지 검사하고, Pipeline 학습과 6개 계수 생성을 확인합니다.'],
        [('수치 열 선택·대치', 'ColumnTransformer / median'), ('Train 기준 표준화', 'StandardScaler fit / transform'), ('모델 학습·예측', 'Pipeline prepare → model')],
        [('workflow.py', 'FinanceWorkflow.preprocessor', None, 11), ('tests/test_finance.py', 'test_train_only_fit_and_imputation', 'original=', 5)],
        extra=p('19개 테스트 통과 기록: ')+file_link('reports/tdd_green.txt')+' · '+file_link('reports/final_verification.json'),
        formula='z=(x−μTrain)/σTrain',
        limit='코드는 원본과 명시적으로 검증한 결측·새 입력 사례에서 동작합니다. 모든 종류의 잘못된 입력을 자동 교정하는 범용 서비스는 아닙니다.')

    answer(4, 1, '예. Logistic과 Random Forest에 balanced class weight를 적용했고 실제 혼동행렬과 ROC 그림을 저장했습니다.',
        [f'Train {train_size:,}명 중 연체는 {train_positive}명입니다. balanced는 드문 연체 레이블의 학습 손실 비중을 높이는 방식이며 데이터를 복제하거나 합성하지 않습니다.',
         'experiment.py는 클래스1 확률을 구하고 0.5 이상을 연체로 예측합니다. 혼동행렬은 행=정답, 열=예측이고 레이블 순서는 정상0·연체1입니다. ROC는 임계값에 따른 정상 오경고율과 연체 탐지율을 보여 줍니다.',
         f'Logistic AUC={logistic["auc"]:.6f}, Forest AUC={forest["auc"]:.6f}입니다. ROC/AUC에는 이진 predict 결과 대신 predict_proba의 연체 점수를 넣습니다.'],
        ['Logistic이 연체라고 경고한 423명 중 실제 연체는210명, 정상은213명입니다. Precision=210/423≈49.65%입니다.',
         '실제 연체240명 중210명을 찾았으므로 Recall=210/240=87.5%입니다. 찾지 못한30명은 FN입니다.',
         '평가자는 confusion_matrix.png에서 이 네 칸을 보고 roc_auc.png의 곡선·AUC를 확인합니다. 행렬과 곡선은 서로 다른 성능 관점을 보여 줍니다.'],
        [('Train 불균형 반영', 'class_weight=balanced'), ('Test 연체 확률 계산', 'predict_proba / threshold=0.5'), ('행렬과 ROC 저장', 'confusion_matrix.png / roc_auc.png')],
        [('workflow.py', 'FinanceWorkflow.classifier', None, 7), ('experiment.py', 'run_experiment', 'probability = model.predict_proba', 6)],
        extra=matrix_table()+p('실제 시각화: ')+file_link('reports/confusion_matrix.png')+' · '+file_link('reports/roc_auc.png'),
        formula='weight(c)=nTrain/(2×nTrain,c)',
        limit='SMOTE를 실행하지 않았으며 클래스 가중치만 사용했습니다. weighted 학습 뒤 확률이 실제 은행의 연체율에 맞게 보정됐다는 검증은 없습니다.')

    answer(5, 1, '예. Ridge와 Lasso 모두 alpha 0.01·0.1·1·10·100을 실험하고 RMSE·MAE·R² 세 지표를 기록했습니다.',
        ['규제는 너무 큰 계수를 억제해 학습 자료의 작은 흔들림까지 과하게 따라가는 것을 줄입니다. regularization.png는 표준화한 입력 6개 계수의 변화를 두 모델별로 보여 줍니다.',
         f'선택 alpha는 Train 내부 5-fold 평균 RMSE 기준으로 Ridge={result["regression"]["ridge"]["selected_alpha"]}, Lasso={result["regression"]["lasso"]["selected_alpha"]}입니다. Test 값이 더 좋은 설정으로 선택을 바꾸지 않습니다.',
         'RMSE와 MAE의 단위는 신용점수의 점이고 R²는 무차원입니다. CV RMSE는 raw 출력으로 계산하며 Test 예측은 PDF 출력 범위에 맞춰 0~1000으로 제한한 후 평가합니다.'],
        ['교육용 두 고객에서 실제 점수 [400,500], 예측 [390,520]이면 오차는 [−10,20]입니다.',
         'MAE=(10+20)/2=15점, RMSE=√((100+400)/2)≈15.811점입니다. RMSE는 큰 오차를 더 강하게 반영합니다.',
         '이 예시 숫자를 실측으로 사용하지 않습니다. 실제 선택 Ridge는 RMSE30.125949·MAE23.932791·R²0.861184이고, 생성 노이즈 표준편차30점과 함께 읽습니다.'],
        [('같은 Train 전처리', '6 standardized inputs'), ('두 모델·alpha 5개', 'Train CV RMSE / 5 folds'), ('계수·Test 3지표', 'PNG + experiment.json')],
        [('workflow.py', 'FinanceWorkflow.regression', None, 12), ('experiment.py', 'run_experiment', 'cv = -cross_val_score', 10)],
        extra=regression_table()+p('계수 그래프: ')+file_link('reports/regularization.png'),
        formula='MAE=Σ|y−ŷ|/n ; RMSE=√(Σ(y−ŷ)²/n) ; R²=1−RSS/TSS',
        limit='RMSE가 작아졌다는 사실만으로 현실 고객의 신용 평가가 정확하다고 결론 내리지 않습니다. 이 값은 합성 정답을 고정 Test에서 예측한 결과입니다.')

    f1_pp=100*(forest['f1']-logistic['f1'])
    accuracy_pp=100*(forest['accuracy']-logistic['accuracy'])
    answer(6, 1, 'Random Forest를 GridSearchCV로 튜닝했고 단일 Logistic 대비 F1·Accuracy 향상을 확인했습니다. AUC·Recall은 더 낮습니다.',
        ['100개 나무, balanced, seed42를 고정합니다. max_depth=[5,None]와 min_samples_leaf=[1,5]의 4조합을 Train 내부 StratifiedKFold 5-fold에서 F1으로 비교합니다. 총20회 후보-fold 학습 후 최선의 Pipeline을 Train 전체에 다시 fit합니다.',
         f'최적 설정은 max_depth=None·min_samples_leaf=5이고 최고 Train CV F1={result["grid_search"]["best_cv_f1"]:.6f}입니다. best_estimator_로 외부 Test를 평가합니다.',
         f'단일 Logistic 대비 Forest Accuracy는 {accuracy_pp:.2f}%p, F1은 {f1_pp:.2f}%p 증가했습니다. 그러나 Recall은 0.875→0.7875, AUC는 0.950457→0.941451로 감소했습니다. 향상한 지표를 정확히 지정합니다.'],
        ['은행의 검토 인력이 제한된 가상 상황에서 FP가213→144로69건 줄면 불필요한 검토가 감소합니다.',
         '동시에 FN이30→51로21건 늘어 연체를 놓치는 비용이 증가할 수 있습니다. F1이 더 좋아도 업무 비용에서 더 좋은지는 별도 판단입니다.',
         '평가자는 아래 비교표와 grid_search.candidates를 대조합니다. 실제 구현은 Random Forest이며 질문의 선택 대안 HistGradientBoosting은 구현하지 않았습니다.'],
        [('4개 Forest 후보', 'depth × min_samples_leaf'), ('Train 5-fold F1 선택', 'GridSearchCV / best_estimator_'), ('Logistic과 Test 비교', 'F1 ↑ / Recall and AUC ↓')],
        [('workflow.py', 'FinanceWorkflow.ensemble_search', None, 14), ('experiment.py', 'run_experiment', 'search = workflow.ensemble_search', 7)],
        extra=metric_table()+table(['설정', 'Train CV F1', 'fold 표준편차'],
             [[str(c['params']), f'{c["mean_f1"]:.6f}', f'{c["std_f1"]:.6f}'] for c in result['grid_search']['candidates']]),
        limit='미튜닝 Forest와 튜닝 Forest의 별도 Test 비교는 저장하지 않았습니다. GridSearch 후보 차이는 Train CV에서, 단일 Logistic 대비 개선은 고정 Test에서 확인한 서로 다른 근거입니다.')

    answer(7, 1, '예. README.md와 requirements.txt가 존재하고 개요·실행·성능 비교를 담았습니다.',
        ['README 1절은 PDF 범위, 2절은 설치·CLI, 3절은 데이터·누수 방지, 4~6절은 분류·회귀·앙상블 실측, 7~9절은 고객 사례·보너스·TDD를 설명합니다.',
         'requirements.txt는 NumPy·Pandas·scikit-learn·Matplotlib·pytest의 확인 버전을 명시합니다. 이 HTML에는 개념과 실제 Python 원문, 줄 번호 이동을 함께 담았습니다.',
         '평가 자료는 코드만 있는지보다 실행 순서, 데이터 재현, 실측 표, 실패와 한계가 함께 있는지를 확인할 수 있도록 구성했습니다.'],
        ['평가자가 폴더를 처음 열면 README 설치 명령과 generate_data 실행부터 확인합니다. 이어 pytest→experiment→bonus_experiment 순서로 동작을 확인합니다.',
         'reports/experiment.json의 숫자를 README 표와 대조하고 그림 링크를 눌러 결과를 확인합니다.',
         '라이브러리 버전은 requirements.txt, 테스트 기록은 RED/GREEN 로그, 원문 일치는 HTML의 SHA와 코드 줄 링크로 확인합니다.'],
        [('설치·실행 안내', 'README.md / requirements.txt'), ('실측 결과 확인', 'reports JSON / PNG / logs'), ('개념·코드 설명', 'code_walkthrough.html')],
        [('tests/test_finance.py', 'test_generator_file', None, 5)],
        extra=p('문서: ')+file_link('README.md')+' · '+file_link('README.html')+' · '+file_link('requirements.txt')+p('실제 requirements.txt 원문:')+'<pre><code>'+escape((ROOT/'requirements.txt').read_text())+'</code></pre>',
        limit='Repository URL 제출을 위한 새 commit/push는 별도 작업입니다. 문서가 존재한다는 사실과 저장소 게시 완료를 같은 상태로 표시하지 않습니다.')

    answer(8, 2, '전처리와 모델 구성은 workflow.py, 실험 실행·평가는 experiment.py, 새 고객 입력은 main.py로 나눴습니다.',
        ['data_gen.py는 데이터만 생성하고 baseline.py는 규칙 예측을 담당합니다. FinanceWorkflow는 분할·전처리·회귀·분류·탐색을 구성하며, 평가 함수는 예측과 정답에서 지표를 계산합니다.',
         'run_experiment는 CSV 확인→8:2 분할→Train CV 설정 선택→fit→Test predict→지표·그림·JSON 저장 순서입니다. 각 모델을 만들 때 새 전처리 인스턴스를 생성합니다.',
         'main.py --customer는 정확히 6개 입력을 받아 Train에서 Ridge와 Logistic을 fit한 뒤 신용점수와 연체 확률을 출력합니다. Notebook 셀 실행 순서나 다른 미션 모듈에 의존하지 않습니다.'],
        ['처음 학습할 때는 고객 이력 표를 data_gen에서 준비하고 workflow에서 처리 규칙과 모델 구조를 정합니다.',
         'experiment는 이 구성을 실제 데이터로 학습·평가해 보고서를 만듭니다. 보고서를 읽는 역할과 모델을 구성하는 역할이 함수로 분리됩니다.',
         '신규 고객 [나이40·소득5000·소비50·부채0.4·카드3·연체1]을 main에 넣은 실제 기록은 점수359.558161·연체확률0.098553입니다. 예제 CLI 로그에서 동일 결과를 확인할 수 있습니다.'],
        [('생성·분할', 'data_gen + FinanceWorkflow.split'), ('전처리·학습', 'workflow + experiment'), ('평가·새 고객 출력', 'metrics / reports / main')],
        [('experiment.py', 'run_experiment', 'workflow = FinanceWorkflow', 9), ('main.py', 'main', 'ridge=work.regression', 6)],
        extra=table(['파일', '역할'],[['data_gen.py','원본 합성 자료 생성'],['baseline.py','5규칙 예측'],['workflow.py','전처리·모델·CV 구조'],['experiment.py','실측 실행·지표·그림'],['main.py','새 고객 CLI'],['tests/test_finance.py','계약·경계·누수 검사']])+p('실제 CLI 실행: ')+file_link('reports/cli_execution.txt'),
        limit='CLI는 고객 요청마다 fit하므로 서비스 배포용 추론 구조와 다릅니다. 이를 이미 학습 모델을 불러오는 운영 API라고 설명하지 않습니다.')

    answer(9, 2, '외부 Test를 먼저 분리하고, 대치·스케일러를 모델과 함께 Pipeline 내부에서 fit했습니다.',
        ['workflow.split이 Train 8,000·Test 2,000을 고정합니다. 이후 xtrain과 xtest를 6개 feature로만 구성하며 두 target은 전처리 입력에서 제외합니다.',
         'CV에 전체 Pipeline을 전달하므로 각 fold의 내부 Training 부분으로 중앙값·평균·표준편차와 모델을 학습합니다. 내부 Validation은 transform·predict만 합니다. CV 이전에 전체 Train을 미리 fit_transform하는 방식이 아닙니다.',
         'alpha와 Forest 설정은 Train CV로 선택합니다. 마지막으로 선택 모델이 Train 전체를 fit하고 Test를 예측합니다. Test 지표가 낮다는 이유로 그 표를 보고 설정을 다시 고르지 않습니다.'],
        ['교육용 Train 소득 [3000,5000,7000]의 평균5000으로 변환한다고 가정합니다. Test의10억 수준 이상치를 포함해 평균을 먼저 구하면 평가 대상의 정보를 배운 상태가 됩니다.',
         '실제 test_train_only_fit_and_imputation은 Test 소득을1e12로 바꾸고 transform한 뒤 scaler.mean_가 원래 값과 같은지 확인합니다.',
         '평가자는 model.fit(xtrain, ...)와 GridSearchCV(Pipeline, ...)를 직접 가리키며 fit 범위를 설명하고, transform에는 새로운 평균 학습이 없음을 보여 줄 수 있습니다.'],
        [('고객을 먼저 분리', 'Train / external Test'), ('fold Training에서 fit', 'imputer + scaler + model'), ('Validation/Test는 변환', 'transform / predict only')],
        [('experiment.py', 'run_experiment', 'cv = -cross_val_score', 6), ('tests/test_finance.py', 'test_train_only_fit_and_imputation', 'original=', 5)],
        extra=p('누수 방지 정의 참고: scikit-learn 1.7 Common pitfalls — https://scikit-learn.org/1.7/common_pitfalls.html'),
        limit='신용점수 하위15% quantile은 PDF의 합성 정답 생성 규칙입니다. 전체 자료로 이를 계산한 생성 절차와 학습 전처리를 Test까지 fit하는 잘못은 구분합니다.')

    answer(10, 2, '입력·분할·전처리 정의는 공통으로 재사용하고, 모델 Pipeline과 정답은 각각 분리했습니다.',
        ['두 문제는 같은 6개 feature와 같은 고객 분할을 사용합니다. preprocessor 메서드는 중앙값 대치와 표준화라는 공통 처리법을 제공합니다.',
         'regression은 credit_score를 정답으로 Ridge 또는 Lasso를 붙입니다. classifier와 ensemble_search는 is_overdue를 정답으로 Logistic 또는 Forest를 붙입니다. 하나의 학습 객체가 두 문제를 동시에 출력하는 다중 작업 모델은 아닙니다.',
         '공통 설계를 재사용하되 Pipeline 객체와 학습 계수·트리 상태는 독립적입니다. 회귀는 RMSE 기반 CV, 분류는 F1 기반 CV이며 평가 함수도 따로 둡니다.'],
        ['같은 고객의 소득·부채·연체 이력으로 “몇 점인가”와 “연체할 가능성이 있는가”를 각각 질문합니다.',
         '회귀는 연속 숫자359점 같은 출력을, 분류는 클래스1 점수0.0986 같은 출력을 냅니다. 두 값의 단위와 의미가 다릅니다.',
         '업무에서 점수의 크기와 위험 분류를 함께 참고할 수 있지만, 이 CLI는 점수만으로 분류 결과를 재계산하지 않고 각각 학습한 두 모델을 호출합니다.'],
        [('공통 고객·입력', 'same 6 features / same split'), ('독립 Pipeline 학습', 'credit score / overdue target'), ('서로 다른 지표·출력', 'RMSE MAE R² / F1 AUC')],
        [('workflow.py', 'FinanceWorkflow.regression', 'return Pipeline', 1), ('workflow.py', 'FinanceWorkflow.classifier', None, 7)],
        limit='코드를 재사용하는 것과 이미 fit된 하나의 스케일러·모델 상태를 두 문제에서 공유하는 것은 다릅니다. 현재 코드는 각 모델 생성 시 전처리도 새로 만듭니다.')

    answer(11, 3, 'Accuracy도 함께 보고합니다. 불균형에서 연체 탐지를 확인하려고 F1을 선택 기준으로, AUC를 순위 평가로 추가했습니다.',
        [f'Test {test_size:,}명 중 정상은 {normal_test:,}명, 연체는240명입니다. 전부 정상이라고 예측하면 Accuracy={normal_test}/{test_size}=88%지만 TP=0·FN=240이어서 연체 Recall과 F1은0입니다.',
         f'Balanced Logistic Accuracy={logistic["accuracy"]:.4f}는 88%보다 약간 낮아도 연체210명을 찾습니다. F1은 Precision과 Recall의 조화평균이므로 경고를 남발하거나 연체를 모두 놓치는 경우를 드러냅니다.',
         'AUC는 임계값 하나의 정답률이 아니라 연체 고객의 점수가 정상보다 높게 순위화되는 정도를 요약합니다. 실제 GridSearchCV scoring은 f1이며 AUC로 Forest 설정을 선택한 것은 아닙니다.'],
        ['Logistic의 TP210·FP213·FN30을 넣으면 Precision=210/423, Recall=210/240입니다.',
         'F1은2TP/(2TP+FP+FN)=420/(420+213+30)=0.633484입니다. 실제 지표 함수 결과와 일치합니다.',
         '전부 정상 모델의88%라는 큰 숫자와 실제 연체를 찾는 모델의F1·Recall을 함께 비교하면 Accuracy만으로 업무 성공을 판단할 수 없다는 점이 보입니다.'],
        [('88% 모두 정상 예측', 'TP=0 / FN=240'), ('연체 탐지와 오경고', 'Precision / Recall → F1'), ('임계값 밖 순위 확인', 'ROC-AUC / continuous score')],
        [('workflow.py', 'classification_metrics', None, 10), ('workflow.py', 'FinanceWorkflow.ensemble_search', 'scoring="f1"', 1)],
        extra=metric_table(), formula='F1=2TP/(2TP+FP+FN)',
        limit='AUC가 높아도 특정 임계값의 오경고 비용이나 확률 보정이 좋다는 뜻은 아닙니다. 실제 손익과 점수 보정은 추가 검증이 필요합니다.')

    coefficients = table(['입력', 'Ridge α=1', 'Lasso α=1', 'Lasso α=100'],
        [[feature]+[f'{next(row for row in result["regression"][method]["rows"] if row["alpha"]==alpha)["coefficients"][i]:.6f}'
                    for method, alpha in [('ridge',1),('lasso',1),('lasso',100)]]
         for i,feature in enumerate(result['data']['features'])])
    answer(12, 3, 'L2는 큰 계수를 부드럽게 억제하고 L1은 일부 계수를 정확히0으로 만들 수 있습니다. 실제 계수 표에서 차이를 확인했습니다.',
        ['Ridge의 목적함수는 RSS+αΣw²이고 Lasso는 RSS/(2n)+αΣ|w|입니다. α는 규제 비중입니다. 두 sklearn 목적함수의 잔차 항 배율이 달라 같은 α를 같은 규제 힘으로 비교하지 않습니다.',
         '입력이 표준화됐으므로 소득 단위가 다른 변수보다 크다는 이유만으로 규제가 불공정해지는 영향을 줄입니다. 절편과 특징 계수도 구분합니다.',
         'Ridge α=1에서는6개 계수가 모두0이 아닙니다. Lasso α=1은 나이·소비점수·카드 수3개 계수를0으로 만들고, α=100은6개 모두0으로 만들어 Test RMSE가80.873692까지 나빠집니다. 큰 α가 항상 좋은 것은 아닙니다.'],
        ['교육용 계수1개가2라면 L1 벌점은|2|=2, L2는2²=4입니다. 계수 크기4가 되면 각각4와16이 되어 큰 값을 다르게 벌점화합니다.',
         '실제 소득 계수는 표준편차1 증가의 점수 변화를 나타냅니다. Ridge α=1의 약58.007은 소득1만원당58점이라는 뜻이 아닙니다.',
         '실제 α별 계수와 CV RMSE를 같이 보며 약한 항을 제거하는 장점과, 너무 강해 모든 특징을 지워 과소적합하는 손해를 설명합니다.'],
        [('표준화한 입력 6개', 'comparable feature scales'), ('L1 또는 L2 벌점', 'alpha 0.01 / 0.1 / 1 / 10 / 100'), ('계수와 오차를 함께', 'sparsity vs underfitting')],
        [('workflow.py', 'FinanceWorkflow.regression', 'if model ==', 7), ('experiment.py', 'run_experiment', 'coefficients=model.named_steps', 6)],
        extra=coefficients+p('실제 계수 그림: ')+file_link('reports/regularization.png')+p('공식 목적함수: scikit-learn 1.7 Ridge — https://scikit-learn.org/1.7/modules/generated/sklearn.linear_model.Ridge.html ; Lasso — https://scikit-learn.org/1.7/modules/generated/sklearn.linear_model.Lasso.html'),
        formula='Ridge: RSS+αΣw² ; Lasso: RSS/(2n)+αΣ|w|',
        limit='이번 비교는 동일 합성 데이터와 한 고정 외부 분할의 결과입니다. 계수0을 현실 고객 특성의 인과적 무의미함으로 일반화하지 않습니다.')

    answer(13, 3, '현재 구현은 Random Forest입니다. 이론상 여러 나무의 평균은 분산을 줄일 수 있고, 실험에서는 F1 향상을 확인했습니다.',
        ['한 결정나무는 학습 자료가 조금 바뀌면 다른 분기를 만들 수 있습니다. Random Forest는 기본 bootstrap=True로 학습 표본을 재추출하고 분기마다 일부 feature를 후보로 사용해 서로 다른 나무를 만든 뒤 클래스 확률을 평균합니다.',
         '각 나무가 독립적일수록 평균의 흔들림이 줄어드는 효과가 큽니다. 현실의 나무들은 상관이 있어 나무100개라는 이유만으로 분산이 정확히1/100이 되는 것은 아닙니다. min_samples_leaf=5도 매우 작은 집단까지 외우는 분기를 억제합니다.',
         f'Logistic 대비 Forest의 Test F1은 {logistic["f1"]:.6f}→{forest["f1"]:.6f}로 개선됐습니다. 같은 Forest 후보 내에서는 leaf1/depthNone의 CV F1 0.570904보다 leaf5/depthNone의0.673420이 높았습니다.'],
        ['교육용 두 나무가 동일 고객에게 위험 점수0.9와0.3을 줬다면 단순 평균은0.6입니다. 한 나무의 극단적 판단에만 의존하지 않습니다.',
         '실제100나무는 학습 표본과 분기 특성이 달라 서로 다른 정보를 종합합니다. 질문에 나오는 Boosting은 이전 모델의 오류를 순차적으로 보완하는 다른 방식이며 이번 폴더에는 없습니다.',
         f'보너스 학습곡선의 마지막 Train/Validation F1은 {curve["train_mean"][-1]:.6f}/{curve["validation_mean"][-1]:.6f}입니다. 이것은 Bonus Logistic의 곡선이며 Forest의 분산 감소 증거로 가져오면 안 됩니다.'],
        [('다른 표본·특징 후보', 'bootstrap / random features'), ('100개 결정나무', 'RandomForestClassifier'), ('확률 평균·Test 평가', 'F1 improved / trade-offs remain')],
        [('workflow.py', 'FinanceWorkflow.ensemble_search', 'forest = RandomForestClassifier', 7)],
        extra=metric_table()+p('원리 참고: scikit-learn 1.7 RandomForestClassifier — https://scikit-learn.org/1.7/modules/generated/sklearn.ensemble.RandomForestClassifier.html'),
        formula='Var(평균)=σ²×[ρ+(1−ρ)/B] (동일 분산·동일 상관을 가정한 설명 모형)',
        limit='단일 결정나무 비교, 여러 데이터 재표집의 편향·분산 분해는 수행하지 않았습니다. F1 개선만으로 분산 감소를 직접 측정했다고 주장하지 않습니다.')

    answer(14, 3, '이번에는 class_weight를 선택했습니다. Train의 손실 비중만 바꾸고 Test의 표본·정답·평가 빈도는 유지합니다.',
        [f'Train 정상7039명·연체{train_positive}명으로 가중치0={result["class_balance"]["weights"]["0"]:.6f}, 가중치1={result["class_balance"]["weights"]["1"]:.6f}입니다. 드문 연체의 한 건이 학습 손실에 더 크게 반영됩니다.',
         'class_weight는 sklearn 내장 기능이라 Pipeline·CV 안에서 간단히 적용할 수 있고, 원본 고객을 늘리거나 가상의 고객 점을 생성하지 않습니다. 이 구현에서 선택한 단순성과 원본 보존의 이유입니다. SMOTE와 어느 것이 더 좋을지는 비교 실험을 하지 않았습니다.',
         'SMOTE를 쓴다면 CV의 내부 Training 부분에서만 합성해야 합니다. Test를 재표집하거나 평가에 학습 가중치를 적용하면 실제 대상 분포의 성능과 다른 값을 보게 됩니다.'],
        ['현재Train에서 정상 한 건 손실0.5의 가중 기여는 약0.284, 연체 한 건은 약2.081입니다. 가중치가 레이블 자체를 바꾸지는 않습니다.',
         'Test는 연체240·정상1760을 그대로 두고 모든 고객을 한 번씩 평가합니다. classification_metrics에는 sample_weight를 전달하지 않습니다.',
         '업무에서 드문 불량·사고를 학습할 때 같은 원리를 쓸 수 있습니다. 다만 weighted 모델의 predict_proba가 실제 발생률에 맞는지는 별도 보정·검증 문제입니다.'],
        [('Train 레이블 빈도', '7039 normal / 961 overdue'), ('학습 손실 비중 조정', 'balanced / no synthetic rows'), ('원본 Test 평가', '2000 customers / unweighted metrics')],
        [('workflow.py', 'FinanceWorkflow.classifier', 'LogisticRegression', 3), ('experiment.py', 'run_experiment', 'result["class_balance"]', 4)],
        formula='weighted loss=Σᵢ weight(yᵢ)×lossᵢ',
        limit='fit된 모델이 가중 학습을 받은 상태로 Test를 예측하는 것은 정상입니다. “Test에 적용하지 않는다”는 말은 모델의 가중치를 없애라는 뜻이 아니라 Test 재표집·재학습·평가 가중치 변경을 하지 않는다는 뜻입니다.')

    answer(15, 4, '가상 대출 심사에서는 위험 판단의 품질을 먼저 충족시키고, 처리 시간 목표 안에서 모델을 고르겠습니다.',
        ['성능과 속도를 하나의 정답으로 고정하지 않습니다. 손실이 큰 심사에서는 연체 탐지·오경고 비용·확률 보정과 검토 가능한 근거를 먼저 정의하고, 온라인 요청의 지연 목표를 만족하는지 확인하는 순서가 합리적입니다.',
         '현재 Logistic은6개 특징의 선형 점수·sigmoid, Forest는100개 나무의 판단을 종합합니다. 계산 구조는 다르지만 이 폴더에는 predict 지연의 p50/p95나 동시 요청 부하 측정이 없으므로 몇 ms로 더 빠르다고 말할 근거는 없습니다.',
         'main.py --customer는 요청마다 데이터 생성·Train 분할·모델 fit까지 수행합니다. 이 전체 실행 시간은 이미 학습된 모델의 순수 predict 속도와 다릅니다. 운영에서는 학습과 추론을 분리하는 설계가 필요하지만 현재 서비스 코드로 구현한 것은 아닙니다.'],
        ['교육용 온라인 사전 점검에 p95≤200ms라는 목표를 가정할 수 있습니다. 이는 실제 측정값이나 요구된 SLA가 아닙니다.',
         '먼저 같은 Test·같은 업무 비용 기준을 만족하는 후보를 찾고, 같은 장비·입력 배치로 전처리 포함 predict 시간과 학습 시간을 구분해 측정합니다.',
         '일괄 월별 심사처럼 수분 처리 시간이 허용되면 조금 느리더라도 업무 비용이 낮은 모델을 고려할 수 있습니다. 실시간 알림이라면 응답 지연이 추가 제약이 됩니다.'],
        [('업무 품질·비용 목표', 'Recall / FP FN cost / calibration'), ('예측 지연 별도 측정', 'same device / p50 p95'), ('조건에 맞는 모델', 'online vs batch constraints')],
        [('main.py', 'main', 'frame=generate_data()', 8), ('workflow.py', 'FinanceWorkflow.ensemble_search', 'n_estimators=100', 2)],
        extra=metric_table(),
        limit='지연 수치를 새로 지어내거나 운영 배포가 끝난 것처럼 설명하지 않습니다. 현재 비교의 실측 근거는 모델 품질 표이고 속도 평가는 미측정입니다.')

    answer(16, 4, '오탐과 미탐의 비용을 함께 정해야 합니다. 현재 임계값은0.5로 고정됐고 비용 기반 임계값 튜닝은 수행하지 않았습니다.',
        ['양성1은 연체입니다. FP는 정상 고객을 연체로 분류해 추가 검토·거절 같은 불편을 줄 수 있는 경우이고, FN은 연체 고객을 정상으로 놓쳐 손실 위험을 남기는 경우입니다. 예측 레이블을 실제 은행의 최종 거절 결정과 동일하게 취급하지 않습니다.',
         '어느 오류가 더 심각한지는 대출액·회수율·고객 손실·검토 정책에 따라 달라집니다. 가상 비용 C_FN이 더 크면 FN을 줄이는 방향을 우선 검토할 수 있습니다. 아래 비용은 교육용이며 실제 은행의 손익을 측정한 값이 아닙니다.',
         '고정 모델에서 임계값을 낮추면 같은 점수의 양성 집합이 커져 Recall은 낮아지지 않고 FP도 줄어들지 않습니다. 높이면 반대입니다. Precision은 데이터에 따라 달라지므로 무조건 좋아진다고 단정하지 않습니다.'],
        ['교육용 FP 비용1만원·FN 비용100만원이면 Logistic 비용은213×1+30×100=3213만원, Forest는144×1+51×100=5244만원입니다. F1이 더 높은 Forest도 이 가정의 비용은 더 큽니다.',
         'FP 비용을100만원·FN 비용을1만원으로 바꾸면 Logistic21330만원, Forest14451만원으로 선택이 달라집니다. 따라서 오류 수와 비용 가정을 같이 말해야 합니다.',
         '실제 조정은 Train 내부 Validation/OOF 점수로 후보 임계값별 FP·FN·비용을 비교하고 선택값을 고정한 뒤 외부 Test에서 한 번 확인하는 순서입니다. 확률이 충분히 보정됐고 단순한 두 오류 비용만 고려한다는 가정에서만 t=C_FP/(C_FP+C_FN)이라는 이론 기준을 쓸 수 있습니다.'],
        [('오류와 비용을 정의', 'FP normal→overdue / FN missed'), ('Train 내부 임계값 선택', 'Validation or OOF / cost curve'), ('고정 후 Test 확인', 'current code threshold=0.5')],
        [('experiment.py', 'run_experiment', 'prediction = (probability>=0.5)', 5), ('workflow.py', 'classification_metrics', 'confusion_matrix=', 1)],
        extra=matrix_table()+table(['교육용 비용 가정', 'Logistic 합계', 'Forest 합계'],
                                 [['FP=1만원, FN=100만원','3,213만원','5,244만원'],['FP=100만원, FN=1만원','21,330만원','14,451만원']]),
        formula='예시 비용=C_FP×FP+C_FN×FN ; 연체 예측 ⇔ score≥t',
        limit='임계값0.3/0.7에서의 실제 혼동행렬·최적 비용·운영 승인/거절/보류 정책은 구현·측정하지 않았습니다. 이 답변은 기존 결과를 이용한 판단 예시와 추가 평가 절차입니다.')

    output = ['<section id="evaluator-questions" class="qa-appendix"><p class="tag">A5-1.PNG / 16 QUESTIONS / CODE AND MEASURED EVIDENCE</p>',
              '<h2>평가 질문과 답변 · A5-1.png의 16개 질문</h2>',
              p('기존 학습 설명과 전체 코드 뒤에 이어 붙인 부록입니다. 항목 1의7개, 항목 2의3개, 항목 3의4개, 항목 4의2개 질문을 원래 순서로 담았습니다. 질문을 먼저 읽고 답변·실제 근거·수치 예시·도식을 따라가면 됩니다.'),
              p('이 부록의 “실측”은 reports/experiment.json·bonus.json에 저장된 같은 고객 분할의 결과입니다. “교육용 예시”는 원리를 설명하는 계산이며 실제 은행 성능·처리 속도·배포 정책을 측정한 결과가 아닙니다.'),
              '<nav aria-label="평가 질문 목차"><ol>'+''.join(f'<li><a href="#qa-{row["number"]:02d}">{escape(row["question"])}</a></li>' for row in rows)+'</ol></nav>']
    current_group = None
    for row in rows:
        if row['group'] != current_group:
            current_group = row['group']
            output.append(f'<h2 id="qa-group-{current_group}">{escape(GROUPS[current_group])}</h2>')
        output.extend([f'<article class="qa-item" id="qa-{row["number"]:02d}"><h3>질문 {row["number"]}. {escape(row["question"])}</h3>',
                       '<h4>답변</h4><div class="status">'+html_tools.inline(row['lead'])+'</div>',
                       ''.join(p(text) for text in row['explanation']), row['extra'],
                       '<h4>초보자가 따라가는 활용 사례와 수치 예시</h4>', steps(row['example'])])
        if row['formula']:
            output.append(html_tools.formula(row['formula']))
        output.append(html_tools.diagram(f'qa-flow-{row["number"]:02d}', f'질문 {row["number"]}의 설명 흐름', row['nodes']))
        output.append('<h4>실제 구현 코드로 이동</h4>')
        for file, symbol, needle, limit in row['evidence']:
            output.append(proof(file, symbol, needle, limit))
        output.extend(['<h4>평가자가 구분할 측정 범위와 한계</h4>', p(row['limit']), '</article>'])
    output.extend([p('설명 자료: A5-1.png. 답변 근거: 이 폴더의 원본 생성 코드·Pipeline·평가 함수·실제 JSON·PNG·README·테스트 기록. 도식은 diagram-design financial-services의 정적 flowchart, doc-inline 960×600입니다.'), '</section>'])
    return '\n'.join(output), references
