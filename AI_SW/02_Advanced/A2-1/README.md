# A2-1 · AI가 어떻게 학습하는지 수학으로 직접 풀어보기

NumPy로 행렬 변환·Power Iteration·SVD·중심차분·역전파·GD/Momentum·확률/손실 연결을 직접 구현한다.
미션 PDF 1~8쪽과 두 평가 목록을 대조하여 구현, 기호 유도, 수치 기준, 그림 연결을 보완했다.

## 바로 읽을 문서

학습과 설명은 **[docs/code_walkthrough.html](docs/code_walkthrough.html) 하나**에 통합했다.
개념·현실 예시 → 15개 항목의 도식·수식·실제 코드·결과 → 선택 과제 → 재현 방법 → PDF 대조 → 노트북 출력 → 실제 코드 전체 순서다.
코드 링크와 노트북 링크는 같은 HTML 안의 해당 줄·셀로 이동한다.

통합 HTML은 15개의 diagram-design 도식과 실험 PNG, 수치표, 노트북 실행 출력, 실제 코드 전체를 내장한다.
HTML을 더블클릭해 브라우저로 열 수 있다. 코드·원본 파일 링크는 A2-1 폴더 구조를 유지한다.
내장 이미지·SVG·CSS는 네트워크 없이 표시되며 외부 실행 스크립트가 없다.

## 구조와 실행

`src/`는 수학 구현, `scripts/`는 실험·비교·실행·문서 생성, `tests/`는 수학 검증,
`notebooks/`는 기호 유도와 실행 증거, `outputs/`는 PNG, `reports/`는 원본 수치와 검수 기록이다.
이미지 입력과 출처는 `data/`에 있다. [requirements.txt](requirements.txt)에 버전을 고정했다.
현재 검증 환경의 Python은 `/Users/oliverjoo/Dev/Anaconda/anaconda3/envs/py312/bin/python`이다.
같은 버전이 준비된 환경에서 A2-1을 작업 디렉토리로 사용한다.

```sh
python scripts/run_experiments.py --bonus > reports/experiment_run.txt
MPLCONFIGDIR=.cache/matplotlib python -m unittest discover -s tests -v > reports/test_revision.txt 2>&1
python scripts/run_notebooks.py --bonus > reports/notebook_execution.txt
python scripts/build_assessment.py
python scripts/verify_artifacts.py
```

처음 환경을 구성해야 한다면 requirements.txt의 패키지가 필요하다. 이번 보완에서는 이미 설치된 환경을 재사용했다.
브라우저 검수 명령과 검사 범위는 [통합 문서의 재현 방법](docs/code_walkthrough.html#reproduction)에 있다.

## 주요 실제 결과

| 실험 | 결과 |
| --- | --- |
| 행렬 면적 | (100,2) 점/100샘플; 세 변환 det·면적비≈1; 상대오차≤1% |
| 고유값 | A=[[4,1],[1,3]]; λ=4.618033988750; 20회; eig·벡터·잔차 PASS |
| SVD | (64,64), 요청10/50/100→유효10/50/64; k=50/64는 인자 값 수가 원본보다 많음 |
| 미분 | x², x=3, h=1e-5; 6.000000000039306; 절대오차3.93e-11≤1e-4; h 민감도도 표시 |
| 역전파 | 2→2→1, y=1; 11 체크포인트 shape+round(4) PASS; 전 파라미터 중심차분 검산 |
| 원형 GD | lr=.1,100회; 반경1.4404e-9≤PDF .1; 경로와 손실 PNG 첨부 |
| 발산 | 원형 .5 수렴/1 진동/1.1 발산; 추가 타원 .5에서 손실275→20250→3.6952e40 |
| 타원 비교 | 같은 lr=.01; 손실 .01 첫 도달 GD194/Momentum78, 이후 유지194/97 |
| 확률 | N(0,1)/N(2,.5) 및 B(.3)/B(.7) 그림·노트북 출력·정규화 검산 |
| Softmax | 최대값 shift·5입력, 합오차≤1e-6 및 유한확률 검사 PASS |
| MLE 연결 | Normal→MSE, Bernoulli→BCE, categorical→CE의 기호식·독립 우도 검산 PASS |

## 기호로 보는 MLE와 손실의 연결

독립 관측에서 L(θ)=∏ᵢp(yᵢ|xᵢ,θ). 로그는 증가 함수여서 argmax L=argmin(−log L)이다.
정규 잡음 εᵢ~N(0,σ²), 같은 양의 고정 분산이라면

```text
log p = −(1/2)log(2πσ²) − (yᵢ−fθ(xᵢ))²/(2σ²)
NLL = n/2 log(2πσ²) + Σᵢ(yᵢ−fθ(xᵢ))²/(2σ²)
    = C + n×MSE/(2σ²)
```

θ에 무관한 C와 양의 고정 계수를 제거하면 MSE와 같은 최소점을 얻는다.
베르누이 p(yᵢ)=qᵢ^yᵢ(1−qᵢ)^(1−yᵢ)에 대해서는

```text
NLL = −log ∏ᵢqᵢ^yᵢ(1−qᵢ)^(1−yᵢ)
    = −Σᵢ[yᵢlog qᵢ+(1−yᵢ)log(1−qᵢ)] = BCE 합
```

카테고리 one-hot 정답의 p(yᵢ)=∏c qᵢc^yᵢc에 대해서는

```text
NLL = −log ∏ᵢ∏c qᵢc^yᵢc = −ΣᵢΣc yᵢc log qᵢc = CE 합
```

고정 n으로 나눈 평균 BCE/CE도 같은 최소점을 갖는다. 상세 수식·생활 예시·코드 검산은
[확률 손실 노트북](notebooks/probability_loss.ipynb)과 [통합 문서의 실행 출력](docs/code_walkthrough.html#executed-notebooks)에 있다.
“같은 손실 숫자”와 “같은 최소화 파라미터”를 구분한다.

## 출력과 검증 근거

- [bernoulli_pmf.png](outputs/bernoulli_pmf.png)
- [bonus_adam_loss.png](outputs/bonus_adam_loss.png)
- [bonus_adam_paths.png](outputs/bonus_adam_paths.png)
- [bonus_newton_loss.png](outputs/bonus_newton_loss.png)
- [bonus_newton_paths.png](outputs/bonus_newton_paths.png)
- [circle_loss.png](outputs/circle_loss.png)
- [circle_paths.png](outputs/circle_paths.png)
- [derivative_sensitivity.png](outputs/derivative_sensitivity.png)
- [ellipse_learning_rate_loss.png](outputs/ellipse_learning_rate_loss.png)
- [ellipse_loss.png](outputs/ellipse_loss.png)
- [ellipse_paths.png](outputs/ellipse_paths.png)
- [gradient_contours.png](outputs/gradient_contours.png)
- [learning_rate_loss.png](outputs/learning_rate_loss.png)
- [learning_rate_paths.png](outputs/learning_rate_paths.png)
- [matrix_transformations.png](outputs/matrix_transformations.png)
- [normal_pdf.png](outputs/normal_pdf.png)
- [svd_reconstructions.png](outputs/svd_reconstructions.png)


[필수 수치](reports/metrics.json), [전체 실행](reports/experiment_run.txt), [32개 테스트](reports/test_revision.txt),
[4개 노트북 실행](reports/notebook_execution.txt), [우도 검산](reports/loss_likelihood_checks.json),
[산출물 검수](reports/artifact_verification.json), [브라우저 검수](reports/browser_verification.json)를 연결한다.
선택 과제는 [bonus_report.ipynb](notebooks/bonus_report.ipynb)와 [bonus_metrics.json](reports/bonus_metrics.json)으로 분리한다.
공개 이미지 출처·전처리·사용 범위는 [SOURCE.md](data/SOURCE.md)를 확인한다.

## PDF 해석과 제한

반경 요구는 .1, k=100의 유효값은64, 원형 .5는 정확한 수렴이다. 타원 .5는 실제 발산한다.
PDF의 y_true 빈칸과 참고 숫자 오류는 원래 입력·수식으로 보완하며 결과를 왜곡하지 않는다.
Momentum의 이점은 명시한 함수·lr·임계값 아래의 결과다. 수학 구현은 NumPy만 사용하고 eig는 비교 검증 전용이다.
과거 TDD·검증 기록은 그대로 보존하고 현재 실행 근거를 새 보고서에 기록한다. 원격 GitHub 제출은 이 작업 범위에 포함하지 않는다.
