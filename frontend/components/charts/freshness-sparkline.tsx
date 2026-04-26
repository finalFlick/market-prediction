"use client";

import { createChart, type LineData } from "lightweight-charts";
import { useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

/** Catppuccin Mocha `teal` */
const SPARK_COLOR = "rgb(148 226 213)";

export function FreshnessSparkline({
  points,
  className,
}: {
  points: { time: string; value: number }[];
  className?: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !points.length) return;
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 64,
      layout: { background: { color: "transparent" }, textColor: "rgb(166 173 200)" },
      grid: { vertLines: { visible: false }, horzLines: { visible: false } },
      rightPriceScale: { visible: false },
      timeScale: { visible: false },
      crosshair: { mode: 0 },
    });
    const series = chart.addLineSeries({
      color: SPARK_COLOR,
      lineWidth: 2,
    });
    series.setData(points as unknown as LineData[]);
    chart.timeScale().fitContent();

    const onResize = () => {
      if (containerRef.current) chart.applyOptions({ width: containerRef.current.clientWidth });
    };
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
    };
  }, [points]);

  if (!points.length) {
    return (
      <div
        className={cn(
          "h-[64px] w-full rounded border border-dashed border-border/50 bg-surface0/20",
          className,
        )}
      />
    );
  }

  return <div ref={containerRef} className={cn("w-full", className)} />;
}
