export async function fetchCoursesByWeek(num) {
  console.log('Fetching courses...')
  const config = useRuntimeConfig()
  console.log(config)

  try {
    return await $fetch(`${config.public.apiBaseUrl}/courses/${num}`)
  } catch (error)
  {
    console.error('Error fetching courses:', error)
    throw error
  }
}
