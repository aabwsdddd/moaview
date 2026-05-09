import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { getSupabaseBrowserKey, getSupabaseEnv, isSupabaseConfigured } from "./env";

export function createSupabaseServerClient(): SupabaseClient | null {
  const env = getSupabaseEnv();
  const key = getSupabaseBrowserKey(env);

  if (!isSupabaseConfigured(env) || !key) {
    return null;
  }

  return createClient(env.url!, key, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
      detectSessionInUrl: false,
    },
  });
}
