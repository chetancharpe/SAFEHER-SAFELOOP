export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#080b12",
        panel: "#101723",
        mint: "#48f2b8",
        coral: "#ff5f6d",
        amber: "#ffd166"
      },
      boxShadow: {
        glow: "0 0 44px rgba(72, 242, 184, 0.18)"
      }
    }
  },
  plugins: []
};
