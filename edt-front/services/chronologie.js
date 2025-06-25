export async function fetchCoursesByChronologie(professeur = '', semestre = '', matiere = '') {
  console.log('Fetching courses...')
  const config = useRuntimeConfig()
  console.log(config)

  try {
    return await $fetch(`${config.public.apiBaseUrl}/chronologie/?professeur=${professeur}&semestre=${semestre}&matiere=${matiere}`)
  }
  catch (error) {
    console.error('Error fetching courses:', error)
    throw error
  }
}

