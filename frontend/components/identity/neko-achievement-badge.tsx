import { cn } from "@/lib/utils";

import { CoinCollarIcon, PawIcon, ShieldPawIcon, TimeLoopTailIcon } from "./neko-icons";

const ICONS = {
  paw: PawIcon,
  fish: CoinCollarIcon,
  brain: ShieldPawIcon,
  chart: TimeLoopTailIcon,
} as const;

export type NekoAchievementKind = keyof typeof ICONS;

/** Display-only badge. Award rules ship in FEATURE-0049. */
export function NekoAchievementBadge({
  label,
  kind = "paw",
  className,
}: {
  label: string;
  kind?: NekoAchievementKind;
  className?: string;
}) {
  const Icon = ICONS[kind];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border border-border bg-mantle/80 px-2 py-0.5",
        "text-[11px] font-mono text-foreground/90",
        className
      )}
    >
      <Icon className="h-3.5 w-3.5 text-mauve" />
      {label}
    </span>
  );
}
