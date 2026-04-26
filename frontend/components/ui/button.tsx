"use client";

import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-md border font-medium text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary:
          "border-primary/40 bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm",
        ghost: "border-transparent bg-transparent text-foreground hover:bg-muted/60",
        danger: "border-danger/40 bg-danger/15 text-danger hover:bg-danger/25",
        command:
          "border-border/80 bg-card/90 text-foreground hover:bg-muted/50 font-mono tracking-tight",
      },
      size: {
        sm: "h-8 px-3 text-xs",
        md: "h-9 px-4",
      },
      loading: {
        true: "cursor-wait",
        false: "",
      },
    },
    defaultVariants: { variant: "primary", size: "md", loading: false },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, disabled, children, ...props }, ref) => (
    <button
      ref={ref}
      type="button"
      className={cn(buttonVariants({ variant, size, loading: Boolean(loading) }), className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="animate-paw-bounce font-mono text-xs" aria-hidden>
            …
          </span>
          <span className="opacity-70">{children}</span>
        </>
      ) : (
        children
      )}
    </button>
  ),
);
Button.displayName = "Button";
