<template>
  <h1>Semaines de formation</h1>
  <div v-if="semaines">
    <DataTable :value="semaines"
               :paginator="true"
               :rows="30"
               :rowsPerPageOptions="[5, 10, 20]"
               :loading="!semaines.length"
               class="mt-4">
      <Column field="data.week" header="N°"/>
      <Column field="label" header="Libellé"/>
      <Column header="Semestre(s)">
        <template #body="slotProps">
          <template v-if="slotProps.data.semesters">
          <Badge v-for="sem in slotProps.data.semesters" :key="sem"
                 class="badge"
                 :value="sem"
                 :style="{ backgroundColor: semesters[sem]?.color || '#ccc', color: '#fff', marginRight: '4px' }"/>
        </template>
        </template>
      </Column>
      <Column header="Actions">
        <template #body="slotProps">
          <Button rounded severity="info" @click="selectedWeek = slotProps.data; showDialog = true">
            <Icon name="prime:eye"/>
          </Button>
          <Button rounded severity="warn" @click="editWeek = slotProps.data; editDialog = true" class="ms-2">
            <Icon name="prime:pen-to-square"/>
          </Button>
        </template>
      </Column>

    </DataTable>
  </div>

  <template v-if="showDialog">
    <Dialog v-model:visible="showDialog" header="Détail de la semaine" :modal="true" :closable="true"
            style="width: 400px">
      <div v-if="selectedWeek">
        <p><strong>N°:</strong> {{ selectedWeek.data.week }}</p>
        <p><strong>Libellé:</strong> {{ selectedWeek.label }}</p>
        <div><strong>Jour(s):</strong>
          <ul>
            <li v-for="day in selectedWeek.data.days" :key="day">{{ day.day }}, {{ day.date }}</li>
          </ul>
        </div>
        <p><strong>Semestre(s):</strong>
          <span v-for="sem in selectedWeek.data.semesters" :key="sem">
          <Badge :value="sem"
                 :style="{ backgroundColor: semesters[sem]?.color || '#ccc', color: '#fff', marginRight: '4px' }"/>
        </span>
        </p>
      </div>
    </Dialog>
  </template>

  <template v-if="editDialog">
    <Dialog v-model:visible="editDialog" header="Modifier la semaine" :modal="true" :closable="true"
            style="width: 400px">
      <div v-if="editWeek">
        <form @submit.prevent="saveWeek">
          <div class="mb-3">
            <label for="weekNumber"><strong>N°:</strong></label>
            <InputText id="weekNumber" v-model="editWeek.data.week" class="w-full"/>
          </div>
          <div class="mb-3">
            <label for="weekLabel"><strong>Libellé:</strong></label>
            <InputText id="weekLabel" v-model="editWeek.label" class="w-full"/>
          </div>
          <div class="mb-3">
              <div v-for="(day, idx) in editWeek.data.days" :key="idx">
                <label>
                {{editWeek.data.days[idx].day}} :
                </label>
                <InputText v-model="editWeek.data.days[idx].date" placeholder="Date"/>
              </div>
          </div>
          <div class="mb-3">
            <label><strong>Semestre(s):</strong></label>
            <InputText
                v-model="editWeek.data.semesters"
                         class="w-full"/>
          </div>
          <div class="flex justify-end">
            <Button label="Annuler" severity="secondary" @click="editDialog = false" class="mr-2"/>
            <Button label="Enregistrer" type="submit" severity="success"/>
          </div>
        </form>
      </div>
    </Dialog>
  </template>
</template>

<script setup>
definePageMeta({
  middleware: ['authenticated'],
})

// Récupérer la liste des intervenants depuis l'API
import { onMounted, ref } from 'vue'
import { fetchWeeksComplet, updateWeek } from '@/services/weeks.js'
import { fetchAllConfig } from '~/services/configGlobale.js'

const semaines = ref([])
const config = ref({})
const semesters = ref([])

const showDialog = ref(false)
const editDialog = ref(false)
const selectedWeek = ref(null)
const editWeek = ref(null)

onMounted(async () => {
  try {
    const data = await fetchWeeksComplet()
    semaines.value = Array.isArray(data) ? data : Object.values(data)
    config.value = await fetchAllConfig()
    semesters.value = config.value.semesters || []

  } catch (error) {
    console.error('Erreur lors de la récupération des semaines:', error)
  }
})

const saveWeek = async () => {
  try {
    const response = await updateWeek(editWeek.value.data.week, editWeek.value.data)
    editDialog.value = false
  } catch (error) {
    console.error('Erreur lors de la sauvegarde de la semaine:', error)
  }
}

</script>
