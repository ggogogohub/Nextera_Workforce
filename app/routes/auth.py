from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserCreate
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from pydantic import BaseModel

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize MongoDB client globally to avoid reconnecting on each request
db_client = AsyncIOMotorClient(settings.MONGODB_URL)
db = db_client.nextgen

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generate a JWT token with an optional expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

class UpdateProfileRequest(BaseModel):
    """Model for updating user profile."""
    current_password: str
    new_full_name: Optional[str] = None
    new_password: Optional[str] = None

@router.post("/register")
async def register(user: UserCreate):
    """Register a new user with hashed password and save to MongoDB."""
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    user_dict = user.dict()
    user_dict['hashed_password'] = hashed_password
    del user_dict['password']
    
    await db.users.insert_one(user_dict)
    return {"message": "User created successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Verify user credentials and return a JWT access token."""
    user = await db.users.find_one({"email": form_data.username})
    
    if not user or not pwd_context.verify(form_data.password, user['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile")
async def get_profile(email: str):
    """Retrieve user profile by email, excluding sensitive fields."""
    user = await db.users.find_one({"email": email}, {"_id": 0, "hashed_password": 0})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/profile")
async def update_profile(update_request: UpdateProfileRequest, email: str):
    """Update user profile information (full name and/or password) after verifying the current password."""
    user = await db.users.find_one({"email": email})
    
    if not user or not pwd_context.verify(update_request.current_password, user['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    update_data = {}
    if update_request.new_full_name:
        update_data['full_name'] = update_request.new_full_name
    if update_request.new_password:
        update_data['hashed_password'] = pwd_context.hash(update_request.new_password)
    
    if update_data:
        await db.users.update_one({"email": email}, {"$set": update_data})
    
    return {"message": "Profile updated successfully"}

@router.delete("/profile")
async def delete_profile(email: str, password: str):
    """Delete a user profile after verifying email and password."""
    user = await db.users.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not pwd_context.verify(password, user['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    await db.users.delete_one({"email": email})
    return {"message": "User deleted successfully"}
