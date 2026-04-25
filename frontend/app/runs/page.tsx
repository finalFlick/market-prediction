import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function RunsPage() {
  return (
    <div className="p-6 space-y-4 bg-night/30 min-h-screen">
      <h1 className="text-2xl font-mono text-foxfire tracking-tight">KitsuneRunner — Runs</h1>
      <Card className="border-mint/30 bg-panel/80">
        <CardHeader>
          <CardTitle className="font-mono text-mint">Paper + backtest runs</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Read <code className="text-magenta">GET /api/runs</code> from the operator console. Dashboard
          wiring ships in the next polish pass; the API path is live.
        </CardContent>
      </Card>
    </div>
  );
}
