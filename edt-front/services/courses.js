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

// méthode pour mettre à jour un cours une fois placé avec son heure et son jour

export async function updateCourse(course, week) {
  const config = useRuntimeConfig()
  console.log('Updating course:', course)

  try {
    return await $fetch(`${config.public.apiBaseUrl}/courses/update/${course.id}/${week}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {updates: course}
    })
  } catch (error) {
    console.error('Error updating course:', error)
    throw error
  }
}

export async function updateCourseToReport(course, week) {
  const config = useRuntimeConfig()
  console.log('Updating course:', course)

  try {
    return await $fetch(`${config.public.apiBaseUrl}/courses/update/${course.id}/deplace-to-report/${week}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {updates: course}
    })
  } catch (error) {
    console.error('Error updating course:', error)
    throw error
  }
}

export async function updateCourseFromReport(course, week) {
  const config = useRuntimeConfig()
  console.log('Updating course:', course)

  try {
    return await $fetch(`${config.public.apiBaseUrl}/courses/update/${course.id}/deplace-from-report/${week}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {updates: course}
    })
  } catch (error) {
    console.error('Error updating course:', error)
    throw error
  }
}

// méthode pour supprimer un cours
export async function deleteCourse(courseId, week) {
  const config = useRuntimeConfig()
  console.log('Deleting course with ID:', courseId)

  try {
    return await $fetch(`${config.public.apiBaseUrl}/courses/delete/${courseId}/${week}`, {
      method: 'DELETE'
    })
  } catch (error) {
    console.error('Error deleting course:', error)
    throw error
  }
}

export async function assignRoomsByWeek(num) {
  console.log('assignRooms week...')
  const config = useRuntimeConfig()
  console.log(config)

  try {
    return await $fetch(`${config.public.apiBaseUrl}/courses/assign-rooms/${num}`, {
      method: 'POST'
    })
  } catch (error)
  {
    console.error('Error assigning rooms:', error)
    throw error
  }
}
