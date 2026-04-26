import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BadgeDemo } from "@/styleguide/demos/catalog";

describe("Badge", () => {
  it("renders demo variants", () => {
    render(<BadgeDemo />);
    expect(screen.getByText("live")).toBeInTheDocument();
    expect(screen.getByText("paper")).toBeInTheDocument();
    expect(screen.getByText("default")).toBeInTheDocument();
  });
});
