import * as React from "react";

import { cn } from "@/lib/utils";

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: string;
  children?: React.ReactNode;
}

export function EmptyState({ title, description, className, children, ...props }: EmptyStateProps) {
  return (
    <div
      role="status"
      className={cn(
        "rounded-lg border border-dashed border-border/80 bg-surface0/30 p-6 text-center",
        className,
      )}
      {...props}
    >
      <p className="text-sm font-semibold text-foreground">{title}</p>
      {description ? (
        <p className="mt-2 text-xs text-muted-foreground font-mono leading-snug">{description}</p>
      ) : null}
      {children ? <div className="mt-4 flex justify-center gap-2">{children}</div> : null}
    </div>
  );
}
