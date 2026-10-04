"""NumPy와 Pandas로 구현한 기본 이커머스 분석 파이프라인."""

import numpy as np
import pandas as pd


class DataAnalyzer:
    """거래 CSV와 상품 이미지 배열을 읽고 분석한다."""

    def __init__(self, data_path, image_path):
        self.data_path = data_path
        self.image_path = image_path
        self.df = None
        self.images = None

    def load_data(self):
        self.df = pd.read_csv(self.data_path)
        self.df['order_date'] = pd.to_datetime(self.df['order_date'])
        if 'signup_date' in self.df:
            self.df['signup_date'] = pd.to_datetime(self.df['signup_date'])
        self.images = np.load(self.image_path, allow_pickle=False)
        return self.df

    def missing_summary(self):
        return self.df.isna().sum()

    def handle_missing_values(self, column='price', group_col='category', strategy='mean'):
        """그룹 통계로 대치하고, 전부 결측인 그룹에는 전체 통계를 쓴다."""
        if strategy not in ('mean', 'median'):
            raise ValueError('strategy는 mean 또는 median이어야 합니다.')
        group_values = self.df.groupby(group_col)[column].transform(strategy)
        fallback = self.df[column].agg(strategy)
        self.df[column] = self.df[column].fillna(group_values).fillna(fallback)
        return self.df

    def engineer_features(self):
        """이미지별 전체 픽셀 통계와 상품명 단어 수를 배열 연산으로 구한다."""
        images = self.images.astype(float)
        axes = tuple(range(1, images.ndim))
        image_index = self.df['image_index'].to_numpy()
        self.df['image_mean'] = images.mean(axis=axes)[image_index]
        self.df['image_std'] = images.std(axis=axes, ddof=0)[image_index]
        self.df['product_word_count'] = self.df['product_name'].str.split().str.len()
        return self.df

    def iqr_bounds(self, column, threshold=1.5):
        q1 = self.df[column].quantile(0.25)
        q3 = self.df[column].quantile(0.75)
        iqr = q3 - q1
        return q1 - threshold * iqr, q3 + threshold * iqr

    def detect_outliers(self, column, threshold=1.5):
        lower, upper = self.iqr_bounds(column, threshold)
        return self.df[(self.df[column] < lower) | (self.df[column] > upper)]

    def handle_outliers(self, column, threshold=1.5):
        """EDA 대상 열만 경계값으로 제한한다. 거래 행/결제액은 보존한다."""
        lower, upper = self.iqr_bounds(column, threshold)
        self.df[column] = self.df[column].clip(lower, upper)
        return self.df

    def summary_statistics(self, columns):
        summary = self.df[columns].agg(['mean', 'median', 'std']).T
        summary['q1'] = self.df[columns].quantile(0.25)
        summary['q3'] = self.df[columns].quantile(0.75)
        return summary

    def calculate_rfm(self, customer_col='customer_id', date_col='order_date',
                      amount_col='amount', reference_date=None, order_col='order_id'):
        """주문 번호가 있으면 고유 주문 수, 없으면 행 수로 F를 계산한다."""
        dates = pd.to_datetime(self.df[date_col])
        reference = dates.max() if reference_date is None else pd.Timestamp(reference_date)
        if reference < dates.max():
            raise ValueError('기준일은 최종 거래일보다 빠를 수 없습니다.')
        grouped = self.df.groupby(customer_col)
        rfm = pd.DataFrame({
            'recency': (reference - grouped[date_col].max()).dt.days,
            'frequency': (grouped[order_col].nunique() if order_col in self.df
                          else grouped[date_col].count()),
            'monetary': grouped[amount_col].sum(),
        })
        # 동일 값에는 동일 점수를 준다. 최근 구매일수는 작을수록 높은 점수다.
        rfm['r_score'] = np.ceil(rfm.recency.rank(pct=True, ascending=False) * 4).astype(int)
        rfm['f_score'] = np.ceil(rfm.frequency.rank(pct=True) * 4).astype(int)
        rfm['m_score'] = np.ceil(rfm.monetary.rank(pct=True) * 4).astype(int)
        return rfm

    def segment_customers(self, rfm, recent_days=30, churn_days=90):
        """이탈 → 우수 → 신규 → 나머지 활동 고객 순서로 분류한다."""
        result = rfm.copy()
        result['segment'] = np.select(
            [result.recency > churn_days,
             (result.recency <= recent_days) & (result.f_score >= 3) & (result.m_score >= 3),
             (result.recency <= recent_days) & (result.frequency == 1)],
            ['Churned', 'VIP', 'New'], default='Loyal',
        )
        return result
