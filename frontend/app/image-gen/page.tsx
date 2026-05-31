"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import { generateImage, generateSessionId } from "@/lib/api";
import Image from "next/image";

const EXAMPLE_PROMPTS = [
  "Noah's Ark during the Great Flood",
  "The Last Supper painting",
  "Moses parting the Red Sea",
  "The Garden of Gethsemane at night",
  "Nativity scene in Bethlehem",
  "Jesus walking on water",
  "The Good Shepherd",
  "David and Goliath",
  "The Resurrection of Jesus",
  "Angel Gabriel visiting Mary",
];

const [SESSION_ID] = [generateSessionId()];

export default function ImageGenPage() {
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{
    image_url: string | null;
    enhanced_prompt: string | null;
    answer: string;
    success: boolean;
    reason?: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<Array<{ prompt: string; url: string }>>([]);

  const handleGenerate = async () => {
    if (!prompt.trim() || isLoading) return;
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await generateImage(prompt, SESSION_ID);
      setResult(data);
      if (data.success && data.image_url) {
        setHistory((prev) => [{ prompt, url: data.image_url! }, ...prev.slice(0, 5)]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Image generation failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-navy-950">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-gold-400 to-gold-700 flex items-center justify-center text-2xl mx-auto mb-4 glow-gold">
            🎨
          </div>
          <h1 className="text-3xl font-bold gold-text mb-2" style={{ fontFamily: "Cinzel, serif" }}>
            Christian Image Generation
          </h1>
          <p className="text-gray-400 text-sm max-w-lg mx-auto">
            Generate reverent, Biblically-inspired artwork. Your prompt is safety-checked and enriched with Biblical context before generation.
          </p>
        </div>

        {/* Safety notice */}
        <div className="glass-light rounded-xl p-4 mb-6 flex items-start gap-3">
          <span className="text-gold-400 text-lg flex-shrink-0">🛡️</span>
          <div className="text-sm">
            <p className="text-gray-300 font-medium mb-0.5">Safety & Enrichment Pipeline</p>
            <p className="text-gray-500 text-xs">
              Every prompt passes through: (1) Content safety check → (2) Biblical context enrichment by LLM → (3) Image generation via Pollinations API. Hate content, violence, and offensive depictions are blocked.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Input */}
          <div className="lg:col-span-1 space-y-4">
            <div className="glass rounded-xl p-5">
              <h2 className="text-sm font-semibold text-gray-300 mb-3">Your Prompt</h2>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe a Biblical scene or Christian artwork..."
                rows={4}
                className="input-dark text-sm resize-none mb-3"
              />
              <button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isLoading}
                className="btn-gold w-full py-2.5 rounded-xl text-sm flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-navy-900/40 border-t-navy-900 rounded-full animate-spin" />
                    Generating...
                  </>
                ) : (
                  <> 🎨 Generate Image </>
                )}
              </button>
            </div>

            {/* Example prompts */}
            <div className="glass rounded-xl p-5">
              <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Example Prompts
              </h2>
              <div className="space-y-1.5">
                {EXAMPLE_PROMPTS.map((p) => (
                  <button
                    key={p}
                    onClick={() => setPrompt(p)}
                    className="w-full text-left text-xs text-gray-300 hover:text-gold-300 hover:bg-gold-900/10 px-2 py-1.5 rounded transition-colors"
                  >
                    • {p}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Result */}
          <div className="lg:col-span-2 space-y-4">
            {error && (
              <div className="glass rounded-xl p-4 border border-red-500/20 text-red-400 text-sm">
                ❌ {error}
              </div>
            )}

            {result && !result.success && (
              <div className="glass rounded-xl p-6 border border-red-500/20">
                <div className="flex items-center gap-2 text-red-400 mb-2">
                  <span>🛡️</span>
                  <span className="font-semibold">Request Blocked</span>
                </div>
                <p className="text-gray-400 text-sm">{result.reason}</p>
              </div>
            )}

            {result?.success && result.image_url && (
              <div className="glass rounded-xl overflow-hidden animate-fade-in">
                <Image
                  src={result.image_url}
                  alt={prompt}
                  width={768}
                  height={512}
                  className="w-full object-cover"
                  unoptimized
                />
                <div className="p-4 space-y-2">
                  <div>
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Enhanced Prompt Used</p>
                    <p className="text-xs text-gray-300 italic">{result.enhanced_prompt}</p>
                  </div>
                  <div className="flex gap-2">
                    <a
                      href={result.image_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-outline text-xs px-3 py-1.5 rounded-lg"
                    >
                      🔗 Open Full Size
                    </a>
                  </div>
                </div>
              </div>
            )}

            {!result && !isLoading && (
              <div className="glass rounded-xl p-12 flex flex-col items-center justify-center text-center">
                <div className="text-5xl mb-4 opacity-20">🎨</div>
                <p className="text-gray-500 text-sm">
                  Enter a Biblical prompt and click Generate Image
                </p>
                <p className="text-gray-600 text-xs mt-2">
                  Powered by Pollinations AI • Safety-checked • Biblically enriched
                </p>
              </div>
            )}

            {/* History */}
            {history.length > 0 && (
              <div className="glass rounded-xl p-4">
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  Recent Generations
                </h3>
                <div className="grid grid-cols-3 gap-2">
                  {history.map((h, i) => (
                    <button
                      key={i}
                      onClick={() => setPrompt(h.prompt)}
                      className="group relative rounded-lg overflow-hidden aspect-video"
                    >
                      <Image
                        src={h.url}
                        alt={h.prompt}
                        fill
                        className="object-cover group-hover:scale-105 transition-transform"
                        unoptimized
                      />
                      <div className="absolute inset-0 bg-navy-950/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-1">
                        <p className="text-[9px] text-white line-clamp-2">{h.prompt}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
