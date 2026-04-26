import { Header } from "@/components/nav/header";
import { Card, CardContent } from "@/components/ui/card";
import { TradesTable } from "@/components/data/trades-table";
import { api, safe } from "@/lib/api";
import { nekoVoice } from "@/lib/neko-voice";

export default async function TradesPage() {
  const [health, trades] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.trades({ limit: 1000 })),
  ]);

  const rows = trades ?? [];
  const empty = rows.length === 0;

  return (
    <main>
      <Header health={health} title="Trade History" />
      <div className="p-6 space-y-4">
        <p className="text-sm text-muted-foreground">
          All fills written to the <code className="font-mono">trades</code> table. Filter by
          venue (backtest / paper / live).
        </p>
        {empty ? (
          <Card>
            <CardContent className="py-8 text-center text-sm text-muted-foreground">
              {nekoVoice.empty("trades")}
            </CardContent>
          </Card>
        ) : (
          <TradesTable data={rows} />
        )}
      </div>
    </main>
  );
}
