export async function fetchWeeks() {
    console.log('Fetching weeks...')
  const config = useRuntimeConfig()
  console.log(config)
  const { data, error } = await useFetch(`${config.public.apiBaseUrl}/weeks/liste`)
  if (error.value) throw error.value
  return data.value
}

export async function fetchWeek(num) {
  console.log('Fetching week...')
  const config = useRuntimeConfig()
  console.log(config)
  const { data, error } = await useFetch(`${config.public.apiBaseUrl}/weeks/${num}`)
  if (error.value) throw error.value
  return data.value
}
