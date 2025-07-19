<script setup>
import { computed } from 'vue'

const props = defineProps({
  course: {
    type: Object,
    default: null
  },
  day: {
    type: String,
    required: true
  },
  time: {
    type: String,
    required: true
  },
  semestre: {
    type: String,
    required: true
  },
  group: {
    type: String,
    required: true
  },
  cellKey: {
    type: String,
    required: true
  },
  displayCourse: {
    type: Function,
    required: true
  }
})

const emit = defineEmits([
  'drag-start',
  'drop',
  'mouseover',
  'mouseout',
  'edit-room',
  'remove-course',
  'dragend'
])

const hasCourse = computed(() => !!props.course)

function onDragStart (event) {
  if (props.course) {
    emit('drag-start', event, props.course, 'grid', props.cellKey)
  }
}

function onDrop (event) {
  emit('drop', event, props.day, props.time, props.semestre, props.group)
}

function onMouseOver () {
  emit('mouseover', props.day, props.time, props.semestre, props.group)
}

function onMouseOut () {
  emit('mouseout', props.day, props.time, props.semestre, props.group)
}

function editRoom () {
  if (props.course) {
    emit('edit-room', props.course)
  }
}

function removeCourse () {
  if (props.course) {
    emit('remove-course', props.day, props.time, props.semestre, props.group, props.course.groupCount)
  }
}
</script>

<template>
  <div
      class="grid-cell"
      @drop="onDrop"
      @mouseover="onMouseOver"
      @mouseout="onMouseOut"
      @dragover.prevent
      :data-key="cellKey"
      draggable="true"
      @dragstart="onDragStart"
      @dragend="$emit('dragend')"
  >
    <span v-if="hasCourse">
      <span v-html="displayCourse(course)"></span><br>
      <span v-if="course.blocked === false" @click="editRoom">
        -{{ course.room }}-
      </span><br>
      <Button
          v-if="course.blocked === false"
          rounded
          class="mt-1"
          severity="danger"
          @click="removeCourse"
      >
        <Icon name="prime:trash"/>
      </Button>
      <Button
          v-if="course.blocked === false"
          rounded
          class="ms-2 mt-1"
          severity="warn"
          @click="editRoom"
      >
        <Icon name="prime:pen-to-square"/>
      </Button>
    </span>
  </div>
</template>
