"""
MongoDB schemas and Pydantic models for authentication.

Collections:
- users: Stores user accounts
- sessions: Stores active sessions
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


# Pydantic models for API requests/responses
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        json_encoders = {
            ObjectId: str
        }


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    expires_at: datetime


# MongoDB document structures (for reference)
"""
users collection:
{
    "_id": ObjectId,
    "email": str (unique, indexed),
    "password_hash": str,
    "full_name": str (optional),
    "created_at": datetime,
    "updated_at": datetime
}

sessions collection:
{
    "_id": ObjectId (used as session_id),
    "user_id": ObjectId (reference to users._id),
    "created_at": datetime,
    "expires_at": datetime,
    "ip_address": str (optional),
    "user_agent": str (optional)
}
"""
