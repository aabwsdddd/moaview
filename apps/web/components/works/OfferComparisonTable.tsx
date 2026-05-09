"use client";

import React, { useState } from "react";
import type { WorkOffer } from "../../lib/api";
import { getAnonymousSessionId, recordPlatformClick } from "../../lib/api";
import { PriceBadge } from "./PriceBadge";

function formatWon(value: number | null) {
  return value === null ? "-" : `${value.toLocaleString("ko-KR")}원`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("ko-KR");
}

type CtaType = "free_cta" | "lowest_price_cta" | "coupon_cta";

export function OfferComparisonTable({ offers, workId }: { offers: WorkOffer[]; workId: string }) {
  const [pendingCta, setPendingCta] = useState<string | null>(null);
  const sortedOffers = [...offers].sort((a, b) => a.effective_price_for_sort - b.effective_price_for_sort);
  const freeOffer = sortedOffers.find((offer) => offer.free_episode_count > 0) ?? sortedOffers[0];
  const lowestOffer = sortedOffers[0];
  const couponOffer = sortedOffers.find((offer) => offer.coupon_expected_price !== null) ?? sortedOffers[0];

  async function openOffer(offer: WorkOffer, ctaType: CtaType) {
    const key = `${offer.id}:${ctaType}`;
    setPendingCta(key);
    await recordPlatformClick({
      anonymous_session_id: getAnonymousSessionId(),
      work_id: workId,
      platform_id: offer.platform_id,
      offer_id: offer.id,
      cta_type: ctaType,
      effective_price_at_click: offer.effective_price_for_sort,
      destination_url: offer.source_url,
      clicked_at: new Date().toISOString(),
    });
    window.open(offer.source_url, "_blank", "noopener,noreferrer");
    setPendingCta(null);
  }

  if (offers.length === 0) {
    return (
      <div className="mt-6 rounded-2xl bg-slate-50 p-5 text-slate-600" role="status">
        fixture-backed API가 실행 중이면 /api/works/{workId}/offers 결과가 여기에 표시됩니다.
      </div>
    );
  }

  return (
    <div className="mt-6 space-y-6">
      <div className="grid gap-3 md:grid-cols-3">
        <button className="rounded-2xl bg-emerald-600 px-5 py-3 font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300" disabled={!freeOffer || pendingCta !== null} onClick={() => freeOffer && openOffer(freeOffer, "free_cta")} type="button">
          무료로 보기
        </button>
        <button className="rounded-2xl bg-moa px-5 py-3 font-semibold text-white transition hover:bg-violet-700 disabled:bg-slate-300" disabled={!lowestOffer || pendingCta !== null} onClick={() => lowestOffer && openOffer(lowestOffer, "lowest_price_cta")} type="button">
          최저가로 보기
        </button>
        <button className="rounded-2xl bg-amber-500 px-5 py-3 font-semibold text-white transition hover:bg-amber-600 disabled:bg-slate-300" disabled={!couponOffer || pendingCta !== null} onClick={() => couponOffer && openOffer(couponOffer, "coupon_cta")} type="button">
          쿠폰 받고 보기
        </button>
      </div>

      <div className="overflow-x-auto rounded-3xl border border-slate-200">
        <table className="min-w-[1100px] divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">플랫폼</th>
              <th className="px-4 py-3">무료 회차</th>
              <th className="px-4 py-3">기다무</th>
              <th className="px-4 py-3">기본가</th>
              <th className="px-4 py-3">확정가</th>
              <th className="px-4 py-3">쿠폰 적용 예상가</th>
              <th className="px-4 py-3">캐시백 포함 체감가</th>
              <th className="px-4 py-3">신뢰도</th>
              <th className="px-4 py-3">마지막 확인</th>
              <th className="px-4 py-3">출처</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {sortedOffers.map((offer) => (
              <tr key={offer.id}>
                <td className="px-4 py-4 font-bold text-ink">{offer.platform}</td>
                <td className="px-4 py-4">{offer.free_episode_count}화</td>
                <td className="px-4 py-4">{offer.wait_free_available ? "가능" : "없음"}</td>
                <td className="px-4 py-4">{formatWon(offer.base_price)}</td>
                <td className="px-4 py-4"><PriceBadge label="확정가" value={offer.instant_discounted_price} tone="confirmed" /></td>
                <td className="px-4 py-4"><PriceBadge label="쿠폰 적용 예상가" value={offer.coupon_expected_price} tone="expected" /></td>
                <td className="px-4 py-4"><PriceBadge label="캐시백 포함 체감가" value={offer.cashback_adjusted_price} tone="cashback" /></td>
                <td className="px-4 py-4">{offer.price_confidence}</td>
                <td className="px-4 py-4">{formatDate(offer.last_updated_at)}</td>
                <td className="max-w-64 break-all px-4 py-4">
                  <a className="font-semibold text-moa hover:text-violet-700" href={offer.source_url} rel="noreferrer" target="_blank">
                    {offer.source_url}
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {sortedOffers.map((offer) => (
          <details className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600" key={`${offer.id}-note`}>
            <summary className="cursor-pointer font-semibold text-ink">{offer.platform} 계산 기준 보기</summary>
            <p className="mt-3 leading-6">{offer.calculation_note}</p>
            {offer.active_coupons.length > 0 ? (
              <p className="mt-2 text-xs text-moa">쿠폰은 사용자 다운로드/수령이 필요할 수 있으므로 확정가가 아닌 쿠폰 적용 예상가로만 표시합니다.</p>
            ) : null}
          </details>
        ))}
      </div>
    </div>
  );
}
