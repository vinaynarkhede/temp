"""
Tests for resource offer API endpoints.

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
from datetime import datetime


class TestCreateResourceOffer:
    """Test suite for POST /offers endpoint."""

    def test_create_resource_offer_successfully(self, client, db_session):
        """Test that user can create a resource offer for their node."""
        from src.database.models import User, Node

        # Create user and node
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

        # Create offer
        offer_data = {
            "node_id": node.id,
            "cpu_cores_available": 4,
            "ram_gb_available": 8.0,
            "storage_gb_available": 100.0,
            "offer_type": "paid"
        }

        response = client.post("/offers", json=offer_data, headers={"X-API-Key": "key123"})

        assert response.status_code == 201
        data = response.json()
        assert data["node_id"] == node.id
        assert data["cpu_cores_available"] == 4
        assert data["offer_type"] == "paid"
        assert data["approval_policy"] == "manual"
        assert data["active"] is True

    def test_create_offer_requires_authentication(self, client):
        """Test that creating offer requires API key."""
        offer_data = {
            "node_id": 1,
            "cpu_cores_available": 4,
            "ram_gb_available": 8.0,
            "storage_gb_available": 100.0,
            "offer_type": "paid"
        }

        response = client.post("/offers", json=offer_data)

        assert response.status_code == 401

    def test_create_offer_requires_node_ownership(self, client, db_session):
        """Test that users can only create offers for their own nodes."""
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

        # Bob tries to create offer for Alice's node
        offer_data = {
            "node_id": node.id,
            "cpu_cores_available": 4,
            "ram_gb_available": 8.0,
            "storage_gb_available": 100.0,
            "offer_type": "paid"
        }

        response = client.post("/offers", json=offer_data, headers={"X-API-Key": "key2"})

        assert response.status_code == 403

    def test_create_offer_validates_offer_type(self, client, db_session):
        """Test that offer_type must be 'paid' or 'free'."""
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

        offer_data = {
            "node_id": node.id,
            "cpu_cores_available": 4,
            "ram_gb_available": 8.0,
            "storage_gb_available": 100.0,
            "offer_type": "invalid"
        }

        response = client.post("/offers", json=offer_data, headers={"X-API-Key": "key123"})

        assert response.status_code == 422


class TestListResourceOffers:
    """Test suite for GET /offers endpoint."""

    def test_list_all_active_offers(self, client, db_session):
        """Test that all active offers are listed."""
        from src.database.models import User, Node, ResourceOffer

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
        db_session.flush()

        # Create multiple offers
        offer1 = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid",
            active=True
        )
        offer2 = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=2,
            ram_gb_available=4.0,
            storage_gb_available=50.0,
            offer_type="free",
            active=True
        )
        offer3 = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=1,
            ram_gb_available=2.0,
            storage_gb_available=25.0,
            offer_type="paid",
            active=False  # Inactive
        )
        db_session.add_all([offer1, offer2, offer3])
        db_session.commit()

        response = client.get("/offers", headers={"X-API-Key": "key123"})

        assert response.status_code == 200
        data = response.json()
        # Only active offers should be returned
        assert len(data) == 2

    def test_list_offers_requires_authentication(self, client):
        """Test that listing offers requires API key."""
        response = client.get("/offers")

        assert response.status_code == 401


class TestGetResourceOffer:
    """Test suite for GET /offers/{offer_id} endpoint."""

    def test_get_offer_by_id(self, client, db_session):
        """Test that offer details can be retrieved."""
        from src.database.models import User, Node, ResourceOffer

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
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid"
        )
        db_session.add(offer)
        db_session.commit()

        response = client.get(f"/offers/{offer.id}", headers={"X-API-Key": "key123"})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == offer.id
        assert data["node_id"] == node.id

    def test_get_offer_not_found(self, client, db_session):
        """Test that non-existent offer returns 404."""
        from src.database.models import User

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.commit()

        response = client.get("/offers/9999", headers={"X-API-Key": "key123"})

        assert response.status_code == 404


class TestUpdateResourceOffer:
    """Test suite for PATCH /offers/{offer_id} endpoint."""

    def test_update_offer_successfully(self, client, db_session):
        """Test that node owner can update their offer."""
        from src.database.models import User, Node, ResourceOffer

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
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid",
            active=True
        )
        db_session.add(offer)
        db_session.commit()

        update_data = {"cpu_cores_available": 6, "active": False}
        response = client.patch(
            f"/offers/{offer.id}",
            json=update_data,
            headers={"X-API-Key": "key123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["cpu_cores_available"] == 6
        assert data["active"] is False

    def test_update_offer_requires_node_ownership(self, client, db_session):
        """Test that users can only update offers for their own nodes."""
        from src.database.models import User, Node, ResourceOffer

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
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid"
        )
        db_session.add(offer)
        db_session.commit()

        # Bob tries to update Alice's offer
        update_data = {"active": False}
        response = client.patch(
            f"/offers/{offer.id}",
            json=update_data,
            headers={"X-API-Key": "key2"}
        )

        assert response.status_code == 403


class TestDeleteResourceOffer:
    """Test suite for DELETE /offers/{offer_id} endpoint."""

    def test_delete_offer_successfully(self, client, db_session):
        """Test that node owner can delete their offer."""
        from src.database.models import User, Node, ResourceOffer

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
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid"
        )
        db_session.add(offer)
        db_session.commit()

        offer_id = offer.id

        response = client.delete(f"/offers/{offer_id}", headers={"X-API-Key": "key123"})

        assert response.status_code == 204

        # Verify offer is deleted
        from src.database.models import ResourceOffer
        deleted_offer = db_session.query(ResourceOffer).filter_by(id=offer_id).first()
        assert deleted_offer is None

    def test_delete_offer_requires_node_ownership(self, client, db_session):
        """Test that users can only delete offers for their own nodes."""
        from src.database.models import User, Node, ResourceOffer

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
        db_session.flush()

        offer = ResourceOffer(
            node_id=node.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid"
        )
        db_session.add(offer)
        db_session.commit()

        # Bob tries to delete Alice's offer
        response = client.delete(f"/offers/{offer.id}", headers={"X-API-Key": "key2"})

        assert response.status_code == 403


class TestListNodeOffers:
    """Test suite for GET /nodes/{node_id}/offers endpoint."""

    def test_list_offers_for_specific_node(self, client, db_session):
        """Test that all offers for a specific node are listed."""
        from src.database.models import User, Node, ResourceOffer

        user = User(username="alice", email="alice@example.com", password_hash="h", api_key="key123")
        db_session.add(user)
        db_session.flush()

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
        db_session.flush()

        # Create offers for both nodes
        offer1 = ResourceOffer(
            node_id=node1.id,
            cpu_cores_available=4,
            ram_gb_available=8.0,
            storage_gb_available=100.0,
            offer_type="paid"
        )
        offer2 = ResourceOffer(
            node_id=node1.id,
            cpu_cores_available=2,
            ram_gb_available=4.0,
            storage_gb_available=50.0,
            offer_type="free"
        )
        offer3 = ResourceOffer(
            node_id=node2.id,
            cpu_cores_available=2,
            ram_gb_available=4.0,
            storage_gb_available=50.0,
            offer_type="paid"
        )
        db_session.add_all([offer1, offer2, offer3])
        db_session.commit()

        response = client.get(f"/nodes/{node1.id}/offers", headers={"X-API-Key": "key123"})

        assert response.status_code == 200
        data = response.json()
        # Only offers for node1
        assert len(data) == 2
        assert all(offer["node_id"] == node1.id for offer in data)
