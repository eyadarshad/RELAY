import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  title: "RELAY // Autonomous Operations Agent",
  description: "Give AI a mission. It handles the calls. Autonomous procurement, logistics rescue, bidding, and scheduling powered by CALL-E.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-void text-text-primary antialiased min-h-screen relative selection:bg-accent selection:text-void">
        {/* Subtle CRT Scanline overlay */}
        <div className="fixed inset-0 scanlines pointer-events-none z-50 opacity-40" />

        {/* Global Matrix Grid Background */}
        <div className="fixed inset-0 grid-bg opacity-30 pointer-events-none z-0" />

        {/* Main Content Viewport */}
        <div className="relative z-10 min-h-screen flex flex-col">
          {/* Top Global Command Bar */}
          <header className="border-b border-border bg-surface/90 backdrop-blur-sm px-4 sm:px-6 py-3 select-none">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
              <a href="/" className="flex items-center gap-2 group cursor-pointer">
                <div className="w-5 h-5 bg-accent flex items-center justify-center font-mono font-black text-void text-xs group-hover:rotate-45 transition-transform">
                  R
                </div>
                <span className="font-display font-black text-lg tracking-wider uppercase text-text-primary group-hover:text-accent transition-colors">
                  RELAY<span className="text-accent">.OPS</span>
                </span>
              </a>

              <div className="flex items-center gap-4 font-mono text-xs">
                <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 bg-surface-raised border border-border">
                  <span className="w-1.5 h-1.5 rounded-full bg-signal-green animate-pulse" />
                  <span className="text-[10px] text-text-secondary uppercase tracking-widest">
                    CALL-E ENGINE ONLINE
                  </span>
                </div>
                <span className="text-text-muted text-[10px]">v1.0.0</span>
              </div>
            </div>
          </header>

          {/* Page Body */}
          <main className="flex-1 flex flex-col">{children}</main>

          {/* Global Footer */}
          <footer className="border-t border-border bg-surface/60 px-4 sm:px-6 py-4 select-none font-mono text-[11px] text-text-muted">
            <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
              <div>
                <span>RELAY AUTONOMOUS OPERATIONS ENGINE</span> • CALL-E HACKATHON 2026
              </div>
              <div className="flex items-center gap-4 text-[10px]">
                <span>NO PLACEHOLDERS</span>
                <span>•</span>
                <span>REAL CALLS</span>
                <span>•</span>
                <span>MULTI-CALL AUTONOMY</span>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
