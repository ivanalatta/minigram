import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..config import UPLOADS_DIR
from ..database import get_session
from ..models import Comment, Like, Post, User
from ..schemas import CommentCreate, CommentRead, LikeStatus, PostRead
from ..security import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


def to_post_read(post: Post, current_user: User) -> PostRead:
    return PostRead(
        id=post.id,
        caption=post.caption,
        image_url=f"/uploads/{post.image_file}",
        created_at=post.created_at,
        author=post.author.username,
        like_count=len(post.likes),
        liked_by_me=any(like.user_id == current_user.id for like in post.likes),
        comments=[
            CommentRead(
                id=c.id, text=c.text, username=c.user.username, created_at=c.created_at
            )
            for c in post.comments
        ],
    )


def get_post_or_404(post_id: int, session: Session) -> Post:
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return post


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    caption: str = Form("", max_length=500),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    imagen_muy_grande = HTTPException(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        detail="La imagen supera el máximo de 5 MB",
    )
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se aceptan imágenes JPG, PNG o WebP",
        )
    # Rechazar por el tamaño declarado ANTES de read(): evita cargar en
    # memoria un archivo gigante solo para descubrir que era muy grande.
    if image.size is not None and image.size > MAX_IMAGE_BYTES:
        raise imagen_muy_grande
    content = await image.read()
    if len(content) > MAX_IMAGE_BYTES:  # por si el tamaño no venía declarado
        raise imagen_muy_grande

    # Nombre aleatorio: evita colisiones y que un nombre malicioso
    # (p. ej. ../../algo) escape de la carpeta uploads/.
    filename = f"{uuid.uuid4().hex}{ALLOWED_IMAGE_TYPES[image.content_type]}"
    (Path(UPLOADS_DIR) / filename).write_bytes(content)

    post = Post(caption=caption, image_file=filename, author_id=current_user.id)
    session.add(post)
    session.commit()
    session.refresh(post)
    return to_post_read(post, current_user)


@router.get("", response_model=list[PostRead])
def get_feed(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    posts = session.exec(
        select(Post).order_by(Post.id.desc()).offset(offset).limit(limit)
    ).all()
    return [to_post_read(p, current_user) for p in posts]


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    post = get_post_or_404(post_id, session)
    # Autorización: estar loggeado no basta, hay que ser el dueño.
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el autor puede borrar su post",
        )
    # El archivo se borra DESPUÉS del commit: si el commit fallara, no queda
    # un post vivo apuntando a una imagen que ya no existe.
    image_path = Path(UPLOADS_DIR) / post.image_file
    session.delete(post)  # likes y comentarios caen en cascada
    session.commit()
    image_path.unlink(missing_ok=True)


@router.post("/{post_id}/like", response_model=LikeStatus)
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    post = get_post_or_404(post_id, session)
    already = session.exec(
        select(Like).where(Like.post_id == post_id, Like.user_id == current_user.id)
    ).first()
    if already is None:
        session.add(Like(post_id=post_id, user_id=current_user.id))
        try:
            session.commit()
        except IntegrityError:
            # Dos likes simultáneos del mismo usuario: el UNIQUE de la BD
            # rechaza el segundo, y el resultado final es el mismo.
            session.rollback()
        session.refresh(post)
    return LikeStatus(like_count=len(post.likes), liked_by_me=True)


@router.delete("/{post_id}/like", response_model=LikeStatus)
def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    post = get_post_or_404(post_id, session)
    like = session.exec(
        select(Like).where(Like.post_id == post_id, Like.user_id == current_user.id)
    ).first()
    if like is not None:
        session.delete(like)
        session.commit()
        session.refresh(post)
    return LikeStatus(like_count=len(post.likes), liked_by_me=False)


@router.post(
    "/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED
)
def add_comment(
    post_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    get_post_or_404(post_id, session)
    comment = Comment(text=data.text, post_id=post_id, user_id=current_user.id)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return CommentRead(
        id=comment.id,
        text=comment.text,
        username=current_user.username,
        created_at=comment.created_at,
    )
