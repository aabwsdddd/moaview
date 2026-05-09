import Link from "next/link";
import { FavoriteButton } from "../../../components/favorites/FavoriteButton";
import { getWorkDetail, getWorkOffers } from "../../../lib/api/favorites";

function formatWon(value: number | null) {
  return value === null ? "-" : `${value.toLocaleString("ko-KR")}원`;
}

export default async function WorkDetailPage({ params }: { params: Promise<{ workId: string }> }) {
  const { workId } = await params;
  const [work, offers] = await Promise.all([getWorkDetail(workId), getWorkOffers(workId)]);

  const displayWork = work ?? {
    id: workId,
    title: "달빛 기록관",
    authors: ["한서윤"],
    content_type: "webtoon",
    description: "fixture API가 꺼져 있어도 확인할 수 있는 샘플 상세 화면입니다.",
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-8 px-6 py-12">
      <Link className="text-sm font-semibold text-moa hover:text-violet-700" href="/">
        ← 검색으로 돌아가기
      </Link>

      <section className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <article className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Work Detail</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-ink">{displayWork.title}</h1>
          <p className="mt-3 text-slate-600">{displayWork.authors.join(", ")} · {displayWork.content_type}</p>
          <p className="mt-5 text-lg leading-8 text-slate-700">{displayWork.description}</p>
        </article>
        <FavoriteButton workId={displayWork.id} />
      </section>

      <section className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Platform Comparison</p>
            <h2 className="mt-2 text-2xl font-bold text-ink">플랫폼별 가격 비교</h2>
          </div>
        </div>

        {offers.length === 0 ? (
          <p className="mt-6 rounded-2xl bg-slate-50 p-5 text-slate-600">API가 실행 중이면 Task 4의 /api/works/{workId}/offers 결과가 여기에 표시됩니다.</p>
        ) : (
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {offers.map((offer) => (
              <article className="rounded-3xl border border-slate-200 p-6" key={offer.id}>
                <div className="flex items-center justify-between gap-4">
                  <h3 className="text-xl font-bold">{offer.platform}</h3>
                  <span className="rounded-full bg-violet-50 px-3 py-1 text-sm font-medium text-moa">
                    {offer.wait_free_available ? "기다무 가능" : "기다무 없음"}
                  </span>
                </div>
                <dl className="mt-5 space-y-3 text-sm">
                  <div className="flex justify-between"><dt>기본가</dt><dd className="font-semibold">{formatWon(offer.base_price)}</dd></div>
                  <div className="flex justify-between"><dt>확정가(자동 할인)</dt><dd className="font-semibold">{formatWon(offer.instant_discounted_price)}</dd></div>
                  <div className="flex justify-between"><dt>쿠폰 적용 예상가</dt><dd className="font-semibold">{formatWon(offer.coupon_expected_price)}</dd></div>
                  <div className="flex justify-between"><dt>캐시백 포함 체감가</dt><dd className="font-semibold">{formatWon(offer.cashback_adjusted_price)}</dd></div>
                  <div className="flex justify-between"><dt>무료 회차</dt><dd className="font-semibold">{offer.free_episode_count}화</dd></div>
                </dl>
                <a className="mt-5 block break-all text-xs font-semibold text-moa hover:text-violet-700" href={offer.source_url} rel="noreferrer" target="_blank">
                  출처: {offer.source_url}
                </a>
                <p className="mt-1 text-xs text-slate-500">마지막 확인: {new Date(offer.last_updated_at).toLocaleString("ko-KR")}</p>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
