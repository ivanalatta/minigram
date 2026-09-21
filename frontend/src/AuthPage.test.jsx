import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import AuthPage from './AuthPage'
import { getToken } from './api'
import { jsonResponse, mockFetch } from './test-utils'

describe('AuthPage', () => {
  it('arranca en modo login y cambia a registro', async () => {
    render(<AuthPage onLogin={vi.fn()} />)
    expect(screen.getByText('Iniciar sesión')).toBeInTheDocument()
    expect(screen.queryByPlaceholderText('Email')).not.toBeInTheDocument()

    await userEvent.click(screen.getByText('¿No tenés cuenta? Registrate'))

    expect(screen.getByText('Crear cuenta')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument()
  })

  it('con login exitoso guarda el token y avisa con el usuario', async () => {
    const onLogin = vi.fn()
    mockFetch(
      jsonResponse({ access_token: 'jwt123', token_type: 'bearer' }),
      jsonResponse({ id: 1, username: 'ana', email: 'ana@test.com' }),
    )
    render(<AuthPage onLogin={onLogin} />)

    await userEvent.type(screen.getByPlaceholderText('Usuario'), 'ana')
    await userEvent.type(screen.getByPlaceholderText('Contraseña'), 'secreta1')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(getToken()).toBe('jwt123')
    expect(onLogin).toHaveBeenCalledWith(
      expect.objectContaining({ username: 'ana' }),
    )
  })

  it('muestra el error del backend si el login falla', async () => {
    mockFetch(jsonResponse({ detail: 'Usuario o contraseña incorrectos' }, 401))
    render(<AuthPage onLogin={vi.fn()} />)

    await userEvent.type(screen.getByPlaceholderText('Usuario'), 'ana')
    await userEvent.type(screen.getByPlaceholderText('Contraseña'), 'malmalmal')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(
      await screen.findByText('Usuario o contraseña incorrectos'),
    ).toBeInTheDocument()
  })
})
