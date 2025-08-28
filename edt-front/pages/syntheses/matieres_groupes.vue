<script setup>

import { onMounted } from 'vue'
import { fetchMatieresGroupes } from '~/services/syntheses.js'

const data = ref([])



onMounted(async () => {
  try {
    data.value = await fetchMatieresGroupes()
  } catch (error) {
    console.error('Erreur lors de la récupération des semaines:', error)
  }
})

</script>

<template>
  <h1>Synthèses Matière/groupes</h1>
  <table class="table-auto border border-collapse border-gray-400 w-full" v-if="data">
    <thead>
    <tr>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">Matière</th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">Niveau</th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">Groupe</th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">Places</th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">À placer</th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">Statut</th>
    </tr>
    </thead>
    <tbody>
    <template v-for="(mat, matiere) in data" :key="matiere">
      <template v-for="(groupes, niveau) in mat" :key="niveau">
        <tr v-for="(infos, groupe) in groupes" :key="groupe">
          <td class="border border-gray-300 p-2 text-left text-white">{{ matiere }}</td>
          <td class="border border-gray-300 p-2 text-left text-white">{{ niveau }}</td>
          <td class="border border-gray-300 p-2 text-left text-white">{{ groupe }}</td>
          <td class="border border-gray-300 p-2 text-left text-white">{{ infos.places }}</td>
          <td class="border border-gray-300 p-2 text-left text-white">{{ infos.non_places }}</td>
          <td class="border border-gray-300 p-2 text-left text-white">
              <span
                  :style="{
                  color: infos.non_places === 0 ? 'green' : 'orange',
                  fontWeight: 'bold'
                }"
              >
                {{ infos.non_places === 0 ? '✔️' : '⚠️' }}
              </span>
          </td>
        </tr>
      </template>
    </template>
    </tbody>
  </table>
</template>

<style scoped>

</style>
