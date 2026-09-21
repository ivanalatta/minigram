from datetime import datetime, timezone

from pydantic import EmailStr, field_serializer, field_validator
from sqlmodel import Field, SQLModel


def as_utc(dt: datetime) -> datetime:
    """SQLite guarda las fechas sin zona horaria; al devolverlas las marcamos
    como UTC para que el navegador las convierta bien a hora local."""
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

# Esquemas de entrada/salida del API, separados de los modelos de tabla:
# controlan qué campos entran y salen (p. ej. hashed_password nunca sale).


class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6)

    @field_validator("password")
    @classmethod
    def password_max_72_bytes(cls, value: str) -> str:
        # bcrypt limita a 72 *bytes*, no caracteres: una ñ o un emoji ocupan
        # varios bytes, así que max_length=72 no alcanza para protegernos.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar los 72 bytes")
        return value


class UserRead(SQLModel):
    id: int
    username: str
    email: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class GoogleCredential(SQLModel):
    credential: str


class CommentCreate(SQLModel):
    text: str = Field(min_length=1, max_length=500)


class CommentRead(SQLModel):
    id: int
    text: str
    username: str
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> datetime:
        return as_utc(dt)


class PostRead(SQLModel):
    id: int
    caption: str
    image_url: str
    created_at: datetime
    author: str
    like_count: int
    liked_by_me: bool
    comments: list[CommentRead]

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> datetime:
        return as_utc(dt)


class LikeStatus(SQLModel):
    like_count: int
    liked_by_me: bool
