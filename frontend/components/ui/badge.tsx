import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium border",
  {
    variants: {
      variant: {
        default: "bg-muted text-foreground border-border",
        success: "bg-success/15 text-success border-success/30",
        warning: "bg-warning/15 text-warning border-warning/30",
        danger: "bg-danger/15 text-danger border-danger/30",
        primary: "bg-primary/15 text-primary border-primary/30",
        outline: "border-border text-muted-foreground",
        live: "bg-success/20 text-success border-success/40",
        paper: "bg-warning/15 text-warning border-warning/35",
        retired: "bg-muted text-muted-foreground border-border/80",
        degraded: "bg-mauve/15 text-mauve border-mauve/30",
        magenta: "bg-mauve/15 text-mauve border-mauve/30",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
