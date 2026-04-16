# app/api/v1/endpoints/users.py
# 用户相关的 API 路由，包含注册、登录和获取当前用户信息的接口
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token
# from app.core.security import SECRET_KEY, ALGORITHM 
from app.core.response import success, fail

router = APIRouter()

# --- 注册 ---
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. 检查邮箱是否已存在
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)

    if result.scalar_one_or_none(): # scalar_one_or_none() 会返回单个结果，如果没有找到则返回 None，如果找到多个则抛出异常
        
        return fail(message="邮箱已被注册", code=400) 
    

    # 2. 创建用户 (密码加密)
    hashed_pw = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_pw
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return success(data=db_user, message="注册成功")
    

# --- 登录 ---
@router.post("/login", response_model=Token)
async def login(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
    # 1. 查找用户
    stmt = select(User).where(User.email == form_data.email) # 根据邮箱查询用户
    result = await db.execute(stmt) # 执行查询，返回结果对象
    user = result.scalar_one_or_none() # 从结果对象中获取单个用户记录，如果没有找到则返回 None
    
    # 2. 验证用户是否存在且密码正确
    if not user or not verify_password(form_data.password, user.hashed_password): 
        return fail(message="邮箱或密码错误", code=401) # 401 Unauthorized 表示认证失败
    
    # 3. 生成 Token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 测试受保护接口 (获取当前用户信息) ---
# 这里先简化，后续会引入 OAuth2Scheme 自动解析 Header
# 测试需要进入/docs，先进行注册和登录，获取到 token（登录进去后返回的access_token值） 后再调用这个接口
@router.get("/me", response_model=UserResponse)
async def get_me(token: str, db: AsyncSession = Depends(get_db)):
    # 简单演示：实际生产中需要解析 token 获取 user_id
    # 这里为了不让代码太复杂，暂时只演示逻辑占位
    # 真实逻辑需要从 token 中解密出 email，再查库
    from jose import jwt,JWTError
    from app.core.security import SECRET_KEY, ALGORITHM
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None: # 
            raise fail(message="Token 无效", code=401)
            
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user: # 
            raise fail(message="用户未找到", code=404)
        return user
    except JWTError:
        raise fail(message="Token 无效", code=401)