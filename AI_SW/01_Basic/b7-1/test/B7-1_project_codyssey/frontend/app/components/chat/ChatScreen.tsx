"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi, chatApi, ChatMessage } from "../../lib/api";
import { AppLoading } from "../common/AppLoading";
import { FooterBar } from "../common/FooterBar";
import { PageDecor } from "../common/PageDecor";
import { WindowTitlebar } from "../common/WindowTitlebar";
import { ChatComposer } from "./ChatComposer";
import { ChatMessageList } from "./ChatMessageList";
import { ChatProfileBar } from "./ChatProfileBar";
import { appendMessages, createUserMessage, mergeMessages } from "./messageUtils";

export function ChatScreen() {
  const router = useRouter();
  const listRef = useRef<HTMLDivElement>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyLoadingMore, setHistoryLoadingMore] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  // 메시지가 추가된 다음 DOM 높이가 반영된 시점에 마지막 메시지로 이동합니다.
  const scrollToBottom = () => requestAnimationFrame(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  });

  const loadInitialHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError("");
    try {
      const page = await chatApi.history(null);
      setMessages(page.messages);
      setNextCursor(page.nextCursor);
      setHasMore(page.hasMore);
      requestAnimationFrame(() => {
        if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
      });
    } catch (caught) {
      setHistoryError(caught instanceof Error ? caught.message : "대화 기록을 불러오지 못했어요. 다시 시도해 주세요.");
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    // 보호 화면 진입 시 Access Token을 복구하고 인증된 경우에만 기록을 조회합니다.
    let active = true;
    authApi.restore().then((authenticated) => {
      if (!active) return;
      if (!authenticated) return router.replace("/login");
      setCheckingAuth(false);
      loadInitialHistory();
    });
    return () => { active = false; };
  }, [loadInitialHistory, router]);

  const loadOlder = useCallback(async () => {
    if (!nextCursor || !hasMore || historyLoadingMore) return;
    const list = listRef.current;
    const previousHeight = list?.scrollHeight ?? 0;
    const previousTop = list?.scrollTop ?? 0;
    setHistoryLoadingMore(true);
    setHistoryError("");
    try {
      const page = await chatApi.history(nextCursor);
      setMessages((current) => mergeMessages(current, page.messages));
      setNextCursor(page.nextCursor);
      setHasMore(page.hasMore);
      requestAnimationFrame(() => {
        // 이전 기록이 위에 추가되어도 사용자가 보던 스크롤 위치를 유지합니다.
        if (list) list.scrollTop = list.scrollHeight - previousHeight + previousTop;
      });
    } catch {
      setHistoryError("이전 대화를 불러오지 못했어요.");
    } finally {
      setHistoryLoadingMore(false);
    }
  }, [hasMore, historyLoadingMore, nextCursor]);

  async function sendExisting(message: ChatMessage) {
    if (sending) return;
    // AI 오류 메시지를 재시도할 때는 저장해 둔 원래 사용자 질문을 전송합니다.
    const content = message.retryContent ?? message.content;
    const replacingAssistantError = message.role === "assistant" && Boolean(message.retryContent);
    setSending(true);
    setMessages((current) => current.map((item) => (
      item.id === message.id ? { ...item, status: "sending" } : item
    )));
    try {
      const reply = await chatApi.send(content);
      setMessages((current) => appendMessages(
        current
          .filter((item) => !(replacingAssistantError && item.id === message.id))
          .map((item) => item.id === message.id ? { ...item, status: "success" } : item),
        [reply],
      ));
      scrollToBottom();
    } catch {
      setMessages((current) => current.map((item) => (
        item.id === message.id ? { ...item, status: "error" } : item
      )));
    } finally {
      setSending(false);
    }
  }

  async function handleSend() {
    const content = draft.trim();
    if (!content || sending) return;
    const userMessage = createUserMessage(content);
    setDraft("");
    // 낙관적 업데이트로 질문을 먼저 보여주고 API 응답을 다음 메시지로 추가합니다.
    setMessages((current) => appendMessages(current, [userMessage]));
    scrollToBottom();
    await sendExisting(userMessage);
  }

  async function handleLogout() {
    if (loggingOut) return;
    setLoggingOut(true);
    try {
      await authApi.logout();
    } finally {
      setMessages([]);
      router.replace("/login");
    }
  }

  if (checkingAuth) return <AppLoading label="Lucky를 만나러 가고 있어요" />;

  return (
    <main className="page-shell chat-page">
      <PageDecor />
      <section className="chat-window pixel-window" aria-label="Lucky Bunny AI 채팅">
        <WindowTitlebar variant="chat" />
        <ChatProfileBar loggingOut={loggingOut} onLogout={handleLogout} />
        <ChatMessageList
          listRef={listRef}
          messages={messages}
          historyLoading={historyLoading}
          historyLoadingMore={historyLoadingMore}
          historyError={historyError}
          hasMore={hasMore}
          sending={sending}
          onScrollTop={loadOlder}
          onLoadOlder={loadOlder}
          onRetryHistory={messages.length ? loadOlder : loadInitialHistory}
          onRetryMessage={sendExisting}
        />
        <ChatComposer
          draft={draft}
          sending={sending}
          onDraftChange={setDraft}
          onSend={handleSend}
        />
        <FooterBar variant="chat" />
      </section>
    </main>
  );
}
