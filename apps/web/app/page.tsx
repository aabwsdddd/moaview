import Link from "next/link";

const sampleWorkId = "work_moonlight_archive";

const sampleOffers = [
  {
    platform: "네이버웹툰",
    confirmed: "300원",
    couponExpected: "240원",
    cashback: "228원",
    freeEpisodes: 5,
    waitFree: true,
    sourceUrl: "https://example.com/naver/moonlight-archive",
    lastVerifiedAt: "2026-05-01T09:00:00Z",
  },
  {
    platform: "카카오페이지",
    confirmed: "350원",
    couponExpected: "280원",
    cashback: "266원",
    freeEpisodes: 7,
    waitFree: true,
    sourceUrl: "https://example.com/kakao/moonlight-archive",
    lastVerifiedAt: "2026-05-01T09:10:00Z",
  },
];

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-10 px-6 py-12">
      <section className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">MoaView MVP</p>
        <h1 className="mt-4 text-4xl font-bold tracking-tight text-ink">작품을 검색하고 플랫폼별 가격을 비교하세요.</h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-600">
          초기 스캐폴드는 fixture 데이터만 사용하며 실제 scraping, 플랫폼 로그인 연동, 자체 뷰어를 구현하지 않습니다.
        </p>
        <form className="mt-8 flex flex-col gap-3 sm:flex-row" action="#offers">
          <input
            className="min-h-12 flex-1 rounded-2xl border border-slate-300 px-4 text-base outline-none transition focus:border-moa focus:ring-4 focus:ring-violet-100"
            name="q"
            placeholder="작품명 또는 작가명 검색"
            aria-label="작품명 또는 작가명 검색"
          />
          <button className="rounded-2xl bg-moa px-6 py-3 font-semibold text-white shadow-sm transition hover:bg-violet-700" type="submit">
            검색
          </button>
        </form>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link className="rounded-2xl border border-moa px-5 py-3 font-semibold text-moa transition hover:bg-violet-50" href={`/works/${sampleWorkId}`}>
            샘플 작품 상세 보기
          </Link>
          <Link className="rounded-2xl border border-slate-300 px-5 py-3 font-semibold text-slate-700 transition hover:border-moa hover:text-moa" href="/favorites">
            찜한 작품 보기
          </Link>
        </div>
      </section>

      <section id="offers" className="grid gap-4 md:grid-cols-2">
        {sampleOffers.map((offer) => (
          <article key={offer.platform} className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-bold">{offer.platform}</h2>
              <span className="rounded-full bg-violet-50 px-3 py-1 text-sm font-medium text-moa">
                {offer.waitFree ? "기다무 가능" : "기다무 없음"}
              </span>
            </div>
            <dl className="mt-5 space-y-3 text-sm">
              <div className="flex justify-between"><dt>확정가(자동 할인)</dt><dd className="font-semibold">{offer.confirmed}</dd></div>
              <div className="flex justify-between"><dt>쿠폰 적용 예상가</dt><dd className="font-semibold">{offer.couponExpected}</dd></div>
              <div className="flex justify-between"><dt>캐시백 포함 체감가</dt><dd className="font-semibold">{offer.cashback}</dd></div>
              <div className="flex justify-between"><dt>무료 회차</dt><dd className="font-semibold">{offer.freeEpisodes}화</dd></div>
            </dl>
            <p className="mt-5 break-all text-xs text-slate-500">출처: {offer.sourceUrl}</p>
            <p className="mt-1 text-xs text-slate-500">마지막 확인: {new Date(offer.lastVerifiedAt).toLocaleString("ko-KR")}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
