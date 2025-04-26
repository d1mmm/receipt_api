def test_register_and_login(client, register_user, login_user):
    res = register_user("newuser", "New User", "newpass")
    assert res.status_code == 201
    assert res.json() == {"message": "User registered", "user": "newuser"}

    login_res = login_user("newuser", "newpass")
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data and data["token_type"] == "bearer"
    assert "access_token_cookie" in login_res.cookies

def test_invalid_login(client):
    res = client.post(
        "/login",
        json={"username": "nouser", "password": "nopass"}
    )
    assert res.status_code == 401
