import React from "react";
export default function SearchLoading() {
  return (
    <main className="mx-auto min-h-screen max-w-5xl px-6 py-12">
      <section className="animate-pulse rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div className="h-4 w-32 rounded bg-slate-200" />
        <div className="mt-4 h-9 w-64 rounded bg-slate-200" />
        <div className="mt-6 h-12 rounded-2xl bg-slate-100" />
      </section>
    </main>
  );
}
