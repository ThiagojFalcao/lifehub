/** Helpers de métricas ricas — compartilhados entre os forms e a lista de Galhos. */

/** Formas vazias para cada métrica declarada (bool começa false, resto ''). */
export function emptyValues(schema = {}) {
  const out = {}
  for (const [nome, tipo] of Object.entries(schema || {})) {
    out[nome] = tipo === 'bool' ? false : ''
  }
  return out
}

/** `<input type>` derivado do tipo declarado no schema do hábito. */
export function inputType(tipo) {
  if (tipo === 'int' || tipo === 'float' || tipo === 'number') return 'number'
  if (tipo === 'bool') return 'checkbox'
  return 'text'
}

export function isNumeric(tipo) {
  return tipo === 'int' || tipo === 'float' || tipo === 'number'
}

/**
 * Remove campos vazios antes do POST: string vazia em métrica numérica viraria
 * 422 no backend, e "não preenchi" é diferente de "preenchi zero".
 */
export function cleanValues(values = {}) {
  const out = {}
  for (const [nome, valor] of Object.entries(values || {})) {
    if (valor === '' || valor === null || valor === undefined) continue
    out[nome] = valor
  }
  return out
}

/** Renderização legível de uma métrica na lista de Galhos. */
export function formatMetric(valor) {
  if (typeof valor === 'boolean') return valor ? 'sim' : 'não'
  if (valor === null || valor === undefined) return '—'
  if (typeof valor === 'object') return JSON.stringify(valor)
  return String(valor)
}

/** `YYYY-MM-DD` de hoje, no fuso local (não UTC — evita virar o dia à noite). */
export function hoje() {
  const d = new Date()
  const mes = String(d.getMonth() + 1).padStart(2, '0')
  const dia = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mes}-${dia}`
}
