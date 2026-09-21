import { useRef, useState } from 'react'
import { apiFetch } from '../services/api'

function NewPostForm({ onCreated }) {
  const [caption, setCaption] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

  async function handleSubmit(e) {
    e.preventDefault()
    const file = fileInputRef.current.files[0]
    if (!file) {
      setError('Elegí una imagen para publicar')
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('La imagen supera el máximo de 5 MB')
      return
    }
    setError('')
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('caption', caption)
      formData.append('image', file)
      const newPost = await apiFetch('/posts', { method: 'POST', body: formData })
      onCreated(newPost)
      setCaption('')
      fileInputRef.current.value = ''
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="new-post" onSubmit={handleSubmit}>
      <input
        type="file"
        ref={fileInputRef}
        accept="image/jpeg,image/png,image/webp"
      />
      <input
        type="text"
        placeholder="Escribí un caption..."
        value={caption}
        onChange={(e) => setCaption(e.target.value)}
        maxLength={500}
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Publicando...' : 'Publicar'}
      </button>
    </form>
  )
}

export default NewPostForm
