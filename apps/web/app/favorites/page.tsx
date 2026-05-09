import React from "react";
import { FavoritesList } from "../../components/favorites/FavoritesList";
import { listFavorites } from "../../lib/api/favorites";

export default async function FavoritesPage() {
  const favorites = await listFavorites();

  return (
    <main className="mx-auto min-h-screen max-w-3xl px-6 py-12">
      <FavoritesList items={favorites.items} />
    </main>
  );
}
