import Link from "next/link";

import { Header } from "@/components/nav/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { api, safe } from "@/lib/api";
import { nekoVoice } from "@/lib/neko-voice";
import { formatDate, formatNumber, formatPct } from "@/lib/utils";

export default async function BacktestLabPage() {
  const [health, backtests] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.backtests({ limit: 200 })),
  ]);

  return (
    <main>
      <Header health={health} title="Backtest Lab" />
      <div className="p-6 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>How to add a run</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-2 font-mono">
            <div>python -m backtests.run --strategy strategies.examples.momentum_xover \</div>
            <div className="pl-4">--config configs/backtest.yaml</div>
            <div className="pt-2 text-xs">
              Each run writes <code>backtests/results/&lt;run_id&gt;/</code> and inserts a row in the{" "}
              <code>backtests</code> table.
            </div>
          </CardContent>
        </Card>

        <Table>
          <THead>
            <tr>
              <TH>Run</TH>
              <TH>Strategy</TH>
              <TH>Started</TH>
              <TH>Sharpe</TH>
              <TH>Sortino</TH>
              <TH>Max DD</TH>
              <TH>CAGR</TH>
              <TH>Trades</TH>
              <TH>Final equity</TH>
            </tr>
          </THead>
          <TBody>
            {(backtests ?? []).map((b) => (
              <TR key={b.run_id}>
                <TD>
                  <Link href={`/backtests/${encodeURIComponent(b.run_id)}`} className="text-primary">
                    {b.run_id.slice(0, 24)}…
                  </Link>
                </TD>
                <TD>{b.strategy_id}</TD>
                <TD>{formatDate(b.started_at)}</TD>
                <TD>{formatNumber(b.sharpe ?? null, 2)}</TD>
                <TD>{formatNumber(b.sortino ?? null, 2)}</TD>
                <TD>{formatPct(b.max_drawdown ?? null, 1)}</TD>
                <TD>{formatPct(b.cagr ?? null, 1)}</TD>
                <TD>{b.n_trades ?? "—"}</TD>
                <TD>{formatNumber(b.final_equity ?? null, 2)}</TD>
              </TR>
            ))}
            {(backtests ?? []).length === 0 ? (
              <tr>
                <TD colSpan={9} className="text-center text-muted-foreground py-6">
                  {nekoVoice.empty("backtests")}
                </TD>
              </tr>
            ) : null}
          </TBody>
        </Table>
      </div>
    </main>
  );
}
