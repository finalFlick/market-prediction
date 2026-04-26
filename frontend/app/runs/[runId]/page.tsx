import Link from "next/link";
import { notFound } from "next/navigation";
import { Header } from "@/components/nav/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, safe } from "@/lib/api";
import { formatDate, formatNumber, formatPct } from "@/lib/utils";

export default async function RunDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;
  const [health, run, backtest] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.run(runId)),
    safe(() => api.backtest(runId)),
  ]);

  if (!run) {
    notFound();
  }

  const cfg = (() => {
    try {
      return JSON.parse(run.config_json ?? "{}");
    } catch {
      return {};
    }
  })();

  return (
    <main>
      <Header health={health} title={`Run — ${runId}`} />
      <div className="p-6 space-y-6">
        {/* Summary */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Status</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge
                variant={
                  run.status === "succeeded"
                    ? "success"
                    : run.status === "failed"
                    ? "danger"
                    : "default"
                }
              >
                {run.status}
              </Badge>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Type / Mode</CardTitle>
            </CardHeader>
            <CardContent className="font-mono text-sm">
              {run.run_type} / {run.mode}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Started</CardTitle>
            </CardHeader>
            <CardContent className="font-mono text-xs">{formatDate(run.started_at)}</CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Finished</CardTitle>
            </CardHeader>
            <CardContent className="font-mono text-xs">{formatDate(run.finished_at)}</CardContent>
          </Card>
        </section>

        {/* Backtest metrics */}
        {backtest && (
          <section>
            <h2 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">
              Backtest metrics
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <Card>
                <CardHeader><CardTitle>Sharpe</CardTitle></CardHeader>
                <CardContent className="font-mono">{formatNumber(backtest.sharpe)}</CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle>Sortino</CardTitle></CardHeader>
                <CardContent className="font-mono">{formatNumber(backtest.sortino)}</CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle>Max DD</CardTitle></CardHeader>
                <CardContent className="font-mono">{formatPct(backtest.max_drawdown)}</CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle>CAGR</CardTitle></CardHeader>
                <CardContent className="font-mono">{formatPct(backtest.cagr)}</CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle>Trades</CardTitle></CardHeader>
                <CardContent className="font-mono">{backtest.n_trades ?? "—"}</CardContent>
              </Card>
            </div>
            {backtest.artifact_dir && (
              <p className="mt-2 text-xs text-muted-foreground font-mono">
                Artifacts: {backtest.artifact_dir}
              </p>
            )}
          </section>
        )}

        {/* Error */}
        {run.error_reason && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Error</CardTitle>
            </CardHeader>
            <CardContent className="font-mono text-xs text-destructive">
              {run.error_reason}
            </CardContent>
          </Card>
        )}

        {/* Config */}
        <Card>
          <CardHeader>
            <CardTitle>Run config</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs font-mono bg-panel/60 rounded p-3 overflow-x-auto">
              {JSON.stringify(cfg, null, 2)}
            </pre>
          </CardContent>
        </Card>

        {/* Audit */}
        <div className="text-xs text-muted-foreground">
          <p>
            Risk audit rows:{" "}
            <code className="text-mint">
              SELECT * FROM ha_risk_decisions WHERE run_id = &apos;{runId}&apos;
            </code>
          </p>
          <p className="mt-1">
            <Link href="/runs" className="text-mint hover:underline">
              ← Back to runs
            </Link>
            {" · "}
            <Link
              href={`/runs/compare?ids=${runId}`}
              className="text-mint hover:underline"
            >
              Compare this run
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
