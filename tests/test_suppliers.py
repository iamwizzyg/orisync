import pytest


class TestCreateSupplier:
    def test_create_supplier_as_admin(self, client, auth_headers):
        response = client.post(
            "/api/v1/suppliers",
            json={"name": "Acme Corp", "contact_email": "acme@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Acme Corp"
        assert data["contact_email"] == "acme@example.com"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_supplier_as_operator(self, client, operator_headers):
        response = client.post(
            "/api/v1/suppliers",
            json={"name": "Operator Supplier"},
            headers=operator_headers,
        )
        assert response.status_code == 201

    def test_create_supplier_without_email(self, client, auth_headers):
        response = client.post(
            "/api/v1/suppliers",
            json={"name": "No Email Supplier"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["contact_email"] is None

    def test_create_supplier_unauthenticated(self, client):
        response = client.post(
            "/api/v1/suppliers",
            json={"name": "Unauthorized"},
        )
        assert response.status_code == 403


class TestListSuppliers:
    def test_list_suppliers(self, client, auth_headers, sample_supplier):
        response = client.get("/api/v1/suppliers", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    def test_list_suppliers_as_viewer(self, client, viewer_headers, sample_supplier):
        response = client.get("/api/v1/suppliers", headers=viewer_headers)
        assert response.status_code == 200


class TestGetSupplier:
    def test_get_supplier_by_id(self, client, auth_headers, sample_supplier):
        supplier_id = sample_supplier["id"]
        response = client.get(
            f"/api/v1/suppliers/{supplier_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["id"] == supplier_id

    def test_get_nonexistent_supplier(self, client, auth_headers):
        response = client.get(
            "/api/v1/suppliers/nonexistent-id",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestUpdateSupplier:
    def test_update_supplier_as_admin(self, client, auth_headers, sample_supplier):
        supplier_id = sample_supplier["id"]
        response = client.patch(
            f"/api/v1/suppliers/{supplier_id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_supplier_as_operator_forbidden(
        self, client, operator_headers, sample_supplier
    ):
        supplier_id = sample_supplier["id"]
        response = client.patch(
            f"/api/v1/suppliers/{supplier_id}",
            json={"name": "Should Fail"},
            headers=operator_headers,
        )
        assert response.status_code == 403


class TestDeactivateSupplier:
    def test_deactivate_supplier(self, client, auth_headers, sample_supplier):
        supplier_id = sample_supplier["id"]
        response = client.delete(
            f"/api/v1/suppliers/{supplier_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify it no longer appears in active list
        list_response = client.get("/api/v1/suppliers", headers=auth_headers)
        ids = [s["id"] for s in list_response.json()]
        assert supplier_id not in ids
