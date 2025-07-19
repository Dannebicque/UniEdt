// composables/useDragDrop.js
import { ref } from 'vue'
import { groupToInt, groupToText } from './useGroupUtils'
import { convertToHeureInt, convertToHeureText } from './useTimeConversion'
import { updateCourse, updateCourseFromReport, updateCourseToReport } from '~/services/courses'
import { getColorBySemestreAndType } from './useColorUtils'

export function useDragDrop(placedCourses, coursesOfWeeks, coursesOfReport, config, selectedNumWeek) {
  const isDragOver = ref(false)

  function onDragEnter() {
    isDragOver.value = true
  }

  function onDragLeave() {
    isDragOver.value = false
  }

  function onDragStart(event, course, source, originSlot) {
    event.dataTransfer.setData('courseId', course.id)
    event.dataTransfer.setData('source', source)
    event.dataTransfer.setData('originSlot', originSlot)

    highlightValidCells(course)
  }

  function highlightValidCells(course) {
    // This function would need to be implemented based on the specific requirements
    // It should highlight cells where the course can be dropped
    console.log('Highlighting valid cells for course:', course)
  }

  function clearHighlight() {
    const highlightedCells = document.querySelectorAll('.highlight')
    highlightedCells.forEach((cell) => {
      cell.classList.remove('highlight')
    })

    const highlightedMandatoryCells = document.querySelectorAll('.highlight-mandatory')
    highlightedMandatoryCells.forEach((cell) => {
      cell.classList.remove('highlight-mandatory')
    })

    const highlightedOptionalCells = document.querySelectorAll('.highlight-optional')
    highlightedOptionalCells.forEach((cell) => {
      cell.classList.remove('highlight-optional')
    })
  }

  function clearSameCoursesHighlight() {
    const highlightedCells = document.querySelectorAll('.highlight-same-course')
    highlightedCells.forEach((cell) => {
      cell.classList.remove('highlight-same-course')
    })
  }

  function highlightSameCourses(day, time, semestre, groupNumber, displayType) {
    const courseKey = `${day}_${time}_${semestre}_${groupNumber}`
    const course = placedCourses.value[courseKey]

    if (course) {
      const highlightValue =
          displayType.value === 'course' ? course.matiere : course.professor
      Object.keys(placedCourses.value).forEach((key) => {
        if (
            (displayType.value === 'course' &&
                placedCourses.value[key].matiere === highlightValue) ||
            (displayType.value === 'professor' &&
                placedCourses.value[key].professor === highlightValue)
        ) {
          const cell = document.querySelector(`[data-key="${key}"]`)
          if (cell) {
            cell.classList.add('highlight-same-course')
          }
        }
      })
    }
  }

  function mergeCells(day, time, semestre, groupNumber, groupSpan, type) {
    const cellSelector = `[data-key="${day}_${time}_${semestre}_${groupNumber}"]`
    console.log(cellSelector)
    const cell = document.querySelector(cellSelector)
    if (cell) {
      cell.style.gridColumn = `span ${groupSpan}`
      const color = getColorBySemestreAndType(config.value.semesters[semestre].color, type)
      cell.style.backgroundColor = `${color} !important`
      cell.style.minWidth = `${50 * groupSpan}px`
      // Remove the extra cells that are merged
      for (let i = 1; i < groupSpan; i++) {
        const extraCellSelector = `[data-key="${day}_${time}_${semestre}_${groupToText(groupToInt(groupNumber) + i)}"]`
        const extraCell = document.querySelector(extraCellSelector)
        if (extraCell) {
          extraCell.remove()
        }
      }
    }
  }

  async function handleDropFromAvailableCourses(courseId, day, time, semestre, groupNumber) {
    const course = coursesOfWeeks.value.find((c) => c.id == courseId)

    if (course && course.semester === semestre && course.groupIndex === groupToInt(groupNumber)) {
      const groupSpan = course.groupCount

      if (groupToInt(groupNumber) <= config.value.semesters[semestre].nbTp - groupSpan + 1) {
        mergeCells(day, time, semestre, groupNumber, groupSpan, course.type)
        course.creneau = convertToHeureInt(time)
        course.date = day
        course.blocked = false
        course.room = 'A définir'

        await updateCourse(course, selectedNumWeek.value)

        placedCourses.value[`${day}_${time}_${semestre}_${groupNumber}`] = course
        coursesOfWeeks.value = coursesOfWeeks.value.filter(c => c.id != courseId)
      }
    }
  }

  async function handleDropFromCoursesToReport(courseId, day, time, semestre, groupNumber) {
    const course = coursesOfReport.value.find((c) => c.id == courseId)

    if (course && course.semester === semestre && course.groupIndex === groupToInt(groupNumber)) {
      const groupSpan = course.groupCount

      if (groupToInt(groupNumber) <= config.value.semesters[semestre].nbTp - groupSpan + 1) {
        mergeCells(day, time, semestre, groupNumber, groupSpan, course.type)
        course.creneau = convertToHeureInt(time)
        course.date = day
        course.blocked = false
        course.room = 'A définir'

        await updateCourseFromReport(course, selectedNumWeek.value)

        placedCourses.value[`${day}_${time}_${semestre}_${groupNumber}`] = course
        coursesOfReport.value = coursesOfReport.value.filter(c => c.id != courseId)
      }
    }
  }

  async function handleDropFromGrid(courseId, day, time, semestre, groupNumber, originSlot, removeCourse) {
    const course = placedCourses.value[originSlot]
    if (course && course.semester === semestre && groupToText(course.groupIndex) === groupNumber) {
      const groupSpan = course.groupCount
      if (groupToInt(groupNumber) <= config.value.semesters[semestre].nbTp - groupSpan + 1) {
        console.log(course.creneau)
        removeCourse(
            course.date,
            convertToHeureText(course.creneau),
            course.semester,
            groupToText(course.groupIndex),
            course.groupCount,
            true
        )
        mergeCells(day, time, semestre, groupNumber, groupSpan, course.type)
        course.creneau = convertToHeureInt(time)
        course.date = day
        course.blocked = false
        course.room = 'A définir'

        await updateCourse(course, selectedNumWeek.value)

        delete placedCourses.value[originSlot]
        clearSameCoursesHighlight()
        placedCourses.value[`${day}_${time}_${semestre}_${groupNumber}`] = course
      }
    }
  }

  async function onDropToReplace(event, removeCourse) {
    console.log('onDropToReplace called')
    isDragOver.value = false
    const courseId = event.dataTransfer.getData('courseId')
    const source = event.dataTransfer.getData('source')

    if (source === 'availableCourses') {
      console.log(coursesOfWeeks.value)
      const courseIndex = Object.keys(placedCourses.value).find(
          k => placedCourses.value[k].id === courseId
      )

      if (courseIndex) {
        const course = placedCourses.value[courseIndex]
        course.creneau = null
        course.date = null
        course.room = 'A définir'

        delete placedCourses.value[courseIndex]
        updateCourse(course, 0)
        //supprimer le cours de la grille et le placer dans le report
        coursesOfReport.value.push(course)
      }
    } else if (source === 'grid') {
      const originSlot = event.dataTransfer.getData('originSlot')
      console.log('onDropToReplace called from grid with originSlot:', originSlot)
      const course = placedCourses.value[originSlot]
      if (course) {
        // Supprimer le cours de la grille
        removeCourse(
            course.date,
            convertToHeureText(course.creneau),
            course.semester,
            groupToText(course.groupIndex),
            course.groupCount,
            true
        )
        updateCourseToReport(course, selectedNumWeek.value)
        // Ajouter le cours dans la liste des cours de report
        coursesOfReport.value.push(course)
        delete placedCourses.value[originSlot]
      }
    }
  }

  function onDrop(event, day, time, semestre, groupNumber, removeCourse) {
    const courseId = event.dataTransfer.getData('courseId')
    const source = event.dataTransfer.getData('source')

    if (!courseId) {
      console.warn('No courseId found in the drop event')
      return
    }
    if (source === 'availableCourses') {
      handleDropFromAvailableCourses(courseId, day, time, semestre, groupNumber)
    } else if (source === 'reportCourses') {
      console.log('Handling drop from reportCourses:', courseId)
      handleDropFromCoursesToReport(courseId, day, time, semestre, groupNumber)
    } else if (source === 'grid') {
      const originSlot = event.dataTransfer.getData('originSlot')
      console.log('Handling drop from grid:', originSlot)
      handleDropFromGrid(courseId, day, time, semestre, groupNumber, originSlot, removeCourse)
    }
    clearHighlight()
  }

  return {
    isDragOver,
    onDragEnter,
    onDragLeave,
    onDragStart,
    highlightValidCells,
    clearHighlight,
    clearSameCoursesHighlight,
    highlightSameCourses,
    mergeCells,
    handleDropFromAvailableCourses,
    handleDropFromCoursesToReport,
    handleDropFromGrid,
    onDropToReplace,
    onDrop
  }
}
