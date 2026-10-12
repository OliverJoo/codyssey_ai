"""보너스 Streamlit 앱. PDF의 '이탈' 예시는 실제 연체 타겟으로 표시한다."""
import streamlit as st
from src.bonus import DashboardAnalysis

@st.cache_resource
def load_analysis():
    return DashboardAnalysis()

st.title('고객 연체 확률과 예측 근거')
st.caption('교육용 가상 데이터 모델입니다. 연체 예측을 임계값 0.5로 승인/거절에 연결합니다.')
age = st.number_input('나이', min_value=20, max_value=69, value=35)
income = st.number_input('연 소득 (만원)', min_value=1500.0, value=5000.0)
spending = st.number_input('소비 점수', min_value=1, max_value=99, value=50)
debt = st.slider('소득 대비 부채비율', 0.0, 1.0, .3)
cards = st.number_input('보유 신용카드 수', min_value=1, max_value=9, value=3)
overdue = st.number_input('최근 6개월 연체 횟수', min_value=0, value=0)
if st.button('예측과 SHAP 설명 보기'):
    result = load_analysis().predict_customer(dict(age=age, annual_income=income, spending_score=spending,
                                                  debt_ratio=debt, credit_card_count=cards, overdue_count_6m=overdue))
    st.metric('연체 확률', f"{result['probability']:.2%}")
    st.write('교육용 판정: '+result['decision'])
    st.write(f"기준 확률 {result['base']:.4f} + 변수별 기여 합 = {result['probability']:.4f}")
    st.bar_chart(result['contributions'])
