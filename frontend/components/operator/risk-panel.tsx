import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RiskLimitMeter } from "@/components/data/risk-limit-meter";
import { cn } from "@/lib/utils";

export interface RiskPanelProps {
  killSwitchArmed: boolean;
  limits: { label: string; current: number; limit: number }[];
  rejects: string[];
  className?: string;
}

export function RiskPanel({ killSwitchArmed, limits, rejects, className }: RiskPanelProps) {
  return (
    <Card variant="risk" className={cn(className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Risk console</CardTitle>
          <Badge variant={killSwitchArmed ? "danger" : "success"}>
            kill-switch {killSwitchArmed ? "armed" : "clear"}
          </Badge>
        </div>
        <p className="text-[11px] text-muted-foreground font-mono leading-snug">
          Read-only telemetry. Orders route only through the risk engine; this panel never places
          trades.
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        {limits.map((l) => (
          <RiskLimitMeter key={l.label} label={l.label} current={l.current} limit={l.limit} />
        ))}
        {rejects.length ? (
          <div className="rounded-md border border-danger/40 bg-danger/5 p-3">
            <p className="text-xs font-semibold text-danger">Active rejects</p>
            <ul className="mt-2 space-y-1 text-[11px] font-mono text-danger/90">
              {rejects.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
