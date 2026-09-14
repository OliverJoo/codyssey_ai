import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"),
  title: "Lucky Bunny — AI Chatbot",
  description: "행운 가득한 픽셀 토끼 Lucky와 나누는 작은 AI 대화",
  icons: { icon: "/assets/lucky-mascot-v2.png" },
  openGraph: {
    title: "Lucky Bunny — AI Chatbot",
    description: "행운 가득한 픽셀 토끼 Lucky와 나누는 작은 AI 대화",
    images: [{ url: "/og.png", width: 1672, height: 941, alt: "Lucky Bunny AI Chatbot" }],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
