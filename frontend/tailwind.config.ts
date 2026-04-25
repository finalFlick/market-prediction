import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1rem",
    },
    extend: {
      colors: {
        background: "hsl(220 13% 7%)",
        foreground: "hsl(220 9% 96%)",
        muted: "hsl(220 13% 14%)",
        "muted-foreground": "hsl(220 9% 64%)",
        card: "hsl(220 13% 10%)",
        "card-foreground": "hsl(220 9% 96%)",
        border: "hsl(220 13% 18%)",
        primary: "hsl(160 84% 50%)",
        "primary-foreground": "hsl(220 13% 7%)",
        danger: "hsl(0 72% 56%)",
        warning: "hsl(38 92% 56%)",
        success: "hsl(142 71% 45%)",
        /* Kitsune cyberpunk palette (MVP-0 operator console) */
        night: "#0a0a0f",
        panel: "#11121a",
        foxfire: "#ff6a3d",
        mint: "#5eead4",
        lavender: "#c4b5fd",
        magenta: "#f472b6",
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
