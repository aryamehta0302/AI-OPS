/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark': {
          '900': '#0a0e17',
          '800': '#111827',
          '700': '#1a1a2e',
          '600': '#16162a',
          '500': '#2d2d4a',
        },
        'cyber': {
          'blue': '#00d4ff',
          'purple': '#a855f7',
          'green': '#22c55e',
          'red': '#ef4444',
          'yellow': '#fbbf24',
        }
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
        'sans': ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
