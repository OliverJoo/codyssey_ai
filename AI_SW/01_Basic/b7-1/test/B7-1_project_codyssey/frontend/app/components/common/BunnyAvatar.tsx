import { Sprite } from "./Sprite";

export function BunnyAvatar({ profile = false }: { profile?: boolean }) {
  return profile ? (
    <Sprite x={803} y={234} width={70} height={69} className="profile-bunny" label="Lucky Bunny" />
  ) : (
    <Sprite x={803} y={384} width={66} height={65} className="message-avatar-sprite" label="Lucky Bunny" />
  );
}
