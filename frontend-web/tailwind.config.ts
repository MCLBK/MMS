import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0F2B46",
          light: "#1A5276",
          dark: "#091E30",
          50: "#E8F0F7",
          100: "#C5D9EA",
          200: "#9EBFD9",
          300: "#77A5C8",
          400: "#4F8AB7",
          500: "#1A5276",
          600: "#0F2B46",
          700: "#091E30",
        },
        accent: {
          DEFAULT: "#F57C00",
          light: "#FFB74D",
          dark: "#E65100",
          50: "#FFF3E0",
          100: "#FFE0B2",
          200: "#FFCC80",
          300: "#FFB74D",
          400: "#FFA726",
          500: "#F57C00",
          600: "#E65100",
        },
        secondary: {
          DEFAULT: "#00897B",
          light: "#4DB6AC",
          dark: "#00695C",
        },
        success: {
          DEFAULT: "#2D936C",
          light: "#E8F5E9",
        },
        warning: {
          DEFAULT: "#F0A202",
          light: "#FFF8E1",
        },
        error: {
          DEFAULT: "#D64045",
          light: "#FFEBEE",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          alt: "#F0F2F5",
          dark: "#151D2E",
          "dark-alt": "#1C2640",
        },
        bg: {
          DEFAULT: "#F7F8FA",
          dark: "#0B1120",
        },
      },
      fontFamily: {
        display: ["Outfit", "system-ui", "sans-serif"],
        body: ["DM Sans", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        DEFAULT: "10px",
        lg: "16px",
        xl: "20px",
      },
      boxShadow: {
        sm: "0 1px 3px rgba(15,43,70,0.06)",
        DEFAULT: "0 4px 12px rgba(15,43,70,0.08)",
        lg: "0 8px 30px rgba(15,43,70,0.12)",
      },
    },
  },
  plugins: [],
};

export default config;
