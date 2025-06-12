<template>
  <h1>emploi-du-temps</h1>
  <div class="flex flex-row flex-wrap">
    <div class="basis-1/4">
      <Button
          :disabled="!selectedNumWeek"
          @click="_previousWeek"
      >Semaine précédente
      </Button>
    </div>
    <div class="basis-1/4">
      <Select v-model="selectedNumWeek" :options="weeks"
              optionLabel="label"
              @change="_loadWeek"
              filter
              optionValue="value"
              placeholder="Sélectionner une semaine"
              class="w-full md:w-56"/>
    </div>
    <div class="basis-1/4">
      <Button
          :disabled="!selectedNumWeek"
          @click="_nextWeek"
      >Semaine suivante
      </Button>
    </div>
    <div class="basis-1/4">
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
  </div>

  <div v-if="selectedWeek">
    <h2 class="mt-4">Emploi du temps pour la semaine N°
      <Badge :value="selectedWeek.week"/>
      (du {{ formatDate(selectedWeek.days[0].date) }} au {{ formatDate(selectedWeek.days[4].date) }})
    </h2>
    <div class="flex flex-row flex-wrap">
      <div class="basis-3/4" id="edt">
        <div class="grid-container mt-2" v-for="day in days" :key="day.day">
          <div class="grid-day">{{ day.day }} {{ day.dateFr }}</div>
          <!-- Header Row: Semesters -->
          <div class="grid-header grid-time">Heure</div>

          <div
              v-for="semestre in selectedWeek.semesters"
              :key="semestre"
              class="grid-header"
              :style="{ gridColumn: `span  ${listeGroupesTp(semestre).length}`, backgroundColor: semesters[semestre].color }"
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
                :style="{ backgroundColor: semesters[semestre].color }"
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
                backgroundColor: placedCourses[
                  `${day.day}_${time}_${semestre}_${group}`
                ]
                  ? placedCourses[`${day.day}_${time}_${semestre}_${group}`].color
                  : ''
              }"
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
                ></span>
                <span
                    v-if="
                    placedCourses[`${day.day}_${time}_${semestre}_${group}`]
                      .blocked === false
                  "
                    @click="
                    openModal(
                      placedCourses[`${day.day}_${time}_${semestre}_${group}`]
                    )
                  "
                >
                  -{{
                    placedCourses[`${day.day}_${time}_${semestre}_${group}`].room
                  }}-
                </span>
                <button
                    v-if="
                    placedCourses[`${day.day}_${time}_${semestre}_${group}`]
                      .blocked === false
                  "
                    class="remove-btn"
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
                  x
                </button>
              </span>
              </div>
            </template>
          </template>
        </div>
      </div>
      <div class="basis-1/4" id="courses">
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
                  @drag-start="onDragStart"
              />
            </TabPanel>
            <TabPanel value="1">
              <ListeCours :items="coursesOfReport" :semesters="semesters"/>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>
    </div>


  </div>
</template>

<script setup>
import RadioButton from 'primevue/radiobutton'
import Button from 'primevue/button'
import Select from 'primevue/select'

import { ref } from 'vue'
import { fetchWeeks, fetchWeek } from '~/services/weeks.js'
import { fetchAllConfig } from '~/services/configGlobale.js'
import { fetchCoursesByWeek } from '~/services/courses.js'
import { fetchConstraintsByWeek } from '~/services/constraints.js'
import { fetchEventsByWeek } from '~/services/events.js'

const configEnv = useRuntimeConfig()
const baseUrl = configEnv.public.apiBaseUrl

const selectedWeek = ref(null)
const selectedNumWeek = ref(null)
const weeks = ref([])
const semesters = ref(null)
const config = ref(null)
const days = ref([])
const coursesOfReport = ref([])
const coursesOfWeeks = ref([])
const displayType = ref('prof')
const constraints = ref({})
const restrictedSlots = ref({})

const timeSlots = ref(['8h00', '9h30', '11h00', '12h30', '14h00', '15h30', '17h00'])

const placedCourses = ref({})

const size = ref(0)

onMounted(async () => {
      // Simulate fetching weeks data
      try {
        weeks.value = await fetchWeeks()
        config.value = await fetchAllConfig()
        console.log('Weeks:', weeks.value)
        console.log('Config:', config.value)
        semesters.value = await config.value.semesters
        console.log('Semesters:', semesters.value)
        Object.values(semesters.value).forEach((semestre) => {
          size.value += semestre.nbTp
        })

      } catch (error) {
        console.error('Erreur lors de la récupération des semaines:', error)
      }
    }
)

const verifyAndResetGrid = () => {
  // pour chaque cours placés on supprime pour remettre la grille en état avant le changement de semestre
  Object.keys(placedCourses.value).forEach((key) => {
    const course = placedCourses.value[key]
    if (course.blocked === false) {
      removeCourse(
          course.day,
          course.time,
          course.group,
          course.groupIndex,
          course.groupCount,
          true
      )
    }
  })
}

const _loadWeek = async () => {
  try {
    verifyAndResetGrid()

    coursesOfWeeks.value = []
    coursesOfReport.value = []

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

  // placedCourses.value = await fetch(baseUrl + '/get-placed-courses/' + selectedNumWeek.value).then((res) =>
  //     res.json()
  // )
  //
  // Object.keys(placedCourses.value).forEach(async (key) => {
  //   const course = await placedCourses.value[key]
  //   if (course.blocked === false) {
  //     mergeCells(course.day, course.time, course.group, course.groupIndex, course.groupCount)
  //   }
  // })
  //
  applyRestrictions()
}

const _getCourses = async () => {
  coursesOfWeeks.value = await fetchCoursesByWeek(selectedNumWeek.value)
  coursesOfReport.value = await fetchCoursesByWeek(0) //0 = semaine de report
}

const onDragStart = (course, source, originSlot) => {
  console.log('onDragStart', course, source, originSlot)
  // event.dataTransfer.setData('courseId', course.id)
  // event.dataTransfer.setData('source', source) // Set the source of the drag
  // event.dataTransfer.setData('originSlot', originSlot) // Set the origin slot

  highlightValidCells(course)
  //event.target.addEventListener('dragend', clearHighlight, { once: true })
}

const onDrop = (event, day, time, semestre, groupNumber) => {
  const courseId = event.dataTransfer.getData('courseId')
  const source = event.dataTransfer.getData('source') // Get the source of the drag

  if (source === 'availableCourses') {
    handleDropFromAvailableCourses(courseId, day, time, semestre, groupNumber)
  } else if (source === 'grid') {
    const originSlot = event.dataTransfer.getData('originSlot') // Get the origin slot
    handleDropFromGrid(courseId, day, time, semestre, groupNumber, originSlot)
  }
  clearHighlight()
}

const handleDropFromAvailableCourses = (courseId, day, time, semestre, groupNumber) => {
  const courseIndex = coursesOfWeeks.value.findIndex((c) => c.id === courseId)
  const course = coursesOfWeeks.value[courseIndex]

  if (course && course.group === semestre && course.groupIndex === groupNumber) {
    const groupSpan = course.groupCount

    if (groupNumber <= groupData.value[semestre].length - groupSpan + 1) {
      mergeCells(day, time, semestre, groupNumber, groupSpan)
      course.time = time
      course.day = day
      course.blocked = false
      course.room = 'A définir'

      const response = $fetch(baseUrl + '/place-course', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          time: time,
          day: day,
          id: course.id,
          week: selectedNumWeek.value
        })
      }).then((res) => res.json())

      response.then((data) => {
        course.id = data.id
      })

      placedCourses.value[`${day}_${time}_${semestre}_${groupNumber}`] = course
      coursesOfWeeks.value.splice(courseIndex, 1)
    }
  }
}

const handleDropFromGrid = (courseId, day, time, semestre, groupNumber, originSlot) => {
  const course = placedCourses.value[originSlot]

  if (course && course.group === semestre && course.groupIndex === groupNumber) {
    const groupSpan = course.groupCount

    if (groupNumber <= groupData.value[semestre].length - groupSpan + 1) {
      removeCourse(
          course.day,
          course.time,
          course.group,
          course.groupIndex,
          course.groupCount,
          true
      )
      mergeCells(day, time, semestre, groupNumber, groupSpan)
      course.time = time
      course.day = day
      course.blocked = false
      course.room = 'A définir'

      const response = $fetch(baseUrl + '/place-course', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          time: time,
          day: day,
          id: course.id,
          week: selectedNumWeek.value
        })
      }).then((res) => res.json())

      response.then((data) => {
        course.id = data.id
      })

      delete placedCourses.value[originSlot]
      placedCourses.value[`${day}_${time}_${semestre}_${groupNumber}`] = course
    }
  }
}

const mergeCells = (day, time, semestre, groupNumber, groupSpan) => {
  const cellSelector = `[data-key="${day}_${time}_${semestre}_${groupNumber}"]`
  const cell = document.querySelector(cellSelector)
  if (cell) {
    cell.style.gridColumn = `span ${groupSpan}`
    cell.style.width = `${50 * groupSpan}px`
    // Remove the extra cells that are merged
    for (let i = 1; i < groupSpan; i++) {
      const extraCellSelector = `[data-key="${day}_${time}_${semestre}_${groupNumber + i}"]`
      const extraCell = document.querySelector(extraCellSelector)
      if (extraCell) {
        extraCell.remove()
      }
    }
  }
}

const onDropToReplace = (event) => {
  const courseId = event.dataTransfer.getData('courseId')
  const courseIndex = coursesOfWeeks.value.findIndex((c) => c.id === courseId)
  const course = coursesOfWeeks.value[courseIndex]

  if (course) {
    course.originalWeek = currentWeek.value
    coursesOfReport.value.push(course)
    coursesOfWeeks.value.splice(courseIndex, 1)
  }
}

const removeCourse = (day, time, semestre, groupNumber, groupSpan, changeSemaine = false) => {
  const courseKey = `${day}_${time}_${semestre}_${groupNumber}`
  const course = placedCourses.value[courseKey]
  const currentCell = document.querySelector(`[data-key="${courseKey}"]`)

  if (course) {
    course.time = null
    course.day = null
    currentCell.style = ''
    currentCell.classList.remove('highlight-same-course')

    // Remove the course from all associated cells and add empty cells back
    for (let i = 0; i < groupSpan; i++) {
      delete placedCourses.value[`${day}_${time}_${semestre}_${groupNumber + i}`]
    }
    // Recreate the missing cells
    for (let i = 1; i < groupSpan; i++) {
      const cellKey = `${day}_${time}_${semestre}_${groupNumber + i}`
      const cell = currentCell.cloneNode(false)
      cell.setAttribute('data-key', cellKey)
      const parent = currentCell.parentNode
      parent.insertBefore(cell, currentCell.nextSibling)
    }

    if (!changeSemaine) {
      //mise à jour de la base de données
      $fetch(baseUrl + '/remove-course/' + course.id, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          week: selectedNumWeek.value
        })
      })
      course.id = null
      coursesOfWeeks.value.push(course)
    }
  }
}

const applyRestrictions = () => {
  console.log('Applying restrictions...')
  // blcoage du créneau de 12h30, tous les jours, pour tous les groupes
  days.value.forEach((day) => {
    // blocage du créneau de 12h30
    Object.keys(semesters.value).forEach((semester) => {
      let semestre = semesters.value[semester]
      console.log(config.value)
      config.value.semesters[semester].groupesTp.forEach((groupe) => {
        blockSlot(day.day, '12h30', semester, groupe, 'Pause')
      })
    })
  })

  console.log(restrictedSlots.value)
  Object.keys(restrictedSlots.value).forEach((key) => {
    restrictedSlots.value[key].forEach((slot) => {
      const { type, slot: timeSlot, semester, days, groups, period, motif } = slot
      console.log(days)
      days.forEach((day) => {
        if (type === 'generic') {
          // dans ce cas tous les semestres, tous les groupes
          Object.keys(groupData.value).forEach((semester) => {
            groupData.value[semester].forEach((groupNumber) => {
              blockSlot(day, timeSlot, semester, groupNumber, motif)
            })
          })
        } else if (type === 'semester') {
          // dans ce cas tous les groupes d'un semestre
          groupData.value[semester].forEach((groupNumber) => {
            blockSlot(day, timeSlot, semester, groupNumber, motif)
          })
        } else if (type === 'group') {
          groups.forEach((groupNumber) => {
            blockSlot(day, timeSlot, semester, groupNumber, motif)
          })
        } else if (type === 'half-day' || type === 'full-day') {
          const times =
              type === 'half-day'
                  ? period === 'morning'
                      ? ['8h00', '9h30', '11h00']
                      : ['14h00', '15h30', '17h00']
                  : ['8h00', '9h30', '11h00', '14h00', '15h30', '17h00']

          if (key === 'all') {
            times.forEach((time) => {
              Object.keys(groupData.value).forEach((semester) => {
                groupData.value[semester].forEach((groupNumber) => {
                  blockSlot(day, time, semester, groupNumber, motif)
                })
              })
            })
          } else {
            console.log(key)
            console.log(groupData.value)
            times.forEach((time) => {
              groupData.value[key].forEach((groupNumber) => {
                blockSlot(day, time, key, groupNumber, motif)
              })
            })
          }
        }
      })
    })
  })
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

const blockSlot = (day, time, semester, groupNumber, motif = null) => {
  const cellKey = `${day}_${time}_${semester}_${groupNumber}`
  placedCourses.value[cellKey] = { motif: motif ?? 'blocked', color: '#e06464', blocked: true }
}

const isProfessorAvailable = (professor, day, time) => {
  return !Object.values(placedCourses.value).some(
      (course) => course.professor === professor && course.time === time && course.day === day
  )
}

const hasProfessorHasContrainte = (professor, day, time) => {
  const professorConstraints = constraints.value[professor]
  // vérifier si le professeur a des contraintes pour ce jour et cette heure
  if (professorConstraints) {
    if (professorConstraints[day] && professorConstraints[day][time]) {
      console.log('Constraint found:', professorConstraints[day][time])
      return professorConstraints[day][time] ?? 'blocked'
    }
  }

  return false
}

const highlightValidCells = (course) => {
  console.log('highlightValidCells', course)
  const { semester, groupIndex, groupCount, professor } = course


  // pour chaque ligne de professorConstraints, identifier le jour, puis parcours les créneaux horaires, marquer les cellules indisponibles

  // affichage des constraintes profs


  days.value.forEach((day) => {
    timeSlots.value.forEach((time) => {
      const hasContrainte = hasProfessorHasContrainte(professor, day.day, convertToHeureInt(time))
      const isAvailable = isProfessorAvailable(professor, day.day, convertToHeureText(time))

      config.value.semesters[semester].groupesTp.forEach((groupe, i) => {
        const cellKey = `${day.day}_${time}_${semester}_${groupe}`
        console.log('cellKey', cellKey)
        const cell = document.querySelector(`[data-key="${cellKey}"]`)

        if (cell && !placedCourses.value[cellKey]) {
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

function convertToHeureText(time) {
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

function convertToHeureInt(time) {
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

  return semesters.value[semestre].groupesTp
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
          cell.classList.remove('highlight-same-course')
        }
      }
    })
  }
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
  console.log('displayCourse', course)
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
    console.log('Course is blocked:', course)
    return course.motif
  }
  return `${course.matiere} <br> ${course.professor} <br> ${course.group} <br> ${groupe}`
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
  text-align: center;
  font-weight: bold;
}

.grid-header {
  background-color: #33B3B2;
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
</style>
