from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class VisionRequest(BaseModel):
    image_base64: str

class ChatMessage(BaseModel):
    role: str
    content: Any # Can be str or list for vision

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class RiskAnalysisRequest(BaseModel):
    ingredients: List[str]

class CalendarLinkRequest(BaseModel):
    event_name: str
    time_str: str
    location: str

class IcsContentRequest(BaseModel):
    event_name: str
    time_str: str
    location: str

class HistoryResponse(BaseModel):
    id: int
    timestamp: datetime
    category: str
    title: str
    summary: str
    owner_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    medical_history: Optional[str] = None
    preferences: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    medical_history: Optional[str] = None
    preferences: Optional[str] = None
    history: List[HistoryResponse] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
