def test_public_receipt_view(client, login_user):
    login_res = login_user("u3", "pass3")
    assert login_res.status_code == 200

    create_res = client.post(
        "/receipts",
        json={
            "products": [{"name": "X", "price": 2.0, "quantity": 3}],
            "payment": {"type": "cash", "amount": 10.0}
        }
    )
    receipt_id = create_res.json()["id"]

    pub_res = client.get(f"/public/receipts/{receipt_id}")
    assert pub_res.status_code == 200
    assert "СУМА" in pub_res.text
