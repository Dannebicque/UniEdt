export async function fetchAllSemesters() {
    console.log('Fetching semesters...')
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/semesters/liste`)
  } catch (error) {
    console.error('Error fetching semesters:', error)
    throw error
  }
}
