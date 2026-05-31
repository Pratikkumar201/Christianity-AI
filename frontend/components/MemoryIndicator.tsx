"use client";

import { SessionInfo } from "@/lib/api";

interface MemoryIndicatorProps {
  session: SessionInfo | null;
}

export default function MemoryIndicator({ session }: MemoryIndicatorProps) {
  if (!session) return null;

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 glass-light rounded-lg text-xs">
      <div className="flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        <span className="text-gray-400">Memory</span>
      </div>
      <span className="text-gold-400 font-medium">{session.denomination}</span>
      {session.message_count > 0 && (
        <>
          <span className="text-gray-600">•</span>
          <span className="text-gray-400">{session.message_count} msgs</span>
        </>
      )}
      {session.history_length > 0 && (
        <>
          <span className="text-gray-600">•</span>
          <span className="text-emerald-400/70">{session.history_length} in context</span>
        </>
      )}
    </div>
  );
}
