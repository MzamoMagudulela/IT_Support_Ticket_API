/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc6fc',
          400: '#36a8f8',
          500: '#0c8de9',
          600: '#016ec7',
          700: '#0258a2',
          800: '#064a85',
          900: '#0b3f6f',
          950: '#07284a',
        },
        slate: {
          850: '#151f32',
          900: '#0f172a',
          950: '#080d1a',
        }
      }
    },
  },
  plugins: [],
}
