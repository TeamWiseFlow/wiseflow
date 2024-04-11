import path from "path"
import * as child from "child_process"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
// const commitHash = child.execSync('git rev-parse --short HEAD').toString()
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // define: { 'import.meta.env.VITE_APP_VERSION': JSON.stringify(commitHash) },
})
