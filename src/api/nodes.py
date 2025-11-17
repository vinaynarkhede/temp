"""
Node management API endpoints.

Handles node registration, updates, and queries.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import Node, User, ResourceOffer
from src.api.marketplace_models import NodeRegister, NodeUpdate, NodeResponse, ResourceOfferResponse
from src.api.auth import get_current_user


router = APIRouter()


@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def register_node(
    node_data: NodeRegister,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a new compute node.

    Args:
        node_data: Node registration data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created node information

    Raises:
        HTTPException: If validation fails
    """
    # Create node
    node = Node(
        owner_id=current_user.id,
        name=node_data.name,
        tailscale_ip=node_data.tailscale_ip,
        cpu_cores=node_data.cpu_cores,
        ram_gb=node_data.ram_gb,
        storage_gb=node_data.storage_gb,
        status="offline"  # Default to offline until first heartbeat
    )

    db.add(node)
    db.commit()
    db.refresh(node)

    return NodeResponse.model_validate(node)


@router.get("", response_model=List[NodeResponse])
async def list_nodes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all nodes owned by the current user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of user's nodes
    """
    nodes = db.query(Node).filter(Node.owner_id == current_user.id).all()

    return [NodeResponse.model_validate(node) for node in nodes]


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific node.

    Args:
        node_id: Node ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Node information

    Raises:
        HTTPException: If node not found or user not authorized
    """
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Check ownership
    if node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this node"
        )

    return NodeResponse.model_validate(node)


@router.patch("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: int,
    node_update: NodeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update node information.

    Allows partial updates - only provided fields will be updated.

    Args:
        node_id: Node ID
        node_update: Fields to update
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated node information

    Raises:
        HTTPException: If node not found or user not authorized
    """
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Check ownership
    if node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this node"
        )

    # Update only provided fields
    update_data = node_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(node, field, value)

    db.commit()
    db.refresh(node)

    return NodeResponse.model_validate(node)


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a node.

    Args:
        node_id: Node ID
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: If node not found or user not authorized
    """
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Check ownership
    if node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this node"
        )

    db.delete(node)
    db.commit()


@router.get("/{node_id}/offers", response_model=List[ResourceOfferResponse])
async def list_node_offers(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all resource offers for a specific node.

    Args:
        node_id: Node ID
        current_user: Authenticated user
        db: Database session

    Returns:
        List of resource offers for the node

    Raises:
        HTTPException: If node not found or user not authorized
    """
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    # Check ownership
    if node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this node's offers"
        )

    # Get all offers for this node
    offers = db.query(ResourceOffer).filter(ResourceOffer.node_id == node_id).all()

    return [ResourceOfferResponse.model_validate(offer) for offer in offers]
