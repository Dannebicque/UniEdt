<template>
  <h1>Intervenants</h1>
  <div v-if="intervenants">
    <DataTable :value="intervenants"
               :paginator="true"
               :rows="30"
               :rowsPerPageOptions="[5, 10, 20]"
               :loading="!intervenants.length"
               class="mt-4">
      <Column field="name" header="Prénom Nom"/>
      <Column field="type" header="Statut"/>
      <Column field="key" header="Abbr."/>
      <Column field="email" header="Email"/>
    </DataTable>
  </div>
</template>

<script setup>

// Récupérer la liste des intervenants depuis l'API
import { onMounted, ref } from 'vue'
import { fetchIntervenantsComplets } from '@/services/intervenants'

const intervenants = ref([])

onMounted(async () => {
  try {
    const data = await fetchIntervenantsComplets()
    intervenants.value = Array.isArray(data) ? data : Object.values(data)

  } catch (error) {
    console.error('Erreur lors de la récupération des intervenants:', error)
  }
})

</script>
