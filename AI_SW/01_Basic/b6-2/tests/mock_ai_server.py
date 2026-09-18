#!/usr/bin/env python3
"""비용과 네트워크 없이 API 호출을 시연하는 로컬 서버입니다."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class MockAIHandler(BaseHTTPRequestHandler):
    """요청 프롬프트에 맞는 고정 commit 또는 PR JSON을 반환합니다."""

    requests: list[dict] = []

    def do_POST(self) -> None:  # noqa: N802 - HTTP 표준 메서드 이름입니다.
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        self.__class__.requests.append(payload)
        prompt = payload.get("messages", [{}])[0].get("content", "")
        if '"how_to_test"' in prompt:
            content = json.dumps(
                {
                    "title": "Git 변경 기반 PR 초안 생성 기능 추가",
                    "why": ["반복적인 PR 설명 작성을 줄이기 위해"],
                    "what": ["변경 내용을 읽어 PR 제목과 본문을 생성"],
                    "how_to_test": ["자동 테스트와 로컬 시연 스크립트 실행"],
                },
                ensure_ascii=False,
            )
        else:
            content = json.dumps(
                {
                    "title": "feat: AI Git 메시지 생성기 추가",
                    "body": ["src/ai_gitgen 모듈 추가", "Git 변경 기반 초안 생성"],
                },
                ensure_ascii=False,
            )
        body = json.dumps(
            {"choices": [{"message": {"content": content}}]},
            ensure_ascii=False,
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        """테스트 출력을 간결하게 유지합니다."""
        return


def start_server(port: int = 0) -> ThreadingHTTPServer:
    """백그라운드 테스트에서 사용할 서버 객체를 만듭니다."""
    return ThreadingHTTPServer(("127.0.0.1", port), MockAIHandler)


def main() -> int:
    """셸 시연용 서버를 실행하고 선택적으로 포트를 파일에 기록합니다."""
    parser = argparse.ArgumentParser(description="로컬 모의 AI API 서버")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--port-file")
    args = parser.parse_args()
    server = start_server(args.port)
    if args.port_file:
        Path(args.port_file).write_text(str(server.server_port), encoding="utf-8")
    print(f"Mock AI API: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
