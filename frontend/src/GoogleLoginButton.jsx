import { useEffect, useRef, useState } from 'react'
import { apiFetch, setToken } from './api'

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
const SCRIPT_URL = 'https://accounts.google.com/gsi/client'

function GoogleLoginButton({ onLogin }) {
  const buttonRef = useRef(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!CLIENT_ID) return

    async function handleCredential(response) {
      setError('')
      try {
        const data = await apiFetch('/auth/google', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ credential: response.credential }),
        })
        setToken(data.access_token)
        const me = await apiFetch('/auth/me')
        onLogin(me)
      } catch (err) {
        setError(err.message)
      }
    }

    function renderButton() {
      if (!buttonRef.current || buttonRef.current.hasChildNodes()) return
      window.google.accounts.id.initialize({
        client_id: CLIENT_ID,
        callback: handleCredential,
      })
      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: 'outline',
        size: 'large',
        text: 'continue_with',
      })
    }

    if (window.google?.accounts) {
      renderButton()
      return
    }
    const existing = document.querySelector(`script[src="${SCRIPT_URL}"]`)
    if (existing) {
      existing.addEventListener('load', renderButton)
      return
    }
    const script = document.createElement('script')
    script.src = SCRIPT_URL
    script.async = true
    script.onload = renderButton
    document.head.appendChild(script)
  }, [onLogin])

  if (!CLIENT_ID) return null

  return (
    <div className="google-login">
      <div className="divider">o</div>
      <div className="google-button" ref={buttonRef} />
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default GoogleLoginButton
