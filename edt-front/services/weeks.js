export async function fetchWeeks() {
    console.log('Fetching weeks...')
  const config = useRuntimeConfig()
  console.log(config)
  try {
      return await $fetch(`${config.public.apiBaseUrl}/weeks/liste`)
  } catch (error) {
      console.error('Error fetching weeks:', error)
      throw error
  }
}

export async function fetchWeek(num) {
  console.log('Fetching week...')
  const config = useRuntimeConfig()
  console.log(config)

  try {
    return await $fetch(`${config.public.apiBaseUrl}/weeks/${num}`)
  } catch (error) {
    console.error('Error fetching week:', error)
    throw error
  }
}
