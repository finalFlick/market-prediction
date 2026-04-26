import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { EquityChart } from "../equity-chart";

vi.mock("lightweight-charts", () => {
  return {
    createChart: () => ({
      addAreaSeries: () => ({ setData: vi.fn() }),
      timeScale: () => ({ fitContent: vi.fn() }),
      remove: vi.fn(),
    }),
  };
});

describe("EquityChart", () => {
  it("renders empty state", () => {
    render(<EquityChart data={[]} />);
    expect(screen.getByText("No equity series")).toBeInTheDocument();
  });
});
