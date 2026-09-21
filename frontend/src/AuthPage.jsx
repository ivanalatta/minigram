import { useState } from 'react'
import { apiFetch, setToken } from './api'

function AuthPage({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'register') {
        await apiFetch('/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password }),
        })
      }
      const data = await apiFetch('/auth/token', {
        method: 'POST',
        body: new URLSearchParams({ username, password }),
      })
      setToken(data.access_token)
      const me = await apiFetch('/auth/me')
      onLogin(me)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function switchMode() {
    setMode(mode === 'login' ? 'register' : 'login')
    setError('')
  }

  return (
    <div className="auth-card">
      <h2>{mode === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          minLength={3}
          maxLength={30}
        />
        {mode === 'register' && (
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        )}
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Un momento...' : mode === 'login' ? 'Entrar' : 'Registrarme'}
        </button>
      </form>
      <button className="link-button" onClick={switchMode}>
        {mode === 'login'
          ? '¿No tenés cuenta? Registrate'
          : '¿Ya tenés cuenta? Iniciá sesión'}
      </button>
    </div>
  )
}

export default AuthPage
