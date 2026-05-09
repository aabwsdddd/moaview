import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { AuthStatus } from "../components/auth/AuthStatus";
import "./globals.css";

export const metadata: Metadata = {
  title: "MoaView",
  description: "Fixture-based Korean webtoon and web novel platform comparison MVP.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="ko">
      <body>
        <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
          <nav className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-6 py-4">
            <Link className="text-xl font-black tracking-tight text-moa" href="/">
              MoaView
            </Link>
            <div className="flex items-center gap-4">
              <Link className="text-sm font-semibold text-slate-700 transition hover:text-moa" href="/search">
                검색
              </Link>
              <Link className="text-sm font-semibold text-slate-700 transition hover:text-moa" href="/favorites">
                찜한 작품
              </Link>
              <Link className="text-sm font-semibold text-slate-700 transition hover:text-moa" href="/notifications">
                알림
              </Link>
              <Link className="text-sm font-semibold text-slate-700 transition hover:text-moa" href="/admin/merge-review">
                병합 검토
              </Link>
              <AuthStatus />
            </div>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
