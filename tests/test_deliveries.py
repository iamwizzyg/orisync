

class TestListDeliveries:
    def test_list_deliveries_empty(self, client, auth_headers):
        response = client.get("/api/v1/deliveries", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_deliveries_operator_forbidden(self, client, operator_headers):
        response = client.get("/api/v1/deliveries", headers=operator_headers)
        assert response.status_code == 403

    def test_retry_nonexistent_delivery(self, client, auth_headers):
        response = client.post(
            "/api/v1/deliveries/nonexistent-id/retry",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestSystemEndpoints:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "orisync"

    def test_metrics_endpoint(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "orisync" in response.text or "python" in response.text
