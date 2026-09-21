from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlmodel import Session, select

from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from .database import get_session
from .models import User

password_hash = PasswordHash((BcryptHasher(),))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def create_access_token(username: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Dependencia que protege endpoints: valida el JWT y devuelve el usuario."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except jwt.InvalidTokenError:
        raise credentials_error
    if username is None:
        raise credentials_error

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_error
    return user
