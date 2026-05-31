"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { healthCheck } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const check = async () => {
      const ok = await healthCheck();
      setBackendOnline(ok);
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  const links = [
    { href: "/", label: "Chat", icon: "💬" },
    { href: "/image-gen", label: "Image Gen", icon: "🎨" },
    { href: "/evaluation", label: "Evaluation", icon: "📊" },
  ];

  return (
    <nav className="sticky top-0 z-50 glass border-b border-gold-700/20">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gold-400 to-gold-700 flex items-center justify-center text-sm glow-gold-sm group-hover:glow-gold transition-all">
            ✝
          </div>
          <div>
            <span className="font-serif font-bold text-lg gold-text" style={{ fontFamily: "Cinzel, serif" }}>
              ChristianityAI
            </span>
            <div className="text-[10px] text-gray-400 leading-none -mt-0.5">
              Scripture-Grounded Assistant
            </div>
          </div>
        </Link>

        {/* Navigation Links */}
        <div className="flex items-center gap-6">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`nav-link flex items-center gap-1.5 ${pathname === link.href ? "active" : ""}`}
            >
              <span className="text-sm">{link.icon}</span>
              {link.label}
            </Link>
          ))}
        </div>

        {/* Backend Status */}
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              backendOnline === null
                ? "bg-gray-500"
                : backendOnline
                ? "bg-emerald-400 animate-pulse"
                : "bg-red-400"
            }`}
          />
          <span className="text-xs text-gray-400">
            {backendOnline === null ? "Connecting..." : backendOnline ? "API Online" : "API Offline"}
          </span>
        </div>
      </div>
    </nav>
  );
}
