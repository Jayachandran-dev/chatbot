import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
  },
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/main.js'),
      name: 'Zenbot',
      formats: ['iife'],
      fileName: () => 'zenbot.iife.js',
    },
    cssCodeSplit: false,
    outDir: '../backend/static/widget',
    emptyOutDir: true,
    rollupOptions: {
      output: { assetFileNames: 'zenbot.css' },
    },
  },
});
