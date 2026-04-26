import * as React from "react";

import { cn } from "@/lib/utils";

const iconClass = "inline-block h-4 w-4 shrink-0 text-current";

export function PawIcon({ className, ...p }: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="none"
      className={cn(iconClass, className)}
      aria-hidden
      {...p}
    >
      <ellipse cx="8" cy="9.5" rx="4" ry="3.5" fill="currentColor" opacity={0.9} />
      <circle cx="4.5" cy="5" r="1.6" fill="currentColor" />
      <circle cx="8" cy="3.5" r="1.6" fill="currentColor" />
      <circle cx="11.5" cy="5" r="1.6" fill="currentColor" />
    </svg>
  );
}

export function CatEarIcon({ className, ...p }: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="currentColor"
      className={cn(iconClass, className)}
      aria-hidden
      {...p}
    >
      <path d="M2 10 L4 2 L7 6 Z M9 6 L12 2 L14 10 Z" />
    </svg>
  );
}

export function NinjaCatIcon({ className, ...p }: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={cn(iconClass, className)}
      aria-hidden
      {...p}
    >
      <path
        d="M2 10 C1 7 2 4 5 3 C8 2 11 3 13 6 C14 8 13 11 10 12 C7 13 3 12 2 10Z"
        fill="currentColor"
        opacity={0.95}
      />
      <rect x="4" y="6" width="7" height="1.4" rx="0.3" fill="currentColor" opacity={0.35} />
    </svg>
  );
}

export function CoinCollarIcon({ className, ...p }: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={cn(iconClass, className)}
      aria-hidden
      {...p}
    >
      <circle cx="5" cy="4" r="1.2" fill="currentColor" />
      <circle cx="5" cy="6.5" r="1.2" fill="currentColor" />
      <circle cx="5" cy="9" r="1.2" fill="currentColor" />
      <rect x="7" y="3" width="8" height="7" rx="1" fill="currentColor" opacity={0.85} />
    </svg>
  );
}

export function ShieldPawIcon({ className, ...p }: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={cn(iconClass, className)}
      aria-hidden
      {...p}
    >
      <path
        d="M8 1 L2 3.5 v5 c0 3 2.5 5.5 6 6.5 3.5-1 6-3.5 6-6.5v-5 L8 1Z"
        fill="currentColor"
        opacity={0.9}
      />
      <circle cx="8" cy="8.5" r="1.2" fill="currentColor" opacity={0.35} />
    </svg>
  );
}

export function TimeLoopTailIcon({ className, ...p }: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="none"
      className={cn(iconClass, className)}
      aria-hidden
      {...p}
    >
      <path
        d="M10 1 C4 1 1 4 1 7 C1 10 2.5 12.5 5.5 13.5 C7 14 6 9 3 9"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
      <path
        d="M1 5 A6 4 0 0 0 3 1"
        stroke="currentColor"
        strokeWidth="0.6"
        strokeLinecap="round"
        opacity={0.6}
      />
    </svg>
  );
}
