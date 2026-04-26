import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ButtonDemo } from "@/styleguide/demos/catalog";

describe("Button", () => {
  it("renders demo variants", () => {
    render(<ButtonDemo />);
    expect(screen.getByText("primary")).toBeInTheDocument();
    expect(screen.getByText("command")).toBeInTheDocument();
  });
});
