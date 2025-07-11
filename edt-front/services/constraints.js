export async function fetchConstraintsByWeek(num) {
  console.log('Fetching constraints...')
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/intervenants/contraintes/${num}`)
  } catch (error)
  {
    console.error('Error fetching constraints:', error)
    throw error
  }
}
