import type { HistogramData } from "lightweight-charts";

import type { ExposureSeries } from "@/components/charts/risk-exposure-chart";
import type { EquityPoint } from "@/components/charts/equity-chart";
import type { EvidenceRow } from "@/components/data/evidence-table";
import type { LogEvent } from "@/components/operator/log-stream";
import type { CommandItem } from "@/components/operator/command-palette";
import type { TimelineEvent } from "@/components/operator/run-timeline";
import type { Trade } from "@/lib/api";
import type { Health } from "@/lib/api";

/** Deterministic pseudo-random in [0,1) from integer seed (stable across runs). */
function det01(seed: number): number {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

export function mockEquitySeries(n = 90): EquityPoint[] {
  const out: EquityPoint[] = [];
  let v = 1;
  for (let i = 0; i < n; i += 1) {
    const drift = (det01(i + 11) - 0.48) * 0.008;
    v = Math.max(0.5, v * (1 + drift));
    const d = new Date(Date.UTC(2024, 0, 1 + i));
    out.push({ time: d.toISOString().slice(0, 10), value: Number(v.toFixed(4)) });
  }
  return out;
}

export const mockTradesPopulated: Trade[] = [
  {
    trade_id: "t-1",
    client_order_id: "coid-1",
    strategy_id: "demo",
    exchange: "paper",
    symbol: "BTCUSDT",
    side: "buy",
    quantity: 0.01,
    price: 42000,
    fee: 0.12,
    pnl: 1.23,
    venue: "paper",
    ts: "2024-06-01T12:00:00Z",
  },
  {
    trade_id: "t-2",
    client_order_id: "coid-2",
    strategy_id: "demo",
    exchange: "paper",
    symbol: "BTCUSDT",
    side: "sell",
    quantity: 0.01,
    price: 42100,
    fee: 0.13,
    pnl: -0.4,
    venue: "live",
    ts: "2024-06-01T13:00:00Z",
  },
];

export const mockTradesEmpty: Trade[] = [];

export const mockHealthOk: Health = {
  status: "ok",
  version: "0.2.0",
  env: "dev",
  uptime_s: 1234,
  db_ok: true,
  redis_ok: true,
  redis_disabled: false,
};

export const mockHealthDegraded: Health = {
  status: "degraded",
  version: "0.2.0",
  env: "dev",
  uptime_s: 60,
  db_ok: false,
  redis_ok: true,
  redis_disabled: false,
};

export const mockEvidenceRows: EvidenceRow[] = [
  {
    runId: "run-a",
    sharpeOos: 1.42,
    maxDdOos: -0.08,
    artifact: "s3://demo/run-a",
    configHash: "cfg:deadbeef",
    auditHash: "audit:cafe",
  },
  {
    runId: "run-b",
    sharpeOos: 0.88,
    maxDdOos: -0.12,
    artifact: "s3://demo/run-b",
    configHash: "cfg:beeff00d",
    auditHash: "audit:babe",
  },
];

export const mockExposureSeries: ExposureSeries[] = [
  {
    id: "BTC",
    color: "rgb(94, 234, 212)",
    points: mockEquitySeries(40).map((p, i) => ({ time: p.time, value: p.value * 0.4 + i * 0.01 })),
  },
  {
    id: "ETH",
    color: "rgb(196, 181, 253)",
    points: mockEquitySeries(40).map((p, i) => ({ time: p.time, value: p.value * 0.35 + i * 0.008 })),
  },
];

export const mockHistogram = Array.from({ length: 24 }).map((_, i) => ({
  time: `2024-01-${String((i % 27) + 1).padStart(2, "0")}`,
  value: Math.round(10 + det01(i + 3) * 40),
  color: i > 18 ? "rgba(239,68,68,0.65)" : "rgba(244,114,182,0.65)",
})) as HistogramData[];

export const mockSparkline = mockEquitySeries(32).map((p) => ({ time: p.time, value: p.value * 0.02 }));

export const mockTimeline: TimelineEvent[] = [
  { id: "e1", at: "2024-06-01T10:00:00Z", state: "queued" },
  { id: "e2", at: "2024-06-01T10:00:02Z", state: "running", note: "worker claimed" },
  { id: "e3", at: "2024-06-01T10:02:11Z", state: "failed", note: "risk rejected", recovered: true },
  { id: "e4", at: "2024-06-01T10:05:00Z", state: "succeeded", note: "replay clean" },
];

export const mockLogEvents: LogEvent[] = [
  { id: "log-1", ts: "10:00:01", level: "info", message: "run queued" },
  { id: "log-2", ts: "10:00:02", level: "warn", message: "latency high on redis" },
  { id: "log-3", ts: "10:00:04", level: "error", message: "risk: gross exposure cap" },
];

export const mockCommands: CommandItem[] = [
  { id: "c1", label: "Queue config diff review", group: "approvals" },
  { id: "c2", label: "Attach artifact to audit", group: "approvals" },
  { id: "c3", label: "Open run compare", group: "navigation" },
];
