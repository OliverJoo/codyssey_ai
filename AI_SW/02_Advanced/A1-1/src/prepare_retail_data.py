"""공개 거래의 고객 표본을 추출하고 이미지/결측 실습 입력을 준비한다."""

from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
import pandas as pd


URL = 'https://raw.githubusercontent.com/dbdmg/data-science-lab/master/datasets/online_retail.csv'


def prepare_retail_data(root, customer_count=240, seed=42):
    root = Path(root)
    raw_path = root / '.cache' / 'online_retail.csv'
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if not raw_path.exists():
        urlretrieve(URL, raw_path)
    source = pd.read_csv(raw_path, encoding='ISO-8859-1')
    # RFM은 고객을 식별할 수 있는 양의 구매만 대상으로 했다.
    valid = source.dropna(subset=['CustomerID', 'Description']).copy()
    valid = valid[(valid.Quantity > 0) & (valid.UnitPrice > 0)
                  & ~valid.InvoiceNo.astype(str).str.startswith('C')].drop_duplicates()
    rng = np.random.default_rng(seed)
    customers = rng.choice(np.sort(valid.CustomerID.unique()), customer_count, replace=False)
    sample = valid[valid.CustomerID.isin(customers)].copy()
    output = root / 'data'
    output.mkdir(parents=True, exist_ok=True)
    # 원본 값은 따로 저장하고 분석용 열 이름만 바꿨다.
    sample.to_csv(output / 'retail_source.csv', index=False)
    orders = sample.rename(columns={
        'InvoiceNo': 'order_id', 'StockCode': 'product_id', 'Description': 'product_name',
        'Quantity': 'qty', 'InvoiceDate': 'order_date', 'UnitPrice': 'price',
        'CustomerID': 'customer_id', 'Country': 'country',
    }).reset_index(drop=True)
    orders['customer_id'] = orders.customer_id.astype(int).astype(str)
    orders['order_date'] = pd.to_datetime(orders.order_date).dt.normalize()
    orders['amount'] = orders.price * orders.qty
    codes, products = pd.factorize(orders.product_id, sort=True)
    orders['image_index'] = codes
    # 원본에 사진이 없어 픽셀 연산 검증용 배열을 별도 생성했다.
    # 실제 상품 사진이나 원본 데이터의 이미지라고 해석하지 않는다.
    images = rng.integers(0, 256, size=(len(products), 8, 8, 3), dtype=np.uint8)
    # 원본 가격에는 결측이 없어 대치 비교를 위해 5%를 가렸다.
    hidden = rng.choice(len(orders), size=int(len(orders) * 0.05), replace=False)
    orders.loc[hidden, 'price'] = np.nan
    orders.to_csv(output / 'orders.csv', index=False)
    np.save(output / 'images.npy', images)
    return orders


if __name__ == '__main__':
    prepare_retail_data(Path(__file__).resolve().parents[1])
