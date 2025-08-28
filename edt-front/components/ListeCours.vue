<script setup>
import { ref, onMounted, watch } from 'vue'
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

const emit = defineEmits(['drag-start', 'update:highlightProf', 'update:selectedProfessor', 'update:highlightCours', 'update:selectedCours'])

function onHighlightProfChange() {
  emit('update:highlightProf', highlightProf.value)
}
function onProfessorChange() {
  emit('update:selectedProfessor', selectedProfessor.value)
}

function onHighlightCoursChange() {
  console.log('onHighlightCoursChange', highlightCours.value)
  emit('update:highlightCours', highlightCours.value)
}
function onCoursChange() {
  console.log('onCoursChange', selectedCourse.value)
  emit('update:selectedCours', selectedCourse.value)
}



const semesters = ref([])
const professors = ref([])
const vacatairesOnly = ref(false)
const courses = ref([])
const groups = ref([])
const config = ref(null)

onMounted(async () => {
  config.value = await fetchAllConfig()
  semesters.value = await config.value.semesters
  professors.value = await fetchIntervenants()
})

const groupToText = (group, semestre, type = 'TP') => {
  if (type === 'TP') {
    return config.value.semesters[semestre].groupesTp[group]
  } else {
    return config.value.semesters[semestre].groupesTd[group]
  }
}

const selectedSemester = ref('')
const selectedProfessor = ref('')
const selectedCourse = ref('')
const selectedGroup = ref('')
const highlightCours = ref(false)
const highlightProf = ref(false)

const filteredCourses = computed(() => {
  return props.items.filter((course) => {
    return (
        (selectedSemester.value === '' || course.semester === selectedSemester.value) &&
        (selectedProfessor.value === '' || course.professor === selectedProfessor.value) &&
        (selectedCourse.value === '' || course.matiere === selectedCourse.value) &&
        (selectedGroup.value === '' || course.groupIndex === parseInt(selectedGroup.value)) &&
        (!vacatairesOnly.value || course.isVacataire === true)
    )
  })
})

watch(selectedCourse, (val) => {
  if (val === null) {
    highlightCours.value = false
    emit('update:highlightCours', false)
  }
})

watch(selectedProfessor, (val) => {
  console.log('watch selectedProfessor', val)
  if (val === null) {
    highlightProf.value = false
    emit('update:highlightProf', false)
  }
})

const getKeys = (obj) => {
  return Object.keys(obj).map((key) => ({ label: key, value: key }))
}

const getListeCoursBySemestre = () => {
  if (selectedSemester.value === '' || selectedSemester.value === null) {
    return []
  }

  return config.value.semesters[selectedSemester.value].matieres.map(matiere => ({
    label: matiere,
    value: matiere
  }))
}

const getListeGroupesBySemestre = () => {
  if (selectedSemester.value === '' || selectedSemester.value === null) {
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
    groupe = 'TP ' + groupToText(course.groupIndex, course.semester, course.type)
  } else if (course.type === 'TD') {
    groupe =
        'TD ' +
        groupToText(course.groupIndex, course.semester, course.type)
  } else {
    groupe = 'CM'
  }

  let texte = `${course.matiere} <br> ${course.professor} <br> ${course.semester} <br> ${groupe}`

  if (course.duree) {
    texte += ` <br> Durée: ${course.duree}h`
  }

  return texte
}

const resetFilters = () => {
  selectedSemester.value = ''
  selectedProfessor.value = ''
  selectedCourse.value = ''
  selectedGroup.value = ''
  highlightCours.value = false
  highlightProf.value = false
  vacatairesOnly.value = false
  emit('update:highlightProf', highlightProf.value)
  emit('update:highlightCours', highlightCours.value)
}

watch(selectedSemester, (val) => {
  if (val === '' || val === null) {
    selectedCourse.value = ''
    selectedGroup.value = ''
  }
})

const onDragStart = (event, course, source, originSlot = '') => {
  console.log('Drag started for course:', course)
  event.dataTransfer.setData('courseId', course.id)
  event.dataTransfer.setData('source', source) // Set the source of the drag
  event.dataTransfer.setData('originSlot', originSlot) // Set the origin slot

  emit('drag-start', course, source, originSlot)
}

</script>

<template>
  <div v-if="config">
    <div style="display: flex; width: 100%;">
      <div style="flex: 8;" class="me-2">
        <div class="mt-2">
          <label for="semester" class="font-semibold">Semestre :</label>
          <Select
              showClear
              id="semester"
              :autoFilterFocus="true"
              :filter="true"
              optionLabel="label"
              optionValue="value"
              class="w-full"
              v-model="selectedSemester" :options="getKeys(semesters)"
          />
        </div>
        <div class="mt-2">
          <label for="selectedProfessor" class="font-semibold">Prof :</label>
          <Select v-model="selectedProfessor"
                  showClear
                  :autoFilterFocus="true"
                  id="selectedProfessor"
                  @change="onProfessorChange($event)"
                  :filter="true"
                  optionLabel="name"
                  optionValue="key"
                  class="w-full"
                  :options="professors"/>
          <div v-if="selectedProfessor">
            <label for="highlightProf">Mettre en surbrillance:</label>
            <Checkbox  v-model="highlightProf"
                       @change="onHighlightProfChange($event)"
                       id="highlightProf"
                       name="highlightProf"
                       class="flex-auto ms-2" binary />
          </div>
        </div>

        <div class="mt-2">
          <label for="selectedCourse" class="font-semibold">Cours :</label>
          <Select v-model="selectedCourse"
                  id="selectedCourse"
                  :autoFilterFocus="true"
                  showClear
                  :filter="true"
                  @change="onCoursChange($event)"
                  optionLabel="label"
                  optionValue="value"
                  emptyMessage="Choisir un semestre pour voir les cours"
                  placeholder="Choisir un semestre"
                  :options="getListeCoursBySemestre()" class="w-full"/>
          <div v-if="selectedCourse">
            <label for="highlightCours">Mettre en surbrillance:</label>
            <Checkbox  v-model="highlightCours" id="highlightCours"
                       @change="onHighlightCoursChange($event)"
                       name="highlightCours" class="flex-auto ms-2" binary />
          </div>
        </div>
        <div class="mt-2">
          <label for="selectedGroup" class="font-semibold">Groupe :</label>
          <Select v-model="selectedGroup" :options="getListeGroupesBySemestre()"
                  :filter="true"
                  id="selectedGroup"
                  :autoFilterFocus="true"
                  showClear
                  emptyMessage="Choisir un semestre pour voir les groupes"
                  placeholder="Choisir un semestre"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full" />
        </div>

        <div class="mt-2">
          <label class="font-semibold w-24 " for="vacatairesOnly">Afficher les cours des vacataires uniquement:</label>
          <Checkbox  v-model="vacatairesOnly" id="vacatairesOnly" name="vacatairesOnly" class="flex-auto ms-2" binary />
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
