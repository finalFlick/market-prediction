import * as React from "react";

import { cn } from "@/lib/utils";

export const Table = ({ className, ...props }: React.HTMLAttributes<HTMLTableElement>) => (
  <div className="w-full overflow-auto">
    <table className={cn("w-full text-sm", className)} {...props} />
  </div>
);

export const THead = (props: React.HTMLAttributes<HTMLTableSectionElement>) => (
  <thead
    className="text-xs uppercase tracking-wide text-muted-foreground border-b border-border"
    {...props}
  />
);

export const TBody = (props: React.HTMLAttributes<HTMLTableSectionElement>) => (
  <tbody className="divide-y divide-border" {...props} />
);

export const TR = ({ className, ...props }: React.HTMLAttributes<HTMLTableRowElement>) => (
  <tr className={cn("hover:bg-muted/40", className)} {...props} />
);

export const TH = ({ className, ...props }: React.ThHTMLAttributes<HTMLTableCellElement>) => (
  <th className={cn("text-left px-3 py-2 font-medium", className)} {...props} />
);

export const TD = ({ className, ...props }: React.TdHTMLAttributes<HTMLTableCellElement>) => (
  <td className={cn("px-3 py-2 font-mono whitespace-nowrap", className)} {...props} />
);
