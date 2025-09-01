from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..database import get_database
from ..auth import get_password_hash
from ..models.user import UserUpdate, UserResponse, UserCreate
from ..dependencies import get_current_active_user
from datetime import datetime, date
from bson import ObjectId

router = APIRouter(prefix="/users", tags=["Users"])


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_active_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update user profile information."""
    # Prepare update data
    update_data = user_update.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    # Check if email is being updated and if it's already taken
    if "email" in update_data:
        del update_data['email']
    
    # Convert date to datetime for MongoDB compatibility
    if "birthdate" in update_data and isinstance(update_data["birthdate"], date):
        update_data["birthdate"] = datetime.combine(update_data["birthdate"], datetime.min.time())
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update user in database
    result = await database.users.update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get updated user data
    updated_user = await database.users.find_one({"_id": current_user.id})
    return UserResponse(**updated_user)


@router.get("", response_model=UserResponse)
async def get_profile(
    current_user = Depends(get_current_active_user)
):
    """Get current user profile."""
    return current_user


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user = Depends(get_current_active_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete user profile (soft delete by setting is_active to False)."""
    result = await database.users.update_one(
        {"_id": current_user.id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )