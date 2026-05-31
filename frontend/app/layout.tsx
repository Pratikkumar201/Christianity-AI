import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChristianityAI — Scripture-Grounded AI Assistant",
  description:
    "A production-grade AI assistant for Christianity: RAG-powered scripture QA, theology discussion, denomination awareness, content generation, and image creation — all grounded in Biblical truth.",
  keywords: ["Christianity", "Bible", "AI", "Scripture", "Theology", "RAG"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Cinzel:wght@400;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-navy-950 text-gray-100 antialiased">{children}</body>
    </html>
  );
}
