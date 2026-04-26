import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CommandPaletteDemo } from "@/styleguide/demos/catalog";

describe("CommandPalette", () => {
  it("lists commands when open", () => {
    render(<CommandPaletteDemo />);
    expect(screen.getByText("Queue config diff review")).toBeInTheDocument();
  });
});
