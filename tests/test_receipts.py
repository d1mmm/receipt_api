import decimal


def test_create_and_get_receipt(client, login_user):
    login_res = login_user("u1", "pass1")
    assert login_res.status_code == 200

    payload = {
        "products": [{"name": "ItemA", "price": 10.0, "quantity": 2}],
        "payment": {"type": "cash", "amount": 25.0}
    }
    create_res = client.post("/receipts", json=payload)
    assert create_res.status_code == 201
    data = create_res.json()
    assert decimal.Decimal(data["total"]) == 20.0
    assert decimal.Decimal(data["rest"]) == 5.0

    get_res = client.get(f"/receipts/{data['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == data["id"]

def test_list_receipts_pagination_and_filter(client, login_user):
    login_res = login_user("u2", "pass2")
    assert login_res.status_code == 200

    for i in range(5):
        client.post(
            "/receipts",
            json={
                "products": [{"name": f"P{i}", "price": 5.0, "quantity": i+1}],
                "payment": {"type": "cashless", "amount": 100.0}
            }
        )

    page_res = client.get("/receipts?skip=2&limit=2")
    assert page_res.status_code == 200
    assert len(page_res.json()) == 2

    filter_res = client.get("/receipts?min_total=15")
    assert filter_res.status_code == 200
    for rec in filter_res.json():
        assert decimal.Decimal(rec["total"]) >= 15
