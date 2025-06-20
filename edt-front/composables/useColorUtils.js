// composables/useColorUtils.js
export function getColorBySemestreAndType(color, type = 'CM') {
  if (type === 'CM') {
    return color
  } else if (type === 'TD') {
    return lightenColor(color, 0.8)
  } else if (type === 'TP') {
    return lightenColor(color, 0.6)
  }
}

export function lightenColor(color, factor) {
  const rgb = hexToRgb(color)
  const r = Math.min(255, Math.floor(rgb.r * factor))
  const g = Math.min(255, Math.floor(rgb.g * factor))
  const b = Math.min(255, Math.floor(rgb.b * factor))
  return rgbToHex(r, g, b)
}

export function hexToRgb(hex) {
  const bigint = parseInt(hex.slice(1), 16)
  const r = (bigint >> 16) & 255
  const g = (bigint >> 8) & 255
  const b = bigint & 255
  return { r, g, b }
}

export function rgbToHex(r, g, b) {
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`
}
