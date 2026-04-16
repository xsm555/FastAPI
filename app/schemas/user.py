# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# --- 注册请求 ---
class UserCreate(BaseModel):
    # BaseModel 是 Pydantic 提供的基类，用于定义数据模型，自动进行数据验证和转换
    email: EmailStr
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

# --- 登录请求 ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- 响应模型 ---
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Token 响应 ---
class Token(BaseModel):
    access_token: str
    token_type: str