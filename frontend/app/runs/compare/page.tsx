export default function RunsComparePage() {
  return (
    <div className="p-6 bg-night/30 min-h-screen">
      <h1 className="text-xl font-mono text-foxfire">Compare runs</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Side-by-side metrics: pass <code className="text-mint">?ids=</code> query params (API assist
        pending).
      </p>
    </div>
  );
}
