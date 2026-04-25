export default function StyleguidePage() {
  return (
    <div className="p-6 space-y-6 bg-night min-h-screen font-mono">
      <h1 className="text-2xl text-foxfire">Operator styleguide</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded border border-mint/40 bg-panel p-4 text-mint">mint accent</div>
        <div className="rounded border border-magenta/40 bg-panel p-4 text-magenta">magenta accent</div>
        <div className="rounded border border-lavender/40 bg-panel p-4 text-lavender">lavender accent</div>
        <div className="rounded border border-foxfire/40 bg-panel p-4 text-foxfire">foxfire accent</div>
      </div>
    </div>
  );
}
