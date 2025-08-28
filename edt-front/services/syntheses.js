export async function fetchMatieresGroupes() {
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/synthese/matiere-groupes`)
  }
  catch (error) {
    console.error('Error fetching courses:', error)
    throw error
  }
}

