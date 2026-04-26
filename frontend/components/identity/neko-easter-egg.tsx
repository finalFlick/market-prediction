"use client";

import { useState } from "react";

import { api, safe } from "@/lib/api";
import { cn } from "@/lib/utils";

type Out = { ok: true; text: string } | { ok: false; text: string };

function pretty(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

/**
 * Read-only Neko “terminal” for `/diagnostics` — whitelisted `neko.*()` → GETs only.
 */
export function NekoEasterEgg({ className }: { className?: string }) {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<string>("");
  const [busy, setBusy] = useState(false);

  async function runLine(raw: string): Promise<Out> {
    const line = raw.trim();
    if (line.length === 0) return { ok: true, text: "" };
    if (line === "help" || line === "neko.help()") {
      return {
        ok: true,
        text: [
          "Read-only pad (no writes, no orders):",
          "  neko.stats()     → /api/system/health + /api/system/metrics",
          "  neko.signal(s)  → /api/signals, filtered by name (client-side)",
          "  neko.backtest(id) → /api/backtests, filtered by strategy_id",
        ].join("\n"),
      };
    }
    if (line === "neko.stats()") {
      const [h, m] = await Promise.all([safe(() => api.health()), safe(() => api.metrics())]);
      return { ok: true, text: `health:\n${pretty(h)}\n\nmetrics:\n${pretty(m)}` };
    }
    const sig = /^neko\.signal\(([^)]+)\)\s*$/.exec(line);
    if (sig) {
      const arg = sig[1]?.trim().replace(/^["']|["']$/g, "") ?? "";
      if (!arg) return { ok: false, text: "usage: neko.signal('SYMBOL_OR_NAME_FRAGMENT')" };
      const list = (await safe(() => api.signals())) ?? [];
      const low = arg.toLowerCase();
      const filtered = list.filter(
        (s) => s.name.toLowerCase().includes(low) || s.signal_id.toLowerCase().includes(low)
      );
      return { ok: true, text: pretty(filtered) };
    }
    const bt = /^neko\.backtest\(([^)]+)\)\s*$/.exec(line);
    if (bt) {
      const arg = bt[1]?.trim().replace(/^["']|["']$/g, "") ?? "";
      if (!arg) return { ok: false, text: "usage: neko.backtest('strategy_id_fragment')" };
      const list = (await safe(() => api.backtests({ limit: 200 }))) ?? [];
      const low = arg.toLowerCase();
      const filtered = list.filter((b) => b.strategy_id.toLowerCase().includes(low));
      return { ok: true, text: pretty(filtered) };
    }
    return { ok: false, text: "Unknown command. Try: help" };
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    const line = input;
    setBusy(true);
    const res = await runLine(line);
    const block = `${`neko@market:~$ ${line}`}\n${res.ok ? res.text : `error: ${res.text}`}`;
    setHistory((h) => (h ? `${h}\n\n` : "") + block);
    setInput("");
    setBusy(false);
  }

  return (
    <div
      className={cn(
        "rounded-md border border-border/70 bg-crust/40 p-3 font-mono text-[11px]",
        className
      )}
    >
      <p className="text-[10px] text-muted-foreground">Read-only Neko console (GET endpoints only)</p>
      {history ? (
        <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap text-foreground/90">
          {history}
        </pre>
      ) : null}
      <form onSubmit={onSubmit} className="mt-2 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 rounded border border-border/60 bg-base px-2 py-1 text-xs text-foreground outline-none ring-primary/0 focus:ring-2 neko-cursor"
          placeholder="neko.stats()"
          spellCheck={false}
          autoComplete="off"
          disabled={busy}
        />
        <button
          type="submit"
          className="rounded border border-mauve/50 bg-surface0 px-2 py-1 text-xs text-mauve hover:bg-surface1"
          disabled={busy}
        >
          run
        </button>
      </form>
    </div>
  );
}
