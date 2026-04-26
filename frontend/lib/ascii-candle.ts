/**
 * Pure ASCII “candlestick” preview for logs / dev tools. Not a chart engine.
 */

export type Ohlc = { o: number; h: number; l: number; c: number };

const BAR = "█";
const WICK = "│";

/**
 * Renders a compact vertical strip of characters per bar (hi–lo range scaled).
 * Best for 5–20 rows of terminal height.
 */
export function formatAsciiCandles(
  rows: number,
  ohlc: Ohlc[],
  options?: { widthPerBar?: number }
): string {
  if (ohlc.length === 0) return "(no bars)";
  if (rows < 1) return "(no rows)";
  const w = options?.widthPerBar ?? 1;
  const highs = ohlc.map((b) => b.h);
  const lows = ohlc.map((b) => b.l);
  const minL = Math.min(...lows);
  const maxH = Math.max(...highs);
  const span = Math.max(maxH - minL, 1e-9);
  const n = ohlc.length;
  const lines: string[] = [];
  const denom = rows > 1 ? rows - 1 : 1;
  for (let r = rows - 1; r >= 0; r--) {
    const level = minL + (r / denom) * span;
    let row = "";
    for (let i = 0; i < n; i++) {
      const b = ohlc[i]!;
      const inBody = level <= Math.max(b.o, b.c) && level >= Math.min(b.o, b.c);
      const inWick = level <= b.h && level >= b.l;
      const ch = inBody ? BAR.repeat(w) : inWick ? WICK.repeat(w) : " ".repeat(w);
      row += ch + (i < n - 1 ? " " : "");
    }
    lines.push(row);
  }
  return lines.join("\n");
}
