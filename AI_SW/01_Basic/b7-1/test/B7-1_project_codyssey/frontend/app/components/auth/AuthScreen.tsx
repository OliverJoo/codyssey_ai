"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "../../lib/api";
import { AppLoading } from "../common/AppLoading";
import { FooterBar } from "../common/FooterBar";
import { PageDecor } from "../common/PageDecor";
import { WindowTitlebar } from "../common/WindowTitlebar";
import { AuthForm } from "./AuthForm";
import { AuthHero } from "./AuthHero";
import { AuthMode } from "./types";

export function AuthScreen({ mode }: { mode: AuthMode }) {
  const router = useRouter();
  const isSignup = mode === "signup";
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    // Refresh Cookie로 로그인 상태를 복구한 사용자는 채팅 화면으로 이동합니다.
    let active = true;
    authApi.restore().then((authenticated) => {
      if (!active) return;
      if (authenticated) router.replace("/chat");
      else setCheckingAuth(false);
    });
    return () => { active = false; };
  }, [router]);

  if (checkingAuth) return <AppLoading label="로그인 상태를 확인하고 있어요" />;

  return (
    <main className={`page-shell auth-page ${isSignup ? "signup-theme" : "login-theme"}`}>
      <PageDecor />
      <section className="auth-window pixel-window" aria-label={isSignup ? "회원가입" : "로그인"}>
        <WindowTitlebar variant={mode} />
        <div className="auth-content">
          <AuthHero mode={mode} />
          <AuthForm mode={mode} onAuthenticated={() => router.replace("/chat")} />
        </div>
        <FooterBar variant={mode} />
      </section>
    </main>
  );
}
