from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional
from datetime import datetime, date
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string")


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Email address")
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number")
    birthdate: date = Field(..., description="Date of birth")
    birthtime: str = Field(..., description="Time of birth (HH:MM format)")
    birth_location: str = Field(..., min_length=2, max_length=200, description="Location of birth")
    
    @validator('birthtime')
    def validate_birthtime(cls, v):
        try:
            datetime.strptime(v, "%H:%M %p")
            return v
        except ValueError:
            raise ValueError("Birth time must be in HH:MM format")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15)
    birthdate: Optional[date] = None
    birthtime: Optional[str] = None
    birth_location: Optional[str] = Field(None, min_length=2, max_length=200)
    
    @validator('birthtime')
    def validate_birthtime(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, "%H:%M %p")
                return v
            except ValueError:
                raise ValueError("Birth time must be in HH:MM format")
        return v


class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    model_config = ConfigDict(
        validate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class UserResponse(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(
        validate_by_name=True,
        json_encoders={ObjectId: str, datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v}
    )
    
    @validator('birthdate', pre=True)
    def convert_birthdate(cls, v):
        """Convert datetime to date for response"""
        if isinstance(v, datetime):
            return v.date()
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
