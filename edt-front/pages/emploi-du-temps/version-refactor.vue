<template>
  <h1>emploi-du-temps</h1>
  <div class="flex flex-row flex-wrap">
    <div class="basis-2/3">
      <WeekSelector
        v-model:selectedNumWeek="selectedNumWeek"
        :weeks="weeks"
        :selected-week="selectedWeek"
        @load-week="_loadWeek"
        @previous-week="_previousWeek"
        @next-week="_nextWeek"
      />
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
        <CourseGrid
            :size="size"
          :days="days"
          :time-slots="timeSlots"
          :selected-week="selectedWeek"
          :semesters="semesters"
          :placed-courses="placedCourses"
          :display-course="displayCourse"
          :get-color-by-semestre-and-type="getColorBySemestreAndType"
          @drag-start="onDragStart"
          @drop="onDrop"
          @mouseover="highlightSameCourses"
          @mouseout="clearSameCoursesHighlight"
          @dragend="clearHighlight"
          @edit-room="openModal"
          @remove-course="removeCourse"
        />
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
    <RoomEditModal
      v-model:is-open="isModalOpen"
      :course="modalCourse"
      @save="saveRoom"
    />
  </div>
</template>

<script setup>
definePageMeta({
  middleware: ['authenticated'],
})

import { ref } from 'vue'
import { fetchWeek, fetchWeeks } from '~/services/weeks.js'
import { fetchAllConfig } from '~/services/configGlobale.js'
import {
  assignRoomsByWeek,
  deleteCourse,
  fetchCoursesByWeek,
  updateCourse,
  updateCourseToReport,
  updateCourseFromReport
} from '~/services/courses.js'
import { fetchConstraintsByWeek } from '~/services/constraints.js'
import { fetchEventsByWeek } from '~/services/events.js'
import { getColorBySemestreAndType } from '@/composables/useColorUtils.js'
import { convertToHeureInt, convertToHeureText } from '@/composables/useTimeConversion.js'
import { groupToInt, groupToText, incrementGroupNumber } from '@/composables/useGroupUtils.js'
import { useDragDrop } from '@/composables/useDragDrop.js'
import { useCoursesManagement } from '@/composables/useCoursesManagement.js'

// Components
import WeekSelector from '@/components/WeekSelector.vue'
import CourseGrid from '@/components/CourseGrid.vue'
import RoomEditModal from '@/components/RoomEditModal.vue'
import ListeCours from '@/components/ListeCours.vue'

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

// Initialize composables
const {
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
} = useCoursesManagement(placedCourses, coursesOfWeeks, selectedNumWeek)

const {
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
} = useDragDrop(placedCourses, coursesOfWeeks, coursesOfReport, config, selectedNumWeek)

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

// verifyAndResetGrid is now provided by useCoursesManagement

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
  applyRestrictions()
}

const _getCourses = async () => {
  coursesOfWeeks.value = await fetchCoursesByWeek(selectedNumWeek.value)

  // parcourir coursesOfWeeks et retirer tous les cours qui sont déjà placés dans placedCourses. Un cours placé est un cours qui a une date et un créneau. Les cours retirés sont à mettre dans placedCourses
  coursesOfWeeks.value = coursesOfWeeks.value.filter((course) => {
    if (course.date && course.creneau) {
      const key = `${course.date}_${convertToHeureText(course.creneau)}_${course.semester}_${groupToText(course.groupIndex)}`
      placedCourses.value[key] = course
      return false
    }
    return true
  })

  Object.keys(placedCourses.value).forEach(async (key) => {
    const course = await placedCourses.value[key]
    if (course.blocked === false) {
      mergeCells(course.date, convertToHeureText(course.creneau), course.semester, groupToText(course.groupIndex), course.groupCount, course.type)
    }
  })

  coursesOfReport.value = await fetchCoursesByWeek(0) //0 = semaine de report
}

// These functions are now provided by composables

const onDragStartEvent = (course, source, originSlot) => {
  console.log('onDragStartEvent called with course:', course, 'source:', source, 'originSlot:', originSlot)
  highlightValidCells(course)
}

const applyRestrictions = () => {
  // blcoage du créneau de 12h30, tous les jours, pour tous les groupes
  days.value.forEach((day) => {
    // blocage du créneau de 12h30
    Object.keys(semesters.value).forEach((semester) => {
      config.value.semesters[semester].groupesTp.forEach((groupe) => {
        blockSlot(day.day, '12h30', semester, groupe, 'Pause')
      })
    })
  })

  Object.keys(restrictedSlots.value).forEach((key) => {
    restrictedSlots.value[key].forEach((slot) => {
      const { type, slot: timeSlot, semester, days, groups, period, motif } = slot
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

// These functions are now provided by composables

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

// These functions are now provided by composables

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: '2-digit'
  }).format(date)
}

const affectRooms = async () => {
  try {
    // appel API pour affecter les salles et récupérer la mise à jour
    const reponse = await assignRoomsByWeek(selectedNumWeek.value)
    console.log(reponse)
    await _getCourses()
  } catch (error) {
    console.error('Erreur lors de l\'affectation des salles:', error)
  }
}

</script>

<style scoped>




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
