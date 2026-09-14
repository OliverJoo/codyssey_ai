import { BunnyAvatar } from "../common/BunnyAvatar";
import { Sprite } from "../common/Sprite";

type ChatProfileBarProps = {
  loggingOut: boolean;
  onLogout: () => void;
};

export function ChatProfileBar({ loggingOut, onLogout }: ChatProfileBarProps) {
  return (
    <div className="chat-profilebar">
      <div className="chat-identity">
        <BunnyAvatar profile />
        <div>
          <strong>LUCKY BUNNY</strong>
          <span className="online"><i />ONLINE</span>
        </div>
      </div>
      <button
        className="logout-button sprite-button"
        type="button"
        onClick={onLogout}
        disabled={loggingOut}
        aria-label="로그아웃"
      >
        <Sprite x={1338} y={247} width={129} height={46} className="logout-sprite" />
      </button>
    </div>
  );
}
