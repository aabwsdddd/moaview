import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import AdminAnalyticsPage from "../app/admin/analytics/page";

vi.mock("../lib/api", () => ({
  getAdminAnalyticsSummary: vi.fn(async () => ({
    total_searches: 3,
    total_detail_views: 2,
    total_platform_clicks: 1,
    total_favorites: 1,
    search_to_detail_rate: 0.6667,
    detail_to_platform_click_rate: 0.5,
    favorite_rate: 0.5,
    coupon_cta_click_rate: 0.5,
    notification_click_rate: 0,
    returning_user_7_day_rate: null,
    top_clicked_works: [{ work_id: "work_moonlight_archive", title: "달빛 기록관", count: 1 }],
    top_clicked_platforms: [{ platform_id: "platform_kakaopage", label: "카카오페이지", count: 1 }],
    top_coupon_cta_works: [],
    generated_at: "2026-05-09T00:00:00Z",
  })),
}));

describe("admin analytics dashboard", () => {
  it("renders KPI cards, top tables, empty states, and timestamp", async () => {
    render(await AdminAnalyticsPage());

    expect(screen.getByRole("heading", { name: "MVP 분석 대시보드" })).toBeInTheDocument();
    expect(screen.getByText("TODO: 실제 운영 전 Supabase Auth 기반 관리자 권한 검사를 연결해야 합니다.")).toBeInTheDocument();
    expect(screen.getByText("검색 수")).toBeInTheDocument();
    expect(screen.getByText("상세 진입 수")).toBeInTheDocument();
    expect(screen.getByText("플랫폼 클릭 수")).toBeInTheDocument();
    expect(screen.getByText("검색→상세 전환율")).toBeInTheDocument();
    expect(screen.getByText("상세→클릭 전환율")).toBeInTheDocument();
    expect(screen.getByText("찜 등록률")).toBeInTheDocument();
    expect(screen.getByText("쿠폰 CTA 클릭률")).toBeInTheDocument();
    expect(screen.getByText("알림 클릭률")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "많이 클릭된 작품" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "많이 클릭된 플랫폼" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "쿠폰 CTA가 많이 눌린 작품" })).toBeInTheDocument();
    expect(screen.getByText("달빛 기록관")).toBeInTheDocument();
    expect(screen.getByText("카카오페이지")).toBeInTheDocument();
    expect(screen.getByText("아직 쿠폰 CTA 클릭 이벤트가 없어요.")).toBeInTheDocument();
    expect(screen.getByText(/계산 시각:/)).toBeInTheDocument();
  });
});
