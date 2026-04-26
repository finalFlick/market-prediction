import { CatEarIcon } from "@/components/identity/neko-icons";

export default function LoginPage() {
  return (
    <div className="p-6 max-w-md mx-auto bg-panel/90 border border-mint/20 rounded-lg mt-12">
      <div className="flex items-center gap-2 text-mauve" aria-hidden>
        <CatEarIcon className="h-5 w-5" />
        <h1 className="text-lg font-mono text-foxfire">Neko awaits authentication</h1>
      </div>
      <p className="text-sm text-subtext0 mt-2">Operator login — paws off the keys until verified.</p>
      <p className="text-sm text-muted-foreground mt-2">
        NextAuth credentials + <code className="text-lavender">NEXTAUTH_SECRET</code> — wire on
        deploy.
      </p>
    </div>
  );
}
