import React from "react";
import Link from "next/link";
import { LoginForm } from "../../components/auth/LoginForm";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center px-6 py-12">
      <LoginForm />
      <Link className="mt-6 text-center text-sm font-semibold text-moa hover:text-violet-700" href="/">
        홈으로 돌아가기
      </Link>
    </main>
  );
}
