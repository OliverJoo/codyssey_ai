# 데이터 출처와 처리 범위

## 1. 기본 분석: UCI Online Retail

- 원저자: Daqing Chen (2015), *Online Retail*, UCI Machine Learning Repository.
- 원본 설명: [UCI 데이터 페이지](https://archive.ics.uci.edu/dataset/352/online%2Bretail).
- DOI: [10.24432/C5BW33](https://doi.org/10.24432/C5BW33).
- 라이선스: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- 사용한 CSV: [Politecnico di Torino 교육 저장소의 사본](https://github.com/dbdmg/data-science-lab/blob/master/datasets/online_retail.csv).
- 다운로드일: 2026-10-04. 다운로드 파일의 SHA-256과 변경 이력은 [source_manifest.json](source_manifest.json)에 기록했다.

영국 온라인 소매업체의 2010-12-01~2011-12-09 거래 데이터이다. 통화는 GBP이며 원본은 541,909행·8열이다. 원본에서 고객/상품명을 확인할 수 없는 행, 취소 번호(C 시작), 비양수 수량/단가, 완전히 중복된 행을 제외했다. 그 뒤 시드 42로 고객 240명을 추출하고 각 고객의 유효 구매 행을 모두 남겼다. 날짜 구간의 일부만 잘라 구매 빈도를 인위적으로 줄이지 않았다.

표본은 **22,488개 상품 행, 1,038개 주문, 240명, 2,601개 상품**이다. 취소·환불을 제외한 양의 구매액 합계는 **521,978.13 GBP**이다. 순매출이나 업체 전체 매출은 아니다.

## 2. 원본과 분석 입력 구분

`retail_source.csv`는 추출한 8열 원본 값이다. `orders.csv`는 분석용 열 이름을 적용하고 다음 실습 변환을 한 10열 입력이다. 가격을 가리기 전 금액을 `amount`에 보존했다.

| 분석 열 | 원본/생성 근거 | 주의 |
|---|---|---|
| order_id | InvoiceNo | 한 주문에 여러 행이 있으므로 고유 개수로 F 계산 |
| product_id | StockCode | 상품별 가격 대치의 그룹 키 |
| product_name | Description | 실제 상품명, 단어 수 피처 계산 |
| qty | Quantity | 해당 상품 행의 수량 |
| order_date | InvoiceDate | 달력 날짜로 정규화 |
| price | UnitPrice | 결측 대치 실습을 위해 1,124행을 의도적으로 가림 |
| customer_id | CustomerID | 정수 형태의 고객 식별자 |
| country | Country | 범주형 국가 변수 |
| amount | 원본 UnitPrice × Quantity | 대치·클리핑 후 다시 계산하지 않음 |
| image_index | 상품 ID factorize 결과 | 보조 이미지 샘플에 연결 |

원본 단가에 결측이 없어서 약 5%를 고정 시드로 가렸다. 이것을 원본 데이터에 원래 존재하던 결측이라고 해석하지 않았다. 이상치는 새로 주입하지 않았고 관측 가격의 IQR로 탐지했다.

## 3. 이미지 배열의 출처와 한계

UCI 원본에는 상품 사진이 없다. `images.npy`는 [prepare_retail_data.py](../src/prepare_retail_data.py)에서 만든 `(2601, 8, 8, 3)` uint8 픽셀 샘플이다. 상품마다 하나의 보조 배열을 연결해 NumPy 평균·표준편차와 행 매핑을 검증했다. **실제 상품 사진 또는 원본의 시각 정보가 아니다.** 이미지 평균과 매출의 관계는 사업 인사이트 근거로 사용하지 않았다.

PDF는 이미지 배열 계산을 요구하므로 보조 배열을 분석 흐름에 포함했다. 실제 상품 사진의 의미 분석을 수행한 것은 아니다.

## 4. 보너스 코호트용 샘플

원본에 가입일도 없다. 첫 구매일을 가입일로 바꾸면 가입 코호트가 아니므로 별도의 교육용 샘플을 사용했다. [make_sample_data.py](../src/make_sample_data.py)가 시드 42로 `sample/orders.csv`와 `sample/images.npy`를 만든다.

샘플은 고객 240명·주문 1,440건·상품 48개·10열이다. `signup_date`는 명시적으로 생성한 가입일이고 모든 고객에게 구매가 있다. 따라서 미구매 가입자를 제외해서 분모가 줄어드는 문제는 이 샘플에 없다. 실제 운영에는 미구매자를 포함한 회원표가 필요하다.

구매 횟수 12/7/1/4회인 고객 유형을 각각 60명씩 생성했고 날짜도 생성 규칙을 따른다. 상품명·가격·이미지·가입일·주문 모두 합성이며 외부 사진이나 개인정보를 쓰지 않았다. 이 샘플의 코호트 수치를 UCI 고객의 가입 행동이라고 설명하지 않았다. Plotly 차트는 기본 분석과 동일한 UCI 거래를 사용한다.

## 5. 재현

분석에 필요한 표본 CSV와 배열은 이 폴더에 포함했다. 분석 실행에 다운로드는 필요 없다. 표본을 원출처부터 다시 준비하려면 `A1-1/`에서 다음을 실행한다.

```bash
conda run -n py312 python -m src.prepare_retail_data
conda run -n py312 python -m src.make_sample_data
```

첫 명령은 `.cache/online_retail.csv`가 없을 때만 CSV 사본을 다운로드한다. 다운로드된 원본은 캐시에, 추출 결과는 `data/`에 저장한다. 두 번째 명령은 보너스/테스트용 `data/sample/`만 갱신한다. 라이브러리 버전과 난수 시드는 README에 기록했다.
