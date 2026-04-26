import Link from "next/link";
import { Header } from "@/components/nav/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, safe } from "@/lib/api";
import { formatDate } from "@/lib/utils";

const STATUS_VARIANT: Record<string, "success" | "danger" | "warning" | "default"> = {
  succeeded: "success",
  failed: "danger",
  running: "warning",
  queued: "default",
  paused: "warning",
};

export default async function RunsPage() {
  const [health, runs] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.runs({ limit: 200 })),
  ]);

  return (
    <main>
      <Header health={health} title="Runs" />
      <div className="p-6 space-y-4">
        {!runs || runs.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-sm text-muted-foreground">
              No runs yet. Submit a run via CLI:{" "}
              <code className="text-mint">python -m runs.submit</code> or the worker.
            </CardContent>
          </Card>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-border text-xs text-muted-foreground">
                <tr>
                  <th className="text-left py-2 pr-4 font-mono">Run ID</th>
                  <th className="text-left py-2 pr-4">Type</th>
                  <th className="text-left py-2 pr-4">Mode</th>
                  <th className="text-left py-2 pr-4">Status</th>
                  <th className="text-left py-2 pr-4">Started</th>
                  <th className="text-left py-2 pr-4">Finished</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr key={r.run_id} className="border-b border-border/40 hover:bg-panel/40">
                    <td className="py-2 pr-4 font-mono text-xs">
                      <Link
                        href={`/runs/${r.run_id}`}
                        className="text-mint hover:underline"
                      >
                        {r.run_id.length > 28 ? r.run_id.slice(0, 26) + "…" : r.run_id}
                      </Link>
                    </td>
                    <td className="py-2 pr-4 font-mono text-xs">{r.run_type}</td>
                    <td className="py-2 pr-4 font-mono text-xs">{r.mode}</td>
                    <td className="py-2 pr-4">
                      <Badge variant={STATUS_VARIANT[r.status] ?? "default"}>
                        {r.status}
                      </Badge>
                    </td>
                    <td className="py-2 pr-4 font-mono text-xs">{formatDate(r.started_at)}</td>
                    <td className="py-2 pr-4 font-mono text-xs">{formatDate(r.finished_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
