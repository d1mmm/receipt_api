import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.anyio
async def test_unauthorized_and_invalid_actions(client):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as anon:
        res = await anon.post(
            "/receipts",
            json={"products": [], "payment": {"type": "cash", "amount": 0}}
        )
        assert res.status_code == 401

        res = await anon.get("/receipts")
        assert res.status_code == 401

    await client.post(
        "/register",
        json={"username": "u4", "full_name": "U4", "password": "pass4"}
    )
    login_res = await client.post(
        "/login",
        json={"username": "u4", "password": "pass4"}
    )
    assert login_res.status_code == 200

    res = await client.get("/receipts/9999")
    assert res.status_code == 404
