# app/api/v1/endpoints/products.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse
from app.core.security import get_current_user
from app.models.user import User
from app.core.response import success, fail

router = APIRouter()

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_product = Product(**product_data.dict())

    db.add(db_product)

    await db.commit()

    await db.refresh(db_product)

    return success(message="商品创建成功", data=db_product)

@router.get("/", response_model=List[ProductResponse])
async def read_products(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    category: Optional[str] = Query(None, description="按分类筛选"),
    search: Optional[str] = Query(None, description="搜索商品名称"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Product)

    if category:
        stmt = stmt.where(Product.category == category)

    if search:
        stmt = stmt.where(Product.name.contains(search))

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)

    products = result.scalars().all()

    return success(message="获取商品列表成功", data=products)