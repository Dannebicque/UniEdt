// composables/useGroupUtils.js

export function groupToInt(group) {
  // convert group letter to number
  return group.charCodeAt(0) - 64
}

export function groupToText(group) {
  // convert group number to letter
  return String.fromCharCode(64 + group)
}

export function incrementGroupNumber(groupNumber, i) {
  //groupeNumber peut être un nombre ou une lettre, donc on gère les deux cas, on retourne le groupe suivant au format lettre
  if (typeof groupNumber === 'number') {
    return groupNumber + i
  } else if (typeof groupNumber === 'string') {
    return String.fromCharCode(groupNumber.charCodeAt(0) + i)
  }
}
