import { z } from 'zod'

const bodySchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export default defineEventHandler(async (event) => {
  const { email, password } = await readValidatedBody(event, bodySchema.parse)
  const config = useRuntimeConfig()


  const response = await $fetch(`${config.public.apiBaseUrl}/auth/login`, {
    method: 'POST',
    body: { email, password }
  })
  console.log(response)
  if (response && response.access_token) {
    console.log('credentials are valid, setting user session...')
    // set the user session in the cookie
    // this server util is auto-imported by the auth-utils module
    await setUserSession(event, {
      token: response.access_token,
      user: {
        email: email
      },
      loggedIn: true
    })
    return true
  } else {
    throw createError({
      statusCode: 401,
      message: 'Bad credentials'
    })
  }

})
