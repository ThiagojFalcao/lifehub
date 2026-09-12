export async function api(path, options = {}) {
  const { body, ...rest } = options
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...rest,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    throw new Error(`${res.status} ${(await res.text()).slice(0, 200)}`)
  }
  return res.json()
}