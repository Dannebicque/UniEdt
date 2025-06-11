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
          <RadioButton v-model="displayType" inputId="displayType1" name="displayType" value="prof"/>
          <label for="displayType1">Par prof.</label>
        </div>
        <div class="flex items-center gap-2">
          <RadioButton v-model="displayType" inputId="displayType2" name="displayType" value="matiere"/>
          <label for="displayType2">Par matière</label>
        </div>
      </div>
    </div>
  </div>

  <div v-if="selectedWeek">
    <h2 class="mt-4">Emploi du temps pour la semaine N° {{ selectedWeek.week }} (du {{ formatDate(selectedWeek.days[0].date) }} au {{ formatDate(selectedWeek.days[4].date) }})</h2>
    <div class="flex flex-row flex-wrap">
      <div class="basis-3/4">
        <div class="grid-container mt-2" v-for="day in days" :key="day.day">
          <div class="grid-day">{{ day.day }} {{ day.dateFr }}</div>
          <!-- Header Row: Semesters -->
          <div class="grid-header grid-time">Heure</div>

          <div
              v-for="semestre in selectedWeek.semesters"
              :key="semestre"
              class="grid-header"
              :style="{ gridColumn: `span  ${listeGroupesTp(semestre)}` }"
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
                    placedCourses[`${day.day}_${time}_${semestre}_${groupToInt(group)}`]
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
                      groupToInt(group),
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
      <div class="basis-1/4">
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
              <ListeCours :items="coursesOfWeeks"/>
            </TabPanel>
            <TabPanel value="1">
              <ListeCours :items="coursesOfReport"/>
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

const selectedWeek = ref(null)
const selectedNumWeek = ref(null)
const weeks = ref([])
const semesters = ref(null)
const config = ref(null)
const days = ref([])
const coursesOfReport = ref([])
const coursesOfWeeks = ref([])
const displayType = ref('prof')

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
          size.value += semestre.nb_tp
        })

      } catch (error) {
        console.error('Erreur lors de la récupération des semaines:', error)
      }
    }
)



const _loadWeek = async () => {
  try {
    selectedWeek.value = await fetchWeek(selectedNumWeek.value)
    days.value = selectedWeek.value.days
  } catch (error) {
    console.error('Erreur lors de la récupération des semaines:', error)
  }
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

  return semesters.value[semestre].nb_tp
}

const highlightSameCourses = (day, time, semestre, groupNumber) => {
  const courseKey = `${day}_${time}_${semestre}_${groupNumber}`
  const course = placedCourses.value[courseKey]

  if (course) {
    const highlightValue =
        selectedHighlightType.value === 'course' ? course.matiere : course.professor
    Object.keys(placedCourses.value).forEach((key) => {
      if (
          (selectedHighlightType.value === 'course' &&
              placedCourses.value[key].matiere === highlightValue) ||
          (selectedHighlightType.value === 'professor' &&
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
        selectedHighlightType.value === 'course' ? course.matiere : course.professor
    Object.keys(placedCourses.value).forEach((key) => {
      if (
          (selectedHighlightType.value === 'course' &&
              placedCourses.value[key].matiere === highlightValue) ||
          (selectedHighlightType.value === 'professor' &&
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

.course-available {
  display: block;
  padding: 8px;
}

.grid-container-available {
  display: grid;
  grid-template-columns: repeat(8, 1fr); /* Ajustez le nombre de colonnes selon vos besoins */
  gap: 3px;
}

.grid-item-available {
  padding: 2px;
  font-size: 9px;
  border: 1px solid #000;
  background-color: #fff;
  text-align: center;
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

.sidebar-toggle {
  position: fixed;
  top: 50%;
  width: 80px;
  right: 0;
  transform: translateY(-50%);
  background-color: #007bff;
  color: white;
  padding: 10px;
  cursor: pointer;
  z-index: 1000;
}

.sidebar {
  position: fixed;
  top: 0;
  right: -300px;
  width: 300px;
  height: 100%;
  background-color: #f8f9fa;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.5);
  transition: right 0.3s ease;
  z-index: 999;
}

.sidebar-open {
  right: 0;
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
  background-color: #ffcccc; /* Rouge pour les contraintes obligatoires */
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
</style>
