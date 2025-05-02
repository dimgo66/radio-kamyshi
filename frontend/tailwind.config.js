/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e7f7f7',
          100: '#c4eaea',
          200: '#9ddcdc',
          300: '#70cfce',
          400: '#4cc5c4',
          500: '#20b2b0',
          600: '#189897',
          700: '#107c7b',
          800: '#086463',
          900: '#04504f',
        },
        secondary: {
          50: '#f3f3f4',
          100: '#e2e2e4',
          200: '#cececf',
          300: '#aeaeb1',
          400: '#8b8b90',
          500: '#727277',
          600: '#5e5e63',
          700: '#4e4e52',
          800: '#43434a',
          900: '#27272e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
} 