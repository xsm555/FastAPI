from pydantic import BaseModel
from typing import List, Optional

# --- 子表：购物车里的具体商品 ---
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float  # 快照价格
    
    class Config:
        from_attributes = True

# --- 主表：整个购物车 ---
class CartBase(BaseModel):
    total_amount: float # 总价

class CartCreate(CartBase):
    items: List[CartItemCreate] # 前端传来的商品列表

class CartOut(CartBase):
    id: int
    user_id: int
    items: List[CartItemOut] = []
    
    class Config:
        from_attributes = True