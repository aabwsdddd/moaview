import React, { type ReactNode } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchResults } from "../components/search/SearchResults";
import { OfferComparisonTable } from "../components/works/OfferComparisonTable";
import type { SearchResult, WorkOffer } from "../lib/api";

vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: { children: ReactNode; href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

const searchResult: SearchResult = {
  id: "work_moonlight_archive",
  title: "달빛 기록관",
  authors: ["한서윤"],
  content_type: "webtoon",
  description: "비밀스러운 기록관에서 시작되는 판타지 로맨스.",
  platforms: [
    {
      id: "platform_kakaopage",
      label: "카카오페이지",
      offer_id: "offer_kakao_moonlight",
      source_url: "https://example.com/kakao/moonlight-archive",
      last_updated_at: "2026-05-01T09:10:00Z",
    },
  ],
  max_free_episodes: 7,
  lowest_confirmed_price: 350,
  lowest_coupon_expected_price: 280,
  best_platform_label: "카카오페이지",
};

const offer: WorkOffer = {
  id: "offer_kakao_moonlight",
  work_id: "work_moonlight_archive",
  platform: "카카오페이지",
  platform_id: "platform_kakaopage",
  source_url: "https://example.com/kakao/moonlight-archive",
  last_updated_at: "2026-05-01T09:10:00Z",
  free_episode_count: 7,
  wait_free_available: true,
  base_price: 400,
  instant_discounted_price: 350,
  coupon_expected_price: 280,
  cashback_adjusted_price: 266,
  effective_price_for_sort: 280,
  price_confidence: "estimated",
  calculation_note: "Coupon price is expected because coupon terms require user action or issuance.",
  active_promotions: [],
  active_coupons: [
    {
      id: "coupon_kakao_code_fixture",
      platform: "카카오페이지",
      coupon_type: "code_required",
      coupon_code: "FIXTURE10",
      title: "fixture 코드 10% 쿠폰",
      label: "쿠폰 적용 예상가",
    },
  ],
};

describe("frontend MVP flow components", () => {
  it("renders search cards with platform and price summary labels", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ count: 1 }) }));

    render(<SearchResults query="달빛" results={[searchResult]} />);

    expect(screen.getByRole("heading", { name: "달빛 기록관" })).toBeInTheDocument();
    expect(screen.getByText("한서윤")).toBeInTheDocument();
    expect(screen.getByText("플랫폼: 카카오페이지")).toBeInTheDocument();
    expect(screen.getByText("쿠폰 적용 예상 최저가")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /달빛 기록관/ })).toHaveAttribute("href", "/works/work_moonlight_archive");

    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalledWith(expect.stringContaining("/api/events/search"), expect.objectContaining({ method: "POST" })));
    vi.unstubAllGlobals();
  });

  it("shows offer comparison labels and records platform click before opening CTA", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ count: 1 }) });
    const openMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    vi.stubGlobal("open", openMock);

    render(<OfferComparisonTable offers={[offer]} workId="work_moonlight_archive" />);

    expect(screen.getAllByText("확정가")[0]).toBeInTheDocument();
    expect(screen.getAllByText("쿠폰 적용 예상가")[0]).toBeInTheDocument();
    expect(screen.getAllByText("캐시백 포함 체감가")[0]).toBeInTheDocument();
    expect(screen.getByText("Coupon price is expected because coupon terms require user action or issuance.")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "쿠폰 받고 보기" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/api/events/platform-click"), expect.objectContaining({ method: "POST" })));
    expect(openMock).toHaveBeenCalledWith("https://example.com/kakao/moonlight-archive", "_blank", "noopener,noreferrer");

    vi.unstubAllGlobals();
  });
});
