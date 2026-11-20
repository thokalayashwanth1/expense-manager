import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  base: "/assets/expense_manager/frontend/",
  build: {
    outDir: "../expense_manager/public/frontend",
    emptyOutDir: true,
    cssCodeSplit: false,
    rollupOptions: {
      input: "src/main.js",
      output: { entryFileNames: "app.js", assetFileNames: "app[extname]" },
    },
  },
});