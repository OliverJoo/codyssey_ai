import { PixelAsset } from "./PixelAsset";

export function PageDecor() {
  return (
    <div className="page-decor" aria-hidden="true">
      <PixelAsset src="/assets/final-sprites/decor-heart.png" width={53} height={52} className="page-decor-heart" />
      <PixelAsset src="/assets/final-sprites/decor-clover.png" width={74} height={76} className="page-decor-clover" />
      <PixelAsset src="/assets/final-sprites/decor-star.png" width={48} height={52} className="page-decor-star" />
      <PixelAsset src="/assets/final-sprites/decor-carrot.png" width={65} height={66} className="page-decor-carrot" />
      <PixelAsset src="/assets/final-sprites/decor-seven.png" width={61} height={68} className="page-decor-seven" />
      <PixelAsset src="/assets/final-sprites/decor-sparkle.png" width={43} height={51} className="page-decor-sparkle" />
      <PixelAsset src="/assets/final-sprites/decor-cloud-left.png" width={80} height={53} className="page-decor-cloud page-decor-cloud-left" />
      <PixelAsset src="/assets/final-sprites/decor-cloud-right.png" width={127} height={75} className="page-decor-cloud page-decor-cloud-right" />
    </div>
  );
}
