import Link from "next/link";
import {
  Activity,
  AreaChart,
  Beaker,
  GanttChart,
  Heart,
  LayoutDashboard,
  LineChart,
  ListChecks,
} from "lucide-react";

const items = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/trades", label: "Trades", icon: ListChecks },
  { href: "/strategies", label: "Strategies", icon: GanttChart },
  { href: "/signals", label: "Signals", icon: AreaChart },
  { href: "/diagnostics", label: "Model Diagnostics", icon: Activity },
  { href: "/backtests", label: "Backtest Lab", icon: Beaker },
  { href: "/health", label: "System Health", icon: Heart },
];

export function Sidebar() {
  return (
    <aside className="w-56 shrink-0 border-r border-border bg-card/40 p-4">
      <div className="flex items-center gap-2 px-2 pb-4 text-sm font-semibold tracking-wide">
        <LineChart className="h-5 w-5 text-primary" />
        <span className="font-mono">trading-lab</span>
      </div>
      <nav className="flex flex-col gap-0.5">
        {items.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
