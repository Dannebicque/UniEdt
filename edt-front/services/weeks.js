export async function fetchWeeks() {
  const config = useRuntimeConfig()
  try {
      return await $fetch(`${config.public.apiBaseUrl}/weeks/liste`)
  } catch (error) {
      console.error('Error fetching weeks:', error)
      throw error
  }
}

export async function fetchWeeksComplet() {
  const config = useRuntimeConfig()
  try {
      return await $fetch(`${config.public.apiBaseUrl}/weeks/complet`)
  } catch (error) {
      console.error('Error fetching weeks:', error)
      throw error
  }
}

export async function fetchWeek(num) {
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/weeks/${num}`)
  } catch (error) {
    console.error('Error fetching week:', error)
    throw error
  }
}

export async function updateWeek(week, data) {
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/weeks/${week}/update`, {
      method: 'PUT',
      body: data
    })
  } catch (error) {
    console.error('Error updating week:', error)
    throw error
  }
}
