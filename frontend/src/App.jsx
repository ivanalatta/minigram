import { useEffect, useState } from 'react'
import './App.css'
import { apiFetch, clearToken, getToken } from './api'
import AuthPage from './AuthPage'
import Feed from './Feed'

function App() {
  const [user, setUser] = useState(null)
  const [checkingSession, setCheckingSession] = useState(() => Boolean(getToken()))

  useEffect(() => {
    if (!getToken()) return
    apiFetch('/auth/me')
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setCheckingSession(false))
  }, [])

  function handleLogout() {
    clearToken()
    setUser(null)
  }

  if (checkingSession) return null

  return (
    <>
      <header className="topbar">
        <h1>Minigram</h1>
        {user && (
          <div className="topbar-user">
            <span>@{user.username}</span>
            <button onClick={handleLogout}>Salir</button>
          </div>
        )}
      </header>
      <main>
        {user ? <Feed currentUser={user} /> : <AuthPage onLogin={setUser} />}
      </main>
    </>
  )
}

export default App
