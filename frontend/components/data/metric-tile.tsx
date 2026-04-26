import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export interface MetricTileProps {
  label: string;
  value: string;
  unit?: string;
  delta?: number;
  stale?: boolean;
  sourceTs?: string;
  className?: string;
}

export function MetricTile({
  label,
  value,
  unit,
  delta,
  stale,
  sourceTs,
  className,
}: MetricTileProps) {
  const deltaTone =
    delta == null ? "text-muted-foreground" : delta >= 0 ? "text-success" : "text-danger";
  return (
    <div
      className={cn(
        "rounded-lg border border-border/70 bg-mantle/60 p-4 shadow-sm",
        stale && "border-warning/40 opacity-90",
        className,
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
        {stale ? <Badge variant="degraded">stale</Badge> : null}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-semibold font-mono text-foreground">{value}</span>
        {unit ? <span className="text-xs text-muted-foreground">{unit}</span> : null}
      </div>
      {delta != null ? (
        <p className={cn("mt-1 text-xs font-mono", deltaTone)}>
          Δ {delta >= 0 ? "+" : ""}
          {delta.toFixed(2)}
        </p>
      ) : null}
      {sourceTs ? <p className="mt-2 text-[10px] text-muted-foreground font-mono">{sourceTs}</p> : null}
    </div>
  );
}
