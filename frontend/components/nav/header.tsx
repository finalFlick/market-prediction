import { Badge } from "@/components/ui/badge";
import { type Health } from "@/lib/api";

export function Header({ health, title }: { health: Health | null; title: string }) {
  const ok = health?.status === "ok" && health.db_ok;
  return (
    <header className="flex items-center justify-between border-b border-border px-6 py-3">
      <h1 className="text-base font-semibold tracking-tight">{title}</h1>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        {health ? (
          <>
            <Badge variant={ok ? "success" : "danger"}>
              {ok ? "online" : "degraded"}
            </Badge>
            <span className="font-mono">v{health.version}</span>
            <span className="font-mono">env={health.env}</span>
          </>
        ) : (
          <Badge variant="warning">api unreachable</Badge>
        )}
      </div>
    </header>
  );
}
