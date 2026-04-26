import { NEKO_NOT_A_TRADE_SIGNAL } from "@/lib/neko-voice";
import { cn } from "@/lib/utils";

type Props = {
  title: string;
  /** Enforced at compile time — research observation, not a trade call. */
  notATradeSignal: true;
  children: React.ReactNode;
  className?: string;
};

export function NekoObservationCard({ title, notATradeSignal: _assert, children, className }: Props) {
  void _assert;
  return (
    <div
      className={cn(
        "rounded-lg border border-mauve/50 bg-surface0/70 p-4 shadow-sm",
        "ring-1 ring-mauve/20",
        className
      )}
    >
      <h3 className="text-xs font-semibold uppercase tracking-wide text-mauve">{title}</h3>
      <p className="mt-1 text-[11px] font-medium text-mauve/90" role="note">
        {NEKO_NOT_A_TRADE_SIGNAL}
      </p>
      <div className="mt-3 text-sm text-foreground/90">{children}</div>
    </div>
  );
}
