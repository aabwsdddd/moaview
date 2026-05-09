import { expect, test } from "@playwright/test";

test.describe("MoaView MVP core flow", () => {
  test("searches a fixture work, compares platform prices, records CTA click, and shows favorite guidance", async ({ page, request }) => {
    const searchEvents: unknown[] = [];
    const platformClickEvents: unknown[] = [];

    const apiBaseUrl = process.env.MOAVIEW_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
    expect(apiBaseUrl).toBe("http://127.0.0.1:8000");

    const apiSearchResponse = await request.get(`${apiBaseUrl}/api/search`, { params: { q: "달빛" } });
    expect(apiSearchResponse.ok()).toBeTruthy();
    const apiSearchJson = await apiSearchResponse.json();
    expect(apiSearchJson.items.map((item: { title: string }) => item.title)).toContain("달빛 기록관");

    await page.addInitScript(() => {
      window.open = (url?: string | URL) => {
        window.localStorage.setItem("moaview_last_opened_url", String(url ?? ""));
        return null;
      };
    });

    await page.route("**/api/events/search", async (route) => {
      searchEvents.push(route.request().postDataJSON());
      await route.fulfill({ json: { item: { id: "event_search_e2e" }, count: 1 } });
    });
    await page.route("**/api/events/platform-click", async (route) => {
      platformClickEvents.push(route.request().postDataJSON());
      await route.fulfill({ json: { item: { id: "event_platform_click_e2e" }, count: 1 } });
    });

    await page.goto("/");
    await expect(page.getByRole("heading", { name: /작품을 검색하고 플랫폼별 무료 회차와 가격을 비교하세요/ })).toBeVisible();

    await page.getByLabel("작품명 또는 작가명 검색").fill("달빛");
    await page.getByRole("button", { name: "검색" }).click();

    await expect(page).toHaveURL(/\/search\?q=/);
    await expect(page.getByRole("heading", { name: "작품 검색" })).toBeVisible();
    await expect(page.locator("body")).toContainText("달빛 기록관");
    await expect(page.getByRole("link", { name: /달빛 기록관/ })).toBeVisible();
    await expect.poll(() => searchEvents.length).toBeGreaterThan(0);

    await page.getByRole("link", { name: /달빛 기록관/ }).click();

    await expect(page.getByRole("heading", { name: "달빛 기록관" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "플랫폼별 가격 비교" })).toBeVisible();
    await expect(page.getByRole("table")).toContainText("확정가");
    await expect(page.getByRole("table")).toContainText("쿠폰 적용 예상가");
    await expect(page.getByRole("table")).toContainText("캐시백 포함 체감가");
    await expect(page.getByText(/쿠폰 적용 예상가는 사용자가 쿠폰을 다운로드하거나 수령해야 할 수 있으며 확정가로 표시하지 않습니다/)).toBeVisible();
    await expect(page.getByText(/캐시백 포함 체감가는 현금 할인이 아닌 추정 체감가입니다/)).toBeVisible();
    await expect(page.getByText("로그인 후 찜할 수 있어요").first()).toBeVisible();

    await page.getByRole("button", { name: "쿠폰 받고 보기" }).click();

    await expect.poll(() => platformClickEvents.length).toBe(1);
    expect(platformClickEvents[0]).toMatchObject({
      work_id: "work_moonlight_archive",
      cta_type: "coupon_cta",
    });
    expect(platformClickEvents[0]).toEqual(expect.objectContaining({
      anonymous_session_id: expect.stringMatching(/^anon_/),
      destination_url: expect.stringMatching(/^https:\/\/example\.com\//),
      effective_price_at_click: expect.any(Number),
      offer_id: expect.any(String),
      platform_id: expect.any(String),
    }));
    await expect
      .poll(() => page.evaluate(() => window.localStorage.getItem("moaview_last_opened_url")))
      .toContain("https://example.com/");
  });
});
