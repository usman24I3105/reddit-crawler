"""
Authentication routes for worker login.
Simple implementation for development.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import secrets

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    token: str
    worker_id: str
    message: str = "Login successful"


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Simple login endpoint.
    For development: accepts any email/password.
    Returns a mock JWT token.
    """
    # For development, accept any credentials
    # In production, validate against database
    
    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Generate a simple token (in production, use proper JWT)
    token = f"worker_token_{secrets.token_urlsafe(16)}"
    
    # Extract worker ID from email (or use email as worker_id)
    worker_id = request.email.split('@')[0] if '@' in request.email else request.email
    
    return LoginResponse(
        token=token,
        worker_id=worker_id,
        message="Login successful"
    )





