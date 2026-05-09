"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import type { SearchResult } from "../../lib/api";
import { recordSearchEvent } from "../../lib/api";

function formatWon(value: number | null) {
  return value === null ? "-" : `${value.toLocaleString("ko-KR")}원`;
}

export function SearchResults({ query, results }: { query: string; results: SearchResult[] }) {
  const [eventState, setEventState] = useState<"idle" | "sent" | "failed">("idle");

  useEffect(() => {
    if (!query.trim()) {
      return;
    }

    let isMounted = true;
    recordSearchEvent(query, results.length)
      .then(() => {
        if (isMounted) setEventState("sent");
      })
      .catch(() => {
        if (isMounted) setEventState("failed");
      });

    return () => {
      isMounted = false;
    };
  }, [query, results.length]);

  if (!query.trim()) {
    return (
      <section className="rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
        <h2 className="text-2xl font-bold text-ink">검색어를 입력해 주세요</h2>
        <p className="mt-3 text-slate-600">작품명 또는 작가명으로 fixture-backed API를 검색합니다.</p>
      </section>
    );
  }

  if (results.length === 0) {
    return (
      <section className="rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
        <h2 className="text-2xl font-bold text-ink">검색 결과가 없어요</h2>
        <p className="mt-3 text-slate-600">다른 작품명이나 작가명으로 다시 검색해 보세요.</p>
        <p className="mt-2 text-xs text-slate-400">검색 이벤트 상태: {eventState === "sent" ? "기록됨" : "대기"}</p>
      </section>
    );
  }

  return (
    <section className="space-y-4" aria-label="검색 결과">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-ink">검색 결과</h2>
          <p className="mt-1 text-sm text-slate-500">{results.length}개 작품 · 검색 이벤트 {eventState === "sent" ? "기록됨" : "전송 중"}</p>
        </div>
      </div>
      {results.map((work) => (
        <Link
          className="block rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200 transition hover:-translate-y-0.5 hover:shadow-md hover:ring-violet-200"
          href={`/works/${work.id}`}
          key={work.id}
        >
          <article>
            <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-moa">{work.content_type}</p>
                <h3 className="mt-2 text-2xl font-bold text-ink">{work.title}</h3>
                <p className="mt-2 text-slate-600">{work.authors.join(", ")}</p>
                <p className="mt-3 text-sm text-slate-500">플랫폼: {work.platforms.map((platform) => platform.label).join(", ") || "-"}</p>
              </div>
              <dl className="grid min-w-64 grid-cols-2 gap-3 text-sm">
                <div className="rounded-2xl bg-slate-50 p-3">
                  <dt className="text-slate-500">최대 무료 회차</dt>
                  <dd className="mt-1 font-bold text-ink">{work.max_free_episodes}화</dd>
                </div>
                <div className="rounded-2xl bg-slate-50 p-3">
                  <dt className="text-slate-500">확정 최저가</dt>
                  <dd className="mt-1 font-bold text-ink">{formatWon(work.lowest_confirmed_price)}</dd>
                </div>
                <div className="col-span-2 rounded-2xl bg-violet-50 p-3">
                  <dt className="text-moa">쿠폰 적용 예상 최저가</dt>
                  <dd className="mt-1 font-bold text-moa">{formatWon(work.lowest_coupon_expected_price)}</dd>
                </div>
              </dl>
            </div>
          </article>
        </Link>
      ))}
    </section>
  );
}
