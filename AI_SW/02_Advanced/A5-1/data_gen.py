"""PDF 제공 생성식/난수 호출 순서를 그대로 사용하는 10,000행 생성기."""
from pathlib import Path
import numpy as np
import pandas as pd

N_SAMPLES = 10000
RANDOM_STATE = 42

def generate_data(path=None):
    """외부 데이터·추가 정제 없이 PDF 데이터 생성 결과를 반환/저장한다."""
    np.random.seed(RANDOM_STATE)
    data = {
        "age": np.random.randint(20, 70, N_SAMPLES),
        "annual_income": np.random.normal(5000, 2000, N_SAMPLES).round(0),
        "spending_score": np.random.randint(1, 100, N_SAMPLES),
        "debt_ratio": np.random.uniform(0, 1, N_SAMPLES).round(2),
        "credit_card_count": np.random.randint(1, 10, N_SAMPLES),
        "overdue_count_6m": np.random.poisson(0.5, N_SAMPLES),
    }
    df = pd.DataFrame(data)
    df["annual_income"] = df["annual_income"].apply(lambda x: max(x, 1500))
    df["credit_score"] = (
        300 + (df["annual_income"] / 100) * 3
        - df["overdue_count_6m"] * 50 - df["debt_ratio"] * 100
        + np.random.normal(0, 30, N_SAMPLES)
    )
    df["credit_score"] = df["credit_score"].clip(0, 1000).round(0)
    threshold = df["credit_score"].quantile(0.15)
    df["is_overdue"] = np.where(
        (df["credit_score"] < threshold) & (np.random.rand(N_SAMPLES) > 0.2), 1, 0
    )
    df = df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    if path is not None:
        df.to_csv(Path(path), index=False)
    return df

if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "finance_data.csv"
    frame = generate_data(path)
    print(f"데이터 생성 완료: {path.name}")
    print(f"전체 샘플 수: {len(frame)}")
    print(f"연체(1) 비율: {frame.is_overdue.mean()*100:.2f}%")
