import Link from "next/link";

import { Header } from "@/components/nav/header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, safe } from "@/lib/api";
import { nekoVoice } from "@/lib/neko-voice";
import { formatDate } from "@/lib/utils";

const statusVariant = (status: string) =>
  ({
    live: "primary",
    paper: "warning",
    backtest: "outline",
    retired: "danger",
  }[status] ?? "default") as "primary" | "warning" | "outline" | "danger" | "default";

export default async function StrategiesPage() {
  const [health, strategies, backtests] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.strategies()),
    safe(() => api.backtests({ limit: 100 })),
  ]);

  return (
    <main>
      <Header health={health} title="Strategy Performance" />
      <div className="p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(strategies ?? []).map((s) => {
            const latest = backtests?.find((b) => b.strategy_id === s.strategy_id);
            return (
              <Link key={s.strategy_id} href={`/strategies/${s.strategy_id}`}>
                <Card className="hover:border-primary/40 transition-colors">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-foreground">{s.name}</CardTitle>
                      <Badge variant={statusVariant(s.status)}>{s.status}</Badge>
                    </div>
                    <div className="text-xs text-muted-foreground font-mono">
                      {s.universe.join(", ")} · {s.timeframe}
                    </div>
                  </CardHeader>
                  <CardContent className="text-xs space-y-1 font-mono">
                    <div>
                      <span className="text-muted-foreground">Sharpe:</span>{" "}
                      {latest?.sharpe?.toFixed(2) ?? "—"}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Max DD:</span>{" "}
                      {latest?.max_drawdown != null
                        ? `${(latest.max_drawdown * 100).toFixed(1)}%`
                        : "—"}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Updated:</span>{" "}
                      {formatDate(s.updated_at)}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
          {(strategies ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">{nekoVoice.empty("strategies")}</p>
          ) : null}
        </div>
      </div>
    </main>
  );
}
