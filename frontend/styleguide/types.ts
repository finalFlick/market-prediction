import type { ComponentType } from "react";

export type ComponentStatus = "draft" | "reviewed" | "production";

export type DemoState = "default" | "loading" | "empty" | "error" | "stale" | "populated";

export type ComponentCategory = "primitives" | "data" | "charts" | "operator" | "navigation";

export interface Demo {
  id: string;
  state: DemoState;
  label: string;
  /** Demo surface rendered inside the styleguide sandbox. */
  DemoComponent: ComponentType;
}

export interface ComponentMeta {
  id: string;
  name: string;
  category: ComponentCategory;
  status: ComponentStatus;
  /** Repo-relative path to the implementation file. */
  sourcePath: string;
  /** Stable import path for product code (alias `@/…`). */
  importPath: string;
  description: string;
  accessibility: string[];
  keyboard?: string[];
  demos: Demo[];
}
