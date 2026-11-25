import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During local training, /api requests are forwarded to Flask on port 5000.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": { target: "http://127.0.0.1:5000", changeOrigin: true } },
  },
});
