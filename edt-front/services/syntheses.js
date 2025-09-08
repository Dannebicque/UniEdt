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

export async function fetchPrevisionnel() {
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/synthese/previsionnel`)
  }
  catch (error) {
    console.error('Error fetching courses:', error)
    throw error
  }
}

