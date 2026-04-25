"use client";

import { createChart, type IChartApi, type ISeriesApi, type LineData } from "lightweight-charts";
import { useEffect, useRef } from "react";

export type EquityPoint = { time: string; value: number };

export function EquityChart({ data }: { data: EquityPoint[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 320,
      layout: {
        background: { color: "transparent" },
        textColor: "rgb(190 195 205)",
      },
      grid: {
        horzLines: { color: "rgba(255,255,255,0.05)" },
        vertLines: { color: "rgba(255,255,255,0.05)" },
      },
      timeScale: { borderColor: "rgba(255,255,255,0.1)" },
      rightPriceScale: { borderColor: "rgba(255,255,255,0.1)" },
    });
    const series: ISeriesApi<"Area"> = chart.addAreaSeries({
      lineColor: "rgb(34 211 159)",
      topColor: "rgba(34, 211, 159, 0.4)",
      bottomColor: "rgba(34, 211, 159, 0.0)",
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

  return <div ref={containerRef} className="w-full" />;
}
