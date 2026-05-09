"use client";

export default function WorkDetailError({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="mx-auto min-h-screen max-w-3xl px-6 py-12">
      <section className="rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
        <h1 className="text-3xl font-bold text-ink">작품 상세를 불러오지 못했어요</h1>
        <p className="mt-3 text-slate-600">fixture-backed API 상태를 확인한 뒤 다시 시도해 주세요.</p>
        <button className="mt-6 rounded-2xl bg-moa px-5 py-3 font-semibold text-white" onClick={reset} type="button">
          다시 시도
        </button>
      </section>
    </main>
  );
}
