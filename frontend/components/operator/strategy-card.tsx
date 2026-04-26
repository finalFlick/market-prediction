import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardValue } from "@/components/ui/card";
import { RunStatusPill, type RunStatus } from "@/components/data/run-status-pill";
import { cn } from "@/lib/utils";

export interface StrategyCardProps {
  name: string;
  mode: "paper" | "live" | "retired";
  status: RunStatus;
  sharpe?: number;
  gate: "open" | "blocked";
  className?: string;
}

export function StrategyCard({ name, mode, status, sharpe, gate, className }: StrategyCardProps) {
  const modeVariant = mode === "live" ? "live" : mode === "paper" ? "paper" : "retired";
  return (
    <Card variant="panel" className={cn(className)}>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle>{name}</CardTitle>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Badge variant={modeVariant}>{mode}</Badge>
            <RunStatusPill status={status} />
            <Badge variant={gate === "open" ? "success" : "danger"}>
              promotion: {gate}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground">Latest OOS Sharpe</p>
        <CardValue>{sharpe == null ? "—" : sharpe.toFixed(2)}</CardValue>
      </CardContent>
    </Card>
  );
}
