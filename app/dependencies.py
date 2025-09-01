from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .database import get_database
from .auth import verify_token
from .models.user import TokenData, UserInDB
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> UserInDB:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    # Find user by email
    user_dict = await database.users.find_one({"email": token_data.email})
    if user_dict is None:
        raise credentials_exception
    
    # Convert ObjectId to string for Pydantic
    user_dict["_id"] = str(user_dict["_id"])
    
    # Convert birthdate from datetime to date if needed
    if isinstance(user_dict.get("birthdate"), datetime):
        user_dict["birthdate"] = user_dict["birthdate"].date()
    
    return UserInDB(**user_dict)


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Get current active user."""
    print("current_user", current_user)
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
