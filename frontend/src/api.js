// En producción VITE_API_URL es "" (mismo dominio, nginx hace de proxy)
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export function getToken() {
  return localStorage.getItem('token')
}

export function setToken(token) {
  localStorage.setItem('token', token)
}

export function clearToken() {
  localStorage.removeItem('token')
}

export function imageUrl(path) {
  return `${API_URL}${path}`
}

export async function apiFetch(path, options = {}) {
  const headers = { ...options.headers }
  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers })

  if (res.status === 401 && token && path !== '/auth/token') {
    clearToken()
    window.location.reload()
    throw new Error('Tu sesión expiró')
  }

  if (res.status === 204) return null

  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const detail = data?.detail
    let message = 'Error inesperado, intentá de nuevo'
    if (typeof detail === 'string') message = detail
    else if (Array.isArray(detail)) message = 'Datos inválidos: revisá el formulario'
    throw new Error(message)
  }
  return data
}
