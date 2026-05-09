import React from "react";
export default function AdminMergeReviewPage() {
  return (
    <main className="mx-auto min-h-screen max-w-4xl px-6 py-12">
      <section className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Admin</p>
        <h1 className="mt-3 text-3xl font-bold text-ink">수동 중복/병합 검토 대기열</h1>
        <p className="mt-4 leading-7 text-slate-600">
          이 페이지는 운영자가 fixture 또는 crawler adapter가 발견한 후보 작품을 수동으로 dedup/merge 검토하기 위한 자리입니다. Task 6에서는 복잡한 admin auth, 자동 병합, production scraping을 구현하지 않습니다.
        </p>
        <div className="mt-6 rounded-2xl bg-slate-50 p-5 text-sm text-slate-600">
          <p className="font-semibold text-ink">현재 상태</p>
          <ul className="mt-3 list-disc space-y-2 pl-5">
            <li>검토 후보 API가 준비되면 이 영역에 후보 목록을 연결합니다.</li>
            <li>플랫폼 로그인, paywall 우회, 원본 이미지 저장은 MVP 범위 밖입니다.</li>
            <li>production crawling은 docs/CRAWLER_POLICY.md 검토 이후에만 추가합니다.</li>
          </ul>
        </div>
      </section>
    </main>
  );
}
