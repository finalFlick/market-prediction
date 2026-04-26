"use client";

import Link from "next/link";

import { getComponent } from "@/styleguide/registry";

export function StyleguideDetailClient({ componentId }: { componentId: string }) {
  const meta = getComponent(componentId);
  if (!meta) return null;

  return (
    <div className="min-h-screen bg-background p-6 text-foreground">
      <div className="mx-auto max-w-5xl space-y-6">
        <div>
          <Link
            className="text-xs font-mono text-muted-foreground hover:text-primary"
            href="/styleguide"
          >
            ← Styleguide index
          </Link>
          <h1 className="mt-3 text-2xl font-semibold tracking-tight">{meta.name}</h1>
          <p className="mt-2 text-sm text-muted-foreground">{meta.description}</p>
          <dl className="mt-4 grid gap-2 text-xs font-mono text-muted-foreground sm:grid-cols-2">
            <div>
              <dt className="text-[10px] uppercase">source</dt>
              <dd className="text-foreground/90">{meta.sourcePath}</dd>
            </div>
            <div>
              <dt className="text-[10px] uppercase">import</dt>
              <dd className="text-foreground/90">{meta.importPath}</dd>
            </div>
            <div>
              <dt className="text-[10px] uppercase">status</dt>
              <dd className="text-foreground/90">{meta.status}</dd>
            </div>
          </dl>
          {meta.accessibility.length ? (
            <div className="mt-4">
              <p className="text-[10px] font-mono uppercase text-muted-foreground">Accessibility</p>
              <ul className="mt-1 list-inside list-disc text-sm text-muted-foreground">
                {meta.accessibility.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {meta.keyboard?.length ? (
            <div className="mt-3">
              <p className="text-[10px] font-mono uppercase text-muted-foreground">Keyboard</p>
              <ul className="mt-1 list-inside list-disc text-sm text-muted-foreground">
                {meta.keyboard.map((k) => (
                  <li key={k}>{k}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>

        <div className="space-y-6">
          {meta.demos.map((d) => (
            <section key={d.id} className="rounded-xl border border-border bg-card/60 shadow-sm">
              <div className="border-b border-border px-4 py-3">
                <h2 className="text-sm font-medium text-foreground">{d.label}</h2>
                <p className="text-[10px] font-mono uppercase text-muted-foreground">
                  {d.state} · {d.id}
                </p>
              </div>
              <div className="p-4">
                <div className="rounded-lg border border-border/60 bg-base/40 p-4">
                  <d.DemoComponent />
                </div>
              </div>
            </section>
          ))}
        </div>

        <p className="pb-8 text-[10px] font-mono text-muted-foreground">
          Run component tests: <code className="text-foreground/90">cd frontend &amp;&amp; npm test</code>
        </p>
      </div>
    </div>
  );
}
