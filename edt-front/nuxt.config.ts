// https://nuxt.com/docs/api/configuration/nuxt-config
import Aura from '@primeuix/themes/aura';

export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  css: [
    '@/assets/css/main.css'
  ],
  devtools: { enabled: true },
  modules: ['@nuxt/eslint', '@primevue/nuxt-module'],
  primevue: {
        options: {
            theme: {
                preset: Aura
            }
        },
        autoImport: true
    },
    runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_API_BASE_URL
    }
  }
})
