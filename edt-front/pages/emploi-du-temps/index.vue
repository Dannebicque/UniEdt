<template>
  <h1>emploi-du-temps</h1>
  <div class="flex flex-row flex-wrap">
    <div class="basis-2/3">
      <div class="flex flex-row flex-wrap">
        <div class="basis-1/3">
          <Button
              :disabled="!selectedNumWeek"
              @click="_previousWeek"
          >Semaine précédente
          </Button>
        </div>
        <div class="basis-1/3">
          <Select v-model="selectedNumWeek" :options="weeks"
                  optionLabel="label"
                  @change="_loadWeek"
                  filter
                  optionValue="value"
                  placeholder="Sélectionner une semaine"
                  class="w-full md:w-56"/>
        </div>
        <div class="basis-1/3">
          <Button
              :disabled="!selectedNumWeek"
              @click="_nextWeek"
          >Semaine suivante
          </Button>
        </div>
      </div>
    </div>
    <div class="basis-1/3">
      <div class="flex flex-row flex-wrap">
        <div class="basis-2/3">
          <div class="flex flex-wrap gap-4">
            <div class="flex items-center gap-2">
              <RadioButton v-model="displayType" inputId="displayType1" name="displayType" value="professor"/>
              <label for="displayType1">Par prof.</label>
            </div>
            <div class="flex items-center gap-2">
              <RadioButton v-model="displayType" inputId="displayType2" name="displayType" value="course"/>
              <label for="displayType2">Par matière</label>
            </div>

          </div>

        </div>
        <div class="basis-1/3">
          <Button
              v-if="!showSidebar"
              @click="showSidebar = true"
          >
            <Icon name="prime:fast-backward"/>
          </Button>
          <Button v-if="showSidebar" class="mb-2" @click="showSidebar = false">
            <Icon name="prime:fast-forward"/>
          </Button>

        </div>
      </div>
    </div>
  </div>

  <div v-if="selectedWeek">
    <div class="flex flex-row flex-wrap mt-3">
      <div class="basis-1/2">
        <h2 class="mt-4">

          Emploi du temps pour la semaine N°
          <Badge :value="selectedWeek.week"/>
          (du {{ formatDate(selectedWeek.days[0].date) }} au {{ formatDate(selectedWeek.days[4].date) }})
        </h2>
      </div>
      <div class="basis-1/2">
        <Button @click="affectRooms">Affecter les salles</Button>
      </div>
    </div>
    <div class="flex flex-row flex-wrap">
      <div :class="['transition-all', showSidebar ? 'basis-3/4' : 'basis-full']" id="edt">
        <div class="grid-container mt-2" v-for="day in days" :key="day.day">
          <div class="grid-day">{{ day.day }} - {{ formatDate(day.date) }}</div>
          <!-- Header Row: Semesters -->
          <div class="grid-header grid-time">Heure</div>

          <div
              v-for="semestre in selectedWeek.semesters"
              :key="semestre"
              class="grid-header"
              :style="{ gridColumn: `span  ${listeGroupesTp(semestre).length}`, backgroundColor: semesters[semestre].color, color: 'white' }"
          >
            {{ semestre }}
          </div>

          <!-- Second Row: Group Headers -->
          <div class="grid-time"></div>
          <template v-for="semestre in selectedWeek.semesters" :key="'group-' + semestre">
            <div
                v-for="group in listeGroupesTp(semestre)"
                :key="semestre + group"
                class="grid-header"
                :style="{ backgroundColor: semesters[semestre].color, color: 'white' }"
            >
              {{ group }}
            </div>
          </template>

          <!-- Time Slots and Group Cells -->
          <template v-for="time in timeSlots" :key="time">
            <div class="grid-time">{{ time }}</div>
            <template v-for="semestre in selectedWeek.semesters" :key="'time-' + semestre">
              <div
                  v-for="group in listeGroupesTp(semestre)"
                  :key="time + semestre + group"
                  class="grid-cell"
                  :style="{
                    color: 'white',
                backgroundColor: placedCourses[`${day.day}_${time}_${semestre}_${group}`] ? getColorBySemestreAndType(placedCourses[`${day.day}_${time}_${semestre}_${group}`].color, placedCourses[`${day.day}_${time}_${semestre}_${group}`].type) : '' }"
                  @drop="onDrop($event, day.day, time, semestre, group)"
                  @mouseover="highlightSameCourses(day.day, time, semestre, group)"
                  @mouseout="clearSameCoursesHighlight(day.day, time, semestre, group)"
                  @dragover.prevent
                  :data-key="day.day + '_' + time + '_' + semestre + '_' + group"
                  draggable="true"
                  @dragstart="
                onDragStart(
                  $event,
                  placedCourses[`${day.day}_${time}_${semestre}_${group}`],
                  'grid',
                  `${day.day}_${time}_${semestre}_${group}`
                )
              "
                  @dragend="clearHighlight"
              >
              <span v-if="placedCourses[`${day.day}_${time}_${semestre}_${group}`]">
                <span
                    v-html="
                    displayCourse(
                      placedCourses[`${day.day}_${time}_${semestre}_${group}`]
                    )
                  "
                ></span><br>
                <span
                    v-if="
                    placedCourses[`${day.day}_${time}_${semestre}_${group}`]
                      .blocked === false
                  "
                    @click="
                    editRoom(
                      placedCourses[`${day.day}_${time}_${semestre}_${group}`]
                    )
                  "
                >
                  -{{
                    placedCourses[`${day.day}_${time}_${semestre}_${group}`].room
                  }}-
                </span><br>
                <Button
                    v-if="
                    placedCourses[`${day.day}_${time}_${semestre}_${group}`]
                      .blocked === false
                  "
                    rounded
                    class="mt-1"
                    severity="danger"
                    @click="
                    removeCourse(
                      day.day,
                      time,
                      semestre,
                      group,
                      placedCourses[`${day.day}_${time}_${semestre}_${group}`]
                        .groupCount
                    )
                  "
                >
                  <Icon name="prime:trash"/>
                </Button>
                <Button
                    v-if="
                    placedCourses[`${day.day}_${time}_${semestre}_${group}`]
                      .blocked === false
                  "
                    rounded
                    class="ms-2 mt-1"
                    severity="warn"
                    @click="
                   openModal(placedCourses[`${day.day}_${time}_${semestre}_${group}`])
                  "
                >
                  <Icon name="prime:pen-to-square"/>
                </Button>
              </span>
              </div>
            </template>
          </template>
        </div>
      </div>
      <div class="basis-1/4" id="courses" v-if="showSidebar">
        <div id="dropToReport" class="ms-2"
             :class="{ dragover: isDragOver }"
             @dragenter.prevent="onDragEnter"
             @dragleave.prevent="onDragLeave"
             @dragover.prevent
             @drop.prevent="onDropToReplace($event)"
        >
          Déposez ici pour reporter un cours
        </div>
        <Tabs value="0" class="w-full ms-2">
          <TabList>
            <Tab value="0">Semaine
              <Badge :value="coursesOfWeeks.length"></Badge>
            </Tab>
            <Tab value="1">Report
              <Badge :value="coursesOfReport.length"></Badge>
            </Tab>
          </TabList>
          <TabPanels>
            <TabPanel value="0">
              <ListeCours
                  :items="coursesOfWeeks"
                  :semesters="semesters"
                  source="availableCourses"
                  @drag-start="onDragStartEvent"
              />
            </TabPanel>
            <TabPanel value="1">
              <ListeCours :items="coursesOfReport"
                          :semesters="semesters"
                          source="reportCourses"
                          @drag-start="onDragStartEvent"
              />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>

    </div>

    <!-- Modal for editing room -->
    <Dialog :visible="isModalOpen" :closable="true" modal
            @update:visible="isModalOpen = $event"
            header="Modifier l'événement">
      <p><strong>Cours:</strong> {{ modalCourse.matiere }}</p>
      <p><strong>Professeur:</strong> {{ modalCourse.professor }}</p>
      <p><strong>Créneau:</strong> {{ modalCourse.date }} {{ modalCourse.creneau }}</p>
      <label for="room">Salle:</label>
      <input type="text" v-model="modalCourse.room" id="room"/>
      <button @click="saveRoom">Enregistrer</button>
    </Dialog>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: ['authenticated'],
})

import RadioButton from 'primevue/radiobutton'
import Button from 'primevue/button'
import Select from 'primevue/select'

import { ref } from 'vue'
import { fetchWeek, fetchWeeks } from '~/services/weeks.js'
import { fetchAllConfig } from '~/services/configGlobale.js'
import {
  assignRoomsByWeek,
  deleteCourse,
  fetchCoursesByWeek,
  updateCourse,
  updateCourseFromReport,
  updateCourseToReport
} from '~/services/courses.js'
import { fetchConstraintsByWeek } from '~/services/constraints.js'
import { fetchEventsByWeek } from '~/services/events.js'
import { getColorBySemestreAndType } from '@/composables/useColorUtils.js'

const configEnv = useRuntimeConfig()
const baseUrl = configEnv.public.apiBaseUrl

const showSidebar = ref(true)

const selectedWeek = ref(null)
const selectedNumWeek = ref(1)
const weeks = ref([])
const semesters = ref(null)
const config = ref(null)
const days = ref([])
const coursesOfReport = ref([])
const coursesOfWeeks = ref([])
const displayType = ref('professor')
const constraints = ref({})
const restrictedSlots = ref({})

const timeSlots = ref(['8h00', '9h30', '11h00', '12h30', '14h00', '15h30', '17h00'])

const placedCourses = ref({})

const size = ref(0)

onMounted(async () => {
      // Simulate fetching weeks data-GEA
      try {
        weeks.value = await fetchWeeks()
        config.value = await fetchAllConfig()
        semesters.value = await config.value.semesters
        Object.values(semesters.value).forEach((semestre) => {
          size.value += semestre.nbTp
        })
        await _loadWeek()
      } catch (error) {
        console.error('Erreur lors de la récupération des semaines:', error)
      }
    }
)

const isDragOver = ref(false)

function onDragEnter () {
  isDragOver.value = true
}

function onDragLeave () {
  isDragOver.value = false
}

const verifyAndResetGrid = () => {
  // pour chaque cours placés on supprime pour remettre la grille en état avant le changement de semaine
  Object.keys(placedCourses.value).forEach((key) => {
    const course = placedCourses.value[key]
    if (course && course.blocked === false) {
      removeCourse(
          course.date,
          convertToHeureText(course.creneau),
          course.semester,
          groupToText(course.groupIndex, course.semester),
          course.groupCount,
          true
      )
    }
  })
}

const clearCell = (key) => {
  const cell = document.querySelector(`[data-key="${key}"]`)
  if (cell) {
    cell.textContent = '' // Retirer le texte
    cell.style = '' // Réinitialiser le style
  }
}

const _loadWeek = async () => {
  try {
    await verifyAndResetGrid()

    coursesOfWeeks.value = []
    coursesOfReport.value = []
    placedCourses.value = []

    await _getWeek()
    await _getCourses()

  } catch (error) {
    console.error('Erreur lors de la récupération des semaines:', error)
  }
}

const _getWeek = async () => {
  selectedWeek.value = await fetchWeek(selectedNumWeek.value)
  days.value = selectedWeek.value.days
  restrictedSlots.value = await fetchEventsByWeek(selectedNumWeek.value)
  constraints.value = await fetchConstraintsByWeek(selectedNumWeek.value)
  applyRestrictions()
}

const _getCourses = async () => {
  coursesOfWeeks.value = await fetchCoursesByWeek(selectedNumWeek.value)

  // parcourir coursesOfWeeks et retirer tous les cours qui sont déjà placés dans placedCourses. Un cours placé est un cours qui a une date et un créneau. Les cours retirés sont à mettre dans placedCourses
  coursesOfWeeks.value = coursesOfWeeks.value.filter((course) => {
    if (course.date && course.creneau) {
      const key = `${course.date}_${convertToHeureText(course.creneau)}_${course.semester}_${groupToText(course.groupIndex, course.semester)}`
      placedCourses.value[key] = course
      return false
    }
    return true
  })

  console.log(placedCourses.value)

  Object.keys(placedCourses.value).forEach(async (key) => {
    const course = await placedCourses.value[key]
    if (course.blocked === false) {
      mergeCells(course.date, convertToHeureText(course.creneau), course.semester, groupToText(course.groupIndex, course.semester), course.groupCount, course.type)
    }
  })

  coursesOfReport.value = await fetchCoursesByWeek(0) //0 = semaine de report
}

const onDragStartEvent = (course, source, originSlot) => {
  highlightValidCells(course)
}

const onDragStart = (event, course, source, originSlot) => {
  event.dataTransfer.setData('courseId', course.id)
  event.dataTransfer.setData('source', source) // Set the source of the drag
  event.dataTransfer.setData('originSlot', originSlot) // Set the origin slot

  highlightValidCells(course)
}

const onDrop = (event, day, time, semestre, groupNumber) => {
  const courseId = event.dataTransfer.getData('courseId')
  const source = event.dataTransfer.getData('source') // Get the source of the drag

  if (!courseId) {
    console.warn('No courseId found in the drop event')
    return
  }
  if (source === 'availableCourses') {
    console.log(`Dropping from availableCourses: ${courseId} on ${day} at ${time} for semestre ${semestre} and group ${groupNumber}`)
    handleDropFromAvailableCourses(courseId, day, time, semestre, groupNumber)
  } else if (source === 'reportCourses') {
    handleDropFromCoursesToReport(courseId, day, time, semestre, groupNumber)
  } else if (source === 'grid') {
    const originSlot = event.dataTransfer.getData('originSlot') // Get the origin slot
    handleDropFromGrid(courseId, day, time, semestre, groupNumber, originSlot)
  }
  clearHighlight()
}

const groupToInt = (group, semestre) => {
  //je veux l'inverse de groupToText, donc si group est un nombre, je le retourne, sinon je le converti en nombre en récupérant la clé de sa valeur dans le tableau groupesTp
  if (typeof group === 'number') {
    return group
  } else if (typeof group === 'string') {
    console.log('string')
    const key = Object.keys(config.value.semesters[semestre].groupesTp).find(k => config.value.semesters[semestre].groupesTp[k] === group)
    return parseInt(key, 10)
  }
}

const groupToText = (group, semestre) => {
  return config.value.semesters[semestre].groupesTp[group]
}

const handleDropFromAvailableCourses = async (courseId, day, time, semestre, groupNumber) => {
  const course = coursesOfWeeks.value.find((c) => c.id == courseId)

  if (course && course.semester === semestre && course.groupIndex === groupToInt(groupNumber, semestre)) {
    console.log('ok')
    const groupSpan = course.groupCount

    // if (groupToInt(groupNumber, semestre) <= config.value.semesters[semestre].nbTp - groupSpan + 1) {
    mergeCells(day, time, semestre, groupNumber, groupSpan, course.type)
    //}

    course.creneau = convertToHeureInt(time)
    course.date = day
    course.blocked = false
    course.room = 'A définir'

    await updateCourse(course, selectedNumWeek.value)

    placedCourses.value[`${day}_${time}_${semestre}_${groupNumber}`] = course
    coursesOfWeeks.value = coursesOfWeeks.value.filter(c => c.id != courseId)
  }
}

const handleDropFromCoursesToReport = async (courseId, day, time, semestre, groupNumber) => {
  const course = coursesOfReport.value.find((c) => c.id == courseId)

  if (course && course.semester === semestre && course.groupIndex === groupToInt(groupNumber, semestre)) {
    const groupSpan = course.groupCount

   // if (groupToInt(groupNumber, semestre) <= config.value.semesters[semestre].nbTp - groupSpan + 1) {
      mergeCells(day, time, semestre, groupNumber, groupSpan, course.type)
    //}

    course.creneau = convertToHeureInt(time)
    course.date = day
    course.blocked = false
    course.room = 'A définir'

    await updateCourseFromReport(course, selectedNumWeek.value)

    placedCourses.value[`${day}_${time}_${semestre}_${groupNumber}`] = course
    coursesOfReport.value = coursesOfReport.value.filter(c => c.id != courseId)
  }
}

const handleDropFromGrid = async (courseId, day, time, semestre, groupNumber, originSlot) => {
  const course = placedCourses.value[originSlot]
  if (course && course.semester === semestre && groupToText(course.groupIndex, course.semester) === groupNumber) {
    const groupSpan = course.groupCount
    //if (groupToInt(groupNumber, semestre) <= config.value.semesters[semestre].nbTp - groupSpan + 1) {
      removeCourse(
          course.date,
          convertToHeureText(course.creneau),
          course.semester,
          groupToText(course.groupIndex, course.semester),
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
    //}
  }
}

const mergeCells = (day, time, semestre, groupNumber, groupSpan, type) => {
  const cellSelector = `[data-key="${day}_${time}_${semestre}_${groupNumber}"]`
  const cell = document.querySelector(cellSelector)
  if (cell) {
    cell.style.gridColumn = `span ${groupSpan}`
    const color = getColorBySemestreAndType(config.value.semesters[semestre].color, type)
    cell.style.backgroundColor = `${color} !important`
    cell.style.color='white'
    cell.style.minWidth = `${50 * groupSpan}px`
    // Remove the extra cells that are merged
    for (let i = 1; i < groupSpan; i++) {
      let extraCellSelector = ''
      //si groupNumber est un nombre, on incrémente le groupe suivant, sinon on converti
      if (typeof groupNumber === 'number') {
        extraCellSelector = `[data-key="${day}_${time}_${semestre}_${groupToText(groupNumber + i, semestre)}"]`
      } else {
        extraCellSelector = `[data-key="${day}_${time}_${semestre}_${groupToText(groupToInt(groupNumber, semestre) + i, semestre)}"]`
      }

      const extraCell = document.querySelector(extraCellSelector)
      if (extraCell) {
        extraCell.remove()
      }
    }
  }
}

const onDropToReplace = async (event) => {
  isDragOver.value = false
  const courseId = event.dataTransfer.getData('courseId')
  const source = event.dataTransfer.getData('source')

  if (source === 'availableCourses') {
    const courseIndex = Object.keys(coursesOfWeeks.value).find(
        k => coursesOfWeeks.value[k].id == courseId
    )
    if (courseIndex) {
      let course = coursesOfWeeks.value[courseIndex]
      course.creneau = null
      course.date = null
      course.room = 'A définir'

      delete coursesOfWeeks.value[courseIndex]
      updateCourseToReport(course, selectedNumWeek.value)
      //supprimer le cours de la grille et le placer dans le report
      coursesOfReport.value.push(course)
    }
  } else if (source === 'grid') {
    const originSlot = event.dataTransfer.getData('originSlot')
    const course = placedCourses.value[originSlot]
    if (course) {
      // Supprimer le cours de la grille
      removeCourse(
          course.date,
          convertToHeureText(course.creneau),
          course.semester,
          groupToText(course.groupIndex, course.semester),
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

function incrementGroupNumber (groupNumber, i, semestre = null) {
  //groupeNumber peut être un nombre ou une lettre, donc on gère les deux cas, on retourne le groupe suivant au format lettre
  if (typeof groupNumber === 'number') {
    return groupNumber + i
  } else if (typeof groupNumber === 'string') {
    return groupToText(groupToInt(groupNumber, semestre) + i, semestre)
  }
}

const removeCourse = (day, time, semestre, groupNumber, groupSpan, changeSemaine = false) => {
  const courseKey = `${day}_${time}_${semestre}_${groupNumber}`
  const course = placedCourses.value[courseKey]
  const currentCell = document.querySelector(`[data-key="${courseKey}"]`)

  if (course) {
    course.creneau = null
    course.date = null
    currentCell.style = ''
    currentCell.classList.remove('highlight-same-course')

    // Remove the course from all associated cells and add empty cells back
      delete placedCourses.value[`${day}_${time}_${semestre}_${groupNumber}`]

    // Recreate the missing cells
    for (let i = 1; i < groupSpan; i++) {
      const cellKey = `${day}_${time}_${semestre}_${incrementGroupNumber(groupNumber, i, semestre)}`
      const cell = currentCell.cloneNode(false)
      cell.setAttribute('data-key', cellKey)
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

const applyRestrictions = () => {
  // blcoage du créneau de 12h30, tous les jours, pour tous les groupes
  days.value.forEach((day) => {
    // blocage du créneau de 12h30
    Object.keys(semesters.value).forEach((semester) => {
      Object.values(config.value.semesters[semester].groupesTp).forEach((groupe) => {
        blockSlot(day.day, '12h30', semester, groupe, 'Pause')
      })
    })
  })

  restrictedSlots.value.forEach((slot) => {
    const { code, creneaux, date, description, jour, nom, room, semaine, semestre, type } = slot
    creneaux.forEach((creneau) => {
      Object.values(config.value.semesters[semestre].groupesTp).forEach((groupe) => {
        blockSlot(jour, convertToHeureText(creneau), semestre, groupe, nom, type)
      })
    })
  })
}

const capitalizeFirstLetter = (word) => {
  return word.charAt(0).toUpperCase() + word.slice(1)
}

const clearHighlight = () => {
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

const blockSlot = (day, time, semester, groupNumber, motif = null, type = 'FIXE') => {
  let bgColor = '#e06464' // default color for blocked slots
  if (type === 'FIXE') {
    bgColor = '#e69797'
  } else if (type === 'INFO') {
    bgColor = '#9ee6ef'
  }
  const cellKey = `${capitalizeFirstLetter(day)}_${time}_${semester}_${groupNumber}`
  placedCourses.value[cellKey] = { motif: motif ?? 'blocked', color: bgColor, blocked: true }
}

const isProfessorAvailable = (professor, day, time) => {
  return !Object.values(placedCourses.value).some(
      (course) => course.professor === professor && course.creneau === time && course.date === day
  )
}

const hasProfessorHasContrainte = (professor, day, time) => {
  const professorConstraints = constraints.value[professor]
  // vérifier si le professeur a des contraintes pour ce jour et cette heure
  if (professorConstraints) {
    if (professorConstraints[day] && professorConstraints[day][time]) {
      return professorConstraints[day][time] ?? 'blocked'
    }
  }

  return false
}

const isGroupInRange = (group, groupIndex, groupCount, allGroups) => {
  let groupPosition = Object.keys(allGroups).find(k => allGroups[k] === group)
  const startPosition = groupIndex - 1
  const endPosition = startPosition + groupCount
  groupPosition = parseInt(groupPosition, 10)
  return groupPosition > startPosition && groupPosition <= endPosition
}

const highlightValidCells = (course) => {
  const { semester, groupIndex, groupCount, professor } = course
  // pour chaque ligne de professorConstraints, identifier le jour, puis parcours les créneaux horaires, marquer les cellules indisponibles

  // affichage des constraintes profs

  days.value.forEach((day) => {
    timeSlots.value.forEach((time) => {
      const hasContrainte = hasProfessorHasContrainte(professor, day.day, convertToHeureInt(time))
      const isAvailable = isProfessorAvailable(professor, day.day, convertToHeureText(time))

      Object.values(config.value.semesters[semester].groupesTp).forEach((groupe, i) => {
        if (!isGroupInRange(groupe, groupIndex, groupCount, config.value.semesters[semester].groupesTp)) {
          return // Le groupe n'est pas dans la plage
        }

        const cellKey = `${day.day}_${time}_${semester}_${groupe}`
        const cell = document.querySelector(`[data-key="${cellKey}"]`)
        if (cell && (!placedCourses.value[cellKey] || (placedCourses.value[cellKey].color && placedCourses.value[cellKey].color === '#9ee6ef'))) {
          if (hasContrainte !== false) {
            cell.classList.add('highlight-mandatory')
          } else if (isAvailable) {
            cell.classList.add('highlight')
          }
        }
      })
    })
  })
}

function convertToHeureText (time) {
  const tab = [
    '',
    '8h00',
    '9h30',
    '11h00',
    '14h00',
    '15h30',
    '17h00'
  ]

  return tab[time] || ''
}

function convertToHeureInt (time) {
  const tab = {
    '8h00': 1,
    '9h30': 2,
    '11h00': 3,
    '14h00': 4,
    '15h30': 5,
    '17h00': 6
  }

  return tab[time] || 0
}

const _previousWeek = () => {
  if (selectedNumWeek.value > 1) {
    selectedNumWeek.value -= 1
    _loadWeek()
  }
}

const _nextWeek = () => {
  if (selectedNumWeek.value < 53) {
    selectedNumWeek.value += 1
    _loadWeek()
  }
}

const listeGroupesTp = (semestre) => {
  if (!selectedWeek.value || !semestre) return []
  if (!semesters.value[semestre]) return []

  return Object.values(config.value.semesters[semestre].groupesTp)
}

const highlightSameCourses = (day, time, semestre, groupNumber) => {
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

const clearSameCoursesHighlight = (day, time, semestre, groupNumber) => {
//supprimer la classe highlight-same-course de toutes les cellules
  const highlightedCells = document.querySelectorAll('.highlight-same-course')
  highlightedCells.forEach((cell) => {
    cell.classList.remove('highlight-same-course')
  })
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: '2-digit'
  }).format(date)
}

const displayCourse = (course) => {
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

const modalCourse = ref(null)
const isModalOpen = ref(false)

const openModal = (course) => {
  modalCourse.value = { ...course }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const affectRooms = async () => {
  try {
    // appel API pour affecter les salles et récupérer la mise à jour
    const reponse = await assignRoomsByWeek(selectedNumWeek.value)
    await _getCourses()
  } catch (error) {
    console.error('Erreur lors de l\'affectation des salles:', error)
  }
}

</script>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: 100px repeat(v-bind(size), 1fr);
  gap: 0;
  width: 100%;
  border: 1px solid #000;
}

.grid-day {
  grid-column: span v-bind(size+1);
  background-color: #137C78;
  color:white;
  text-align: center;
  font-weight: bold;
}

.grid-header {
  background-color: #33B3B2;
  color:white;
  text-align: center;
  padding: 8px;
  font-weight: bold;
  border: 1px solid #000;
  grid-column: span 1;
}

.grid-time {
  text-align: center;
  padding: 8px;
  background-color: #33B3B2;
  color:white;
  border: 1px solid #000;
  grid-column: span 1;
}

.grid-cell {
  text-align: center;
  font-size: 9px;
  min-width: 50px;
  padding: 2px;
  border: 1px solid #000;
  background-color: #fff;
  grid-column: span 1;
}

.grid-cell.highlight {
  background-color: #d1e7dd;
}

.grid-cell.highlight-same-course {
  background-color: #ffeb3b !important; /* Highlight color */
}


.remove-btn {
  background: none;
  border: none;
  color: red;
  cursor: pointer;
  font-size: 16px;
  margin-left: 8px;
}

.row {
  position: relative;
}

.list-group-item {
  padding: 10px;
  border-bottom: 1px solid #ddd;
}

.grid-container-replace {
  display: grid;
  grid-template-columns: repeat(8, 1fr); /* Adjust the number of columns as needed */
  gap: 3px;
  min-height: 50px;
}

.grid-item-replace {
  padding: 2px;
  font-size: 9px;
  border: 1px solid #000;
  background-color: #fff;
  text-align: center;
}

.course-replace {
  display: block;
  padding: 8px;
}

.grid-cell.highlight-mandatory {
  background-color: #E69797; /* Rouge pour les contraintes obligatoires */
}

.grid-cell.highlight-optional {
  background-color: #ffffcc; /* Jaune pour les contraintes facultatives */
}

.modal {
  display: block;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgb(0, 0, 0);
  background-color: rgba(0, 0, 0, 0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: 15% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 80%;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: black;
  text-decoration: none;
  cursor: pointer;
}

#edt, #courses {
  max-height: 170vh; /* ou une hauteur fixe, ex: 600px */
  overflow-y: auto;
}

#dropToReport {
  min-height: 60px;
  border: 2px dashed #33B3B2;
  background-color: #f5fafd;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #33B3B2;
  font-size: 1rem;
  transition: background 0.2s, border-color 0.2s;
}

#dropToReport.dragover {
  background-color: #e0f7fa;
  border-color: #ff212e;
  color: #ff212e;
}
</style>
