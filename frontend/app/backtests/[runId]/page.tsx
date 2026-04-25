import { notFound } from "next/navigation";

import { Header } from "@/components/nav/header";
import { Card, CardContent, CardHeader, CardTitle, CardValue } from "@/components/ui/card";
import { api, safe } from "@/lib/api";
import { formatDate, formatNumber, formatPct } from "@/lib/utils";

export default async function BacktestDetailPage({
  params,
}: {
  params: { runId: string };
}) {
  const runId = decodeURIComponent(params.runId);
  const [health, run] = await Promise.all([safe(() => api.health()), safe(() => api.backtest(runId))]);
  if (!run) notFound();

  return (
    <main>
      <Header health={health} title={`Backtest · ${run.strategy_id}`} />
      <div className="p-6 space-y-6">
        <p className="text-xs font-mono text-muted-foreground break-all">{run.run_id}</p>
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Sharpe</CardTitle>
              <CardValue>{formatNumber(run.sharpe ?? null, 2)}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Sortino</CardTitle>
              <CardValue>{formatNumber(run.sortino ?? null, 2)}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Max drawdown</CardTitle>
              <CardValue>{formatPct(run.max_drawdown ?? null, 1)}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Final equity</CardTitle>
              <CardValue>{formatNumber(run.final_equity ?? null, 2)}</CardValue>
            </CardHeader>
          </Card>
        </section>
        <Card>
          <CardHeader>
            <CardTitle>Run metadata</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1 font-mono text-xs">
            <div>
              <span className="text-muted-foreground">strategy:</span> {run.strategy_id}
            </div>
            <div>
              <span className="text-muted-foreground">commit:</span> {run.git_commit ?? "—"}
            </div>
            <div>
              <span className="text-muted-foreground">cfg hash:</span> {run.config_hash ?? "—"}
            </div>
            <div>
              <span className="text-muted-foreground">started:</span>{" "}
              {formatDate(run.started_at)}
            </div>
            <div>
              <span className="text-muted-foreground">finished:</span>{" "}
              {formatDate(run.finished_at)}
            </div>
            <div>
              <span className="text-muted-foreground">trades:</span> {run.n_trades ?? "—"}
            </div>
            <div className="col-span-1 md:col-span-2 break-all">
              <span className="text-muted-foreground">artifacts:</span> {run.artifact_dir}
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
