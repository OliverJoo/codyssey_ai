"""측정 JSON과 현재 코드로 README/단일 학습 문서를 재생성한다."""
import ast
import hashlib
import json
from html import escape
from pathlib import Path
import sys
import html_tools as h

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'reports/clustering.json').read_text())
S=json.loads((ROOT/'reports/shap.json').read_text())
B=json.loads((ROOT/'reports/bonus_comparison.json').read_text())

def location(file,symbol):
    tree=ast.parse((ROOT/file).read_text())
    return next(node.lineno for node in ast.walk(tree) if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name==symbol)

def code(file,symbol):
    line=location(file,symbol)
    return f'[{file}:{line}](../{file}#L{line})'

def image(name,caption):
    return f'![{caption}](../reports/{name})\n'

CHAPTERS=[
('01','1. 입력·정답·예측을 먼저 구분하기','src/analysis.py','__init__',
 '입력은 예측 시 알고 있는 고객 정보이고 타겟은 맞히려는 정답이다. CSV에는 나이, 연 소득, 소비 점수, 부채비율, 카드 수, 최근 6개월 연체 횟수의 6개 입력과 신용 점수·연체 여부의 2개 타겟이 있다. 군집화는 정답 없이 비슷한 입력을 묶기 때문에 두 타겟을 사용하지 않는다. 과거 연체 횟수는 입력이고 예측 대상 연체 여부는 타겟이라는 시간적 의미도 구분한다.',
 '은행 직원이 상담 전 볼 수 있는 소득 5,000만원과 과거 연체 0회를 고객 카드에 적는 장면을 생각하자. ① 카드에 입력 6개를 적는다. ② 미래 연체 여부가 적힌 정답 칸을 가린다. ③ 비슷한 카드를 묶고 별도로 학습된 모델이 미래 위험을 계산한다. 정답을 군집 거리 계산에 넣으면 위험군을 발견한 것처럼 보이지만 이미 답을 사용한 결과다.',
 '코드는 원본 8개 컬럼의 순서까지 검사한 후 FEATURES만 복사한다. 원본 CSV를 재생성하거나 고객 데이터에 군집 컬럼을 붙이지 않는다. 군집 번호는 별도 NumPy 배열이고 보고서는 별도 JSON이다. CSV 10,000행의 SHA-256을 기록해 이전 미션에서 넘어온 원본이 변하지 않았음을 확인한다.',
 '상담 대상 분류, 상품 추천 그룹 탐색에 쓸 수 있다. 실제 서비스에서는 과거 입력과 미래 타겟의 관측 시점을 명확히 해야 한다. 이 데이터는 PDF 생성 규칙의 가상 고객이므로 실제 은행 고객으로 해석하면 안 된다.',
 'X ∈ ℝ^(10000×6), y ∈ {0,1}^10000'),
('02','2. 표준화로 서로 다른 단위의 거리를 맞추기','src/analysis.py','scaled',
 '유클리드 거리는 두 고객의 특성별 차이를 제곱해서 합한 뒤 제곱근을 취한다. 만원 단위 소득과 0~1 부채비율을 그대로 넣으면 큰 숫자인 소득이 대부분의 거리를 결정한다. 표준화 z=(x−평균)/표준편차는 각 특성을 평균 0, 표준편차 1로 바꾸어 단위의 지배를 줄인다. 모든 특성이 동등하게 유용하다는 보장은 아니다.',
 '고객 A 소득 4,000만원·부채 .2, B 소득 6,000만원·부채 .8을 비교하자. ① 원래 소득 차이 2,000, 부채 차이 .6을 구한다. ② 평균 소득 5,000·표준편차 2,000이면 z 소득은 −.5와 .5가 된다. ③ 부채 평균 .5·표준편차 .3이면 z 부채는 −1과 1이 된다. 표준화 후 차이는 1과 2라 부채 차이가 사라지지 않는다. 숫자는 원리 설명용이며 실제 평균·표준편차는 CSV에서 fit한다.',
 'scaled는 StandardScaler.fit_transform(self.features)를 사용한다. 테스트는 실제 10,000×6 배열의 열 평균이 0, 열 표준편차가 1인지 허용오차 1e-12로 검사한다. 군집화 scaler와 RF 모델의 기존 prepare 단계 scaler는 별도 목적이므로 서로 바꾸지 않는다.',
 '소득·나이·횟수처럼 단위가 섞인 고객 분석에 적합하다. 모든 고객을 탐색하는 비지도 분석에는 전체 데이터 표준화를 사용하지만 미래 고객에 적용할 때는 fit된 scaler와 군집 모델을 재사용해야 한다.',
 'zⱼ=(xⱼ−μⱼ)/σⱼ ; d(x,c)=√Σⱼ(xⱼ−cⱼ)²'),
('03','3. K-Means와 K 선택을 순서대로 이해하기','src/analysis.py','cluster',
 'K-Means는 K개 중심을 정하고 가까운 중심에 고객을 배정한 뒤 각 그룹 평균으로 중심을 갱신한다. Inertia는 중심까지의 제곱 거리 합이어서 K가 커지면 대체로 줄어든다. Elbow는 감소 폭이 완만해지는 지점을 찾는 보조 기준이다. Silhouette는 같은 군집 거리 a와 가장 가까운 다른 군집 거리 b를 비교하는 −1~1 점수다. 1에 가까우면 분리가 좋고 0 근처면 경계가 겹친다.',
 '점심 메뉴를 고르는 고객 6명을 두 테이블로 나누는 장면이다. ① 초기 중심 두 명을 뽑는다. ② 각 고객이 더 비슷한 테이블에 앉는다. ③ 테이블의 평균 취향으로 중심을 갱신하고 이동이 멈출 때까지 반복한다. K=6이면 한 명씩 앉아 거리 합이 0이지만 유용한 그룹 설명은 사라진다. 그래서 거리 합만 최소화하지 않고 분리도와 설명 가능성을 같이 본다.',
 '실제 코드는 K=2~8, seed=42, n_init=10을 고정한다. Silhouette는 비용을 줄이기 위해 동일 seed의 1,500명 표본을 사용한다. 최댓값이 K=2이고 Elbow 곡선에는 뚜렷한 급격한 꺾임이 없어 K=2의 확실성을 과장하지 않는다. 후보 범위와 표본을 바꾸면 결과가 달라질 수 있다.',
 '고객을 몇 팀으로 운영할지 초기 가설을 세우는 데 유용하다. K는 실제 고객 유형 수의 정답이 아니며 구형·비슷한 밀도 군집에 유리한 알고리즘 특성 때문에 업무별 검증이 필요하다.',
 'J=Σᵢ ‖zᵢ−c(labelᵢ)‖² ; sᵢ=(bᵢ−aᵢ)/max(aᵢ,bᵢ)'),
('04','4. PCA 그림과 원본 특성을 혼동하지 않기','analysis_clustering.py','run',
 'PCA는 표준화된 6차원 데이터를 분산이 큰 방향의 축으로 회전하고 일부 축을 남기는 차원 축소다. PC1은 나이나 소득 한 가지가 아니라 6개 특성을 가중 합한 새로운 좌표이다. 설명된 분산 비율은 그 축이 원본 변동 중 얼마나 남겼는지를 뜻하고 분류 정확도가 아니다. 군집은 6차원에서 만들고 2차원 그림은 보여주기 위해서만 사용한다.',
 '입체 조각을 종이에 사진 찍는 상황이다. ① 3차원 조각을 특정 방향에서 본다. ② 2차원 사진에 앞뒤 차이가 겹쳐 보일 수 있다. ③ 사진에서 가까워 보인다고 실제 공간에서도 가깝다고 단정하지 않는다. 이번 PCA도 6차원에서 두 축만 남겨 전체 분산 약 34.61%를 보이므로 보이지 않는 방향의 정보가 많다.',
 'analysis_clustering은 KMeans 결과 labels로 색을 정하고 PCA 좌표를 scatter한다. PC1 17.47%, PC2 17.13%, 합 34.61%를 축과 제목에 직접 표시한다. clustering.json에는 6개 입력별 PCA loading도 기록하여 PC를 단일 금융 특성처럼 잘못 부르는 것을 방지한다.',
 '군집의 겹침과 이상한 점을 탐색하는 시각화에 사용할 수 있다. 군집 이름과 업무 전략은 이 그림의 위치가 아닌 원본 단위 통계에서 결정한다.',
 'PCₖ=z·vₖ ; EVRₖ=λₖ/Σⱼλⱼ'),
('05','5. 통계에서 페르소나를 만들고 대표 고객 고르기','src/analysis.py','cluster',
 '페르소나는 군집의 관측 통계를 사람이 이해할 수 있는 설명으로 바꾼 가설이다. 평균이 높다는 이유만으로 VIP나 위험군이라고 이름 붙이면 근거가 부족할 수 있다. 대표 고객은 표준화 공간에서 군집 중심과 가장 가까운 실제 행으로 정한다. 가상의 평균 고객을 생성하지 않고 실제 입력 행을 쓰기 때문에 Local SHAP과 직접 연결할 수 있다.',
 '상담 팀장에게 군집 0의 소득과 나이가 군집 1과 거의 같지만 과거 연체 횟수 평균이 1.287 대 0이라고 보고하는 상황이다. ① 차이가 큰 실제 통계를 찾는다. ② 군집 0을 과거 연체 경험군, 1을 최근 연체 이력 없음군이라 부른다. ③ 각각 중심에 가까운 고객 6225·2707번을 확인한다. 대표 둘 모두 승인이라는 결과는 과거 경험군 전체를 자동 거절하면 안 된다는 점을 보여준다.',
 '각 군집의 행 수와 입력 6개 평균을 원본 단위로 계산한다. indices를 이용해 전체 CSV 행 번호를 보존하고 중심까지 거리 argmin으로 대표를 선택한다. 번호는 0부터 시작하는 데이터 행 인덱스이며 실제 개인 식별번호가 아니다.',
 '군집별 상담 메시지, 자동 결제 안내, 추가 확인 항목을 정하는 데 쓸 수 있다. 군집 평균을 한 고객의 속성으로 적용하는 생태학적 오류와 실제로 측정하지 않은 과소비·재산·장기 거래 추정을 피한다.',
 '대표 행=argminᵢ∈cluster ‖zᵢ−c‖₂'),
('06','6. 기존 모델과 예측 확률을 안전하게 연결하기','src/analysis.py','probabilities',
 '지도 학습 모델은 입력을 받아 타겟의 확률을 예측한다. 기존 Random Forest Pipeline은 prepare 전처리와 model 분류기를 포함한다. 본 미션은 그 모델을 새로 학습하지 않고 독립 폴더에 복사된 모델을 로드한다. predict_proba의 클래스 1 확률을 연체 위험으로 해석하고 교육용 임계값 .5 이상을 거절, 미만을 승인으로 정의한다.',
 '한 고객의 연체 확률이 .7이면 70%라는 출력이다. ① 입력 6개를 모델이 학습할 때와 같은 순서로 만든다. ② Pipeline이 같은 imputer·scaler를 적용한다. ③ RF가 확률 .7을 출력하면 교육용 규칙상 거절이다. PDF의 확률 5는 500%라 불가능하므로 .5로 정정한 해석을 공개한다. 승인 확률은 1−연체 확률이며 숫자 .7을 승인 확률로 바꿔 읽지 않는다.',
 'probabilities는 Pipeline 전체 predict_proba를 사용하고 SHAP 입력만 prepare.transform 결과를 사용한다. TreeExplainer는 Pipeline 전체가 아닌 RF tree에 적용해야 한다. 테스트는 probability=5 입력을 ValueError로 거부하고 .5 경계를 확인한다.',
 '상담원이 모델 출력 의미를 확인할 때 쓴다. class_weight=balanced로 학습한 모델 확률은 실제 모집단 연체율과 다를 수 있으므로 보정 없는 확률을 실거래 의사결정 근거로 단정하지 않는다. 이번 SHAP 표본은 성능 평가용 독립 Test가 아니라 모델 설명용 표본이다.',
 'p=P(is_overdue=1|x) ; 승인 확률=1−p ; 거절⇔p≥0.5'),
('07','7. SHAP을 기준값과 기여도의 덧셈으로 이해하기','src/analysis.py','explain',
 'SHAP은 여러 특성 조합에서 예측 변화의 몫을 나누는 Shapley 값 기반 설명이다. 기준값은 explainer가 정의한 배경에서의 출력이고 각 변수 기여 φ가 더해져 해당 고객의 출력이 된다. 양수는 연체 확률을 기준보다 높이고 음수는 낮춘다. 기여도는 원인이 아니라 이 모델 내부에서 입력이 출력과 연결되는 설명이다.',
 '회의에서 최종 위험 확률을 계산서로 설명하는 상황이다. ① 기준 확률 .4989에서 시작한다. ② 거절 사례의 소득 기여 +.2846, 부채 +.1385, 과거 연체 +.0792를 더한다. ③ 나이·소비·카드 기여도 합해 .9830에 도달한다. 카드 기여 −.0243은 이 사례에서는 위험을 약간 낮추지만 카드 수를 바꾸면 실제 미래 연체가 줄어든다는 인과 결론은 아니다.',
 'RF의 shap 값은 (행,특성,클래스) 형태다. 코드가 [:,:,1]과 base_values[:,1]을 선택해 연체 클래스만 설명한다. data에는 전처리 후 z값 대신 원본 입력을 넣어 그래프의 소득이 만원으로 읽히게 한다. 같은 순서·6개 수치 컬럼만 있는 기존 전처리이므로 SHAP 기여도 열과 원본 특성이 정확히 대응한다. 1,000개 실제 표본 모두 baseline+sum=probability 오차 <1e-7을 assert한다.',
 '특정 예측의 숫자 근거를 설명할 때 유용하다. TreeExplainer 기본 tree_path_dependent 배경과 class-balanced RF 때문에 기준값 .4989가 CSV 실제 연체율이라고 해석하면 안 된다.',
 'f(x)=E[f(X)]+Σⱼφⱼ ; φⱼ=ΣS⊆F∖{j} |S|!(M−|S|−1)!/M!·[f(S∪{j})−f(S)]'),
('08','8. Global Summary와 방향성을 함께 읽기','analysis_shap.py','run',
 'Global 해석은 여러 고객의 기여도를 모아 모델이 어떤 특성에 의존하는지 본다. 평균 절대 SHAP은 영향 크기를 순위로 만들지만 부호를 제거하므로 위험을 올리는 방향은 따로 확인해야 한다. Summary beeswarm은 각 점을 고객 한 명으로 보여주고 가로축은 SHAP, 색은 입력 값의 높낮이이다.',
 '영업팀이 중요 변수 1위를 보고 소득이 높을수록 위험이 높다고 오해하는 상황이다. ① 소득 평균 절대 기여 .2472는 영향 크기라는 것을 확인한다. ② 낮은 소득 사분위 평균 SHAP +.1755, 높은 소득 사분위 −.3837을 비교한다. ③ 이번 모델은 낮은 소득에서 연체 확률을 높이는 경향이라고 설명한다. 소득 구간별 다른 입력 분포가 섞이므로 단조 인과 효과라고 말하지 않는다.',
 'sample 1,000행 seed42, mean(abs(values),axis=0) 순위를 저장한다. 상위 3개는 연 소득·6개월 연체 횟수·부채비율이다. 각 특성의 낮은/높은 사분위 평균 SHAP을 JSON에 저장해 그래프와 문장 해석의 근거를 함께 남긴다. scipy나 외부 트리 모델 없이 sklearn RF+SHAP을 사용한다.',
 '모델 점검 우선순위, 상담 설명 항목, 입력 품질 관리 대상을 정할 때 쓴다. 전체 영향 순위가 모든 고객의 개별 영향 순위와 일치하지는 않는다.',
 '중요도ⱼ=(1/n)Σᵢ|φᵢⱼ|'),
('09','9. Waterfall로 승인·거절을 실제 숫자로 설명하기','analysis_shap.py','run',
 'Local 해석은 고객 한 명의 출력에만 초점을 맞춘다. Waterfall은 기준값에서 시작해서 특성별 양수·음수 기여를 누적하며 최종 예측에 도달한다. 승인·거절 사례는 관측 타겟이 아니라 모델 예측 확률 기준으로 골라야 요구사항의 예측 이유를 설명할 수 있다.',
 '① 전체 고객 중 가장 낮은 확률 행 6을 승인 예로, 가장 높은 행 576을 거절 예로 고른다. ② 승인 고객은 연체 0회·부채 .18이 확률을 각각 −.1699·−.1642 낮춘다. ③ 거절 고객은 소득 2,071만원·부채 .93이 +.2846·+.1385를 더한다. 두 사례는 설명을 선명하게 하는 극단 사례라 보통 고객의 위험분포를 대표한다고 말하지 않는다.',
 'argmin·argmax로 선택 기준을 재현 가능하게 만들고 각 원본 입력, 실제 타겟, 예측, 기여도를 shap.json에 저장한다. Waterfall PNG 네 장은 승인·거절 2건과 군집 대표 2건이다. 실제 is_overdue는 참고로만 표시하고 선정에 사용하지 않는다.',
 '상담원 교육 및 결과 검토에 활용할 수 있다. 실제 고객에게 거절 이유를 제공하려면 모델 설명과 별도로 정책·법적 절차·공정성 검토가 필요하며 이 과제는 교육용 수치 해석만 수행한다.',
 '0.498882+Σφ(승인)=0.000000 ; 0.498882+Σφ(거절)=0.983036'),
('10','10. Dependence를 관측 관계로 읽고 제언 연결하기','analysis_shap.py','run',
 'Dependence는 x축에 한 특성의 실제 값, y축에 해당 특성의 SHAP을 놓는 그래프다. 같은 x값에서 높이가 다르면 다른 입력과의 상호작용이나 트리 분기 때문에 기여가 달라질 수 있다. 곡선은 고객 입력을 강제로 바꾼 실험 결과도 아니고 예측 확률 자체도 아니다.',
 '부채비율 .8 고객들이 점 여러 개로 나타나는 장면이다. ① x=.8 주변의 기여 분포를 살핀다. ② 낮은 부채 사분위 평균 −.1898과 높은 사분위 +.1052를 비교한다. ③ 고부채 고객에게 상환 일정 확인 상담을 제안하되 상담이 실제 연체를 줄이는지는 별도 결과 측정으로 검증한다. 개별 고객 기여는 전체 사분위 평균과 다를 수 있다.',
 '선정 규칙은 Summary 상위 두 변수 소득·과거 연체와 비즈니스 의미가 큰 부채비율이며 중복을 제거한다. 세 PNG를 저장하고 각 그래프마다 관측 방향과 실무 해석을 2문장 이상 README에 남긴다. Dependence 색 상호작용 추정 대신 interaction_index=None으로 기본 관계를 분명히 보여준다.',
 '상담 항목을 구체화하고 이상한 비단조 구간을 확인할 때 쓴다. 소득이 생성 신용 점수와 타겟 규칙에 연결된 합성 데이터라는 점을 감안해 현실의 대출 정책으로 옮기지 않는다.',
 'Dependenceⱼ={(xᵢⱼ,φᵢⱼ)}ᵢ₌₁ⁿ'),
('11','11. 상속 보너스: 계층 군집과 실제 입력 대시보드','src/bonus.py','HierarchicalAnalysis',
 '계층 군집은 가까운 그룹을 순차적으로 합쳐 트리를 만든다. Ward 연결은 합칠 때 군집 내 제곱 거리 증가를 최소화하며 K-Means와 같은 K라도 그룹이 다를 수 있다. ARI는 두 배정의 일치도를 우연 수준을 보정해 비교한다. Streamlit은 Python 입력 위젯으로 웹 화면을 만들고 기존 예측·설명 로직을 호출한다.',
 '① 동일 표준화 고객 10,000명에 Ward K=2를 적용한다. ② K-Means와 비교하면 silhouette .13388, ARI .26583으로 같은 그룹이 아니다. ③ 상담원이 대시보드 나이 40·부채 .8·최근 연체 2를 입력하고 버튼을 누르면 RF확률과 SHAP 기여 차트가 나온다. 실제 타겟은 연체이며 PDF 보너스 예시의 이탈을 새 타겟으로 생성하지 않는다.',
 'HierarchicalAnalysis와 DashboardAnalysis는 CustomerAnalysis를 상속한다. 기본 파일을 수정해 보너스를 섞지 않는다. AppTest는 새 프로세스에서 위젯 값을 바꾼 뒤 버튼을 클릭하고 출력 확률이 직접 model.predict_proba 결과와 일치하는지 확인한다. 웹 그래프는 기여도 막대와 덧셈 설명이다.',
 '군집 알고리즘에 따른 상담 대상 변화와 입력에 따른 모델 설명을 비교할 수 있다. 계층 군집은 거리를 저장하므로 큰 데이터에서 메모리 비용이 높고, 이 로컬 대시보드는 배포 서비스를 구성한 결과가 아니다.',
 'Ward 병합 비용=|A||B|/(|A|+|B|)·‖μA−μB‖²'),
('12','12. TDD와 재현성으로 평가자가 확인하는 순서','tests/test_analysis.py','test_shap_additivity_and_decision',
 'TDD는 먼저 기대 행동을 테스트로 쓰고 실패를 확인한 다음 구현해 통과시키는 흐름이다. 단순히 구현 줄을 복제하는 검사가 아니라 데이터 원본 보존, 타겟 배제, 표준화, K 선택, SHAP 덧셈, 임계값, 상속 구조라는 의미 있는 계약을 검증한다. 실행 로그와 그래프는 문서 주장과 연결되는 실제 근거이다.',
 '평가자가 숫자 .9830을 의심하는 장면이다. ① reports/shap.json에서 행 576과 입력을 읽는다. ② 해당 입력을 predict_proba에 넣어 같은 확률을 확인한다. ③ SHAP 기준과 6개 기여를 더해 허용오차 내 일치하는지 본다. 그 후 그림을 열어 텍스트 해석이 실제 부호와 맞는지 확인하면 결과를 단계별로 평가할 수 있다.',
 '미구현 모듈로 실제 RED 로그를 저장한 뒤 구현 후 GREEN 5개 테스트를 통과했다. 설치 검증은 root 설치 프로세스와 독립된 새 Python 프로세스에서 실제 패키지 경로·중복 metadata·TreeSHAP 호출·Streamlit 위젯 상호작용을 확인한다. HTML 코드 부록은 현재 파일 SHA와 정확한 줄 앵커를 기록하므로 설명에서 즉시 실제 코드로 이동할 수 있다.',
 '환경이 다른 동료의 재실행과 코드 리뷰에 쓰인다. 수치 실험의 고정 seed는 재현성을 돕지만 라이브러리 버전 변화·부동소수점 차이까지 같은 비트 결과를 보장하지 않는다.',
 '검증: maxᵢ|baseᵢ+Σⱼφᵢⱼ−predict_probaᵢ|<10⁻⁷'),
]

def build_readme():
    parts=['# A5-2: 고객 군집화와 설명 가능한 연체 예측','## 1. 문제 / 목표',
    '원본 가상 금융 고객 10,000명의 입력 6개로 페르소나를 탐색하고 이전 미션의 Random Forest로 예측한 연체 확률을 TreeSHAP으로 설명한다. 각 미션 폴더는 독립적이다. 원본 CSV와 학습 모델을 이 폴더 내부로 복사했으며 실행 시 다른 미션의 코드·데이터를 참조하지 않는다.',
    'PDF의 거절 확률 `5 이상`은 확률 범위 [0,1]을 벗어나므로 `0.5 이상`으로 명시적으로 정정하였다. 보너스의 이탈 확률 예시는 실제 타겟 `is_overdue`인 연체 확률로 표시한다. 타겟·데이터 컬럼을 새로 추가하지 않았다.',
    '### 설치 및 실행',
    'Python 3.12 / conda py312에서 검증했다. `requirements.txt`에는 scikit-learn·SHAP 버전을 포함한 직접 의존성을 기록했다. 복사된 모델 파일은 이 과제에서 생성한 신뢰하는 로컬 artifact다.',
    '```bash\nconda activate py312\ncd A5-2\npython -m pip install -r requirements.txt\npython -m pytest tests -q\npython analysis_clustering.py\npython analysis_shap.py\npython bonus_compare.py\npython scripts/build_docs.py\npython -m streamlit run app.py\n```',
    '실행 순서는 군집화 → SHAP → README/HTML 재생성이다. `models/random_forest.joblib`은 이전 미션 Train 분할에서 학습한 sklearn 전처리+RF Pipeline이다. 원본 SHA-256: `'+C['csv_sha256']+'`; 모델 SHA-256: `'+S['model_sha256']+'`.',
    '평가자가 읽을 순서는 [코드 설명](docs/code_walkthrough.md), [도식·수식·실제 코드 HTML](docs/code_walkthrough.html), [실험 JSON](reports/shap.json)이다. README HTML은 [README.html](README.html)이다.',
    '## 2. 군집 요약',
    f"K=2~8을 조사했다. Silhouette 우선 기준으로 K={C['chosen_k']}를 선택했고 점수는 {max(r['silhouette'] for r in C['candidates']):.6f}다. Elbow는 감소가 점차 완만하지만 명확한 꺾임은 약하므로 확정적 최적 K라고 단정하지 않는다. Silhouette는 seed42로 1,500행을 표본화했고 KMeans는 전체 10,000행, 6차원, n_init=10이다.",
    '|K|Inertia|Silhouette (동일 1,500 표본)|','|---|---|---|']
    parts += [f"|{r['k']}|{r['inertia']:.3f}|{r['silhouette']:.6f}|" for r in C['candidates']]
    parts += [image('k_selection.png','Elbow와 Silhouette: K=2 최대이나 분리도는 낮음'),
              '|군집|인원|나이 평균|소득 평균(만원)|소비 점수|부채비율|카드 수|6개월 연체 평균|','|---|---|---|---|---|---|---|---|']
    for r in C['clusters']:
        m=r['means'];parts.append(f"|{r['cluster']}|{r['count']}|{m['age']:.2f}|{m['annual_income']:.2f}|{m['spending_score']:.2f}|{m['debt_ratio']:.3f}|{m['credit_card_count']:.2f}|{m['overdue_count_6m']:.3f}|")
    parts += [f"PCA 설명된 분산은 PC1={C['explained_variance_ratio'][0]:.2%}, PC2={C['explained_variance_ratio'][1]:.2%}, 합={sum(C['explained_variance_ratio']):.2%}다. PC는 원본 특성의 가중 합이고 소득·나이 한 가지가 아니다. 2D는 정보 약 65.39%를 생략하므로 화면의 겹침만으로 6차원 군집을 판정하지 않는다.",image('pca_clusters.png','6차원 군집을 2D로 투영한 그림; 축에 설명된 분산 표시'),
    '## 3. 페르소나 정의',
    '### 군집 0: 과거 연체 경험군',
    '3,931명, 최근 6개월 연체 평균 1.287회이며 소득 5,054만원·부채 .506이다. 다른 군집과 나이·소득 차이는 작아서 VIP·저소득군으로 이름 붙일 근거가 약하다.',
    '상환 일정 점검과 자동 결제 안내를 우선 제안한다. 연체 경험만으로 자동 거절하지 않고 현재 입력의 모델 예측과 별도로 해석한다.',
    '대표 행 6225는 중심에 가장 가까운 실제 고객이며 소득 5,396만원, 연체1회, 부채 .46, 연체 확률 .0051(승인)이다. 소득 기여 −.3574가 전체 위험을 크게 낮추므로 군집 명칭이 예측 판정과 동일하지 않다.',
    image('waterfall_cluster_0.png','군집0 대표: 과거 연체가 있어도 예측은 승인'),
    '### 군집 1: 최근 연체 이력 없음군',
    '6,069명, 최근 연체 평균 0회이며 소득 5,020만원·부채 .498이다. 이 군집의 최근 연체0회는 실제 관측 통계이고 미래 연체가 절대로 없다는 뜻은 아니다.',
    '기본 결제 관리와 상황 변화 시 재상담 안내를 제안한다. 소득·부채 확인을 생략하지 않는다.',
    '대표 행2707은 소득4,645만원·연체0회·부채 .5, 예측확률0이며 최근 연체 기여 −.1947이 크다. 대표 한 명의 설명을 6,069명 전원에게 그대로 복사하면 안 된다.',image('waterfall_cluster_1.png','군집1 대표의 실제 개별 SHAP'),
    '## 4. Global SHAP 해석',
    f"TreeExplainer, 클래스1 연체 확률 출력, 실제 1,000행 seed42 표본이다. 최대 SHAP 덧셈 오차 {S['max_additivity_error']:.3e}로 1e-7 기준을 통과했다. 기준값 약 .4989는 class-balanced RF와 TreeExplainer 배경의 모델 출력 기준이지 실제 CSV 연체율 12.01% (1,201/10,000)가 아니다.",
    '|상위 변수|평균 절대 SHAP|낮은 사분위 평균 기여|높은 사분위 평균 기여|','|---|---|---|---|']
    parts += [f"|{r['feature']}|{r['mean_abs_shap']:.6f}|{r['low_quartile_mean_shap']:+.6f}|{r['high_quartile_mean_shap']:+.6f}|" for r in S['ranking'][:3]]
    parts += [image('shap_summary.png','Global Summary: 영향 크기와 특성 값의 방향을 함께 표시')]
    insights={
     'annual_income':'낮은 소득 사분위 평균 기여 +.1755, 높은 소득 사분위 −.3837으로 이 모델에서는 소득이 높을 때 연체 위험을 낮추는 경향이 보인다. 소득 확인과 상환 능력 상담의 우선순위를 제안하되 이 관계는 합성 타겟 생성 규칙의 영향을 크게 받으며 임금 인상의 인과 효과가 아니다.',
     'overdue_count_6m':'최근 연체 횟수의 낮은 사분위 기여 −.1796, 높은 사분위 +.1020으로 과거 이력이 모델 위험을 높이는 경향이 보인다. 연체 이력군에 상환 일정 점검을 제안하지만 같은 횟수에서 기여가 달라질 수 있으므로 단독 거절 규칙으로 바꾸지 않는다.',
     'debt_ratio':'낮은 부채 사분위 기여 −.1898, 높은 사분위 +.1052로 고부채가 모델 위험을 높이는 경향이 보인다. 부채 상환 상담을 우선 안내하되 고객별 소득·연체 정보와 함께 보고 상담 효과는 별도 검증한다.'}
    for feature in S['dependence_features']:
        parts += ['### Dependence: '+feature,insights[feature],image('dependence_'+feature+'.png',feature+' 원본값 대 SHAP 기여: 예측확률 자체·인과 곡선이 아님')]
    parts += ['## 5. Local 사례 2건',
      '전체 고객 예측 확률의 최소와 최대 행을 선정했다. 관측 타겟을 선정 기준으로 사용하지 않았고 교육용 임계값 .5로 판정했다. 극단 사례는 해석을 선명하게 하지만 보통 고객의 대표 사례는 아니다.']
    for name in ['approval','rejection']:
        case=S['cases'][name];parts += [f"### {case['decision']}: 행 {case['row_index']} / 연체 확률 {case['probability']:.6f}",
            '원본 입력: '+', '.join(f'{k}={v:g}' for k,v in case['features'].items())+'.',
            f"실제 타겟은 {case['actual_is_overdue']}이며 모델 판정과 별개의 관측 값이다. 기준 {case['base']:.6f}에 아래 6개 기여를 더하면 출력 확률이 된다.",
            '|입력|SHAP 기여 (연체 확률 단위)|','|---|---|']
        parts += [f'|{k}|{v:+.6f}|' for k,v in case['contributions'].items()]
        parts += [image('waterfall_'+name+'.png',case['decision']+' 실제 Waterfall: 기준→기여→예측')]
    parts += ['승인 사례는 연체0회·낮은 부채의 음수 기여가 크다. 거절 사례는 낮은 소득과 높은 부채의 양수 기여가 크다. 이 결과는 모델이 입력을 사용한 이유를 설명하고 실제 거절 정책의 정당성이나 미래 결과를 증명하지 않는다.',
     '## 6. 실행 제언',
     '|대상|메시지|제안 액션|확인할 결과|','|---|---|---|---|',
     '|과거 연체 경험군|상환 일정과 자동 결제를 함께 점검|납부일 상담·알림 안내|다음 기간 연체 변화 (본 실험 미측정)|',
     '|최근 연체 이력 없음군|현재의 정상 납부를 유지|기본 결제 안내·소득/부채 변화 재상담|이상 변화 탐지율 (본 실험 미측정)|',
     '|높은 부채 기여 개별 고객|다른 입력과 함께 상환 부담 확인|소득 확인·상환 일정 상담|추가 상담 완료율 (본 실험 미측정)|',
     '군집은 상담 메시지 분류, RF는 예측, SHAP은 설명이라는 서로 다른 역할이다. 군집0 대표 승인 사례가 보여주듯 군집별 마케팅 전략을 곧바로 대출 거절 규칙으로 변환하지 않는다.',
     '## 7. 한계 / 추가 실험',
     '합성 데이터의 원본 8개 컬럼을 그대로 사용했으며 실제 금융 효과·법적 적합성·공정성을 측정한 결과가 아니다. 타겟의 생성 규칙에 소득·부채·연체가 주입되어 실제 고객 데이터의 복잡성을 반영하지 못한다. CSV의 입력 컬럼 추가·외부 데이터 병합·증강은 수행하지 않았다.',
     'K=2 silhouette .13639가 낮고 PCA 총34.61%라 명확한 실제 고객 계층 발견으로 과장하지 않는다. SHAP 표본1000, silhouette표본1500 선택에는 변동이 있고 추가 seed/K 후보 실험은 향후 검증 대상이다. 설명용 표본에 학습 행이 포함될 수 있으므로 이 SHAP 보고서의 수치를 독립 Test 성능으로 보고하지 않는다.',
     f"선택 과제 Ward K=2는 silhouette {B['silhouette']:.6f}, KMeans와 ARI {B['ari_vs_kmeans']:.6f}, 군집 크기 {B['counts']}다. KMeans 분리도와 비슷하지만 배정은 다르고 가장 큰 그룹 비중이 높다. 어느 알고리즘이 업무에 더 좋은지는 군집별 상담 유용성을 평가해야 한다.",
     '대시보드는 상속한 DashboardAnalysis로 연체 확률·변수별 SHAP 막대·덧셈을 표시한다. `python -m streamlit run app.py`로 실행한다. 새 프로세스의 AppTest에서 실제 위젯 값을 변경하고 예측 버튼·SHAP 계산·출력 확률 일치를 확인했다.',
     '검증 증거: [RED](reports/tdd_red.txt), [GREEN](reports/tdd_green.txt), [설치·앱 E2E](reports/installation_verification.json), [군집 JSON](reports/clustering.json), [SHAP JSON](reports/shap.json), [비교 JSON](reports/bonus_comparison.json). 핵심 구현은 '+code('src/analysis.py','CustomerAnalysis')+' 및 '+code('analysis_shap.py','run')+'이다.']
    return '\n\n'.join(parts)+'\n'

def walkthrough():
    parts=['# A5-2 순차 코드 설명','개념 → 현실 상황을 3단계로 계산 → 실제 구현 → 결과와 활용의 순서로 읽는다. 이 문서는 A5-2 PDF의 요구사항만 다루며 다른 미션 코드를 import하지 않는다. HTML의 코드 링크는 현재 파일을 임베딩한 정확한 줄로 이동한다. README는 측정 결과와 비즈니스 제언, 이 문서는 그 결과에 이르는 이해의 순서를 설명한다.']
    images={3:['k_selection.png'],4:['pca_clusters.png'],5:['waterfall_cluster_0.png','waterfall_cluster_1.png'],8:['shap_summary.png'],9:['waterfall_approval.png','waterfall_rejection.png'],10:['dependence_annual_income.png','dependence_overdue_count_6m.png','dependence_debt_ratio.png']}
    for n,(slug,title,file,symbol,concept,example,detail,cases,formula) in enumerate(CHAPTERS,1):
        parts += ['## '+title,'### 먼저 이해할 개념',concept,'$$ '+formula+' $$','### 현실 예시를 순서대로 풀기',example,'### 실제 작성한 코드와 결과',code(file,symbol),detail]
        tree=ast.parse((ROOT/file).read_text());node=next(x for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name==symbol)
        snippet='\n'.join((ROOT/file).read_text().splitlines()[node.lineno-1:min(node.end_lineno,node.lineno+18)])
        parts += ['```python\n'+snippet+'\n```','### 활용과 해석 범위',cases]
        for name in images.get(n,[]):parts.append(image(name,'실제 실행 결과: '+name))
    parts += ['## 평가자가 확인할 실행 근거',
    '입력 SHA → 전처리 검사 → K 후보 표 → PCA 분산 → 원본 군집 평균 → 대표 고객 → RF 확률 → SHAP 덧셈 → 그림 방향 → 업무 제언 순서로 확인한다. 모든 그림은 실제 저장 PNG를 HTML 안에 넣고 코드 부록은 실제 원문과 SHA를 포함한다.',
    '핵심 테스트 '+code('tests/test_analysis.py','test_exact_data_and_target_exclusion')+' 및 '+code('tests/test_analysis.py','test_shap_additivity_and_decision')+'를 먼저 실행하고 README의 측정 결과와 비교한다. 보너스는 '+code('src/bonus.py','DashboardAnalysis')+'에서 기본 클래스를 상속하므로 필수 분석과 구별된다.']
    return '\n\n'.join(parts)+'\n'

def source_html():
    manifest={};parts=['<section id="source"><h2>실제 코드 부록: 파일·줄·SHA-256</h2><p>문서 생성 시점의 원문이다. 링크로 이동한 줄은 금색 배경으로 강조된다. 파일을 수정하면 build_docs.py로 다시 생성한다.</p>']
    files=sorted([p for p in ROOT.rglob('*.py') if '.cache' not in p.parts and '__pycache__' not in p.parts])
    for path in files:
        name=str(path.relative_to(ROOT));raw=path.read_text();sha=hashlib.sha256(path.read_bytes()).hexdigest();manifest[name]={'sha256':sha,'lines':len(raw.splitlines())}
        parts += [f'<section class="source-section"><h3>{escape(name)}</h3><p>SHA-256 <code>{sha}</code></p><pre><code>']
        for line,text in enumerate(raw.splitlines(),1):
            identifier=h.anchor(name,line);parts.append(f'<span class="source-line" id="{identifier}"><a class="ln" href="#{identifier}">{line}</a>{escape(text)}</span>')
        parts += ['</code></pre></section>']
    parts.append('</section>');return '\n'.join(parts),manifest

def document(markdown,title,guide=False):
    content=h.markdown_html(markdown,'guide' if guide else 'readme')
    # Root README relative links resolve within its own folder; generated code links stay embedded.
    if not guide:content=content.replace('href="../','href="').replace('href="#guide"','href="docs/code_walkthrough.html"')
    if guide:
        for index in (0,2,5,6,8,10):
            slug,title_ch,*_=CHAPTERS[index]
            nodes={
                0:[('원본 고객 CSV','10000 rows / 8 columns'),('타겟 두 열 제외','FEATURES only'),('입력 6개 확정','X: 10000 x 6')],
                2:[('표준화된 고객','z-score / 6 features'),('K 후보별 군집·점수','K=2..8 / seed=42'),('분리도 우선 K=2','silhouette=0.13639')],
                5:[('실제 고객 입력 6개','ORIGINAL UNITS'),('기존 RF Pipeline','prepare -> RF'),('연체 확률과 판정','reject if p >= 0.5')],
                6:[('RF와 변환된 입력','TREE / PREPARE'),('연체 클래스 TreeSHAP','class 1 / phi'),('확률 덧셈 검증','base + sum(phi) = p')],
                8:[('확률 최소·최대 행','rows 6 / 576'),('실제 개별 Waterfall','base -> contributions'),('승인·거절 이유','p=0.0000 / 0.9830')],
                10:[('CustomerAnalysis 상속','BONUS CLASSES'),('Ward와 웹 입력','CLUSTER / STREAMLIT'),('배정 비교·예측 설명','ARI / SHAP')],
            }[index]
            marker=f'<h2 id="guide-h'
            # Chapter diagrams precede their first concept heading; all source boxes remain separate.
            heading='>'+title_ch+'</h2>'
            content=content.replace(heading,heading+h.diagram('a52-'+slug,title_ch,nodes))
    else:
        content=h.diagram('a52-readme','A5-2 분석 흐름',[('원본 입력 6개','CSV'),('군집과 TreeSHAP','ANALYSIS'),('상담 제언','REPORT')])+content
    source,manifest=source_html()
    html=f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>{h.CSS}</style></head><body><main><p class="tag">A5-2 · FINANCIAL SERVICES · OFFLINE</p><nav><a href="'+('README.html' if not guide else '../README.html')+'">README</a> · <a href="'+('docs/code_walkthrough.html' if not guide else '#guide')+'">순차 코드 설명</a> · <a href="#source">실제 코드 부록</a></nav><article id="guide">'+content+'</article>'+source+'<footer>diagram-design 2.6.12 financial-services profile / flowchart doc-wide. 오프라인 로컬 글꼴 대체를 사용한다. 이미지·수식·도식·코드는 파일 내부에 포함되어 있다.</footer></main></body></html>'
    return html,manifest

if __name__=='__main__':
    readme=build_readme().replace('](../','](');guide=walkthrough()
    (ROOT/'README.md').write_text(readme);(ROOT/'docs/code_walkthrough.md').write_text(guide)
    html,manifest=document(guide,'A5-2 순차 코드 설명',True);(ROOT/'docs/code_walkthrough.html').write_text(html)
    html,_=document(readme,'A5-2 README');(ROOT/'README.html').write_text(html)
    (ROOT/'reports/document_build.json').write_text(json.dumps({'sources':manifest,'chapters':len(CHAPTERS),'diagram_profile':'financial-services','code_background':'#e7ebf0','code_foreground':'#14213d'},indent=2))
    print('Generated README.md/html and docs/code_walkthrough.md/html')
