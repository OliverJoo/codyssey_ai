# Lucky Bunny API 명세

이 문서는 Lucky Bunny 프론트엔드와 FastAPI 백엔드가 함께 사용할 API 계약입니다. 모든 서비스 API는 `/api` 접두사를 유지합니다.

## 1. 공통 규칙

- 기본 주소: `${NEXT_PUBLIC_API_BASE_URL}`
- API 접두사: `/api`
- JSON 요청의 `Content-Type`: `application/json`
- 보호 API 인증: `Authorization: Bearer <access_token>`
- 날짜와 시간: ISO 8601 문자열
- 필드명: 백엔드의 Python 모델에 맞춰 `snake_case` 사용

FastAPI 기본 오류 응답을 사용합니다.

```json
{
  "detail": "오류 내용"
}
```

입력값 검증 실패는 `422 Unprocessable Entity`와 `detail` 배열을 반환할 수 있습니다.

## 2. 구현 현황

| 기능 | 메서드 | 경로 | 인증 | 상태 |
| --- | --- | --- | --- | --- |
| 회원가입 | `POST` | `/api/auth/signup` | 없음 | 구현됨 |
| 로그인 | `POST` | `/api/auth/login` | 없음 | 구현됨 |
| 토큰 갱신 | `POST` | `/api/auth/refresh` | refresh cookie | 구현됨 |
| 로그아웃 | `POST` | `/api/auth/logout` | refresh cookie | 구현됨 |
| AI 메시지 전송 | `POST` | `/api/chat` | Bearer JWT | 구현됨 |
| 과거 메시지 조회 | `GET` | `/api/me/chats` | Bearer JWT | 구현됨, 페이지네이션 추가 필요 |

## 3. 인증 API

### 3.1 회원가입

`POST /api/auth/signup`

요청:

```json
{
  "username": "lucky_user",
  "password": "lucky1234"
}
```

성공: `201 Created`

```json
{
  "id": 1,
  "username": "lucky_user",
  "created_at": "2026-08-09T00:00:00Z"
}
```

주요 오류:

- `409 Conflict`: 이미 사용 중인 아이디
- `422 Unprocessable Entity`: 아이디 또는 비밀번호 규칙 위반

회원가입 성공 응답에는 토큰이 없습니다. 현재 프론트엔드는 성공 후 로그인 API를 자동으로 호출합니다.

### 3.2 로그인

`POST /api/auth/login`

요청:

```json
{
  "username": "lucky_user",
  "password": "lucky1234"
}
```

성공: `200 OK`

```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "bearer"
}
```

백엔드는 `refresh_token`을 응답하는 동시에 HttpOnly cookie에도 설정합니다. 프론트엔드는 응답 본문의 refresh token을 저장하지 않고 access token만 메모리에 보관합니다.

주요 오류:

- `401 Unauthorized`: 아이디 또는 비밀번호 불일치
- `422 Unprocessable Entity`: 필수 JSON 항목 누락

### 3.3 토큰 갱신

`POST /api/auth/refresh`

- 요청 본문 없음
- 브라우저가 HttpOnly refresh cookie를 전송
- 프론트 요청 옵션에 `credentials: include` 사용

성공: `200 OK`

```json
{
  "access_token": "new-jwt-access-token",
  "refresh_token": "new-jwt-refresh-token",
  "token_type": "bearer"
}
```

실패: `401 Unauthorized`

### 3.4 로그아웃

`POST /api/auth/logout`

- 요청 본문 없음
- 백엔드는 refresh token cookie를 만료 처리

성공: `200 OK`

```json
{
  "message": "Successfully logged out"
}
```

## 4. 채팅 API

### 4.1 AI 메시지 전송

`POST /api/chat`

요청 헤더:

```text
Authorization: Bearer <access_token>
Content-Type: application/json
```

요청:

```json
{
  "message": "오늘 해야 할 일을 정리해줘"
}
```

메시지는 1자 이상 1,000자 이하입니다.

성공: `200 OK`

```json
{
  "id": 25,
  "user_message": "오늘 해야 할 일을 정리해줘",
  "ai_response": "좋아요. 우선순위부터 함께 정리해볼게요.",
  "error_status": null,
  "created_at": "2026-08-09T00:00:00Z"
}
```

AI 호출에 실패해도 현재 백엔드는 저장된 채팅 객체를 `200 OK`로 반환합니다.

```json
{
  "id": 26,
  "user_message": "다시 알려줘",
  "ai_response": "현재 응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요. (error: AI_TIMEOUT)",
  "error_status": "AI_TIMEOUT",
  "created_at": "2026-08-09T00:01:00Z"
}
```

`error_status` 값:

- `AI_TIMEOUT`: AI 응답 제한 시간 초과
- `AI_ERROR`: 기타 AI 서버 오류

### 4.2 과거 메시지 조회

`GET /api/me/chats`

현재 백엔드는 query parameter 없이 로그인한 사용자의 전체 기록을 오래된 순서부터 배열로 반환합니다.

성공: `200 OK`

```json
[
  {
    "id": 21,
    "user_message": "안녕",
    "ai_response": "안녕하세요!",
    "error_status": null,
    "created_at": "2026-08-09T00:00:00Z"
  }
]
```

서버 페이지네이션은 아직 지원하지 않습니다. 프론트는 현재 `nextCursor: null`, `hasMore: false`로 변환합니다.

## 5. 프론트 메시지 변환 규칙

백엔드의 채팅 한 건은 사용자 질문과 AI 답변을 함께 저장합니다. 프론트는 한 객체를 다음 두 메시지로 변환합니다.

```text
ChatResponse.user_message -> role: user
ChatResponse.ai_response  -> role: assistant
```

두 메시지의 안정적인 key는 다음처럼 만들 수 있습니다.

```text
chat-25-user
chat-25-assistant
```

`error_status`가 있으면 해당 assistant 메시지에 오류 및 재시도 UI를 표시합니다.

## 6. 보안 및 CORS 합의사항

- access token은 프론트 메모리에만 보관합니다.
- refresh token은 백엔드가 `HttpOnly`, `Secure`, 적절한 `SameSite` 속성의 cookie로 발급합니다.
- 백엔드는 모든 보호 API에서 JWT와 사용자 권한을 다시 검증합니다.
- 운영 환경의 CORS `allow_origins`는 실제 프론트엔드 origin만 허용합니다.
- `allow_credentials=True`를 사용할 때 wildcard origin(`*`)을 사용하지 않습니다.
- 로그인 시도 제한, refresh token 폐기 및 회전 정책은 백엔드에서 처리합니다.

## 7. 프론트 연결 상태

`app/lib/api.ts`에 다음 연동이 반영되어 있습니다.

- JSON 로그인 요청 및 `access_token` 응답 처리
- HttpOnly refresh cookie를 이용한 access token 갱신
- `POST /api/chat` AI 메시지 전송
- `GET /api/me/chats` 전체 대화 기록 조회
- `ChatResponse`를 사용자·AI 메시지로 변환
- `error_status` 표시 및 원래 사용자 질문 재시도

API 명세가 확정되기 전까지 `NEXT_PUBLIC_API_BASE_URL`을 비워두면 demo 모드가 유지됩니다.
