// https://nuxt.com/docs/api/configuration/nuxt-config
import Aura from '@primeuix/themes/aura';

export default defineNuxtConfig({
    compatibilityDate: '2025-05-15',
    css: [
        '~/assets/scss/main.scss',
        '~/assets/css/tailwind.css'
    ],
    devtools: {enabled: true},
    modules: [
      '@nuxt/eslint',
      '@nuxtjs/tailwindcss',
      '@primevue/nuxt-module',
      '@pinia/nuxt',
      'nuxt-auth-utils',
      '@nuxt/icon'
    ],
    primevue: {
        usePrimeVue: true,
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
    },
    postcss: {
        plugins: {
            tailwindcss: {},
            autoprefixer: {}
        }
    }
})