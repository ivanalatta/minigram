import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import Feed from './Feed'
import { jsonResponse, makePost, mockFetch } from './test-utils'

const ana = { id: 1, username: 'ana', email: 'ana@test.com' }

describe('Feed', () => {
  it('muestra los posts que devuelve el API', async () => {
    mockFetch(
      jsonResponse([
        makePost({ id: 1, caption: 'primer post' }),
        makePost({ id: 2, caption: 'segundo post', author: 'eva' }),
      ]),
    )
    render(<Feed currentUser={ana} />)

    expect(await screen.findByText('primer post')).toBeInTheDocument()
    expect(screen.getByText('segundo post')).toBeInTheDocument()
    expect(screen.getAllByText('@eva').length).toBeGreaterThan(0)
  })

  it('con feed vacío invita a publicar', async () => {
    mockFetch(jsonResponse([]))
    render(<Feed currentUser={ana} />)

    expect(
      await screen.findByText('Todavía no hay posts. ¡Publicá el primero!'),
    ).toBeInTheDocument()
  })

  it('muestra el error si el feed no carga', async () => {
    mockFetch(jsonResponse({ detail: 'Error de base de datos' }, 500))
    render(<Feed currentUser={ana} />)

    expect(await screen.findByText('Error de base de datos')).toBeInTheDocument()
  })
})
