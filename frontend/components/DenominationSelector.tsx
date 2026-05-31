"use client";

import { DENOMINATIONS } from "@/lib/api";

interface DenominationSelectorProps {
  value: string;
  onChange: (denomination: string) => void;
}

const DENOMINATION_ICONS: Record<string, string> = {
  "Non-denominational": "✝️",
  "Catholic": "⛪",
  "Protestant": "📖",
  "Orthodox": "🕍",
  "Baptist": "🌊",
  "Methodist": "🙏",
  "Lutheran": "✡️",
  "Pentecostal": "🔥",
  "Anglican": "👑",
  "Presbyterian": "📜",
};

export default function DenominationSelector({ value, onChange }: DenominationSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400 whitespace-nowrap">Denomination:</span>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="appearance-none bg-navy-800/60 border border-gold-700/25 text-gray-200 text-xs rounded-lg px-3 py-1.5 pr-7 focus:outline-none focus:border-gold-500/50 cursor-pointer hover:border-gold-500/40 transition-colors"
          style={{ background: "rgba(15,31,51,0.8)" }}
        >
          {DENOMINATIONS.map((d) => (
            <option key={d} value={d}>
              {DENOMINATION_ICONS[d] || "✝"} {d}
            </option>
          ))}
        </select>
        <div className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gold-400 text-[10px]">
          ▾
        </div>
      </div>
    </div>
  );
}
