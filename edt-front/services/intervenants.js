export async function fetchIntervenants() {
    console.log('Fetching intervenants...')
  const config = useRuntimeConfig()

  try {
      return await $fetch(`${config.public.apiBaseUrl}/intervenants`)
  } catch (error) {
      console.error('Error fetching intervenants:', error)
      throw error
  }
}
