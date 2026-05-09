import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MoaView",
  description: "Fixture-based Korean webtoon and web novel platform comparison MVP.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
