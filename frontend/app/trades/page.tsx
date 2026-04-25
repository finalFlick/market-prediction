import { Header } from "@/components/nav/header";
import { TradesTable } from "@/components/data/trades-table";
import { api, safe } from "@/lib/api";

export default async function TradesPage() {
  const [health, trades] = await Promise.all([
    safe(() => api.health()),
    safe(() => api.trades({ limit: 1000 })),
  ]);

  return (
    <main>
      <Header health={health} title="Trade History" />
      <div className="p-6 space-y-4">
        <p className="text-sm text-muted-foreground">
          All fills written to the <code className="font-mono">trades</code> table. Filter by
          venue (backtest / paper / live).
        </p>
        <TradesTable data={trades ?? []} />
      </div>
    </main>
  );
}
