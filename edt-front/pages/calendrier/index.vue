<template>
  <h1>Calendrier</h1>
  <div class="flex flex-row flex-wrap">
    <div class="basis-full">
      <div class="flex flex-row flex-wrap">
        <div class="basis-1/3">
          <Button
              :disabled="!selectedNumWeek"
              @click="_previousWeek"
          >Semaine précédente
          </Button>
        </div>
        <div class="basis-1/3">
          <Select v-model="selectedNumWeek" :options="weeks"
                  optionLabel="label"
                  @change="_loadWeek"
                  filter
                  optionValue="value"
                  placeholder="Sélectionner une semaine"
                  class="w-full md:w-56"/>
        </div>
        <div class="basis-1/3">
          <Button
              :disabled="!selectedNumWeek"
              @click="_nextWeek"
          >Semaine suivante
          </Button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="selectedWeek">
    <div class="flex flex-row flex-wrap mt-3">
      <div class="basis-1/2">
        <h2 class="mt-4">

          Emploi du temps pour la semaine N°
          <Badge :value="selectedWeek.week"/>
          (du {{ formatDate(selectedWeek.days[0].date) }} au {{ formatDate(selectedWeek.days[4].date) }})
        </h2>
      </div>
      <div class="basis-1/2">
      </div>
    </div>
  <div class="grid-container mt-2" v-for="day in days" :key="day.day">
    <!-- En-tête du jour -->
    <div class="grid-day">{{ day.day }} - {{ formatDate(day.date) }}</div>

    <!-- Colonnes des semestres -->
    <div class="grid-header grid-time">Heure</div>
    <div
        v-for="semestre in selectedWeek.semesters"
        :key="semestre"
        class="grid-header"
        :style="{ backgroundColor: semesters[semestre].color }"
    >
      {{ semestre }}
    </div>
    <!-- Ligne pour indiquer le type de la journée -->
    <div class="grid-header grid-time">Journée</div>
    <div
        class="grid-header"
        v-for="semestre in selectedWeek.semesters"
        :style="{ backgroundColor: getCouleurParDayType(day, semestre) }"
        @click="changerTypeJour(day, semestre)"
        :title="'Type actuel : ' + getTypeJour(day, semestre)"
    >
      {{ getTypeJour(day, semestre) }}
    </div>
    <!-- Créneaux horaires -->
    <template v-for="time in timeSlots" :key="time">
      <div class="grid-time">{{ time }}</div>
      <div
          v-for="semestre in selectedWeek.semesters"
          :key="'time-' + semestre"
          class="grid-cell"
          :style="{ backgroundColor: getCouleurParType(day.day, time, semestre) }"
          @click="changerTypeCreneau(day.day, time, semestre)"
          :title="'Type actuel : ' + (getType(day.day, time, semestre))"
      >
        {{ getType(day.day, time, semestre) }}
      </div>
    </template>
  </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: ['authenticated'],
})

import Button from 'primevue/button'
import Select from 'primevue/select'

import { ref, computed } from 'vue'
import { fetchWeek, fetchWeeks } from '~/services/weeks.js'
import { fetchAllConfig } from '~/services/configGlobale.js'
import { fetchEventsByWeek } from '~/services/events.js'

const configEnv = useRuntimeConfig()
const baseUrl = configEnv.public.apiBaseUrl

const selectedWeek = ref(null)
const selectedNumWeek = ref(1)
const weeks = ref([])
const semesters = ref(null)
const config = ref(null)
const days = ref([])

const timeSlots = ref(['8h00', '9h30', '11h00', '14h00', '15h30', '17h00'])

const placedCourses = ref({})
const size = ref(0)

onMounted(async () => {
      // Simulate fetching weeks data-GEA
      try {
        weeks.value = await fetchWeeks()
        config.value = await fetchAllConfig()
        semesters.value = await config.value.semesters
        Object.values(semesters.value).forEach((semestre) => {
          size.value += 1
        })
        await _loadWeek()
      } catch (error) {
        console.error('Erreur lors de la récupération des semaines:', error)
      }
    }
)

const getType = computed(() => (day, time, semester) => {
  const cellKey = `${day}_${time}_${semester}`;
  return placedCourses.value[cellKey] ? placedCourses.value[cellKey].nom || '' : '';
})

const _loadWeek = async () => {
  try {
    await _getWeek()
    placedCourses.value = {}
    const event = await fetchEventsByWeek(selectedNumWeek.value)
    // parcourir les event pour construire placedCourses
    event.forEach((e) => {
      //créneau est un tableau, à parcourir pour placer l'événement
      if (Array.isArray(e.creneaux)) {
        e.creneaux.forEach((creneau) => {
          const cellKey = `${e.jour}_${convertToHeureText(creneau)}_${e.semester}`;
          placedCourses.value[cellKey] = e;
        });
      } else {
        // Si c'est un seul créneau, on le place directement
        const cellKey = `${e.jour}_${e.creneau}_${e.semester}`;
        placedCourses.value[cellKey] = e;
      }
    });

    console.log('placedCourses:', placedCourses.value)
  } catch (error) {
    console.error('Erreur lors de la récupération des semaines:', error)
  }
}

const _getWeek = async () => {
  selectedWeek.value = await fetchWeek(selectedNumWeek.value)
  days.value = selectedWeek.value.days
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

// Types possibles pour les créneaux et journées
const typesCase = [
  { nom: '', couleur: '#ffffff' }, // Disponible
  { nom: 'entreprise', couleur: '#add8e6' },
  { nom: 'soutenances', couleur: '#dda0dd' },
  { nom: 'banalisé', couleur: '#ffeb3b' },
  { nom: 'férié', couleur: '#ffcccb' },
  { nom: 'vacances', couleur: '#90ee90' }
]

// Fonction pour récupérer la couleur associée à un type
const getCouleurParType = computed(() =>(day, time, semester) => {
  console.log('coucou', day, time, semester)
  const cellKey = `${day}_${time}_${semester}`;

  // Vérifie si la clé existe dans placedCourses
  if (!placedCourses.value[cellKey]) {
    return '#ffffff'; // Couleur par défaut (blanc) si la clé n'existe pas
  }

  const type = placedCourses.value[cellKey].nom || '';
  const typeInfo = typesCase.find((t) => t.nom === type);
  return typeInfo ? typeInfo.couleur : '#ffffff'; // Retourne la couleur associée ou blanc par défaut
});

const getCouleurParDayType = (day, semester) => {
  const dayKey = `${day.day}_${semester}`;

  // Vérifie si la clé existe dans placedCourses
  if (!placedCourses.value[dayKey]) {
    return '#ffffff'; // Couleur par défaut (blanc) si la clé n'existe pas
  }

  const type = placedCourses.value[dayKey].nom || '';
  const typeInfo = typesCase.find((t) => t.nom === type);
  return typeInfo ? typeInfo.couleur : '#ffffff'; // Retourne la couleur associée ou blanc par défaut
};

// Fonction pour changer le type d'une journée
const changerTypeJour = (day, semester) => {
  const dayKey = `${day.day}_${semester}`;

  // Vérifie si la clé existe, sinon initialise-la
  if (!placedCourses.value[dayKey]) {
    placedCourses.value[dayKey] = { nom: '' }; // Valeur par défaut
  }

  // Change le type cycliquement
  const currentType = placedCourses.value[dayKey].nom || '';
  const currentIndex = typesCase.findIndex((t) => t.nom === currentType);
  const newType = typesCase[(currentIndex + 1) % typesCase.length].nom;
  placedCourses.value[dayKey].nom = newType;
  console.log(placedCourses.value)

  // Met à jour tous les créneaux de la journée pour ce semestre
  timeSlots.value.forEach((time) => {
    const slotKey = `${day.day}_${time}_${semester}`;
    if (!placedCourses.value[slotKey]) {
      placedCourses.value[slotKey] = { nom: '' }; // Valeur par défaut
    }
    placedCourses.value[slotKey].nom = newType;
  });

  // Envoi des données à l'API
  envoyerType({
    type: 'jour',
    jour: day.day,
    semestre: semester,
    semaine: selectedNumWeek.value,
    nouveauType: newType,
  });
};

const getTypeJour = (day, semester) => {
  const dayKey = `${day.day}_${semester}`;
  return placedCourses.value[dayKey] ? placedCourses.value[dayKey].nom || '' : '';
}

// Fonction pour changer le type d'un créneau
const changerTypeCreneau = (day, time, semester) => {
  const cellKey = `${day}_${time}_${semester}`;

  // Vérifie si la clé existe, sinon initialise-la
  if (!placedCourses.value[cellKey]) {
    placedCourses.value[cellKey] = { nom: '' }; // Valeur par défaut
  }

  const currentType = placedCourses.value[cellKey].nom || '';
  const currentIndex = typesCase.findIndex((t) => t.nom === currentType);
  const newType = typesCase[(currentIndex + 1) % typesCase.length].nom;
  placedCourses.value[cellKey].nom = newType;

  // Envoi des données à l'API
  envoyerType({
    type: 'creneau',
    jour: day,
    creneau: convertToHeureInt(time),
    semestre: semester,
    semaine: selectedNumWeek.value,
    nouveauType: newType,
  });
};

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: '2-digit'
  }).format(date)
}

const envoyerType = async (data) => {
  try {
    const response = await fetch(`${baseUrl}/calendrier/updateType`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      console.error('Erreur lors de l\'envoi des données à l\'API');
    }
  } catch (error) {
    console.error('Erreur réseau ou serveur :', error);
  }
};

</script>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: 100px repeat(v-bind(size), 1fr);
  gap: 0;
  width: 100%;
  border: 1px solid #000;
}

.grid-day {
  grid-column: span v-bind(size+1);
  background-color: #137C78;
  text-align: center;
  font-weight: bold;
}

.grid-header {
  background-color: #33B3B2;
  text-align: center;
  padding: 8px;
  font-weight: bold;
  border: 1px solid #000;
  grid-column: span 1;
}

.grid-time {
  text-align: center;
  padding: 8px;
  background-color: #33B3B2;
  border: 1px solid #000;
  grid-column: span 1;
}

.grid-cell {
  text-align: center;
  font-size: 9px;
  min-width: 50px;
  padding: 2px;
  border: 1px solid #000;
  background-color: #fff;
  grid-column: span 1;
}

.grid-cell.highlight {
  background-color: #d1e7dd;
}

.grid-cell.highlight-same-course {
  background-color: #ffeb3b !important; /* Highlight color */
}


.remove-btn {
  background: none;
  border: none;
  color: red;
  cursor: pointer;
  font-size: 16px;
  margin-left: 8px;
}

.row {
  position: relative;
}

.list-group-item {
  padding: 10px;
  border-bottom: 1px solid #ddd;
}

.grid-container-replace {
  display: grid;
  grid-template-columns: repeat(8, 1fr); /* Adjust the number of columns as needed */
  gap: 3px;
  min-height: 50px;
}

.grid-item-replace {
  padding: 2px;
  font-size: 9px;
  border: 1px solid #000;
  background-color: #fff;
  text-align: center;
}

.course-replace {
  display: block;
  padding: 8px;
}

.grid-cell.highlight-mandatory {
  background-color: #E69797; /* Rouge pour les contraintes obligatoires */
}

.grid-cell.highlight-optional {
  background-color: #ffffcc; /* Jaune pour les contraintes facultatives */
}

.modal {
  display: block;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgb(0, 0, 0);
  background-color: rgba(0, 0, 0, 0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: 15% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 80%;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: black;
  text-decoration: none;
  cursor: pointer;
}

#edt, #courses {
  max-height: 170vh; /* ou une hauteur fixe, ex: 600px */
  overflow-y: auto;
}

#dropToReport {
  min-height: 60px;
  border: 2px dashed #33B3B2;
  background-color: #f5fafd;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #33B3B2;
  font-size: 1rem;
  transition: background 0.2s, border-color 0.2s;
}

#dropToReport.dragover {
  background-color: #e0f7fa;
  border-color: #ff212e;
  color: #ff212e;
}
</style>
