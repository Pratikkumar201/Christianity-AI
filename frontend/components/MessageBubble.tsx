"use client";

import { ChatMessage, ROUTE_LABELS, ROUTE_ICONS } from "@/lib/api";
import { useState } from "react";
import Image from "next/image";

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [showPipeline, setShowPipeline] = useState(false);
  const [showSources, setShowSources] = useState(false);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-slide-up`}>
      <div className={`max-w-[85%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-2`}>
        {/* Avatar + Route badge row (assistant only) */}
        {!isUser && (
          <div className="flex items-center gap-2 px-1">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-gold-400 to-gold-700 flex items-center justify-center text-xs flex-shrink-0">
              ✝
            </div>
            {message.route && (
              <span className={`badge route-${message.route}`}>
                {ROUTE_ICONS[message.route]} {ROUTE_LABELS[message.route]}
                {message.routingConfidence && (
                  <span className="opacity-60 ml-1">
                    {(message.routingConfidence * 100).toFixed(0)}%
                  </span>
                )}
              </span>
            )}
            {message.safety && (
              <span className={`badge ${message.safety.allowed ? "badge-safe" : "badge-danger"}`}>
                🛡 {message.safety.risk_level}
              </span>
            )}
            {message.responseTimeMs && (
              <span className="text-[10px] text-gray-500">{message.responseTimeMs}ms</span>
            )}
          </div>
        )}

        {/* Message bubble */}
        <div className={isUser ? "message-user px-4 py-3 text-sm" : "message-ai px-4 py-3 text-sm"}>
          {/* Safety block */}
          {message.route === "SAFETY_VIOLATION" && (
            <div className="flex items-center gap-2 mb-2 text-red-400">
              <span>⚠️</span>
              <span className="text-xs font-semibold uppercase tracking-wider">Safety Block</span>
            </div>
          )}

          {/* Main content */}
          <div className="text-gray-100 leading-relaxed whitespace-pre-wrap">
            {formatContent(message.content)}
          </div>

          {/* Image */}
          {message.imageUrl && (
            <div className="mt-3">
              <Image
                src={message.imageUrl}
                alt="Generated Christian Image"
                width={512}
                height={341}
                className="rounded-lg w-full object-cover border border-gold-700/20"
                unoptimized
              />
            </div>
          )}

          {/* Citations */}
          {message.citations && message.citations.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {message.citations.map((c, i) => (
                <span key={i} className="citation-tag">
                  📖 {c}
                </span>
              ))}
            </div>
          )}

          {/* Validation warning */}
          {message.validation && !message.validation.verified && (
            <div className="mt-2 p-2 rounded bg-red-900/20 border border-red-500/20 text-xs text-red-300">
              ⚠️ Citation validation failed — some references could not be verified.
              {message.validation.hallucinated?.length > 0 && (
                <span className="block mt-0.5 text-red-400">
                  Unverified: {message.validation.hallucinated.join(", ")}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Sources & Pipeline toggles (assistant only) */}
        {!isUser && (message.sources?.length || message.pipelineLog?.length) ? (
          <div className="flex gap-2 px-1">
            {message.sources && message.sources.length > 0 && (
              <button
                onClick={() => setShowSources(!showSources)}
                className="text-[11px] text-gold-400 hover:text-gold-300 transition-colors flex items-center gap-1"
              >
                📚 {showSources ? "Hide" : "View"} Sources ({message.sources.length})
              </button>
            )}
            {message.pipelineLog && message.pipelineLog.length > 0 && (
              <button
                onClick={() => setShowPipeline(!showPipeline)}
                className="text-[11px] text-gray-500 hover:text-gray-400 transition-colors flex items-center gap-1"
              >
                🔍 {showPipeline ? "Hide" : "Pipeline"} Log
              </button>
            )}
          </div>
        ) : null}

        {/* Sources panel */}
        {showSources && message.sources && message.sources.length > 0 && (
          <div className="glass-light rounded-lg p-3 space-y-2 w-full animate-fade-in">
            <p className="text-[11px] font-semibold text-gold-400 uppercase tracking-wider mb-2">
              📚 Retrieved Sources
            </p>
            {message.sources.map((s, i) => (
              <div key={i} className="text-xs border-l-2 border-gold-700/40 pl-2">
                <span className="text-gold-300 font-medium">[{s.reference}]</span>
                {s.score && (
                  <span className="ml-1 text-gray-500 text-[10px]">
                    (sim: {(s.score * 100).toFixed(1)}%)
                  </span>
                )}
                <p className="text-gray-300 mt-0.5 italic">&ldquo;{s.text}&rdquo;</p>
              </div>
            ))}
          </div>
        )}

        {/* Pipeline log */}
        {showPipeline && message.pipelineLog && (
          <div className="glass-light rounded-lg p-3 space-y-1.5 w-full animate-fade-in">
            <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
              🔍 Pipeline Trace
            </p>
            {message.pipelineLog.map((stage, i) => (
              <div key={i} className="pipeline-stage">
                <span className="text-gold-400 font-bold w-24 flex-shrink-0">
                  {stage.stage}
                </span>
                <span className="text-gray-300 text-[10px] overflow-hidden">
                  {JSON.stringify(
                    Object.fromEntries(
                      Object.entries(stage).filter(([k]) => k !== "stage" && k !== "timestamp")
                    )
                  )}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function formatContent(content: string): React.ReactNode {
  // Bold **text**
  const parts = content.split(/(\*\*[^*]+\*\*|\[[^\]]+\])/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} className="text-gold-300">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("[") && part.endsWith("]") && part.match(/\[[A-Za-z1-9 ]+ \d+:\d+\]/)) {
      return (
        <span key={i} className="citation-tag mx-0.5">
          📖 {part.slice(1, -1)}
        </span>
      );
    }
    return <span key={i}>{part}</span>;
  });
}
