import base64
from pathlib import Path

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
    "z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def crear_post(client, headers, caption="hola"):
    return client.post(
        "/posts",
        headers=headers,
        data={"caption": caption},
        files={"image": ("foto.png", PNG, "image/png")},
    )


def test_crear_post(client, login):
    res = crear_post(client, login(), caption="mi primer post")
    assert res.status_code == 201
    data = res.json()
    assert data["caption"] == "mi primer post"
    assert data["author"] == "ana"
    assert data["image_url"].startswith("/uploads/")
    assert data["created_at"].endswith("Z")
    assert data["like_count"] == 0 and data["comments"] == []


def test_feed_sin_token_401(client):
    assert client.get("/posts").status_code == 401


def test_crear_post_sin_token_401(client):
    res = client.post(
        "/posts", data={"caption": "x"}, files={"image": ("a.png", PNG, "image/png")}
    )
    assert res.status_code == 401


def test_crear_post_tipo_no_permitido_415(client, login):
    res = client.post(
        "/posts",
        headers=login(),
        data={"caption": "x"},
        files={"image": ("virus.exe", b"MZ...", "application/octet-stream")},
    )
    assert res.status_code == 415


def test_crear_post_muy_grande_413(client, login):
    grande = b"x" * (5 * 1024 * 1024 + 1)
    res = client.post(
        "/posts",
        headers=login(),
        data={"caption": "x"},
        files={"image": ("grande.png", grande, "image/png")},
    )
    assert res.status_code == 413


def test_feed_ordenado_y_paginado(client, login):
    headers = login()
    for i in range(3):
        crear_post(client, headers, caption=f"post {i}")

    pagina = client.get("/posts?offset=0&limit=2", headers=headers).json()
    assert [p["caption"] for p in pagina] == ["post 2", "post 1"]

    resto = client.get("/posts?offset=2&limit=2", headers=headers).json()
    assert [p["caption"] for p in resto] == ["post 0"]


def test_like_es_idempotente_y_unlike(client, login):
    headers = login()
    post_id = crear_post(client, headers).json()["id"]

    res = client.post(f"/posts/{post_id}/like", headers=headers).json()
    assert res == {"like_count": 1, "liked_by_me": True}

    res = client.post(f"/posts/{post_id}/like", headers=headers).json()
    assert res["like_count"] == 1

    res = client.delete(f"/posts/{post_id}/like", headers=headers).json()
    assert res == {"like_count": 0, "liked_by_me": False}


def test_like_a_post_inexistente_404(client, login):
    assert client.post("/posts/999/like", headers=login()).status_code == 404


def test_comentar(client, login):
    headers = login()
    post_id = crear_post(client, headers).json()["id"]

    res = client.post(
        f"/posts/{post_id}/comments", headers=headers, json={"text": "qué lindo"}
    )
    assert res.status_code == 201
    assert res.json()["username"] == "ana"

    feed = client.get("/posts", headers=headers).json()
    assert feed[0]["comments"][0]["text"] == "qué lindo"


def test_borrar_post_propio_borra_tambien_el_archivo(client, login, tmp_path):
    headers = login()
    post = crear_post(client, headers).json()
    archivo = tmp_path / post["image_url"].removeprefix("/uploads/")
    assert archivo.exists()

    res = client.delete(f"/posts/{post['id']}", headers=headers)
    assert res.status_code == 204
    assert not archivo.exists()
    assert client.get("/posts", headers=headers).json() == []


def test_borrar_post_ajeno_403(client, login):
    dueña = login("ana")
    otra = login("eva")
    post_id = crear_post(client, dueña).json()["id"]

    res = client.delete(f"/posts/{post_id}", headers=otra)
    assert res.status_code == 403
