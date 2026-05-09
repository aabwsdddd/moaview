import React from "react";
import Link from "next/link";
import { DetailViewReporter } from "../../../components/works/DetailViewReporter";
import { FavoriteButton } from "../../../components/works/FavoriteButton";
import { OfferComparisonTable } from "../../../components/works/OfferComparisonTable";
import { getWorkDetail, getWorkOffers } from "../../../lib/api";

export default async function WorkDetailPage({ params }: { params: Promise<{ work_id: string }> }) {
  const { work_id: workId } = await params;
  const [work, offers] = await Promise.all([getWorkDetail(workId), getWorkOffers(workId)]);

  if (!work) {
    return (
      <main className="mx-auto min-h-screen max-w-3xl px-6 py-12">
        <section className="rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
          <h1 className="text-3xl font-bold text-ink">작품을 찾을 수 없어요</h1>
          <p className="mt-3 text-slate-600">fixture API에 없는 작품 ID입니다.</p>
          <Link className="mt-6 inline-flex rounded-2xl bg-moa px-5 py-3 font-semibold text-white" href="/search">
            검색으로 돌아가기
          </Link>
        </section>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-8 px-6 py-12">
      <DetailViewReporter workId={work.id} />
      <Link className="text-sm font-semibold text-moa hover:text-violet-700" href="/search">
        ← 검색으로 돌아가기
      </Link>

      <section className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <article className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Work Detail</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-ink">{work.title}</h1>
          <p className="mt-3 text-slate-600">{work.authors.join(", ")} · {work.content_type}</p>
          <dl className="mt-5 flex flex-wrap gap-3 text-sm">
            {work.genre ? <div className="rounded-full bg-slate-100 px-3 py-1"><dt className="sr-only">장르</dt><dd>{work.genre}</dd></div> : null}
            {work.status ? <div className="rounded-full bg-slate-100 px-3 py-1"><dt className="sr-only">상태</dt><dd>{work.status}</dd></div> : null}
          </dl>
          {work.description ? <p className="mt-5 text-lg leading-8 text-slate-700">{work.description}</p> : null}
          <p className="mt-5 text-sm text-slate-500">제공 플랫폼: {(work.available_platforms ?? []).map((platform) => platform.label).join(", ") || "-"}</p>
        </article>
        <FavoriteButton workId={work.id} />
      </section>

      <section className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Platform Comparison</p>
          <h2 className="mt-2 text-2xl font-bold text-ink">플랫폼별 가격 비교</h2>
          <p className="mt-3 text-sm text-slate-600">
            확정가는 자동 할인만 반영합니다. 쿠폰 적용 예상가는 사용자가 쿠폰을 다운로드하거나 수령해야 할 수 있으며 확정가로 표시하지 않습니다. 캐시백 포함 체감가는 현금 할인이 아닌 추정 체감가입니다.
          </p>
        </div>
        <OfferComparisonTable offers={offers} workId={work.id} />
      </section>
    </main>
  );
}
