export default function LoginPage() {
  return (
    <div className="p-6 max-w-md mx-auto bg-panel/90 border border-mint/20 rounded-lg mt-12">
      <h1 className="text-lg font-mono text-foxfire">Operator login</h1>
      <p className="text-sm text-muted-foreground mt-2">
        NextAuth credentials + <code className="text-lavender">NEXTAUTH_SECRET</code> — wire on
        deploy.
      </p>
    </div>
  );
}
