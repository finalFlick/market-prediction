import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const cardVariants = cva("rounded-xl border text-card-foreground", {
  variants: {
    variant: {
      default: "border-border bg-card shadow-sm",
      panel: "border-border/80 bg-card/95 shadow-sm",
      metric: "border-primary/25 bg-card shadow-sm",
      risk: "border-danger/45 bg-card shadow-sm",
      alert: "border-warning/40 bg-card shadow-sm",
      glass: "border-border/60 bg-card/75 shadow-sm backdrop-blur-sm",
    },
  },
  defaultVariants: { variant: "default" },
});

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, ...props }, ref) => (
    <div ref={ref} className={cn(cardVariants({ variant }), className)} {...props} />
  ),
);
Card.displayName = "Card";

export const CardHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("flex flex-col gap-1 p-4 border-b border-border", className)} {...props} />
);

export const CardTitle = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("text-sm font-medium text-muted-foreground", className)} {...props} />
);

export const CardValue = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("text-2xl font-semibold tracking-tight font-mono", className)} {...props} />
);

export const CardContent = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("p-4", className)} {...props} />
);
