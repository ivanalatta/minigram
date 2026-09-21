from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..database import get_session
from ..models import User
from ..schemas import Token, UserCreate, UserRead
from ..security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: Session = Depends(get_session)):
    duplicado = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="El usuario o email ya está registrado",
    )
    exists = session.exec(
        select(User).where((User.username == data.username) | (User.email == data.email))
    ).first()
    if exists:
        raise duplicado
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        # Dos registros simultáneos pueden pasar el chequeo de arriba;
        # el constraint UNIQUE de la base de datos es la garantía final.
        session.rollback()
        raise duplicado
    session.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == form.username)).first()
    # Mismo mensaje si el usuario no existe o la contraseña falla:
    # no revelamos cuál de los dos fue (evita enumerar usuarios).
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.username))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
