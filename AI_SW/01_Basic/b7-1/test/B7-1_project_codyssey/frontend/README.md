# Lucky Bunny Frontend

픽셀 아트 AI 챗봇 프론트엔드입니다. 로그인, 회원가입, 한 채팅방의 연속 대화와 과거 메시지 페이지네이션을 제공합니다.

## 기술 구성

- Next.js App Router
- React
- TypeScript
- Mona 웹 폰트
- FastAPI 백엔드 API + JWT 인증 연동

## 로컬 실행

Node.js 20.9 이상이 필요합니다.

```bash
npm install
cp .env.example .env.local
npm run dev
```

브라우저에서 `http://localhost:3000`을 열면 로그인 화면으로 이동합니다.

## 화면 경로

- `/login`: 로그인
- `/signup`: 회원가입
- `/chat`: AI 채팅

`NEXT_PUBLIC_API_BASE_URL`이 비어 있으면 demo 모드가 활성화됩니다. 임의의 아이디와 비밀번호로 로그인할 수 있고, `error` 아이디는 로그인 오류, `lucky` 아이디는 회원가입 중복 오류를 확인하는 데 사용합니다. 채팅 메시지에 `오류`를 포함하면 AI 답변 실패와 재시도 상태를 확인할 수 있습니다.

## 환경변수

```env
NEXT_PUBLIC_API_BASE_URL=https://api.example.com
NEXT_PUBLIC_SITE_URL=https://example.com
```

API 주소는 브라우저에 공개되는 값이므로 비밀키를 넣으면 안 됩니다.

## API 명세

모든 서비스 API는 `/api` 접두사를 유지합니다. 현재 백엔드 구현과 프론트 요구사항을 반영한 전체 계약은 [API_SPEC.md](./API_SPEC.md)에 정리되어 있습니다.

주요 경로:

- `POST /api/auth/signup`: 회원가입
- `POST /api/auth/login`: 로그인
- `POST /api/auth/refresh`: HttpOnly cookie 기반 토큰 갱신
- `POST /api/auth/logout`: 로그아웃
- `POST /api/chat`: AI 메시지 전송
- `GET /api/me/chats`: 전체 과거 기록 조회

## JWT와 공개 서비스 보안

- access token은 `localStorage`에 저장하지 않고 현재 탭의 메모리에만 유지합니다.
- refresh token은 백엔드가 `HttpOnly`, `Secure`, 적절한 `SameSite` 속성의 쿠키로 발급해야 합니다.
- 프론트 요청은 refresh cookie 전송을 위해 `credentials: include`를 사용합니다.
- 백엔드는 허용할 프론트엔드 origin을 정확히 지정하고 credential CORS를 설정해야 합니다.
- 화면의 로그인 여부 확인은 사용자 경험을 위한 처리입니다. 실제 권한 검증은 모든 보호 API에서 백엔드가 수행해야 합니다.
- 비밀번호 해시, 로그인 시도 제한, 토큰 폐기와 만료 정책은 백엔드에서 처리해야 합니다.

## 검증

```bash
npm run lint
npm run build
```

이 프로젝트는 로컬 개발과 API 연동 준비까지만 포함하며 배포 설정은 포함하지 않습니다.
