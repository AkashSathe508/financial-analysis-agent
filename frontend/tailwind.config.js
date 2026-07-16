/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "var(--bg-base)",
        surface: "var(--bg-surface)",
        raised: "var(--bg-surface-2)",
        ink: "var(--ink-primary)",
        muted: "var(--ink-muted)",
        accent: "var(--accent)",
        gain: "var(--signal-gain)",
        loss: "var(--signal-loss)",
        line: "var(--border-hairline)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        mono: ["Geist Mono", "JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
}
