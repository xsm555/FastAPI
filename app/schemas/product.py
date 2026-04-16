# app/schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional

# --- 请求模型 (前端传给我们的) ---
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="商品名称")
    price: float = Field(..., gt=0, description="价格必须大于0")
    stock: int = Field(default=0, ge=0, description="库存不能为负")
    category: Optional[str] = None

# --- 响应模型 (我们返回给前端的) ---
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    category: Optional[str]

    class Config:
        from_attributes = True  # 允许从 SQLAlchemy 对象读取数据