import { Header } from "@/components/nav/header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardValue } from "@/components/ui/card";
import { api, safe } from "@/lib/api";

export default async function HealthPage() {
  const [health, metrics] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.metrics()),
  ]);

  const m = metrics?.metrics ?? {};
  const equity = m["equity"];
  const gross = m["gross_exposure"];
  const net = m["net_exposure"];
  const orders = m["risk.orders_emitted"];
  const rejects = Object.entries(m)
    .filter(([k]) => k.startsWith("risk.reject"))
    .reduce((sum, [, v]) => sum + Number(v), 0);

  return (
    <main>
      <Header health={health} title="System Health" />
      <div className="p-6 space-y-6">
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>API</CardTitle>
              <CardValue>
                <Badge variant={health?.status === "ok" ? "success" : "danger"}>
                  {health?.status ?? "unknown"}
                </Badge>
              </CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>DuckDB</CardTitle>
              <CardValue>
                <Badge variant={health?.db_ok ? "success" : "danger"}>
                  {health?.db_ok ? "ok" : "fail"}
                </Badge>
              </CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Redis</CardTitle>
              <CardValue>
                <Badge variant={health?.redis_ok ? "success" : "warning"}>
                  {health?.redis_ok ? "ok" : "missing"}
                </Badge>
              </CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Uptime (s)</CardTitle>
              <CardValue>{Math.round(health?.uptime_s ?? 0)}</CardValue>
            </CardHeader>
          </Card>
        </section>

        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Equity</CardTitle>
              <CardValue>{equity != null ? equity.toFixed(2) : "—"}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Gross exposure</CardTitle>
              <CardValue>{gross != null ? gross.toFixed(2) : "—"}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Net exposure</CardTitle>
              <CardValue>{net != null ? net.toFixed(2) : "—"}</CardValue>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Risk rejects</CardTitle>
              <CardValue>{rejects}</CardValue>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground">
              orders emitted: {orders ?? 0}
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}
