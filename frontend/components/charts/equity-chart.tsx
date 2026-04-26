"use client";

import { createChart, type IChartApi, type ISeriesApi, type LineData } from "lightweight-charts";
import { useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

export type EquityPoint = { time: string; value: number };

/** Catppuccin Mocha `green` — see `frontend/tailwind.config.ts`. */
const EQUITY_LINE = "rgb(166 230 161)";

export function EquityChart({ data }: { data: EquityPoint[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    if (!data.length) {
      return;
    }
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 320,
      layout: {
        background: { color: "transparent" },
        textColor: "rgb(186 194 222)",
      },
      grid: {
        horzLines: { color: "rgba(255,255,255,0.05)" },
        vertLines: { color: "rgba(255,255,255,0.05)" },
      },
      timeScale: { borderColor: "rgba(255,255,255,0.1)" },
      rightPriceScale: { borderColor: "rgba(255,255,255,0.1)" },
    });
    const series: ISeriesApi<"Area"> = chart.addAreaSeries({
      lineColor: EQUITY_LINE,
      topColor: "rgba(166, 230, 161, 0.35)",
      bottomColor: "rgba(166, 230, 161, 0.0)",
      lineWidth: 2,
    });
    series.setData(data as unknown as LineData[]);
    chart.timeScale().fitContent();
    chartRef.current = chart;

    const onResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
    };
  }, [data]);

  if (!data.length) {
    return (
      <div
        className={cn(
          "flex h-[320px] w-full items-center justify-center rounded-md border border-dashed border-border/60 bg-surface0/25 text-xs text-muted-foreground font-mono",
        )}
      >
        No equity series
      </div>
    );
  }

  return <div ref={containerRef} className="w-full" />;
}
