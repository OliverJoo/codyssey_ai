"""5개 양성 if 규칙과 정상 else를 사용하는 학습 없는 기준선."""
import numpy as np

class RuleBaseline:
    def predict_row(self, row):
        """위에서부터 처음 만족하는 규칙으로 연체 위험(1)을 반환한다."""
        if row["overdue_count_6m"] >= 3:
            return 1
        elif row["debt_ratio"] > 0.7:
            return 1
        elif row["annual_income"] < 3000:
            return 1
        elif row["credit_card_count"] > 7:
            return 1
        elif row["overdue_count_6m"] >= 1 and row["debt_ratio"] > 0.45:
            return 1
        else:
            return 0

    def predict(self, frame):
        """확률이 아닌 0/1 경고 플래그를 각 고객에게 반환한다."""
        return np.array([self.predict_row(row) for _, row in frame.iterrows()])
