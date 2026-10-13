# A5-2 · PDF 필수 요구사항 재검토

2026-10-13에 이 폴더 8쪽 PDF와 소스·모델·실측 JSON·그림·README를 대조했다. 실행 시 데이터와 모델은 이 폴더의 사본만 사용한다.

| PDF 위치 | 필수 내용 | 실제 근거 | 판정 |
|---|---|---|---|
| 1–2쪽 | 군집→분류→SHAP 연결, 군집 통계/페르소나 | [analysis_clustering.py](../analysis_clustering.py), [analysis_shap.py](../analysis_shap.py), [군집](clustering.json), [README](../README.md) | 수행 |
| 2–3쪽 | 원본 finance CSV 동일 사용, 타겟 제외, 임의 컬럼/외부 병합 금지 | 입력 10,000×6, 원본 CSV SHA 4ddf83dd…fe1a2, [CustomerAnalysis](../src/analysis.py) | 준수 |
| 3–4쪽 | 스케일→KMeans, Elbow/Silhouette 선택, PCA2D·설명 분산 | K2..8, Silhouette 최대 K2=.136391, [K 선택](k_selection.png), [PCA](pca_clusters.png), PC합34.61% | 수행 |
| 4쪽 | 군집별 특징·페르소나·추천 전략 | README 2–3/6절, 군집 0:3931명 연체 경험군, 군집1:6069명 최근 연체 없음군 | 수행 |
| 2/4쪽 | sklearn Tree모델 + TreeExplainer, Summary PNG | [모델](../models/random_forest.joblib), [Global](shap_summary.png), [SHAP 결과](shap.json) | 수행 |
| 2/4쪽 | 승인·거절 개별 Force 또는 Waterfall 저장 | [승인](waterfall_approval.png), [거절](waterfall_rejection.png), README 5절 | 수행 |
| 2/4쪽 | 상위 변수 + 업무 의미 변수 Dependence PNG·2문장 이상 | [소득](dependence_annual_income.png), [연체](dependence_overdue_count_6m.png), [부채](dependence_debt_ratio.png), README 4절 각각 해석 | 수행 |
| 3쪽 권장 | 군집별 대표 고객 Local 해석 | [군집0](waterfall_cluster_0.png), [군집1](waterfall_cluster_1.png) | 수행 |
| 4/7쪽 | 그림과 업무 해석, 버전 txt, 군집→SHAP→README 순서 | [requirements.txt](../requirements.txt), README 실행 순서·각 그림의 설명 | 수행 |
| 4–5쪽 | Streamlit·대안 군집(선택) | [별도 상속](../src/bonus.py), [비교](bonus_comparison.json) | 필수와 분리 |
| 5–8쪽 | 동일 생성 데이터·허용 sklearn 모델, 예시와 실제 구분 | 외부 모델링 라이브러리 없음, 예시 K4를 실제 최적값으로 복사하지 않음 | 준수 |

PDF의 '거절 확률 5 이상'은 확률 범위 [0,1]과 모순이다. 실제 구현은 **0.5 이상**으로 정정하고 README에 이유를 명시했다. SHAP 덧셈 최대 오차 9.714e-15는 1e-7 이내이며, 기여도는 모델 출력 설명이지 인과적 효과나 실제 금융 정책의 정당성 증명이 아니다.

py312에서 `python -m pytest tests -q` 재실행 **5개 통과**. 원본 해시/타겟 제외, 표준화, K선택/PCA, SHAP 덧셈/판정 경계, 보너스 상속을 확인했다. SHAP·joblib의 기존 경고는 테스트 실패가 아니다. 이 재검토에서 필수 기능 누락은 발견하지 않았다.
