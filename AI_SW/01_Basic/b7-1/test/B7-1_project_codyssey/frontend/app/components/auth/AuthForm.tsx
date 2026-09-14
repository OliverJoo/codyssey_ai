"use client";

import { FormEvent, useState } from "react";
import { authApi } from "../../lib/api";
import { Sprite } from "../common/Sprite";
import { FieldIcon } from "./FieldIcon";
import { AuthMode } from "./types";

type AuthFormProps = {
  mode: AuthMode;
  onAuthenticated: () => void;
};

export function AuthForm({ mode, onAuthenticated }: AuthFormProps) {
  const isSignup = mode === "signup";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting) return;
    setError("");

    // API 요청 전에 비어 있는 필드와 비밀번호 확인 값을 우선 검사합니다.
    if (!username.trim() || !password || (isSignup && !passwordConfirm)) {
      setError(isSignup ? "모든 항목을 입력해 주세요." : "아이디와 비밀번호를 입력해 주세요.");
      return;
    }
    if (isSignup && password !== passwordConfirm) {
      setError("비밀번호가 일치하지 않아요.");
      return;
    }

    setSubmitting(true);
    try {
      // 회원가입 성공 시 authApi가 로그인까지 처리하므로 동일한 완료 콜백을 사용합니다.
      if (isSignup) await authApi.signup(username.trim(), password);
      else await authApi.login(username.trim(), password);
      onAuthenticated();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "문제가 발생했어요. 잠시 후 다시 시도해 주세요.");
      if (!isSignup) setPassword("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit} noValidate>
      <label className="field-label" htmlFor={`${mode}-username`}>아이디</label>
      <div className="field-wrap">
        <FieldIcon type="user" />
        <input
          id={`${mode}-username`}
          name="username"
          autoComplete="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          disabled={submitting}
          aria-invalid={Boolean(error)}
        />
      </div>

      <label className="field-label" htmlFor={`${mode}-password`}>비밀번호</label>
      <div className="field-wrap">
        <FieldIcon type="lock" />
        <input
          id={`${mode}-password`}
          name="password"
          type="password"
          autoComplete={isSignup ? "new-password" : "current-password"}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          disabled={submitting}
          aria-invalid={Boolean(error)}
        />
      </div>

      {isSignup && (
        <>
          <label className="field-label" htmlFor="signup-password-confirm">비밀번호 확인</label>
          <div className="field-wrap">
            <FieldIcon type="lock" />
            <input
              id="signup-password-confirm"
              name="passwordConfirm"
              type="password"
              autoComplete="new-password"
              value={passwordConfirm}
              onChange={(event) => setPasswordConfirm(event.target.value)}
              disabled={submitting}
              aria-invalid={Boolean(error)}
            />
          </div>
        </>
      )}

      <div className={`form-error ${error ? "visible" : ""}`} role="alert" aria-live="assertive">{error}</div>
      <button className="auth-submit" type="submit" disabled={submitting}>
        {submitting ? (isSignup ? "가입 중..." : "로그인 중...") : (isSignup ? "회원가입" : "로그인")}
      </button>
      <div className="auth-divider">
        <Sprite x={214} y={759} width={19} height={20} className="divider-heart" />
      </div>
      <a className="auth-link" href={isSignup ? "/login" : "/signup"}>
        {isSignup ? "로그인으로 돌아가기" : "회원가입"}
      </a>
    </form>
  );
}
