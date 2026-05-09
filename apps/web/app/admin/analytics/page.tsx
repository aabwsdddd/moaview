import { getAdminAnalyticsSummary, type AnalyticsTopPlatform, type AnalyticsTopWork } from "../../../lib/api";

function formatRate(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("ko-KR").format(value);
}

export default async function AdminAnalyticsPage() {
  const summary = await getAdminAnalyticsSummary();
  const cards = [
    { label: "검색 수", value: formatNumber(summary.total_searches) },
    { label: "상세 진입 수", value: formatNumber(summary.total_detail_views) },
    { label: "플랫폼 클릭 수", value: formatNumber(summary.total_platform_clicks) },
    { label: "검색→상세 전환율", value: formatRate(summary.search_to_detail_rate) },
    { label: "상세→클릭 전환율", value: formatRate(summary.detail_to_platform_click_rate) },
    { label: "찜 등록률", value: formatRate(summary.favorite_rate) },
    { label: "쿠폰 CTA 클릭률", value: formatRate(summary.coupon_cta_click_rate) },
    { label: "알림 클릭률", value: formatRate(summary.notification_click_rate) },
  ];

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-12">
      <section className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Admin Analytics</p>
        <h1 className="mt-3 text-3xl font-bold text-ink">MVP 분석 대시보드</h1>
        <p className="mt-4 leading-7 text-slate-600">
          검색→상세→플랫폼 클릭 흐름과 찜, 쿠폰 CTA, 알림 클릭 KPI를 fixture 이벤트 기반으로 확인합니다.
        </p>
        <p className="mt-3 rounded-2xl bg-amber-50 px-4 py-3 text-sm text-amber-800">
          TODO: 실제 운영 전 Supabase Auth 기반 관리자 권한 검사를 연결해야 합니다.
        </p>
        <p className="mt-4 text-sm text-slate-500">계산 시각: {summary.generated_at ? new Date(summary.generated_at).toLocaleString("ko-KR") : "기록 없음"}</p>
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <article className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200" key={card.label}>
            <p className="text-sm font-semibold text-slate-500">{card.label}</p>
            <p className="mt-3 text-3xl font-bold text-ink">{card.value}</p>
          </article>
        ))}
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-3">
        <TopWorkTable title="많이 클릭된 작품" items={summary.top_clicked_works} empty="아직 플랫폼 클릭 이벤트가 없어요." />
        <TopPlatformTable title="많이 클릭된 플랫폼" items={summary.top_clicked_platforms} empty="아직 플랫폼 클릭 이벤트가 없어요." />
        <TopWorkTable title="쿠폰 CTA가 많이 눌린 작품" items={summary.top_coupon_cta_works} empty="아직 쿠폰 CTA 클릭 이벤트가 없어요." />
      </section>
    </main>
  );
}

function TopWorkTable({ title, items, empty }: { title: string; items: AnalyticsTopWork[]; empty: string }) {
  return (
    <article className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h2 className="text-xl font-bold text-ink">{title}</h2>
      {items.length === 0 ? (
        <p className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">{empty}</p>
      ) : (
        <table className="mt-5 w-full text-left text-sm">
          <thead className="text-slate-500">
            <tr>
              <th className="pb-3">작품</th>
              <th className="pb-3 text-right">클릭</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((item) => (
              <tr key={item.work_id}>
                <td className="py-3 font-semibold text-ink">{item.title}</td>
                <td className="py-3 text-right text-slate-600">{formatNumber(item.count)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </article>
  );
}

function TopPlatformTable({ title, items, empty }: { title: string; items: AnalyticsTopPlatform[]; empty: string }) {
  return (
    <article className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h2 className="text-xl font-bold text-ink">{title}</h2>
      {items.length === 0 ? (
        <p className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">{empty}</p>
      ) : (
        <table className="mt-5 w-full text-left text-sm">
          <thead className="text-slate-500">
            <tr>
              <th className="pb-3">플랫폼</th>
              <th className="pb-3 text-right">클릭</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((item) => (
              <tr key={item.platform_id}>
                <td className="py-3 font-semibold text-ink">{item.label}</td>
                <td className="py-3 text-right text-slate-600">{formatNumber(item.count)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </article>
  );
}
