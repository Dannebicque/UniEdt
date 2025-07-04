<script setup>
import { ref, computed } from 'vue';
import { fetchAllConfig } from '~/services/configGlobale.js'

// Configuration des semestres
const semestres = ref([]);
const semestresKeys = ref([]);
const config = ref(null);

onMounted(async () => {
  config.value = await fetchAllConfig()
  semestres.value = await config.value.semesters
  //extraire dans une nouvelle variables les clés des semestres dans un tableau
  semestresKeys.value = Object.keys(semestres.value);
  console.log(semestresKeys.value)
})

// Mois de l'année scolaire
const moisScolaire = [
  { nom: 'Septembre', jours: 30, index: 8 },
  { nom: 'Octobre', jours: 31, index: 9 },
  { nom: 'Novembre', jours: 30, index: 10 },
  { nom: 'Décembre', jours: 31, index: 11 },
  { nom: 'Janvier', jours: 31, index: 0 },
  { nom: 'Février', jours: 28, index: 1 },
  { nom: 'Mars', jours: 31, index: 2 },
  { nom: 'Avril', jours: 30, index: 3 },
  { nom: 'Mai', jours: 31, index: 4 },
  { nom: 'Juin', jours: 30, index: 5 },
  { nom: 'Juillet', jours: 31, index: 6 },
  { nom: 'Août', jours: 31, index: 7 },
];

// Types possibles pour chaque case
const typesCase = [
  { type: 'cours', couleur: 'bg-white' },
  { type: 'banalisé', couleur: 'bg-yellow-600' },
  { type: 'entreprise', couleur: 'bg-blue-600' },
  { type: 'férié', couleur: 'bg-red-600' },
  { type: 'vacances', couleur: 'bg-green-600' },
  { type: 'soutenances', couleur: 'bg-purple-600' },
];

// Mois actuel (par défaut : septembre)
const moisActuel = ref(0);

// Année scolaire (par défaut : 2025)
const anneeScolaire = ref(2025);

// Données du calendrier
const calendrier = ref(
    Array.from({ length: moisScolaire.length }, (_, moisIndex) =>
        Array.from({ length: moisScolaire[moisIndex].jours }, () =>
            semestresKeys.value.map(() => ({ type: 'cours' })) // Par défaut : "cours"
        )
    )
);

// Navigation entre les mois
const moisPrecedent = () => {
  if (moisActuel.value > 0) moisActuel.value--;
};
const moisSuivant = () => {
  if (moisActuel.value < moisScolaire.length - 1) moisActuel.value++;
};

// Jours de la semaine
const joursSemaine = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];

// Calcul du jour de la semaine pour le 1er jour du mois
const premierJourSemaine = computed(() => {
  const mois = moisScolaire[moisActuel.value];
  const date = new Date(anneeScolaire.value, mois.index, 1);
  return (date.getDay() + 6) % 7; // Ajuste pour que 0 = Lundi, 1 = Mardi, etc.
});

// Vérification si un jour est un week-end
const estWeekend = (jourIndex) => (jourIndex % 7 === 5 || jourIndex % 7 === 6);

// Récupération de la classe CSS pour un type
const getCouleurParType = (type) => {
  const typeInfo = typesCase.find((t) => t.type === type);
  return typeInfo ? typeInfo.couleur : 'bg-gray-200'; // Couleur par défaut si le type n'existe pas
};
</script>

<template>
  <div class="p-4" v-if="semestres && semestresKeys">
    <!-- Navigation -->
    <div class="flex justify-between items-center mb-4">
      <button @click="moisPrecedent" :disabled="moisActuel === 0" class="btn">Mois précédent</button>
      <h2 class="text-xl font-bold">{{ moisScolaire[moisActuel].nom }} {{ anneeScolaire }}</h2>
      <button @click="moisSuivant" :disabled="moisActuel === moisScolaire.length - 1" class="btn">Mois suivant</button>
    </div>

    <!-- Tableau du calendrier -->
    <table class="table-auto w-full border-collapse border border-gray-300">
      <thead>
      <!-- Ligne des jours de la semaine -->
      <tr>
        <th class="border border-gray-300 p-1 jour">Jour</th>
        <th class="border border-gray-300 p-1 jour">Date</th>
        <th v-for="semestre in semestresKeys" :key="semestre" class="border border-gray-300 p-1 jour">
          {{ semestre }}
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(jour, index) in moisScolaire[moisActuel].jours" :key="index">
        <!-- Affichage du jour et de la date -->
        <td class="border border-gray-300 p-2" :class="estWeekend((index + premierJourSemaine) % 7) ? 'we' : 'jour'">
          {{ joursSemaine[(index + premierJourSemaine) % 7] }}
        </td>
        <td class="border border-gray-300 p-2" :class="estWeekend((index + premierJourSemaine) % 7) ? 'we' : 'jour'">
          {{ index + 1 }}
        </td>
        <!-- Colonnes pour chaque semestre -->
        <template v-if="estWeekend((index + premierJourSemaine) % 7)">
          <td class="we text-center"
              v-for="(semestre, semestreIndex) in semestres"
              :key="semestreIndex"
          >Week End</td>
        </template>
        <template v-else>
          <td
              v-for="(semestre, semestreIndex) in semestres"
              :key="semestreIndex"
              class="border border-gray-300 p-2 cursor-pointer"
              :class="getCouleurParType(calendrier[moisActuel][index][semestreIndex].type)"
              @click="calendrier[moisActuel][index][semestreIndex].type = typesCase[(typesCase.findIndex(t => t.type === calendrier[moisActuel][index][semestreIndex].type) + 1) % typesCase.length].type"
          >
            {{ calendrier[moisActuel][index][semestreIndex].type }}
          </td>
        </template>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.btn {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.jour {
  background-color: #33B3B2;
}

.we {
  background-color: #00b7eb;
}
</style>
