from app.models import User
from app.routers import auth as auth_router
from app.routers.auth import unique_username


def test_register_devuelve_usuario_sin_password(client):
    res = client.post(
        "/auth/register",
        json={"username": "ana", "email": "ana@test.com", "password": "secreta1"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "ana"
    assert "password" not in data and "hashed_password" not in data


def test_register_username_duplicado_409(client):
    body = {"username": "ana", "email": "ana@test.com", "password": "secreta1"}
    client.post("/auth/register", json=body)
    res = client.post(
        "/auth/register",
        json={"username": "ana", "email": "otra@test.com", "password": "secreta1"},
    )
    assert res.status_code == 409


def test_register_email_duplicado_409(client):
    client.post(
        "/auth/register",
        json={"username": "ana", "email": "ana@test.com", "password": "secreta1"},
    )
    res = client.post(
        "/auth/register",
        json={"username": "otra", "email": "ana@test.com", "password": "secreta1"},
    )
    assert res.status_code == 409


def test_register_password_multibyte_supera_72_bytes_422(client):
    # 72 caracteres ñ = 144 bytes: pasa un max_length de caracteres
    # pero supera el límite real de bcrypt
    res = client.post(
        "/auth/register",
        json={"username": "ana", "email": "ana@test.com", "password": "ñ" * 72},
    )
    assert res.status_code == 422


def test_login_ok_y_me(client, login):
    headers = login("ana")
    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["username"] == "ana"


def test_login_no_revela_si_el_usuario_existe(client, login):
    login("ana")
    mal_password = client.post(
        "/auth/token", data={"username": "ana", "password": "incorrecta"}
    )
    no_existe = client.post(
        "/auth/token", data={"username": "nadie", "password": "incorrecta"}
    )
    assert mal_password.status_code == no_existe.status_code == 401
    assert mal_password.json()["detail"] == no_existe.json()["detail"]


def test_me_sin_token_401(client):
    assert client.get("/auth/me").status_code == 401


def test_me_con_token_invalido_401(client):
    res = client.get("/auth/me", headers={"Authorization": "Bearer basura"})
    assert res.status_code == 401


def test_google_sin_configurar_503(client, monkeypatch):
    monkeypatch.setattr(auth_router, "GOOGLE_CLIENT_ID", "")
    res = client.post("/auth/google", json={"credential": "algo"})
    assert res.status_code == 503


def test_google_credential_invalida_401(client, monkeypatch):
    monkeypatch.setattr(auth_router, "GOOGLE_CLIENT_ID", "fake-id")
    res = client.post("/auth/google", json={"credential": "basura"})
    assert res.status_code == 401


def test_cuenta_google_no_entra_con_password(client, session):
    session.add(User(username="googler", email="g@test.com", hashed_password=None))
    session.commit()
    res = client.post(
        "/auth/token", data={"username": "googler", "password": "loquesea"}
    )
    assert res.status_code == 401


def test_unique_username(session):
    assert unique_username("pedro@test.com", session) == "pedro"

    session.add(User(username="ana", email="ana@test.com", hashed_password="x"))
    session.commit()
    assert unique_username("ana@otro.com", session) == "ana2"

    assert len(unique_username("ab@test.com", session)) >= 3
