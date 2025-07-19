<script setup>
import { computed, ref } from 'vue'
import CourseCell from './CourseCell.vue'

const props = defineProps({
  size: {
    type: Number,
    required: true
  },
  days: {
    type: Array,
    required: true
  },
  timeSlots: {
    type: Array,
    required: true
  },
  selectedWeek: {
    type: Object,
    required: true
  },
  semesters: {
    type: Object,
    required: true
  },
  placedCourses: {
    type: Object,
    required: true
  },
  displayCourse: {
    type: Function,
    required: true
  },
  getColorBySemestreAndType: {
    type: Function,
    required: true
  }
})

const emit = defineEmits([
  'drag-start',
  'drop',
  'mouseover',
  'mouseout',
  'dragend',
  'edit-room',
  'remove-course'
])

const size = ref(0)


function listeGroupesTp(semestre) {
  if (!props.selectedWeek || !semestre) return []
  if (!props.semesters[semestre]) return []

  return props.semesters[semestre].groupesTp
}

function onDragStart(event, course, source, originSlot) {
  emit('drag-start', event, course, source, originSlot)
}

function onDrop(event, day, time, semestre, group) {
  emit('drop', event, day, time, semestre, group)
}

function onMouseOver(day, time, semestre, group) {
  emit('mouseover', day, time, semestre, group)
}

function onMouseOut(day, time, semestre, group) {
  emit('mouseout', day, time, semestre, group)
}

function onDragEnd() {
  emit('dragend')
}

function onEditRoom(course) {
  emit('edit-room', course)
}

function onRemoveCourse(day, time, semestre, group, groupCount) {
  emit('remove-course', day, time, semestre, group, groupCount)
}

function getCellStyle(day, time, semestre, group) {
  const key = `${day}_${time}_${semestre}_${group}`
  const course = props.placedCourses[key]

  if (course) {
    return {
      backgroundColor: props.getColorBySemestreAndType(course.color, course.type)
    }
  }

  return {}
}
</script>

<template>
  <div>
    <div class="grid-container mt-2" v-for="day in days" :key="day.day">
      <div class="grid-day">{{ day.day }} {{ day.dateFr }}</div>
      <!-- Header Row: Semesters -->
      <div class="grid-header grid-time">Heure</div>

      <div
          v-for="semestre in selectedWeek.semesters"
          :key="semestre"
          class="grid-header"
          :style="{ gridColumn: `span  ${listeGroupesTp(semestre).length}`, backgroundColor: semesters[semestre].color }"
      >
        {{ semestre }}
      </div>

      <!-- Second Row: Group Headers -->
      <div class="grid-time"></div>
      <template v-for="semestre in selectedWeek.semesters" :key="'group-' + semestre">
        <div
            v-for="group in listeGroupesTp(semestre)"
            :key="semestre + group"
            class="grid-header"
            :style="{ backgroundColor: semesters[semestre].color }"
        >
          {{ group }}
        </div>
      </template>

      <!-- Time Slots and Group Cells -->
      <template v-for="time in timeSlots" :key="time">
        <div class="grid-time">{{ time }}</div>
        <template v-for="semestre in selectedWeek.semesters" :key="'time-' + semestre">
          <CourseCell
            v-for="group in listeGroupesTp(semestre)"
            :key="time + semestre + group"
            :course="placedCourses[`${day.day}_${time}_${semestre}_${group}`]"
            :day="day.day"
            :time="time"
            :semestre="semestre"
            :group="group"
            :cell-key="`${day.day}_${time}_${semestre}_${group}`"
            :display-course="displayCourse"
            :style="getCellStyle(day.day, time, semestre, group)"
            @drag-start="onDragStart"
            @drop="onDrop"
            @mouseover="onMouseOver"
            @mouseout="onMouseOut"
            @dragend="onDragEnd"
            @edit-room="onEditRoom"
            @remove-course="onRemoveCourse"
          />
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: 100px repeat(v-bind(props.size), 1fr);
  gap: 0;
  width: 100%;
  border: 1px solid #000;
}

.grid-day {
  grid-column: span v-bind(props.size+1);
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
</style>
