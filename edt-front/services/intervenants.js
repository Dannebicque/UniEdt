export async function fetchIntervenantsComplets () {
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/intervenants/complet`)
  } catch (error) {
    console.error('Error fetching intervenants:', error)
    throw error
  }
}

export async function fetchIntervenants() {
  const config = useRuntimeConfig()

  try {
      return await $fetch(`${config.public.apiBaseUrl}/intervenants`)
  } catch (error) {
      console.error('Error fetching intervenants:', error)
      throw error
  }
}

export async function updateIntervenant(key, intervenant) {
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/intervenants/${key}/update`, {
      method: 'PUT',
      body: intervenant
    })
  } catch (error) {
    console.error('Error updating intervenant:', error)
    throw error
  }
}

export async function addIntervenant(intervenant) {
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.public.apiBaseUrl}/intervenants/add`, {
      method: 'POST',
      body: intervenant
    })
  } catch (error) {
    console.error('Error adding intervenant:', error)
    throw error
  }
}
