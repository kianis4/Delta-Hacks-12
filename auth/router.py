"""
Authentication router for FastAPI.

Endpoints:
- POST /auth/register: Register new user
- POST /auth/login: Login user
- POST /auth/logout: Logout user
- GET /auth/me: Get current user info
"""

from fastapi import APIRouter, HTTPException, status, Response, Depends, Request
from pymongo.errors import DuplicateKeyError
from .models import UserRegister, UserLogin, UserResponse
from .database import auth_db
from .security import hash_password, verify_password, get_session_expiry
from .dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

# Session cookie configuration
SESSION_COOKIE_NAME = "juris_session"
SESSION_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, response: Response, request: Request):
    """
    Register a new user account.
    
    - Email must be unique
    - Password must be at least 8 characters
    - Creates user and automatically logs them in with a session cookie
    """
    try:
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        user = auth_db.create_user(
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name
        )
        
        # Create session for automatic login
        session = auth_db.create_session(
            user_id=str(user["_id"]),
            expires_at=get_session_expiry(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Set HttpOnly cookie
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=str(session["_id"]),
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=SESSION_MAX_AGE
        )
        
        # Return user data (without password hash)
        return UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            full_name=user.get("full_name"),
            created_at=user["created_at"]
        )
        
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin, response: Response, request: Request):
    """
    Login with email and password.
    
    - Creates a session valid for 7 days
    - Sets HttpOnly cookie for session management
    """
    # Find user by email
    user = auth_db.get_user_by_email(credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create session
    session = auth_db.create_session(
        user_id=str(user["_id"]),
        expires_at=get_session_expiry(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    # Set HttpOnly cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=str(session["_id"]),
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=SESSION_MAX_AGE
    )
    
    # Return user data
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user.get("full_name"),
        created_at=user["created_at"]
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, user: dict = Depends(get_current_user)):
    """
    Logout current user.
    
    - Deletes session from database
    - Removes session cookie
    """
    # Get session ID from cookie (already validated by dependency)
    # We need to get it again from the response context
    # The session was already validated by get_current_user, so we'll delete all user sessions
    user_id = str(user["_id"])
    auth_db.delete_user_sessions(user_id)
    
    # Clear cookie
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    
    return None


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires valid session cookie.
    """
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user.get("full_name"),
        created_at=user["created_at"]
    )


@router.post("/cleanup-sessions")
async def cleanup_expired_sessions():
    """
    Admin endpoint to manually clean up expired sessions.
    
    In production, this should be:
    1. Protected with admin authentication
    2. Run as a scheduled background task
    """
    deleted_count = auth_db.cleanup_expired_sessions()
    return {"deleted_sessions": deleted_count}
