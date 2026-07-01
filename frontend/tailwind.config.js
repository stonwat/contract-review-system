/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  // 仅用于间距/布局微调，配合 Element Plus 使用
  // 为避免与 Element Plus 样式冲突，不启用 preflight
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {},
  },
  plugins: [],
}
