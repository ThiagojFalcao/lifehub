/** Cliente HTTP da API do LifeHub. */
export async function api(path, options = {}) {
  const { body, ...rest } = options
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...rest,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    throw new Error(await mensagemDeErro(res))
  }
  return res.json()
}

/**
 * Extrai o motivo real do erro. O FastAPI responde `{"detail": "..."}` para erros
 * de negócio (ex.: métrica inválida) e uma lista de objetos para erros de
 * validação do Pydantic. Mostrar `422 {...}` cru não diz nada ao usuário.
 */
async function mensagemDeErro(res) {
  const texto = await res.text()
  try {
    const corpo = JSON.parse(texto)
    const { detail } = corpo
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((d) => {
          const campo = (d.loc || []).filter((p) => p !== 'body').join('.')
          return campo ? `${campo}: ${d.msg}` : d.msg
        })
        .join('; ')
    }
  } catch {
    // resposta não-JSON (ex.: 500 do proxy): cai no texto cru
    return texto.slice(0, 200) || `HTTP ${res.status}`
  }
  return texto.slice(0, 200) || `HTTP ${res.status}`
}
