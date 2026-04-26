import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

import { NekoShell } from "@/components/identity/neko-shell";
import { Sidebar } from "@/components/nav/sidebar";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "trading-lab",
  description: "Quantitative trading research platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`dark ${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen font-sans antialiased">
        <NekoShell>
          <div className="flex min-h-screen w-full min-w-0">
            <Sidebar />
            <div className="min-w-0 flex-1">{children}</div>
          </div>
        </NekoShell>
      </body>
    </html>
  );
}
