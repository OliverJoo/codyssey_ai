def count_words(text: str) -> int:
    """공백 기준으로 단어 개수를 세어 반환합니다."""
    return len(text.strip().split())