# JWT逻辑
# app/core/security.py
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional,Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# 配置
SECRET_KEY = "your_secret_key_change_this_in_production" # 生产环境要换复杂的
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """验证密码：明文 vs 密文"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """生成 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 这行代码告诉 FastAPI：Token 放在 Header 的 Authorization 字段里，格式是 Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login") # 指向你的登录接口地址

# ==========================
# 【新增】获取当前用户的依赖函数
# ==========================
async def get_current_user(
    token: str = Depends(oauth2_scheme), # 自动从请求头获取 Token
    db: AsyncSession = Depends(get_db)   # 获取数据库会话
):
    # 定义异常信息
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, # 401 未授权
        detail="Could not validate credentials", # 认证失败的提示信息
        headers={"WWW-Authenticate": "Bearer"}, # 这个头告诉客户端需要提供 Bearer Token
    )
    
    try:
        # 1. 解析 Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub") # 我们存 Token 时把 user_id 放在了 'sub' 字段
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 2. 去数据库查用户
    # 注意：这里要把 user_id 转成 int，因为 JWT 解析出来可能是字符串
    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user

# --- Token 生成相关 ---
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # 2. 使用从 config 导入的 SECRET_KEY 和 ALGORITHM
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt