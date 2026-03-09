/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          primary: '#101216',
          secondary: '#22252d',
          tertiary: '#1a1d24',
          card: '#22252d',
          hover: '#2a2d35',
        },
        text: {
          primary: '#dfdfdf',
          secondary: '#a0a0a0',
          tertiary: '#707070',
        },
        accent: {
          primary: '#03b79c',
          hover: '#019e87',
          light: 'rgba(3, 183, 156, 0.1)',
        },
        border: {
          DEFAULT: '#2a2d35',
          light: '#3a3d45',
        },
      },
      boxShadow: {
        'glow': '0 0 20px rgba(3, 183, 156, 0.3)',
        'glow-strong': '0 0 30px rgba(3, 183, 156, 0.5)',
      },
      animation: {
        'fade-in-up': 'fadeInUp 400ms ease-out',
        'fade-in': 'fadeIn 250ms ease-out',
        'glow': 'glow 2s ease-in-out infinite',
      },
      transitionDuration: {
        'fast': '150ms',
        'normal': '250ms',
        'slow': '400ms',
      },
    },
  },
  plugins: [],
}
