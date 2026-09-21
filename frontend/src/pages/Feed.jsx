import { useEffect, useState } from 'react'
import { apiFetch } from '../services/api'
import NewPostForm from '../components/NewPostForm'
import PostCard from '../components/PostCard'

const PAGE_SIZE = 10

function Feed({ currentUser }) {
  const [posts, setPosts] = useState([])
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch(`/posts?offset=0&limit=${PAGE_SIZE}`)
      .then((page) => {
        setPosts(page)
        setHasMore(page.length === PAGE_SIZE)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  async function loadMore() {
    setLoading(true)
    setError('')
    try {
      const page = await apiFetch(`/posts?offset=${posts.length}&limit=${PAGE_SIZE}`)
      setPosts((prev) => [...prev, ...page.filter((p) => !prev.some((q) => q.id === p.id))])
      setHasMore(page.length === PAGE_SIZE)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleCreated(newPost) {
    setPosts((prev) => [newPost, ...prev])
  }

  function handleChanged(updated) {
    setPosts((prev) => prev.map((p) => (p.id === updated.id ? updated : p)))
  }

  function handleDeleted(postId) {
    setPosts((prev) => prev.filter((p) => p.id !== postId))
  }

  return (
    <div>
      <NewPostForm onCreated={handleCreated} />
      {error && <p className="error">{error}</p>}
      {!loading && posts.length === 0 && !error && (
        <p className="empty">Todavía no hay posts. ¡Publicá el primero!</p>
      )}
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          currentUser={currentUser}
          onChange={handleChanged}
          onDelete={handleDeleted}
        />
      ))}
      {loading && <p className="empty">Cargando...</p>}
      {hasMore && !loading && (
        <button className="load-more" onClick={loadMore}>
          Cargar más
        </button>
      )}
    </div>
  )
}

export default Feed
