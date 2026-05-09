"use client";

import React, { FormEvent, useState } from "react";
import { createSupabaseBrowserClient } from "../../lib/supabase/client";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("Supabase 환경 변수가 없으면 데모 모드로 화면만 확인할 수 있어요.");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const supabase = createSupabaseBrowserClient();

  async function handleMagicLink(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);

    if (!supabase) {
      setMessage("개발/테스트 모드: Supabase 설정 없이도 앱이 렌더링됩니다.");
      setIsSubmitting(false);
      return;
    }

    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/favorites`,
      },
    });

    setMessage(error ? `매직 링크 요청 실패: ${error.message}` : "메일함에서 로그인 매직 링크를 확인해 주세요.");
    setIsSubmitting(false);
  }

  async function handleGoogleLogin() {
    if (!supabase) {
      setMessage("개발/테스트 모드: Google OAuth는 Supabase 설정 후 사용할 수 있어요.");
      return;
    }

    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/favorites`,
      },
    });

    if (error) {
      setMessage(`Google 로그인 시작 실패: ${error.message}`);
    }
  }

  return (
    <div className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-moa">Supabase Auth</p>
        <h1 className="mt-3 text-3xl font-bold tracking-tight text-ink">로그인</h1>
        <p className="mt-3 text-slate-600">이메일 매직 링크 또는 Google OAuth로 로그인해 찜한 작품을 관리하세요.</p>
      </div>

      <form className="mt-8 space-y-4" onSubmit={handleMagicLink}>
        <label className="block text-sm font-semibold text-slate-700" htmlFor="email">
          이메일 주소
        </label>
        <input
          className="min-h-12 w-full rounded-2xl border border-slate-300 px-4 text-base outline-none transition focus:border-moa focus:ring-4 focus:ring-violet-100"
          id="email"
          name="email"
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
          required
          type="email"
          value={email}
        />
        <button className="w-full rounded-2xl bg-moa px-6 py-3 font-semibold text-white shadow-sm transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:bg-slate-300" disabled={isSubmitting} type="submit">
          {isSubmitting ? "전송 중..." : "이메일 매직 링크 받기"}
        </button>
      </form>

      <div className="my-6 flex items-center gap-3 text-xs text-slate-400">
        <span className="h-px flex-1 bg-slate-200" />
        또는
        <span className="h-px flex-1 bg-slate-200" />
      </div>

      <button className="w-full rounded-2xl border border-slate-300 bg-white px-6 py-3 font-semibold text-slate-700 shadow-sm transition hover:border-moa hover:text-moa" onClick={handleGoogleLogin} type="button">
        Google로 계속하기
      </button>

      <p className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600" role="status">
        {message}
      </p>
    </div>
  );
}
