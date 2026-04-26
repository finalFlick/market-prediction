import { describe, expect, it } from "vitest";

import { components, componentsByCategory, getComponent, productionComponentCount } from "../registry";
import type { ComponentStatus } from "../types";

describe("styleguide registry", () => {
  it("has unique ids", () => {
    const ids = components.map((c) => c.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("uses known status literals", () => {
    const allowed: ComponentStatus[] = ["draft", "reviewed", "production"];
    for (const c of components) {
      expect(allowed).toContain(c.status);
    }
  });

  it("has at least one demo per component", () => {
    for (const c of components) {
      expect(c.demos.length).toBeGreaterThan(0);
    }
  });

  it("getComponent resolves known id", () => {
    expect(getComponent("badge")?.name).toBe("Badge");
    expect(getComponent("missing")).toBeUndefined();
  });

  it("componentsByCategory buckets all components", () => {
    const buckets = componentsByCategory();
    const sum =
      buckets.primitives.length +
      buckets.data.length +
      buckets.charts.length +
      buckets.operator.length +
      buckets.navigation.length;
    expect(sum).toBe(components.length);
  });

  it("production count is consistent", () => {
    expect(productionComponentCount).toBe(components.filter((c) => c.status === "production").length);
  });
});
