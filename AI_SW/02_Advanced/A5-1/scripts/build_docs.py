"""실측 JSON·실제 AST·원문 SHA로 두 Markdown와 두 독립 HTML 생성."""
import ast
import hashlib
from html import escape
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).parent))
import html_tools
from doc_content import SECTIONS
from assessment_answers import QUESTIONS, render_answers
html_tools.SECTIONS=SECTIONS

def locate(file,symbol):
    source=(ROOT/file).read_text()
    nodes=ast.parse(source).body
    for name in symbol.split("."):
        found=next(n for n in nodes if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
        nodes=found.body
    return found.lineno,"\n".join(source.splitlines()[found.lineno-1:found.end_lineno])

def sources():
    blocks,hashes=[],[]
    for path in sorted(ROOT.rglob("*.py")):
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):continue
        relative=path.relative_to(ROOT).as_posix();text=path.read_text()
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.append(dict(file=relative,sha256=digest,lines=len(text.splitlines())))
        rows=[f'<span class="source-line" id="{html_tools.anchor(relative,i)}"><a class="ln" href="#{html_tools.anchor(relative,i)}">{i}</a>{escape(line)}</span>' for i,line in enumerate(text.splitlines(),1)]
        blocks.append(f'<section class="source-section"><h2>{escape(relative)}</h2><p>SHA-256: <code>{digest}</code> · <a href="../{relative}">원본 파일</a></p><pre><code>'+"".join(rows)+'</code></pre></section>')
    return "\n".join(blocks),hashes

def page(title,body):
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>'+html_tools.CSS+'</style></head><body><main><p class="tag">A5-1 / FINANCE / SUPERVISED LEARNING / PY312</p>'+body+'<footer>diagram-design financial-services · flowchart doc-inline960×600 · 정적SVG·MathML·실측PNG내장. 외부다운로드없음. Geist·Instrument Serif가없으면 Apple SD Gothic Neo·Georgia·Menlo로대체됩니다.</footer></main></body></html>'

def comparison(result):
    table="| 모델 | Accuracy | Precision | Recall | F1 | AUC |\n|---|---:|---:|---:|---:|---:|\n"
    for name,row in result["classification"].items():
        table+="| "+name+" | "+" | ".join(f"{row[k]:.6f}" for k in ["accuracy","precision","recall","f1","auc"])+" |\n"
    return table

def readme(result,bonus):
    regression="| 모델 | alpha | Train CV RMSE | Test RMSE | Test MAE | Test R² |\n|---|---:|---:|---:|---:|---:|\n"
    for name,m in result["regression"].items():
        for row in m["rows"]:
            regression+=f"| {name} | {row['alpha']} | {row['cv_rmse']:.6f} | {row['rmse']:.6f} | {row['mae']:.6f} | {row['r2']:.6f} |\n"
    grid="| max_depth | min_samples_leaf | Train CV F1 평균 | fold 표준편차 |\n|---|---:|---:|---:|\n"
    for c in result["grid_search"]["candidates"]:
        grid+=f"| {c['params']['model__max_depth']} | {c['params']['model__min_samples_leaf']} | {c['mean_f1']:.6f} | {c['std_f1']:.6f} |\n"
    curve="| fold내Train 고객수 | Train F1 평균 | Validation F1 평균 | Validation std |\n|---:|---:|---:|---:|\n"
    c=bonus["learning_curve"]
    for n,a,b,s in zip(c["sizes"],c["train_mean"],c["validation_mean"],c["validation_std"]):
        curve+=f"| {n} | {a:.6f} | {b:.6f} | {s:.6f} |\n"
    e=result["example"]
    return f"""# A5-1: 대출을 해줘도 될지 판단하는 지도학습 시스템

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
python main.py --customer '{{"age":40,"annual_income":5000,"spending_score":50,"debt_ratio":0.4,"credit_card_count":3,"overdue_count_6m":1}}'
```

위 실제 입력의 결과는 신용점수 359.558161, 연체 확률 0.098553입니다. [실제 CLI 로그](reports/cli_execution.txt)에 기록했습니다. 소득 단위는 만원, 부채비율은 0~1입니다. CLI는 실행마다 Train에서 Ridge alpha 1과 balanced Logistic을 fit합니다. `python main.py`는 전체 기본 실험을 실행합니다. PDF 세부 기능 밖의 배포 API·승인/거절/보류 정책 서비스는 추가하지 않았습니다.

## 3. 데이터와 누수 방지

- 입력: age, annual_income, spending_score, debt_ratio, credit_card_count, overdue_count_6m의 6개입니다.
- 정답: credit_score(0~1000 회귀), is_overdue(0/1 분류)이며 입력에서 모두 제외합니다.
- 전체 정상은 8,799명, 연체는 1,201명입니다. Train 양성={result['split']['train_positive']}, Test 양성={result['split']['test_positive']}입니다.
- CSV SHA-256은 `{result['data']['sha256']}`입니다.
- 외부 분할은 층화 8:2/seed 42이며 고객 ID 중복이 없습니다. 회귀 KFold와 분류 StratifiedKFold는 모두 5-fold/shuffle/seed 42입니다.
- 대치→표준화→모델을 Pipeline으로 묶어 CV 내부 Training 부분에서만 fit합니다. Test는 transform/predict만 합니다.
- alpha는 Train CV RMSE, Forest 설정은 Train CV F1으로 선택하며 Test 표로 설정을 바꾸지 않습니다.

표준화는 `z=(x−μtrain)/σtrain`입니다. 원본 결측은 없지만 요구된 median 대치 단계와 NaN 검증을 수행했습니다. Test 소득을 1e12로 바꿔 transform해도 Train 평균이 바뀌지 않음을 검사합니다. 원본 레이블의 하위 15% quantile은 PDF 합성 생성 규칙이며 학습 전처리의 Train-only 통계와 구분해서 보존합니다.

## 4. 규칙 기준선과 분류 성능

다섯 양성 규칙은 연체≥3, 부채>0.7, 소득<3000, 카드>7, 연체≥1이면서 부채>0.45입니다. 처음 만족한 조건에서 1을 반환하고 끝까지 해당하지 않으면 0입니다. 동일 Test 2,000명에서 측정했고 ML 임계값은 0.5로 고정했습니다.

{comparison(result)}

규칙은 1,218명을 경고하고 그중 989명이 오경고입니다. Recall은 높지만 Precision/F1은 낮습니다. Forest는 규칙보다 F1과 오경고 수를 개선하는 대신 미탐이 늘었습니다. Logistic은 Forest보다 AUC/Recall이 높고 Forest는 Accuracy/F1이 높으므로 한 모델이 모든 지표에서 우수하다고 설명하지 않습니다.

Test를 모두 정상이라 하면 Accuracy는 88%지만 양성 Recall/F1은 0입니다. Logistic Accuracy 87.85%가 그보다 조금 낮아도 연체 210/240명을 찾습니다. balanced weight는 Train 빈도에서 `n_train/(2×n_class)`로 계산하며 실제 가중치는 `{result['class_balance']['weights']}`입니다. SMOTE는 선택 대안이고 이번에는 사용하지 않았습니다.

![동일 Test의 세 모델 혼동행렬](reports/confusion_matrix.png)

행=정답, 열=예측, 순서=[정상0,연체1]입니다. Logistic 행렬은 [[1547,213],[30,210]], Forest는 [[1616,144],[51,189]]입니다. 오경고 FP와 미탐 FN의 영향을 분리해서 읽습니다.

$$ Precision=TP/(TP+FP), Recall=TP/(TP+FN) $$

$$ F1=2×Precision×Recall/(Precision+Recall) $$

![ROC와 각 모델 AUC](reports/roc_auc.png)

규칙 AUC에는 확률이 아닌 0/1 flag를 사용합니다. 몇 개 점으로 된 거친 ROC이며 보정된 위험 확률이 아닙니다. ML AUC에는 predict_proba의 클래스 1 확률을 사용합니다.

## 5. 신용점수 회귀와 규제

{regression}

선택 alpha는 Ridge {result['regression']['ridge']['selected_alpha']}, Lasso {result['regression']['lasso']['selected_alpha']}입니다. alpha별 Test 값은 진단 자료이며 선택은 Train CV RMSE만으로 했습니다. Test 출력은 0~1000으로 clip하여 지표를 계산합니다. CV scoring은 raw 출력의 RMSE라는 차이를 명시합니다.

$$ RMSE=√(Σᵢ(yᵢ−ŷᵢ)²/n) $$

$$ R²=1−Σᵢ(yᵢ−ŷᵢ)²/Σᵢ(yᵢ−ȳ)² $$

![Ridge와 Lasso의 alpha별 실제 계수](reports/regularization.png)

표준화한 6입력의 계수입니다. sklearn Ridge는 RSS+alpha×L2, Lasso는 RSS/(2n)+alpha×L1이므로 같은 alpha를 같은 규제 힘으로 읽지 않습니다. 강한 Lasso alpha는 여러 계수를 0으로 만들지만 오차도 커집니다. RMSE 약 30점은 생성 노이즈 표준편차 30점과 함께 해석합니다.

## 6. 앙상블 최적화와 특징 중요도

Random Forest는 100 trees/balanced/seed 42/n_jobs 1입니다. depth [5,None]×leaf [1,5]의 4조합을 5-fold F1으로 탐색합니다. 파라미터당 2후보·총 4조합은 PDF 권장 제한 이내입니다. 최적 설정은 `{result['grid_search']['best_params']}`, 최고 Train CV F1={result['grid_search']['best_cv_f1']:.6f}입니다.

{grid}

![튜닝된 Forest의 특징 중요도](reports/feature_importance.png)

1. 연소득 중요도 0.491469가 가장 높고 최근 연체 0.225720·부채비율 0.168634가 뒤를 잇습니다.
2. 제공 점수 생성식이 이 세 변수를 사용하므로 합성 데이터 구조와 일관됩니다.
3. 불순도 감소 중요도는 모델이 사용한 정보를 요약하며 인과효과가 아닙니다. 카드 수의 작은 중요도를 현실에서 무의미하다고 일반화하지 않습니다.

## 7. 실제 고객 예측과 오류 해석

Test 고객 {e['customer_id']}의 입력은 `{e['input']}`입니다. 실제 점수는 {e['actual_credit']:.0f}, Ridge 예측은 {e['predicted_credit']:.6f}, 실제 연체={e['actual_overdue']}, Logistic 확률={e['overdue_probability']:.6f}입니다. 확률이 0.5보다 낮아 연체를 놓쳤습니다. 회귀 점수 오차와 분류 오류가 다른 형태로 발생하는 예입니다.

노이즈와 별도 레이블 난수가 있으며 모델은 6입력만 보므로 완벽한 분류를 기대할 수 없습니다. 합성 자료만으로 현실 오류의 원인을 확정하지 않습니다. 고객 번호는 합성 행 ID이며 실제 개인정보가 아닙니다.

## 8. 보너스: 상속·모듈화·학습곡선

[bonus.py](bonus.py)의 DerivedFeatures는 BaseEstimator/TransformerMixin을 상속해 카드당 소득과 부채×연체를 계산합니다. BonusWorkflow(FinanceWorkflow)는 전처리만 재정의하고 기본 회귀·분류·탐색을 상속합니다. 원본 CSV는 수정하지 않습니다. 보너스 Test F1={bonus['classifier']['f1']:.6f}, AUC={bonus['classifier']['auc']:.6f}입니다. F1이 기본 Logistic과 같아 뚜렷한 개선이라고 보고하지 않습니다.

기본과 보너스 모두 .py 모듈로 나눠 Notebook 상태에 의존하지 않습니다. 학습곡선은 보너스 Logistic을 원래 Train 내부 5-fold로 평가하며 외부 Test를 사용하지 않습니다.

{curve}

![보너스의 Train/Validation 학습곡선](reports/learning_curve.png)

최대 크기의 Train F1={c['train_mean'][-1]:.6f}, Validation={c['validation_mean'][-1]:.6f}로 차이가 작습니다. 크기를 늘려도 큰 개선이 관측되지 않고 약 0.64~0.65여서 표현·모델·노이즈 제약을 검토할 근거가 됩니다. 작은 차이만으로 모든 과대적합이 없다고 증명하지 않습니다. 음영은 fold 표준편차이며 신뢰구간이 아닙니다.

## 9. TDD·검증·설명 문서

미구현 stub에서 19개 테스트를 실행해 11 failed/8 errors를 기록했고 구현 후 19 passed가 되었습니다. [RED 로그](reports/tdd_red.txt), [GREEN 로그](reports/tdd_green.txt). 데이터 동치·범위, 5개 규칙 경계, 고정 층화 분할, Train-only 통계·결측 대치, 타겟 제외, alpha/clip/balanced/grid, 손계산 지표, 상속/clone/원본 무변경을 검증합니다.

- [README HTML](README.html): 이 보고서와 실제 그림·도식.
- [학습 MD](docs/code_walkthrough.md): 15개 개념·수식·현실 예시·실제 함수의 순차 설명.
- [학습 HTML](docs/code_walkthrough.html): 위 설명과 Python 전체 원문·줄번호 링크·SHA 내장.
- [기본 실측값](reports/experiment.json), [보너스 실측값](reports/bonus.json), [문서 생성 근거](reports/document_build.json), [최종 검증](reports/final_verification.json).

Markdown은 README와 학습 문서의 정확히 두 개이며 각각 HTML을 만들었습니다. diagram-design financial-services를 적용하고 코드 배경 #e7ebf0/글자 #14213d/줄번호 #475569/선택줄 #f4eddf를 사용합니다. flowchart 960×600, 실제 그림, 코드, MathML을 내장하여 외부 서버 없이 읽힙니다.

기존 상위 저장소는 `https://github.com/OliverJoo/codyssey_ai`, 미션 경로는 `AI_SW/02_Advanced/A5-1`입니다. A5-1 변경은 상위 저장소에서 기능 단위 커밋으로 관리합니다. Git에 CSV를 포함하지 않고 제공 생성기로 재현합니다.
"""


def build():
    result=json.loads((ROOT/"reports/experiment.json").read_text())
    bonus=json.loads((ROOT/"reports/bonus.json").read_text())
    md=readme(result,bonus);(ROOT/"README.md").write_text(md)
    guide=["# A5-1: 초보 개념에서 실제 코드 평가까지\n",
           "지도학습을 처음 배우는 독자는 01~05에서 입력·정답·데이터 분리·전처리를 이해한 뒤 06~11에서 수식과 모델·실측 평가를 읽고 12~15에서 실행·보너스·TDD를 확인합니다. 현실 예시의 교육용 손계산과 실제 10,000행 측정 결과를 구분합니다. 함수 링크는 실제 코드의 해당 줄로 연결되고 HTML에는 전체 원문도 내장됩니다.\n",
           "## 먼저 알아둘 기본 용어\n",
           "한 행은 고객 한 명입니다. feature는 예측 입력 열, target은 학습 정답, fit은 통계·계수 학습, transform은 배운 통계로 변환, predict는 새 입력의 답 계산입니다. NumPy array는 숫자 배열, Pandas DataFrame은 행·열 이름을 가진 표, sklearn Pipeline은 처리를 순서대로 연결한 객체입니다. [6개 입력] → [학습한 변환] → [모델] → [예측]을 같은 관점으로 읽습니다.\n"]
    refs=[]
    images={"regularization":"regularization.png","metrics":"confusion_matrix.png","ensemble":"roc_auc.png","importance":"feature_importance.png","learning":"learning_curve.png"}
    for section in SECTIONS:
        line,code=locate(section["file"],section["symbol"])
        refs.append(dict(section=section["id"],file=section["file"],symbol=section["symbol"],line=line))
        guide.extend(["## "+section["title"]+"\n","### 개념과 필요한 이유\n",section["concept"]+"\n","### 현실 예시: 입력→계산→판단\n",section["example"]+"\n"])
        for name in ["formula","extra_formula"]:
            if name in section:guide.append("$$ "+section[name]+" $$\n")
        if "diagram" in section:
            guide.extend(["<!-- diagram:"+section["id"]+" -->\n","처리순서: "+" → ".join(n[0] for n in section["diagram"])+"\n"])
        guide.extend(["### 실제 코드와 순차 실행\n",section["detail"]+"\n",f"[실제 코드: {section['file']} · {section['symbol']} · L{line}](../{section['file']}#L{line})\n","```python\n"+code+"\n```\n","### 활용 사례와 해석 한계\n",section["cases"]+"\n"])
        if section["id"] in images:
            guide.append(f"![실제실행결과: {section['title']}](../reports/{images[section['id']]})\n")
        if section["id"]=="importance":guide.append(comparison(result)+"\n")
        if section["id"]=="learning":
            c=bonus["learning_curve"]
            guide.append(f"실측 마지막 Train/Validation F1={c['train_mean'][-1]:.6f}/{c['validation_mean'][-1]:.6f}이고 작은 크기부터 큰 크기까지 Validation은 약 0.64~0.65입니다. 데이터 증가의 큰 개선이 관측되지 않았다는 점과 fold별 흔들림을 함께 읽습니다.\n")
    guide.append("## 전체 실행과 보고서\n\n[README](../README.md)와 [README HTML](../README.html)의 실행 명령, 실제 전체 표, CV 조건, Git 미게시 상태를 확인하세요. 아래는 현재 파일의 실제 원문이며 SHA를 같이 기록합니다. 다른 미션에 의존하지 않습니다.\n")
    gmd="\n".join(guide);(ROOT/"docs/code_walkthrough.md").write_text(gmd)
    source,hashes=sources()
    toc='<nav aria-label="순차 학습 목차"><ul>'+"".join(f'<li><a href="#{s["id"]}">{escape(s["title"])}</a></li>' for s in SECTIONS)+'</ul></nav>'
    gh=page("A5-1 개념·실제코드·평가",'<p class="status">10,000가상고객 · 19개테스트통과 · 실제5개그래프 · 교육용예시와실측구분</p>'+toc+html_tools.markdown_html(gmd,"guide")+'<section id="sources"><h2>실제 전체 코드</h2>'+source+'</section>')
    appendix,question_refs=render_answers(result,bonus,locate)
    # 원래 학습 내용·코드·footer 뒤에 부록을 이어 붙인다. 재생성에도 유지된다.
    gh=gh.replace('</main></body></html>',appendix+'</main></body></html>')
    (ROOT/"docs/code_walkthrough.html").write_text(gh)
    render=re.sub(r'\]\(reports/([^)]*\.png)\)',r'](../reports/\1)',md)
    rh=html_tools.markdown_html(render,"readme")
    rh=re.sub(r'href="\.\./([^"]+)"',r'href="\1"',rh)
    rh=re.sub(r'href="(#code-[^"]+)"',r'href="docs/code_walkthrough.html\1"',rh)
    rh=rh.replace('href="#guide">학습 MD','href="docs/code_walkthrough.md">학습 MD').replace('href="#guide"','href="docs/code_walkthrough.html"')
    rh+=html_tools.diagram("readme-models","신용점수와연체모델흐름",[("PDF 10,000행 생성","6 features / 2 targets"),("Train-only 모델 학습","Ridge / Lasso / Logistic / RF"),("동일 Test 비교","regression + classification")])
    rh+=html_tools.diagram("readme-validation","설정선택과실측리포트",[("8:2 고객 분리","seed 42 / stratified"),("Train 5-fold 설정 선택","alpha RMSE / forest F1"),("Test 지표와 그림","report.json / PNG")])
    rh=page("A5-1 README",rh);(ROOT/"README.html").write_text(rh)
    for doc in [gh,rh]:
        ids=re.findall(r'\bid="([^"]+)"',doc)
        assert len(ids)==len(set(ids)),"duplicate IDs"
        assert all(link in ids for link in re.findall(r'href="#([^"]+)"',doc)),"broken anchor"
    report=dict(markdown_files=["README.md","docs/code_walkthrough.md"],html_files=["README.html","docs/code_walkthrough.html"],
                sections=len(SECTIONS),tests=19,guide_diagrams=gh.count('<svg '),readme_diagrams=rh.count('<svg '),
                guide_mathml=gh.count('<math '),readme_mathml=rh.count('<math '),sources=hashes,code_references=refs,broken_internal_links=0,
                assessment_questions=len(QUESTIONS),assessment_question_texts=QUESTIONS,assessment_code_references=question_refs)
    (ROOT/"reports/document_build.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print({k:v for k,v in report.items() if k not in ["sources","code_references","assessment_code_references","assessment_question_texts"]})

if __name__=="__main__":build()
