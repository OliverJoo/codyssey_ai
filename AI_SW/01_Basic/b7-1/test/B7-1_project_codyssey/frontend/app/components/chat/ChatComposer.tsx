import { KeyboardEvent } from "react";
import { PixelAsset } from "../common/PixelAsset";

type ChatComposerProps = {
  draft: string;
  sending: boolean;
  onDraftChange: (draft: string) => void;
  onSend: () => void;
};

export function ChatComposer({
  draft,
  sending,
  onDraftChange,
  onSend,
}: ChatComposerProps) {
  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter는 전송하고 Shift+Enter는 줄바꿈으로 유지합니다.
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSend();
    }
  }

  return (
    <div className="composer-wrap">
      <PixelAsset
        src="/assets/final-sprites/decor-clover.png"
        width={74}
        height={76}
        className="composer-clover"
      />
      <label className="sr-only" htmlFor="chat-message">메시지</label>
      <textarea
        id="chat-message"
        rows={1}
        value={draft}
        onChange={(event) => onDraftChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="메시지를 입력해 주세요"
        disabled={sending}
      />
      <button
        className="send-button sprite-button"
        type="button"
        onClick={onSend}
        disabled={!draft.trim() || sending}
        aria-label="전송"
      >
        <PixelAsset
          src="/assets/final-sprites/send-carrot.png"
          width={124}
          height={63}
          className="send-sprite"
        />
      </button>
    </div>
  );
}
