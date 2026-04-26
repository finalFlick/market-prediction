import { Header } from "@/components/nav/header";
import { Card, CardContent, CardHeader, CardTitle, CardValue } from "@/components/ui/card";
import { api, safe } from "@/lib/api";
import { formatNumber, formatPct } from "@/lib/utils";

export default async function OverviewPage() {
  const [health, strategies, signals, backtests, trades] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.strategies()),
    safe(() => api.signals()),
    safe(() => api.backtests({ limit: 10 })),
    safe(() => api.trades({ limit: 10 })),
  ]);

  const liveStrategies = strategies?.filter((s) => s.status === "live").length ?? 0;
  const paperStrategies = strategies?.filter((s) => s.status === "paper").length ?? 0;
  const activeSignals = signals?.filter((s) => s.status !== "retired").length ?? 0;
  const lastBacktest = backtests?.[0];

  return (
    <main>
      <Header health={health} title="System Overview" />
      <div className="p-6 space-y-6">
        <p className="text-xs text-mauve/90 font-mono -mt-2">Neko&apos;s market notes</p>
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Live strategies</CardTitle>
              <CardValue>{liveStrategies}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Paper strategies</CardTitle>
              <CardValue>{paperStrategies}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Active signals</CardTitle>
              <CardValue>{activeSignals}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Recent trades (10)</CardTitle>
              <CardValue>{trades?.length ?? 0}</CardValue>
            </CardHeader>
          </Card>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Latest backtest — Sharpe</CardTitle>
              <CardValue>{formatNumber(lastBacktest?.sharpe ?? null, 2)}</CardValue>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground font-mono">
              {lastBacktest?.run_id ?? "no runs yet"}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Latest backtest — Max DD</CardTitle>
              <CardValue>{formatPct(lastBacktest?.max_drawdown ?? null, 1)}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Latest backtest — CAGR</CardTitle>
              <CardValue>{formatPct(lastBacktest?.cagr ?? null, 1)}</CardValue>
            </CardHeader>
          </Card>
        </section>
      </div>
    </main>
  );
}
