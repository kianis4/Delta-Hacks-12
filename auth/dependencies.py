"""
FastAPI dependency for authentication middleware.
"""

from typing import Optional
from fastapi import Cookie, HTTPException, status
from .database import auth_db
from .security import is_session_expired


async def get_current_user(session_id: Optional[str] = Cookie(None, alias="juris_session")):
    """
    Dependency to get the current authenticated user from session cookie.
    
    Args:
        session_id: Session ID from HttpOnly cookie
        
    Returns:
        User document
        
    Raises:
        HTTPException: If not authenticated or session invalid
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Get session from database
    session = auth_db.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    # Check if session expired
    if is_session_expired(session["expires_at"]):
        auth_db.delete_session(session_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Get user
    user = auth_db.get_user_by_id(str(session["user_id"]))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_optional_user(session_id: Optional[str] = Cookie(None, alias="juris_session")):
    """
    Dependency to optionally get the current user (doesn't raise if not authenticated).
    
    Args:
        session_id: Session ID from HttpOnly cookie
        
    Returns:
        User document or None
    """
    if not session_id:
        return None
    
    try:
        return await get_current_user(session_id)
    except HTTPException:
        return None
