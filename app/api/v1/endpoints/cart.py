from app.models.order import Order
from datetime import datetime
import random
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload 

# 导入刚才写的模型和Schema
from app.models.cart import Cart, CartItem
from app.models.order import OrderItem
from app.models.product import Product # 假设你有这个商品模型，用来查价格
from app.schemas.cart import CartCreate, CartOut
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.core.response import success, fail
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter()

def generate_order_number():
    # 生成一个简单的订单号，实际可以更复杂一些
    return datetime.now().strftime("%Y%m%d%H%M%S") + "".join(random.choices(string.digits, k=4))

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in : OrderCreate, # 前端传来的订单数据，包含商品ID和数量 
    db: AsyncSession = Depends(get_db), # 数据库会话，依赖注入获取
    current_user: User = Depends(get_current_user) # 当前登录用户，依赖注入获取
):
    total_amout = 0.0 # 订单总价
    order_items = [] # 订单详情列表

    for item in order_in.items:
        result = await db.execute(select(Product).where(Product.id == item.product_id).with_for_update())
        product = result.scalar_one_or_none() # result.scalar_one_or_none() 会返回单个结果，如果没有找到则返回 None，如果找到多个则抛出异常

        if not product:
            # 商品不存在，返回错误响应
            return fail(message = f"商品ID{item.product_id}不存在", code = 404)
        
        if product.stock < item.quantity:
            # 库存不足，返回错误响应
            return fail(message = f"商品ID{item.product_id}库存不足", code = 400)
        
        total_amout += product.price * item.quantity
        # 3. 创建订单详情对象
        db_item = OrderItem(
            product_id=product.id, # 商品ID
            product_name=product.name, # 商品名称
            price=product.price, # 商品单价
            quantity=item.quantity, # 数量
            total_price=product.price * item.quantity # 商品总价 = 单价 * 数量
        )
        order_items.append(db_item)

    # --- 创建订单 ---
    db_order = Order(
        order_number=generate_order_number(), # 生成随机订单号
        user_id=current_user.id, # 关联用户
        total_amount=total_amout, # 订单总价
        status="pending", # 订单状态，默认待处理
        created_at=datetime.now(), # 创建时间
        items=order_items # 订单详情列表
    )

    # --- 事务提交 (你原本就写好的骨架) ---
    try:
        db.add(db_order)
        
        # 注意：这里我们只加了订单，库存是在上面查询的时候直接修改内存对象
        # SQLAlchemy 会自动检测到 product.stock 被改了，也会把它更新进数据库
        # (因为 product 是从 db 里查出来的，它处于 db 的监控之下)
        
        await db.commit()      # 提交：订单写入 + 库存扣减写入
        await db.refresh(db_order)
        
        return db_order
        
    except Exception as e:
        await db.rollback()    # 回滚：如果订单写入失败，库存也不会被扣
        raise HTTPException(status_code=500, detail="创建订单失败")




@router.post("/add", response_model=CartOut, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart_in: CartCreate,  # 前端传来的购物车数据，包含商品ID和数量# 
    db: AsyncSession = Depends(get_db), # 数据库会话，依赖注入获取
    current_user: User = Depends(get_current_user)# 当前登录用户，依赖注入获取
):
    result = await db.execute(
        select(Cart).where(Cart.user_id == current_user.id, Cart.is_active == True)
    )
    cart = result.scalar_one_or_none()

    if cart is None:
        cart = Cart(
            user_id=current_user.id,
            total_amount=0,
            is_active=True
        )
        db.add(cart)
        await db.flush()

    total = 0.0

    for item_data in cart_in.items:
        result = await db.execute(select(Product).where(Product.id == item_data.product_id))
        product = result.scalar_one_or_none()

        if not product:
            return fail(message=f"商品ID{item_data.product_id}不存在", code=404)

        result = await db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == item_data.product_id
            )
        )
        existing_item = result.scalar_one_or_none()

        if existing_item:
            existing_item.quantity += item_data.quantity
        else:
            cart_item = CartItem(
                product_id=product.id,
                product_name=product.name,
                quantity=item_data.quantity,
                price=product.price
            )
            cart.items.append(cart_item)

        total += product.price * item_data.quantity

    cart.total_amount += total

    try:
        await db.commit()
        stmt = select(Cart).where(Cart.id == cart.id).options(selectinload(Cart.items))
        result = await db.execute(stmt)
        fresh_cart = result.scalar_one() 
        cart_out = CartOut.model_validate(fresh_cart) 
        return success(message="添加购物车成功", data=cart_out)
    except Exception as e:
        await db.rollback()
        print(f"添加购物车失败: {e}")
        return fail(message="添加购物车失败", code=500)

@router.get("/me")
async def read_my_carts(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (select(Cart)
            .where(Cart.user_id == current_user.id)
            .options(selectinload(Cart.items))
            .offset(skip)
            .limit(limit))
    result = await db.execute(stmt)
    carts = result.scalars().all()
    return success(message="获取购物车成功", data=[CartOut.model_validate(cart) for cart in carts])

@router.delete("/items/{item_id}")
async def delete_cart_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(CartItem).where(CartItem.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        return fail(message="购物车商品不存在", code=404)

    stmt_cart = select(Cart).where(Cart.id == item.cart_id, Cart.user_id == current_user.id)
    result_cart = await db.execute(stmt_cart)
    cart = result_cart.scalar_one_or_none()

    if not cart:
        return fail(message="无权删除此商品", code=403)

    cart.total_amount -= item.price * item.quantity
    await db.delete(item)
    await db.commit()
    return success(message="删除成功")