# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    # 继承自 Base，表示这是一个 ORM 模型类，对应数据库中的一张表
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False) # 存加密后的密码
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 【新增】关联订单：一个用户有多个订单
    orders = relationship("Order", back_populates="user")
    
# 用户模型定义了用户表的结构，包括字段类型、约束和默认值等信息，SQLAlchemy 会根据这个模型自动生成相应的数据库表结构。