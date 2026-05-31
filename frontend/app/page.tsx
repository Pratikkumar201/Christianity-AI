"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Navbar from "@/components/Navbar";
import MessageBubble from "@/components/MessageBubble";
import DenominationSelector from "@/components/DenominationSelector";
import MemoryIndicator from "@/components/MemoryIndicator";
import {
  ChatMessage,
  SessionInfo,
  sendChat,
  getSessionInfo,
  generateSessionId,
} from "@/lib/api";

const SUGGESTED_PROMPTS = [
  { label: "📖 John 3:16", prompt: "What does John 3:16 say and what does it mean?" },
  { label: "⛪ Salvation", prompt: "What does the Bible say about salvation?" },
  { label: "✍️ Write Sermon", prompt: "Write a short sermon on God's grace" },
  { label: "🔍 Verify Verse", prompt: "Is Romans 15:99 a real Bible verse?" },
  { label: "🙏 Prayer", prompt: "Write a prayer for healing and strength" },
  { label: "⚖️ Purgatory", prompt: "What do different denominations believe about purgatory?" },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const [denomination, setDenomination] = useState("Non-denominational");
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Welcome message
  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content:
          "Peace be with you! 🙏\n\nI am **ChristianityAI**, a scripture-grounded assistant. I can:\n\n• **Answer Bible questions** using retrieved scripture\n• **Discuss theology** with denomination-aware perspectives\n• **Generate Christian content** (sermons, devotionals, prayers)\n• **Verify Bible verses** and detect fake references\n• **Create Christian images** via AI generation\n\nAll my answers are grounded in the Bible — I will never fabricate scripture. How can I assist you today?",
        citations: [],
        sources: [],
      },
    ]);
  }, []);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Refresh session info after each message
  const refreshSession = useCallback(async () => {
    try {
      const info = await getSessionInfo(sessionId);
      setSessionInfo(info);
    } catch {}
  }, [sessionId]);

  const handleSend = async (messageText?: string) => {
    const text = (messageText || input).trim();
    if (!text || isLoading) return;

    setInput("");
    setError(null);

    const userMessage: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChat(text, sessionId, denomination);
      setMessages((prev) => [...prev, response]);
      await refreshSession();
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : "Unknown error";
      setError(errMsg);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `❌ Error: ${errMsg}. Please make sure the backend is running on http://localhost:8000`,
          citations: [],
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
    setMessages([
      {
        role: "assistant",
        content: "Chat cleared. How can I assist you with your Biblical questions?",
        citations: [],
      },
    ]);
  };

  return (
    <div className="flex flex-col h-screen bg-navy-950">
      <Navbar />

      {/* Hero Banner */}
      <div className="border-b border-gold-700/10" style={{ background: "rgba(15,31,51,0.5)" }}>
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <DenominationSelector
              value={denomination}
              onChange={(d) => setDenomination(d)}
            />
            <MemoryIndicator session={sessionInfo} />
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={clearChat}
              className="btn-outline text-xs px-3 py-1.5 rounded-lg"
            >
              🗑 Clear Chat
            </button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}

          {/* Typing indicator */}
          {isLoading && (
            <div className="flex justify-start animate-fade-in">
              <div className="message-ai px-4 py-3 flex items-center gap-1.5">
                <div className="flex items-center gap-2 text-xs text-gray-400 mr-2">
                  <span className="text-[10px]">✝</span>
                  Processing pipeline...
                </div>
                <div className="flex gap-1">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Suggested prompts (shown when empty) */}
      {messages.length <= 1 && (
        <div className="max-w-4xl mx-auto px-4 pb-3">
          <p className="text-xs text-gray-500 mb-2 text-center">Try these examples:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {SUGGESTED_PROMPTS.map((p) => (
              <button
                key={p.prompt}
                onClick={() => handleSend(p.prompt)}
                className="btn-outline text-xs px-3 py-1.5 rounded-lg hover:scale-105 transition-transform"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error banner */}
      {error && (
        <div className="max-w-4xl mx-auto px-4 mb-2">
          <div className="text-xs text-red-400 bg-red-900/20 border border-red-500/20 rounded-lg px-3 py-2">
            ⚠️ {error}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gold-700/10 bg-navy-950/90 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a Bible question, request content, verify a verse... (Enter to send, Shift+Enter for newline)"
                rows={2}
                className="input-dark resize-none text-sm leading-relaxed"
                disabled={isLoading}
              />
              <div className="absolute right-3 bottom-2.5 text-[10px] text-gray-600">
                {input.length > 0 && `${input.length} chars`}
              </div>
            </div>
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              className="btn-gold px-5 py-3 rounded-xl text-sm flex items-center gap-2 flex-shrink-0"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-navy-900/40 border-t-navy-900 rounded-full animate-spin" />
                  Processing
                </>
              ) : (
                <>
                  <span>Send</span>
                  <span>↑</span>
                </>
              )}
            </button>
          </div>

          {/* Footer info */}
          <div className="flex items-center justify-between mt-2">
            <p className="text-[10px] text-gray-600">
              ✝ All responses are grounded in scripture • Citations verified • Hallucination prevention active
            </p>
            <p className="text-[10px] text-gray-600">
              Session: {sessionId.slice(-8)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
