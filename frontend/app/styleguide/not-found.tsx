import Link from "next/link";

export default function StyleguideNotFound() {
  return (
    <div className="p-6">
      <p className="text-muted-foreground">No styleguide entry for this id.</p>
      <Link className="mt-3 inline-block text-sm text-primary hover:underline" href="/styleguide">
        Back to styleguide
      </Link>
    </div>
  );
}
