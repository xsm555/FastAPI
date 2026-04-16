# 定义订单相关的数据库表和模型

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, DECIMAL, TIMESTAMP, Text, func
from sqlalchemy.orm import relationship
from app.db.base import Base  # 导入 Base，所有模型都要继承它

# 1.订单表
class Order(Base):
    __tablename__ = "orders" # 对应数据库中的表名

    # Column 定义了表中的列，参数指定了列的类型和约束条件
    # column_name = Column(data_type:数据类型，ment1, argument2, ...)
    id = Column(Integer, primary_key = True, index = True) 
    # 订单ID，主键，自增。primary_key=True 表示这是主键，index=True 表示在这个列上创建索引
    order_number = Column(String(50), unique = True, nullable = False, index = True) 
    # 订单编号，唯一，不可为空，索引。unique=True 表示这个列的值必须唯一，nullable=False 表示这个列不能为空，index=True 表示在这个列上创建索引
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False) 
    # 用户ID，外键，不可为空。ForeignKey("users.id") 表示这个列是一个外键，引用了 users 表的 id 列
    user = relationship("User", back_populates="orders")
    # 关联用户。relationship 定义了两个模型之间的关系。back_populates="orders" 表示在 User 模型中有一个属性 orders 用于访问关联的 Order 记录，而在 Order 模型中有一个属性 user 用于访问关联的 User 记录。这种双向关系使得我们可以方便地从订单访问用户，或者从用户访问订单。
    total_amount = Column(DECIMAL(10, 2), nullable  =False)  
    # 订单总金额，DECIMAL类型，10位数字，2位小数，不可为空。
    status = Column(String(20), default = "pending", index = True) 
    # 订单状态，默认值为"pending"。default = "pending" 表示如果未指定值，则默认为"pending"。index=True 表示在这个列上创建索引
    created_at = Column(DateTime, default=func.now(), nullable=False)
    # 订单创建时间，默认值为当前时间。default=func.now() 表示如果未指定值，则默认为当前时间，nullable=False 表示这个列不能为空

    # 可选：关联订单详情
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    


# 2. 订单商品详情表
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    # 订单详情ID，主键，自增。primary_key=True 表示这是主键，index=True 表示在这个列上创建索引
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    # 订单ID，外键，级联删除。ForeignKey("orders.id", ondelete="CASCADE") 表示这个列是一个外键，引用了 orders 表的 id 列，并且当关联的订单被删除时，这条记录也会被自动删除
    product_id = Column(Integer, index = True, nullable=False)
    # 商品ID，不可为空。这里没有设置外键约束，因为可能商品信息在另一个服务中管理，或者我们不需要在数据库层面强制关联
    product_name = Column(String(100), nullable=False)
    # 商品名称，字符串类型，最大长度100，不可为空。
    price = Column(DECIMAL(10, 2), nullable=False)
    # 商品价格，DECIMAL类型，10位数字，2位小数，不可为空。
    quantity = Column(Integer, nullable=False)
    # 购买数量，整数类型，不可为空。

    # 关联订单
    order = relationship("Order", back_populates="items")
    # relationship 定义了两个模型之间的关系。back_populates="items" 表示在 Order 模型中有一个属性 items 用于访问关联的 OrderItem 记录，而在 OrderItem 模型中有一个属性 order 用于访问关联的 Order 记录。这种双向关系使得我们可以方便地从订单访问订单详情，或者从订单详情访问订单。
