"use client";

import { createChart, type HistogramData } from "lightweight-charts";
import { useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

export function PnLDistributionChart({
  buckets,
  className,
}: {
  buckets: HistogramData[];
  className?: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !buckets.length) return;
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 240,
      layout: { background: { color: "transparent" }, textColor: "rgb(186 194 222)" },
      grid: {
        horzLines: { color: "rgba(255,255,255,0.05)" },
        vertLines: { color: "rgba(255,255,255,0.05)" },
      },
      rightPriceScale: { borderColor: "rgba(255,255,255,0.1)" },
      timeScale: { borderColor: "rgba(255,255,255,0.1)" },
    });
    const series = chart.addHistogramSeries({
      color: "rgba(203, 166, 247, 0.7)",
    });
    series.setData(buckets);
    chart.timeScale().fitContent();

    const onResize = () => {
      if (containerRef.current) chart.applyOptions({ width: containerRef.current.clientWidth });
    };
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
    };
  }, [buckets]);

  if (!buckets.length) {
    return (
      <div
        className={cn(
          "flex h-[240px] w-full items-center justify-center rounded-md border border-dashed border-border/60 bg-surface0/25 text-xs text-muted-foreground font-mono",
          className,
        )}
      >
        No distribution
      </div>
    );
  }

  return <div ref={containerRef} className={cn("w-full", className)} />;
}
