<template>
  <h1>Intervenants</h1>
  <Button label="Ajouter" icon="pi pi-plus" class="mb-3" severity="success"
          @click="openAddDialog"/>
  <div v-if="intervenants">
    <DataTable :value="intervenants"
               sortField="name"
               :sortOrder="1"
               :paginator="true"
               :rows="30"
               :rowsPerPageOptions="[5, 10, 20]"
               :loading="!intervenants.length"
               class="mt-4">
      <Column field="name" header="Prénom Nom" :sortable="true" />
      <Column field="type" header="Statut" sortable >
        <template #body="slotProps">
          <Badge
              class="badge"
              :value="slotProps.data.type"
              :severity="slotProps.data.type === 'permanent' ? 'success' : 'info'"
          />
        </template>
      </Column>
      <Column field="service" header="Service"/>
      <Column field="key" header="Abbr."/>
      <Column field="email" header="Email"/>
      <Column header="Actions">
        <template #body="slotProps">
          <Button rounded severity="info" @click="selectedIntervenant = slotProps.data; showDialog = true">
            <Icon name="prime:eye"/>
          </Button>
          <Button rounded severity="warn" @click="openEditDialog(slotProps.data)" class="ms-2">
            <Icon name="prime:pen-to-square"/>
          </Button>
        </template>
      </Column>
    </DataTable>
  </div>

  <Dialog v-model:visible="showDialog" header="Détail Intervenant" :modal="true" :closable="true"
          :style="{ width: '400px' }">
    <div v-if="selectedIntervenant">
      <p><b>Nom :</b> {{ selectedIntervenant.name }}</p>
      <p><b>Statut :</b> {{ selectedIntervenant.type }}</p>
      <p><b>Abbr. :</b> {{ selectedIntervenant.key }}</p>
      <p><b>Email :</b> {{ selectedIntervenant.email }}</p>
      <p><b>Service :</b> {{ selectedIntervenant.service }}</p>
    </div>
  </Dialog>

  <Dialog v-model:visible="editDialog" :header="isEdit ? 'Éditer Intervenant' : 'Ajouter Intervenant'"
          :modal="true" :closable="true" :style="{ width: '400px' }">
    <div v-if="editIntervenant">
      <div class="mb-3 flex flex-col gap-2">
        <label for="nom">Nom</label>
        <InputText id="nom" v-model="editIntervenant.name" class="mb-2"/>
      </div>
      <div class="mb-3 flex flex-col gap-2">
        <label for="statut">Statut</label>
        <Select id="statut" v-model="editIntervenant.type" class="mb-2"
                :options="[
          { label: 'Permanent', value: 'permanent' },
          { label: 'Vacataire', value: 'vacataire' }
        ]"
                optionLabel="label" optionValue="value" placeholder="Sélectionner un statut"
        />
      </div>
      <div class="mb-3 flex flex-col gap-2">
        <label for="abbr">Abbr.</label>
        <InputText id="abbr" v-model="editIntervenant.key" class="mb-2"/>
      </div>
      <div class="mb-3 flex flex-col gap-2">
        <label for="service">Service</label>
        <InputText id="service" v-model="editIntervenant.service" class="mb-2"/>
      </div>
      <div class="mb-3 flex flex-col gap-2">
        <label for="email">Email</label>
        <InputText id="email" v-model="editIntervenant.email" class="mb-2"/>
      </div>
      <div class="mt-3">
        <Button :label="isEdit ? 'Enregistrer' : 'Ajouter'" @click="saveEdit" severity="success"/>
        <Button label="Annuler" @click="editDialog = false" severity="secondary" class="ms-2"/>
      </div>
    </div>
  </Dialog>

</template>

<script setup>
definePageMeta({
  middleware: ['authenticated'],
})

// Récupérer la liste des intervenants depuis l'API
import { onMounted, ref } from 'vue'
import { addIntervenant, fetchIntervenantsComplets, updateIntervenant } from '@/services/intervenants'

const intervenants = ref([])
const showDialog = ref(false)
const selectedIntervenant = ref(null)
const editDialog = ref(false)
const editIntervenant = ref(null)
const isEdit = ref(false)
const initialKey = ref(null)

onMounted(async () => {
  try {
    const data = await fetchIntervenantsComplets()
    intervenants.value = Array.isArray(data) ? data : Object.values(data)

  } catch (error) {
    console.error('Erreur lors de la récupération des intervenants:', error)
  }
})

const openAddDialog = () => {
  editIntervenant.value = { name: '', type: '', key: '', email: '' }
  isEdit.value = false
  editDialog.value = true
}

const openEditDialog = (intervenant) => {
  initialKey.value = intervenant.key
  editIntervenant.value = { ...intervenant }
  isEdit.value = true
  editDialog.value = true
}

const saveEdit = async () => {
  if (isEdit.value) {
    // Logique de modification (API ou local)
    const response = await updateIntervenant(initialKey.value, editIntervenant.value).then(
        (res) => res.data,
        (error) => {
          console.error('Erreur lors de la modification de l\'intervenant:', error)
          return null
        }
    )
    // Mettre à jour l'intervenant dans la liste
    const index = intervenants.value.findIndex(i => i.key === initialKey.value)
    if (index !== -1) {
      intervenants.value[index] = { ...editIntervenant.value }
    }
  } else {
    editIntervenant.value.availability = []
    // Logique d'ajout (API ou local)
    const response = await addIntervenant(editIntervenant.value).then(
        (res) => res.data,
        (error) => {
          console.error('Erreur lors de l\'ajout de l\'intervenant:', error)
          return null
        }
    )
    intervenants.value.push({ ...editIntervenant.value })
  }
  editDialog.value = false
}

</script>
