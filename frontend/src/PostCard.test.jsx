import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import PostCard from './PostCard'
import { jsonResponse, makePost, mockFetch } from './test-utils'

const ana = { id: 1, username: 'ana', email: 'ana@test.com' }

describe('PostCard', () => {
  it('al dar like avisa con el post actualizado', async () => {
    const onChange = vi.fn()
    mockFetch(jsonResponse({ like_count: 1, liked_by_me: true }))
    render(
      <PostCard
        post={makePost()}
        currentUser={ana}
        onChange={onChange}
        onDelete={vi.fn()}
      />,
    )

    await userEvent.click(screen.getByRole('button', { name: /♡/ }))

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ id: 1, like_count: 1, liked_by_me: true }),
    )
  })

  it('al comentar agrega el comentario que devolvió el API', async () => {
    const onChange = vi.fn()
    mockFetch(
      jsonResponse(
        { id: 7, text: 'genial', username: 'ana', created_at: '2026-09-21T15:00:00Z' },
        201,
      ),
    )
    render(
      <PostCard
        post={makePost()}
        currentUser={ana}
        onChange={onChange}
        onDelete={vi.fn()}
      />,
    )

    await userEvent.type(
      screen.getByPlaceholderText('Agregar un comentario...'),
      'genial',
    )
    await userEvent.click(screen.getByRole('button', { name: 'Enviar' }))

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({
        comments: [expect.objectContaining({ text: 'genial' })],
      }),
    )
  })

  it('muestra Borrar solo al autor del post', () => {
    const { rerender } = render(
      <PostCard
        post={makePost({ author: 'ana' })}
        currentUser={ana}
        onChange={vi.fn()}
        onDelete={vi.fn()}
      />,
    )
    expect(screen.getByText('Borrar')).toBeInTheDocument()

    rerender(
      <PostCard
        post={makePost({ author: 'eva' })}
        currentUser={ana}
        onChange={vi.fn()}
        onDelete={vi.fn()}
      />,
    )
    expect(screen.queryByText('Borrar')).not.toBeInTheDocument()
  })
})
