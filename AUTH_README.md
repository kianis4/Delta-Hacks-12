# Juris Authentication System

## 📋 Overview

A complete authentication system for Juris AI legal assistant, implementing secure user authentication with MongoDB persistence, HttpOnly cookies, and session management.

## 🏗️ Architecture

### Backend (FastAPI)
```
agent/
├── auth/
│   ├── models.py          # Pydantic models & DB schemas
│   ├── security.py        # Password hashing & session utils
│   ├── database.py        # MongoDB operations
│   ├── dependencies.py    # Auth middleware
│   └── router.py          # Auth endpoints
├── protected_routes.py    # Example protected APIs
└── server.py              # Main FastAPI application
```

### Frontend (Next.js)
```
web/
├── lib/
│   ├── auth-api.ts        # API client
│   └── auth-context.tsx   # Global auth state
└── app/
    ├── login/             # Login page
    ├── register/          # Registration page
    └── dashboard/         # Protected dashboard
```

## 🔐 Security Features

- ✅ **bcrypt password hashing** with salt
- ✅ **HttpOnly cookies** for session management (XSS protection)
- ✅ **SameSite=lax** cookies (CSRF protection)
- ✅ **Server-side session storage** in MongoDB
- ✅ **7-day session expiry** with automatic cleanup
- ✅ **Email validation** and password strength requirements
- ✅ **Unique email constraint** with proper error handling

## 📊 Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique, indexed),
  password_hash: String,
  full_name: String (optional),
  created_at: DateTime,
  updated_at: DateTime
}
```

### Sessions Collection
```javascript
{
  _id: ObjectId,  // Used as session_id
  user_id: ObjectId,  // Reference to users
  created_at: DateTime,
  expires_at: DateTime,
  ip_address: String (optional),
  user_agent: String (optional)
}
```

## 🚀 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with email/password
- `POST /auth/logout` - Logout (clear session)
- `GET /auth/me` - Get current user info

### Protected Examples (Placeholders)
- `GET /api/cases` - User's legal cases
- `GET /api/checklist` - User's checklist items
- `GET /api/reminders` - User's reminders

## 🔄 Authentication Flow

1. **Registration/Login**
   ```
   Client → POST /auth/register or /auth/login
           → Backend validates credentials
           → Backend creates session in MongoDB
           → Backend sets HttpOnly cookie
           ← Returns user data
   ```

2. **Authenticated Requests**
   ```
   Client → Any request (cookie auto-sent)
           → Backend validates session from cookie
           → Backend checks session expiry
           → Backend retrieves user from session
           ← Returns protected data
   ```

3. **Logout**
   ```
   Client → POST /auth/logout
           → Backend deletes session from DB
           → Backend clears cookie
           ← Success
   ```

## 🛠️ Setup Instructions

### 1. Backend Setup
```bash
cd agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URI
python -m uvicorn server:app --reload
```

### 2. Frontend Setup
```bash
cd web
npm install
npm run dev
```

### 3. MongoDB Setup
See [MONGODB_SETUP_INSTRUCTIONS.txt](./MONGODB_SETUP_INSTRUCTIONS.txt)

## 💻 Usage Examples

### Frontend - Login
```typescript
import { useAuth } from '@/lib/auth-context';

function LoginComponent() {
  const { login } = useAuth();
  
  const handleSubmit = async () => {
    await login(email, password);
    // Automatically redirects to dashboard
  };
}
```

### Frontend - Protected Route
```typescript
import { useAuth } from '@/lib/auth-context';

function ProtectedPage() {
  const { user, loading } = useAuth();
  
  if (!user) return <div>Please login</div>;
  
  return <div>Welcome {user.email}</div>;
}
```

### Backend - Protected Endpoint
```python
from fastapi import APIRouter, Depends
from auth.dependencies import get_current_user

router = APIRouter()

@router.get("/my-data")
async def get_user_data(user: dict = Depends(get_current_user)):
    user_id = str(user["_id"])
    # Query user-specific data
    return {"data": []}
```

## 🔌 Frontend API Client

All auth operations use the `AuthAPI` class with `credentials: 'include'`:

```typescript
import { AuthAPI } from '@/lib/auth-api';

// Register
await AuthAPI.register({ 
  email, 
  password, 
  full_name 
});

// Login
await AuthAPI.login({ email, password });

// Logout
await AuthAPI.logout();

// Get current user
const user = await AuthAPI.getCurrentUser();
```

## 🧪 Testing

### Manual Testing Flow
1. Visit `http://localhost:3000/register`
2. Create an account
3. Verify redirect to dashboard
4. Check browser cookies for `juris_session`
5. Test logout
6. Try accessing `/dashboard` while logged out
7. Login again

### API Testing (Swagger UI)
Visit `http://localhost:8000/docs` to test endpoints interactively.

## 📝 Configuration

### Backend (.env)
```bash
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=juris
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚨 Production Checklist

Before deploying:
- [ ] Set `secure=True` for cookies (requires HTTPS)
- [ ] Update CORS origins to production domain
- [ ] Add rate limiting
- [ ] Implement session cleanup cron job
- [ ] Add monitoring/logging
- [ ] Configure MongoDB backups
- [ ] Use strong environment-specific secrets
- [ ] Add email verification (optional)
- [ ] Implement refresh tokens (optional)

## 🔧 Extending the System

### Add Password Reset
1. Create password_reset_tokens collection
2. Add `/auth/forgot-password` endpoint
3. Implement email sending
4. Add reset password UI

### Add OAuth
1. Install OAuth library (e.g., authlib)
2. Add OAuth provider endpoints
3. Link OAuth accounts to users
4. Add OAuth buttons to UI

### Add Roles/Permissions
1. Add `role` field to users
2. Create role-checking dependencies
3. Update UI based on roles

## 📚 Documentation

- [Complete Setup Guide](./AUTH_SETUP_GUIDE.txt)
- [MongoDB Setup Instructions](./MONGODB_SETUP_INSTRUCTIONS.txt)

## 🤝 Integration with Existing AI System

The authentication system is **completely separate** from the AI logic:
- ✅ LangGraph agents unchanged
- ✅ AI chat flow unchanged
- ✅ Auth is ONLY for persistence layer
- ✅ Chat endpoint remains public (can be protected later)

To protect the chat endpoint:
```python
from auth.dependencies import get_current_user

@app.post("/chat")
async def chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    # Now requires authentication
    # Can associate conversations with user_id
```

## ⚠️ Important Notes

- **Cookies must be HttpOnly** - Already configured
- **Always use `credentials: 'include'`** in frontend fetch calls
- **Sessions expire after 7 days** - Configurable in security.py
- **Passwords must be 8+ characters** - Enforced on both ends
- **Email must be unique** - MongoDB unique index enforces this

## 🐛 Troubleshooting

### "Not authenticated" after login
- Check browser cookies for `juris_session`
- Verify `credentials: 'include'` in all fetch calls
- Check CORS middleware allows credentials

### CORS errors
- Verify frontend origin in CORS middleware
- Ensure `allow_credentials=True`

### MongoDB connection fails
- Check connection string format
- Verify IP whitelist in Atlas
- Test connection with MongoDB Compass

## 📖 Key Concepts

### Why HttpOnly Cookies?
- Cannot be accessed by JavaScript
- Prevents XSS attacks from stealing tokens
- Automatically sent with requests
- More secure than localStorage

### Why Server-Side Sessions?
- Can revoke access immediately
- Can track active sessions
- Can implement "logout everywhere"
- More control than JWT

### Why bcrypt?
- Industry standard for password hashing
- Includes salt automatically
- Configurable difficulty
- Resistant to rainbow tables

---

**Built for Delta Hacks 12** 🎯
