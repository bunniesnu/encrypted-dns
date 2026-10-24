import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import fs from 'node:fs'
import path from 'node:path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    {
      name: 'serve-profiles',
      configureServer(server) {
        server.middlewares.use('/profiles', (req, res, next) => {
          const filePath = path.join(process.cwd(), 'out', req.url || '')
          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            return fs.createReadStream(filePath).pipe(res)
          }
          next()
        })
      }
    },
    react(),
  ],
})
