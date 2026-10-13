# A1-1 · PDF 필수 요구사항 재검토

2026-10-13에 이 폴더의 7쪽 PDF, 실제 실행된 필수 노트북, 기본 소스, 데이터, 그림, 테스트를 대조했다. 평가 질문지의 확장 가정은 PDF 필수 기능으로 추가하지 않았다.

| PDF 위치 | 필수 내용 | 실제 제출 근거 | 판정 |
|---|---|---|---|
| 1–2쪽 | OOP 통합 처리, EDA, 4개 이상 RFM 그룹 | [DataAnalyzer](../src/pipeline.py), [실행 노트북](../notebooks/analysis_report.ipynb) | 구현·실행 |
| 2쪽 최종 결과물 | pipeline.py, analysis_report.ipynb, README | [기본 소스](../src/pipeline.py), [분석 보고서](../notebooks/analysis_report.ipynb), [README](../README.md) | 존재 |
| 2–3쪽 | 1,000행·8열 이상, 3가지 데이터 유형, info/describe/head 및 수치 해석 | 22,488행·10열, 수치·범주·날짜·텍스트; 노트북 1절 | 수행 |
| 3쪽 | customer_id/order_date/amount, 최종 거래일 기준일 | 노트북 6절, calculate_rfm; 기준일 2011-12-09 | 수행 |
| 3쪽 | load_data/handle_missing_values/detect_outliers/calculate_rfm, 인자화 | DataAnalyzer의 실제 4개 메서드, mean/median·threshold·기준일 인자 | 수행 |
| 3쪽 | NumPy 이미지 mean/std 벡터화, 텍스트 파생변수 | engineer_features, 이미지 (2601,8,8,3), 단어 수; 노트북 3절 | 수행 |
| 3쪽 | 그룹별 결측 대치, 직접 IQR, 처리 전후 분포 | 상품별 가격 대치 1,124→0건; IQR 1,971행, [박스플롯](figures/02_boxplot.png) | 수행 |
| 3쪽 | 평균·중앙값·표준편차·사분위수, 2쌍 이상 상관과 해석 | [요약 통계](summary_statistics.csv), [상관행렬](correlations.csv), 노트북 5절 | 수행 |
| 3–4쪽 | 제목·축 레이블이 있는 6종 차트 | [히스토그램](figures/01_histogram.png), [박스](figures/02_boxplot.png), [막대](figures/03_bar.png), [히트맵](figures/04_heatmap.png), [산점도](figures/05_scatter.png), [라인](figures/06_line.png) | 수행 |
| 4쪽 | RFM 점수·4개 그룹 특성 | [RFM](rfm.csv), [그룹 통계](segments.csv); Churned86/Loyal90/New6/VIP58 | 수행 |
| 4쪽 | README 인사이트 3개 이상: 근거·대상/실행/효과·추가 데이터/반증 | README 8절의 네 그룹 전략; 캠페인 실적은 미측정임을 구분 | 수행 |
| 5쪽 | 허용 라이브러리, 출처, NumPy 이미지 처리 | [출처·변환](../data/SOURCE.md), 기본 소스 NumPy/Pandas, 그림 Matplotlib/Seaborn | 준수 |
| 6–7쪽 | 참고 Class·표·인사이트 예시 | 참고 구조에 맞추되 예시 숫자를 실제 성과로 복사하지 않음 | 구분 |

이미지는 원본 상품 사진이 아닌 **명시적 보조 NumPy 배열**이다. UCI 원본에 이미지·가입일이 없어 실제 사진 분석·가입 코호트를 수행했다고 주장하지 않는다. PDF는 이미지 배열의 mean/std 계산을 요구하며 해당 연산은 실제로 수행했다. 가입 코호트·고급 이미지 피처·Plotly는 선택 과제이며 필수 충족 판단과 분리했다.

py312에서 `python -m unittest discover -s tests -v`를 재실행해 **18개 통과**했다. 노트북의 실행 출력, 여섯 차트, 표의 수치와 현재 입력을 대조했다. GitHub URL 제출·새 커밋·푸시는 이번 재검토 요청에 포함하지 않았다.
