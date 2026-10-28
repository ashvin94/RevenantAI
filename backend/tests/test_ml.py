def test_ml_score_is_honestly_unavailable_without_artifact(client):
    order = client.post("/api/orders", json={"sku": "LAPTOP-001", "quantity": 1, "logical_event_id": "evt-ml"}).json()
    response = client.get(f"/api/orders/{order['id']}/ml-score")
    assert response.status_code == 200
    assert response.json()["available"] is False
    assert response.json()["suspicious"] is None
    assert "missing" in response.json()["reason"].lower()
