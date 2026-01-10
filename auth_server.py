"""
Auth-enabled server wrapper for Juris.

This file extends the original server.py with authentication endpoints
WITHOUT modifying the original file to avoid merge conflicts.

Usage:
    python auth_server.py

Or with uvicorn:
    uvicorn auth_server:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the original app routes
from agent.server import app as original_app, ChatRequest, chat, health

# Import auth components
from auth.router import router as auth_router
from protected_routes import router as protected_router

# Create new app with auth
app = FastAPI(
    title="Juris API with Authentication",
    description="AI-powered legal assistance with user authentication"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routers
app.include_router(auth_router)
app.include_router(protected_router)

# Mount original endpoints
app.post("/chat")(chat)
app.get("/health")(health)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
