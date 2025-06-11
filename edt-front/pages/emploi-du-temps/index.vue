<template>
  <h1>emploi-du-temps</h1>
  <div class="flex flex-row flex-wrap">
    <div class="basis-1/4">
      <Button
          :disabled="!selectedNumWeek"
      @click="_previousWeek"
      >Semaine précédente</Button>
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
      >Semaine suivante</Button>
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
    <h2 class="mt-4">Emploi du temps pour {{ selectedWeek }}</h2>
    <p>Affichage: {{ displayType }}</p>
    <p>{{selectedWeek}}</p>
    <!-- Here you would render the timetable based on the selected week and display type -->
  </div>
</template>

<script setup>
import RadioButton from 'primevue/radiobutton'
import Button from 'primevue/button'
import Select from 'primevue/select'

import { ref } from 'vue'
import { fetchWeeks, fetchWeek } from '~/services/weeks.js'

const selectedWeek = ref(null)
const selectedNumWeek = ref(null)
const weeks = ref([])
const displayType = ref('prof')

onMounted(async () => {
      // Simulate fetching weeks data
      try {
        weeks.value = await fetchWeeks()
      } catch (error) {
        console.error('Erreur lors de la récupération des semaines:', error)
      }
    }
)

const _loadWeek = async () => {
  try {
    selectedWeek.value = await fetchWeek(selectedNumWeek.value)
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

</script>
