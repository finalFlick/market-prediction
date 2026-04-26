import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(value: number | null | undefined, digits = 2): string {
  if (value == null || Number.isNaN(value)) return "—";
  return value.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function formatPct(value: number | null | undefined, digits = 2): string {
  if (value == null || Number.isNaN(value)) return "—";
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatDate(value: string | Date | null | undefined): string {
  if (!value) return "—";
  const d = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(d.getTime())) return "—";
  return d.toISOString().replace("T", " ").slice(0, 19) + "Z";
}

/** Compact “paw meter” for playful research UI (not operator alerts). */
export function formatPawConfidence(value: number): string {
  const v = Math.max(0, Math.min(1, value));
  const steps = 5;
  const n = Math.min(steps, Math.max(0, Math.round(v * steps)));
  const pct = Math.round(v * 100);
  return `${"🐾".repeat(n)}${n < steps ? "░" : ""} ${pct}%`;
}
