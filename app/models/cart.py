
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

# 注意：这里导入的是你项目里定义的 Base
# 通常在 app/db/base_class.py 或者 app/db/session.py 里
from app.db.base import Base 

class Cart(Base):
    """
    购物车主表
    """
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # 关联用户users.id,从users表中查询
    total_amount = Column(Float, default=0.0) # 总价
    is_active = Column(Boolean, default=True) # 是否有效（用来模拟删除或结算后归档）
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc)) # 创建时间，默认当前时间

    # 关联关系：一个购物车有多个商品详情
    # back_populates 对应 CartItem 里的 cart
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan",  lazy="selectin") # 级联删除，使用 selectin 加载方式优化查询
    
    # 如果需要关联用户对象（可选）
    # owner = relationship("User", back_populates="carts")


class CartItem(Base):
    """
    购物车详情表（子表）
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True) # 主键，自增
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False) # 关联主表
    product_id = Column(Integer, nullable=False) # 商品ID
    product_name = Column(String(100), nullable=False) # 商品名称快照
    quantity = Column(Integer, default=1) # 数量
    price = Column(Float, nullable=False) # 商品单价快照（防止商品改价后购物车乱套）

    # 关联关系：属于某个购物车
    # back_populates 对应 Cart 里的 items
    cart = relationship("Cart", back_populates="items")