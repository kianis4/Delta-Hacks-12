# Understanding auth_server.py - How It Works
=====================================================

## The Problem We Solved

You didn't want to modify existing files (server.py, requirements.txt) to avoid merge conflicts.
But we need to add auth endpoints to your FastAPI server.

## The Solution: Wrapper Pattern

Instead of modifying server.py, we created auth_server.py that:
1. Imports your original endpoints
2. Adds auth endpoints
3. Combines them into one server

## How It Works

### Your Original server.py (UNCHANGED):
```python
# agent/server.py
from fastapi import FastAPI

app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    # Your AI chat logic
    pass

@app.get("/health")
def health():
    return {"status": "ok"}
```

### New auth_server.py (Wrapper):
```python
# auth_server.py (top-level)
from fastapi import FastAPI
from agent.server import chat, health  # Import original functions
from auth.router import router as auth_router

app = FastAPI()

# Mount original endpoints
app.post("/chat")(chat)
app.get("/health")(health)

# Add new auth endpoints
app.include_router(auth_router)  # Adds /auth/login, /auth/register, etc.
```

## Result

When you run `python auth_server.py`, you get ONE server with:

### Original Endpoints (from server.py):
- POST /chat
- GET /health

### New Auth Endpoints:
- POST /auth/register
- POST /auth/login
- POST /auth/logout
- GET /auth/me

### New Protected Endpoints:
- GET /api/cases
- GET /api/checklist
- GET /api/reminders

## Why This Is Better

✅ **No Merge Conflicts**: server.py is untouched
✅ **Modular**: Auth can be removed easily
✅ **Team Friendly**: Teammates can use original server
✅ **Flexible**: Run with or without auth

## Running Options

### Option 1: With Auth (Recommended)
```bash
python auth_server.py
# or
uvicorn auth_server:app --reload
```
Gives you: Original endpoints + Auth endpoints

### Option 2: Without Auth (Original)
```bash
cd agent
python -m uvicorn server:app --reload
```
Gives you: Only original endpoints

## Why Not Just Modify server.py?

You could, but:
❌ Creates merge conflicts
❌ Harder for teammates to opt-out
❌ Mixes auth code with AI code
❌ Harder to remove later

With auth_server.py:
✅ Original code untouched
✅ Auth is separate module
✅ Easy to opt-in or opt-out
✅ Clean separation of concerns

## Technical Details

### How Mounting Works

FastAPI allows you to "mount" existing route handlers:

```python
# Original definition
@app.post("/chat")
async def chat(...):
    pass

# Mount it in new app
new_app.post("/chat")(chat)
```

This reuses the same function without modifying the original file!

### Import Path

auth_server.py imports from agent.server:
```python
from agent.server import app as original_app, ChatRequest, chat, health
```

This works because:
1. auth_server.py is at project root
2. agent/ is a package (has Python files)
3. Python can import from agent.server

## For Your Teammates

When they pull your code:
1. They see new files (auth/, auth_server.py)
2. Their agent/server.py is UNCHANGED
3. They can choose:
   - Use auth_server.py (opt-in)
   - Keep using agent/server.py (opt-out)

No breaking changes!

## Future: Integrating Auth with Chat

Right now /chat is public (no auth required).

To protect it later, you could:

### Option A: Modify Protected copy (no conflict)
Create a new protected_chat.py:
```python
from fastapi import Depends
from agent.server import chat as original_chat
from auth.dependencies import get_current_user

async def protected_chat(request, user = Depends(get_current_user)):
    # Add user_id to request
    request.user_id = str(user["_id"])
    return await original_chat(request)
```

Then in auth_server.py:
```python
app.post("/chat")(protected_chat)  # Use protected version
```

### Option B: Optional Auth
```python
from auth.dependencies import get_optional_user

async def chat_with_optional_auth(request, user = Depends(get_optional_user)):
    if user:
        # Logged in: save chat history
        pass
    # Continue with regular chat
```

Original server.py still untouched!

## Summary

auth_server.py is a **wrapper** that:
- Imports your original code
- Adds new functionality
- Doesn't modify original files

This pattern is common in Python when you want to extend existing code
without creating merge conflicts.

Perfect for team environments and hackathons!
