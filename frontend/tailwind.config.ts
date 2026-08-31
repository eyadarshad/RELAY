import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        void: "#000000",
        surface: "#080808",
        "surface-raised": "#101010",
        "surface-overlay": "#161616",
        border: "#1C1C1C",
        "border-active": "#333333",
        "border-highlight": "#444444",
        "text-primary": "#F4F4F4",
        "text-secondary": "#8E8E8E",
        "text-muted": "#555555",
        accent: "#CCFF00", // Acid signal green
        "accent-dim": "#99BF00",
        "signal-green": "#00FF88",
        "signal-cyan": "#00E5FF",
        "signal-amber": "#FFB800",
        "signal-red": "#FF3333",
      },
      fontFamily: {
        mono: ["var(--font-jetbrains)", "Courier New", "monospace"],
        display: ["var(--font-space)", "sans-serif"],
        sans: ["var(--font-inter)", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-ping": "ping 2s cubic-bezier(0, 0, 0.2, 1) infinite",
        "scanline": "scanline 8s linear infinite",
        "glitch": "glitch 1s infinite linear alternate-reverse",
      },
      keyframes: {
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(1000%)" },
        },
        glitch: {
          "0%": { textShadow: "1px 0 0 #00FF88, -1px 0 0 #00E5FF" },
          "50%": { textShadow: "-1px 0 0 #00FF88, 1px 0 0 #CCFF00" },
          "100%": { textShadow: "1px 0 0 #FF3333, -1px 0 0 #00E5FF" },
        }
      },
    },
  },
  plugins: [],
};
export default config;
