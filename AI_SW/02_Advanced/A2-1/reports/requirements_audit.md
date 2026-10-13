# A2-1 PDF 필수 요구사항 재검증

## 검증 범위와 기준

기준은 [A2-1_미션 - AI 심화 학습_AI가 어떻게 학습.pdf](../A2-1_%E1%84%86%E1%85%B5%E1%84%89%E1%85%A7%E1%86%AB%20-%20AI%20%E1%84%89%E1%85%B5%E1%86%B7%E1%84%92%E1%85%AA%20%E1%84%92%E1%85%A1%E1%86%A8%E1%84%89%E1%85%B3%E1%86%B8_AI%E1%84%80%E1%85%A1%20%E1%84%8B%E1%85%A5%E1%84%84%E1%85%A5%E1%87%82%E1%84%80%E1%85%A6%20%E1%84%92%E1%85%A1%E1%86%A8%E1%84%89%E1%85%B3%E1%86%B8.pdf) 전체입니다. 이 미션 폴더의 실제 소스·실행 결과·제출 파일만 확인했습니다. 평가 질문지의 가정·확장 질문을 새로운 PDF 필수 구현으로 취급하지 않았고, 선택 보너스를 필수 결과와 섞지 않았습니다.

현재 py312 경로: `/Users/oliverjoo/Dev/Anaconda/anaconda3/envs/py312/bin/python`. PDF SHA256: `0c29988b6d406c64de096a3955295230c4010fde78aade1861b956bf301ae5ea`.

## 요구사항별 근거

| PDF 쪽 | 필수 조건 | 실제 코드·파일·결과 | 판정 |
| --- | --- | --- | --- |
| 1~2 | linear_algebra/calculus/optimizer 및 필수 두 노트북 | [선형대수](../src/linear_algebra.py), [미적분](../src/calculus.py), [최적화](../src/optimizer.py), [역전파 노트북](../notebooks/backprop_derivation.ipynb), [확률 노트북](../notebooks/probability_loss.ipynb) | 충족 |
| 3 | 단위 원 회전·S(2,.5)·전단 전후 Figure | [구현](../src/linear_algebra.py), [세 변환 PNG](../outputs/matrix_transformations.png) | 충족 |
| 3 | det와 면적비 상대오차≤1% | [metrics.area](metrics.json),100×2 좌표·오차0% | 충족 |
| 3 | 직접 PowerIteration·eig 기준 오차≤5% | [구현](../src/linear_algebra.py), [비교 전용 eig](../scripts/assessment.py), [행렬/고유쌍/잔차](metrics.json) | 충족 |
| 3,5 | 64×64 이하 공개 grayscale의 SVD k10/50/100 비교 | [이미지 출처](../data/SOURCE.md), [복원 PNG](../outputs/svd_reconstructions.png), effective k10/50/64 | 충족 |
| 3 | x²,x3 수치미분과 해석값6 오차≤1e−4 | [구현](../src/calculus.py), [오차/h 민감도](metrics.json), [그림](../outputs/derivative_sensitivity.png) | 충족 |
| 3 | f=x²+y² 등고선과 수직 Gradient 화살표 | [구현](../src/calculus.py), [그림](../outputs/gradient_contours.png) | 충족 |
| 3~4 | 2→2→1 고정 예제의 순·역전파 수식·shape·손계산 | [실행 노트북](../notebooks/backprop_derivation.ipynb), [NumPy](../src/backprop.py) | 충족 |
| 4 | 손계산과 NumPy의 소수4자리 일치 | [11체크포인트 비교](metrics.json), [독립 비교 상수](../scripts/assessment.py) | 충족 |
| 4 | 원형GD lr.1 100회 반경.1 이내·점선 등고선 경로 | [원형 경로](../outputs/circle_paths.png), [손실](../outputs/circle_loss.png), 실제반경1.4404e−9 | 충족 |
| 4 | lr≥.5 범위의 발산 경로 | [원형 lr1.1 발산/1진동/.5수렴](../outputs/learning_rate_paths.png), [타원 lr.5 발산](../outputs/ellipse_learning_rate_loss.png) | 수학적 경계 구분하여 실측 |
| 4 | Momentum beta.9 구현·GD와 한 Figure 비교 | [Momentum](../src/optimizer.py), [원형 비교](../outputs/circle_paths.png), [타원 비교](../outputs/ellipse_paths.png) | 충족 |
| 4 | 타원 f=x²+10y² 두 옵티마이저 경로 비교 | [손실](../outputs/ellipse_loss.png), [경로](../outputs/ellipse_paths.png), 동일lr.01/200회 | 충족 |
| 4 | 정규PDF2종·베르누이PMF2종 한 Figure씩 | [정규](../outputs/normal_pdf.png), [베르누이](../outputs/bernoulli_pmf.png), [실행 노트북](../notebooks/probability_loss.ipynb) | 충족 |
| 4 | Softmax 합오차≤1e−6 | [안정적 구현](../src/probability.py), [5입력 실제검증](metrics.json) | 충족 |
| 4 | MSE-MLE·BCE/CE-MLE 기호식 유도 | [확률 노트북](../notebooks/probability_loss.ipynb), [README 기호 유도](../README.md), [독립 PDF/PMF 검산](loss_likelihood_checks.json) | 충족 |
| 5 | seed42·outputs PNG 저장·requirements 버전 | [실험 실행](../scripts/run_experiments.py), [requirements](../requirements.txt), [산출물 검사](artifact_verification.json) | 충족 |
| 6 | 금지 자동미분/PCA/최적화 라이브러리 미사용·eig 비교전용 | [AST 검증 결과](artifact_verification.json): forbidden_imports=[], eig는assessment/tests에만 존재 | 충족 |
| 6 | 모든 함수/클래스 docstring·수식·환경명시 | [검수](artifact_verification.json): missing_docstrings=[], [소스](../src/linear_algebra.py) 및 실행노트북 확인 | 충족 |

## 실제 확인한 결과

- [현재32개 unittest 재실행](pdf_audit_tests.txt): PASS.
- [실험 재실행](pdf_audit_experiments.txt): 기존 필수·선택 결과 재현.
- 고유값오차 8.500908881654e-12%; 중심차분오차 3.930633596383e-11; 손계산11항목4자리비교PASS.
- 필수 두 노트북·수학 실험·기존 선택 노트북을 py312 커널로 다시 실행하고 출력·execution_count·오류 없음을 검수했습니다.
- [이전 산출물 검수 실패](pdf_audit_artifacts_before.txt)→[현재 검수 통과](pdf_audit_artifacts_after.txt): 옛 검수기가 삭제된 전체 코드 부록과 docs 단일 파일만 가정하던 문제를 현재 실제 파일 링크·짧은 발췌·추가 질문지 형식으로 수정했습니다. 수학 알고리즘을 바꾸거나 조건을 낮추지 않았습니다.

## 해석과 제출 범위

- 원형 f=x²+y²는0<lr<1에서수렴하므로.5를발산이라고 꾸밀수없습니다. lr≥.5범위의1.1실제발산과타원.5발산을보이고.5안정/1진동을명시합니다.
- 64×64 이미지에는 최대64개 성분만 있어 요청k100은유효k64입니다. k50/64는인자수기준저장압축이아님을명시합니다.
- PDF 참고 예시의 손계산 일부 숫자 오류와 y_true 빈칸은 실제 고정 입력·BCE 수식·예시 정답1로 검산했습니다.
- 필수 노트북은 Git에서 제외되는 docs와 분리되어 있으며, MLE 유도는 README에도 있습니다. 보조 HTML의29질답과15기존항목을보존했습니다.

필수 코드·보고서·수치·그래프는 이 미션 폴더 및 하위 reports/figures/outputs/notebooks에 있습니다. docs의 학습 HTML은 보조 설명이며 Git에서 docs를 제외하더라도 필수 제출물을 확인할 수 있어야 합니다. 실제 GitHub 제출은 로컬 파일 생성과 별개이며 이번 작업에서 커밋·푸시는 수행하지 않았습니다.
