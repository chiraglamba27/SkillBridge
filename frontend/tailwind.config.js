/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: "#F3EFE6",
        surface: "#FBF9F4",
        "surface-raised": "#FFFFFF",
        ink: "#14130F",
        "ink-muted": "#5B574D",
        "ink-subtle": "#8C877A",
        rule: "#D9D3C4",
        "rule-subtle": "#E8E3D7",
        "canvas-dark": "#14130F",

        // Functional Status Colors
        known: "#1F6B4F",
        "known-bg": "rgba(31, 107, 79, 0.08)",
        missing: "#C8412B",
        "missing-bg": "rgba(200, 65, 43, 0.08)",
        saffron: "#D99A1E",
        "saffron-bg": "rgba(217, 154, 30, 0.12)",
        cobalt: "#2B4C9B",
      },
      fontFamily: {
        serif: ["Fraunces", "Georgia", "serif"],
        sans: ["'IBM Plex Sans'", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      borderRadius: {
        DEFAULT: "2px",
        sm: "2px",
        md: "4px",
        lg: "6px",
      },
      boxShadow: {
        subtle: "0 1px 2px rgba(20, 19, 15, 0.04)",
        lift: "0 2px 6px rgba(20, 19, 15, 0.06)",
        dark: "0 10px 30px rgba(0, 0, 0, 0.4)",
      },
    },
  },
  plugins: [],
}
