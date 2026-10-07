# 이미지 출처와 전처리

John Burkardt의 공개 [PGMA 샘플 데이터](https://people.math.sc.edu/Burkardt/data/pgma/pgma.html)에서 [baboon.ascii.pgm](https://people.math.sc.edu/Burkardt/data/pgma/baboon.ascii.pgm)을 내려받았다. 출처 페이지는 코드와 데이터의 배포 라이선스를 GNU LGPL로 표기한다. 라이선스 안내는 해당 페이지의 Licensing 링크를 따른다. 수집일은 2026-10-07이다.

원본은 P2 형식의 512×512 흑백 이미지이며 최대 회색값은 255다. 주석과 헤더를 읽고 `pixels / maximum`으로 정규화했다. PDF의 64×64 이하 조건을 맞추기 위해 `original[::8, ::8]`로 픽셀을 선택했다. 이 방식은 보간이나 별도 이미지 처리 라이브러리를 사용하지 않으며, 세부 질감 일부가 소실될 수 있다.

실험에는 원본 512×512가 아니라 **image64.npy (64×64)**만 입력했다. 원본은 출처 확인과 재현을 위해 보존했다.

- [전처리 코드](../scripts/prepare_image.py)
- [입력 배열](image64.npy)
- [출처·크기·SHA-256 메타데이터](source_metadata.json)
- 원본 SHA-256: `bf82d82e4f7597d4cea8672cf524c080fdfe307fced42d0b39b7427267eaa45b`

실험의 SVD 인자 개수를 세어 저장량을 비교했다. 원본 PGM 텍스트 파일의 바이트 수와 비교하는 압축률은 계산하지 않았다. 파일 형식, 숫자의 자료형, 헤더와 메타데이터가 다르기 때문이다.
