from fastapi.testclient import TestClient
from app.main import app

def test_unauthorized_and_invalid_actions(client):
    c = TestClient(app)

    res = c.post("/receipts", json={"products": [], "payment": {"type": "cash", "amount": 0}})
    assert res.status_code == 401

    res = c.get("/receipts")
    assert res.status_code == 401

    client.post("/register", json={"username": "u4", "full_name": "U4", "password": "pass4"})
    login_res = client.post("/login", json={"username": "u4", "password": "pass4"})
    assert login_res.status_code == 200

    res = client.get("/receipts/9999")
    assert res.status_code == 404
