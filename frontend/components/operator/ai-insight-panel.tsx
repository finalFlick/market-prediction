import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { NEKO_NOT_A_TRADE_SIGNAL } from "@/lib/neko-voice";
import { cn } from "@/lib/utils";

export function AiInsightPanel({
  summary,
  cites,
  className,
}: {
  summary: string;
  cites: string[];
  className?: string;
}) {
  return (
    <Card variant="glass" className={cn(className)}>
      <CardHeader className="space-y-1">
        <CardTitle>AI insight</CardTitle>
        <p className="text-[11px] font-medium text-mauve/90" role="note">
          {NEKO_NOT_A_TRADE_SIGNAL}
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm leading-snug text-foreground/90">{summary}</p>
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Citations</p>
          <ul className="mt-2 space-y-1 text-xs font-mono text-lavender/90">
            {cites.map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
