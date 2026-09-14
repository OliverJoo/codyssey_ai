import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatMessage } from "../../lib/api";
import { BunnyAvatar } from "../common/BunnyAvatar";
import { Sprite } from "../common/Sprite";
import { CarrotAvatar } from "./CarrotAvatar";
import { formatTime } from "./messageUtils";

type MessageBubbleProps = {
  message: ChatMessage;
  onRetry: () => void;
};

export function MessageBubble({ message, onRetry }: MessageBubbleProps) {
  const isUser = message.role === "user";
  // 메시지 재시도 정책이 확정될 때까지 버튼을 임시로 숨깁니다.
  const showRetryButton = false;

  return (
    <article className={`message-row ${isUser ? "user-message" : "assistant-message"}`}>
      <div className="message-avatar">
        {isUser ? <CarrotAvatar /> : <BunnyAvatar />}
      </div>
      <div className="message-column">
        <div className="message-meta">
          <strong>{isUser ? "" : "LUCKY BUNNY"}</strong>
          <time dateTime={message.createdAt}>{formatTime(message.createdAt)}</time>
        </div>
        <div className={`message-bubble ${message.status === "sending" ? "pending" : ""}`}>
          {isUser ? (
            message.content.split("\n").map((line, index) => (
              <span className="plain-message-line" key={`${message.id}-${index}`}>{line}</span>
            ))
          ) : (
            // AI 답변만 Markdown으로 렌더링하고 사용자 입력은 일반 텍스트로 표시합니다.
            <div className="markdown-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  a: (props) => <a {...props} target="_blank" rel="noopener noreferrer" />,
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>
        {message.status === "error" && (
          <div className="message-error" role="alert">
            <Sprite x={878} y={695} width={26} height={25} className="warning-sprite" />
            <p>답변을 불러오지 못했어요. 다시 시도해 주세요.</p>
            {showRetryButton && <button type="button" onClick={onRetry}>다시 시도</button>}
          </div>
        )}
      </div>
    </article>
  );
}
