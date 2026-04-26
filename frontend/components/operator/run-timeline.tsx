import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type TimelineEvent = {
  id: string;
  at: string;
  state: string;
  note?: string;
  recovered?: boolean;
};

export function RunTimeline({ events, className }: { events: TimelineEvent[]; className?: string }) {
  return (
    <ol className={cn("relative border-l border-border/70 pl-4 space-y-4", className)}>
      {events.map((e) => (
        <li key={e.id} className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-mono text-muted-foreground">{e.at}</span>
            <Badge variant="outline">{e.state}</Badge>
            {e.recovered ? <Badge variant="paper">recovered</Badge> : null}
          </div>
          {e.note ? <p className="text-xs text-foreground/90">{e.note}</p> : null}
        </li>
      ))}
    </ol>
  );
}
