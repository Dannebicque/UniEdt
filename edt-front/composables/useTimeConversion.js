// composables/useTimeConversion.js

export function convertToHeureText(time) {
  const tab = [
    '',
    '8h00',
    '9h30',
    '11h00',
    '14h00',
    '15h30',
    '17h00'
  ]

  return tab[time] || ''
}

export function convertToHeureInt(time) {
  const tab = {
    '8h00': 1,
    '9h30': 2,
    '11h00': 3,
    '14h00': 4,
    '15h30': 5,
    '17h00': 6
  }

  return tab[time] || 0
}
