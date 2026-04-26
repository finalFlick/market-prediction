import { Header } from "@/components/nav/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, safe } from "@/lib/api";
import { formatNumber, formatDate } from "@/lib/utils";

export default async function LearningsPage() {
  const [health, rows] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.scoreboard()),
  ]);

  const levels = ["strategy", "source", "feature", "llm_calibration"] as const;

  return (
    <main>
      <Header health={health} title="Learnings — lever scoreboard" />
      <div className="p-6 space-y-6">
        {!rows || rows.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-sm text-muted-foreground">
              No scoreboard data yet. Run a backtest to populate lever scores.
            </CardContent>
          </Card>
        ) : (
          <>
            {levels.map((lvl) => {
              const lvlRows = rows.filter((r) => r.level === lvl);
              if (lvlRows.length === 0) return null;
              return (
                <section key={lvl}>
                  <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
                    {lvl.replace("_", " ")} lever
                  </h2>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="border-b border-border text-xs text-muted-foreground">
                        <tr>
                          <th className="text-left py-2 pr-4 font-mono">Key</th>
                          <th className="text-right py-2 pr-4">Score</th>
                          <th className="text-right py-2 pr-4">Weight</th>
                          <th className="text-left py-2 pr-4 font-mono">Last run</th>
                          <th className="text-left py-2 pr-4">Updated</th>
                        </tr>
                      </thead>
                      <tbody>
                        {lvlRows.map((r) => (
                          <tr
                            key={`${r.level}-${r.key}`}
                            className="border-b border-border/40 hover:bg-panel/40"
                          >
                            <td className="py-2 pr-4 font-mono text-xs">{r.key}</td>
                            <td className="py-2 pr-4 text-right font-mono text-xs">
                              {formatNumber(r.score)}
                            </td>
                            <td className="py-2 pr-4 text-right font-mono text-xs">
                              {formatNumber(r.weight)}
                            </td>
                            <td className="py-2 pr-4 font-mono text-xs">
                              {r.last_run_id ?? "—"}
                            </td>
                            <td className="py-2 pr-4 font-mono text-xs">
                              {formatDate(r.updated_at)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              );
            })}
          </>
        )}
      </div>
    </main>
  );
}
