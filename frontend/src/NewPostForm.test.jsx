import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import NewPostForm from './NewPostForm'
import { jsonResponse, makePost, mockFetch } from './test-utils'

describe('NewPostForm', () => {
  it('exige elegir una imagen antes de publicar', async () => {
    const fetchMock = mockFetch()
    render(<NewPostForm onCreated={vi.fn()} />)

    await userEvent.click(screen.getByRole('button', { name: 'Publicar' }))

    expect(screen.getByText('Elegí una imagen para publicar')).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('publica la imagen y avisa con el post nuevo', async () => {
    const onCreated = vi.fn()
    mockFetch(jsonResponse(makePost({ caption: 'desde el test' }), 201))
    render(<NewPostForm onCreated={onCreated} />)

    const archivo = new File(['fake-png'], 'foto.png', { type: 'image/png' })
    await userEvent.upload(document.querySelector('input[type="file"]'), archivo)
    await userEvent.type(
      screen.getByPlaceholderText('Escribí un caption...'),
      'desde el test',
    )
    await userEvent.click(screen.getByRole('button', { name: 'Publicar' }))

    expect(onCreated).toHaveBeenCalledWith(
      expect.objectContaining({ caption: 'desde el test' }),
    )
  })
})
