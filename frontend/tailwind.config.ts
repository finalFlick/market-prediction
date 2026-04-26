import type { Config } from "tailwindcss";

/**
 * Catppuccin Mocha palette — verbatim hex values from
 * https://github.com/catppuccin/palette (palette.json v1.8.0, MIT).
 *
 * Operator-console role aliases (`primary`, `danger`, `warning`, etc.) sit on
 * top so utility classes like `bg-primary` resolve to the canonical Mocha
 * accent and `bg-blue` / `bg-peach` continue to work as raw palette utilities.
 *
 * See `docs/UI_REQUIREMENTS.md` and FEATURE-0034 for usage guidance.
 */
const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./styleguide/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1rem",
    },
    extend: {
      colors: {
        // Catppuccin Mocha — accents
        rosewater: "#f5e0dc",
        flamingo: "#f2cdcd",
        pink: "#f5c2e7",
        mauve: "#cba6f7",
        red: "#f38ba8",
        maroon: "#eba0ac",
        peach: "#fab387",
        yellow: "#f9e2af",
        green: "#a6e3a1",
        teal: "#94e2d5",
        sky: "#89dceb",
        sapphire: "#74c7ec",
        blue: "#89b4fa",
        lavender: "#b4befe",

        // Catppuccin Mocha — text
        text: "#cdd6f4",
        subtext1: "#bac2de",
        subtext0: "#a6adc8",

        // Catppuccin Mocha — surfaces / overlays / backgrounds
        overlay2: "#9399b2",
        overlay1: "#7f849c",
        overlay0: "#6c7086",
        surface2: "#585b70",
        surface1: "#45475a",
        surface0: "#313244",
        base: "#1e1e2e",
        mantle: "#181825",
        crust: "#11111b",

        // Operator-console semantic roles → Catppuccin Mocha
        background: "#1e1e2e", // Base
        foreground: "#cdd6f4", // Text
        muted: "#45475a", // Surface1
        "muted-foreground": "#a6adc8", // Subtext0
        card: "#313244", // Surface0
        "card-foreground": "#cdd6f4", // Text
        border: "#585b70", // Surface2
        primary: "#89b4fa", // Blue (per Catppuccin style guide: links / primary)
        "primary-foreground": "#11111b", // Crust (text on accent)
        danger: "#f38ba8", // Red
        warning: "#f9e2af", // Yellow
        success: "#a6e3a1", // Green
      },
      fontFamily: {
        sans: [
          "var(--font-inter)",
          "ui-sans-serif",
          "system-ui",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "var(--font-jetbrains-mono)",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "monospace",
        ],
      },
      keyframes: {
        "paw-bounce": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-3px)" },
        },
        scanline: {
          "0%": { opacity: "0.88" },
          "50%": { opacity: "1" },
          "100%": { opacity: "0.9" },
        },
        "candle-pulse": {
          "0%, 100%": { filter: "brightness(1)" },
          "50%": { filter: "brightness(1.08)" },
        },
      },
      animation: {
        "paw-bounce": "paw-bounce 1.1s ease-in-out infinite",
        scanline: "scanline 4.5s ease-in-out infinite",
        "candle-pulse": "candle-pulse 2.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
