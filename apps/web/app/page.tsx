import React from "react";
import Link from "next/link";
import { SearchBox } from "../components/search/SearchBox";
import { searchWorks } from "../lib/api";

function formatWon(value: number | null) {
  return value === null ? "-" : `${value.toLocaleString("ko-KR")}원`;
}

export default async function Home() {
  const works = (await searchWorks("")).items;
  const freeWorks = works.filter((work) => work.max_free_episodes > 0);
  const recentWorks = works.filter((work) => work.platforms.some((platform) => Boolean(platform.last_updated_at)));

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-12">
      <section className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">MoaView MVP</p>
        <h1 className="mt-4 max-w-3xl text-4xl font-bold tracking-tight text-ink md:text-5xl">작품을 검색하고 플랫폼별 무료 회차와 가격을 비교하세요.</h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-600">
          fixture-backed API만 사용해 검색 → 상세 → 플랫폼 비교 → 외부 플랫폼 클릭 흐름을 검증합니다. 실제 scraping이나 플랫폼 로그인은 필요하지 않습니다.
        </p>
        <div className="mt-8">
          <SearchBox size="hero" />
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link className="rounded-2xl border border-moa px-5 py-3 font-semibold text-moa transition hover:bg-violet-50" href="/search?q=달빛">
            달빛 검색해 보기
          </Link>
          <Link className="rounded-2xl border border-slate-300 px-5 py-3 font-semibold text-slate-700 transition hover:border-moa hover:text-moa" href="/favorites">
            찜한 작품 보기
          </Link>
        </div>
      </section>

      <section className="space-y-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Popular Fixtures</p>
          <h2 className="mt-2 text-2xl font-bold text-ink">인기 fixture 작품</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {works.map((work) => (
            <Link className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200 transition hover:-translate-y-0.5 hover:shadow-md" href={`/works/${work.id}`} key={work.id}>
              <p className="text-sm font-semibold text-moa">{work.content_type}</p>
              <h3 className="mt-2 text-xl font-bold text-ink">{work.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{work.authors.join(", ")}</p>
              <p className="mt-3 text-sm text-slate-500">플랫폼: {work.platforms.map((platform) => platform.label).join(", ")}</p>
              <p className="mt-2 text-sm text-slate-500">확정 최저가 {formatWon(work.lowest_confirmed_price)} · 쿠폰 적용 예상 최저가 {formatWon(work.lowest_coupon_expected_price)}</p>
            </Link>
          ))}
        </div>
      </section>

      {freeWorks.length > 0 ? (
        <section className="rounded-3xl bg-emerald-50 p-6 ring-1 ring-emerald-100">
          <h2 className="text-2xl font-bold text-ink">무료/이벤트 작품</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {freeWorks.map((work) => (
              <Link className="rounded-2xl bg-white p-4 shadow-sm" href={`/works/${work.id}`} key={`${work.id}-free`}>
                <span className="text-sm font-semibold text-emerald-700">최대 {work.max_free_episodes}화 무료</span>
                <h3 className="mt-1 font-bold text-ink">{work.title}</h3>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      {recentWorks.length > 0 ? (
        <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="text-2xl font-bold text-ink">최근 업데이트</h2>
          <div className="mt-4 space-y-3">
            {recentWorks.map((work) => {
              const latest = [...work.platforms].sort((a, b) => b.last_updated_at.localeCompare(a.last_updated_at))[0];
              return (
                <Link className="flex flex-col justify-between gap-2 rounded-2xl bg-slate-50 p-4 md:flex-row md:items-center" href={`/works/${work.id}`} key={`${work.id}-recent`}>
                  <span className="font-semibold text-ink">{work.title}</span>
                  <span className="text-sm text-slate-500">{latest.label} · {new Date(latest.last_updated_at).toLocaleString("ko-KR")}</span>
                </Link>
              );
            })}
          </div>
        </section>
      ) : null}
    </main>
  );
}
