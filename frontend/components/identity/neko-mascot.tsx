import { cn } from "@/lib/utils";

export type NekoMascotState =
  | "analyzing"
  | "excited"
  | "sad"
  | "sleeping"
  | "confused"
  | "triumphant";

/** Inline ASCII — designer stubs; `public/neko/mascot/*.txt` mirrors for export. */
const MASCOT_INLINE: Record<NekoMascotState, string> = {
  analyzing: `  /\\_/\\
 ( o.o )
  > ^ <`,
  excited: `  /\\_/\\
 ( ^o^ )
 /|   |\\`,
  sad: `  /\\_/\\
 ( T T )
  ~~~~~`,
  sleeping: `  /\\_/\\
 ( -.- )
  z z z`,
  confused: `  /\\_/\\
 ( o?o )
  ? ? ?`,
  triumphant: `  /\\_/\\
 ( *^* )✧
  |   |`,
};

const sizeClass: Record<"sm" | "md" | "lg", string> = {
  sm: "text-[10px] leading-tight",
  md: "text-xs leading-tight",
  lg: "text-sm leading-tight",
};

export function NekoMascot({
  state,
  size = "md",
  className,
}: {
  state: NekoMascotState;
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  return (
    <pre
      className={cn(
        "font-mono text-mauve/90 neko-mascot-glow select-none",
        "animate-candle-pulse",
        sizeClass[size],
        className
      )}
      role="img"
      aria-label={`Neko mascot (${state})`}
    >
      {MASCOT_INLINE[state]}
    </pre>
  );
}
