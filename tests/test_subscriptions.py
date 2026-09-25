

class TestCreateSubscription:
    def test_create_subscription(self, client, auth_headers):
        response = client.post(
            "/api/v1/subscriptions",
            json={
                "name": "Delay Alerts",
                "webhook_url": "https://example.com/hooks/delays",
                "event_types": ["DELAYED", "ANOMALY"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Delay Alerts"
        assert "DELAYED" in data["event_types"]
        assert data["is_active"] is True

    def test_create_subscription_all_events(self, client, auth_headers):
        """Empty event_types means subscribe to all event types."""
        response = client.post(
            "/api/v1/subscriptions",
            json={
                "webhook_url": "https://example.com/hooks/all",
                "event_types": [],
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["event_types"] == []

    def test_create_subscription_invalid_url(self, client, auth_headers):
        response = client.post(
            "/api/v1/subscriptions",
            json={
                "webhook_url": "not-a-valid-url",
                "event_types": [],
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_subscription_operator_forbidden(self, client, operator_headers):
        response = client.post(
            "/api/v1/subscriptions",
            json={
                "webhook_url": "https://example.com/hook",
                "event_types": [],
            },
            headers=operator_headers,
        )
        assert response.status_code == 403

    def test_create_subscription_invalid_event_type(self, client, auth_headers):
        response = client.post(
            "/api/v1/subscriptions",
            json={
                "webhook_url": "https://example.com/hook",
                "event_types": ["INVALID_TYPE"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestListSubscriptions:
    def test_list_subscriptions(self, client, auth_headers):
        client.post(
            "/api/v1/subscriptions",
            json={
                "webhook_url": "https://example.com/list-test",
                "event_types": [],
            },
            headers=auth_headers,
        )
        response = client.get("/api/v1/subscriptions", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestDeactivateSubscription:
    def test_deactivate_subscription(self, client, auth_headers):
        create_resp = client.post(
            "/api/v1/subscriptions",
            json={
                "webhook_url": "https://example.com/to-delete",
                "event_types": [],
            },
            headers=auth_headers,
        )
        sub_id = create_resp.json()["id"]

        response = client.delete(
            f"/api/v1/subscriptions/{sub_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204
