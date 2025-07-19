// composables/useCoursesManagement.js
import { ref } from 'vue'
import { groupToInt, groupToText, incrementGroupNumber } from './useGroupUtils'
import { convertToHeureText } from './useTimeConversion'
import { deleteCourse } from '~/services/courses'

export function useCoursesManagement(placedCourses, coursesOfWeeks, selectedNumWeek) {
  function displayCourse(course) {
    let groupe = ''
    if (course.groupCount === 1) {
      groupe = 'TP ' + String.fromCharCode(64 + course.groupIndex)
    } else if (course.groupCount === 2) {
      groupe =
          'TD ' +
          String.fromCharCode(64 + course.groupIndex) +
          String.fromCharCode(65 + course.groupIndex)
    } else {
      groupe = 'CM'
    }

    if (course.blocked && course.blocked === true) {
      return course.motif
    }
    return `${course.matiere} <br> ${course.professor} <br> ${course.semester} <br> ${groupe}`
  }

  function blockSlot(day, time, semester, groupNumber, motif = null) {
    const cellKey = `${day}_${time}_${semester}_${groupNumber}`
    placedCourses.value[cellKey] = { motif: motif ?? 'blocked', color: '#e06464', blocked: true }
  }

  function isProfessorAvailable(professor, day, time) {
    return !Object.values(placedCourses.value).some(
        (course) => course.professor === professor && course.time === time && course.day === day
    )
  }

  function hasProfessorHasContrainte(professor, day, time, constraints) {
    const professorConstraints = constraints.value[professor]
    // vérifier si le professeur a des contraintes pour ce jour et cette heure
    if (professorConstraints) {
      if (professorConstraints[day] && professorConstraints[day][time]) {
        return professorConstraints[day][time] ?? 'blocked'
      }
    }

    return false
  }

  function removeCourse(day, time, semestre, groupNumber, groupSpan, changeSemaine = false) {
    const courseKey = `${day}_${time}_${semestre}_${groupNumber}`
    const course = placedCourses.value[courseKey]
    const currentCell = document.querySelector(`[data-key="${courseKey}"]`)

    if (course) {
      course.creneau = null
      course.date = null
      currentCell.style = ''
      currentCell.classList.remove('highlight-same-course')

      // Remove the course from all associated cells and add empty cells back
      for (let i = 0; i < groupSpan; i++) {
        delete placedCourses.value[`${day}_${time}_${semestre}_${incrementGroupNumber(groupNumber, i)}`]
      }
      // Recreate the missing cells
      for (let i = 1; i < groupSpan; i++) {
        const cellKey = `${day}_${time}_${semestre}_${incrementGroupNumber(groupNumber, i)}`
        const cell = currentCell.cloneNode(false)
        cell.setAttribute('data-GEA-key', cellKey)
        const parent = currentCell.parentNode
        parent.insertBefore(cell, currentCell.nextSibling)
      }

      if (!changeSemaine) {
        deleteCourse(
            course.id,
            selectedNumWeek.value
        ).then(() => {
              delete placedCourses.value[courseKey]
            }
        )

        coursesOfWeeks.value.push(course)
      }
    }
  }

  function verifyAndResetGrid() {
    // pour chaque cours placés on supprime pour remettre la grille en état avant le changement de semestre
    Object.keys(placedCourses.value).forEach((key) => {
      const course = placedCourses.value[key]
      if (course.blocked === false) {
        removeCourse(
            course.date,
            convertToHeureText(course.creneau),
            course.semester,
            groupToText(course.groupIndex),
            course.groupCount,
            true
        )
      }
    })
  }

  const modalCourse = ref(null)
  const isModalOpen = ref(false)

  function openModal(course) {
    modalCourse.value = { ...course }
    isModalOpen.value = true
  }

  function closeModal() {
    isModalOpen.value = false
  }

  function saveRoom() {
    // This function would need to be implemented based on the specific requirements
    // It should save the room assignment for the course
    console.log('Saving room for course:', modalCourse.value)
    isModalOpen.value = false
  }

  return {
    displayCourse,
    blockSlot,
    isProfessorAvailable,
    hasProfessorHasContrainte,
    removeCourse,
    verifyAndResetGrid,
    modalCourse,
    isModalOpen,
    openModal,
    closeModal,
    saveRoom
  }
}
