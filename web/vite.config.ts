import { defineConfig } from 'vite';
export default defineConfig({ base: './', worker: { format: 'es' }, build:{rolldownOptions:{input:{main:'index.html',atlas:'atlas.html'}}} });
