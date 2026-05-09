export type PlatformSummary = {
  id: string;
  label: string;
  offer_id: string;
  source_url: string;
  last_updated_at: string;
};

export type WorkSummary = {
  id: string;
  title: string;
  authors: string[];
  content_type?: string;
  description?: string | null;
};

export type SearchResult = WorkSummary & {
  content_type: string;
  platforms: PlatformSummary[];
  max_free_episodes: number;
  lowest_confirmed_price: number | null;
  lowest_coupon_expected_price: number | null;
  best_platform_label: string | null;
};

export type SearchResponse = {
  items: SearchResult[];
  count: number;
};

export type FavoriteItem = {
  user_id: string;
  work_id: string;
  created_at: string;
  work: WorkSummary | null;
};

export type FavoriteListResponse = {
  items: FavoriteItem[];
  count: number;
};

export type PromotionSummary = {
  id: string;
  platform: string;
  promotion_type: string;
  title: string;
};

export type CouponSummary = {
  id: string;
  platform: string;
  coupon_type: string;
  coupon_code?: string | null;
  title: string;
  label?: string;
};

export type WorkOffer = {
  id: string;
  work_id: string;
  platform: string;
  platform_id: string;
  source_url: string;
  last_updated_at: string;
  free_episode_count: number;
  wait_free_available: boolean;
  base_price: number;
  instant_discounted_price: number;
  coupon_expected_price: number | null;
  cashback_adjusted_price: number | null;
  effective_price_for_sort: number;
  price_confidence: string;
  calculation_note: string;
  active_promotions: PromotionSummary[];
  active_coupons: CouponSummary[];
};

export type WorkDetail = WorkSummary & {
  content_type: string;
  genre?: string | null;
  status?: string | null;
  description?: string | null;
  available_platforms: PlatformSummary[];
};

export type NotificationEvent = {
  id: string;
  event_type: string;
  work_id?: string | null;
  user_id?: string | null;
  anonymous_session_id?: string | null;
  payload: Record<string, unknown>;
  created_at: string;
};

export type NotificationResponse = {
  items: NotificationEvent[];
  count: number;
};

export type PlatformClickPayload = {
  anonymous_session_id: string;
  work_id: string;
  platform_id: string;
  offer_id: string;
  cta_type: "free_cta" | "lowest_price_cta" | "coupon_cta" | "compare_cta";
  effective_price_at_click?: number;
  destination_url?: string;
  clicked_at?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export function getAnonymousSessionId() {
  if (typeof window === "undefined") {
    return "anon_server_fixture";
  }

  const key = "moaview_anonymous_session_id";
  const existing = window.localStorage.getItem(key);
  if (existing) {
    return existing;
  }

  const generated = `anon_${globalThis.crypto?.randomUUID?.() ?? Date.now().toString(36)}`;
  window.localStorage.setItem(key, generated);
  return generated;
}

function withAuthHeader(accessToken?: string, headers?: HeadersInit): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    ...headers,
  };
}

async function safeJson<T>(path: string, init?: RequestInit, fallback?: T, accessToken?: string): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: withAuthHeader(accessToken, init?.headers),
      cache: "no-store",
    });

    if (!response.ok) {
      return fallback as T;
    }

    return (await response.json()) as T;
  } catch {
    return fallback as T;
  }
}

export async function searchWorks(query: string): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query });
  return safeJson<SearchResponse>(`/api/search?${params.toString()}`, undefined, { items: [], count: 0 });
}

export async function recordSearchEvent(query: string, resultCount: number, anonymousSessionId = getAnonymousSessionId()) {
  return safeJson<{ item?: unknown; count: number }>(
    "/api/events/search",
    { method: "POST", body: JSON.stringify({ anonymous_session_id: anonymousSessionId, query, result_count: resultCount }) },
    { count: 0 },
  );
}

export async function recordDetailViewEvent(workId: string, anonymousSessionId = getAnonymousSessionId()) {
  return safeJson<{ item?: unknown; count: number }>(
    "/api/events/detail-view",
    { method: "POST", body: JSON.stringify({ anonymous_session_id: anonymousSessionId, work_id: workId }) },
    { count: 0 },
  );
}

export async function recordPlatformClick(payload: PlatformClickPayload) {
  return safeJson<{ item?: unknown; count: number }>(
    "/api/events/platform-click",
    { method: "POST", body: JSON.stringify(payload) },
    { count: 0 },
  );
}

export async function listFavorites(accessToken?: string): Promise<FavoriteListResponse> {
  return safeJson<FavoriteListResponse>("/api/favorites", undefined, { items: [], count: 0 }, accessToken);
}

export async function addFavorite(workId: string, accessToken?: string): Promise<FavoriteListResponse> {
  return safeJson<FavoriteListResponse>(
    "/api/favorites",
    { method: "POST", body: JSON.stringify({ work_id: workId }) },
    { items: [], count: 0 },
    accessToken,
  );
}

export async function removeFavorite(workId: string, accessToken?: string): Promise<{ deleted: boolean; work_id: string; count: number }> {
  return safeJson<{ deleted: boolean; work_id: string; count: number }>(`/api/favorites/${workId}`, { method: "DELETE" }, { deleted: false, work_id: workId, count: 0 }, accessToken);
}

export async function getWorkDetail(workId: string): Promise<WorkDetail | null> {
  return safeJson<WorkDetail | null>(`/api/works/${workId}`, undefined, null);
}

export async function getWorkOffers(workId: string): Promise<WorkOffer[]> {
  const response = await safeJson<{ items: WorkOffer[]; count: number }>(`/api/works/${workId}/offers`, undefined, { items: [], count: 0 });
  return response.items;
}

export async function listNotifications(): Promise<NotificationResponse> {
  return safeJson<NotificationResponse>("/api/notifications", undefined, { items: [], count: 0 });
}
