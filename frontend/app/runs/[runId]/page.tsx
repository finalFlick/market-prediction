export default function RunDetailPage({ params }: { params: { runId: string } }) {
  return (
    <div className="p-6 bg-night/30 min-h-screen">
      <h1 className="text-xl font-mono text-lavender">Run {params.runId}</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Detail &amp; audit panels: use <code className="text-mint">GET /api/runs/{params.runId}</code>
      </p>
    </div>
  );
}
