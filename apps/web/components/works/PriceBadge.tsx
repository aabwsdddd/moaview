export function PriceBadge({ label, value, tone = "default" }: { label: string; value: number | null; tone?: "default" | "confirmed" | "expected" | "cashback" }) {
  const tones = {
    default: "bg-slate-100 text-slate-700",
    confirmed: "bg-emerald-50 text-emerald-700",
    expected: "bg-violet-50 text-moa",
    cashback: "bg-amber-50 text-amber-700",
  };

  return (
    <span className={`inline-flex flex-col rounded-2xl px-3 py-2 text-xs font-semibold ${tones[tone]}`}>
      <span>{label}</span>
      <span className="mt-1 text-sm">{value === null ? "-" : `${value.toLocaleString("ko-KR")}원`}</span>
    </span>
  );
}
