# app/models/__init__.py

# 导入 Base，这是所有模型继承的基础
from app.db.base import Base

# 导入具体的模型类
# 注意：这里的 .product、.user、.order 是相对于当前 __init__.py 文件的相对导入
from .product import Product
from .user import User
from .order import Order  # 👈 这是你刚刚创建的订单模型
from .order import OrderItem  # 👈 这是你刚刚创建的订单详情模型

# 这样，Base.metadata.create_all() 就能“看到”并创建所有表了