from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=utcnow)

    posts: list["Post"] = Relationship(back_populates="author")


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    caption: str = ""
    image_file: str  # nombre del archivo dentro de uploads/
    created_at: datetime = Field(default_factory=utcnow)
    author_id: int = Field(foreign_key="user.id")

    author: User = Relationship(back_populates="posts")
    # cascade_delete: al borrar un post se borran sus likes y comentarios
    likes: list["Like"] = Relationship(back_populates="post", cascade_delete=True)
    comments: list["Comment"] = Relationship(back_populates="post", cascade_delete=True)


class Like(SQLModel, table=True):
    # Un usuario solo puede dar like una vez al mismo post:
    # la base de datos lo garantiza, no solo el código.
    __table_args__ = (UniqueConstraint("user_id", "post_id"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")

    post: Post = Relationship(back_populates="likes")


class Comment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    created_at: datetime = Field(default_factory=utcnow)
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")

    user: User = Relationship()
    post: Post = Relationship(back_populates="comments")
