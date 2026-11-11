import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { defineConfig, loadEnv } from 'vite'

// Chèn các thẻ meta SEO/Ads cần URL tuyệt đối hoặc mã tài khoản, lấy từ biến môi trường.
// Thẻ nào chưa khai báo biến thì bỏ qua, để không xuất bản thẻ rỗng hay mã giả.
// Không đặt og:url/canonical cố định: SPA dùng chung index.html cho mọi route.
function seoMeta(env) {
  const site = (env.VITE_SITE_URL || '').replace(/\/+$/, '')
  const verifications = [
    ['name', 'google-site-verification', env.VITE_GOOGLE_SITE_VERIFICATION],
    ['name', 'facebook-domain-verification', env.VITE_FACEBOOK_DOMAIN_VERIFICATION],
    ['name', 'google-adsense-account', env.VITE_GOOGLE_ADSENSE_ACCOUNT],
    ['property', 'fb:app_id', env.VITE_FACEBOOK_APP_ID],
  ]

  return {
    name: 'seo-meta',
    transformIndexHtml() {
      const tags = []
      const meta = (key, value, content) =>
        tags.push({ tag: 'meta', attrs: { [key]: value, content }, injectTo: 'head' })

      if (site) {
        const image = `${site}/og-image.jpg`
        meta('property', 'og:image', image)
        meta('property', 'og:image:secure_url', image)
        meta('name', 'twitter:image', image)
      }
      verifications.forEach(([key, value, content]) => content && meta(key, value, content))
      return tags
    },
  }
}

export default defineConfig(({ mode }) => ({
  plugins: [
    seoMeta(loadEnv(mode, process.cwd())),
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver({ importStyle: false })],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      dirs: ['src/components', 'src/components/element'],
      resolvers: [ElementPlusResolver({ importStyle: false })],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    host: true,
    // Chỉ dùng khi VITE_API_BASE_URL là đường dẫn tương đối (/api/v1).
    // Mặc định frontend gọi thẳng domain backend.
    proxy: {
      '/api': {
        target: process.env.DEV_API_TARGET || 'http://127.0.0.1:3060',
        changeOrigin: true,
      },
    },
  },
}))
