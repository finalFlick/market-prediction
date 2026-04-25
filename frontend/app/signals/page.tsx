import { Header } from "@/components/nav/header";
import { Badge } from "@/components/ui/badge";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { api, safe } from "@/lib/api";
import { formatDate } from "@/lib/utils";

const variantFor = (status: string) =>
  ({
    hypothesis: "outline",
    research: "default",
    backtest: "warning",
    paper: "warning",
    live: "primary",
    retired: "danger",
  }[status] ?? "default") as "outline" | "default" | "warning" | "primary" | "danger";

export default async function SignalsPage() {
  const [health, signals] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.signals()),
  ]);

  return (
    <main>
      <Header health={health} title="Signal Explorer" />
      <div className="p-6 space-y-4">
        <p className="text-sm text-muted-foreground">
          Hypothesis backlog and lifecycle status. Source of truth is{" "}
          <code className="font-mono">SIGNALS.md</code>; this view reads the{" "}
          <code className="font-mono">signals</code> DuckDB table.
        </p>
        <Table>
          <THead>
            <tr>
              <TH>ID</TH>
              <TH>Name</TH>
              <TH>Status</TH>
              <TH>Timeframe</TH>
              <TH>Owner</TH>
              <TH>Updated</TH>
              <TH>Intuition</TH>
            </tr>
          </THead>
          <TBody>
            {(signals ?? []).map((s) => (
              <TR key={s.signal_id}>
                <TD>{s.signal_id}</TD>
                <TD>{s.name}</TD>
                <TD>
                  <Badge variant={variantFor(s.status)}>{s.status}</Badge>
                </TD>
                <TD>{s.timeframe}</TD>
                <TD>{s.owner ?? "—"}</TD>
                <TD>{formatDate(s.updated_at)}</TD>
                <TD className="whitespace-normal max-w-md text-xs text-muted-foreground">
                  {s.intuition ?? ""}
                </TD>
              </TR>
            ))}
            {(signals ?? []).length === 0 ? (
              <tr>
                <TD colSpan={7} className="text-center text-muted-foreground py-6">
                  No signals registered yet.
                </TD>
              </tr>
            ) : null}
          </TBody>
        </Table>
      </div>
    </main>
  );
}
