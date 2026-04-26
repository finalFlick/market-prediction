"use client";

import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export type CommandItem = { id: string; label: string; group: string };

export type CommandPaletteHandlers = {
  onCommand: (cmd: CommandItem) => void;
};

export function CommandPalette({
  commands,
  onCommand,
  className,
  initialOpen = false,
}: {
  commands: CommandItem[];
  onCommand: CommandPaletteHandlers["onCommand"];
  className?: string;
  /** Styleguide / tests: start opened without a global hotkey. */
  initialOpen?: boolean;
}) {
  const [open, setOpen] = useState(initialOpen);
  const [q, setQ] = useState("");

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return commands;
    return commands.filter((c) => c.label.toLowerCase().includes(needle));
  }, [commands, q]);

  if (!open) {
    return (
      <p className={cn("text-xs text-muted-foreground font-mono", className)}>
        Press <kbd className="rounded border border-border px-1">⌘</kbd>+
        <kbd className="rounded border border-border px-1">K</kbd> to open palette
      </p>
    );
  }

  return (
    <div
      className={cn(
        "fixed inset-0 z-50 flex items-start justify-center bg-black/60 backdrop-blur-sm p-10",
        className,
      )}
    >
      <div className="w-full max-w-lg rounded-lg border border-border bg-card p-3 shadow-md">
        <Input
          autoFocus
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search commands…"
          className="font-mono text-sm"
        />
        <ul className="mt-3 max-h-72 overflow-auto space-y-1">
          {filtered.map((c) => (
            <li key={c.id}>
              <Button
                variant="command"
                className="w-full justify-between"
                onClick={() => {
                  onCommand(c);
                  setOpen(false);
                  setQ("");
                }}
              >
                <span>{c.label}</span>
                <span className="text-[10px] text-muted-foreground">{c.group}</span>
              </Button>
            </li>
          ))}
        </ul>
        <p className="mt-2 text-[10px] text-muted-foreground font-mono">
          Mutations enqueue operator approvals; never calls brokers directly.
        </p>
      </div>
    </div>
  );
}
