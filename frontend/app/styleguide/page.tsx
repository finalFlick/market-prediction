import Link from "next/link";

import { componentsByCategory, productionComponentCount } from "@/styleguide/registry";
import type { ComponentCategory } from "@/styleguide/types";

const categoryLabel: Record<ComponentCategory, string> = {
  primitives: "Primitives",
  data: "Data",
  charts: "Charts",
  operator: "Operator",
  navigation: "Navigation",
};

export default function StyleguidePage() {
  const byCat = componentsByCategory();

  return (
    <div className="min-h-screen bg-background p-6 text-foreground">
      <div className="mx-auto max-w-5xl space-y-6">
        <header className="space-y-2 border-b border-border pb-6">
          <p className="text-xs font-mono uppercase tracking-wide text-muted-foreground">
            FEATURE-0034 · Neko Quant
          </p>
          <h1 className="text-2xl font-semibold tracking-tight">Component styleguide</h1>
          <p className="text-sm text-muted-foreground">
            Catppuccin Mocha operator console (DEC-010). Demoable registry:{" "}
            <span className="font-mono text-foreground">{productionComponentCount}</span> production
            components.
          </p>
        </header>

        {(Object.keys(byCat) as ComponentCategory[]).map((cat) => (
          <section key={cat} className="space-y-3">
            <h2 className="text-sm font-semibold text-primary">{categoryLabel[cat]}</h2>
            <ul className="grid gap-2 sm:grid-cols-2">
              {byCat[cat].map((c) => (
                <li key={c.id}>
                  <Link
                    href={`/styleguide/${c.id}`}
                    className="block rounded-lg border border-border bg-card/80 px-4 py-3 shadow-sm transition hover:border-primary/40 hover:bg-card"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium">{c.name}</span>
                      <span className="rounded border border-border px-1.5 py-0.5 text-[10px] font-mono uppercase text-muted-foreground">
                        {c.status}
                      </span>
                    </div>
                    <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">{c.description}</p>
                    <p className="mt-2 font-mono text-[10px] text-muted-foreground/80">{c.sourcePath}</p>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
