from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import uuid


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str


class VerifyTokenRequest(BaseModel):
    refresh_token: str


class ExpenseCreate(BaseModel):
    title: str
    desc: str
    amount: float
    category: str
    type: str


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    type: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    desc: str
    amount: float
    category: str
    type: str
    created_at: datetime

    class Config:
        from_attributes = True