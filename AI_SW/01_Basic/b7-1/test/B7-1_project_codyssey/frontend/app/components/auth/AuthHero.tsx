import { PixelAsset } from "../common/PixelAsset";
import { AuthMode } from "./types";

export function AuthHero({ mode }: { mode: AuthMode }) {
  return mode === "login" ? (
    <PixelAsset
      src="/assets/final-sprites/login-hero.png"
      width={288}
      height={277}
      className="auth-hero-art login-hero-art"
      alt="손을 들고 인사하는 Lucky Bunny"
    />
  ) : (
    <PixelAsset
      src="/assets/final-sprites/signup-hero.png"
      width={279}
      height={279}
      className="auth-hero-art signup-hero-art"
      alt="하트를 안고 있는 Lucky Bunny"
    />
  );
}
