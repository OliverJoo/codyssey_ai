"""데이터 모델 및 유효성 검증 모듈"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional


class ValidationError(Exception):
    """입력 데이터 검증 실패 시 발생하는 예외"""

    def __init__(self, message: str, hint: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.hint = hint


def validate_date(date_str: str) -> str:
    """YYYY-MM-DD 날짜 형식 검증"""
    if not isinstance(date_str, str):
        raise ValidationError("날짜는 문자열이어야 합니다.", hint="예: 2024-01-15")
    try:
        parsed = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        raise ValidationError(
            "날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).",
            hint="예: 2024-01-15",
        )


def validate_month(month_str: str) -> str:
    """YYYY-MM 월 형식 검증"""
    if not isinstance(month_str, str):
        raise ValidationError("월 형식은 문자열이어야 합니다.", hint="예: 2024-01")
    try:
        parsed = datetime.strptime(month_str.strip(), "%Y-%m")
        return parsed.strftime("%Y-%m")
    except ValueError:
        raise ValidationError(
            "월 형식이 올바르지 않습니다 (YYYY-MM).",
            hint="예: 2024-01",
        )


def validate_amount(amount: Any) -> int:
    """금액 검증 (양수 정수)"""
    try:
        val = int(amount)
        if val <= 0:
            raise ValueError
        return val
    except (ValueError, TypeError):
        raise ValidationError(
            "금액은 0보다 큰 양수 정수여야 합니다.",
            hint="예: 15000",
        )


def validate_type(type_str: str) -> str:
    """거래 타입 검증 (income / expense)"""
    if not isinstance(type_str, str):
        raise ValidationError("타입은 income 또는 expense 여야 합니다.", hint="income 또는 expense")
    clean = type_str.strip().lower()
    if clean not in ("income", "expense"):
        raise ValidationError(
            f"지원하지 않는 거래 타입입니다: {type_str}",
            hint="income 또는 expense 중 하나를 입력하세요.",
        )
    return clean


@dataclass
class Transaction:
    """거래 내역 데이터 모델"""

    id: str
    type: str  # income | expense
    date: str  # YYYY-MM-DD
    amount: int  # > 0
    category: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.id:
            raise ValidationError("거래 ID는 비어있을 수 없습니다.")
        self.date = validate_date(self.date)
        self.type = validate_type(self.type)
        self.amount = validate_amount(self.amount)
        if not self.category or not self.category.strip():
            raise ValidationError("카테고리는 필수 입력값입니다.")
        self.category = self.category.strip()
        self.memo = (self.memo or "").strip()
        if isinstance(self.tags, str):
            self.tags = [t.strip() for t in self.tags.split(",") if t.strip()]
        else:
            self.tags = [str(t).strip() for t in self.tags if str(t).strip()]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "memo": self.memo,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Transaction":
        tags = data.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        return cls(
            id=str(data.get("id", "")),
            type=str(data.get("type", "")),
            date=str(data.get("date", "")),
            amount=int(data.get("amount", 0)),
            category=str(data.get("category", "")),
            memo=str(data.get("memo", "") or ""),
            tags=list(tags),
        )


@dataclass
class Category:
    """카테고리 데이터 모델"""

    name: str

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError("카테고리명은 비어있을 수 없습니다.", hint="예: food, transport")
        self.name = self.name.strip()

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Category":
        return cls(name=str(data.get("name", "")))


@dataclass
class Budget:
    """예산 데이터 모델"""

    month: str  # YYYY-MM
    amount: int  # >= 0

    def validate(self) -> None:
        self.month = validate_month(self.month)
        try:
            val = int(self.amount)
            if val < 0:
                raise ValueError
            self.amount = val
        except (ValueError, TypeError):
            raise ValidationError("예산 금액은 0 이상의 정수여야 합니다.", hint="예: 500000")

    def to_dict(self) -> dict[str, Any]:
        return {"month": self.month, "amount": self.amount}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Budget":
        return cls(
            month=str(data.get("month", "")),
            amount=int(data.get("amount", 0)),
        )
