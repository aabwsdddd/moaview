import React, { type ReactNode } from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import LoginPage from "../app/login/page";
import { FavoritesList } from "../components/favorites/FavoritesList";
import { FavoriteButton } from "../components/favorites/FavoriteButton";
import { createSupabaseBrowserClient } from "../lib/supabase/client";
import { createSupabaseServerClient } from "../lib/supabase/server";

vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: { children: ReactNode; href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

describe("auth and favorites UI", () => {
  it("renders the login page with email magic link and Google copy", () => {
    render(<LoginPage />);

    expect(screen.getByRole("heading", { name: "로그인" })).toBeInTheDocument();
    expect(screen.getByLabelText("이메일 주소")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "이메일 매직 링크 받기" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Google로 계속하기" })).toBeInTheDocument();
  });

  it("shows login guidance when logged out on favorite CTA", async () => {
    render(<FavoriteButton workId="work_moonlight_archive" />);

    expect(await screen.findByText("로그인 후 찜할 수 있어요")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "로그인하고 찜하기" })).toHaveAttribute("href", "/login");
  });

  it("renders the favorites empty state", () => {
    render(<FavoritesList items={[]} />);

    expect(screen.getByRole("heading", { name: "찜한 작품" })).toBeInTheDocument();
    expect(screen.getByText("아직 찜한 작품이 없어요.")).toBeInTheDocument();
  });

  it("does not crash Supabase utilities when env vars are missing", () => {
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_URL", "");
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", "");
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "");

    expect(createSupabaseBrowserClient()).toBeNull();
    expect(createSupabaseServerClient()).toBeNull();

    vi.unstubAllEnvs();
  });
});
