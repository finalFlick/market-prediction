import { Header } from "@/components/nav/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, safe } from "@/lib/api";

export default async function DiagnosticsPage() {
  const [health, metrics, backtests] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.metrics()),
    safe(() => api.backtests({ limit: 5 })),
  ]);

  const m = metrics?.metrics ?? {};
  const rows = Object.entries(m).sort(([a], [b]) => a.localeCompare(b));

  return (
    <main>
      <Header health={health} title="Model Diagnostics" />
      <div className="p-6 space-y-6">
        <p className="text-sm text-muted-foreground">
          Live metric snapshot from the engine plus headline metrics from the most recent
          backtests. Drift detection runs on the engine; alerts surface here.
        </p>

        <Card>
          <CardHeader>
            <CardTitle>Engine metrics (gauge + counter snapshot)</CardTitle>
          </CardHeader>
          <CardContent className="font-mono text-sm space-y-1">
            {rows.length === 0 ? (
              <span className="text-muted-foreground">no metrics published yet</span>
            ) : (
              rows.map(([k, v]) => (
                <div key={k} className="flex justify-between border-b border-border/50 py-0.5">
                  <span className="text-muted-foreground">{k}</span>
                  <span>{Number(v).toLocaleString()}</span>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent backtests — IC / metrics</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            {(backtests ?? []).map((b) => (
              <div
                key={b.run_id}
                className="grid grid-cols-2 md:grid-cols-5 gap-3 font-mono text-xs border-b border-border/50 pb-2"
              >
                <div className="col-span-2 truncate">
                  <span className="text-muted-foreground">run:</span> {b.run_id}
                </div>
                <div>
                  <span className="text-muted-foreground">sharpe:</span>{" "}
                  {b.sharpe?.toFixed(2) ?? "—"}
                </div>
                <div>
                  <span className="text-muted-foreground">maxDD:</span>{" "}
                  {b.max_drawdown != null ? (b.max_drawdown * 100).toFixed(1) + "%" : "—"}
                </div>
                <div>
                  <span className="text-muted-foreground">trades:</span> {b.n_trades ?? "—"}
                </div>
              </div>
            ))}
            {(backtests ?? []).length === 0 ? (
              <p className="text-muted-foreground">no backtests yet</p>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
