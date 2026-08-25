"""공통 관심사 분리를 위한 데코레이터 모듈"""

import functools
import sys
import time
from typing import Any, Callable, Optional
from budget_app.models import ValidationError


def handle_cli_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    CLI 명령어 실행 중 발생하는 도메인 예외(ValidationError 등)를 포착하여
    스택트레이스 대신 [오류], [힌트] 형식으로 출력하고 비정상 종료(exit code 1)합니다.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            print(f"[오류] {e.message}")
            if e.hint:
                print(f"[힌트] {e.hint}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n[알림] 작업이 사용자에 의해 중단되었습니다.")
            sys.exit(130)
        except Exception as e:
            print(f"[오류] 예기치 않은 오류가 발생했습니다: {e}")
            sys.exit(1)

    return wrapper


def measure_execution_time(
    callback: Optional[Callable[[str], None]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    함수 실행 시간을 측정하여 콜백 또는 로거로 전달하는 데코레이터.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                msg = f"[성능] {func.__name__} 실행 시간: {elapsed_ms:.2f}ms"
                if callback:
                    callback(msg)

        return wrapper

    return decorator
