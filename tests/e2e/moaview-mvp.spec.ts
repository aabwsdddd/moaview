import { expect, test } from "@playwright/test";

test.describe("MoaView frontend MVP flow", () => {
  test("user searches, opens detail, compares prices, and clicks a CTA", async ({ page }) => {
    await page.route("**/api/events/search", async (route) => {
      await route.fulfill({ json: { item: { id: "event_search_test" }, count: 1 } });
    });
    await page.route("**/api/events/platform-click", async (route) => {
      await route.fulfill({ json: { item: { id: "event_platform_click_test" }, count: 1 } });
    });

    await page.goto("/");
    await page.getByLabel("작품명 또는 작가명 검색").fill("달빛");
    await page.getByRole("button", { name: "검색" }).click();

    await expect(page).toHaveURL(/\/search\?q=/);
    await page.getByRole("link", { name: /달빛 기록관/ }).click();

    await expect(page.getByRole("heading", { name: "플랫폼별 가격 비교" })).toBeVisible();
    await expect(page.getByText("쿠폰 적용 예상가").first()).toBeVisible();

    const popupPromise = page.waitForEvent("popup");
    await page.getByRole("button", { name: "쿠폰 받고 보기" }).click();
    const popup = await popupPromise;
    await expect(popup).toHaveURL(/example\.com/);
  });
});
