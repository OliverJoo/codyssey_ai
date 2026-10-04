"""외부 원본을 가장하지 않는, 고정 시드의 교육용 합성 이커머스 샘플."""

from pathlib import Path

import numpy as np
import pandas as pd


def make_sample_data(output_dir, seed=42):
    rng = np.random.default_rng(seed)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    customer = np.arange(240)
    group = customer // 60
    frequency = np.array([12, 7, 1, 4])[group]
    reference = pd.Timestamp('2026-09-30')
    recency = np.select([group == 0, group == 1, group == 2],
                        [rng.integers(0, 20, 240), rng.integers(31, 75, 240),
                         rng.integers(0, 30, 240)], default=rng.integers(100, 160, 240))
    recency[0] = 0
    last = reference - pd.to_timedelta(recency, unit='D')
    signup = pd.Timestamp('2026-01-01') + pd.to_timedelta(rng.integers(0, 100, 240), unit='D')
    signup = pd.Series(signup)
    signup[group == 2] = last[group == 2] - pd.Timedelta(days=3)
    first = pd.DatetimeIndex(signup) + pd.Timedelta(days=1)

    customer_index = np.repeat(customer, frequency)
    start = np.repeat(np.cumsum(frequency) - frequency, frequency)
    order_number = np.arange(frequency.sum()) - start
    fraction = order_number / np.maximum(frequency[customer_index] - 1, 1)
    span = (last - first).days.to_numpy()[customer_index]
    order_date = first[customer_index] + pd.to_timedelta(np.rint(span * fraction), unit='D')
    order_date = pd.Series(order_date)
    single = frequency[customer_index] == 1
    order_date[single] = last[customer_index[single]]

    product = rng.integers(0, 48, len(customer_index))
    category = np.array(['Home', 'Beauty', 'Sports', 'Electronics'])[product // 12]
    unit_price = (product // 12 + 1) * 10000 + (product % 12) * 1000
    qty = rng.integers(1, 4, len(product))
    price = unit_price.astype(float)
    altered = rng.choice(len(price), size=84, replace=False)
    price[altered[:72]] = np.nan
    price[altered[72:]] *= 20

    # 픽셀은 사진이 아니라 밝기/엣지 통계 연습용 합성 RGB 배열이다.
    brightness = (30 + np.arange(48) * 4)[:, None, None, None]
    noise = rng.normal(0, 16, (48, 8, 8, 3))
    images = np.clip(brightness + noise, 0, 255).astype(np.uint8)
    orders = pd.DataFrame({
        'order_id': np.arange(1, len(product) + 1),
        'customer_id': np.char.add('C', customer_index.astype(str)),
        'product_name': np.char.add(np.char.add(category, ' item '), product.astype(str)),
        'category': category, 'price': price, 'qty': qty,
        'amount': unit_price * qty, 'order_date': order_date,
        'signup_date': pd.DatetimeIndex(signup)[customer_index], 'image_index': product,
    })
    orders.to_csv(output_dir / 'orders.csv', index=False)
    np.save(output_dir / 'images.npy', images)
    return orders


if __name__ == '__main__':
    make_sample_data(Path(__file__).resolve().parents[1] / 'data' / 'sample')
