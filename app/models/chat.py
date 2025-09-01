from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class ChatMessage(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    message: str
    is_user_message: bool = True  # True for user message, False for AI response
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v}
    )


class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Chat message content")


class ChatMessageResponse(BaseModel):
    id: str
    message: str
    response: str
    is_user_message: bool
    created_at: datetime

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v}
    )


class ChatSession(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    messages: list[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v}
    )
