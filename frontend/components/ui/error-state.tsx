import * as React from "react";

import { cn } from "@/lib/utils";

export interface ErrorStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: string;
  children?: React.ReactNode;
}

export function ErrorState({ title, description, className, children, ...props }: ErrorStateProps) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-lg border border-danger/50 bg-danger/10 p-6 text-center shadow-sm",
        className,
      )}
      {...props}
    >
      <p className="text-sm font-semibold text-danger">{title}</p>
      {description ? (
        <p className="mt-2 text-xs text-danger/90 font-mono leading-snug">{description}</p>
      ) : null}
      {children ? <div className="mt-4 flex justify-center gap-2">{children}</div> : null}
    </div>
  );
}
