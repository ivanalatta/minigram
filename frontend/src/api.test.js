import { describe, expect, it } from 'vitest'
import { apiFetch, clearToken, getToken, setToken } from './api'
import { jsonResponse, mockFetch } from './test-utils'

describe('token en localStorage', () => {
  it('guarda, lee y borra el token', () => {
    setToken('abc')
    expect(getToken()).toBe('abc')
    clearToken()
    expect(getToken()).toBeNull()
  })
})

describe('apiFetch', () => {
  it('agrega el header Authorization cuando hay token', async () => {
    setToken('mi-token')
    const fetchMock = mockFetch(jsonResponse({ ok: true }))

    await apiFetch('/posts')

    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('http://localhost:8000/posts')
    expect(options.headers.Authorization).toBe('Bearer mi-token')
  })

  it('no agrega Authorization sin token', async () => {
    const fetchMock = mockFetch(jsonResponse({ ok: true }))

    await apiFetch('/posts')

    expect(fetchMock.mock.calls[0][1].headers.Authorization).toBeUndefined()
  })

  it('lanza un Error con el detail que devuelve el backend', async () => {
    mockFetch(jsonResponse({ detail: 'Post no encontrado' }, 404))

    await expect(apiFetch('/posts/999')).rejects.toThrow('Post no encontrado')
  })

  it('convierte los errores de validación en un mensaje legible', async () => {
    mockFetch(jsonResponse({ detail: [{ msg: 'field required' }] }, 422))

    await expect(apiFetch('/auth/register')).rejects.toThrow(
      'Datos inválidos: revisá el formulario',
    )
  })

  it('devuelve null en respuestas 204', async () => {
    mockFetch({ ok: true, status: 204 })

    expect(await apiFetch('/posts/1', { method: 'DELETE' })).toBeNull()
  })

  it('limpia el token si la sesión expiró (401 con token)', async () => {
    setToken('vencido')
    mockFetch(jsonResponse({ detail: 'Token inválido o expirado' }, 401))

    await expect(apiFetch('/auth/me')).rejects.toThrow('Tu sesión expiró')
    expect(getToken()).toBeNull()
  })

  it('un 401 en el login NO recarga: muestra el error normal', async () => {
    mockFetch(jsonResponse({ detail: 'Usuario o contraseña incorrectos' }, 401))

    await expect(apiFetch('/auth/token', { method: 'POST' })).rejects.toThrow(
      'Usuario o contraseña incorrectos',
    )
  })
})
