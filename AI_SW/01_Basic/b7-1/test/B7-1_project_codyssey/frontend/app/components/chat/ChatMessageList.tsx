import { RefObject } from "react";
import { ChatMessage } from "../../lib/api";
import { BunnyAvatar } from "../common/BunnyAvatar";
import { MessageBubble } from "./MessageBubble";

type ChatMessageListProps = {
  listRef: RefObject<HTMLDivElement | null>;
  messages: ChatMessage[];
  historyLoading: boolean;
  historyLoadingMore: boolean;
  historyError: string;
  hasMore: boolean;
  sending: boolean;
  onScrollTop: () => void;
  onLoadOlder: () => void;
  onRetryHistory: () => void;
  onRetryMessage: (message: ChatMessage) => void;
};

export function ChatMessageList({
  listRef,
  messages,
  historyLoading,
  historyLoadingMore,
  historyError,
  hasMore,
  sending,
  onScrollTop,
  onLoadOlder,
  onRetryHistory,
  onRetryMessage,
}: ChatMessageListProps) {
  return (
    <div
      className="chat-body"
      ref={listRef}
      onScroll={() => {
        // 목록 상단에 가까워지면 다음 과거 기록 페이지를 요청합니다.
        if ((listRef.current?.scrollTop ?? 100) < 56) onScrollTop();
      }}
      aria-live="polite"
    >
      {historyLoading && (
        <div className="history-state">
          <BunnyAvatar profile />
          <p>지난 대화를 불러오고 있어요...</p>
        </div>
      )}
      {!historyLoading && hasMore && !historyLoadingMore && (
        <button className="load-older" type="button" onClick={onLoadOlder}>
          이전 대화 더 보기
        </button>
      )}
      {historyLoadingMore && (
        <div className="history-more">
          <div className="typing-dots"><i /><i /><i /></div>
        </div>
      )}
      {historyError && (
        <div className="history-error" role="alert">
          <p>{historyError}</p>
          <button type="button" onClick={onRetryHistory}>다시 시도</button>
        </div>
      )}

      {!historyLoading && !historyError && messages.length === 0 && (
        <MessageBubble
          message={{
            id: "welcome",
            role: "assistant",
            content: "안녕하세요! 저는 Lucky예요. 무엇을 도와드릴까요?",
            status: "success",
            createdAt: new Date().toISOString(),
          }}
          onRetry={() => {}}
        />
      )}
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          onRetry={() => onRetryMessage(message)}
        />
      ))}
      {sending && (
        <div className="typing-row">
          <BunnyAvatar />
          <div className="typing-bubble">
            <div className="typing-dots"><i /><i /><i /></div>
          </div>
        </div>
      )}
    </div>
  );
}
