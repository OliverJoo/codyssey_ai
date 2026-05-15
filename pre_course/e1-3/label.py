"""라벨 정규화 관련 함수"""


def normalize_label(raw_label):
    """입력 라벨을 표준 라벨(Cross/X)로 정규화한다."""
    if raw_label is None:
        return None

    text = str(raw_label).strip()
    lowered = text.lower()

    if lowered == "+" or lowered == "cross":
        return "Cross"
    if lowered == "x":
        return "X"

    return text