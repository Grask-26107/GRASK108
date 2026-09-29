/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bis: {
          navy: '#0f172a',
          blue: '#1e3a8a',
          sky: '#0284c7',
          gold: '#d97706',
          saffron: '#ea580c',
          green: '#15803d',
          darkBg: '#090d16',
          cardDark: '#111827',
          borderDark: '#1f2937'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
