import { cn } from "@/lib/utils";

export interface RiskLimitMeterProps {
  label: string;
  current: number;
  limit: number;
  unit?: string;
  rejectReason?: string;
  className?: string;
}

export function RiskLimitMeter({
  label,
  current,
  limit,
  unit = "",
  rejectReason,
  className,
}: RiskLimitMeterProps) {
  const pct = limit <= 0 ? 0 : Math.min(100, (current / limit) * 100);
  const danger = pct >= 90;
  return (
    <div className={cn("space-y-2 rounded-lg border border-border/70 bg-surface0/40 p-3", className)}>
      <div className="flex items-center justify-between text-xs font-mono text-muted-foreground">
        <span>{label}</span>
        <span className={danger ? "text-danger" : "text-foreground"}>
          {current.toFixed(2)}
          {unit} / {limit.toFixed(2)}
          {unit}
        </span>
      </div>
      <div className="h-2 w-full rounded bg-muted/60">
        <div
          className={cn(
            "h-2 rounded bg-success transition-all",
            danger && "bg-danger",
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      {rejectReason ? (
        <p className="text-[11px] text-danger font-mono leading-snug">{rejectReason}</p>
      ) : null}
    </div>
  );
}
