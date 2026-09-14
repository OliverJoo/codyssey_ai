import { PixelAsset } from "./PixelAsset";

export type WindowVariant = "login" | "signup" | "chat";

export function WindowTitlebar({ variant }: { variant: WindowVariant }) {
  const controls = {
    login: { src: "/assets/final-sprites/controls-login.png", width: 87, height: 35 },
    signup: { src: "/assets/final-sprites/controls-signup.png", width: 90, height: 35 },
    chat: { src: "/assets/final-sprites/controls-chat.png", width: 99, height: 38 },
  } as const;

  return (
    <header className={`window-titlebar ${variant}-titlebar`}>
      <div className="window-brand">
        <PixelAsset
          src="/assets/final-sprites/brand-rabbit.png"
          width={101}
          height={112}
          className="window-brand-rabbit"
        />
        <span>LUCKY BUNNY</span>
      </div>
      <PixelAsset {...controls[variant]} className="titlebar-controls" />
    </header>
  );
}
