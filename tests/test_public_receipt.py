import pytest

@pytest.mark.anyio
async def test_public_receipt_view(client, register_and_login):
    login_res = await register_and_login("u3", "pass3")
    assert login_res.status_code == 200

    create_res = await client.post(
        "/receipts",
        json={
            "products": [{"name": "X", "price": 2.0, "quantity": 3}],
            "payment": {"type": "cash", "amount": 10.0}
        }
    )
    receipt_id = create_res.json()["id"]

    pub_res = await client.get(f"/public/receipts/{receipt_id}")
    assert pub_res.status_code == 200
    assert "TOTAL" in pub_res.text
