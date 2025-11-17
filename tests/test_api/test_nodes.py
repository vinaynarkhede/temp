"""
Tests for node management API endpoints.

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
from datetime import datetime


class TestNodeRegistration:
    """Test suite for POST /nodes endpoint."""

    def test_register_node_successfully(self, client, db_session):
        """Test that authenticated user can register a node."""
        from src.database.models import User

        # Create and authenticate user
        user = User(
            username="alice",
            email="alice@example.com",
            password_hash="hashed",
            api_key="test_api_key_123"
        )
        db_session.add(user)
        db_session.commit()

        # Register node
        node_data = {
            "name": "Alice-Desktop",
            "tailscale_ip": "100.64.0.1",
            "cpu_cores": 8,
            "ram_gb": 16.0,
            "storage_gb": 500.0
        }

        response = client.post(
            "/nodes",
            json=node_data,
            headers={"X-API-Key": "test_api_key_123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alice-Desktop"
        assert data["cpu_cores"] == 8
        assert data["status"] == "offline"
        assert data["owner_id"] == user.id
        assert "id" in data

    def test_register_node_requires_authentication(self, client):
        """Test that node registration requires API key."""
        node_data = {
            "name": "Test-Node",
            "tailscale_ip": "100.64.0.1",
            "cpu_cores": 4,
            "ram_gb": 8.0,
            "storage_gb": 200.0
        }

        response = client.post("/nodes", json=node_data)

        assert response.status_code == 401

    def test_register_node_validates_cpu_cores(self, client, db_session):
        """Test that CPU cores must be positive."""
        from src.database.models import User

        user = User(username="bob", email="bob@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.commit()

        node_data = {
            "name": "Bob-PC",
            "tailscale_ip": "100.64.0.2",
            "cpu_cores": 0,
            "ram_gb": 8.0,
            "storage_gb": 200.0
        }

        response = client.post(
            "/nodes",
            json=node_data,
            headers={"X-API-Key": "key123"}
        )

        assert response.status_code == 422

    def test_register_node_validates_ram(self, client, db_session):
        """Test that RAM must be positive."""
        from src.database.models import User

        user = User(username="charlie", email="charlie@example.com", password_hash="h", api_key="key456")
        db_session.add(user)
        db_session.commit()

        node_data = {
            "name": "Charlie-Laptop",
            "tailscale_ip": "100.64.0.3",
            "cpu_cores": 4,
            "ram_gb": -1.0,
            "storage_gb": 200.0
        }

        response = client.post(
            "/nodes",
            json=node_data,
            headers={"X-API-Key": "key456"}
        )

        assert response.status_code == 422


class TestListNodes:
    """Test suite for GET /nodes endpoint."""

    def test_list_user_nodes(self, client, db_session):
        """Test that user can list their own nodes."""
        from src.database.models import User, Node

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

        # Create multiple nodes
        node1 = Node(
            owner_id=user.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0
        )
        node2 = Node(
            owner_id=user.id,
            name="Alice-Laptop",
            tailscale_ip="100.64.0.2",
            cpu_cores=4,
            ram_gb=8.0,
            storage_gb=250.0
        )
        db_session.add_all([node1, node2])
        db_session.commit()

        response = client.get("/nodes", headers={"X-API-Key": "key123"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Alice-Desktop" or data[1]["name"] == "Alice-Desktop"

    def test_list_nodes_requires_authentication(self, client):
        """Test that listing nodes requires API key."""
        response = client.get("/nodes")

        assert response.status_code == 401

    def test_list_nodes_only_shows_user_nodes(self, client, db_session):
        """Test that users only see their own nodes."""
        from src.database.models import User, Node

        user1 = User(username="alice", email="alice@example.com", password_hash="h", api_key="key1")
        user2 = User(username="bob", email="bob@example.com", password_hash="h", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.flush()

        node1 = Node(
            owner_id=user1.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0
        )
        node2 = Node(
            owner_id=user2.id,
            name="Bob-Desktop",
            tailscale_ip="100.64.0.2",
            cpu_cores=4,
            ram_gb=8.0,
            storage_gb=250.0
        )
        db_session.add_all([node1, node2])
        db_session.commit()

        response = client.get("/nodes", headers={"X-API-Key": "key1"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice-Desktop"


class TestGetNodeById:
    """Test suite for GET /nodes/{node_id} endpoint."""

    def test_get_node_by_id(self, client, db_session):
        """Test that user can get their node by ID."""
        from src.database.models import User, Node

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0
        )
        db_session.add(node)
        db_session.commit()

        response = client.get(f"/nodes/{node.id}", headers={"X-API-Key": "key123"})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == node.id
        assert data["name"] == "Alice-Desktop"

    def test_get_node_requires_authentication(self, client, db_session):
        """Test that getting node requires API key."""
        response = client.get("/nodes/1")

        assert response.status_code == 401

    def test_get_node_not_found(self, client, db_session):
        """Test that non-existent node returns 404."""
        from src.database.models import User

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.commit()

        response = client.get("/nodes/9999", headers={"X-API-Key": "key123"})

        assert response.status_code == 404

    def test_get_node_forbidden_for_non_owner(self, client, db_session):
        """Test that users cannot access other users' nodes."""
        from src.database.models import User, Node

        user1 = User(username="alice", email="alice@example.com", password_hash="h", api_key="key1")
        user2 = User(username="bob", email="bob@example.com", password_hash="h", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.flush()

        node = Node(
            owner_id=user1.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0
        )
        db_session.add(node)
        db_session.commit()

        # Bob tries to access Alice's node
        response = client.get(f"/nodes/{node.id}", headers={"X-API-Key": "key2"})

        assert response.status_code == 403


class TestUpdateNode:
    """Test suite for PATCH /nodes/{node_id} endpoint."""

    def test_update_node_status(self, client, db_session):
        """Test that user can update their node status."""
        from src.database.models import User, Node

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0,
            status="offline"
        )
        db_session.add(node)
        db_session.commit()

        update_data = {"status": "online"}
        response = client.patch(
            f"/nodes/{node.id}",
            json=update_data,
            headers={"X-API-Key": "key123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"

    def test_update_node_requires_authentication(self, client):
        """Test that updating node requires API key."""
        response = client.patch("/nodes/1", json={"status": "online"})

        assert response.status_code == 401

    def test_update_node_forbidden_for_non_owner(self, client, db_session):
        """Test that users cannot update other users' nodes."""
        from src.database.models import User, Node

        user1 = User(username="alice", email="alice@example.com", password_hash="h", api_key="key1")
        user2 = User(username="bob", email="bob@example.com", password_hash="h", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.flush()

        node = Node(
            owner_id=user1.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0
        )
        db_session.add(node)
        db_session.commit()

        response = client.patch(
            f"/nodes/{node.id}",
            json={"status": "online"},
            headers={"X-API-Key": "key2"}
        )

        assert response.status_code == 403

    def test_update_node_partial_update(self, client, db_session):
        """Test that partial updates work correctly."""
        from src.database.models import User, Node

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0
        )
        db_session.add(node)
        db_session.commit()

        # Update only CPU cores
        update_data = {"cpu_cores": 16}
        response = client.patch(
            f"/nodes/{node.id}",
            json=update_data,
            headers={"X-API-Key": "key123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["cpu_cores"] == 16
        assert data["ram_gb"] == 16.0  # Unchanged


class TestDeleteNode:
    """Test suite for DELETE /nodes/{node_id} endpoint."""

    def test_delete_node(self, client, db_session):
        """Test that user can delete their node."""
        from src.database.models import User, Node

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

        node = Node(
            owner_id=user.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0
        )
        db_session.add(node)
        db_session.commit()

        node_id = node.id

        response = client.delete(f"/nodes/{node_id}", headers={"X-API-Key": "key123"})

        assert response.status_code == 204

        # Verify node is deleted
        from src.database.models import Node
        deleted_node = db_session.query(Node).filter_by(id=node_id).first()
        assert deleted_node is None

    def test_delete_node_requires_authentication(self, client):
        """Test that deleting node requires API key."""
        response = client.delete("/nodes/1")

        assert response.status_code == 401

    def test_delete_node_forbidden_for_non_owner(self, client, db_session):
        """Test that users cannot delete other users' nodes."""
        from src.database.models import User, Node

        user1 = User(username="alice", email="alice@example.com", password_hash="h", api_key="key1")
        user2 = User(username="bob", email="bob@example.com", password_hash="h", api_key="key2")
        db_session.add_all([user1, user2])
        db_session.flush()

        node = Node(
            owner_id=user1.id,
            name="Alice-Desktop",
            tailscale_ip="100.64.0.1",
            cpu_cores=8,
            ram_gb=16.0,
            storage_gb=500.0
        )
        db_session.add(node)
        db_session.commit()

        response = client.delete(f"/nodes/{node.id}", headers={"X-API-Key": "key2"})

        assert response.status_code == 403

    def test_delete_node_not_found(self, client, db_session):
        """Test that deleting non-existent node returns 404."""
        from src.database.models import User

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.commit()

        response = client.delete("/nodes/9999", headers={"X-API-Key": "key123"})

        assert response.status_code == 404
