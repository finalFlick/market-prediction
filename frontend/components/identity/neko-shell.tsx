"use client";

import { createContext, useContext, useMemo, useState } from "react";

import { cn } from "@/lib/utils";

import type { NekoMascotState } from "./neko-mascot";
import { NekoStatus } from "./neko-status";

type Ctx = {
  mood: NekoMascotState;
  setMood: (m: NekoMascotState) => void;
};

const NekoMoodContext = createContext<Ctx | null>(null);

export function useNekoMood(): Ctx {
  const v = useContext(NekoMoodContext);
  if (!v) {
    return {
      mood: "analyzing",
      setMood: () => {
        /* no-op if shell missing */
      },
    };
  }
  return v;
}

/**
 * App chrome: terminal prompt + optional mood override for pages that use `useNekoMood()`.
 */
export function NekoShell({ children, className }: { children: React.ReactNode; className?: string }) {
  const [mood, setMood] = useState<NekoMascotState>("analyzing");
  const value = useMemo(() => ({ mood, setMood }), [mood]);
  return (
    <NekoMoodContext.Provider value={value}>
      <div className={cn("flex min-h-screen min-w-0 flex-col", className)}>
        <NekoStatus />
        <div className="flex min-h-0 min-w-0 flex-1">{children}</div>
      </div>
    </NekoMoodContext.Provider>
  );
}
