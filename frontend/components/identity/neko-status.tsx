"use client";

import { usePathname } from "next/navigation";

import { activityForPath } from "@/lib/neko-voice";
import { cn } from "@/lib/utils";

export function NekoStatus({ className }: { className?: string }) {
  const pathname = usePathname() ?? "/";
  const activity = activityForPath(pathname);

  return (
    <div
      className={cn(
        "w-full border-b border-border/60 bg-mantle/80 px-4 py-1.5 font-mono text-[11px] text-subtext0",
        "neko-scanline",
        className
      )}
    >
      <span className="text-mauve">neko@market</span>
      <span className="text-subtext0">:~$</span>{" "}
      <span className="text-foreground/90">{activity}</span>
    </div>
  );
}
