import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: './src/main.ts',
        preload: './src/preload.ts',
        renderer: './src/renderer.tsx'
      },
      output: {
        entryFileNames: '[name].js'
      }
    }
  }
}); 