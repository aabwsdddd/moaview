export type SupabaseEnv = {
  url?: string;
  publishableKey?: string;
  anonKey?: string;
};

export function getSupabaseEnv(): SupabaseEnv {
  return {
    url: process.env.NEXT_PUBLIC_SUPABASE_URL,
    publishableKey: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
    anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  };
}

export function getSupabaseBrowserKey(env: SupabaseEnv = getSupabaseEnv()): string | undefined {
  return env.publishableKey || env.anonKey;
}

export function isSupabaseConfigured(env: SupabaseEnv = getSupabaseEnv()): boolean {
  return Boolean(env.url && getSupabaseBrowserKey(env));
}
