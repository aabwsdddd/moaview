"use client";

import { useRouter } from "next/navigation";
import React, { FormEvent, useState } from "react";

export function SearchBox({ initialQuery = "", size = "default" }: { initialQuery?: string; size?: "default" | "hero" }) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = query.trim();
    const params = trimmed ? `?q=${encodeURIComponent(trimmed)}` : "";
    router.push(`/search${params}`);
  }

  return (
    <form className="flex flex-col gap-3 sm:flex-row" onSubmit={submitSearch} role="search">
      <input
        className={`min-h-12 flex-1 rounded-2xl border border-slate-300 px-4 text-base outline-none transition focus:border-moa focus:ring-4 focus:ring-violet-100 ${size === "hero" ? "sm:text-lg" : ""}`}
        name="q"
        onChange={(event) => setQuery(event.target.value)}
        placeholder="작품명 또는 작가명 검색"
        aria-label="작품명 또는 작가명 검색"
        value={query}
      />
      <button className="rounded-2xl bg-moa px-6 py-3 font-semibold text-white shadow-sm transition hover:bg-violet-700" type="submit">
        검색
      </button>
    </form>
  );
}
