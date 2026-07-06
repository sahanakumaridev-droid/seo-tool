"""
auth.py — Authentication endpoints
Supports JWT tokens, refresh tokens, and OAuth2
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from auth import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    hash_password,
    verify_password,
    User,
    TokenResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# In-memory user store (replace with database in production)
_users = {}


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    """Register a new user."""
    if req.email in _users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = req.email.split("@")[0]
    hashed_password = hash_password(req.password)
    
    _users[req.email] = {
        "user_id": user_id,
        "email": req.email,
        "name": req.name,
        "password": hashed_password,
        "is_active": True
    }
    
    access_token = create_access_token(user_id, req.email)
    refresh_token = create_refresh_token(user_id, req.email)
    
    logger.info(f"User registered: {req.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60  # 30 minutes
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Login with email and password."""
    user = _users.get(req.email)
    
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    access_token = create_access_token(user["user_id"], req.email)
    refresh_token = create_refresh_token(user["user_id"], req.email)
    
    logger.info(f"User logged in: {req.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    from jose import jwt
    from config import settings
    
    try:
        payload = jwt.decode(
            req.refresh_token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        access_token = create_access_token(user_id, email)
        refresh_token = create_refresh_token(user_id, email)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout (client should discard token)."""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out successfully"}
