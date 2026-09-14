import re

# ── 검증 규칙 (source of truth) ──────────────────────
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
USERNAME_PATTERN = r"^[a-zA-Z0-9_-]+$"
USERNAME_PATTERN_MSG = "아이디는 영문, 숫자, _, - 만 사용할 수 있습니다."

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 72  # bcrypt 바이트 제한 고려


def validate_username(v: str) -> str:
    if not (USERNAME_MIN_LENGTH <= len(v) <= USERNAME_MAX_LENGTH):
        raise ValueError(f"아이디는 {USERNAME_MIN_LENGTH}~{USERNAME_MAX_LENGTH}자여야 합니다.")
    if not re.match(USERNAME_PATTERN, v):
        raise ValueError(USERNAME_PATTERN_MSG)
    return v


def validate_password(v: str) -> str:
    if not (PASSWORD_MIN_LENGTH <= len(v) <= PASSWORD_MAX_LENGTH):
        raise ValueError(f"비밀번호는 {PASSWORD_MIN_LENGTH}~{PASSWORD_MAX_LENGTH}자여야 합니다.")
    if v.isspace() or v != v.strip():
        raise ValueError("비밀번호에 앞뒤 공백을 사용할 수 없습니다.")
    if not re.search(r"[A-Za-z]", v) or not re.search(r"[0-9]", v):
        raise ValueError("비밀번호는 영문과 숫자를 모두 포함해야 합니다.")
    return v


def get_validation_rules() -> dict:
    """프론트엔드에 공유할 규칙 (엔드포인트에서 그대로 반환)"""
    return {
        "username": {
            "min_length": USERNAME_MIN_LENGTH,
            "max_length": USERNAME_MAX_LENGTH,
            "pattern": USERNAME_PATTERN,
            "message": USERNAME_PATTERN_MSG,
        },
        "password": {
            "min_length": PASSWORD_MIN_LENGTH,
            "max_length": PASSWORD_MAX_LENGTH,
        },
    }