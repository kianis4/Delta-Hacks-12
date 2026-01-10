"""
Security utilities for password hashing and session management.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        password: Plain text password to check
        password_hash: Stored hash to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def generate_session_id() -> str:
    """
    Generate a secure random session ID.
    
    Returns:
        Random hex string suitable for session identification
    """
    return secrets.token_hex(32)


def get_session_expiry(days: int = 7) -> datetime:
    """
    Calculate session expiry time.
    
    Args:
        days: Number of days until session expires (default: 7)
        
    Returns:
        Datetime object representing expiry time
    """
    return datetime.utcnow() + timedelta(days=days)


def is_session_expired(expires_at: datetime) -> bool:
    """
    Check if a session has expired.
    
    Args:
        expires_at: Session expiry datetime
        
    Returns:
        True if expired, False otherwise
    """
    return datetime.utcnow() > expires_at
