#  FastAPI 的核心，用于接收前端数据并返回响应数据。
# 模型定义，使用 Pydantic 来定义数据模型，确保数据的验证和序列化。
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    # 订单详情创建模型，包含商品ID和购买数量
    product_id: int # 商品ID，整数类型，不可为空。
    quantity: int # 购买数量，整数类型，不可为空。


class OrderItemResponse(OrderItemCreate):
    # 订单详情响应模型，包含订单详情ID、商品名称和价格
    id: int # 订单详情ID，整数类型，主键，自增。
    product_name: str # 商品名称，字符串类型，最大长度100，不可为空。
    price: float # 商品价格，DECIMAL类型，10位数字，2位小数，不可为空。

    class Config:
        from_attributes = True # 允许从 ORM 模型创建 Pydantic 模型


class OrderCreate(BaseModel):
    # 前端只需要传一个商品列表，其他信息（用户ID、总价、状态）由后端生成
    items: List[OrderItemCreate] # 订单详情列表，包含多个订单详情创建模型


class OrderResponse(BaseModel):
    # 订单响应模型，包含订单ID、订单编号、总金额、状态、创建时间和订单详情列表
    id :int  # 订单ID，整数类型，主键，自增。
    order_number: str # 订单编号，字符串类型，唯一，不可为空，索引。
    total_amount: float # 订单总金额，DECIMAL类型，10位数字，2位小数，不可为空。
    status: str # 订单状态，字符串类型，默认值为"pending"，索引。
    created_at: datetime # 订单创建时间，DateTime类型，默认值为当前时间，不可为空。
    items: List[OrderItemResponse] = [] # 订单详情列表，包含多个订单详情响应模型，默认为空列表

    class Config:
        from_attributes = True # 允许从 ORM 模型创建 Pydantic 模型


