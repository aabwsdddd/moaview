import Link from "next/link";
import type { FavoriteItem } from "../../lib/api/favorites";

export function FavoritesList({ items }: { items: FavoriteItem[] }) {
  if (items.length === 0) {
    return (
      <section className="rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
        <h1 className="text-3xl font-bold tracking-tight text-ink">찜한 작품</h1>
        <p className="mt-4 text-slate-600">아직 찜한 작품이 없어요.</p>
        <Link className="mt-6 inline-flex rounded-2xl bg-moa px-5 py-3 font-semibold text-white transition hover:bg-violet-700" href="/">
          작품 검색하러 가기
        </Link>
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <h1 className="text-3xl font-bold tracking-tight text-ink">찜한 작품</h1>
      {items.map((item) => (
        <article className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200" key={item.work_id}>
          <p className="text-sm text-slate-500">{item.work?.content_type ?? "work"}</p>
          <h2 className="mt-1 text-xl font-bold text-ink">{item.work?.title ?? item.work_id}</h2>
          <p className="mt-2 text-sm text-slate-600">{item.work?.authors.join(", ")}</p>
          <p className="mt-2 text-xs text-slate-500">찜한 시간: {new Date(item.created_at).toLocaleString("ko-KR")}</p>
          <Link className="mt-4 inline-flex text-sm font-semibold text-moa hover:text-violet-700" href={`/works/${item.work_id}`}>
            가격 비교 보기 →
          </Link>
        </article>
      ))}
    </section>
  );
}
