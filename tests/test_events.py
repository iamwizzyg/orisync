

class TestCreateEvent:
    def test_create_event_success(self, client, operator_headers, sample_supplier):
        response = client.post(
            "/api/v1/events",
            json={
                "supplier_id": sample_supplier["id"],
                "event_type": "SHIPPED",
                "payload": {"order_id": "ORD-001", "quantity": 50},
            },
            headers=operator_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["event_type"] == "SHIPPED"
        assert data["status"] == "PENDING"
        assert data["payload"]["order_id"] == "ORD-001"

    def test_create_event_invalid_type(self, client, operator_headers, sample_supplier):
        response = client.post(
            "/api/v1/events",
            json={
                "supplier_id": sample_supplier["id"],
                "event_type": "INVALID_TYPE",
                "payload": {},
            },
            headers=operator_headers,
        )
        assert response.status_code == 422

    def test_create_event_nonexistent_supplier(self, client, operator_headers):
        response = client.post(
            "/api/v1/events",
            json={
                "supplier_id": "nonexistent-supplier-id",
                "event_type": "SHIPPED",
                "payload": {},
            },
            headers=operator_headers,
        )
        assert response.status_code == 400

    def test_create_event_viewer_forbidden(
        self, client, viewer_headers, sample_supplier
    ):
        response = client.post(
            "/api/v1/events",
            json={
                "supplier_id": sample_supplier["id"],
                "event_type": "SHIPPED",
                "payload": {},
            },
            headers=viewer_headers,
        )
        assert response.status_code == 403

    def test_idempotency_key_prevents_duplicate(
        self, client, operator_headers, sample_supplier
    ):
        """
        Sending the same event twice with the same idempotency_key
        must return the original event, not create a second one.
        This is a critical distributed systems concept.
        """
        payload = {
            "supplier_id": sample_supplier["id"],
            "event_type": "ORDERED",
            "payload": {"order_id": "ORD-IDEM-001"},
            "idempotency_key": "unique-key-abc-123",
        }
        response1 = client.post("/api/v1/events", json=payload, headers=operator_headers)
        response2 = client.post("/api/v1/events", json=payload, headers=operator_headers)

        assert response1.status_code == 201
        assert response2.status_code == 201
        # Both responses return the same event ID
        assert response1.json()["id"] == response2.json()["id"]

    def test_event_type_stored_uppercase(
        self, client, operator_headers, sample_supplier
    ):
        response = client.post(
            "/api/v1/events",
            json={
                "supplier_id": sample_supplier["id"],
                "event_type": "shipped",
                "payload": {},
            },
            headers=operator_headers,
        )
        assert response.status_code == 201
        assert response.json()["event_type"] == "SHIPPED"


class TestListEvents:
    def test_list_events(self, client, auth_headers, operator_headers, sample_supplier):
        client.post(
            "/api/v1/events",
            json={
                "supplier_id": sample_supplier["id"],
                "event_type": "RECEIVED",
                "payload": {},
            },
            headers=operator_headers,
        )
        response = client.get("/api/v1/events", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_filter_events_by_type(
        self, client, auth_headers, operator_headers, sample_supplier
    ):
        client.post(
            "/api/v1/events",
            json={
                "supplier_id": sample_supplier["id"],
                "event_type": "DELAYED",
                "payload": {},
            },
            headers=operator_headers,
        )
        response = client.get(
            "/api/v1/events?event_type=DELAYED",
            headers=auth_headers,
        )
        assert response.status_code == 200
        events = response.json()
        assert all(e["event_type"] == "DELAYED" for e in events)

    def test_get_event_by_id(
        self, client, auth_headers, operator_headers, sample_supplier
    ):
        create_resp = client.post(
            "/api/v1/events",
            json={
                "supplier_id": sample_supplier["id"],
                "event_type": "ANOMALY",
                "payload": {"note": "shipment damaged"},
            },
            headers=operator_headers,
        )
        event_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/events/{event_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == event_id

    def test_get_nonexistent_event(self, client, auth_headers):
        response = client.get("/api/v1/events/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404
