

export async function fetchEventsByWeek(num) {
  console.log('Fetching events...')
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/events/${num}`)
  } catch (error)
  {
    console.error('Error fetching events:', error)
    throw error
  }
}
