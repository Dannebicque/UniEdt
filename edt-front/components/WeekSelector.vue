<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  selectedWeek: {
    type: Object,
    default: null
  },
  weeks: {
    type: Array,
    required: true
  },
  selectedNumWeek: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:selectedNumWeek', 'load-week', 'previous-week', 'next-week'])

const localSelectedNumWeek = ref(props.selectedNumWeek)

watch(() => props.selectedNumWeek, (newVal) => {
  localSelectedNumWeek.value = newVal
})

function onWeekChange() {
  emit('update:selectedNumWeek', localSelectedNumWeek.value)
  emit('load-week')
}

function previousWeek() {
  if (localSelectedNumWeek.value > 1) {
    emit('previous-week')
  }
}

function nextWeek() {
  if (localSelectedNumWeek.value < 53) {
    emit('next-week')
  }
}
</script>

<template>
  <div class="flex flex-row flex-wrap">
    <div class="basis-1/3">
      <Button
          :disabled="!localSelectedNumWeek"
          @click="previousWeek"
      >Semaine précédente
      </Button>
    </div>
    <div class="basis-1/3">
      <Select v-model="localSelectedNumWeek" :options="weeks"
              optionLabel="label"
              @change="onWeekChange"
              filter
              optionValue="value"
              placeholder="Sélectionner une semaine"
              class="w-full md:w-56"/>
    </div>
    <div class="basis-1/3">
      <Button
          :disabled="!localSelectedNumWeek"
          @click="nextWeek"
      >Semaine suivante
      </Button>
    </div>
  </div>
</template>
