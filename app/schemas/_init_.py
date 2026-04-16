# app/schemas/__init__.py

# 1. 先导入用户 (确保 user.py 里真的有这些类)
from .user import UserCreate, UserResponse 

# 2. 再导入商品 (确保 product.py 里真的有这些类)
from .product import ProductCreate, ProductResponse

# 3. 最后导入订单 (这是你新加的)
from .order import OrderCreate, OrderResponse