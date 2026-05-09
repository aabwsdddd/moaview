"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { addFavorite, listFavorites, removeFavorite } from "../../lib/api/favorites";
import { createSupabaseBrowserClient } from "../../lib/supabase/client";

export type FavoriteButtonProps = {
  workId: string;
};

export function FavoriteButton({ workId }: FavoriteButtonProps) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const [message, setMessage] = useState("로그인 후 찜할 수 있어요");
  const [isPending, setIsPending] = useState(false);
  const supabase = createSupabaseBrowserClient();

  useEffect(() => {
    let isMounted = true;

    async function hydrateFavoriteState() {
      if (!supabase) {
        setIsLoggedIn(false);
        return;
      }

      const [{ data: userData }, { data: sessionData }] = await Promise.all([
        supabase.auth.getUser(),
        supabase.auth.getSession(),
      ]);
      const loggedIn = Boolean(userData.user);

      if (!isMounted) {
        return;
      }

      setIsLoggedIn(loggedIn);
      setMessage(loggedIn ? "관심 작품으로 저장해 보세요." : "로그인 후 찜할 수 있어요");

      if (loggedIn) {
        const favorites = await listFavorites(sessionData.session?.access_token);
        if (isMounted) {
          setIsFavorite(favorites.items.some((item) => item.work_id === workId));
        }
      }
    }

    void hydrateFavoriteState();

    if (!supabase) {
      return () => {
        isMounted = false;
      };
    }

    const { data } = supabase.auth.onAuthStateChange((_event, session) => {
      setIsLoggedIn(Boolean(session?.user));
      setMessage(session?.user ? "관심 작품으로 저장해 보세요." : "로그인 후 찜할 수 있어요");
      if (!session?.user) {
        setIsFavorite(false);
      }
    });

    return () => {
      isMounted = false;
      data.subscription.unsubscribe();
    };
  }, [supabase, workId]);

  async function getAccessToken() {
    const { data } = (await supabase?.auth.getSession()) ?? { data: { session: null } };
    return data.session?.access_token;
  }

  async function toggleFavorite() {
    if (!isLoggedIn) {
      setMessage("로그인 후 찜할 수 있어요");
      return;
    }

    setIsPending(true);
    const accessToken = await getAccessToken();

    if (isFavorite) {
      await removeFavorite(workId, accessToken);
      setIsFavorite(false);
      setMessage("찜을 해제했어요.");
    } else {
      await addFavorite(workId, accessToken);
      setIsFavorite(true);
      setMessage("찜한 작품에 추가했어요.");
    }
    setIsPending(false);
  }

  if (!isLoggedIn) {
    return (
      <div className="rounded-3xl border border-dashed border-violet-200 bg-violet-50 p-5">
        <p className="font-semibold text-moa">로그인 후 찜할 수 있어요</p>
        <p className="mt-1 text-sm text-slate-600">찜 목록은 Supabase Auth 세션이 있을 때 API 즐겨찾기 엔드포인트와 동기화됩니다.</p>
        <Link className="mt-4 inline-flex rounded-2xl bg-moa px-5 py-2 font-semibold text-white transition hover:bg-violet-700" href="/login">
          로그인하고 찜하기
        </Link>
      </div>
    );
  }

  return (
    <div className="rounded-3xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <button className="rounded-2xl bg-moa px-5 py-2 font-semibold text-white transition hover:bg-violet-700 disabled:bg-slate-300" disabled={isPending} onClick={toggleFavorite} type="button">
        {isFavorite ? "찜 해제" : "찜하기"}
      </button>
      <p className="mt-3 text-sm text-slate-600" role="status">
        {message}
      </p>
    </div>
  );
}
