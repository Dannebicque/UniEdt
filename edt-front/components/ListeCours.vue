<script setup>
import { ref, onMounted } from 'vue'
import { fetchAllConfig } from '@/services/configGlobale.js'
import { fetchIntervenants } from '~/services/intervenants.js'

const props = defineProps({
  items: {
    type: Array,
    required: true
  }
})

const semesters = ref([])
const professors = ref([])
const courses = ref([])
const groups = ref([])
const config = ref(null)

onMounted(async () => {
  config.value = await fetchAllConfig()
  semesters.value = await config.value.semesters
  console.log("semesters" + semesters.value)
  professors.value = await fetchIntervenants()
  courses.value = config.courses
  groups.value = config.groups
})

const selectedSemester = ref('')
const selectedProfessor = ref('')
const selectedCourse = ref('')
const selectedGroup = ref('')

const filteredCourses = computed(() => {
  return props.items.filter((course) => {
    return (
        (selectedSemester.value === '' || course.group === selectedSemester.value) &&
        (selectedProfessor.value === '' || course.professor === selectedProfessor.value) &&
        (selectedCourse.value === '' || course.matiere === selectedCourse.value) &&
        (selectedGroup.value === '' || course.groupIndex === parseInt(selectedGroup.value))
    )
  })
})

const getKeys = (obj) => {
  return Object.keys(obj).map((key) => ({ label: key, value: obj[key] }))
}

const displayCourseListe = (course) => {
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

  return `${course.matiere} <br> ${course.professor} <br> ${course.group} <br> ${groupe}`
}

const resetFilters = () => {
  selectedSemester.value = ''
  selectedProfessor.value = ''
  selectedCourse.value = ''
  selectedGroup.value = ''
}


</script>

<template>
  <div>
    <div>
      <label for="semester">Semestre :</label>
      <Select
          id="semester"
          optionLabel="label"
          @change=""
          v-model="selectedSemester" :options="getKeys(semesters)"
      />
    </div>
    <div>
      <label for="semester">Prof :</label>
      <Select v-model="selectedProfessor"
              optionLabel="name"
              optionValue="key"
              :options="professors"/>
    </div>
    <div>
      <label for="semester">Cours :</label>
      <Select v-model="selectedCourse" :options="courses"/>
    </div>
    <div>
      <label for="semester">Groupe :</label>
      <Select v-model="selectedGroup" :options="groups" />
    </div>
    <div class="list-group grid-container-available">
      <div
          v-for="course in filteredCourses"
          :key="course.id"
          class="list-group-item grid-item-available"
          :style="{
          gridColumn: `span ${course.groupCount}`,
          backgroundColor: course.color,
          cursor: 'move'
        }"
          draggable="true"
          @dragstart="onDragStart($event, course, 'availableCourses', '')"
      >
        <span v-html="displayCourseListe(course)" class="course-available"></span>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
