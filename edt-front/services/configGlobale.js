export async function fetchAllConfig() {
    console.log('Fetching config...')
  const config = useRuntimeConfig()
  console.log(config)
  try {
      return await $fetch(`${config.public.apiBaseUrl}/config-globale`)
    } catch (error) {
      console.error('Error fetching config:', error)
      throw error
    }
}


