import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MetricTileDemo } from "@/styleguide/demos/catalog";

describe("MetricTile", () => {
  it("renders labels", () => {
    render(<MetricTileDemo />);
    expect(screen.getByText("Sharpe (OOS)")).toBeInTheDocument();
    expect(screen.getByText("Latency p99")).toBeInTheDocument();
  });
});
