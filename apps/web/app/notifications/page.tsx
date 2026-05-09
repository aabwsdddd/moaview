import React from "react";
import Link from "next/link";
import { listNotifications } from "../../lib/api";

export default async function NotificationsPage() {
  const notifications = await listNotifications();

  return (
    <main className="mx-auto min-h-screen max-w-4xl px-6 py-12">
      <section className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Notifications</p>
        <h1 className="mt-3 text-3xl font-bold text-ink">알림 이벤트</h1>
        <p className="mt-3 text-slate-600">현재는 fixture-compatible 이벤트 기록을 표시하며 실제 이메일 발송은 구현하지 않습니다.</p>
      </section>

      {notifications.items.length === 0 ? (
        <section className="mt-6 rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
          <h2 className="text-2xl font-bold text-ink">아직 알림 이벤트가 없어요</h2>
          <p className="mt-3 text-slate-600">작품 상세를 열거나 플랫폼 CTA를 클릭하면 API 이벤트 기반 알림 기록이 표시됩니다.</p>
          <Link className="mt-6 inline-flex rounded-2xl bg-moa px-5 py-3 font-semibold text-white" href="/search?q=달빛">
            작품 보러 가기
          </Link>
        </section>
      ) : (
        <section className="mt-6 space-y-4">
          {notifications.items.map((item) => (
            <article className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200" key={item.id}>
              <p className="text-sm font-semibold text-moa">{item.event_type}</p>
              <h2 className="mt-2 text-xl font-bold text-ink">{item.work_id ?? "work 없음"}</h2>
              <p className="mt-2 text-sm text-slate-500">생성: {new Date(item.created_at).toLocaleString("ko-KR")}</p>
              <pre className="mt-4 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-100">{JSON.stringify(item.payload, null, 2)}</pre>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
