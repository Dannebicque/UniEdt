<script setup>
definePageMeta({
  middleware: ['authenticated'],
})

import { fetchCoursesByChronologie } from '~/services/chronologie.js'
import { fetchIntervenants } from '~/services/intervenants.js'
import { fetchAllConfig } from '~/services/configGlobale.js'

const professeur = ref()
const semestre = ref()
const matiere = ref()

const professeurs = ref([])
const semestres = ref([])
const matieres = ref([])

const courses = ref()

const onChangeFiltre = async () => {
  courses.value = await fetchCoursesByChronologie(professeur.value, semestre.value, matiere.value)
}

onMounted(async () => {
  professeurs.value = await fetchIntervenants()
  const config = await fetchAllConfig()
  semestres.value = config.semesters || []
  console.log(semestres.value)
})


</script>

<template>
  <h1>Affichage chronologie de l'EDT</h1>
  <div class="flex flex-row flex-wrap">
    <div class="basis-1/3">
      <label for="professeur">Professeur</label>
      <Select
          :filter="true"
          :auto-filter-focus="true"
          id="professeur"
          v-model="professeur"
          :options="professeurs"
          option-label="name"
          option-value="key"
          @change="onChangeFiltre"></Select>
    </div>
    <div class="basis-1/3">
      <label for="semestre">Semestre</label>
      <Select
          id="semestre"
          :filter="true"
          :auto-filter-focus="true"
          v-model="semestre"
          :options="semestres"
          option-label="name"
          option-value="id"
          @change="onChangeFiltre"></Select>
    </div>
    <div class="basis-1/3">
      <label for="matiere">Matière</label>
      <Select
          id="matiere"
          :filter="true"
          :auto-filter-focus="true"
          v-model="matiere"
          :options="matieres"
          option-label="name"
          option-value="id"
          @change="onChangeFiltre"></Select>
    </div>
  </div>

  <div v-if="courses && courses.length > 0">
    <DataTable :value="courses"
               :paginator="true"
               :rows="30"
               :rowsPerPageOptions="[5, 10, 20]"
               class="mt-4">
      <Column field="matiere" header="Matière"/>
      <Column field="professor.name" header="Intervenant"/>
      <Column field="semester" header="Semestre"/>
      <Column field="groupe" header="Groupe"/>
      <Column field="date" header="Date"/>
      <Column field="heure" header="Heure début"/>
      <Column field="heureFin" header="Heure fin"/>
    </DataTable>
  </div>
  <div v-else-if="courses && courses.length === 0">
    <Message severity="info" class="mt-2">Aucun cours trouvé pour les critères sélectionnés.</Message>
  </div>
  <div v-else>
    <Message severity="warn" class="mt-2">Choisir au moins un critère</Message>
  </div>
</template>

<style scoped>

</style>
