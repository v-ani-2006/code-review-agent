import "@/styles/globals.css";
import { Providers } from "@/components/providers";

export const metadata = {
  title: "CodePilot AI — Autonomous Code Review & AI Reasoning Engine",
  description:
    "Production-grade, asynchronous code analysis platform coupling deterministic in-memory Python AST parsing, Radon complexity, and Bandit security with Google Gemini 2.5 Flash reasoning.",
  keywords: [
    "Code Review",
    "AST Analysis",
    "Gemini AI",
    "FastAPI",
    "Static Analysis",
    "Security Scanner",
    "Python Linter",
  ],
  authors: [{ name: "CodePilot AI Team" }],
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
