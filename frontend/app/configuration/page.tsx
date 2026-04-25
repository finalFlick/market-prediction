export default function ConfigurationIndexPage() {
  return (
    <div className="p-6 bg-night/30 min-h-screen">
      <h1 className="text-xl font-mono text-lavender">Configuration (read-only, MVP-0)</h1>
      <ul className="mt-4 space-y-2 text-sm">
        <li>
          <a className="text-mint hover:underline" href="/configuration/risk">
            Risk
          </a>
        </li>
        <li>
          <a className="text-mint hover:underline" href="/configuration/costs">
            Costs
          </a>
        </li>
        <li>
          <a className="text-mint hover:underline" href="/configuration/runtime">
            Runtime
          </a>
        </li>
      </ul>
      <p className="mt-6 text-xs text-muted-foreground">
        Edits require PR + reseed in MVP-0; v1 adds approval-gated writes.
      </p>
    </div>
  );
}
