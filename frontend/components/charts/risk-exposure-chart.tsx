"use client";

import { createChart, type LineData } from "lightweight-charts";
import { useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

export type ExposureSeries = {
  id: string;
  color: string;
  points: { time: string; value: number }[];
};

export function RiskExposureChart({
  series,
  className,
}: {
  series: ExposureSeries[];
  className?: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !series.length) return;
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 280,
      layout: { background: { color: "transparent" }, textColor: "rgb(186 194 222)" },
      grid: {
        horzLines: { color: "rgba(255,255,255,0.05)" },
        vertLines: { color: "rgba(255,255,255,0.05)" },
      },
      rightPriceScale: { borderColor: "rgba(255,255,255,0.1)" },
      timeScale: { borderColor: "rgba(255,255,255,0.1)" },
    });
    for (const s of series) {
      const area = chart.addAreaSeries({
        lineColor: s.color,
        topColor: `${s.color}55`,
        bottomColor: `${s.color}00`,
        lineWidth: 2,
      });
      area.setData(s.points as unknown as LineData[]);
    }
    chart.timeScale().fitContent();

    const onResize = () => {
      if (containerRef.current) chart.applyOptions({ width: containerRef.current.clientWidth });
    };
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
    };
  }, [series]);

  if (!series.length) {
    return (
      <div
        className={cn(
          "flex h-[280px] w-full items-center justify-center rounded-md border border-dashed border-border/60 bg-surface0/25 text-xs text-muted-foreground font-mono",
          className,
        )}
      >
        No exposure series
      </div>
    );
  }

  return <div ref={containerRef} className={cn("w-full", className)} />;
}
