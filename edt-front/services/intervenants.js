export async function fetchIntervenants() {
    console.log('Fetching intervenants...')
  const config = useRuntimeConfig()
  console.log(config)
  const { data, error } = await useFetch(`${config.public.apiBaseUrl}/intervenants`)
  if (error.value) throw error.value
  return data.value
}
