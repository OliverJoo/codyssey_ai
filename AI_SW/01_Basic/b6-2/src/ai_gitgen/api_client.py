"""OpenAI 호환 Chat Completions API 호출을 담당합니다."""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request


class APIError(RuntimeError):
    """사용자가 원인을 확인할 수 있는 AI API 오류입니다."""


def request_completion(
    *,
    api_url: str,
    api_key: str,
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    timeout: float = 30.0,
) -> str:
    """API를 한 번 호출하고 응답 텍스트를 반환합니다."""
    payload = json.dumps(
        {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            reason = "API 키가 거부되었습니다. AI_API_KEY를 확인하세요."
        elif exc.code == 429:
            reason = "API 호출 한도 또는 사용량 제한을 확인하세요."
        else:
            reason = f"API 서버가 HTTP {exc.code} 오류를 반환했습니다."
        raise APIError(reason) from exc
    except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
        raise APIError(f"네트워크 연결에 실패했습니다: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise APIError("API 응답이 올바른 JSON이 아닙니다.") from exc

    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise APIError("API 응답에 choices[0].message.content가 없습니다.") from exc
