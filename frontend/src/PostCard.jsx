import { useState } from 'react'
import { apiFetch, imageUrl } from './api'

function PostCard({ post, currentUser, onChange, onDelete }) {
  const [commentText, setCommentText] = useState('')
  const [error, setError] = useState('')

  const isMine = post.author === currentUser.username

  async function toggleLike() {
    setError('')
    try {
      const status = await apiFetch(`/posts/${post.id}/like`, {
        method: post.liked_by_me ? 'DELETE' : 'POST',
      })
      onChange({ ...post, ...status })
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleComment(e) {
    e.preventDefault()
    const text = commentText.trim()
    if (!text) return
    setError('')
    try {
      const comment = await apiFetch(`/posts/${post.id}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })
      onChange({ ...post, comments: [...post.comments, comment] })
      setCommentText('')
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleDelete() {
    if (!window.confirm('¿Borrar este post?')) return
    setError('')
    try {
      await apiFetch(`/posts/${post.id}`, { method: 'DELETE' })
      onDelete(post.id)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <article className="post-card">
      <div className="post-header">
        <strong>@{post.author}</strong>
        <span className="post-date">
          {new Date(post.created_at).toLocaleString()}
        </span>
        {isMine && (
          <button className="link-button" onClick={handleDelete}>
            Borrar
          </button>
        )}
      </div>
      <img src={imageUrl(post.image_url)} alt={post.caption || 'Post'} />
      <div className="post-body">
        <button
          className={post.liked_by_me ? 'like-button liked' : 'like-button'}
          onClick={toggleLike}
        >
          {post.liked_by_me ? '♥' : '♡'} {post.like_count}
        </button>
        {post.caption && (
          <p className="caption">
            <strong>@{post.author}</strong> {post.caption}
          </p>
        )}
        {post.comments.map((c) => (
          <p className="comment" key={c.id}>
            <strong>@{c.username}</strong> {c.text}
          </p>
        ))}
        <form className="comment-form" onSubmit={handleComment}>
          <input
            type="text"
            placeholder="Agregar un comentario..."
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            maxLength={500}
          />
          <button type="submit" disabled={!commentText.trim()}>
            Enviar
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>
    </article>
  )
}

export default PostCard
