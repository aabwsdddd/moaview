import { SearchBox } from "../../components/search/SearchBox";
import { SearchResults } from "../../components/search/SearchResults";
import { searchWorks } from "../../lib/api";

export default async function SearchPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q } = await searchParams;
  const query = q ?? "";
  const results = query.trim() ? await searchWorks(query) : { items: [], count: 0 };

  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-8 px-6 py-12">
      <section className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Search</p>
        <h1 className="mt-3 text-3xl font-bold tracking-tight text-ink">작품 검색</h1>
        <p className="mt-3 text-slate-600">작품명과 작가명을 기준으로 fixture 작품을 검색합니다.</p>
        <div className="mt-6">
          <SearchBox initialQuery={query} />
        </div>
      </section>
      <SearchResults query={query} results={results.items} />
    </main>
  );
}
