import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import fs from 'node:fs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [{
      name: 'local-file-proxy',
      configureServer(server) {
        server.middlewares.use('/profiles/profiles.json', (req, res) => {
          res.setHeader('Content-Type', 'application/json')
          fs.createReadStream('./out/providers.json').pipe(res)
        })
      }
    },
    react(),
  ],
})
