import { vi } from 'vitest'

export function jsonResponse(data, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
  }
}

export function mockFetch(...responses) {
  const fn = vi.fn()
  for (const r of responses) fn.mockResolvedValueOnce(r)
  vi.stubGlobal('fetch', fn)
  return fn
}

export function makePost(overrides = {}) {
  return {
    id: 1,
    caption: 'un atardecer',
    image_url: '/uploads/foto.png',
    created_at: '2026-09-21T15:00:00Z',
    author: 'ana',
    like_count: 0,
    liked_by_me: false,
    comments: [],
    ...overrides,
  }
}
