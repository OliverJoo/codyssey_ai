"""선택 과제: 기본 분석 클래스를 상속하며 기본 파일과 분리한다."""

import numpy as np
import pandas as pd

from src.pipeline import DataAnalyzer


class BonusDataAnalyzer(DataAnalyzer):
    def add_edge_features(self):
        """가로/세로 인접 픽셀 차이의 절댓값 평균을 엣지 강도로 사용한다."""
        images = self.images.astype(float)
        horizontal = np.abs(np.diff(images, axis=2))
        vertical = np.abs(np.diff(images, axis=1))
        axes = tuple(range(1, images.ndim))
        edge = (horizontal.mean(axis=axes) + vertical.mean(axis=axes)) / 2
        self.df['image_edge'] = edge[self.df.image_index.to_numpy()]
        return self.df

    def cohort_retention(self):
        """가입 코호트 전체 고객 중 해당 월에 두 번째 이후 구매한 고객 비율."""
        orders = self.df.sort_values('order_date').copy()
        orders['cohort'] = orders.signup_date.dt.to_period('M')
        orders['month'] = orders.order_date.dt.to_period('M')
        orders['age'] = orders['month'].astype('int64') - orders.cohort.astype('int64')
        repeat = orders.groupby('customer_id').cumcount() > 0
        sizes = orders.groupby('cohort').customer_id.nunique()
        counts = orders[repeat].groupby(['cohort', 'age']).customer_id.nunique().unstack()
        last_month = orders['month'].max()
        max_age = last_month.ordinal - sizes.index.min().ordinal
        counts = counts.reindex(index=sizes.index, columns=range(max_age + 1)).fillna(0)
        retention = counts.div(sizes, axis=0)
        observed = (sizes.index.astype('int64').to_numpy()[:, None]
                    + retention.columns.to_numpy()[None, :] <= last_month.ordinal)
        retention = retention.where(observed)
        retention.index = retention.index.astype(str)
        return retention

    def plot_cohort(self, retention):
        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(retention, annot=True, fmt='.0%', cmap='Blues', vmin=0, vmax=1, ax=ax)
        ax.set(title='Repeat purchase rate by signup cohort',
               xlabel='Months since signup', ylabel='Signup month')
        fig.tight_layout()
        return fig

    def plot_rfm(self, rfm, currency='GBP'):
        # Plotly는 이 보너스 메서드에서만 가져온다.
        import plotly.express as px

        return px.scatter(rfm.reset_index(), x='recency', y='monetary',
                          size='frequency', color='segment', hover_name='customer_id',
                          title='RFM customer segments',
                          labels={'recency': 'Days since last order',
                                  'monetary': f'Total amount ({currency})',
                                  'frequency': 'Order count', 'segment': 'Segment'})
