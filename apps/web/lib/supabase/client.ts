import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { getSupabaseBrowserKey, getSupabaseEnv, isSupabaseConfigured } from "./env";

let browserClient: SupabaseClient | null = null;

export function createSupabaseBrowserClient(): SupabaseClient | null {
  const env = getSupabaseEnv();
  const key = getSupabaseBrowserKey(env);

  if (!isSupabaseConfigured(env) || !key) {
    return null;
  }

  browserClient ??= createClient(env.url!, key, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  });

  return browserClient;
}
