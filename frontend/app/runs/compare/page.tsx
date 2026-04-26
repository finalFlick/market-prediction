import Link from "next/link";
import { Header } from "@/components/nav/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, safe } from "@/lib/api";
import { formatDate, formatNumber, formatPct } from "@/lib/utils";

export default async function RunsComparePage({
  searchParams,
}: {
  searchParams: Promise<{ ids?: string }>;
}) {
  const { ids: idsParam } = await searchParams;
  const ids = (idsParam ?? "").split(",").filter(Boolean);

  const [health, rows] = await Promise.all([
    safe(() => api.health()),
    ids.length > 0 ? safe(() => api.compareRuns(ids)) : Promise.resolve([]),
  ]);

  return (
    <main>
      <Header health={health} title="Compare runs" />
      <div className="p-6 space-y-4">
        {ids.length === 0 && (
          <Card>
            <CardContent className="py-8 text-center text-sm text-muted-foreground">
              Pass run IDs as query params, e.g.{" "}
              <code className="text-mint">/runs/compare?ids=run-a,run-b</code>
            </CardContent>
          </Card>
        )}

        {rows && rows.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-border text-xs text-muted-foreground">
                <tr>
                  <th className="text-left py-2 pr-4 font-mono">Run ID</th>
                  <th className="text-left py-2 pr-4">Status</th>
                  <th className="text-left py-2 pr-4">Type</th>
                  <th className="text-right py-2 pr-4">Sharpe</th>
                  <th className="text-right py-2 pr-4">Max DD</th>
                  <th className="text-right py-2 pr-4">CAGR</th>
                  <th className="text-right py-2 pr-4">Trades</th>
                  <th className="text-left py-2 pr-4">Finished</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.run_id} className="border-b border-border/40 hover:bg-panel/40">
                    <td className="py-2 pr-4 font-mono text-xs">
                      <Link href={`/runs/${r.run_id}`} className="text-mint hover:underline">
                        {r.run_id.length > 24 ? r.run_id.slice(0, 22) + "…" : r.run_id}
                      </Link>
                    </td>
                    <td className="py-2 pr-4 font-mono text-xs">{r.status}</td>
                    <td className="py-2 pr-4 font-mono text-xs">{r.run_type}</td>
                    <td className="py-2 pr-4 text-right font-mono text-xs">
                      {formatNumber(r.sharpe)}
                    </td>
                    <td className="py-2 pr-4 text-right font-mono text-xs">
                      {formatPct(r.max_drawdown)}
                    </td>
                    <td className="py-2 pr-4 text-right font-mono text-xs">
                      {formatPct(r.cagr)}
                    </td>
                    <td className="py-2 pr-4 text-right font-mono text-xs">
                      {r.n_trades ?? "—"}
                    </td>
                    <td className="py-2 pr-4 font-mono text-xs">{formatDate(r.finished_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="text-xs text-muted-foreground">
          <Link href="/runs" className="text-mint hover:underline">
            ← Back to runs
          </Link>
        </div>
      </div>
    </main>
  );
}
