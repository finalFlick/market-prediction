/**
 * Neko Quant voice / tone — copy lookup tables and route activity strings.
 * Playful only where DEC-012 allows; risk/exec surfaces stay neutral.
 */

export const NEKO_NOT_A_TRADE_SIGNAL = "Research observation. Not a trade signal." as const;

export const loadingPhrases: readonly string[] = [
  "Neko sharpening claws on data...",
  "Fetching market fish...",
  "Backtesting strategies...",
  "Analyzing market signals...",
  "Finding purr-fect opportunities...",
];

export const errorPhrases: readonly string[] = [
  "Neko is confused. Try again.",
  "Market data unavailable. Neko will nap until it returns.",
  "Something went wrong. Neko pounced on a bug.",
];

export const successPhrases: readonly string[] = [
  "Strategy validated. Good hunt.",
  "Backtest complete. Tails up.",
  "Data refreshed. Paws on the keys.",
];

/** Empty-state copy per surface (playful, non-operational). */
export const emptyBySurface: Record<string, string> = {
  runs: "No runs in the log yet. Neko is standing by.",
  backtests: "No backtest runs yet. Time to backtest, nyow.",
  signals: "No signals in view. Neko is scanning the wire.",
  strategies: "No strategies yet. Neko is waiting for ideas.",
  trades: "No trades in this window. Quiet markets.",
  learnings: "No learning rows yet. Teach Neko with a run first.",
  health: "Health data missing. Neko is concerned.",
  diagnostics: "Diagnostics are quiet. All systems, or napping?",
  configuration: "No config snapshot. Neko prefers typed YAML.",
  default: "Nothing here yet. Neko is watching.",
};

/** Playful one-liner for the configuration index (page is not an empty state). */
export const configurationIndexTagline =
  "Neko keeps configs typed and in Git — pick a section (read-only).";

/** Route path prefix → `neko@market:~$` activity blurb. */
export const routeActivity: Record<string, string> = {
  "/": "watching markets",
  "/trades": "tailing the tape",
  "/strategies": "scouting strategies",
  "/signals": "hunting signal hypotheses",
  "/diagnostics": "running read-only checks",
  "/backtests": "reviewing backtests",
  "/health": "pulsing the stack",
  "/runs": "tailing the run engine",
  "/learnings": "comparing OOS levers",
  "/configuration": "reading configs (read-only)",
  "/login": "awaiting your key",
};

export type NekoCopyCategory = "loading" | "error" | "success";

/** Deterministic pick for tests (same seed → same string). */
export function pickCopy(category: NekoCopyCategory, seed: number = 0): string {
  const table =
    category === "loading" ? loadingPhrases : category === "error" ? errorPhrases : successPhrases;
  const i = Math.abs(Math.floor(seed)) % table.length;
  return table[i] ?? table[0];
}

/** Activity for current pathname (longest prefix match). */
export function activityForPath(pathname: string): string {
  const keys = Object.keys(routeActivity).sort((a, b) => b.length - a.length);
  for (const k of keys) {
    if (pathname === k || (k !== "/" && pathname.startsWith(k))) {
      return routeActivity[k] ?? "watching";
    }
  }
  return "watching the stack";
}

export function emptyMessage(surface: keyof typeof emptyBySurface | string): string {
  if (surface in emptyBySurface) {
    return emptyBySurface[surface as keyof typeof emptyBySurface];
  }
  return emptyBySurface.default;
}

/** Ergonomic namespace for pages (`nekoVoice.empty("runs")`). */
export const nekoVoice = {
  empty: emptyMessage,
  loading: (seed = 0) => pickCopy("loading", seed),
  error: (seed = 0) => pickCopy("error", seed),
  success: (seed = 0) => pickCopy("success", seed),
};
