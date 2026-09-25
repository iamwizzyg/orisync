class TestRegister:
    def test_register_success(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "securepass123",
            "role": "VIEWER",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "VIEWER"
        assert "hashed_password" not in data
        assert "password" not in data

    def test_register_duplicate_email(self, client):
        payload = {
            "email": "duplicate@test.com",
            "password": "securepass123",
            "role": "VIEWER",
        }
        client.post("/api/v1/auth/register", json=payload)
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "securepass123",
            "role": "VIEWER",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "user@test.com",
            "password": "short",
            "role": "VIEWER",
        })
        assert response.status_code == 422

    def test_register_invalid_role(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "user@test.com",
            "password": "securepass123",
            "role": "SUPERUSER",
        })
        assert response.status_code == 422

    def test_register_default_role_is_viewer(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "defaultrole@test.com",
            "password": "securepass123",
        })
        assert response.status_code == 201
        assert response.json()["role"] == "VIEWER"


class TestLogin:
    def test_login_success(self, client):
        client.post("/api/v1/auth/register", json={
            "email": "logintest@test.com",
            "password": "securepass123",
            "role": "VIEWER",
        })
        response = client.post("/api/v1/auth/login", json={
            "email": "logintest@test.com",
            "password": "securepass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        client.post("/api/v1/auth/register", json={
            "email": "wrongpass@test.com",
            "password": "correctpass123",
            "role": "VIEWER",
        })
        response = client.post("/api/v1/auth/login", json={
            "email": "wrongpass@test.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com",
            "password": "somepass123",
        })
        assert response.status_code == 401

    def test_protected_route_without_token(self, client):
        response = client.get("/api/v1/suppliers")
        assert response.status_code == 403

    def test_protected_route_with_invalid_token(self, client):
        response = client.get(
            "/api/v1/suppliers",
            headers={"Authorization": "Bearer fake.token.here"},
        )
        assert response.status_code == 401
