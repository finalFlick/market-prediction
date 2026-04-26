/**
 * Typed client for the trading-lab backend API.
 *
 * Server components call these functions directly. The base URL is read from
 * NEXT_PUBLIC_API_URL so the same code works from the browser and from a
 * server-side render in a docker network.
 */

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://backend:8000";

async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export type Trade = {
  trade_id: string;
  client_order_id: string;
  strategy_id: string | null;
  exchange: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  fee: number;
  pnl: number | null;
  venue: string;
  ts: string;
};

export type Strategy = {
  strategy_id: string;
  name: string;
  universe: string[];
  timeframe: string;
  status: string;
  config_path: string | null;
  created_at: string;
  updated_at: string;
};

export type Signal = {
  signal_id: string;
  name: string;
  status: string;
  timeframe: string;
  intuition: string | null;
  owner: string | null;
  updated_at: string;
};

export type Backtest = {
  run_id: string;
  strategy_id: string;
  git_commit: string | null;
  config_hash: string | null;
  started_at: string;
  finished_at: string | null;
  sharpe: number | null;
  sortino: number | null;
  max_drawdown: number | null;
  cagr: number | null;
  final_equity: number | null;
  n_trades: number | null;
  artifact_dir: string;
};

export type Health = {
  status: string;
  version: string;
  env: string;
  uptime_s: number;
  db_ok: boolean;
  redis_ok: boolean;
  redis_disabled: boolean;
};

export type Run = {
  run_id: string;
  run_type: string;
  mode: string;
  status: string;
  config_hash: string | null;
  git_commit: string | null;
  started_at: string | null;
  finished_at: string | null;
  error_reason: string | null;
};

export type RunDetail = Run & {
  config_json: string;
  artifact_dir: string | null;
};

export type RunCompareRow = {
  run_id: string;
  run_type: string;
  mode: string;
  status: string;
  config_hash: string | null;
  git_commit: string | null;
  started_at: string | null;
  finished_at: string | null;
  sharpe: number | null;
  max_drawdown: number | null;
  cagr: number | null;
  n_trades: number | null;
  artifact_dir: string | null;
};

export type ScoreboardRow = {
  level: string;
  key: string;
  score: number;
  weight: number;
  last_run_id: string | null;
  updated_at: string;
};

export const api = {
  trades: (params?: {
    strategy_id?: string;
    symbol?: string;
    venue?: string;
    limit?: number;
  }) => {
    const q = new URLSearchParams();
    if (params?.strategy_id) q.set("strategy_id", params.strategy_id);
    if (params?.symbol) q.set("symbol", params.symbol);
    if (params?.venue) q.set("venue", params.venue);
    if (params?.limit) q.set("limit", String(params.limit));
    return getJson<Trade[]>(`/api/trades?${q.toString()}`);
  },
  strategies: () => getJson<Strategy[]>("/api/strategies"),
  strategy: (id: string) => getJson<Strategy>(`/api/strategies/${id}`),
  signals: (status?: string) =>
    getJson<Signal[]>(`/api/signals${status ? `?status=${status}` : ""}`),
  backtests: (params?: { strategy_id?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.strategy_id) q.set("strategy_id", params.strategy_id);
    if (params?.limit) q.set("limit", String(params.limit));
    return getJson<Backtest[]>(`/api/backtests?${q.toString()}`);
  },
  backtest: (runId: string) => getJson<Backtest>(`/api/backtests/${runId}`),
  runs: (params?: { status?: string; run_type?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.run_type) q.set("run_type", params.run_type);
    if (params?.limit) q.set("limit", String(params.limit));
    return getJson<{ items: Run[] }>(`/api/runs?${q.toString()}`).then((r) => r.items);
  },
  run: (runId: string) => getJson<RunDetail>(`/api/runs/${runId}`),
  compareRuns: (ids: string[]) =>
    getJson<RunCompareRow[]>(`/api/learnings/compare?ids=${ids.join(",")}`),
  scoreboard: () => getJson<ScoreboardRow[]>("/api/learnings/scoreboard"),
  health: () => getJson<Health>("/api/system/health"),
  metrics: () => getJson<{ metrics: Record<string, number> }>("/api/system/metrics"),
};

export async function safe<T>(fn: () => Promise<T>): Promise<T | null> {
  try {
    return await fn();
  } catch {
    return null;
  }
}
