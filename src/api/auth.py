"""
Authentication endpoints for user registration and login.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.api.models import UserRegister, UserLogin, UserResponse
from src.database.connection import get_db
from src.database.models import User
from src.utils.security import hash_password, verify_password, generate_api_key

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Creates a new user account with:
    - Hashed password (bcrypt)
    - Generated API key (cryptographically secure)
    - Initial credit balance of 100

    Args:
        user_data: User registration data (username, email, password)
        db: Database session (injected)

    Returns:
        UserResponse: Created user data with API key

    Raises:
        HTTPException 409: If username or email already exists
        HTTPException 422: If validation fails (handled by Pydantic)
    """
    logger.info(f"Registration attempt for username: {user_data.username}")

    # Hash password
    password_hash = hash_password(user_data.password)

    # Generate API key
    api_key = generate_api_key()

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        api_key=api_key,
        credit_balance=100  # Initial credits as per specification
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"User registered successfully: {user.username} (ID: {user.id})")

        # Return user data with API key
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            api_key=user.api_key,
            credit_balance=user.credit_balance,
            created_at=user.created_at
        )

    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()

        # Determine which field caused the conflict
        if 'username' in error_msg:
            logger.warning(f"Registration failed: Username '{user_data.username}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{user_data.username}' is already registered"
            )
        elif 'email' in error_msg:
            logger.warning(f"Registration failed: Email '{user_data.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{user_data.email}' is already registered"
            )
        elif 'api_key' in error_msg:
            # This should be extremely rare (API key collision)
            logger.error(f"API key collision during registration for user: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error during registration. Please try again."
            )
        else:
            # Unknown integrity error
            logger.error(f"Unknown integrity error during registration: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error during registration"
            )


@router.post("/login", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login an existing user.

    Authenticates user credentials and returns user data with API key.

    Args:
        login_data: User login credentials (username, password)
        db: Database session (injected)

    Returns:
        UserResponse: User data with API key

    Raises:
        HTTPException 401: If credentials are invalid
    """
    logger.info(f"Login attempt for username: {login_data.username}")

    # Query user by username
    user = db.query(User).filter(User.username == login_data.username).first()

    # Check if user exists
    if not user:
        logger.warning(f"Login failed: User '{login_data.username}' not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"Login failed: Invalid password for user '{login_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    logger.info(f"User logged in successfully: {user.username} (ID: {user.id})")

    # Return user data with API key
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        api_key=user.api_key,
        credit_balance=user.credit_balance,
        created_at=user.created_at
    )
