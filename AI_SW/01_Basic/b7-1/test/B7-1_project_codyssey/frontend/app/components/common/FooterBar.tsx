import { PixelAsset } from "./PixelAsset";
import { WindowVariant } from "./WindowTitlebar";

type FooterIconType = "heart" | "clover" | "seven" | "star" | "carrot";

function FooterIcon({ type }: { type: FooterIconType }) {
  const assets = {
    heart: { src: "/assets/final-sprites/decor-heart.png", width: 53, height: 52 },
    clover: { src: "/assets/final-sprites/decor-clover.png", width: 74, height: 76 },
    seven: { src: "/assets/final-sprites/decor-seven.png", width: 61, height: 68 },
    star: { src: "/assets/final-sprites/decor-star.png", width: 48, height: 52 },
    carrot: { src: "/assets/final-sprites/decor-carrot.png", width: 65, height: 66 },
  } as const;

  return <PixelAsset {...assets[type]} className={`footer-icon footer-icon-${type}`} />;
}

export function FooterBar({ variant }: { variant: WindowVariant }) {
  const icons = variant === "signup"
    ? (["carrot", "star", "seven", "clover"] as const)
    : (["heart", "clover", "seven", "star"] as const);

  return (
    <footer className={`footer-bar ${variant}-footer-bar`} aria-hidden="true">
      {icons.map((icon) => <FooterIcon key={icon} type={icon} />)}
    </footer>
  );
}
