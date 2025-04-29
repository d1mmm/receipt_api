import pytest

@pytest.mark.anyio
async def test_register_and_login(client):
    res = await client.post(
        "/register",
        json={"username": "newuser", "full_name": "New User", "password": "newpass"}
    )
    assert res.status_code == 201
    assert res.json() == {"message": "User registered", "user": "newuser"}

    login_res = await client.post(
        "/login",
        json={"username": "newuser", "password": "newpass"}
    )
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data and data["token_type"] == "bearer"
    assert "access_token_cookie" in login_res.cookies

@pytest.mark.anyio
async def test_invalid_login(client):
    res = await client.post(
        "/login",
        json={"username": "nouser", "password": "nopass"}
    )
    assert res.status_code == 401
