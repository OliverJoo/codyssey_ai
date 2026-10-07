# A2-1 PDF 요구사항 재검토

코드와 노트북 실행을 마친 뒤 PDF 1~8쪽을 다시 읽고, 필수 산출물·수치 기준·금지 사항·선택 과제를 구현과 대조했다. 검토일은 2026-10-07이다. 계산 근거는 [필수 결과](../reports/metrics.json), [보너스 결과](../reports/bonus_metrics.json), [테스트 실행 기록](../reports/tdd_all_green.txt), [노트북 실행 기록](../reports/notebook_execution.txt)이다.

## 1. 필수 산출물

| PDF 위치 | 요구 산출물 | 실제 파일 | 판단 |
|---|---|---|---|
| 1쪽 | 선형대수 모듈 | [linear_algebra.py](../src/linear_algebra.py) | 포함 |
| 1~2쪽 | 미적분 모듈 | [calculus.py](../src/calculus.py) | 포함 |
| 2쪽 | 역전파 유도 노트북 | [backprop_derivation.ipynb](../notebooks/backprop_derivation.ipynb) | 실행 완료 |
| 2쪽 | VanillaGD/Momentum 모듈 | [optimizer.py](../src/optimizer.py) | 포함 |
| 2쪽 | 확률·손실 노트북 | [probability_loss.ipynb](../notebooks/probability_loss.ipynb) | 실행 완료 |
| 2쪽 | 개요·실행·결과 README | [README.md](../README.md) | 포함 |
| 6쪽 | 라이브러리 버전 명시 | [requirements.txt](../requirements.txt) | py312 실제 버전 확인 |

`backprop.py`와 `probability.py`는 필수 노트북의 수학 계산을 테스트 가능한 형태로 옮긴 보조 모듈이다. 별도의 학습 기능이나 새 문제를 추가하지 않았다. 이미지 전처리, 결과 실행, 노트북 실행 스크립트는 필수 결과의 재현을 위한 보조 파일이다.

## 2. 선형대수·미적분

| PDF 3쪽 요구 | 검사 및 실제 결과 | 판단 |
|---|---|---|
| 단위 원 회전 전후를 한 Figure에 겹쳐 출력 | [행렬 변환 PNG](../outputs/matrix_transformations.png), 회전 반지름선도 표시 | 충족 |
| S(2,.5)의 타원 | 같은 Figure의 두 번째 축, x축 2배/y축 .5배 | 충족 |
| Sh(k)의 전단 | k=.8, x'=x+.8y | 충족 |
| det와 면적비의 오차 ≤1% | 신발끈 공식으로 독립 측정, 세 변환 모두 0% | 충족 |
| Power Iteration 직접 구현 | [반복 코드](../src/linear_algebra.py#L64), 20회 후 λ=4.618033988749502 | 충족 |
| eig와 비교 오차 ≤5% | 검증 λ=4.618033988749895, 상대 오차 8.50×10⁻¹²% | 충족 |
| k=10,50,100 SVD 복원 한 Figure | [복원 PNG](../outputs/svd_reconstructions.png), 유효 k=10,50,64 표시 | 수학적 상한 명시하여 충족 |
| x², x=3의 중심차분 오차 ≤1e-4 | 미분값 6.000000000039306, 절대 오차 3.93×10⁻¹¹ | 충족 |
| x²+y² 등고선 및 여러 점의 Gradient | [기울기 PNG](../outputs/gradient_contours.png), 8개 점에 화살표 | 충족 |
| Gradient가 등고선에 수직 | 그림과 별도로 접선 내적 확인, 최대 1.78×10⁻¹⁵ | 충족 |

면적비는 비음수이므로 일반적인 비교 대상은 `abs(det(A))`다. 선택한 세 변환의 det는 모두 양수 1이다. 다각형 면적과 정확한 원 면적 π를 섞지 않고 동일한 점 집합의 변환 전후를 비교했다.

## 3. 고정 역전파 예제

| PDF 3~4쪽 요구 | 실제 구현·검증 | 판단 |
|---|---|---|
| 입력 2→은닉 2→출력 1 | W1(2,2), x(2,), W2(2,), 출력 스칼라 | 충족 |
| x/W1/b1/W2/b2 고정값, Sigmoid, BCE | [fixed_example](../src/backprop.py#L6)와 노트북에 동일 값 기록 | 충족 |
| z1,a1,z2,y_pred 중간값 | 노트북 손계산 및 NumPy 출력, shape 포함 | 충족 |
| 여섯 필수 미분을 단계별 유도 | dy_pred/dz2/dW2/da1/dz1/dW1 모두 식과 숫자 표시 | 충족 |
| 모든 단계의 shape | 스칼라 `()`, 벡터 `(2,)`, 행렬 `(2,2)` 표기 | 충족 |
| 손계산과 NumPy 소수점 4자리 일치 | 각 체크포인트에서 `assert_array_equal(round(...,4), hand)` 실행 | 충족 |

추가 검증은 모든 가중치와 편향의 중심차분이다. 이는 역전파 검증이며 새로운 학습 과제가 아니다. 편향의 미분도 덧셈 연쇄 법칙에 따라 기록했다. 학습 루프와 자동 미분 엔진은 만들지 않았다.

## 4. 최적화·확률

| PDF 4쪽 요구 | 실제 결과 | 판단 |
|---|---|---|
| Vanilla GD, 원형 함수 | 직접 업데이트, 초기점 (5,5) | 충족 |
| lr=.1, 100회 후 반경 ≤.1 | 반경 1.4404×10⁻⁹ | 충족 |
| 등고선 위 점선 경로 | [원형 경로](../outputs/circle_paths.png) | 충족 |
| lr≥.5의 발산 그래프 | lr=1.1에서 20회 후 반경 271.088, [.5/1/1.1 비교](../outputs/learning_rate_loss.png) | 문구의 일반화 오류를 설명하고 실제 발산 사례 포함 |
| Momentum β=.9, 같은 Figure 비교 | GD와 원형·타원형 경로 각각 겹쳐 출력 | 충족 |
| 타원형 x²+10y²의 Momentum 이점 | 같은 lr=.01, 손실 .01 첫 도달 GD 194회/Momentum 78회 | 충족, 기준과 조건 명시 |
| 정규 N(0,1), N(2,.5) PDF 한 Figure | [normal_pdf.png](../outputs/normal_pdf.png) | 충족 |
| Bernoulli B(.3), B(.7) PMF 한 Figure | [bernoulli_pmf.png](../outputs/bernoulli_pmf.png) | 충족 |
| 직접 Softmax, 합 오차 ≤1e-6 | 큰 로짓 [1000,1001,1002], 합 0.9999999999999999 | 충족 |
| MSE-MLE 유도 | 독립 정규 잡음·양의 고정 분산 가정, NLL 상수 제거 | 충족 |
| Cross-Entropy-MLE 유도 | Bernoulli/BCE와 categorical/one-hot CE 모두 전개 | 충족 |

속도 기준의 ‘첫 도달’은 이후에도 계속 기준 이하라는 뜻이 아니다. 원형 함수에서 Momentum은 기준에 먼저 도달했지만, 100회 최종 손실은 GD가 더 작았다. Momentum이 언제나 빠르거나 더 부드럽다고 결론 내리지 않았다.

## 5. 보너스 분리와 상속

| PDF 4~5쪽 선택 과제 | 별도 파일·상속 | 결과 |
|---|---|---|
| Adam 및 GD/Momentum/Adam 속도 비교 | [bonus_optimizer.py](../src/bonus_optimizer.py), `Adam(Momentum)` | 같은 lr=.01의 타원: .01 첫 도달 194/78/1242회 |
| Hessian 기반 Newton 및 GD 비교 | 같은 보너스 파일, `NewtonMethod(VanillaGD)` | Hessian diag(2,20), Newton 1회에 원점 |
| 엔트로피/KL/CE 직접 구현 | [bonus_probability.py](../src/bonus_probability.py), `InformationTheory(ProbabilityLoss)` | H=.610864, KL=.183787, CE=.794651 nats, CE=H+KL |

보너스 실행·수식·해석은 [bonus_report.ipynb](../notebooks/bonus_report.ipynb)와 `bonus_` 접두사 PNG, `bonus_metrics.json`으로 분리했다. 필수 실행에서는 보너스 모듈을 불러오지 않는다. 같은 lr에서 Adam이 가장 느린 결과도 그대로 기록했다.

## 6. 제약조건 재검토

| PDF 5~6쪽 제약 | 검사 결과 |
|---|---|
| Python≥3.8 | conda py312, Python 3.12.2 |
| NumPy로 수학 구현 | 수치 구현은 NumPy만 사용 |
| Matplotlib/Seaborn은 시각화 전용 | Matplotlib만 시각화에 사용, Seaborn은 불필요하여 사용하지 않음 |
| eig 검증 전용 | `tests/test_core.py`, `scripts/run_experiments.py`의 비교 위치에서만 호출; `src/`에는 호출 없음 |
| AutoGrad 및 sklearn PCA/최적화 금지 | PyTorch/TensorFlow/JAX/sklearn import 없음 |
| seed=42 | 실험 스크립트와 세 노트북에 `np.random.seed(42)` 명시 |
| 64×64 이하 Grayscale | 공개 P2 원본을 전처리한 64×64 입력만 SVD에 사용 |
| PNG outputs/ 저장 | 필수 11개, 보너스 4개, 총 15개 |
| 모든 클래스·함수 Docstring | src/scripts/tests의 AST 검사에서 누락 0개 |
| 수식 주석/Markdown | 코드 Docstring, 노트북, 설명 문서에 구현 식 명시 |
| 라이브러리·버전 requirements | 별도 새 py312 프로세스에서 실제 버전을 읽고 고정 |

Jupyter 도구는 노트북 실행에, Markdown/BeautifulSoup은 사용자가 요청한 HTML 변환·검수에만 사용했다. 이 도구들로 수학 알고리즘을 대신 계산하지 않았다.

## 7. PDF의 모호함과 참고 예시 오류

1. **y_true 빈칸:** 3쪽은 값이 없지만 7쪽은 1이라고 명시한다. 그 값을 사용했다.
2. **lr≥.5 발산:** 원형 함수의 GD 식은 `θ_next=(1-2lr)θ`다. .5에서는 한 번에 0, 1에서는 크기가 일정한 진동, 1 초과에서는 발산이다. ‘.5 이상은 모두 발산’으로 설명하지 않고, 그 범위에 들어가는 1.1의 발산을 제시했다.
3. **64×64와 k=100:** 성분 수는 최대 64다. 요청 k=100을 받되 실제 64개를 사용하고 요청/유효 값을 함께 표시했다. 이미지 크기를 늘려 가이드 조건을 깨지 않았다.
4. **큰 k의 저장량:** k=50은 6450개, 유효 k=64는 8256개 인자를 저장하므로 원본 4096개 값보다 많다. 이 경우 저장량이 줄었다고 쓰지 않았다. k=10은 1290개다.
5. **정규분포의 .5:** 표준적인 N(μ,σ²) 규약을 명시했다. PDF는 분산/표준편차를 따로 설명하지 않으므로 해석을 숨기지 않았다.
6. **7쪽 역전파 숫자:** 고정 입력으로 재계산하면 z2=.6071551038, dz1[1]=-.0517335044다. 4자리 값은 .6072/-.0517이다. 참고 예시의 .6071/-.0513에 맞추어 계산을 왜곡하지 않았다.
7. **8쪽 결과 예시:** 초기점 (5,5), lr=.1의 GD는 100회 뒤 좌표 약 1.0185×10⁻⁹이다. 참고 좌표 (.08,.08)를 실제 100회 결과로 복사하지 않았다. 타원 lr=.05의 예시는 필수 파라미터가 아니며, 비교 실험은 같은 lr=.01로 실행했다.

## 8. TDD 기록과 작업 범위

필수 테스트를 먼저 작성했고 구현 파일이 없는 실패를 [core Red](../reports/tdd_core_red.txt)에 보존했다. 첫 구현 뒤 18개가 통과한 기록은 [core Green](../reports/tdd_core_green.txt)이다.

보너스 기준 테스트도 모듈 작성 전에 만들었지만 첫 실행은 폰트 캐시 준비와 겹쳐 구현 후에 완료되어 통과했다. 따라서 [그 첫 실행](../reports/tdd_bonus_initial.txt)을 Red 증거로 취급하지 않았다. 이후 확률 합 `1.000001`을 거부하는 테스트를 먼저 추가하고 실제 실패를 [bonus Red](../reports/tdd_bonus_red.txt)에 남겼다. `np.isclose`의 상대 허용오차를 제거한 후 [전체 27개 Green](../reports/tdd_all_green.txt)을 확인했다. 로그를 사후에 실패한 것처럼 바꾸지 않았다.

PDF 밖의 알고리즘·학습 프레임워크·데이터 분석 과제·서비스·배포 기능은 추가하지 않았다. TDD 테스트, 코드 설명 Markdown, Mermaid, diagram-design HTML, 재검토 문서는 사용자가 명시한 작업이다. 캐시·커널 설정·브라우저 검수 자료는 A2-1/.cache/에 모았다. 폴더별 `.gitignore`는 만들지 않았고 저장소 루트의 기존 `.cache`/`__pycache__`/`.ipynb_checkpoints` 규칙을 사용했다.

PDF의 GitHub Repository URL 제출은 코드·노트북·README가 포함된 저장소를 제출하는 절차다. 이 작업에서 원격 push나 제출은 수행하지 않았으며, 로컬 완료를 원격 제출 완료로 기록하지 않았다.

검토 결과, 구현 가능한 필수 기능의 누락과 금지 라이브러리 사용은 발견하지 못했다. 위 문서 해석·참고 수치 차이와 원격 제출 절차를 별도로 남겼다.

## 9. HTML의 도식·수식·링크 검수

[통합 설명 HTML](code_walkthrough.html)은 개념·코드 설명, README, 이 재검토 문서를 순서대로 포함한다. SVG 7개, MathML 수식 27개, 내장 PNG 15개가 들어 있다. [README HTML](../README.html)은 README 원문을 별도로 제공한다. Markdown의 문단·목록·표를 HTML 텍스트와 대조해 누락 0개를 확인했다.

diagram-design의 financial-services 프로필과 flowchart/UML/bar 유형 가이드를 적용했다. Mermaid의 작업 흐름 6노드/5관계, 순전파 6노드/5관계, 역전파 7노드/6관계, 상속 6클래스/4관계를 유지했다. 노드·관계의 병합/누락은 없다. UML에는 실제 코드의 대표 속성·메서드만 추가로 표시했다. 클래스 도식은 플러그인 추출기가 지원하지 않는 문법이어서 자동 import를 주장하지 않고 UML 가이드에 따라 직접 구성했다. 속도 막대는 보너스 JSON의 실제 값을 사용한 별도 설명 도식이다.

플러그인의 `verify-geometry.py`는 두 HTML에서 모두 finding 0개였다. `self_check.py`는 공개 이미지 출처를 가리키는 일반 `<a>` 링크를 `remote reference on <a>`로 보고했다. 출처를 삭제해 통과시키지 않고 이 예외를 남겼다. [산출물 검수](../reports/artifact_verification.json)에서 외부 실행 스크립트·스타일·이미지 요청이 없음을 별도로 확인했다.

[브라우저 검수](../reports/browser_verification.json)는 Chrome에서 두 파일을 1440px/390px 너비로 열고 수식·도식·내장 이미지·목차·문서 너비를 확인한 결과다. 외부 HTTP 요청과 JavaScript 오류는 0개였다. 좁은 화면에서는 큰 표·도식을 해당 영역 안에서 가로로 볼 수 있게 했으며 본문 전체가 화면 밖으로 밀리지 않는다. 설치 폰트가 없을 때 사용하는 로컬 폰트 대체도 HTML 하단에 명시했다.
