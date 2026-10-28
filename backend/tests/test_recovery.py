def broken_incident(client):
    order = client.post("/api/orders", json={"sku": "LAPTOP-001", "quantity": 1, "logical_event_id": "evt-recover"}).json()
    injected = client.post(f"/api/orders/{order['id']}/inject-duplicate").json()
    incident = client.post(f"/api/orders/{order['id']}/inspect").json()["incident"]
    return order, injected, incident


def test_simulation_is_pure_and_recovery_is_verified_and_idempotent(client):
    order, injected, incident = broken_incident(client)
    candidate = {"id": "RELEASE_DUPLICATE", "reservation_id": injected["injected_reservation_id"]}
    simulation = client.post(f"/api/incidents/{incident['id']}/simulate", json={"candidate": candidate})
    assert simulation.status_code == 200
    assert simulation.json()["safe"] is True
    assert simulation.json()["active_reservations_after"] == 1
    assert client.get(f"/api/orders/{order['id']}").json()["reservations"][1]["status"] == "ACTIVE"
    body = {"candidate": candidate, "expected_order_version": simulation.json()["expected_order_version"], "idempotency_key": "recover-key-001", "approved": True}
    first = client.post(f"/api/incidents/{incident['id']}/recover", json=body)
    assert first.status_code == 200
    assert first.json()["verified"] is True
    second = client.post(f"/api/incidents/{incident['id']}/recover", json=body)
    assert second.status_code == 200
    assert second.json()["status"] == "REPLAYED"
    assert second.json()["available_stock"] == first.json()["available_stock"]


def test_recovery_rejects_stale_version_and_wrong_target(client):
    _order, injected, incident = broken_incident(client)
    candidate = {"id": "RELEASE_DUPLICATE", "reservation_id": injected["injected_reservation_id"]}
    response = client.post(f"/api/incidents/{incident['id']}/recover", json={"candidate": candidate, "expected_order_version": 1, "idempotency_key": "recover-key-002", "approved": True})
    assert response.status_code == 409
    wrong = client.post(f"/api/incidents/{incident['id']}/simulate", json={"candidate": {"id": "RELEASE_DUPLICATE", "reservation_id": "missing"}})
    assert wrong.status_code == 409
