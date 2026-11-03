def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_login_success(client):
    response = client.post("/api/v1/auth/login", data={"username": "admin", "password": "Admin123!"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "admin"

def test_login_invalid_password(client):
    response = client.post("/api/v1/auth/login", data={"username": "admin", "password": "WrongPassword!"})
    assert response.status_code == 401

def test_refresh_token_rotation(client):
    login_res = client.post("/api/v1/auth/login", data={"username": "admin", "password": "Admin123!"})
    refresh_token = login_res.json()["refresh_token"]

    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["refresh_token"] != refresh_token

    # Reusing the old refresh token should now fail (revocation upon rotation)
    stale_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert stale_res.status_code == 401
