"""
MongoDB database connection and operations for authentication.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()


class AuthDatabase:
    """
    Handles all database operations for authentication.
    """
    
    def __init__(self):
        """Initialize MongoDB connection."""
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI environment variable not set")
        
        self.client = MongoClient(mongo_uri)
        db_name = os.getenv("MONGODB_DB_NAME", "juris")
        self.db = self.client[db_name]
        
        # Collections
        self.users = self.db.users
        self.sessions = self.db.sessions
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes for performance and uniqueness."""
        # Unique index on email
        self.users.create_index([("email", ASCENDING)], unique=True)
        
        # Index on user_id for sessions (for faster lookups)
        self.sessions.create_index([("user_id", ASCENDING)])
        
        # Index on expires_at for automatic cleanup
        self.sessions.create_index([("expires_at", ASCENDING)])
    
    # User operations
    def create_user(self, email: str, password_hash: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            email: User email (must be unique)
            password_hash: Hashed password
            full_name: Optional full name
            
        Returns:
            Created user document
            
        Raises:
            Exception if email already exists
        """
        user_doc = {
            "email": email.lower(),
            "password_hash": password_hash,
            "full_name": full_name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return user_doc
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find user by email.
        
        Args:
            email: User email to search for
            
        Returns:
            User document or None if not found
        """
        return self.users.find_one({"email": email.lower()})
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find user by ID.
        
        Args:
            user_id: User ObjectId as string
            
        Returns:
            User document or None if not found
        """
        try:
            return self.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None
    
    # Session operations
    def create_session(self, user_id: str, expires_at: datetime, 
                      ip_address: Optional[str] = None, 
                      user_agent: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            user_id: User ObjectId as string
            expires_at: Session expiry datetime
            ip_address: Optional IP address
            user_agent: Optional user agent string
            
        Returns:
            Created session document
        """
        session_doc = {
            "user_id": ObjectId(user_id),
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        result = self.sessions.insert_one(session_doc)
        session_doc["_id"] = result.inserted_id
        return session_doc
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ObjectId as string
            
        Returns:
            Session document or None if not found
        """
        try:
            return self.sessions.find_one({"_id": ObjectId(session_id)})
        except Exception:
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session (logout).
        
        Args:
            session_id: Session ObjectId as string
            
        Returns:
            True if deleted, False if not found
        """
        try:
            result = self.sessions.delete_one({"_id": ObjectId(session_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    def delete_user_sessions(self, user_id: str) -> int:
        """
        Delete all sessions for a user.
        
        Args:
            user_id: User ObjectId as string
            
        Returns:
            Number of sessions deleted
        """
        try:
            result = self.sessions.delete_many({"user_id": ObjectId(user_id)})
            return result.deleted_count
        except Exception:
            return 0
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions from database.
        
        Returns:
            Number of sessions deleted
        """
        result = self.sessions.delete_many({"expires_at": {"$lt": datetime.utcnow()}})
        return result.deleted_count


# Global database instance
auth_db = AuthDatabase()
