def reverse_string(text: str) -> str:
    """문자열을 뒤집어서 반환합니다. (예: 'abc' -> 'cba')"""
    if not isinstance(text, str):
        raise TypeError("입력값은 문자열이어야 합니다.")
    return text[::-1]
