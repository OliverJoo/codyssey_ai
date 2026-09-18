"""모듈 사이에서 주고받는 데이터 구조입니다."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GitChanges:
    """현재 저장소의 변경 정보입니다."""

    root: str
    branch: str
    status: str
    diff: str
    files: tuple[str, ...]


@dataclass(frozen=True)
class SafetyReport:
    """민감정보 마스킹과 크기 제한 결과입니다."""

    status: str
    diff: str
    masked_count: int = 0
    files_used: int = 0
    files_total: int = 0
    lines_used: int = 0
    truncated: bool = False


@dataclass(frozen=True)
class GeneratedMessage:
    """검증을 마친 최종 메시지입니다."""

    title: str
    body: str
    warnings: tuple[str, ...] = field(default_factory=tuple)
