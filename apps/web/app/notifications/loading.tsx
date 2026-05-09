import React from "react";
export default function NotificationsLoading() {
  return (
    <main className="mx-auto min-h-screen max-w-4xl px-6 py-12">
      <section className="animate-pulse rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div className="h-4 w-40 rounded bg-slate-200" />
        <div className="mt-4 h-9 w-56 rounded bg-slate-200" />
        <div className="mt-6 h-32 rounded-2xl bg-slate-100" />
      </section>
    </main>
  );
}
