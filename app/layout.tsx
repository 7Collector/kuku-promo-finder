import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { readMeta } from "@/lib/kuku";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Kuku Promo Finder — AI Microdrama Acquisition Engine",
  description: "Automated scroll-stopping promo discovery for vertical microdramas using the Omega design system.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header
          style={{
            background: "var(--surface)",
            borderBottom: "1px solid var(--hairline)",
            position: "sticky",
            top: 0,
            zIndex: 100,
          }}
        >
          <div
            style={{
              maxWidth: 1200,
              margin: "0 auto",
              padding: "0 var(--page-margin)",
              height: 64,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "var(--s-16)" }}>
              <Link
                href="/"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "var(--s-8)",
                  textDecoration: "none",
                  color: "var(--ink)",
                }}
              >
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: "var(--radius-md)",
                    background: "var(--board)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#fff",
                  }}
                >
                  <i className="om-icon om-icon-sparkle" style={{ color: "#fff", width: 18, height: 18 }}></i>
                </div>
                <div>
                  <span className="om-body-strong" style={{ display: "block", lineHeight: "1.1" }}>
                    Kuku Promo Finder
                  </span>
                  <span className="om-caption" style={{ color: "var(--ink-3)" }}>
                    Microdrama Acquisition Engine
                  </span>
                </div>
              </Link>

              <div
                style={{
                  width: 1,
                  height: 24,
                  background: "var(--hairline)",
                  margin: "0 var(--s-8)",
                }}
              />

              <nav style={{ display: "flex", alignItems: "center", gap: "var(--s-4)" }}>
                <Link
                  href="/"
                  className="om-button om-button--compact"
                  style={{
                    background: "transparent",
                    color: "var(--ink)",
                    minHeight: 36,
                    padding: "0 var(--s-12)",
                  }}
                >
                  Ranked promos
                </Link>
                <Link
                  href="/episodes"
                  className="om-button om-button--compact"
                  style={{
                    background: "transparent",
                    color: "var(--ink)",
                    minHeight: 36,
                    padding: "0 var(--s-12)",
                  }}
                >
                  Screenplays
                </Link>
              </nav>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "var(--s-12)" }}>
              <span
                className="om-status-badge--neutral om-tag"
                style={{
                  background: "var(--neutral-container)",
                  color: "var(--neutral-on-container)",
                  padding: "4px 8px",
                  borderRadius: "var(--radius-xs)",
                  fontSize: 12,
                  fontFamily: "var(--font-sans)",
                }}
              >
                {(() => { const m = readMeta(); return m ? `${m.episodes} episodes · ${m.beats.toLocaleString()} beats` : "no run found"; })()}
              </span>

            </div>
          </div>
        </header>

        <main>{children}</main>

        <footer
          style={{
            borderTop: "1px solid var(--hairline)",
            background: "var(--surface)",
            padding: "var(--s-32) 0",
            marginTop: "var(--s-48)",
          }}
        >
          <div
            style={{
              maxWidth: 1200,
              margin: "0 auto",
              padding: "0 var(--page-margin)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              color: "var(--ink-3)",
              fontSize: 13,
            }}
          >
            <div>
              <span>Kuku AI Generalist Assignment · Problem 1 (Find the Promos)</span>
            </div>
            <div>
              <span>Styled with Omega design system · Inter & tabular figures</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
