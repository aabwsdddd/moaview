"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";
import { createSupabaseBrowserClient } from "../../lib/supabase/client";

export function AuthStatus() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const supabase = createSupabaseBrowserClient();

  useEffect(() => {
    if (!supabase) {
      setReady(true);
      return;
    }

    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
      setReady(true);
    });

    const { data } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      setReady(true);
    });

    return () => data.subscription.unsubscribe();
  }, [supabase]);

  async function handleLogout() {
    await supabase?.auth.signOut();
    setUser(null);
  }

  if (!ready) {
    return <span className="text-sm text-slate-500">세션 확인 중...</span>;
  }

  if (user?.email) {
    return (
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <span className="rounded-full bg-violet-50 px-3 py-1 font-medium text-moa">{user.email}</span>
        <button className="rounded-full border border-slate-300 px-3 py-1 font-semibold text-slate-700 transition hover:border-moa hover:text-moa" onClick={handleLogout} type="button">
          로그아웃
        </button>
      </div>
    );
  }

  return (
    <Link className="rounded-full bg-moa px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-violet-700" href="/login">
      로그인
    </Link>
  );
}
