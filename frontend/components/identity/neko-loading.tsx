"use client";

import { useEffect, useState } from "react";

import { pickCopy } from "@/lib/neko-voice";
import { cn } from "@/lib/utils";

import { NekoMascot } from "./neko-mascot";
import { PawIcon } from "./neko-icons";

function asciiBar(pct: number, width = 12): string {
  const w = Math.max(1, width);
  const filled = Math.round((pct / 100) * w);
  const f = "█".repeat(Math.min(filled, w));
  const e = "░".repeat(w - f.length);
  return `[${f}${e}] ${Math.round(pct)}%`;
}

export function NekoLoading({
  progress,
  className,
  messageSeed = 0,
}: {
  /** 0–100. Omit for indeterminate shimmer. */
  progress?: number;
  className?: string;
  messageSeed?: number;
}) {
  const [tick, setTick] = useState(0);
  const indeterminate = progress == null;
  const [fake, setFake] = useState(0);

  useEffect(() => {
    if (!indeterminate) return;
    const id = window.setInterval(() => {
      setTick((t) => (t + 1) % 8);
      setFake((f) => {
        const n = (f + 11) % 101;
        return n < 8 ? 12 : n;
      });
    }, 320);
    return () => window.clearInterval(id);
  }, [indeterminate]);

  const pct = indeterminate ? fake : progress;
  const line = pickCopy("loading", messageSeed + tick);
  const pawPhases = ["🐾", "·", "·", "·"] as const;
  const paw = pawPhases[(tick + messageSeed) % 4] ?? "🐾";

  return (
    <div
      className={cn("rounded-md border border-border/60 bg-surface0/50 p-4 font-mono text-xs", className)}
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <NekoMascot state="analyzing" size="sm" className="animate-paw-bounce" />
          <div>
            <p className="text-foreground/90">{line}</p>
            <p
              className="mt-1 text-[11px] text-mauve/90 tabular-nums"
              aria-live="polite"
            >
              {asciiBar(Math.min(100, Math.max(0, pct)))} {paw}
            </p>
          </div>
        </div>
        <PawIcon className="h-5 w-5 text-mauve/70 animate-paw-bounce" />
      </div>
    </div>
  );
}
