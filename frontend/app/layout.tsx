import type { Metadata } from "next";

import { Sidebar } from "@/components/nav/sidebar";

import "./globals.css";

export const metadata: Metadata = {
  title: "trading-lab",
  description: "Quantitative trading research platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen">
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 min-w-0">{children}</div>
        </div>
      </body>
    </html>
  );
}
