<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  course: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:isOpen', 'save'])

const localIsOpen = ref(props.isOpen)
const localCourse = ref(props.course ? { ...props.course } : null)

watch(() => props.isOpen, (newVal) => {
  localIsOpen.value = newVal
})

watch(() => props.course, (newVal) => {
  if (newVal) {
    localCourse.value = { ...newVal }
  }
})

function updateVisibility(value) {
  localIsOpen.value = value
  emit('update:isOpen', value)
}

function saveRoom() {
  emit('save', localCourse.value)
  updateVisibility(false)
}
</script>

<template>
  <Dialog :visible="localIsOpen" :closable="true" modal
          @update:visible="updateVisibility($event)"
          header="Modifier l'événement">
    <template v-if="localCourse">
      <p><strong>Cours:</strong> {{ localCourse.matiere }}</p>
      <p><strong>Professeur:</strong> {{ localCourse.professor }}</p>
      <p><strong>Créneau:</strong> {{ localCourse.date }} {{ localCourse.creneau }}</p>
      <label for="room">Salle:</label>
      <input type="text" v-model="localCourse.room" id="room"/>
      <button @click="saveRoom">Enregistrer</button>
    </template>
  </Dialog>
</template>
