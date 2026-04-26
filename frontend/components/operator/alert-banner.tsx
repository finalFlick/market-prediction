import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type AlertSeverity = "info" | "warning" | "critical";

const tone: Record<AlertSeverity, string> = {
  info: "border-success/40 bg-success/5 text-success",
  warning: "border-warning/50 bg-warning/10 text-warning",
  critical: "border-danger/55 bg-danger/15 text-danger shadow-sm",
};

export function AlertBanner({
  severity,
  title,
  body,
  auditHref,
  className,
}: {
  severity: AlertSeverity;
  title: string;
  body: string;
  auditHref?: string;
  className?: string;
}) {
  return (
    <div
      role="status"
      className={cn(
        "rounded-lg border px-4 py-3 flex flex-col gap-2 backdrop-blur-sm",
        tone[severity],
        className,
      )}
    >
      <div className="flex items-center gap-2">
        <Badge
          variant={
            severity === "critical" ? "danger" : severity === "warning" ? "warning" : "primary"
          }
        >
          {severity}
        </Badge>
        <p className="text-sm font-semibold">{title}</p>
      </div>
      <p className="text-xs font-mono leading-snug opacity-90">{body}</p>
      {auditHref ? (
        <a className="text-xs underline text-foreground/80" href={auditHref}>
          View audit entry
        </a>
      ) : null}
    </div>
  );
}
