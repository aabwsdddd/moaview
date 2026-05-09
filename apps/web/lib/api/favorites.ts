export type WorkSummary = {
  id: string;
  title: string;
  authors: string[];
  content_type?: string;
  description?: string;
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

export type WorkOffer = {
  id: string;
  work_id: string;
  platform: string;
  source_url: string;
  last_updated_at: string;
  free_episode_count: number;
  wait_free_available: boolean;
  base_price: number;
  instant_discounted_price: number;
  coupon_expected_price: number | null;
  cashback_adjusted_price: number | null;
};

export type WorkDetail = WorkSummary & {
  genre?: string;
  status?: string;
  available_platforms?: Array<{ id: string; label: string; offer_id: string; source_url: string; last_updated_at: string }>;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

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
  const response = await safeJson<{ item: WorkDetail | null }>(`/api/works/${workId}`, undefined, { item: null });
  return response.item;
}

export async function getWorkOffers(workId: string): Promise<WorkOffer[]> {
  const response = await safeJson<{ items: WorkOffer[]; count: number }>(`/api/works/${workId}/offers`, undefined, { items: [], count: 0 });
  return response.items;
}
