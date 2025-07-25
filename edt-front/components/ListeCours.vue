<script setup>
import { ref, onMounted } from 'vue'
import { fetchAllConfig } from '@/services/configGlobale.js'
import { fetchIntervenants } from '~/services/intervenants.js'
import { getColorBySemestreAndType } from '@/composables/useColorUtils.js'

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  semesters: {
    type: Object,
    required: true
  },
  source: {
    type: String,
    default: 'availableCourses'
  }
})

const emit = defineEmits(['drag-start'])

const semesters = ref([])
const professors = ref([])
const courses = ref([])
const groups = ref([])
const config = ref(null)

onMounted(async () => {
  config.value = await fetchAllConfig()
  semesters.value = await config.value.semesters
  professors.value = await fetchIntervenants()
})

const selectedSemester = ref('')
const selectedProfessor = ref('')
const selectedCourse = ref('')
const selectedGroup = ref('')

const filteredCourses = computed(() => {
  return props.items.filter((course) => {
    return (
        (selectedSemester.value === '' || course.semester === selectedSemester.value) &&
        (selectedProfessor.value === '' || course.professor === selectedProfessor.value) &&
        (selectedCourse.value === '' || course.matiere === selectedCourse.value) &&
        (selectedGroup.value === '' || course.groupIndex === parseInt(selectedGroup.value))
    )
  })
})

const getKeys = (obj) => {
  return Object.keys(obj).map((key) => ({ label: key, value: key }))
}

const getListeCoursBySemestre = () => {
  if (selectedSemester.value === '') {
    return []
  }

  return config.value.semesters[selectedSemester.value].matieres.map(matiere => ({
    label: matiere,
    value: matiere
  }))
}

const getListeGroupesBySemestre = () => {
  if (selectedSemester.value === '') {
    return []
  }

  const groupesObj = config.value.semesters[selectedSemester.value].groupesTp || {}
  return Object.entries(groupesObj).map(([key, label]) => ({
    label,
    value: key
  }))
}

const displayCourseListe = (course) => {
  let groupe = ''
  if (course.type === 'TP') {
    groupe = 'TP ' + String.fromCharCode(64 + course.groupIndex)
  } else if (course.type === 'TD') {
    groupe =
        'TD ' +
        String.fromCharCode(64 + course.groupIndex) +
        String.fromCharCode(65 + course.groupIndex)
  } else {
    groupe = 'CM'
  }

  return `${course.matiere} <br> ${course.professor} <br> ${course.semester} <br> ${groupe}`
}

const resetFilters = () => {
  selectedSemester.value = ''
  selectedProfessor.value = ''
  selectedCourse.value = ''
  selectedGroup.value = ''
}

const onDragStart = (event, course, source, originSlot = '') => {
  console.log('Drag started for course:', course)
  event.dataTransfer.setData('courseId', course.id)
  event.dataTransfer.setData('source', source) // Set the source of the drag
  event.dataTransfer.setData('originSlot', originSlot) // Set the origin slot

  emit('drag-start', course, source, originSlot)
}

</script>

<template>
  <div>
    <div style="display: flex; width: 100%;">
      <div style="flex: 8;" class="me-2">
        <div>
          <label for="semester">Semestre :</label>
          <Select
              id="semester"
              :filter="true"
              optionLabel="label"
              optionValue="value"
              class="w-full"
              v-model="selectedSemester" :options="getKeys(semesters)"
          />
        </div>
        <div>
          <label for="semester">Prof :</label>
          <Select v-model="selectedProfessor"
                  :filter="true"
                  optionLabel="name"
                  optionValue="key"
                  class="w-full"
                  :options="professors"/>
        </div>
        <div>
          <label for="semester">Cours :</label>
          <Select v-model="selectedCourse"
                  :filter="true"
                  optionLabel="label"
                  optionValue="value"
                  emptyMessage="Choisir un semestre pour voir les cours"
                  placeholder="Choisir un semestre"
                  :options="getListeCoursBySemestre()" class="w-full"/>
        </div>
        <div>
          <label for="semester">Groupe :</label>
          <Select v-model="selectedGroup" :options="getListeGroupesBySemestre()"
                  :filter="true"
                  emptyMessage="Choisir un semestre pour voir les groupes"
                  placeholder="Choisir un semestre"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full" />
        </div>
      </div>
      <div style="flex: 2; display: flex; align-items: stretch; justify-content: center;">
        <button style="width: 100%; height: 100%;" @click="resetFilters"
                class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
        >
          Reset filtre
        </button>
      </div>
    </div>
    <div class="list-group grid-container-available mt-2" v-if="filteredCourses && filteredCourses.length > 0">
      <div
          v-for="course in filteredCourses"
          :key="course.id"
          :class="`list-group-item grid-item-available ${course.type} ${course.isVacataire === true ? 'vacataire' : ''}`"
          :style="{
          gridColumn: `span ${course.groupCount}`,
          backgroundColor: getColorBySemestreAndType(course.color, course.type),
          color: 'white',
          cursor: 'move'
        }"
          draggable="true"
          :data-id="course.id"
          @dragstart="onDragStart($event, course, source, '')"
      >
        <span v-html="displayCourseListe(course)" class="course-available"></span>
      </div>
    </div>
    <div class="mt-2" v-else-if="filteredCourses && filteredCourses.length === 0 && selectedGroup === '' && selectedCourse === '' && selectedSemester === '' && selectedProfessor === ''">
      <Message severity="success">
      <strong>Youpi !</strong> Tous les cours sont placés pour cette semaine.
      </Message>
    </div>
    <div class="mt-2" v-else>
      <Message severity="warn">
        <strong>Ohoho</strong> Aucun cours trouvé.
      </Message>
    </div>
  </div>
</template>

<style scoped>

</style>
