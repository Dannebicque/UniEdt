<script setup>
import { onMounted } from 'vue'
import { fetchPrevisionnel } from '~/services/syntheses.js'

const data = ref([])

onMounted(async () => {
  try {
    data.value = await fetchPrevisionnel()
  } catch (error) {
    console.error('Erreur lors de la récupération des semaines:', error)
  }
})

function getBadgeClass (diff) {
  if (diff === 0) return 'bg-green-500 text-white'
  if (diff > 0) return 'bg-red-500 text-white'
  return 'bg-orange-500 text-white'
}
</script>

<template>
  <h1>Synthèses Prévisionnel</h1>

  <table class="table-auto border border-collapse border-gray-400 w-full" v-if="data">
    <thead>
    <tr>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white"
          rowspan="2">Matière
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white"
          rowspan="2">Enseignant
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white"
          colspan="5">CM
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white"
          colspan="5">TD
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white"
          colspan="5">TP
      </th>
    </tr>
    <tr>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Groupes
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Prévi.
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Total<br> Prev.
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        EDT
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Diff
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Groupes
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Prévi.
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Total<br> Prev.
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        EDT
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Diff
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Groupes
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Prévi.
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Total<br> Prev.
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        EDT
      </th>
      <th class="border border-gray-300 p-2 text-left font-semibold  dark:border-gray-600 dark:text-gray-200 text-white">
        Diff
      </th>
    </tr>
    </thead>
    <tbody>
    <template v-for="(enseignants, matiere) in data" :key="matiere">
      <tr v-for="(infos, enseignant) in enseignants" :key="enseignant">

        <td class="border p-2">{{ matiere }}</td>
        <td class="border p-2">{{ enseignant }}</td>
        <!-- CM -->
        <td class="border p-2">{{ infos.previ.nbCM }}</td>
        <td class="border p-2">{{ infos.previ.CM }}</td>
        <td class="border p-2">{{ infos.previ.totCM }}</td>
        <td class="border p-2">{{ infos.edt.CM }}</td>
        <td class="border p-2">
            <span :class="`px-2 py-1 rounded ${getBadgeClass(infos.edt.CM - infos.previ.totCM)}`">
              {{ infos.edt.CM - infos.previ.totCM }}
            </span>
        </td>
        <!-- TD -->
        <td class="border p-2">{{ infos.previ.nbTD }}</td>
        <td class="border p-2">{{ infos.previ.TD }}</td>
        <td class="border p-2">{{ infos.previ.totTD }}</td>
        <td class="border p-2">{{ infos.edt.TD }}</td>
        <td class="border p-2">
          <span :class="`px-2 py-1 rounded ${getBadgeClass(infos.edt.TD - infos.previ.totTD)}`">
              {{ infos.edt.TD - infos.previ.totTD }}
            </span>
        </td>
        <!-- TP -->
        <td class="border p-2">{{ infos.previ.nbTP }}</td>
        <td class="border p-2">{{ infos.previ.TP }}</td>
        <td class="border p-2">{{ infos.previ.totTP }}</td>
        <td class="border p-2">{{ infos.edt.TP }}</td>
        <td class="border p-2">
          <span :class="`px-2 py-1 rounded ${getBadgeClass(infos.edt.TP - infos.previ.totTP)}`">
              {{ infos.edt.TP - infos.previ.totTP }}
            </span>
        </td>
      </tr>

    </template>
    </tbody>
  </table>

</template>

<style scoped>

</style>
