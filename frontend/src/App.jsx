import { useEffect, useState } from 'react'
import './App.css'

// URL del backend: viene de una variable de entorno para poder
// cambiarla en producción sin tocar el código.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [apiStatus, setApiStatus] = useState('conectando...')

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then((data) => setApiStatus(data.status === 'ok' ? 'conectada ✅' : 'error'))
      .catch(() => setApiStatus('sin conexión ❌'))
  }, [])

  return (
    <main>
      <h1>Minigram</h1>
      <p>Esqueleto del proyecto — Fase 0</p>
      <p>
        API: <strong>{apiStatus}</strong>
      </p>
    </main>
  )
}

export default App
