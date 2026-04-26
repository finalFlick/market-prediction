"use client";

import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export type LogEvent = { id: string; ts: string; level: string; message: string };

export function LogStream({ events, className }: { events: LogEvent[]; className?: string }) {
  const [q, setQ] = useState("");
  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return events;
    return events.filter(
      (e) =>
        e.message.toLowerCase().includes(needle) ||
        e.id.toLowerCase().includes(needle) ||
        e.level.toLowerCase().includes(needle),
    );
  }, [events, q]);

  return (
    <div className={cn("rounded-lg border border-border/70 bg-base/50", className)}>
      <div className="flex items-center gap-2 border-b border-border/60 p-2">
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="filter events"
          className="h-8 font-mono text-xs"
        />
      </div>
      <ul className="max-h-64 overflow-auto divide-y divide-border/50 font-mono text-[11px]">
        {filtered.map((e) => (
          <li key={e.id} className="flex items-start justify-between gap-2 px-3 py-2">
            <div>
              <span className="text-muted-foreground">{e.ts}</span>{" "}
              <span
                className={cn(
                  e.level === "error" && "text-danger",
                  e.level === "warn" && "text-warning",
                  e.level === "info" && "text-primary",
                )}
              >
                {e.level}
              </span>{" "}
              <span className="text-foreground/90">{e.message}</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 px-2 text-[10px]"
              onClick={() => {
                void navigator.clipboard.writeText(e.id);
              }}
            >
              copy id
            </Button>
          </li>
        ))}
      </ul>
    </div>
  );
}
