# app/api/v1/endpoints/order.py
# 订单相关的 API 路由，包含创建订单和查询用户订单的接口
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import random
import string
from datetime import datetime
from app.models.product import Product # 用来查价格

from app.schemas.order import OrderResponse, OrderCreate
from app.models.user import User
from app.models.order import Order, OrderItem
from app.db.session import get_db
from app.core.security import get_current_user
from app.core.response import success, fail

router = APIRouter() # 创建一个新的 APIRouter 实例，专门处理订单相关的路由，这样可以更好地组织代码和路由结构

# 辅助函数：生成随机订单号
def generate_order_number():
    return datetime.now().strftime("%Y%m%d%H%M%S") + "".join(random.choices(string.digits, k=4))

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order_number = generate_order_number()
    total_amount = 0.0
    order_items = []
    products_to_update = []

    for item in order_in.items:
        stmt = select(Product).where(Product.id == item.product_id).with_for_update()
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            await db.rollback()
            return fail(message=f"商品ID {item.product_id} 不存在", code=404)

        if product.stock < item.quantity:
            product_name = product.name
            product_stock = product.stock
            await db.rollback()
            return fail(message=f"商品【{product_name}】库存不足，当前库存: {product_stock}", code=400)

        product.stock -= item.quantity
        products_to_update.append(product)

        total_amount += float(product.price) * item.quantity

        db_item = OrderItem(
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            quantity=item.quantity
        )
        order_items.append(db_item)

    db_order = Order(
        order_number=order_number,
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending",
        created_at=datetime.now(),
        items=order_items
    )

    try:
        db.add(db_order)
        await db.commit()

        order_data = {
            "id": db_order.id,
            "order_number": db_order.order_number,
            "total_amount": float(db_order.total_amount),
            "status": db_order.status,
            "created_at": db_order.created_at.isoformat() if db_order.created_at else None,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "price": float(item.price),
                    "quantity": item.quantity
                }
                for item in order_items
            ]
        }
        return success(message="订单创建成功", data=order_data)
    except Exception as e:
        await db.rollback()
        return fail(message="创建订单失败", code=500)

@router.get("/me")
async def read_my_orders(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Order).where(Order.user_id == current_user.id).options(selectinload(Order.items)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    orders = result.scalars().all()

    orders_data = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items": []
        }

        for item in order.items:
            order_dict["items"].append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "price": float(item.price),
                "quantity": item.quantity
            })
        orders_data.append(order_dict)

    return success(message="获取订单列表成功", data=orders_data)

@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        return fail(message="订单不存在", code=404)

    await db.delete(order)
    await db.commit()
    return success(message="订单删除成功")

@router.patch("/{order_id}/pay")
async def pay_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        return fail(message="订单不存在", code=404)

    if order.status == "paid":
        return fail(message="订单已结算", code=400)

    order.status = "paid"
    await db.commit()
    return success(message="订单结算成功")