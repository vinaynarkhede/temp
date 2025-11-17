"""
Resource offer API endpoints.

Handles marketplace offer creation, updates, and queries.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import ResourceOffer, Node, User
from src.api.marketplace_models import (
    ResourceOfferCreate,
    ResourceOfferUpdate,
    ResourceOfferResponse
)
from src.api.auth import get_current_user


router = APIRouter()


@router.post("", response_model=ResourceOfferResponse, status_code=status.HTTP_201_CREATED)
async def create_resource_offer(
    offer_data: ResourceOfferCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new resource offer.

    Args:
        offer_data: Resource offer creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created resource offer

    Raises:
        HTTPException: If node not found or user not authorized
    """
    # Verify node exists and user owns it
    node = db.query(Node).filter(Node.id == offer_data.node_id).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    if node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create offer for this node"
        )

    # Create offer
    offer = ResourceOffer(
        node_id=offer_data.node_id,
        cpu_cores_available=offer_data.cpu_cores_available,
        ram_gb_available=offer_data.ram_gb_available,
        storage_gb_available=offer_data.storage_gb_available,
        offer_type=offer_data.offer_type,
        approval_policy=offer_data.approval_policy,
        trusted_users=offer_data.trusted_users,
        active=True
    )

    db.add(offer)
    db.commit()
    db.refresh(offer)

    return ResourceOfferResponse.model_validate(offer)


@router.get("", response_model=List[ResourceOfferResponse])
async def list_resource_offers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all active resource offers (marketplace view).

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of active resource offers
    """
    offers = db.query(ResourceOffer).filter(ResourceOffer.active == True).all()

    return [ResourceOfferResponse.model_validate(offer) for offer in offers]


@router.get("/{offer_id}", response_model=ResourceOfferResponse)
async def get_resource_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific resource offer.

    Args:
        offer_id: Offer ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Resource offer information

    Raises:
        HTTPException: If offer not found
    """
    offer = db.query(ResourceOffer).filter(ResourceOffer.id == offer_id).first()

    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource offer not found"
        )

    return ResourceOfferResponse.model_validate(offer)


@router.patch("/{offer_id}", response_model=ResourceOfferResponse)
async def update_resource_offer(
    offer_id: int,
    offer_update: ResourceOfferUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a resource offer.

    Allows partial updates - only provided fields will be updated.

    Args:
        offer_id: Offer ID
        offer_update: Fields to update
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated resource offer

    Raises:
        HTTPException: If offer not found or user not authorized
    """
    offer = db.query(ResourceOffer).filter(ResourceOffer.id == offer_id).first()

    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource offer not found"
        )

    # Check node ownership
    node = db.query(Node).filter(Node.id == offer.node_id).first()
    if node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this offer"
        )

    # Update only provided fields
    update_data = offer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(offer, field, value)

    db.commit()
    db.refresh(offer)

    return ResourceOfferResponse.model_validate(offer)


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a resource offer.

    Args:
        offer_id: Offer ID
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: If offer not found or user not authorized
    """
    offer = db.query(ResourceOffer).filter(ResourceOffer.id == offer_id).first()

    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource offer not found"
        )

    # Check node ownership
    node = db.query(Node).filter(Node.id == offer.node_id).first()
    if node.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this offer"
        )

    db.delete(offer)
    db.commit()
