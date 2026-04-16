# app/models/product.py
from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base  # 导入刚才定义的 Base

class Product(Base):
    __tablename__ = "products"  # 数据库表名

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    name = Column(String(100), nullable=False)       # 商品名
    price = Column(Float, nullable=False)            # 价格
    stock = Column(Integer, default=0)               # 库存
    category = Column(String(50), nullable=True)     # 分类