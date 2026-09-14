import Image from "next/image";

type PixelAssetProps = {
  src: string;
  width: number;
  height: number;
  className?: string;
  alt?: string;
};

export function PixelAsset({
  src,
  width,
  height,
  className = "",
  alt = "",
}: PixelAssetProps) {
  // 픽셀 아트가 흐려지지 않도록 Next.js 이미지 최적화를 사용하지 않습니다.
  return (
    <Image
      className={`pixel-asset ${className}`}
      src={src}
      width={width}
      height={height}
      alt={alt}
      unoptimized
    />
  );
}
