def test_ai_is_explicitly_unavailable_without_key(client):
    order = client.post("/api/orders", json={"sku": "LAPTOP-001", "quantity": 1, "logical_event_id": "evt-ai"}).json()
    client.post(f"/api/orders/{order['id']}/inject-duplicate")
    incident = client.post(f"/api/orders/{order['id']}/inspect").json()["incident"]
    response = client.post(f"/api/incidents/{incident['id']}/analyze")
    assert response.status_code == 503
    assert response.json()["detail"] == "Gemini is not configured."
