from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

# Esquemas de entrada/salida del API, separados de los modelos de tabla:
# controlan qué campos entran y salen (p. ej. hashed_password nunca sale).


class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    # bcrypt tiene un límite de 72 bytes, por eso el max_length
    password: str = Field(min_length=6, max_length=72)


class UserRead(SQLModel):
    id: int
    username: str
    email: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class CommentCreate(SQLModel):
    text: str = Field(min_length=1, max_length=500)


class CommentRead(SQLModel):
    id: int
    text: str
    username: str
    created_at: datetime


class PostRead(SQLModel):
    id: int
    caption: str
    image_url: str
    created_at: datetime
    author: str
    like_count: int
    liked_by_me: bool
    comments: list[CommentRead]


class LikeStatus(SQLModel):
    like_count: int
    liked_by_me: bool
